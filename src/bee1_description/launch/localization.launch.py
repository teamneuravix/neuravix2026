#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bee1 - Lokalizasyon launch (iki EKF + navsat, REP-105 GPS fuzyonu)
==================================================================
UC node + relay:
  0) odom_relay        : FAST-LIO /Odometry (camera_init/body) -> /odometry/fastlio (odom/base_link)
  1) ekf_local         : /odometry/fastlio + IMU       -> odom->base_link TF
  2) ekf_global        : /odometry/fastlio + IMU + GPS -> map->odom TF
  3) navsat_transform  : GPS(NavSatFix) -> /odometry/gps

Frame zinciri: map --(ekf_global)--> odom --(ekf_local)--> base_link --> sensorler

KULLANIM (altyapi + FAST-LIO calisirken):
  ros2 launch bee1_description localization.launch.py
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

    # 0) Odom relay: FAST-LIO frame'lerini EKF'e uygun hale getir
    odom_relay = Node(
        package='bee1_description',
        executable='odom_relay',
        name='odom_relay',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # 1) LOKAL EKF: odom -> base_link
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

    # 2) GLOBAL EKF: map -> odom
    ekf_global = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_global',
        output='screen',
        parameters=[config_file, {'use_sim_time': use_sim_time}],
        remappings=[
            ('odometry/filtered', '/odometry/global'),
        ],
    )

    # 3) navsat_transform: GPS -> /odometry/gps
    navsat = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform_node',
        output='screen',
        parameters=[config_file, {'use_sim_time': use_sim_time}],
        remappings=[
            ('imu', '/carla/ego_vehicle/imu'),
            ('gps/fix', '/carla/ego_vehicle/gnss'),
            # navsat LOKAL EKF ciktisini girdi alir (/odometry/filtered).
            # Boylece dongu kirilir: ekf_local -> navsat -> /odometry/gps -> ekf_global
            ('odometry/filtered', '/odometry/filtered'),
            ('odometry/gps', '/odometry/gps'),
            ('gps/filtered', '/gps/filtered'),
        ],
    )

    return LaunchDescription(args + [odom_relay, ekf_local, ekf_global, navsat])
