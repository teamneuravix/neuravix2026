#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bee1 - Lokal Lokalizasyon launch (GPS'siz)
==========================================
Sadece lokal odometri fuzyonu. GPS/global capalama YOK.
Gercek araca gecince ekf_global + navsat eklenir (localization.launch.py).

Node'lar:
  1) odom_relay : FAST-LIO /Odometry (camera_init/body) -> /odometry/fastlio (odom/base_link)
  2) ekf_local  : /odometry/fastlio + IMU -> odom->base_link TF

Frame zinciri: odom -> base_link -> sensorler
(map->odom yok; navigasyon icin camera_init veya odom referans alinabilir)

KULLANIM (altyapi + FAST-LIO calisirken):
  ros2 launch bee1_description localization_local.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('bee1_description')
    default_config = os.path.join(pkg_share, 'config', 'ekf_navsat.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    config_file = LaunchConfiguration('config_file')

    args = [
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('config_file', default_value=default_config),
    ]

    odom_relay = Node(
        package='bee1_description',
        executable='odom_relay',
        name='odom_relay',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    ekf_local = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_local',
        output='screen',
        parameters=[config_file, {'use_sim_time': use_sim_time}],
        remappings=[
            ('odometry/filtered', '/odometry/filtered'),
        ],
    )

    return LaunchDescription(args + [odom_relay, ekf_local])
