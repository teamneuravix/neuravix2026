#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asama 3 - Point Cloud On Isleme Dugumu (numpy vektorize)
========================================================
Ham LIDAR bulutunu FAST-LIO'ya vermeden once iki filtreden gecirir,
ayrica FAST-LIO'nun istedigi 'time' ve 'intensity' alanlarini uretir.

  /carla/ego_vehicle/lidar  (ham: x,y,z,intensity - time YOK)
        |
        v  1) Govde kirpma: arac govdesi icindeki noktalari AT
        v  2) Zemin filtre:  zemin altindaki noktalari AT
        v  3) time alani ekle: azimuttan per-point zaman damgasi
        |
        v
  /lidar/filtered  (x,y,z,intensity,time)  --> FAST-LIO

NEDEN time alani: CARLA per-point timestamp uretmiyor. FAST-LIO hareket
bozulmasi (motion distortion) duzeltmesi icin her noktanin tarama icindeki
zamanini ister. VLP-16 bir turu 1/scan_rate saniyede tamamlar; noktanin
azimut acisi (atan2(y,x)) tarama icindeki konumunu -> zamanini verir.

FRAME: lidar_link (sensorun kendi) frame'inde, TF donusumu YOK.
  Sinirlar base_link'ten lidar_link'e kaydirildi (LIDAR base_link'in
  0.177 onunde, 0.620 ustunde): lidar_z = base_z - 0.620.

KULLANIM:
  ros2 run bee1_description pointcloud_filter
"""

import struct
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
from sensor_msgs_py import point_cloud2


class PointCloudFilter(Node):
    def __init__(self):
        super().__init__('pointcloud_filter')

        # -- Parametreler --
        self.declare_parameter('input_topic', '/carla/ego_vehicle/lidar')
        self.declare_parameter('output_topic', '/lidar/filtered')

        # Govde kutusu sinirlari (lidar_link frame'inde) - bu kutu ICI silinir
        self.declare_parameter('ego_min_x', -2.677)
        self.declare_parameter('ego_max_x', 0.423)
        self.declare_parameter('ego_min_y', -0.7)
        self.declare_parameter('ego_max_y', 0.7)
        self.declare_parameter('ego_min_z', -0.720)
        self.declare_parameter('ego_max_z', 1.380)

        # Zemin esigi (lidar_link frame'inde) - bunun ALTI silinir
        self.declare_parameter('ground_z', -0.470)

        # VLP-16 tarama suresi (saniye). 10 Hz -> 0.1s
        self.declare_parameter('scan_period', 0.1)

        p = self.get_parameter
        self.in_topic = p('input_topic').value
        self.out_topic = p('output_topic').value
        self.ego = (
            p('ego_min_x').value, p('ego_max_x').value,
            p('ego_min_y').value, p('ego_max_y').value,
            p('ego_min_z').value, p('ego_max_z').value,
        )
        self.ground_z = p('ground_z').value
        self.scan_period = p('scan_period').value

        # Cikti alan tanimlari: x,y,z,intensity,time (hepsi float32)
        # FAST-LIO velodyne preprocess bu alanlari bekler.
        self.out_fields = [
            PointField(name='x', offset=0,  datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4,  datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8,  datatype=PointField.FLOAT32, count=1),
            PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1),
            PointField(name='time', offset=16, datatype=PointField.FLOAT32, count=1),
        ]

        self.sub = self.create_subscription(
            PointCloud2, self.in_topic, self.cb, 10)
        self.pub = self.create_publisher(
            PointCloud2, self.out_topic, 10)

        self._n = 0
        self.get_logger().info(
            f'Filtre basladi: {self.in_topic} -> {self.out_topic} '
            f'(lidar_link frame, time alani uretiliyor)')

    def cb(self, msg: PointCloud2):
        # x,y,z,intensity oku (CARLA bu dordunu veriyor)
        arr = point_cloud2.read_points_numpy(
            msg, field_names=('x', 'y', 'z', 'intensity'), skip_nans=True)
        if arr.shape[0] == 0:
            self.pub.publish(msg)
            return

        x = arr[:, 0]
        y = arr[:, 1]
        z = arr[:, 2]
        intensity = arr[:, 3]

        mnx, mxx, mny, mxy, mnz, mxz = self.ego

        # 1) Govde kutusu ICI -> at
        in_ego = (
            (x >= mnx) & (x <= mxx) &
            (y >= mny) & (y <= mxy) &
            (z >= mnz) & (z <= mxz)
        )
        # 2) Zemin alti -> at
        below_ground = z < self.ground_z
        # Tut: govde DISI ve zemin USTU
        keep = (~in_ego) & (~below_ground)

        xf = x[keep]
        yf = y[keep]
        zf = z[keep]
        intf = intensity[keep]

        # 3) time alani: azimut acisindan per-point zaman.
        # Velodyne saat yonunde doner; azimut = atan2(y,x) [-pi,pi].
        # Tarama basini -pi kabul edip [0, scan_period] araligina olcekle.
        az = np.arctan2(yf, xf)                 # [-pi, pi]
        frac = (az + np.pi) / (2.0 * np.pi)     # [0, 1]
        t = (frac * self.scan_period).astype(np.float32)

        # Structured array kur ve manuel PointCloud2 olustur
        n = xf.shape[0]
        cloud = np.zeros(n, dtype=[
            ('x', np.float32), ('y', np.float32), ('z', np.float32),
            ('intensity', np.float32), ('time', np.float32)])
        cloud['x'] = xf.astype(np.float32)
        cloud['y'] = yf.astype(np.float32)
        cloud['z'] = zf.astype(np.float32)
        cloud['intensity'] = intf.astype(np.float32)
        cloud['time'] = t

        out = PointCloud2()
        out.header = msg.header          # ayni frame_id, ayni stamp
        out.height = 1
        out.width = n
        out.fields = self.out_fields
        out.is_bigendian = False
        out.point_step = 20              # 5 alan * 4 byte
        out.row_step = out.point_step * n
        out.is_dense = True
        out.data = cloud.tobytes()
        self.pub.publish(out)

        self._n += 1
        if self._n % 100 == 0:
            total = arr.shape[0]
            self.get_logger().info(
                f'nokta: {total} -> {n} '
                f'(govde at: {int(in_ego.sum())}, '
                f'zemin at: {int(below_ground.sum())}, time alani eklendi)')


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudFilter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
