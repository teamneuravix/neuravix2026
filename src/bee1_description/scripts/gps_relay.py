#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPS Frame Relay
===============
CARLA GPS (/carla/ego_vehicle/gnss) frame_id'sini 'ego_vehicle/gnss'den
'gnss_link'e cevirip /gps/fixed olarak yeniden yayinlar.

NEDEN: navsat_transform, GPS anteninin base_link'e gore konumunu bulmak icin
'base_link -> <gps frame_id>' TF'ini arar. CARLA GPS'i 'ego_vehicle/gnss'
frame'inde geliyor ama bu frame bizim base_link agacinda DEGIL (REP-105'te
ayirdik). Sonuc: navsat 'Could not obtain base_link -> ego_vehicle/gnss'
hatasi verip GPS'i isleyemiyor, sifir odometri uretiyor.

URDF'imizde 'base_link -> gnss_link' (-1.440, 0, 1.390) zaten var. GPS
mesajinin frame_id'sini 'gnss_link' yapinca navsat bu transform'u bulur.

KULLANIM:
  ros2 run bee1_description gps_relay
  # navsat'in gps/fix girdisi /gps/fixed'e remap edilmeli
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix


class GpsRelay(Node):
    def __init__(self):
        super().__init__('gps_relay')

        self.declare_parameter('input_topic', '/carla/ego_vehicle/gnss')
        self.declare_parameter('output_topic', '/gps/fixed')
        self.declare_parameter('out_frame', 'gnss_link')

        self.in_topic = self.get_parameter('input_topic').value
        self.out_topic = self.get_parameter('output_topic').value
        self.out_frame = self.get_parameter('out_frame').value

        self.sub = self.create_subscription(
            NavSatFix, self.in_topic, self.cb, 10)
        self.pub = self.create_publisher(NavSatFix, self.out_topic, 10)

        self.get_logger().info(
            f'GPS relay: {self.in_topic} -> {self.out_topic} '
            f'(frame_id -> {self.out_frame})')

    def cb(self, msg: NavSatFix):
        msg.header.frame_id = self.out_frame
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = GpsRelay()
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
