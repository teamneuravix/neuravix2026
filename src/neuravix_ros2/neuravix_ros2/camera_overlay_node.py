#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SADECE CARLA SİMÜLASYONU - gerçek araca taşınmayacak.
Gerçek tespit zaten lane_follower_node.py / tabela_tespit_node.py'de YOLO ile
ayrı yapılıyor; bu node yalnızca CARLA'nın kendi RGB+Depth sensörüyle bir
görselleştirme/debug overlay'i üretir ve `carla.Client` API'sine bağımlıdır.

Tabela + Serit OVERLAY - ROS2 yayinci (KENDI kamerasi + DEPTH occlusion)
========================================================================
Ego'ya KENDI RGB + DEPTH kamerasini takar:
  - Goruntu ve kamera transform'u AYNI callback'te yakalanir -> titreme azalir
    (ROS round-trip + gec transform sorgusu kaynakli kayma giderilir).
  - DEPTH kamerasi ile occlusion: serit/tabela bir cismin (bariyer) ARKASINDA
    ise CIZILMEZ -> "engelin ustunden gecme" sorunu gider.

Cikti: /carla/ego_vehicle/rgb_overlay/image  (lane_follower + tabela_tespit bunu okur)

NOT: Package CARLA xodr serit boyalarini kameraya render etmiyor; overlay tek
pure-python yol. Tam stabil/gercek serit icin UE4 source build gerekir.

Calistirma:
    ros2 run neuravix_ros2 tabela_overlay
    ros2 run neuravix_ros2 tabela_overlay --ros-args -p draw_lanes:=false   # sadece tabela
"""
import json
import math
import os
import sys
import time

import numpy as np

try:
    import carla
except ImportError:
    sys.exit("carla paketi yok")
try:
    import cv2
except ImportError:
    sys.exit("opencv yok: pip install opencv-python")

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

# --- Veri dizini: kurulu paket share'i; yoksa dosya yani (dev) ---
try:
    from ament_index_python.packages import get_package_share_directory
    HERE = os.path.join(get_package_share_directory("neuravix_ros2"), "tabela")
    if not os.path.isdir(HERE):
        raise RuntimeError
except Exception:
    HERE = os.path.dirname(os.path.abspath(__file__))

LAYOUT = os.path.join(HERE, "pist_layout.json")

TABELA_PNG = {
    "ileri_git": ("ileri.png", False),
    "sol_don":   ("sola-dön.png", False),
    "sag_don":   ("saga-dön.png", False),
    "tunel":     ("tünel.png", False),
    "park":      ("park-yapılabilir.png", False),
    "no_park":   ("park-edilemez.png", False),
    "durak":     ("durak.png", False),
}

SIGN_Z = 2.2
SIGN_REAL_W = 0.9
LANE_Z = 0.06


# ---------------------------------------------------------------------------
# Projeksiyon + geometri yardimcilari
# ---------------------------------------------------------------------------

def build_K(w, h, fov):
    focal = w / (2.0 * math.tan(math.radians(fov) / 2.0))
    return np.array([[focal, 0, w / 2.0],
                     [0, focal, h / 2.0],
                     [0, 0, 1.0]]), focal


def project(x, y, z, K, w2c):
    p = np.array([x, y, z, 1.0])
    pc = np.dot(w2c, p)
    point = np.array([pc[1], -pc[2], pc[0]])
    depth = point[2]
    if depth <= 0.05:
        return None, None, depth
    ip = np.dot(K, point)
    return ip[0] / ip[2], ip[1] / ip[2], depth


def build_lane_segments(layout):
    VX = layout.get("vertical_roads_x", [])
    HY = layout.get("horizontal_roads_y", [])
    meta = layout.get("meta", {})
    W = meta.get("main_w", 73.0)
    H = meta.get("main_h", 73.0)
    lw = meta.get("lane_width", 3.0)
    segs = []

    def add(x0, y0, x1, y1):
        segs.append(((x0, -y0), (x1, -y1)))

    def solid(x0, y0, x1, y1, step=2.0):
        d = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(d / step))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            add(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0,
                x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)

    def dashed(x0, y0, x1, y1, dash=2.0, gap=4.0):
        d = math.hypot(x1 - x0, y1 - y0)
        if d < 1e-6:
            return
        ux, uy = (x1 - x0) / d, (y1 - y0) / d
        s = 0.0
        while s < d:
            e = min(s + dash, d)
            add(x0 + ux * s, y0 + uy * s, x0 + ux * e, y0 + uy * e)
            s += dash + gap

    for x in VX:
        solid(x - lw, 0, x - lw, H)
        solid(x + lw, 0, x + lw, H)
        dashed(x, 0, x, H)
    for y in HY:
        solid(0, y - lw, W, y - lw)
        solid(0, y + lw, W, y + lw)
        dashed(0, y, W, y)

    pk = layout.get("parking")
    if pk:
        px = pk.get("x", 73.0); pw = pk.get("w", 17.0)
        pyb = pk.get("y", 43.0); ph = pk.get("h", 20.0)
        ey = pk.get("entry_y", 47.0)
        col_mid = px + pw / 2
        solid(px, pyb, px + pw, pyb)
        solid(px, pyb + ph, px + pw, pyb + ph)
        solid(px, pyb, px, pyb + ph)
        solid(px + pw, pyb, px + pw, pyb + ph)
        solid(col_mid, pyb, col_mid, pyb + ph)
        slot_h = 2.5
        for k in range(int(round(ph / slot_h)) + 1):
            sy = pyb + k * slot_h
            solid(px, sy, col_mid, sy)
        solid(W, ey - lw, px, ey - lw)
        solid(W, ey + lw, px, ey + lw)
    return segs


def _durak_xy_hdg(d, W, H):
    if d.get("kind") == "ic":
        return float(d.get("cx", 0)), float(d.get("cy", 0)), math.pi
    side = d.get("side")
    along = float(d.get("along", 0))
    depth = float(d.get("depth", 3.5))
    if side == "W":
        return -depth / 2, along, 0.0
    if side == "E":
        return W + depth / 2, along, math.pi
    if side == "S":
        return along, -depth / 2, math.pi / 2
    if side == "N":
        return along, H + depth / 2, -math.pi / 2
    return 0.0, 0.0, math.pi


def load_signs(layout):
    signs = []

    def load_png(tn):
        spec = TABELA_PNG.get(tn)
        if not spec:
            return None
        fname, flip = spec
        path = os.path.join(HERE, fname)
        if not os.path.exists(path):
            print(f"[uyari] {fname} yok ({path}), {tn} atlandi")
            return None
        data = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
        if img is None:
            return None
        return cv2.flip(img, 1) if flip else img

    for m in layout.get("misyon_objeleri", []):
        if m.get("kind") != "sign":
            continue
        img = load_png(m.get("type_name"))
        if img is None:
            continue
        hdg = float(m.get("hdg", math.pi))
        signs.append((m["type_name"], float(m["x"]), -float(m["y"]),
                      (math.cos(hdg), -math.sin(hdg)), img))

    meta = layout.get("meta", {})
    W = meta.get("main_w", 73.0)
    H = meta.get("main_h", 73.0)
    durak_img = load_png("durak")
    if durak_img is not None:
        for d in layout.get("duraklar", []):
            px, py, hdg = _durak_xy_hdg(d, W, H)
            signs.append(("durak", px, -py,
                          (math.cos(hdg), -math.sin(hdg)), durak_img))
    return signs


def overlay_png(frame, png, cu, cv_, px_w, alpha=1.0):
    if px_w < 6:
        return
    h0, w0 = png.shape[:2]
    px_h = int(px_w * h0 / w0)
    px_w = int(px_w)
    if px_w < 1 or px_h < 1:
        return
    resized = cv2.resize(png, (px_w, px_h), interpolation=cv2.INTER_AREA)
    x0, y0 = int(cu - px_w / 2), int(cv_ - px_h / 2)
    H, W = frame.shape[:2]
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(W, x0 + px_w), min(H, y0 + px_h)
    if sx0 >= sx1 or sy0 >= sy1:
        return
    rx0, ry0 = sx0 - x0, sy0 - y0
    roi = resized[ry0:ry0 + (sy1 - sy0), rx0:rx0 + (sx1 - sx0)]
    if roi.shape[2] == 4:
        a = (roi[:, :, 3:4] / 255.0) * alpha
        frame[sy0:sy1, sx0:sx1] = (
            a * roi[:, :, :3] + (1 - a) * frame[sy0:sy1, sx0:sx1]).astype(np.uint8)
    else:
        frame[sy0:sy1, sx0:sx1] = roi[:, :, :3]


# ---------------------------------------------------------------------------
# ROS2 Node
# ---------------------------------------------------------------------------

class OverlayNode(Node):
    def __init__(self):
        super().__init__("tabela_serit_overlay")

        self.declare_parameter("host", "localhost")
        self.declare_parameter("port", 2000)
        self.declare_parameter("out_topic", "/carla/ego_vehicle/rgb_overlay/image")
        self.declare_parameter("ego_role", "ego_vehicle")
        self.declare_parameter("width", 1280)
        self.declare_parameter("height", 720)
        self.declare_parameter("fov", 110.0)
        self.declare_parameter("cam_x", 2.0)
        self.declare_parameter("cam_z", 1.0)
        self.declare_parameter("cam_pitch", -5.0)
        self.declare_parameter("range", 45.0)
        self.declare_parameter("lane_horizon", 0.46)
        self.declare_parameter("lane_thickness", 2)
        self.declare_parameter("lane_bri", 225)
        self.declare_parameter("lane_alpha", 0.85)
        self.declare_parameter("draw_lanes", True)
        self.declare_parameter("use_depth", True)     # serit depth occlusion (engel ustu fix)
        self.declare_parameter("depth_margin", 0.6)   # m tolerans
        self.declare_parameter("occlude_signs", True) # tabela cast_ray occlusion (bariyer arkasi gizle)

        host = self.get_parameter("host").value
        port = int(self.get_parameter("port").value)
        self.out_topic = self.get_parameter("out_topic").value
        self.ego_role = self.get_parameter("ego_role").value
        self.W = int(self.get_parameter("width").value)
        self.H = int(self.get_parameter("height").value)
        self.fov = float(self.get_parameter("fov").value)
        self.cam_x = float(self.get_parameter("cam_x").value)
        self.cam_z = float(self.get_parameter("cam_z").value)
        self.cam_pitch = float(self.get_parameter("cam_pitch").value)
        self.range = float(self.get_parameter("range").value)
        self.lane_horizon = float(self.get_parameter("lane_horizon").value)
        self.lane_thickness = int(self.get_parameter("lane_thickness").value)
        lb = int(self.get_parameter("lane_bri").value)
        self.lane_color = (lb, lb, lb)
        self.lane_alpha = float(self.get_parameter("lane_alpha").value)
        self.draw_lanes = bool(self.get_parameter("draw_lanes").value)
        self.use_depth = bool(self.get_parameter("use_depth").value)
        self.depth_margin = float(self.get_parameter("depth_margin").value)
        self.occlude_signs = bool(self.get_parameter("occlude_signs").value)

        self.get_logger().info(f"Veri dizini: {HERE}")

        self.client = carla.Client(host, port)
        self.client.set_timeout(20.0)
        self.world = self.client.get_world()

        # Ego bul (bridge spawn etmis olmali)
        self.ego = None
        for _ in range(40):
            for a in self.world.get_actors().filter("vehicle.*"):
                if a.attributes.get("role_name") in (self.ego_role, "hero", "ego"):
                    self.ego = a
                    break
            if self.ego:
                break
            time.sleep(0.5)
        if self.ego is None:
            raise RuntimeError(f"ego ({self.ego_role}) bulunamadi - bridge/spawn calisti mi?")
        self.get_logger().info(f"Ego bulundu: {self.ego.type_id} id={self.ego.id}")

        bl = self.world.get_blueprint_library()
        cam_tf = carla.Transform(
            carla.Location(x=self.cam_x, z=self.cam_z),
            carla.Rotation(pitch=self.cam_pitch))

        # RGB kamera (bloom KAPALI -> serit kenarlari net)
        rgb_bp = bl.find("sensor.camera.rgb")
        rgb_bp.set_attribute("image_size_x", str(self.W))
        rgb_bp.set_attribute("image_size_y", str(self.H))
        rgb_bp.set_attribute("fov", str(self.fov))
        for attr, val in (("bloom_intensity", "0.0"),
                          ("lens_flare_intensity", "0.0"),
                          ("motion_blur_intensity", "0.0")):
            if rgb_bp.has_attribute(attr):
                rgb_bp.set_attribute(attr, val)
        self.rgb_cam = self.world.spawn_actor(rgb_bp, cam_tf, attach_to=self.ego)

        # DEPTH kamera (occlusion icin) - ayni transform/fov/res
        self.depth_cam = None
        self.depth_img = None
        if self.use_depth:
            d_bp = bl.find("sensor.camera.depth")
            d_bp.set_attribute("image_size_x", str(self.W))
            d_bp.set_attribute("image_size_y", str(self.H))
            d_bp.set_attribute("fov", str(self.fov))
            self.depth_cam = self.world.spawn_actor(d_bp, cam_tf, attach_to=self.ego)
            self.depth_cam.listen(self._depth_cb)

        self.K, self.focal = build_K(self.W, self.H, self.fov)

        with open(LAYOUT, encoding="utf-8") as f:
            layout = json.load(f)
        self.signs = load_signs(layout)
        self.lane_segs = build_lane_segments(layout) if self.draw_lanes else []
        self.lane_mid = np.array(
            [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in self.lane_segs]
        ) if self.lane_segs else np.zeros((0, 2))

        self.bridge = CvBridge()
        self.pub = self.create_publisher(Image, self.out_topic, 10)
        self.rgb_cam.listen(self._rgb_cb)

        self.get_logger().info(
            f"Overlay KENDI kamerasi -> {self.out_topic} "
            f"(tabela={len(self.signs)}, serit_seg={len(self.lane_segs)}, "
            f"depth_occlusion={self.use_depth})")

    def _depth_cb(self, image):
        """CARLA depth -> metre array (occlusion icin)."""
        arr = np.frombuffer(image.raw_data, dtype=np.uint8)
        arr = arr.reshape((image.height, image.width, 4)).astype(np.float32)
        # BGRA; CARLA depth = (R + G*256 + B*256^2)/(256^3-1) * 1000 m
        b, g, r = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        normalized = (r + g * 256.0 + b * 65536.0) / (16777215.0)
        self.depth_img = normalized * 1000.0

    def _occluded(self, u, v, d):
        """(u,v) pikselindeki sahne derinligi d'den kucukse -> cismin arkasinda."""
        if self.depth_img is None:
            return False
        iu, iv = int(round(u)), int(round(v))
        if 0 <= iv < self.depth_img.shape[0] and 0 <= iu < self.depth_img.shape[1]:
            return self.depth_img[iv, iu] + self.depth_margin < d
        return False

    def _rgb_cb(self, image):
        arr = np.frombuffer(image.raw_data, dtype=np.uint8)
        frame = arr.reshape((image.height, image.width, 4))[:, :, :3].copy()  # BGR

        # Transform GORUNTU ile birlikte (callback aninda) -> titreme az
        cam_tf = self.rgb_cam.get_transform()
        cam_loc = cam_tf.location
        w2c = np.array(cam_tf.get_inverse_matrix())
        H, W = frame.shape[:2]

        # --- SERIT ---
        if self.lane_segs:
            cx, cy = cam_loc.x, cam_loc.y
            horizon_y = H * self.lane_horizon
            d2 = (self.lane_mid[:, 0] - cx) ** 2 + (self.lane_mid[:, 1] - cy) ** 2
            near_idx = np.where(d2 < (self.range + 10) ** 2)[0]
            lane_layer = frame.copy()
            drew = False
            for i in near_idx:
                (ax, ay), (bx, by) = self.lane_segs[i]
                u0, v0, dd0 = project(ax, ay, LANE_Z, self.K, w2c)
                u1, v1, dd1 = project(bx, by, LANE_Z, self.K, w2c)
                if u0 is None or u1 is None:
                    continue
                if v0 < horizon_y or v1 < horizon_y:
                    continue
                # DEPTH occlusion: iki uc da cismin arkasindaysa cizme
                if self._occluded(u0, v0, dd0) and self._occluded(u1, v1, dd1):
                    continue
                cv2.line(lane_layer, (int(u0), int(v0)), (int(u1), int(v1)),
                         self.lane_color, self.lane_thickness, cv2.LINE_AA)
                drew = True
            if drew:
                cv2.addWeighted(lane_layer, self.lane_alpha,
                                frame, 1.0 - self.lane_alpha, 0.0, frame)

        # --- TABELA ---
        for tn, sx, sy, normal, png in self.signs:
            u, v, depth = project(sx, sy, SIGN_Z, self.K, w2c)
            if u is None or depth > self.range:
                continue
            if u < -200 or u > W + 200:
                continue

            # OCCLUSION: kameradan tabela TABANINA (z~0.3) isin at. Araba ile
            # tabela arasinda cisim (bariyer/engel) varsa HIC CIZME.
            # Tabana atiyoruz: tepeye atinca isin kisa bariyerin USTUNDEN gecip
            # "gorunur" diyordu -> tabela engelin arkasindan gorunuyordu.
            # Engeli gecince taban hatti temizlenir, tabela ekrana gelir.
            if self.occlude_signs:
                base = carla.Location(x=sx, y=sy, z=0.3)
                ds = cam_loc.distance(base)
                try:
                    hits = self.world.cast_ray(cam_loc, base)
                    blocked = any(
                        1.0 < cam_loc.distance(hp.location) < ds - 1.0
                        for hp in hits)
                    if blocked:
                        continue
                except Exception:
                    pass

            px_w = self.focal * SIGN_REAL_W / depth
            overlay_png(frame, png, u, v, px_w)

        try:
            out = self.bridge.cv2_to_imgmsg(frame, "bgr8")
            out.header.stamp = self.get_clock().now().to_msg()
            out.header.frame_id = "ego_vehicle/rgb_front"
            self.pub.publish(out)
        except Exception as e:
            self.get_logger().warn(f"publish: {e}")

    def destroy_node(self):
        try:
            self.rgb_cam.stop(); self.rgb_cam.destroy()
        except Exception:
            pass
        try:
            if self.depth_cam:
                self.depth_cam.stop(); self.depth_cam.destroy()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = OverlayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
