#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bee1 bringup launch
===================
Gorevler:
  1) robot_state_publisher: URDF'i isler, tum sensor frame'lerini
     (base_link -> lidar_link, camera_*, imu_link, gnss_link) TF'e koyar.
  2) (OPSIYONEL) CARLA ego_vehicle -> base_link static transform.

ONEMLI - base_link'i kim suruyor:
  REP-105'te base_link'in parent'i odom olmali ve bunu EKF (robot_localization)
  surer. Bu yuzden ego_vehicle->base_link static transform'u VARSAYILAN OLARAK
  KAPALI (publish_ego_to_base:=false). base_link iki parent alamaz; EKF
  calisirken bringup base_link'i surmemelidir.

  publish_ego_to_base:=false (varsayilan) -> EKF base_link'i surer (REP-105).
                                              Lokalizasyonlu normal kullanim.
  publish_ego_to_base:=true  -> bringup ego_vehicle->base_link surer.
                                 Sadece EKF YOKKEN, tek basina FAST-LIO/URDF
                                 testi icin. Bu modda ego_to_base_x/z ofsetini ver.

KULLANIM:
  # Lokalizasyonlu (normal):
  ros2 launch bee1_description bee1_bringup.launch.py

  # EKF olmadan tek basina test (eski davranis):
  ros2 launch bee1_description bee1_bringup.launch.py \\
      publish_ego_to_base:=true ego_to_base_x:=0.223 ego_to_base_z:=0.980
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('bee1_description')
    xacro_path = os.path.join(pkg_share, 'urdf', 'bee1_robotaxi.urdf.xacro')

    args = [
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='CARLA /clock kullan'),
        DeclareLaunchArgument('ego_frame', default_value='ego_vehicle',
                              description='CARLA arac frame adi'),
        # base_link'i EKF mi bringup mi sursun? Varsayilan: EKF (false).
        DeclareLaunchArgument('publish_ego_to_base', default_value='false',
                              description='true: bringup ego_vehicle->base_link surer '
                                          '(sadece EKF yokken). false: EKF surer (REP-105).'),
        DeclareLaunchArgument('ego_to_base_x', default_value='0.0',
                              description='ego_vehicle -> base_link x ofseti (m)'),
        DeclareLaunchArgument('ego_to_base_y', default_value='0.0'),
        DeclareLaunchArgument('ego_to_base_z', default_value='0.0'),
        DeclareLaunchArgument('ego_to_base_yaw', default_value='0.0',
                              description='ego_vehicle -> base_link yaw (rad)'),
    ]

    use_sim_time = LaunchConfiguration('use_sim_time')
    ego_frame = LaunchConfiguration('ego_frame')

    robot_description = ParameterValue(
        Command(['xacro ', xacro_path]),
        value_type=str,
    )

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }],
    )

    jsp = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # ego_vehicle -> base_link static transform.
    # SADECE publish_ego_to_base:=true iken yayinlanir (EKF yokken).
    ego_to_base = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='ego_to_base_link',
        output='screen',
        condition=IfCondition(LaunchConfiguration('publish_ego_to_base')),
        arguments=[
            '--x', LaunchConfiguration('ego_to_base_x'),
            '--y', LaunchConfiguration('ego_to_base_y'),
            '--z', LaunchConfiguration('ego_to_base_z'),
            '--yaw', LaunchConfiguration('ego_to_base_yaw'),
            '--pitch', '0.0',
            '--roll', '0.0',
            '--frame-id', ego_frame,
            '--child-frame-id', 'base_link',
        ],
    )

    return LaunchDescription(args + [rsp, jsp, ego_to_base])
