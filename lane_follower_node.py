#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LANE FOLLOWER FINAL VERSION
YOLO + BEV (Bird Eye View) + Clean Polyfit + Stable Steering
Uzun yanlış çizgiler FIX EDILDI
"""

# ROS
from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

# Vision
from cv_bridge import CvBridge
import cv2
import numpy as np
import time
from ultralytics import YOLO
import os

# Debug mouse
clicked_points = []


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        print("Clicked:", (x, y))


# ---------------- PID --------------------
class PIDController:
    def __init__(self, Kp=0.08, Ki=0.001, Kd=0.01):
        self.Kp = Kp  # Oransal kazanc
        self.Ki = Ki  # Integral kazanc
        self.Kd = Kd  # Turevsel kazanc
        self.prev_err = 0 # Bir cnceki framedeki hata
        self.integral = 0 # Zamana yayilmis hatanin birikimi

    def calculate(self, error):
        self.integral += error #Her karede hatayi ust uste ekler
        der = error - self.prev_err #derivative
        self.prev_err = error #Bir sonraki frame icin referans olarak saklaniyor
        return self.Kp * error + self.Ki * self.integral + self.Kd * der


# ---------------- LANE NODE --------------------
class LaneFollowerNode(Node):

    def bev_warp(self, img):
        return cv2.warpPerspective(img, self.M_ipm, (self.img_w, self.img_h))

    def bev_to_image(self, pts):
        if len(pts) == 0:
            return []
        pts_arr = np.array(pts, dtype=np.float32).reshape(-1, 1, 2)
        out = cv2.perspectiveTransform(pts_arr, self.M_ipm_inv)
        return out.reshape(-1, 2).astype(int).tolist()

    # YOLO mask combine
    def combine_masks(self, masks, shape):
        h, w = shape[0], shape[1]
        out = np.zeros((h, w), dtype=np.uint8)
        for m in masks:
            mm = cv2.resize(m, (w, h))
            mm = (mm > 0.5).astype(np.uint8) * 255
            out |= mm

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))# Saginda-solunda 5 piksel Yukarisinda-asagisinda 5 piksel toplam 11x11 = 121 piksel birlikte degerlendirilir.
        out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, kernel, 2)
        out = cv2.morphologyEx(out, cv2.MORPH_OPEN, kernel, 1)
        return out

    # ------------- FINAL POLYFIT -----------------
    def fit_lane_poly(self, mask):
        ys, xs = np.where(mask > 0)
        if len(xs) < 80:
            return None

        # ustteki bozuk BEV bolgesi tamamen silinir
        y_min = int(self.img_h * 0.55)
        keep = ys >= y_min
        ys = ys[keep]
        xs = xs[keep]

        if len(xs) < 50:
            return None

        #  maskede genislik cok dar ise fit yapma ---
        if np.std(xs) < 5:      # serit izi yoksa
            return None

        try:
            # Normalize weights Agirlikli Linear Fit alt bolgeye daha fazla onem
            w = (ys / np.max(ys)) ** 4

            # BEV icin dogrusal fit (1. derece)
            poly = np.polyfit(ys, xs, 1, w=w)
            m, b = poly

            # egim (m) cok buyukse yanlis fit'tir ---
            # BEV seritleri dikeydir, egim 0.1 - 0.6 arasi olur.
            if abs(m) > 1.0:    # cok egik ekrandan capraz gecen hatali cizgi
                return None

            return poly

        except:
            return None

    def poly_x(self, poly, y):
        if poly is None: # Poly yoksa crash olmasin
            return 0
        if len(poly) == 2: #Linear fit icin hizli hesap
            m, b = poly
            return int(m * y + b)
        # fallback ( Eski fitler fallback olarak korunuyor )
        return int(np.polyval(poly, y))

    # ---------------- NODE INIT -----------------
    def __init__(self):
        super().__init__("lane_follower")

        self.bridge = CvBridge() #ROS Image <-> OpenCV cv::Mat donusumu icin CvBridge
        self.img_w = 640
        self.img_h = 360

        # BEV Homografi (Noktalari biz belirledik. Yaris aninda ekrandan kamera acisina gore yol koseleri kontrol edilmeli. Ciktida yolun kenarlarina basinca koordinat degerleri veriliyor.)
        self.src_pts = np.float32([
            [15, 356],    # bottom-left
            [620, 356],   # bottom-right
            [386, 216],   # top-right
            [282, 216],   # top-left
        ])

        self.dst_pts = np.float32([
            [self.img_w * 0.20, self.img_h * 0.95],
            [self.img_w * 0.80, self.img_h * 0.95],
            [self.img_w * 0.80, self.img_h * 0.10],
            [self.img_w * 0.20, self.img_h * 0.10],
        ])

        self.M_ipm = cv2.getPerspectiveTransform(self.src_pts, self.dst_pts)
        self.M_ipm_inv = cv2.getPerspectiveTransform(self.dst_pts, self.src_pts)

        # Prev polynomials
        self.left_prev = None
        self.right_prev = None

        # PID
        self.pid = PIDController()

        # Load YOLO
        share_dir = get_package_share_directory("neuravix_ros2")
        model_path = os.path.join(share_dir, "models", "best_yolo11.pt")
        self.model = YOLO(model_path)
        self.get_logger().info("YOLO loaded.")

        # ROS
        self.pub = self.create_publisher(String, "/master", 10)
        self.sub = self.create_subscription(
            #Image, "/carla/ego_vehicle/rgb_front/image", self.cb, 10 #QoS depth = 10 Yani Bu subscriber, en fazla 10 adet mesaji kuyrukta tutabilir.
            Image, "/carla/ego_vehicle/rgb_overlay/image", self.cb, 10
        )
        """
        yaris icin carla yerine zedden alinmali
        self.sub = self.create_subscription
            (Image,/zed/zed_node/rgb/image_rect_color",self.cb,qos
        )
        """

        self.prev_time = 0

        # ---------------- VIDEO KAYDI ('r' tusu) -----------------
        # 'r' tusu ile kayit baslar/durur. overlay frame'i (BEV serit
        # cizimli) ~/neuravix_kayit/ altina yazilir.
        self.video_writer = None
        self._video_path  = None

    def _toggle_record(self, frame):
        """'r' tusu: kaydi baslat / durdur."""
        if self.video_writer is None:
            h, w = frame.shape[:2]
            out_dir = os.path.expanduser("~/neuravix_kayit")
            os.makedirs(out_dir, exist_ok=True)
            ts = time.strftime("%Y%m%d_%H%M%S")
            self._video_path = os.path.join(out_dir, f"serit_takip_{ts}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.video_writer = cv2.VideoWriter(self._video_path, fourcc, 20.0, (w, h))
            self.get_logger().info(f"[REC] Kayit BASLADI: {self._video_path}")
        else:
            self.video_writer.release()
            self.get_logger().info(f"[REC] Kayit DURDU: {self._video_path}")
            self.video_writer = None

    # ---------------- MAIN CALLBACK -----------------
    def cb(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        img = cv2.resize(frame, (self.img_w, self.img_h))

        original = img.copy()

        # FPS
        t = time.time()
        if self.prev_time != 0:
            fps = int(1 / (t - self.prev_time))
            cv2.putText(original, f"FPS: {fps}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        self.prev_time = t

        # YOLO inference
        results = self.model(img, verbose=False)
        masks = []
        for r in results:
            if r.masks is not None:
                for m in r.masks.data:
                    masks.append(m.cpu().numpy())

        center_x_bev = self.img_w // 2
        lane_x = center_x_bev

        # Eğer hiç maske yoksa fallback
        left_poly = self.left_prev
        right_poly = self.right_prev

        if len(masks) == 0:
            y_eval = int(self.img_h * 0.90)
            if left_poly is not None and right_poly is not None:
                lx = self.poly_x(left_poly, y_eval)
                rx = self.poly_x(right_poly, y_eval)
                lane_x = (lx + rx) // 2
            elif left_poly is not None:
                lane_x = self.poly_x(left_poly, y_eval) + self.img_w // 4
            elif right_poly is not None:
                lane_x = self.poly_x(right_poly, y_eval) - self.img_w // 4

        else:
            lane_mask = self.combine_masks(masks, img.shape)

            # Horizon üstünü tamamen sil → kavşak/gölge fix
            horizon = int(self.img_h * 0.40)
            lane_mask[:horizon, :] = 0

            # BEV mask
            bev = self.bev_warp(lane_mask)

            # Left-right split
            mid = self.img_w // 2
            offset = 70

            left_mask = np.zeros_like(bev)
            right_mask = np.zeros_like(bev)

            left_mask[:, :mid] = bev[:, :mid]
            left_mask[:, mid - offset:] = 0

            right_mask[:, mid:] = bev[:, mid:]
            right_mask[:, :mid + offset] = 0

            # Polyfit
            lp = self.fit_lane_poly(left_mask)
            rp = self.fit_lane_poly(right_mask)

            if lp is not None:
                left_poly = lp
            if rp is not None:
                right_poly = rp

            y_eval = int(self.img_h * 0.90)

            if left_poly is not None and right_poly is not None:
                lane_x = (self.poly_x(left_poly, y_eval) +
                          self.poly_x(right_poly, y_eval)) // 2
            elif left_poly is not None:
                lane_x = self.poly_x(left_poly, y_eval) + self.img_w // 4
            elif right_poly is not None:
                lane_x = self.poly_x(right_poly, y_eval) - self.img_w // 4

        # Save polynomials
        self.left_prev = left_poly
        self.right_prev = right_poly

        # DRAW BEV → image projection
        overlay = original.copy()

        # Left
        if left_poly is not None:
            ys = np.linspace(self.img_h * 0.55, self.img_h - 1, 40).astype(int)
            pts = [(self.poly_x(left_poly, y), y) for y in ys]
            imgpts = self.bev_to_image(pts)
            for i in range(len(imgpts) - 1):
                cv2.line(overlay, tuple(imgpts[i]), tuple(imgpts[i+1]), (255, 0, 0), 3)

        # Right
        if right_poly is not None:
            ys = np.linspace(self.img_h * 0.55, self.img_h - 1, 40).astype(int)
            pts = [(self.poly_x(right_poly, y), y) for y in ys]
            imgpts = self.bev_to_image(pts)
            for i in range(len(imgpts) - 1):
                cv2.line(overlay, tuple(imgpts[i]), tuple(imgpts[i+1]), (0, 0, 255), 3)

        # Center line (yellow)
        bottom = int(self.img_h * 0.90)
        top = int(self.img_h * 0.55)
        cen_pts = [(lane_x, bottom), (lane_x, top)]
        cen_img = self.bev_to_image(cen_pts)
        if len(cen_img) == 2:
            cv2.line(overlay, tuple(cen_img[0]), tuple(cen_img[1]), (0, 255, 255), 3)

        # Steering
        err = lane_x - center_x_bev
        out = self.pid.calculate(err)
        steer = 45 - out  #0.05 olcekleme
        steer = max(15, min(75, int(steer))) #sınırlandırma

        cv2.putText(overlay, f"Error: {err}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(overlay, f"Steering: {steer}", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        msg = String()
        msg.data = f"2,{steer}"
        self.pub.publish(msg)

        # Kayit aktifse, ekranda gosterilen overlay'i videoya yaz
        if self.video_writer is not None:
            self.video_writer.write(overlay)

        cv2.imshow("Original with BEV Lanes", overlay)
        cv2.setMouseCallback("Original with BEV Lanes", mouse_callback)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):          # kaydi baslat/durdur
            self._toggle_record(overlay)


# ---------------- MAIN --------------------
def main(args=None):
    rclpy.init(args=args)
    node = LaneFollowerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.video_writer is not None:   # acik kayit varsa kapat
            node.video_writer.release()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
