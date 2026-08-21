#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lidar_echo_node.py — LiDAR nokta verisini TERMINALE basar (Bee1 / debug araci)

CARLA LiDAR'i (/carla/ego_vehicle/lidar, PointCloud2) abone alir, her karede:
  - frame_id, nokta sayisi
  - x/y/z min-max araligi ve ortalama menzil
  - ilk N noktanin (x, y, z, intensity) degerleri
terminale yazilir.

NOT: 'ros2 topic echo' PointCloud2'de ham byte dizisi bastigi icin okunmaz;
     bu node noktalari cozup insan-okur formatta gosterir.

Kullanim:
  ros2 run bee1_description lidar_echo
  # baska topic / daha cok ornek nokta:
  ros2 run bee1_description lidar_echo --ros-args \\
      -p input_topic:=/lidar/filtered -p sample:=10 -p every_n:=1
"""
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


class LidarEcho(Node):
    def __init__(self):
        super().__init__('lidar_echo')

        self.declare_parameter('input_topic', '/carla/ego_vehicle/lidar')
        self.declare_parameter('sample', 5)       # terminale basilacak ornek nokta sayisi
        self.declare_parameter('every_n', 1)      # her N karede bir bas (1 = her kare)

        self.in_topic = self.get_parameter('input_topic').value
        self.sample = int(self.get_parameter('sample').value)
        self.every_n = max(1, int(self.get_parameter('every_n').value))

        self.sub = self.create_subscription(
            PointCloud2, self.in_topic, self.cb, 10)

        self._n = 0
        self.get_logger().info(
            f"LiDAR echo basladi -> '{self.in_topic}' dinleniyor "
            f"(her {self.every_n} karede, {self.sample} ornek nokta)")

    def cb(self, msg: PointCloud2):
        self._n += 1
        if self._n % self.every_n != 0:
            return

        # x,y,z,intensity oku. read_points_numpy DEGIL: Velodyne bulutunda
        # ring alani uint16 oldugu icin read_points_numpy "All fields need
        # to have the same datatype" assert'iyle patliyor (gercek aracta
        # obstacle_lidar'da yasandi, 2026-07-12). read_points structured
        # array dondurur, karisik tiplerden etkilenmez.
        arr = point_cloud2.read_points(
            msg, field_names=('x', 'y', 'z', 'intensity'), skip_nans=True)

        total = arr.shape[0]
        if total == 0:
            self.get_logger().warn(f"[{self._n}] bos bulut (frame={msg.header.frame_id})")
            return

        x = np.asarray(arr['x'], dtype=np.float32)
        y = np.asarray(arr['y'], dtype=np.float32)
        z = np.asarray(arr['z'], dtype=np.float32)
        inten = np.asarray(arr['intensity'], dtype=np.float32)
        rng = np.sqrt(x * x + y * y + z * z)

        print('-' * 60)
        print(f"[kare {self._n}] frame_id={msg.header.frame_id}  nokta={total}")
        print(f"  x: [{x.min():7.2f}, {x.max():7.2f}]   "
              f"y: [{y.min():7.2f}, {y.max():7.2f}]   "
              f"z: [{z.min():7.2f}, {z.max():7.2f}]  (m)")
        print(f"  menzil: min={rng.min():.2f}  max={rng.max():.2f}  "
              f"ort={rng.mean():.2f} m   |   intensity ort={inten.mean():.1f}")

        k = min(self.sample, total)
        print(f"  ilk {k} nokta (x, y, z, intensity):")
        for i in range(k):
            print(f"    {i:>3}: ({x[i]:7.2f}, {y[i]:7.2f}, {z[i]:6.2f})  "
                  f"i={inten[i]:.1f}")


def main(args=None):
    rclpy.init(args=args)
    node = LidarEcho()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
