#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pist Odometri Koprusu
=====================
CARLA /carla/ego_vehicle/odometry mesajini alip odom->ego_vehicle TF'i yayinlar.

NEDEN: slam_toolbox odom_frame->base_frame (odom->ego_vehicle) bir odometri
TF'i bekler, kendisi map->odom uretir. Bu kopru CARLA odometrisini
odom->ego_vehicle olarak verir; slam_toolbox uzerine map->odom kurar.

KULLANIM:
  ros2 run bee1_description pist_odom_tf
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped


class PistOdomTF(Node):
    def __init__(self):
        super().__init__('pist_odom_tf')
        self.declare_parameter('odom_topic', '/carla/ego_vehicle/odometry')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'ego_vehicle')

        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        topic = self.get_parameter('odom_topic').value

        self.br = TransformBroadcaster(self)
        self.sub = self.create_subscription(Odometry, topic, self.cb, 10)
        self.get_logger().info(
            f'Pist odom TF: {topic} -> {self.odom_frame}->{self.base_frame}')

    def cb(self, msg: Odometry):
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.base_frame
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation = msg.pose.pose.orientation
        self.br.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = PistOdomTF()
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
