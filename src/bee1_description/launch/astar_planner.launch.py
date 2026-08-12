#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
astar_planner.launch.py — KTR-uyumlu A* planner test launch'i (Team NeuraVix)
Konum: bee1_description/launch/

map_server (kayitli pist haritasi) + lifecycle_manager (otomatik aktivasyon)
+ astar_planner_node. Localization BEKLENMEZ; baslangic/hedef RViz'den verilir.

Calistirma:
  ros2 launch bee1_description astar_planner.launch.py \
      map_yaml:=/home/neuravix/Desktop/carla-pist/pist_haritasi.yaml

Sonra RViz'de:
  - Fixed Frame = map
  - Add -> Map      (topic: /map)
  - Add -> Path     (topic: /planned_path)
  - "2D Pose Estimate" ile baslangici, "2D Goal Pose" ile hedefi tikla.

Gereken paketler:
  sudo apt install ros-humble-nav2-map-server ros-humble-nav2-lifecycle-manager
"""
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    map_yaml = LaunchConfiguration("map_yaml")
    plan_res = LaunchConfiguration("plan_resolution")
    base_frame = LaunchConfiguration("base_frame")
    use_tf_pose = LaunchConfiguration("use_tf_pose")

    default_map = os.path.expanduser(
        "~/Desktop/carla-pist/pist_haritasi.yaml")

    return LaunchDescription([
        DeclareLaunchArgument("map_yaml", default_value=default_map,
                              description="Kayitli OccupancyGrid .yaml yolu"),
        DeclareLaunchArgument("plan_resolution", default_value="0.20",
                              description="Planlama izgara cozunurlugu [m]"),
        DeclareLaunchArgument("base_frame", default_value="ego_vehicle",
                              description="Robot frame'i (pist: ego_vehicle)"),
        DeclareLaunchArgument("use_tf_pose", default_value="false",
                              description="true: TF'den poz (localization "
                                          "calisinca); false: RViz initialpose"),

        # 1) map_server — kayitli haritayi /map'e yayinlar (latched)
        Node(package="nav2_map_server", executable="map_server",
             name="map_server", output="screen",
             parameters=[{"yaml_filename": map_yaml,
                          "use_sim_time": True,
                          "topic_name": "map",
                          "frame_id": "map"}]),

        # 2) lifecycle_manager — map_server'i otomatik configure+activate eder
        Node(package="nav2_lifecycle_manager",
             executable="lifecycle_manager",
             name="lifecycle_manager_map", output="screen",
             parameters=[{"use_sim_time": True,
                          "autostart": True,
                          "node_names": ["map_server"]}]),

        # 3) A* planner
        Node(package="bee1_description", executable="astar_planner_node",
             name="astar_planner_node", output="screen",
             parameters=[{"map_frame": "map",
                          "base_frame": base_frame,
                          "plan_resolution": plan_res,
                          "use_tf_pose": use_tf_pose,
                          "use_sim_time": True}]),
    ])
