#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Team NeuraVix - TEKNOFEST 2026 Robotaksi (Hazır Araç) — CARLA SİMÜLASYONU
Karar Beyni (FSM) + ROS 2 Köprüsü — v2 Kararlı Kontrol

Karar mantığı (FSM, direksiyon/hız/fren hesaplama) decision_brain.py'dedir ve
CARLA'dan bağımsızdır. Bu dosya sadece CARLA'ya özel I/O katmanıdır:
CarlaEgoVehicleControl çıkışı, /carla/ego_vehicle/vehicle_status hız geri
beslemesi, /carla/ego_vehicle/odometry konum geri beslemesi.

Gerçek araç eşdeğeri: neuravix_control_node_real.py (aynı decision_brain'i
kullanır, CARLA I/O'su yoktur).
"""

import time
import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Int32, Bool, String, Float32MultiArray
from carla_msgs.msg import CarlaEgoVehicleControl, CarlaEgoVehicleStatus
from nav_msgs.msg import Odometry

from .decision_brain import (
    Alkar_Function4, ROUTE, WP_REACH, WP_STR_GAIN, GRID_SCALE,
    ID_LANE, ID_SIGN, ID_OBSTACLE, ID_PLANNER,
)


# ================================================================
# ROS 2 NODE
# ================================================================
class DecisionControlNode(Node):
    def __init__(self):
        super().__init__('neuravix_decision_control_node')

        self.brain = Alkar_Function4()

        # Bee 1
        self.pub_throttle = self.create_publisher(Float32, '/beemobs/RC_THRT_DATA', 10)
        self.pub_brake    = self.create_publisher(Int32, '/beemobs/AUTONOMOUS_BrakePedalControl', 10)
        self.pub_steering = self.create_publisher(Float32, '/beemobs/RC_STR_DATA', 10)
        self.pub_signal   = self.create_publisher(Int32, '/beemobs/RC_SIGNAL_STATUS', 10)

        # CARLA
        self.pub_carla_ctrl = self.create_publisher(
            CarlaEgoVehicleControl, '/carla/ego_vehicle/vehicle_control_cmd', 10)

        # Debug
        self.pub_state    = self.create_publisher(String, '/neuravix/current_state', 10)
        self.pub_decision = self.create_publisher(Float32MultiArray, '/neuravix/decision_dump', 10)

        # /master perception kanalı
        self.sub_master    = self.create_subscription(String, '/master', self.master_cb, 10)
        self.sub_emergency = self.create_subscription(Bool, '/safety/emergency_stop', self.emergency_cb, 10)

        # CARLA hız geri beslemesi
        self.current_speed  = 0.0
        self.speed_integral = 0.0
        self.sub_status = self.create_subscription(
            CarlaEgoVehicleStatus, '/carla/ego_vehicle/vehicle_status', self.status_cb, 10)

        # FIX: Odometri aboneliği — konum takibi + A* güncelleme
        self.odom_x   = None
        self.odom_y   = None
        self.odom_yaw = None
        self.sub_odom = self.create_subscription(
            Odometry, '/carla/ego_vehicle/odometry', self._odom_cb, 10)

        # Waypoint indeksi (pure-pursuit için)
        self.wp_idx = 0

        # Şerit verisi tazelik takibi
        self._lane_steer      = 45
        self._lane_steer_time = 0.0
        self._LANE_FRESH_SEC  = 0.5

        self._last_log_state = None
        self._last_log_event = None
        self._last_hb_time   = 0.0

        self.timer = self.create_timer(0.05, self.control_loop)  # 20 Hz

        self.get_logger().info(
            "NeuraVix Decision/Control node v2 started "
            "(odometry + waypoint hybrid, Bee1 + CARLA, 20 Hz).")

    # ----------------------------------------------------------------
    # FIX: Odometri callback
    # carla-ros-bridge dönüşümü: ros_x = carla_x, ros_y = -carla_y = pist_y
    # Yaw: quaternion → standart math (CCW+, radyan)
    # ----------------------------------------------------------------
    def _odom_cb(self, msg):
        self.odom_x = msg.pose.pose.position.x   # ≈ pist_x
        self.odom_y = msg.pose.pose.position.y   # ≈ pist_y

        q = msg.pose.pose.orientation
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.odom_yaw = math.atan2(siny, cosy)

        # A* grid güncelleme (pist 0-73 m → grid 0-59 hücre)
        gx = int(self.odom_x * GRID_SCALE)
        gy = int(self.odom_y * GRID_SCALE)
        self.brain.update_position(gx, gy)

    # ----------------------------------------------------------------
    # FIX: Pure-pursuit — mevcut waypointe doğru Alkar açısı hesaplar
    # Odometri gelmemişse None döner (FSM tek başına devam eder)
    # ----------------------------------------------------------------
    def _pure_pursuit_steer(self):
        if self.odom_x is None:
            return None
        if self.wp_idx >= len(ROUTE):
            return None

        wp = ROUTE[self.wp_idx]
        dx = wp['x'] - self.odom_x
        dy = wp['y'] - self.odom_y

        # Waypoint'e ulaşıldıysa ilerle
        if math.hypot(dx, dy) < WP_REACH and self.wp_idx < len(ROUTE) - 1:
            self.wp_idx += 1
            wp = ROUTE[self.wp_idx]
            dx = wp['x'] - self.odom_x
            dy = wp['y'] - self.odom_y

        # Heading hatası (ROS frame: CCW pozitif = sola dön = Alkar > 45)
        target_yaw = math.atan2(dy, dx)
        err_rad = (target_yaw - self.odom_yaw + math.pi) % (2 * math.pi) - math.pi
        err_deg = math.degrees(err_rad)

        steer = int(45 + err_deg * WP_STR_GAIN)
        return max(15, min(75, steer))

    # ----------------------------------------------------------------
    # /master parser
    # ----------------------------------------------------------------
    def master_cb(self, msg):
        try:
            parts = [p.strip() for p in msg.data.split(',')]
            data  = [float(x) for x in parts]
            mid   = int(data[0])
        except (ValueError, IndexError):
            self.get_logger().warn(f"/master parse hatasi: '{msg.data}'")
            return

        if mid == ID_LANE:
            try:
                self._lane_steer      = float(data[1])
                self._lane_steer_time = time.time()
            except (IndexError, ValueError):
                pass
            self.brain.lane_detect_event(data)

        elif mid == ID_SIGN:
            if len(data) < 7:
                self.get_logger().warn(f"Tabela mesaji eksik: '{msg.data}'")
                return
            self.brain.sign_detect_event(data)

        elif mid == ID_OBSTACLE:
            if len(data) < 4:
                self.get_logger().warn(f"Engel mesaji eksik: '{msg.data}'")
                return
            self.brain.obstacle_event(front=data[1], left=data[2], right=data[3])

        elif mid == ID_PLANNER:
            if len(data) < 3:
                self.get_logger().warn(f"Planner mesaji eksik: '{msg.data}'")
                return
            self.brain.planner_event(data)

        else:
            self.get_logger().warn(f"Bilinmeyen /master id: {mid}")

    def emergency_cb(self, msg):
        self.brain.emergency_event(active=bool(msg.data))

    def status_cb(self, msg):
        self.current_speed = float(msg.velocity)

    # ----------------------------------------------------------------
    # Ana döngü — FIX: hibrit direksiyon karıştırması (LANE_FOLLOW'da)
    # ----------------------------------------------------------------
    def control_loop(self):
        # Mesafe tabanlı slalom (2026-07-21): CARLA'nın hız geri beslemesi
        # doğrudan m/s. Gerçek araçla aynı yolu izlesin diye sim'de de
        # beslenir — yoksa sim zaman tabanlı yedekte kalır ve araçta test
        # ettiğimiz davranıştan ayrışır.
        self.brain.update_motion(speed_mps=self.current_speed)
        self.brain._update_state_machine()
        decision = self.brain.get_decision()

        lane_fresh = (time.time() - self._lane_steer_time) < self._LANE_FRESH_SEC

        if decision['state'] == 'LANE_FOLLOW':
            wp_steer   = self._pure_pursuit_steer()

            if wp_steer is not None and lane_fresh:
                # Her iki kaynak taze: %55 waypoint + %45 şerit algısı
                blended = int(0.55 * wp_steer + 0.45 * self._lane_steer)
                decision['steering_angle'] = max(15, min(75, blended))
            elif wp_steer is not None:
                # Şerit yok/bayat: sadece waypoint
                decision['steering_angle'] = wp_steer
            # wp_steer is None: odometri yok, FSM çıktısı kullanılır

        elif lane_fresh and decision.get('lane_blend', 0.0) > 0.0:
            # Kaçınma sırasında şerit devrede (gerçek node ile aynı politika)
            w = float(decision['lane_blend'])
            blended = int((1.0 - w) * decision['steering_angle']
                          + w * self._lane_steer)
            decision['steering_angle'] = max(15, min(75, blended))

        self.publish_commands(decision)
        self.publish_debug(decision)
        self._log_decision(decision)

    def _log_decision(self, d):
        st  = d['state']
        ev  = self.brain.last_event
        now = time.time()
        changed = (st != self._last_log_state) or (ev != self._last_log_event)
        if changed or (now - self._last_hb_time > 2.0):
            tag = "[KARAR]" if changed else "[DURUM]"
            wp_info = (f"wp={self.wp_idx}/{len(ROUTE)}"
                       if self.odom_x is not None else "wp=?")
            self.get_logger().info(
                f"{tag} state={st} | steer={d['steering_angle']} "
                f"hiz={d['target_speed_kmh']:.0f} fren={d['brake']} "
                f"sinyal={d['signal_status']} {wp_info} | sebep: {ev}")
            self._last_log_state = st
            self._last_log_event = ev
            self._last_hb_time   = now

    # ----------------------------------------------------------------
    # Çıktı: Bee 1 + CARLA
    # ----------------------------------------------------------------
    def publish_commands(self, d):
        steer_centered = float(d['steering_angle']) - 45.0
        speed_kmh      = float(d['target_speed_kmh'])
        brake          = int(d['brake'])
        signal         = int(d['signal_status'])

        # Bee 1
        thr = Float32(); thr.data = 0.0 if brake else speed_kmh
        self.pub_throttle.publish(thr)

        brk = Int32(); brk.data = brake
        self.pub_brake.publish(brk)

        stm = Float32(); stm.data = float(d['steering_angle'])
        self.pub_steering.publish(stm)

        sig = Int32(); sig.data = signal
        self.pub_signal.publish(sig)

        # CARLA: Alkar >45=sol → steer_centered>0 → carla_steer<0 (sol negatif)
        carla_steer = max(-1.0, min(1.0, -steer_centered / 45.0))

        ctrl = CarlaEgoVehicleControl()
        ctrl.header.stamp      = self.get_clock().now().to_msg()
        ctrl.steer             = float(carla_steer)
        ctrl.hand_brake        = False
        ctrl.reverse           = False
        ctrl.gear              = 1
        ctrl.manual_gear_shift = False

        if brake or speed_kmh <= 0.0:
            ctrl.throttle       = 0.0
            ctrl.brake          = 1.0
            self.speed_integral = 0.0
        else:
            target_ms = speed_kmh / 3.6
            err = target_ms - self.current_speed

            self.speed_integral += err * 0.05
            self.speed_integral  = max(-5.0, min(5.0, self.speed_integral))

            Kff, Kp, Ki = 0.06, 0.18, 0.04
            throttle = Kff * target_ms + Kp * err + Ki * self.speed_integral

            ctrl.throttle = float(max(0.0, min(0.6, throttle)))
            ctrl.brake    = 0.0

        self.pub_carla_ctrl.publish(ctrl)

    def publish_debug(self, d):
        st = String(); st.data = str(d['state'])
        self.pub_state.publish(st)

        dump = Float32MultiArray()
        dump.data = [
            float(d['steering_angle']),
            float(d['target_speed_kmh']),
            float(d['brake']),
            float(d['signal_status']),
            float(d['speed_limit']),
        ]
        self.pub_decision.publish(dump)


# ================================================================
# Giriş Noktası
# ================================================================
def main(args=None):
    rclpy.init(args=args)
    node = DecisionControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
