#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pist Localization launch (slam_toolbox localization modu)
=========================================================
YARIS MODU: Onceden cikarilmis haritayi (pist_haritasi.posegraph) yukler,
slam_toolbox'i LOCALIZATION modunda baslatir. Harita kurmaz; gelen /scan'i
hazir haritaya eslestirip aracin konumunu bulur (AMCL gibi).

Mapping launch'tan farki:
  - executable: localization_slam_toolbox_node (async degil)
  - config: slam_toolbox_pist_localization.yaml (mode: localization, map_file_name)
pointcloud_to_laserscan + odom koprusu AYNI (scan uretimi degismez).

KULLANIM (pist altyapisi calisirken):
  ros2 launch bee1_description pist_localization.launch.py

Baslangic pozu: config'te map_start_pose, ya da RViz "2D Pose Estimate".
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
    slam_config = os.path.join(pkg_share, 'config', 'slam_toolbox_pist_localization.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    args = [DeclareLaunchArgument('use_sim_time', default_value='true')]

    # 1) Odometri koprusu (mapping ile ayni): CARLA odom -> odom->ego_vehicle
    odom_tf = Node(
        package='bee1_description',
        executable='pist_odom_tf',
        name='pist_odom_tf',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # 2) 3D bulut -> 2D scan (mapping ile ayni, tunel-guvenli pencere)
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

    # 3) slam_toolbox LOCALIZATION modu (hazir haritayi yukler)
    slam = Node(
        package='slam_toolbox',
        executable='localization_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_config, {'use_sim_time': use_sim_time}],
    )

    return LaunchDescription(args + [odom_tf, p2l, slam])
