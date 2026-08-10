#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odometri Frame Relay
====================
FAST-LIO /Odometry topic'ini alir, frame isimlerini yeniden yazip
/odometry/fastlio olarak yeniden yayinlar.

  /Odometry  (frame_id: camera_init, child: body)
        |
        v  [relay: frame isimlerini degistir]
        |
  /odometry/fastlio  (frame_id: odom, child: base_link)  --> EKF girdisi

NEDEN: FAST-LIO camera_init/body isimlerini hardcoded yayinliyor, config'ten
degistirilemiyor. EKF ise odom/base_link bekliyor. Bu relay ikisini koprular.
Sadece TOPIC icerigi yeniden adlandirilir; FAST-LIO'nun kendi TF'ine
dokunulmaz (o boşta kalir, EKF tek TF otoritesi olur).

KULLANIM:
  ros2 run bee1_description odom_relay
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class OdomRelay(Node):
    def __init__(self):
        super().__init__('odom_relay')

        self.declare_parameter('input_topic', '/Odometry')
        self.declare_parameter('output_topic', '/odometry/fastlio')
        self.declare_parameter('out_frame', 'odom')
        self.declare_parameter('out_child_frame', 'base_link')

        self.in_topic = self.get_parameter('input_topic').value
        self.out_topic = self.get_parameter('output_topic').value
        self.out_frame = self.get_parameter('out_frame').value
        self.out_child = self.get_parameter('out_child_frame').value

        self.sub = self.create_subscription(
            Odometry, self.in_topic, self.cb, 10)
        self.pub = self.create_publisher(Odometry, self.out_topic, 10)

        self.get_logger().info(
            f'Odom relay: {self.in_topic} (camera_init/body) -> '
            f'{self.out_topic} ({self.out_frame}/{self.out_child})')

    def cb(self, msg: Odometry):
        # Sadece frame isimlerini degistir, geri kalan (pose, twist) ayni kalir
        msg.header.frame_id = self.out_frame
        msg.child_frame_id = self.out_child
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = OdomRelay()
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
