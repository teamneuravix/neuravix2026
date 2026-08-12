#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pist SLAM launch - GERÇEK ARAÇ (slam_toolbox 2D)
================================================
pist_slam.launch.py'nin gerçek araç karşılığı. CARLA'ya dokunmaz.

Sim'den farklar:
  - pist_odom_tf (CARLA odom köprüsü) yerine can_odom (CAN dead reckoning)
  - LiDAR topic'i /carla/ego_vehicle/lidar yerine gerçek Velodyne
    (varsayılan /velodyne_points - araçta 'ros2 topic list' ile doğrula,
    farklıysa lidar_topic:=... argümanıyla ver)
  - base_frame ego_vehicle yerine base_link
  - use_sim_time: false (gerçek saat; /clock YOK)

Akış:
  /beemobs/* (CAN fb) --> can_odom --> odom->base_link (TF + /odometry/can_wheel)
  <lidar_topic> (3D)  --> pointcloud_to_laserscan --> /scan (2D)
                                     --> slam_toolbox --> map->odom + 2D harita

KULLANIM (araçta, smart_can_stuff CAN köprüsü çalışırken):
  ros2 launch bee1_description pist_slam_real.launch.py
  # LiDAR topic'i farklıysa:
  ros2 launch bee1_description pist_slam_real.launch.py \
      lidar_topic:=/points_raw
  # İkinci testte IMU yaw denemesi:
  ros2 launch bee1_description pist_slam_real.launch.py \
      use_imu_yaw:=true imu_topic:=/imu/data

NOT: base_link -> lidar_link TF'i için bee1_bringup.launch.py de
     çalışıyor olmalı (use_sim_time:=false ile) - yoksa
     pointcloud_to_laserscan dönüşüm bulamaz.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('bee1_description')
    p2l_config = os.path.join(pkg_share, 'config', 'pointcloud_to_laserscan_real.yaml')
    slam_config = os.path.join(pkg_share, 'config', 'slam_toolbox_pist_real.yaml')
    ekf_config = os.path.join(pkg_share, 'config', 'ekf_odom_real.yaml')

    lidar_topic = LaunchConfiguration('lidar_topic')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_imu_yaw = LaunchConfiguration('use_imu_yaw')
    use_imu_orientation = LaunchConfiguration('use_imu_orientation')
    imu_topic = LaunchConfiguration('imu_topic')
    steer_gain = LaunchConfiguration('steer_feedback_gain')
    steer_offset = LaunchConfiguration('steer_feedback_offset')
    speed_scale = LaunchConfiguration('speed_scale')
    speed_topic = LaunchConfiguration('speed_topic')
    use_ekf = LaunchConfiguration('use_ekf')
    # bool'a zorla (string 'true'/'false' -> bool); tum node'lara verilir.
    sim_time = ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)

    args = [
        DeclareLaunchArgument('lidar_topic', default_value='/velodyne_points',
                              description='Gerçek Velodyne PointCloud2 topic (araçta doğrula)'),
        # Canlı araçta false (gerçek saat). OFFLINE bag replay'de true + bag'i
        # --clock ile oynat, yoksa can_odom "şimdi", scan "dün" damgalanır ->
        # slam TF eşleştiremez, harita çıkmaz.
        DeclareLaunchArgument('use_sim_time', default_value='false',
                              description='Offline bag replay icin true (+ bag play --clock)'),
        # use_ekf:=true -> odom->base_link'i robot_localization EKF surer
        # (can_odom publish_tf=false), puruzsuz/glitch-reddeden prior. Default
        # false = kanitlanmis can_odom-TF yolu. EKF_DRIFT_COZUMU.txt.
        DeclareLaunchArgument('use_ekf', default_value='false',
                              description='true: odom->base_link EKF surer (can_odom TF kapanir)'),
        DeclareLaunchArgument('use_imu_yaw', default_value='true',
                              description='true: yaw_rate XSENS gyro\'dan entegre (bias birikir)'),
        DeclareLaunchArgument('use_imu_orientation', default_value='false',
                              description='true: yaw XSENS AHRS mutlak orientation\'dan (drift\'siz, öncelikli)'),
        DeclareLaunchArgument('imu_topic', default_value='/imu/data',
                              description='XSENS IMU topic (araçta doğrula)'),
        # Direksiyon kalibrasyonu 2026-07-13'te araçta ölçüldü:
        # ham düz=2, tam sol=-21, tam sağ=26 -> gain=-0.02322 rad/birim, offset=2
        # (detay: can_odom_node.py rev5 notu). Gerekirse launch'tan ezilebilir.
        DeclareLaunchArgument('steer_feedback_gain', default_value='-0.02322'),
        DeclareLaunchArgument('steer_feedback_offset', default_value='2.0'),
        DeclareLaunchArgument('speed_scale', default_value='0.31627',
                              description='fb_reelvehiclespeed_kmh -> m/s (uint8 km/h alanı)'),
        # 5. oturum (output11): /beemobs/fbvehiclespeed hiç yayınlanmıyordu,
        # canlı olduğu kanıtlanan topic FB_VehicleSpeed. Araçta farklıysa
        # launch'tan geçilebilsin diye argüman olarak açıldı.
        DeclareLaunchArgument('speed_topic', default_value='/beemobs/FB_VehicleSpeed',
                              description='Hız geri besleme topic\'i (Fbvehiclespeed msg)'),
    ]

    # 1) CAN odometri. odom mesaji (/odometry/can_wheel) her iki modda da akar;
    #    fark SADECE odom->base_link TF'ini KIMIN yayinladigi:
    #      use_ekf=false -> can_odom kendi TF'ini yayinlar (publish_tf=true)
    #      use_ekf=true  -> can_odom TF'i KAPATIR, TF'i EKF yayinlar
    #    Boylece odom->base_link'in DAIMA tek broadcaster'i olur (cift = ziplama).
    #    Iki ayri Node (birbirini disliyan kosullar) publish_tf'i literal bool
    #    gecmek icin -- substitution ile bool param tip cakismasini onler.
    _can_odom_params = {
        'use_sim_time': sim_time,
        'use_imu_yaw': use_imu_yaw,
        'use_imu_orientation': use_imu_orientation,
        'imu_topic': imu_topic,
        'steer_feedback_gain': steer_gain,
        'steer_feedback_offset': steer_offset,
        'speed_scale': speed_scale,
        'speed_topic': speed_topic,
    }

    can_odom_tf = Node(   # use_ekf=false: can_odom TF'i yayinlar
        package='bee1_description', executable='can_odom', name='can_odom_node',
        output='screen',
        parameters=[dict(_can_odom_params, publish_tf=True)],
        condition=UnlessCondition(use_ekf),
    )
    can_odom_notf = Node(  # use_ekf=true: can_odom TF'i KAPALI (EKF yayinlar)
        package='bee1_description', executable='can_odom', name='can_odom_node',
        output='screen',
        parameters=[dict(_can_odom_params, publish_tf=False)],
        condition=IfCondition(use_ekf),
    )

    # 1b) Lokal EKF (SADECE use_ekf=true): odom->base_link'i puruzsuz surer
    ekf_odom = Node(
        package='robot_localization', executable='ekf_node', name='ekf_odom',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': sim_time}],
        condition=IfCondition(use_ekf),
    )

    # 2) 3D bulut -> 2D scan (yükseklik penceresi config'te)
    p2l = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[p2l_config, {'use_sim_time': sim_time}],
        remappings=[
            ('cloud_in', lidar_topic),
            # /scan DEĞİL: host'un sensör launch'ındaki velodyne_laserscan_node
            # da /scan yayınlıyor (tek ring, 897/898 değişken uzunluk) ve
            # slam_toolbox onu yiyip uzunluğu tutmayan her scan'i reddediyordu
            # (6. oturum, output12: "LaserRangeScan contains 897, expected 898").
            # Kendi yükseklik-pencereli scan'imiz ayrı isimde:
            ('scan', '/scan_bee1'),
        ],
    )

    # 3) slam_toolbox mapping modu
    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_config, {'use_sim_time': sim_time}],
    )

    return LaunchDescription(
        args + [can_odom_tf, can_odom_notf, ekf_odom, p2l, slam])
