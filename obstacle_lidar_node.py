#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Engel Tespit Node - Lidar -> /master (ID 4)
================================================================
CARLA lidar point cloud'undan onundeki/yanindaki en yakin engel
mesafelerini hesaplar ve karar beynine (/master) yayinlar.

/master formati (neuravix_control_node bunu bekler):
    "4,<front>,<left>,<right>"   (metre)

Sektorler (lidar sensor frame, ROS REP-103: x ileri, +y SOL, z yukari):
  - front : x>0, |y| < corridor      -> ileri en yakin engel
  - left  : +y > corridor            -> sol klerans
  - right : -y > corridor            -> sag klerans

Zemin ve yuksek noktalar z filtresi ile atilir.

Calistirma:
    ros2 run neuravix_ros2 obstacle_lidar
    # y ekseni ters cikarsa (sol/sag yer degistirirse):
    ros2 run neuravix_ros2 obstacle_lidar --ros-args -p flip_y:=true
"""
import sys

import numpy as np

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import String

try:
    from sensor_msgs_py import point_cloud2 as pc2
except ImportError:
    sys.exit("sensor_msgs_py yok (ROS2 humble ile gelir)")


class ObstacleLidarNode(Node):
    def __init__(self):
        super().__init__("obstacle_lidar_node")

        self.declare_parameter("lidar_topic", "/carla/ego_vehicle/lidar")
        self.declare_parameter("master_topic", "/master")
        self.declare_parameter("corridor", 1.2)      # ileri koridor yari-genisligi (m)
        self.declare_parameter("side_window", 4.0)   # yan klerans icin ileri pencere (m)
        self.declare_parameter("z_min", -1.3)        # zemin filtresi (sensor altinda)
        self.declare_parameter("z_max", 2.0)         # yuksek nesne filtresi
        self.declare_parameter("x_min", 0.5)         # sensorun bu kadar onunden itibaren
        self.declare_parameter("max_range", 30.0)    # bunun otesi 99 (engel yok)
        self.declare_parameter("flip_y", False)      # +y sag cikarsa True yap
        self.declare_parameter("rate_hz", 10.0)

        self.lidar_topic = self.get_parameter("lidar_topic").value
        self.master_topic = self.get_parameter("master_topic").value
        self.corridor = float(self.get_parameter("corridor").value)
        self.side_window = float(self.get_parameter("side_window").value)
        self.z_min = float(self.get_parameter("z_min").value)
        self.z_max = float(self.get_parameter("z_max").value)
        self.x_min = float(self.get_parameter("x_min").value)
        self.max_range = float(self.get_parameter("max_range").value)
        self.flip_y = bool(self.get_parameter("flip_y").value)

        self.pub = self.create_publisher(String, self.master_topic, 10)
        self.sub = self.create_subscription(
            PointCloud2, self.lidar_topic, self.cloud_cb, 10)

        # rate limit (lidar her donuste gelebilir; biz sabit hizda yayinlariz)
        self._last_front = 99.0
        self._last_left = 99.0
        self._last_right = 99.0
        rate = float(self.get_parameter("rate_hz").value)
        self.timer = self.create_timer(1.0 / max(1.0, rate), self.publish_master)

        self.get_logger().info(
            f"Engel lidar node: {self.lidar_topic} -> {self.master_topic} (ID 4), "
            f"corridor={self.corridor}m, flip_y={self.flip_y}")

    def cloud_cb(self, cloud: PointCloud2):
        try:
            pts = pc2.read_points_numpy(
                cloud, field_names=("x", "y", "z"), skip_nans=True)
        except AttributeError:
            pts = np.array(
                [[p[0], p[1], p[2]] for p in pc2.read_points(
                    cloud, field_names=("x", "y", "z"), skip_nans=True)],
                dtype=np.float32)

        if pts is None or len(pts) == 0:
            self._last_front = self._last_left = self._last_right = 99.0
            return

        x = pts[:, 0].astype(np.float32)
        y = pts[:, 1].astype(np.float32)
        z = pts[:, 2].astype(np.float32)
        if self.flip_y:
            y = -y

        # zemin + yuksek + cok uzak filtre
        m = (z > self.z_min) & (z < self.z_max)
        x, y = x[m], y[m]
        if x.size == 0:
            self._last_front = self._last_left = self._last_right = 99.0
            return

        # --- ONDEKI en yakin engel ---
        fm = (x > self.x_min) & (np.abs(y) < self.corridor) & (x < self.max_range)
        if np.any(fm):
            front = float(np.min(np.sqrt(x[fm] ** 2 + y[fm] ** 2)))
        else:
            front = 99.0

        # --- SOL klerans (+y) ---
        lm = (y > self.corridor) & (np.abs(x) < self.side_window) & (y < self.max_range)
        left = float(np.min(y[lm])) if np.any(lm) else 99.0

        # --- SAG klerans (-y) ---
        rm = (y < -self.corridor) & (np.abs(x) < self.side_window) & (-y < self.max_range)
        right = float(np.min(-y[rm])) if np.any(rm) else 99.0

        self._last_front = front
        self._last_left = left
        self._last_right = right

    def publish_master(self):
        msg = String()
        msg.data = (f"4,{self._last_front:.2f},"
                    f"{self._last_left:.2f},{self._last_right:.2f}")
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleLidarNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
