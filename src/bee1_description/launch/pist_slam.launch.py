#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pist SLAM launch (slam_toolbox 2D)
==================================
Pist (duz+bariyerli) icin 2D SLAM. Town02/FAST-LIO'ya dokunmaz.

Akis:
  /carla/ego_vehicle/lidar (3D) --> pointcloud_to_laserscan --> /scan (2D)
  /carla/ego_vehicle/odometry --> pist_odom_tf --> odom->ego_vehicle
                                                          --> slam_toolbox --> map->odom + 2D harita

KULLANIM (pist altyapisi calisirken: CARLA+world+bridge+spawn):
  ros2 launch bee1_description pist_slam.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('bee1_description')
    p2l_config = os.path.join(pkg_share, 'config', 'pointcloud_to_laserscan_pist.yaml')
    slam_config = os.path.join(pkg_share, 'config', 'slam_toolbox_pist.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    args = [DeclareLaunchArgument('use_sim_time', default_value='true')]

    odom_tf = Node(
        package='bee1_description',
        executable='pist_odom_tf',
        name='pist_odom_tf',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    p2l = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[p2l_config, {'use_sim_time': use_sim_time}],
        remappings=[
            ('cloud_in', '/carla/ego_vehicle/lidar'),
            ('scan', '/scan'),
        ],
    )

    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_config, {'use_sim_time': use_sim_time}],
    )

    return LaunchDescription(args + [odom_tf, p2l, slam])
