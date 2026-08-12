#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pist Localization launch - GERÇEK ARAÇ (slam_toolbox localization modu)
=======================================================================
YARIŞ MODU. pist_localization.launch.py'nin gerçek araç karşılığı.

Önceden pist_slam_real.launch.py ile çıkarılıp kaydedilmiş haritayı
(pist_haritasi.posegraph + .data) yükler, harita KURMAZ; gelen /scan'i
hazır haritaya eşleştirip aracın konumunu bulur (AMCL gibi).

pist_slam_real'den tek fark 3. node: async_slam_toolbox_node yerine
localization_slam_toolbox_node + localization config'i.
can_odom + pointcloud_to_laserscan AYNI.

KULLANIM (araçta, smart_can_stuff CAN köprüsü + bringup çalışırken):
  ros2 launch bee1_description pist_localization_real.launch.py \
      map_file:=/root/maps/pist_haritasi
  # (map_file UZANTISIZ verilir; .posegraph + .data otomatik bulunur)

Kalibrasyon/sensör argümanları pist_slam_real ile aynı:
  lidar_topic, use_imu_yaw, imu_topic, steer_feedback_gain,
  steer_feedback_offset, speed_scale

Başlangıç pozu: config'te map_start_pose, ya da RViz "2D Pose Estimate".
Araç yarışa hep start çizgisinden başlayacaksa harita çıkarma turuna da
start çizgisinden başla - o zaman map_start_pose: [0,0,0] doğru olur.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('bee1_description')
    p2l_config = os.path.join(pkg_share, 'config', 'pointcloud_to_laserscan_real.yaml')
    slam_config = os.path.join(pkg_share, 'config', 'slam_toolbox_pist_localization_real.yaml')
    ekf_config = os.path.join(pkg_share, 'config', 'ekf_odom_real.yaml')

    lidar_topic = LaunchConfiguration('lidar_topic')
    map_file = LaunchConfiguration('map_file')
    use_imu_yaw = LaunchConfiguration('use_imu_yaw')
    use_imu_orientation = LaunchConfiguration('use_imu_orientation')
    imu_topic = LaunchConfiguration('imu_topic')
    steer_gain = LaunchConfiguration('steer_feedback_gain')
    steer_offset = LaunchConfiguration('steer_feedback_offset')
    speed_scale = LaunchConfiguration('speed_scale')
    speed_topic = LaunchConfiguration('speed_topic')
    use_ekf = LaunchConfiguration('use_ekf')

    args = [
        DeclareLaunchArgument('map_file',
                              default_value='/root/maps/pist_haritasi',
                              description='Kayıtlı posegraph yolu, UZANTISIZ'),
        # use_ekf: yarista KRITIK - odom ziplarsa scan-match kilidi kacar,
        # konum sicrar, pure-pursuit/A* hayalet sicramaya tepki verir. Default
        # false = kanitlanmis can_odom-TF yolu. EKF_DRIFT_COZUMU.txt.
        DeclareLaunchArgument('use_ekf', default_value='false',
                              description='true: odom->base_link EKF surer (can_odom TF kapanir)'),
        DeclareLaunchArgument('lidar_topic', default_value='/velodyne_points'),
        DeclareLaunchArgument('use_imu_yaw', default_value='true'),
        DeclareLaunchArgument('use_imu_orientation', default_value='false'),
        DeclareLaunchArgument('imu_topic', default_value='/imu/data'),
        # Direksiyon kalibrasyonu 2026-07-13 (bkz. pist_slam_real / can_odom rev5)
        DeclareLaunchArgument('steer_feedback_gain', default_value='-0.02322'),
        DeclareLaunchArgument('steer_feedback_offset', default_value='2.0'),
        DeclareLaunchArgument('speed_scale', default_value='0.31627'),
        # 5. oturum bulgusu: canlı hız topic'i FB_VehicleSpeed (bkz. pist_slam_real)
        DeclareLaunchArgument('speed_topic', default_value='/beemobs/FB_VehicleSpeed'),
    ]

    # 1) CAN odometri (mapping ile aynı). odom mesaji her iki modda akar;
    #    fark odom->base_link TF'ini kimin yayinladigi (bkz. pist_slam_real).
    _can_odom_params = {
        'use_sim_time': False,
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
        parameters=[ekf_config, {'use_sim_time': False}],
        condition=IfCondition(use_ekf),
    )

    # 2) 3D bulut -> 2D scan (mapping ile aynı config)
    p2l = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[p2l_config, {'use_sim_time': False}],
        remappings=[
            ('cloud_in', lidar_topic),
            # /scan değil: host velodyne_laserscan_node çakışması
            # (bkz. pist_slam_real.launch.py'deki not)
            ('scan', '/scan_bee1'),
        ],
    )

    # 3) slam_toolbox LOCALIZATION modu (kayıtlı haritayı yükler)
    slam = Node(
        package='slam_toolbox',
        executable='localization_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_config,
            {'use_sim_time': False,
             'map_file_name': map_file},
        ],
    )

    return LaunchDescription(
        args + [can_odom_tf, can_odom_notf, ekf_odom, p2l, slam])
