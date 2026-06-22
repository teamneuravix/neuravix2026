#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Team NeuraVix - TEKNOFEST 2026 Robotaksi (Hazır Araç)
Karar Beyni (FSM) + ROS 2 Köprüsü — v2 Kararlı Kontrol

Düzeltmeler:
  - A* current_position: sabit (2,2) yerine odometri ile güncelleniyor
  - Hibrit direksiyon: LANE_FOLLOW'da waypoint + şerit karıştırması
  - Dönüş süreleri kalibre edildi (6 km/h, faz1=5.5s, faz2=8.5s)
  - obstacle_event: engel A* grid'e gerçek konumdan ekleniyor
"""

import time
import math
from enum import Enum

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Int32, Bool, String, Float32MultiArray
from carla_msgs.msg import CarlaEgoVehicleControl, CarlaEgoVehicleStatus
from nav_msgs.msg import Odometry

from .astar_planner import AStarPlanner


# ================================================================
# ROTA — pist_layout.json koordinatları (pist/OpenDRIVE)
# carla-ros-bridge: ros_x = pist_x, ros_y = pist_y
# ================================================================
WP_REACH    = 4.0    # (m) waypoint'e ulaşma eşiği
WP_STR_GAIN = 0.7    # heading hatası (°) → Alkar birim katsayısı

ROUTE = [
    dict(x=72.0, y=70.0),
    dict(x=67.0, y=70.0),
    dict(x=64.0, y=65.5),
    dict(x=60.0, y=65.5),
    dict(x=56.0, y=70.0),
    dict(x=45.0, y=70.0),
    dict(x=34.0, y=70.0),
    dict(x=29.0, y=70.0),
    dict(x=25.0, y=64.0),
    dict(x=24.5, y=55.0),
    dict(x=24.5, y=45.0),
    dict(x=26.0, y=36.5),
    dict(x=26.0, y=26.0),
    dict(x=36.0, y=23.5),
    dict(x=47.0, y=25.0),
    dict(x=47.0, y=33.0),
    dict(x=51.0, y=36.5),
    dict(x=53.0, y=36.5),
    dict(x=49.0, y=40.0),
    dict(x=47.0, y=47.0),
    dict(x=58.0, y=47.0),
    dict(x=68.0, y=47.0),
    dict(x=73.0, y=50.0),
    dict(x=78.0, y=55.0),
    dict(x=78.0, y=59.0),
]

# pist 73x73 m → A* grid 60x60 hücre
GRID_SCALE = 60.0 / 73.0


# ================================================================
# /master mesaj id'leri
# ================================================================
ID_LANE     = 2
ID_SIGN     = 3
ID_OBSTACLE = 4
ID_PLANNER  = 5


# ================================================================
# TABELA / IŞIK SINIF ID'LERİ
# ================================================================
TRESPASS       = 0
GIRILMEZ       = 1
ILERI_SOL      = 2
ILERI_SAG      = 3
SOLA_DON       = 4
HIZ_20         = 5
HIZ_30         = 6
HIZ_20B        = 7
SAGA_DON       = 8
SAGA_DON_YASAK = 9
SOLA_DON_YASAK = 10
DUR            = 11
PARK_YASAK     = 12
PARK           = 13
DURAK          = 14
KIRMIZI_ISIK   = 15
SARI_ISIK      = 16
YESIL_ISIK     = 17
ENGELLI_PARK   = 18
KAVSAK         = 19
YAYA_GECIDI    = 20
IKI_YON        = 21
ILERI          = 22
TUNEL          = 23

SIGN_NAMES = {
    TRESPASS: "trespass", GIRILMEZ: "girilmez", ILERI_SOL: "ileri_sol",
    ILERI_SAG: "ileri_sag", SOLA_DON: "sola_don", HIZ_20: "hiz_20",
    HIZ_30: "hiz_30", HIZ_20B: "hiz_20b", SAGA_DON: "saga_don",
    SAGA_DON_YASAK: "saga_don_yasak", SOLA_DON_YASAK: "sola_don_yasak",
    DUR: "dur", PARK_YASAK: "park_yasak", PARK: "park", DURAK: "durak",
    KIRMIZI_ISIK: "kirmizi_isik", SARI_ISIK: "sari_isik",
    YESIL_ISIK: "yesil_isik", ENGELLI_PARK: "engelli_park", KAVSAK: "kavsak",
    YAYA_GECIDI: "yaya_gecidi", IKI_YON: "iki_yon", ILERI: "ileri",
    TUNEL: "tunel",
}


# ================================================================
# DURUM MAKİNESİ
# ================================================================
class DriveState(Enum):
    LANE_FOLLOW       = 0
    RED_LIGHT_STOP    = 1
    STOP_SIGN         = 2
    CROSSWALK_STOP    = 3
    BUS_STOP          = 4
    TURN_LEFT         = 5
    TURN_RIGHT        = 6
    GO_STRAIGHT_LEFT  = 7
    GO_STRAIGHT_RIGHT = 8
    OBSTACLE_STOP     = 9
    OBSTACLE_AVOID    = 10
    PARK_SEARCH       = 11
    PARKING           = 12
    EMERGENCY         = 13


# ================================================================
# KARAR BEYNİ (FSM)
# ================================================================
class Alkar_Function4:

    def __init__(self):
        self.steering_angle = 45
        self.target_speed   = 12.0
        self.brake          = 0
        self.signal_status  = 0
        self.state          = DriveState.LANE_FOLLOW

        self.default_speed = 12.0
        self.slow_speed    = 6.0
        self.turn_speed    = 6.0    # FIX: 5.0 → 6.0 km/h (dönüş yayı ~11m @ R≈7m)
        self.park_speed    = 3.0
        self.speed_limit   = 20.0

        self.image_center = (1280 / 2, 720 / 2)

        self.sign_counts        = {i: 0 for i in range(24)}
        self.last_sign_time     = {}
        self.sign_confirm_count = 3
        self.sign_window_sec    = 2.0
        self.sign_cooldown      = {}
        self.default_cooldown   = 4.0

        self.state_start_time      = time.time()
        self.red_light_seen_time   = 0.0
        self.green_light_seen_time = 0.0

        self.stop_wait_sec      = 3.0
        self.crosswalk_wait_sec = 5.0

        self.bus_stop_align_time = 2.0
        self.bus_stop_wait_sec   = 17.0
        self.bus_stop_exit_time  = 2.0

        self.left_turn_angle          = 73
        self.right_turn_angle         = 17
        self.turn_recover_angle_left  = 50   # FIX: 55 → 50 (daha agresif düzeltme)
        self.turn_recover_angle_right = 40   # FIX: 35 → 40

        self.stop_distance        = 2.2
        self.slow_distance        = 5.0
        self.safe_side_distance   = 2.0
        self.obstacle_replan_wait = 3.0
        self.avoid_direction      = None

        # --- Slalom (alternasyonlu sürekli weave) ---
        self.slalom_speed     = 4.0    # km/h, weave sırasında sabit hız
        self.slalom_out_time  = 1.5    # s, engelden kaçma fazı süresi
        self.slalom_weave_time = 3.0   # s, bir weave'in toplam süresi (kaç + geri dön)
        self.slalom_count     = 0      # geçilen engel sayısı (debug)

        self.front_distance = 99.0
        self.left_distance  = 99.0
        self.right_distance = 99.0

        self.park_forbidden   = False
        self.emergency_active = False
        self.last_event       = "baslangic: LANE_FOLLOW"

        self.planner = AStarPlanner(grid_width=60, grid_height=60)
        # FIX: current_position artık update_position() ile odometriden güncelleniyor
        self.current_position = (2, 2)
        self.goal_position    = (50, 50)
        self.path = self.planner.plan_path(self.current_position, self.goal_position)

    # ------------------------------------------------------------
    # FIX: Dışarıdan çağrılarak gerçek araç konumunu grid'e yazar
    # ------------------------------------------------------------
    def update_position(self, grid_x, grid_y):
        self.current_position = (
            max(0, min(59, grid_x)),
            max(0, min(59, grid_y)),
        )

    # ------------------------------------------------------------
    # Yardımcılar
    # ------------------------------------------------------------
    def _now(self): return time.time()

    def _set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.state_start_time = self._now()

    def _explain(self, msg):
        self.last_event = msg

    def _elapsed(self): return self._now() - self.state_start_time

    def _cooldown_ok(self, sign_id):
        return self._now() >= self.sign_cooldown.get(sign_id, 0.0)

    def _start_cooldown(self, sign_id, sec=None):
        self.sign_cooldown[sign_id] = self._now() + (
            sec if sec is not None else self.default_cooldown)

    def _stop_vehicle(self):
        self.target_speed   = 0.0
        self.brake          = 1
        self.steering_angle = 45

    def _move_vehicle(self, speed=None):
        self.brake = 0
        req = speed if speed is not None else self.default_speed
        self.target_speed = min(req, self.speed_limit)

    def _smooth_angle(self, old_angle, new_angle, alpha=0.35):
        return int((1 - alpha) * old_angle + alpha * new_angle)

    def _is_blocking_state(self):
        blocking = {
            DriveState.RED_LIGHT_STOP, DriveState.STOP_SIGN,
            DriveState.CROSSWALK_STOP, DriveState.BUS_STOP,
            DriveState.TURN_LEFT, DriveState.TURN_RIGHT,
            DriveState.GO_STRAIGHT_LEFT, DriveState.GO_STRAIGHT_RIGHT,
            DriveState.OBSTACLE_STOP, DriveState.OBSTACLE_AVOID,
            DriveState.PARKING, DriveState.EMERGENCY,
        }
        return self.state in blocking

    # ------------------------------------------------------------
    # Olaylar
    # ------------------------------------------------------------
    def lane_detect_event(self, data):
        try:
            lane_angle = float(data[1])
        except (IndexError, ValueError, TypeError):
            return

        if self.emergency_active:
            self._set_state(DriveState.EMERGENCY)
            self._stop_vehicle()
            return

        self._update_state_machine()

        if self._is_blocking_state():
            return

        # Şerit açısını FSM'e yaz; control_loop'ta waypoint ile karıştırılır
        fused = max(15, min(75, lane_angle))
        self.steering_angle = self._smooth_angle(self.steering_angle, fused)
        self._move_vehicle(self.default_speed)

    def sign_detect_event(self, data):
        try:
            sign     = int(data[1])
            distance = float(data[2])
            w        = int(data[5])
            h        = int(data[6])
        except (IndexError, ValueError, TypeError):
            return

        if sign == 24:
            sign = ILERI_SAG
        elif sign == 25:
            sign = ILERI_SOL

        if self.emergency_active:
            self._set_state(DriveState.EMERGENCY)
            self._stop_vehicle()
            return

        if not self._update_sign_counter(sign): return
        if not self._cooldown_ok(sign):         return

        name = SIGN_NAMES.get(sign, str(sign))
        self._explain(f"TABELA {name} (id={sign}, d={distance:.1f}m, h={h}) -> islendi")

        if sign in (HIZ_20, HIZ_20B):
            self.speed_limit   = 20.0
            self.default_speed = min(self.default_speed, 12.0)
            self._start_cooldown(sign, 5.0)

        elif sign == HIZ_30:
            self.speed_limit   = 30.0
            self.default_speed = min(self.default_speed, 15.0)
            self._start_cooldown(sign, 5.0)

        elif sign == KIRMIZI_ISIK:
            if distance < 12.0:
                self.red_light_seen_time = self._now()
                self._set_state(DriveState.RED_LIGHT_STOP)
                self._start_cooldown(sign, 1.0)
                self._explain(f"KIRMIZI ISIK (d={distance:.1f}) -> DUR")
            else:
                self._explain(f"KIRMIZI ISIK ama uzak (d={distance:.1f}) -> bekle")

        elif sign == SARI_ISIK:
            if distance < 10.0:
                self.target_speed = self.slow_speed
                self._explain(f"SARI ISIK (d={distance:.1f}) -> yavasla")

        elif sign == YESIL_ISIK:
            self.green_light_seen_time = self._now()
            if self.state == DriveState.RED_LIGHT_STOP:
                self._set_state(DriveState.LANE_FOLLOW)
                self._move_vehicle(self.default_speed)
                self._explain("YESIL ISIK -> DEVAM (kirmizidan cikildi)")
            else:
                self._explain("YESIL ISIK -> devam")
            self._start_cooldown(sign, 1.0)

        elif sign == DUR:
            if distance < 9.0:
                self._set_state(DriveState.STOP_SIGN)
                self._start_cooldown(sign, 8.0)
                self._explain(f"DUR tabelasi (d={distance:.1f}) -> 3sn DUR")

        elif sign == YAYA_GECIDI:
            if distance < 12.0:
                self._set_state(DriveState.CROSSWALK_STOP)
                self._start_cooldown(sign, 10.0)

        elif sign == DURAK:
            if distance < 10.0:
                if self.state != DriveState.BUS_STOP:
                    self._set_state(DriveState.BUS_STOP)
                    self._start_cooldown(sign, 30.0)
                    self._explain(f"DURAK (d={distance:.1f}) -> duraga yanas + bekle")

        elif sign == SOLA_DON:
            if distance < 12.0:
                self._begin_left_turn()
                self._explain(f"SOLA DON tabelasi (d={distance:.1f}) -> SOLA DONUS")

        elif sign == SOLA_DON_YASAK:
            self._start_cooldown(sign, 6.0)

        elif sign == SAGA_DON:
            if distance < 12.0:
                self._begin_right_turn()
                self._explain(f"SAGA DON tabelasi (d={distance:.1f}) -> SAGA DONUS")

        elif sign == SAGA_DON_YASAK:
            self._start_cooldown(sign, 6.0)

        elif sign == GIRILMEZ:
            self._start_cooldown(sign, 6.0)

        elif sign == ILERI_SOL:
            if distance < 12.0:
                self._begin_straight_then_left()

        elif sign == ILERI_SAG:
            if distance < 12.0:
                self._begin_straight_then_right()

        elif sign == ILERI:
            if self.state in (DriveState.TURN_LEFT, DriveState.TURN_RIGHT,
                              DriveState.GO_STRAIGHT_LEFT,
                              DriveState.GO_STRAIGHT_RIGHT):
                self._set_state(DriveState.LANE_FOLLOW)
            self._start_cooldown(sign, 4.0)

        elif sign == PARK_YASAK:
            self.park_forbidden = True
            self._start_cooldown(sign, 8.0)

        elif sign == PARK:
            if not self.park_forbidden and distance < 10.0:
                if self.state not in (DriveState.PARKING, DriveState.PARK_SEARCH):
                    self._set_state(DriveState.PARK_SEARCH)
                    self._start_cooldown(sign, 10.0)
                    self._explain(f"PARK (d={distance:.1f}) -> park arama")

        elif sign == TUNEL:
            self.steering_angle = 45
            self.target_speed   = min(self.target_speed, self.slow_speed)
            self._start_cooldown(sign, 6.0)
            self._explain(f"TUNEL (d={distance:.1f}) -> duz + yavasla")

        elif sign == IKI_YON:
            if self.target_speed > self.slow_speed:
                self.target_speed = self.slow_speed
            self._start_cooldown(sign, 5.0)

    def obstacle_event(self, front=None, left=None, right=None):
        if front is not None: self.front_distance = float(front)
        if left  is not None: self.left_distance  = float(left)
        if right is not None: self.right_distance = float(right)

        if self.emergency_active:
            self._set_state(DriveState.EMERGENCY)
            self._stop_vehicle()
            return

        if self.state in (DriveState.OBSTACLE_AVOID,
                          DriveState.PARKING,
                          DriveState.PARK_SEARCH):
            return

        # FIX: self.current_position artık gerçek konumla güncelleniyor;
        # makul yan mesafe yoksa planner'a engel ekleme (false-positive önleme)
        if (self.planner is not None
                and self.front_distance < self.slow_distance
                and (self.left_distance > 1.0 or self.right_distance > 1.0)):
            cx, cy = self.current_position
            self.planner.add_obstacle(min(59, int(cx + 2)), cy, safety_margin=2)
            self.path = self.planner.replan_if_needed(
                self.current_position, self.goal_position)

        # FSM'in açık şekilde durmaya/beklemeye karar verdiği durumları ezme
        if self.state in (DriveState.RED_LIGHT_STOP, DriveState.STOP_SIGN,
                          DriveState.CROSSWALK_STOP, DriveState.BUS_STOP,
                          DriveState.EMERGENCY):
            return

        # --- Engel algılama eşiği (genel, reaktif) ---
        if self.front_distance < self.slow_distance:
            direction = self._pick_avoid_direction()

            if direction is not None:
                # Boş taraf var -> DURMADAN doğrudan slaloma gir (akıcı geçiş)
                self.avoid_direction = direction
                self.slalom_count    = 0
                self._set_state(DriveState.OBSTACLE_AVOID)
                self.signal_status   = 2 if direction == "left" else 1
                self._explain(
                    f"ENGEL front={self.front_distance:.1f} -> "
                    f"SLALOM {direction} (durmadan)")
            elif self.front_distance < self.stop_distance:
                # İki taraf da kapalı ve çok yakın -> güvenli dur
                self._set_state(DriveState.OBSTACLE_STOP)
                self._stop_vehicle()
                self.signal_status = 3
                self._explain(
                    f"ENGEL front={self.front_distance:.1f}, iki taraf kapali -> DUR")
            else:
                # Yer yok ama henüz uzak -> yavaşlayarak yaklaş
                self._move_vehicle(self.slow_speed)
                self._explain(f"ENGEL front={self.front_distance:.1f} -> yavasla")

    def planner_event(self, data):
        try:
            self.goal_position = (int(float(data[1])), int(float(data[2])))
        except (IndexError, ValueError, TypeError):
            return
        self.path = self.planner.plan_path(self.current_position, self.goal_position)

    def emergency_event(self, active=True):
        self.emergency_active = bool(active)
        if self.emergency_active:
            self._set_state(DriveState.EMERGENCY)
            self._stop_vehicle()
            self.signal_status = 3
        else:
            self.signal_status = 0
            self._set_state(DriveState.LANE_FOLLOW)

    # ------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------
    def _update_state_machine(self):
        if self.state == DriveState.EMERGENCY:
            self._stop_vehicle(); self.signal_status = 3; return
        if self.state == DriveState.OBSTACLE_STOP:
            self._obstacle_stop_control(); return
        if self.state == DriveState.RED_LIGHT_STOP:
            self._stop_vehicle(); return
        if self.state == DriveState.STOP_SIGN:
            self._stop_vehicle()
            if self._elapsed() >= self.stop_wait_sec:
                self._set_state(DriveState.LANE_FOLLOW)
                self._move_vehicle(self.default_speed)
            return
        if self.state == DriveState.CROSSWALK_STOP:
            self._stop_vehicle()
            if (self._elapsed() >= self.crosswalk_wait_sec
                    and self.front_distance > self.slow_distance):
                self._set_state(DriveState.LANE_FOLLOW)
                self._move_vehicle(self.default_speed)
            return
        if self.state == DriveState.BUS_STOP:
            self._bus_stop_control(); return
        if self.state == DriveState.TURN_LEFT:
            self._left_turn_control(); return
        if self.state == DriveState.TURN_RIGHT:
            self._right_turn_control(); return
        if self.state == DriveState.GO_STRAIGHT_LEFT:
            self._straight_then_left_control(); return
        if self.state == DriveState.GO_STRAIGHT_RIGHT:
            self._straight_then_right_control(); return
        if self.state == DriveState.OBSTACLE_AVOID:
            self._obstacle_avoid_control(); return
        if self.state == DriveState.PARK_SEARCH:
            self._park_search_control(); return
        if self.state == DriveState.PARKING:
            self._parking_control(); return

    # ------------------------------------------------------------
    # Tabela doğrulama
    # ------------------------------------------------------------
    def _update_sign_counter(self, sign):
        now = self._now()
        if sign not in self.last_sign_time:
            self.last_sign_time[sign] = now
            self.sign_counts[sign] = 1
            return False
        if now - self.last_sign_time[sign] <= self.sign_window_sec:
            self.sign_counts[sign] += 1
        else:
            self.sign_counts[sign] = 1
        self.last_sign_time[sign] = now
        return self.sign_counts[sign] >= self.sign_confirm_count

    # ------------------------------------------------------------
    # Dönüş başlatıcılar
    # ------------------------------------------------------------
    def _begin_left_turn(self):
        self.signal_status = 2
        self._set_state(DriveState.TURN_LEFT)
        self._start_cooldown(SOLA_DON, 10.0)

    def _begin_right_turn(self):
        self.signal_status = 1
        self._set_state(DriveState.TURN_RIGHT)
        self._start_cooldown(SAGA_DON, 10.0)

    def _begin_straight_then_left(self):
        self.signal_status = 2
        self._set_state(DriveState.GO_STRAIGHT_LEFT)
        self._start_cooldown(ILERI_SOL, 12.0)

    def _begin_straight_then_right(self):
        self.signal_status = 1
        self._set_state(DriveState.GO_STRAIGHT_RIGHT)
        self._start_cooldown(ILERI_SAG, 12.0)

    # ------------------------------------------------------------
    # Manevra kontrolleri
    # FIX: Dönüş süreleri kalibre edildi.
    # 6 km/h = 1.67 m/s, steer=73 → R≈7m, 90° yay=11m → ~6.6s
    # faz1=5.5s (tam direksiyon), faz2=8.5s (3s düzeltme)
    # NOT: Bu süreler hesap tahminidir; CARLA testinde araç modeline
    #      ve kavşak genişliğine göre ince ayar gerekebilir.
    # ------------------------------------------------------------
    def _left_turn_control(self):
        t = self._elapsed()
        self.brake = 0
        self.target_speed = self.turn_speed
        if t < 5.5:      # FIX: 4.0 → 5.5s
            self.steering_angle = self.left_turn_angle
        elif t < 8.5:    # FIX: 6.0 → 8.5s
            self.steering_angle = self.turn_recover_angle_left
        else:
            self.signal_status  = 0
            self.steering_angle = 45
            self._set_state(DriveState.LANE_FOLLOW)

    def _right_turn_control(self):
        t = self._elapsed()
        self.brake = 0
        self.target_speed = self.turn_speed
        if t < 5.5:      # FIX: 4.0 → 5.5s
            self.steering_angle = self.right_turn_angle
        elif t < 8.5:    # FIX: 6.0 → 8.5s
            self.steering_angle = self.turn_recover_angle_right
        else:
            self.signal_status  = 0
            self.steering_angle = 45
            self._set_state(DriveState.LANE_FOLLOW)

    def _straight_then_left_control(self):
        t = self._elapsed()
        self.brake = 0
        self.target_speed = self.turn_speed
        if t < 3.0:
            self.steering_angle = 45
        elif t < 8.5:    # FIX: 7.0 → 8.5s
            self.steering_angle = self.left_turn_angle
        elif t < 11.0:   # FIX: 9.0 → 11.0s
            self.steering_angle = self.turn_recover_angle_left
        else:
            self.signal_status  = 0
            self.steering_angle = 45
            self._set_state(DriveState.LANE_FOLLOW)

    def _straight_then_right_control(self):
        t = self._elapsed()
        self.brake = 0
        self.target_speed = self.turn_speed
        if t < 3.0:
            self.steering_angle = 45
        elif t < 8.5:    # FIX: 7.0 → 8.5s
            self.steering_angle = self.right_turn_angle
        elif t < 11.0:   # FIX: 9.0 → 11.0s
            self.steering_angle = self.turn_recover_angle_right
        else:
            self.signal_status  = 0
            self.steering_angle = 45
            self._set_state(DriveState.LANE_FOLLOW)

    # ------------------------------------------------------------
    # Engel kontrolleri
    # ------------------------------------------------------------
    def _pick_avoid_direction(self):
        """Boş tarafı seç (genel, piste bağımsız). Geri dönüş:
        'left' / 'right' / None (iki taraf da kapalı)."""
        left_ok  = self.left_distance  > self.safe_side_distance
        right_ok = self.right_distance > self.safe_side_distance
        if not left_ok and not right_ok:
            return None
        if left_ok and not right_ok:
            return "left"
        if right_ok and not left_ok:
            return "right"
        # İkisi de uygun -> daha geniş olanı seç (eşitlikte sol)
        return "left" if self.left_distance >= self.right_distance else "right"

    def _obstacle_stop_control(self):
        self._stop_vehicle()
        self.signal_status = 3
        if self.front_distance > self.slow_distance:
            self.signal_status = 0
            self._set_state(DriveState.LANE_FOLLOW)
            return
        if self._elapsed() > self.obstacle_replan_wait:
            if (self.left_distance > self.right_distance
                    and self.left_distance > self.safe_side_distance):
                self.avoid_direction = "left"
                self.signal_status   = 2
                self._set_state(DriveState.OBSTACLE_AVOID)
            elif self.right_distance > self.safe_side_distance:
                self.avoid_direction = "right"
                self.signal_status   = 1
                self._set_state(DriveState.OBSTACLE_AVOID)

    def _obstacle_avoid_control(self):
        """SLALOM: tek sapma yerine alternasyonlu sürekli weave.
        Her weave iki fazlı: (1) engelden kaç, (2) şeride geri dön.
        Weave bitince önde hâlâ engel varsa TERS yöne yeni weave başlatır;
        yol açıldıysa LANE_FOLLOW'a döner."""
        t = self._elapsed()
        self.brake        = 0
        self.target_speed = self.slalom_speed

        if self.avoid_direction is None:
            self._set_state(DriveState.LANE_FOLLOW)
            return

        if t < self.slalom_out_time:
            # Faz 1: engelden kaç (sola=70/sağa=20)
            if self.avoid_direction == "left":
                self.steering_angle = 70; self.signal_status = 2
            else:
                self.steering_angle = 20; self.signal_status = 1
        elif t < self.slalom_weave_time:
            # Faz 2: şeride geri dön (ters yöne kır)
            if self.avoid_direction == "left":
                self.steering_angle = 25; self.signal_status = 1
            else:
                self.steering_angle = 65; self.signal_status = 2
        else:
            # Bir weave tamamlandı
            self.slalom_count += 1
            if self.front_distance < self.slow_distance:
                # Önde başka engel var -> TERS yöne yeni weave
                self.avoid_direction = (
                    "right" if self.avoid_direction == "left" else "left")
                self.state_start_time = self._now()   # weave zamanlayıcıyı sıfırla
                self._explain(
                    f"SLALOM weave #{self.slalom_count} bitti, "
                    f"engel devam (front={self.front_distance:.1f}) "
                    f"-> {self.avoid_direction} yöne devam")
            else:
                self._explain(
                    f"SLALOM bitti ({self.slalom_count} engel gecildi) -> serit")
                self._end_avoidance()

    def _end_avoidance(self):
        self.steering_angle  = 45
        self.signal_status   = 0
        self.avoid_direction = None
        self.slalom_count    = 0
        self._set_state(DriveState.LANE_FOLLOW)

    # ------------------------------------------------------------
    # Durak
    # ------------------------------------------------------------
    def _bus_stop_control(self):
        t = self._elapsed()
        if t < self.bus_stop_align_time:
            self.brake          = 0
            self.target_speed   = self.park_speed
            self.steering_angle = 25
            self.signal_status  = 1
            return
        wait_end = self.bus_stop_align_time + self.bus_stop_wait_sec
        if t < wait_end:
            self._stop_vehicle()
            self.signal_status = 3
            return
        exit_end = wait_end + self.bus_stop_exit_time
        if t < exit_end:
            self.brake          = 0
            self.target_speed   = self.park_speed
            self.steering_angle = 65
            self.signal_status  = 2
            return
        self.signal_status  = 0
        self.steering_angle = 45
        self._move_vehicle(self.default_speed)
        self._set_state(DriveState.LANE_FOLLOW)

    # ------------------------------------------------------------
    # Park
    # ------------------------------------------------------------
    def _park_search_control(self):
        self.brake         = 0
        self.target_speed  = self.park_speed
        self.signal_status = 1
        if self.front_distance < 3.0 and self.right_distance > 3.5:
            self._set_state(DriveState.PARKING)

    def _parking_control(self):
        if self.left_distance > 4.0:
            self.steering_angle = 65
        elif self.right_distance > 4.0:
            self.steering_angle = 25
        else:
            self.steering_angle = 45
        self.brake        = 0
        self.target_speed = self.park_speed
        if self.front_distance < 1.5:
            self._stop_vehicle()
            self.signal_status = 3

    # ------------------------------------------------------------
    # Çıktı
    # ------------------------------------------------------------
    def get_decision(self):
        return {
            "state":            self.state.name,
            "steering_angle":   int(self.steering_angle),
            "target_speed_kmh": float(self.target_speed),
            "brake":            int(self.brake),
            "signal_status":    int(self.signal_status),
            "speed_limit":      float(self.speed_limit),
        }


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
        self.brain._update_state_machine()
        decision = self.brain.get_decision()

        if decision['state'] == 'LANE_FOLLOW':
            wp_steer   = self._pure_pursuit_steer()
            lane_fresh = (time.time() - self._lane_steer_time) < self._LANE_FRESH_SEC

            if wp_steer is not None and lane_fresh:
                # Her iki kaynak taze: %55 waypoint + %45 şerit algısı
                blended = int(0.55 * wp_steer + 0.45 * self._lane_steer)
                decision['steering_angle'] = max(15, min(75, blended))
            elif wp_steer is not None:
                # Şerit yok/bayat: sadece waypoint
                decision['steering_angle'] = wp_steer
            # wp_steer is None: odometri yok, FSM çıktısı kullanılır

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
