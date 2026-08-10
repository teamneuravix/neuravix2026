#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
astar_planner_node.py — KTR-uyumlu A* planner'in ROS 2 entegrasyonu (Team NeuraVix)
Konum: bee1_description/scripts/  (astar_planner.py ile AYNI dizinde)

Pist sistemine (slam_toolbox + map_server) gore uyarlanmistir:
  - Harita        : /map  (map_server'in yukledigi kayitli OccupancyGrid)
  - Baslangic poz : RViz "2D Pose Estimate" -> /initialpose  (test icin)
                    veya TF map->base_frame (localization calisinca, use_tf_pose:=true)
  - Hedef         : RViz "2D Goal Pose"  -> /goal_pose
  - Cikti         : /planned_path (nav_msgs/Path) + /velocity_profile (Float32MultiArray)

Harita cok ince cozunurlukteyse (orn. slam_toolbox 0.05 m), planlama icin
plan_resolution'a (varsayilan 0.20 m) kabalastirilir; A* hizli kalir, harita
guvenli tarafta (blokta engel varsa engel) birlestirilir.

Parametreler:
  map_frame (str)="map" | base_frame (str)="ego_vehicle" (Town02'de base_link)
  plan_resolution (float)=0.20 | use_tf_pose (bool)=False
  replan_rate_hz (float)=5.0 | waypoint_threshold_m (float)=0.8
"""
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy

from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from std_msgs.msg import Float32MultiArray

import tf2_ros
from tf2_ros import TransformException

from astar_planner import AStarPlanner, OCC_OBSTACLE, OCC_FREE


def occupancy_to_binary(data, h, w, occ_thresh=50, unknown_is_obstacle=True):
    g = np.array(data, dtype=np.int16).reshape(h, w)
    occ = g >= occ_thresh
    if unknown_is_obstacle:
        occ |= (g < 0)
    return occ


def block_reduce_occupied(occ, factor):
    if factor <= 1:
        return occ
    h, w = occ.shape
    h2, w2 = (h // factor) * factor, (w // factor) * factor
    occ = occ[:h2, :w2].reshape(h2 // factor, factor, w2 // factor, factor)
    return occ.any(axis=(1, 3))


class AStarPlannerNode(Node):
    def __init__(self):
        super().__init__("astar_planner_node")

        self.declare_parameter("map_frame", "map")
        self.declare_parameter("base_frame", "ego_vehicle")
        self.declare_parameter("plan_resolution", 0.20)
        self.declare_parameter("use_tf_pose", False)
        self.declare_parameter("replan_rate_hz", 5.0)
        self.declare_parameter("waypoint_threshold_m", 0.8)

        self.map_frame = self.get_parameter("map_frame").value
        self.base_frame = self.get_parameter("base_frame").value
        self.plan_res = float(self.get_parameter("plan_resolution").value)
        self.use_tf_pose = bool(self.get_parameter("use_tf_pose").value)

        self.planner = None
        self.current_pose = None
        self.goal = None

        map_qos = QoSProfile(depth=1)
        map_qos.durability = QoSDurabilityPolicy.TRANSIENT_LOCAL
        map_qos.reliability = QoSReliabilityPolicy.RELIABLE
        self.create_subscription(OccupancyGrid, "/map", self.cb_map, map_qos)

        self.create_subscription(PoseWithCovarianceStamped, "/initialpose",
                                 self.cb_initialpose, 10)
        self.create_subscription(PoseStamped, "/goal_pose", self.cb_goal, 1)

        self.pub_path = self.create_publisher(Path, "/planned_path", 1)
        self.pub_vel = self.create_publisher(Float32MultiArray,
                                             "/velocity_profile", 1)

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        rate = float(self.get_parameter("replan_rate_hz").value)
        self.create_timer(1.0 / rate, self.tick)

        self.get_logger().info(
            f"A* planner hazir | map_frame={self.map_frame} "
            f"base_frame={self.base_frame} plan_res={self.plan_res} m "
            f"use_tf_pose={self.use_tf_pose}")
        self.get_logger().info("/map bekleniyor. Baslangic: RViz "
                               "'2D Pose Estimate', Hedef: '2D Goal Pose'.")

    def cb_map(self, msg: OccupancyGrid):
        w, h = msg.info.width, msg.info.height
        res = msg.info.resolution
        origin = (msg.info.origin.position.x, msg.info.origin.position.y)
        occ = occupancy_to_binary(msg.data, h, w)
        factor = max(1, int(round(self.plan_res / res)))
        occ_ds = block_reduce_occupied(occ, factor)
        plan_res = res * factor
        grid = np.where(occ_ds, OCC_OBSTACLE, OCC_FREE).astype(np.uint8)
        gh, gw = grid.shape
        self.planner = AStarPlanner(grid_width=gw, grid_height=gh,
                                    resolution=plan_res, origin=origin)
        self.planner.set_static_map(grid)
        self.get_logger().info(
            f"Harita alindi: {w}x{h}@{res:.3f}m -> {gw}x{gh}@{plan_res:.2f}m "
            f"(kabalastirma x{factor}), inflation "
            f"{self.planner.inflation_m:.2f} m")

    def cb_initialpose(self, msg: PoseWithCovarianceStamped):
        if self.use_tf_pose:
            return
        p = msg.pose.pose.position
        self.current_pose = (p.x, p.y)
        self.get_logger().info(
            f"Baslangic (RViz): ({p.x:.1f}, {p.y:.1f})")

    def cb_goal(self, msg: PoseStamped):
        self.goal = (msg.pose.position.x, msg.pose.position.y)
        self.get_logger().info(
            f"Hedef (RViz): ({self.goal[0]:.1f}, {self.goal[1]:.1f})")
        self._plan_now()

    def _update_pose_from_tf(self):
        try:
            t = self.tf_buffer.lookup_transform(
                self.map_frame, self.base_frame, rclpy.time.Time())
            self.current_pose = (t.transform.translation.x,
                                 t.transform.translation.y)
        except TransformException:
            pass

    def _plan_now(self):
        if self.planner is None:
            self.get_logger().warn("Harita yok — once map_server.")
            return
        if self.use_tf_pose:
            self._update_pose_from_tf()
        if self.current_pose is None:
            self.get_logger().warn("Baslangic pozu yok — RViz "
                                   "'2D Pose Estimate' ver.")
            return
        if self.goal is None:
            return
        path = self.planner.plan_path(self.current_pose, self.goal)
        if not path:
            self.pub_vel.publish(Float32MultiArray(data=[0.0]))
            self.get_logger().warn("Gecerli rota yok (ulasilamaz/engelli).")
            return
        self._publish_plan()
        self.get_logger().info(
            f"Rota: {len(path)} nokta, maks egrilik "
            f"{self.planner._last_curvature.max():.3f} 1/m")

    def tick(self):
        if self.planner is None or self.goal is None:
            return
        if self.use_tf_pose:
            self._update_pose_from_tf()
            if self.current_pose is not None and self.planner.path_world:
                self.planner.update_waypoint(
                    self.current_pose,
                    threshold=self.get_parameter(
                        "waypoint_threshold_m").value)

    def _publish_plan(self):
        msg = Path()
        msg.header.frame_id = self.map_frame
        msg.header.stamp = self.get_clock().now().to_msg()
        for (x, y) in self.planner.path_world:
            ps = PoseStamped()
            ps.header = msg.header
            ps.pose.position.x = float(x)
            ps.pose.position.y = float(y)
            ps.pose.orientation.w = 1.0
            msg.poses.append(ps)
        self.pub_path.publish(msg)
        self.pub_vel.publish(Float32MultiArray(
            data=[float(v) for v in self.planner.velocity_profile]))


def main():
    rclpy.init()
    node = AStarPlannerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
