#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNSS -> MAP POZU  (route_planner icin AMCL'siz konum kaynagi)
=============================================================
NEDEN VAR (2026-08-22 karari):
  route_planner map-cerceveli bir poz bekliyor ve bugune kadar bunun tek
  kaynagi AMCL + GNSS gozetmeniydi. Ama:
    * AMCL bu pistte TEK BASINA kullanilamiyor  -> medyan 27-29 m (iki
      bagimsiz cevrimdisi kosu). Yani AMCL'in dogrulugu zaten GNSS'ten
      geliyor: gozetmen onu GNSS'e demirliyor.
    * Yigin GERCEK ARACTA HIC CALISMADI (20-21 Agustos kayitlarinin hicbirinde
      /amcl_pose yok).
    * Olculen dogruluk sayilari (medyan 0.29-1.19 m) GNSS'e KARSI olculdu,
      yani "AMCL GNSS'i takip ediyor" diyorlar -- bagimsiz bir dogruluk
      kaniti degiller.
  Teknik kontrol rotasi ~54 m, tunel yok, iki olay var (6 m ve 2 m esikleri).
  Bu is icin GNSS tek basina yeterli ve AMCL'in sahada hic denenmemis
  yakinsama/aliasing riskini tamamen ortadan kaldiriyor.

  ⚠️ Bu dugum AMCL YIGININI DEGISTIRMEZ, ONUN YERINE GECMEZ. Ayri bir topic'e
  (/gnss_pose) yayin yapar; hangisinin kullanilacagi planner'in `pose_topic`
  parametresiyle secilir. Ikisi ayni anda kosabilir (AMCL'i izlemek icin).

KONUM:
  gnss_supervisor.to_map ile BIREBIR ayni donusum -- ayni datum, ayni
  `R.T @ p` konvansiyonu. (Ters yon `R @ p` GNSS'i haritanin disina koyuyor;
  2026-08-13'te olculdu.) datum_lat/lon HARITANIN (0,0) NOKTASININ enlem/
  boylamidir, yarismanin geojson'undaki datum satiri DEGIL -- ikisi arasinda
  109 m kuzey + 64.5 m dogu fark var.

YON (yaw):
  1) Xsens filtre kuaterniyonu (/filter/quaternion) + datum_yaw. Sahada
     dogrulandi: GNSS gidis yonu ile filtre yaw'i arasindaki fark medyan
     -2.2 derece / +0.1 derece (iki bag, 2026-08-20).
  2) Filtre yoksa GNSS gidis yonu (course over ground) -- yalnizca arac
     `min_speed_for_heading` uzerindeyken guvenilir.
  3) Hicbiri yoksa son bilinen yaw korunur.

CALISTIRMA:
    ros2 run bee1_description gnss_pose
    ros2 run neuravix_ros2 route_planner --ros-args -p pose_topic:=/gnss_pose ...
"""
import math

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import PoseWithCovarianceStamped, QuaternionStamped

R_EARTH = 6378137.0


class GnssPose(Node):
    def __init__(self):
        super().__init__('gnss_pose')

        # Datum: gnss_supervisor ile AYNI degerler olmak zorunda.
        self.declare_parameter('datum_lat', 40.79041010)
        self.declare_parameter('datum_lon', 29.50912636)
        self.declare_parameter('datum_yaw_deg', -149.20)
        self.declare_parameter('gnss_topic', '/gnss')
        self.declare_parameter('quat_topic', '/filter/quaternion')
        self.declare_parameter('output_topic', '/gnss_pose')
        self.declare_parameter('use_filter_yaw', True)
        # Bu hizin altinda GNSS gidis yonu gurultuye bogulur (2 m gurultu /
        # yavas arac). Filtre yaw'i kullaniliyorsa bu deger onemsiz.
        self.declare_parameter('min_speed_for_heading', 0.4)
        # Filtre kuaterniyonu bu suredir gelmiyorsa gidis yonune dus.
        self.declare_parameter('quat_timeout', 1.0)
        # Planner'a bildirilen belirsizlik. GNSS'in GERCEK dogrulugu (~2 m),
        # alici hassasiyeti degil.
        self.declare_parameter('pose_std_xy', 2.0)
        self.declare_parameter('pose_std_yaw_deg', 10.0)

        g = lambda n: self.get_parameter(n).value
        self.lat0, self.lon0 = g('datum_lat'), g('datum_lon')
        self.datum_yaw = math.radians(g('datum_yaw_deg'))
        c, s = math.cos(self.datum_yaw), math.sin(self.datum_yaw)
        self.R = np.array([[c, -s], [s, c]])
        self.use_filter_yaw = bool(g('use_filter_yaw'))
        self.min_spd = float(g('min_speed_for_heading'))
        self.quat_timeout = float(g('quat_timeout'))
        self.sxy = float(g('pose_std_xy'))
        self.syaw = math.radians(g('pose_std_yaw_deg'))

        self.pub = self.create_publisher(
            PoseWithCovarianceStamped, g('output_topic'), 10)
        # Surucu QoS'u best-effort olabilir; sensor profili ikisiyle de eslesir.
        self.create_subscription(NavSatFix, g('gnss_topic'), self.on_fix,
                                 qos_profile_sensor_data)
        if self.use_filter_yaw:
            self.create_subscription(QuaternionStamped, g('quat_topic'),
                                     self.on_quat, qos_profile_sensor_data)

        self.filter_yaw = None       # ENU yaw (rad), Xsens filtresinden
        self.filter_t = None
        self.prev = None             # (t, x, y) -- gidis yonu icin
        self.yaw = None
        self.n_fix = 0
        self.n_yok = 0

        self.get_logger().info(
            f"gnss_pose: datum ({self.lat0:.7f}, {self.lon0:.7f}) "
            f"yaw {math.degrees(self.datum_yaw):+.2f}deg | "
            f"{g('gnss_topic')} -> {g('output_topic')} | "
            f"yon kaynagi: {'filtre kuaterniyonu' if self.use_filter_yaw else 'gidis yonu'}")

    # ------------------------------------------------------------------
    def to_map(self, lat, lon):
        """WGS84 -> yerel ENU -> map. gnss_supervisor.to_map ile BIREBIR ayni.

        ⚠️ `R.T @ p`, `R @ p` DEGIL -- datum satir-vektor konvansiyonuyla
        (P @ R) cikarilmisti, sutun-vektor karsiligi budur.
        """
        e = math.radians(lon - self.lon0) * R_EARTH * math.cos(math.radians(self.lat0))
        n = math.radians(lat - self.lat0) * R_EARTH
        return self.R.T @ np.array([e, n])

    def on_quat(self, msg):
        q = msg.quaternion
        # ENU yaw (Xsens filtresi ENU verir; datum_yaw ile map'e cevrilir)
        enu = math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                         1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        self.filter_yaw = enu
        self.filter_t = self._now()

    def _now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def on_fix(self, msg):
        if not (math.isfinite(msg.latitude) and math.isfinite(msg.longitude)):
            self.n_yok += 1
            if self.n_yok % 20 == 1:
                self.get_logger().warn(f"GNSS fix gecersiz (NaN) x{self.n_yok}")
            return
        t = self._now()
        x, y = self.to_map(msg.latitude, msg.longitude)

        # --- YON ---
        yaw = None
        taze = (self.filter_t is not None
                and (t - self.filter_t) <= self.quat_timeout)
        if self.use_filter_yaw and taze and self.filter_yaw is not None:
            # ENU yaw -> map yaw: haritanin ENU'ya gore donmesi cikarilir.
            yaw = self._norm(self.filter_yaw - self.datum_yaw)
        elif self.prev is not None:
            dt = t - self.prev[0]
            dx, dy = x - self.prev[1], y - self.prev[2]
            if dt > 1e-3 and math.hypot(dx, dy) / dt >= self.min_spd:
                yaw = math.atan2(dy, dx)
        if yaw is not None:
            self.yaw = yaw
        self.prev = (t, x, y)
        if self.yaw is None:
            # Henuz yon yok: planner yaklasma testi icin yaw'a ihtiyac duyar,
            # ama konum yayinlamamak da ilerlemeyi tamamen durdurur. 0 ile
            # yayinlamak yanlis yone donus komutu urettirebilecegi icin
            # BEKLIYORUZ ve sebebini soyluyoruz.
            if self.n_fix % 40 == 0:
                self.get_logger().warn(
                    "Yon (yaw) henuz yok -> poz YAYINLANMIYOR. Filtre "
                    "kuaterniyonu gelmiyorsa arac birkac metre hareket etmeli.")
            self.n_fix += 1
            return

        p = PoseWithCovarianceStamped()
        p.header.stamp = msg.header.stamp if msg.header.stamp.sec else \
            self.get_clock().now().to_msg()
        p.header.frame_id = 'map'
        p.pose.pose.position.x = float(x)
        p.pose.pose.position.y = float(y)
        p.pose.pose.orientation.z = math.sin(self.yaw / 2.0)
        p.pose.pose.orientation.w = math.cos(self.yaw / 2.0)
        cov = [0.0] * 36
        cov[0] = cov[7] = self.sxy ** 2
        cov[35] = self.syaw ** 2
        p.pose.covariance = cov
        self.pub.publish(p)

        self.n_fix += 1
        if self.n_fix % 100 == 0:
            kaynak = 'filtre' if (self.use_filter_yaw and taze) else 'gidis yonu'
            self.get_logger().info(
                f"gnss_pose: map ({x:+.2f}, {y:+.2f}) yaw "
                f"{math.degrees(self.yaw):+.1f}deg [{kaynak}] | {self.n_fix} fix")

    @staticmethod
    def _norm(a):
        return (a + math.pi) % (2 * math.pi) - math.pi


def main():
    rclpy.init()
    node = GnssPose()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
