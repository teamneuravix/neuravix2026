#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""map -> base_link TF'ini CSV'ye yazar (lokalizasyon dogrulugu olcumu icin).
   python3 pose_logger.py <cikti.csv> --ros-args -p use_sim_time:=true"""
import sys, csv, math
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
import tf2_ros


class PoseLogger(Node):
    def __init__(self, path):
        super().__init__('pose_logger')
        # use_sim_time'i BURADA declare ETME: --ros-args -p ile verildiginde
        # rclpy onu zaten otomatik tanimliyor.
        self.buf = tf2_ros.Buffer(cache_time=Duration(seconds=30))
        self.lis = tf2_ros.TransformListener(self.buf, self)
        self.f = open(path, 'w', newline='')
        self.w = csv.writer(self.f)
        self.w.writerow(['t', 'x', 'y', 'yaw'])
        self.n = 0
        self.miss = 0
        self.create_timer(0.1, self.tick)          # 10 Hz

    def tick(self):
        try:
            tr = self.buf.lookup_transform('map', 'base_link', rclpy.time.Time())
        except Exception:
            self.miss += 1
            if self.miss % 100 == 0:
                self.get_logger().warn(f'map->base_link yok ({self.miss} deneme)')
            return
        t = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
        q = tr.transform.rotation
        yaw = math.atan2(2 * (q.w * q.z + q.x * q.y),
                         1 - 2 * (q.y * q.y + q.z * q.z))
        self.w.writerow([f'{t:.3f}',
                         f'{tr.transform.translation.x:.4f}',
                         f'{tr.transform.translation.y:.4f}',
                         f'{yaw:.5f}'])
        self.n += 1
        if self.n % 300 == 0:
            self.f.flush()
            self.get_logger().info(f'{self.n} poz yazildi (kacan: {self.miss})')


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/pose_log.csv'
    rclpy.init()
    n = PoseLogger(path)
    try:
        rclpy.spin(n)
    except KeyboardInterrupt:
        pass
    finally:
        n.f.flush(); n.f.close()
        print(f'\n{n.n} poz yazildi -> {path}  (kacan lookup: {n.miss})')
        rclpy.shutdown()


if __name__ == '__main__':
    main()
