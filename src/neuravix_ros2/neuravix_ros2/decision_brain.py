#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NeuraVix karar beyni (FSM) - CARLA'dan / gerçek araçtan bağımsız çekirdek.

neuravix_control_node.py (CARLA sim) ve neuravix_control_node_real.py (gerçek
Bee1 aracı) bu modülü ortak kullanır. Bu dosyada CARLA'ya veya araca özel hiçbir
şey olmamalı — sadece /master mesajlarından karar üreten saf mantık. Sim/gerçek
farkı sadece o iki dosyadaki ROS I/O (mesaj tipi, topic adı) katmanındadır.
"""

import time
import math
from enum import Enum

from .astar_planner import AStarPlanner


# ================================================================
# ROTA — pist_layout.json koordinatları (pist/OpenDRIVE)
# carla-ros-bridge: ros_x = pist_x, ros_y = pist_y
# NOT: Bu ROUTE CARLA pistine özeldir. Gerçek arac/pist için anlamsızdır;
# odometri gelmezse (gerçek araçta ilk fazda olduğu gibi) pure-pursuit
# devre dışı kalır ve FSM tek başına (şerit+tabela+engel) sürer.
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
        # ESIKLER AYRILDI (2026-07-21, algi2/3/4 bag analizi): eskiden
        # slow_distance hem "yavaşla" hem "slaloma gir" eşiğiydi; 9 slalom
        # girişinin 7'si front 4.45-4.99 m'de, yani eşiğin tam dibinde
        # tetiklenmişti. Artık 5 m sadece yavaşlatır (şeritte kalınır),
        # slaloma girmek için engelin avoid_distance'a kadar yaklaşması VE
        # tetiğin avoid_confirm_time boyunca sürmesi gerekir.
        self.slow_distance        = 5.0   # yavaşla, şeridi bırakma
        self.avoid_distance       = 3.0   # bundan yakınsa kaçınmaya gir
        self.avoid_confirm_time   = 0.5   # s, tetik bu kadar sürmeli
        self.safe_side_distance   = 2.0
        self.obstacle_replan_wait = 3.0
        self.avoid_direction      = None
        self._avoid_trigger_since = None

        # --- Slalom (alternasyonlu sürekli weave) ---
        # MESAFE TABANLI (2026-07-21): fazlar eskiden saat tabanlıydı ve
        # slalom_speed=4 km/h (1.11 m/s) varsayıyordu. Araçta ölçülen gerçek:
        # 18.0 s slalomda 3.12 m (biri 6.0 s'de 0.00 m) — zamanlayıcının
        # beklediğinin ~6'da biri. Direksiyon savruluyor, araç yerinde sayıyor.
        # Fazlar artık katedilen mesafeye bağlı; süre yalnızca emniyet tavanı.
        self.slalom_speed          = 4.0   # km/h, weave sırasında hedef hız
        self.slalom_out_distance   = 2.0   # m, kaçış fazında yol alınacak mesafe
        self.slalom_weave_distance = 4.5   # m, bir weave'in toplam mesafesi
        self.slalom_max_time       = 12.0  # s, EMNIYET tavanı (odometri ölürse)
        # Hareketsizlik koruması: bu sürede bu kadar bile ilerlemediyse manevra
        # gerçekleşmiyor demektir — direksiyonu savurmayı bırak, dur.
        self.stall_timeout         = 4.0   # s
        self.stall_min_distance    = 0.25  # m
        # Şerit karışımı (kontrol node'u kullanır): kaçışta şerit büyük ölçüde
        # yok sayılır, dönüş fazında şerit bizi merkeze geri çeker.
        self.avoid_lane_blend_escape = 0.15
        self.avoid_lane_blend_return = 0.55
        # Zaman tabanlı YEDEK (hiç hareket kaynağı beslenmezse, ör. sim):
        self.slalom_out_time   = 1.5
        self.slalom_weave_time = 3.0
        self.slalom_count     = 0      # geçilen engel sayısı (debug)
        self.avoid_phase      = None   # 'escape' | 'return'
        # SONSUZ WEAVE KORUMASI (2026-07-20, debug_control5 bag analizi):
        # araç ilerlemiyorken (fren/rampa/engel gerçekten geçilemiyor) engel
        # önde kaldığı için her weave sonunda ters yöne yenisi açılıyor ve
        # direksiyon 18-24 sn boyunca 70<->20 arası savruluyordu. Bu kadar
        # weave'den sonra slalom bırakılır, OBSTACLE_STOP'a düşülür ve yol
        # gerçekten açılana (front > slow_distance) kadar yeniden slaloma
        # girilmez.
        self.slalom_max_weaves = 3
        self.avoid_blocked     = False  # True: slalom denendi, çözemedi -> dur

        self.front_distance = 99.0
        self.left_distance  = 99.0
        self.right_distance = 99.0

        # --- Hareket (mesafe tabanlı slalom için) ---
        # update_motion() ile dışarıdan beslenir. Hiç beslenmezse
        # _motion_ok False kalır ve slalom otomatik olarak eski zaman
        # tabanlı davranışa döner (sim/odometrisiz çalışma bozulmasın).
        self.odom_distance  = 0.0     # monoton katedilen mesafe (m)
        self.speed_mps      = 0.0
        self._motion_ok     = False
        self._last_motion_t = None
        self._avoid_mark    = 0.0     # weave başındaki odom_distance
        self._phase_mark    = 0.0     # faz başındaki odom_distance
        self._avoid_start_t = 0.0

        self.park_forbidden   = False
        self.emergency_active = False
        self.last_event       = "baslangic: LANE_FOLLOW"

        # resolution=1.0: bu katmanda konumlar GRID_SCALE ile hücreye çevrilmiş
        # 0..59 grid koordinatı — planner'ın "dünya" birimi de hücre olmalı,
        # yoksa plan_path metre sanıp 0.5'e bölerek grid dışına taşar (IndexError)
        self.planner = AStarPlanner(grid_width=60, grid_height=60, resolution=1.0)
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
    # Katedilen mesafe — slalom fazlarının ölçüsü (2026-07-21)
    # ------------------------------------------------------------
    def update_motion(self, speed_mps=None, distance=None):
        """Mesafe tabanlı slalomu besler. İki kaynaktan biri yeter:
          distance  : odometriden gelen MUTLAK katedilen yol (m, monoton)
          speed_mps : anlık hız; kendi saatimizle integre edilir
        Hiç çağrılmazsa slalom zaman tabanlı yedeğe düşer."""
        now = self._now()
        if distance is not None:
            self.odom_distance = float(distance)
            self._motion_ok = True
        elif speed_mps is not None:
            self.speed_mps = max(0.0, float(speed_mps))
            if self._last_motion_t is not None:
                dt = now - self._last_motion_t
                if 0.0 < dt < 1.0:        # uzun boşlukları yut (donma/yeniden başlama)
                    self.odom_distance += self.speed_mps * dt
            self._motion_ok = True
        self._last_motion_t = now

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
        # İKİ KADEMELI (2026-07-21): slow_distance yavaşlatır, avoid_distance
        # kaçınmaya sokar. Böylece 5 m'de görülen bir şey için 3 saniyelik
        # açık-döngü manevraya girilmez; önce yavaşlanır, engel gerçekten
        # yaklaşır ve avoid_confirm_time boyunca kalıcı olursa kaçınılır.
        if self.front_distance >= self.slow_distance:
            self._avoid_trigger_since = None
            return

        if self.avoid_blocked:
            # Slalom tavanı dolmuştu ve yol hâlâ kapalı -> tekrar slaloma
            # girme (sonsuz weave koruması), dur ve bekle.
            self._set_state(DriveState.OBSTACLE_STOP)
            self._stop_vehicle()
            self.signal_status = 3
            return

        # Tetik kalıcılığı: yalnızca avoid_distance içindeyken sayaç işler.
        if self.front_distance < self.avoid_distance:
            if self._avoid_trigger_since is None:
                self._avoid_trigger_since = self._now()
            held = self._now() - self._avoid_trigger_since
        else:
            self._avoid_trigger_since = None
            held = 0.0

        if held >= self.avoid_confirm_time:
            direction = self._pick_avoid_direction()
            if direction is not None:
                # Boş taraf var -> DURMADAN doğrudan slaloma gir (akıcı geçiş)
                self.slalom_count = 0
                self._begin_weave(direction)
                self._explain(
                    f"ENGEL front={self.front_distance:.1f} (>{self.avoid_confirm_time}s) "
                    f"-> SLALOM {direction} (durmadan)")
                return
            if self.front_distance < self.stop_distance:
                # İki taraf da kapalı ve çok yakın -> güvenli dur
                self._set_state(DriveState.OBSTACLE_STOP)
                self._stop_vehicle()
                self.signal_status = 3
                self._explain(
                    f"ENGEL front={self.front_distance:.1f}, iki taraf kapali -> DUR")
                return

        # Onay dolmadıysa bile çok yakınsa beklemeden dur (güvenlik önce).
        if self.front_distance < self.stop_distance:
            self._set_state(DriveState.OBSTACLE_STOP)
            self._stop_vehicle()
            self.signal_status = 3
            self._explain(f"ENGEL front={self.front_distance:.1f} cok yakin -> DUR")
            return

        # slow_distance ile avoid_distance arası: YAVAŞLA, şeridi bırakma.
        self._move_vehicle(self.slow_speed)
        self._explain(f"ENGEL front={self.front_distance:.1f} -> yavasla (seritte kal)")

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
            self.signal_status  = 0
            self.avoid_blocked  = False   # yol açıldı -> slalom tekrar serbest
            self._avoid_trigger_since = None
            self._set_state(DriveState.LANE_FOLLOW)
            return
        if self.avoid_blocked:
            # Slalom denendi ve engel geçilemedi -> yol gerçekten açılana kadar
            # bekle (tekrar slaloma girip direksiyonu savurma).
            return
        if self._elapsed() > self.obstacle_replan_wait:
            direction = self._pick_avoid_direction()
            if direction is not None:
                self.slalom_count = 0
                self._begin_weave(direction)

    def _begin_weave(self, direction):
        """Yeni bir weave başlat: yön + mesafe/zaman işaretlerini sıfırla.
        slalom_count'a DOKUNMAZ (çağıran yönetir)."""
        self.avoid_direction  = direction
        self.avoid_phase      = "escape"
        self._avoid_mark      = self.odom_distance
        self._phase_mark      = self.odom_distance
        self._avoid_start_t   = self._now()
        self.signal_status    = 2 if direction == "left" else 1
        self._set_state(DriveState.OBSTACLE_AVOID)

    def _obstacle_avoid_control(self):
        """SLALOM: alternasyonlu weave. Her weave iki fazlı:
        (1) engelden kaç, (2) şeride geri dön.

        MESAFE TABANLI (2026-07-21): fazlar katedilen yola bağlı, saate değil.
        Araçta ölçülen sorun: 6.0 s süren bir weave boyunca araç 0.00 m gitti,
        yani zamanlayıcı fazları bitirirken araç hiç yer değiştirmemişti.
        Süre yalnızca iki emniyet rolünde: hareketsizlik tespiti (stall) ve
        odometri ölürse takılı kalmama (slalom_max_time).
        Hiç hareket kaynağı beslenmediyse (_motion_ok False) eski zaman
        tabanlı davranışa döner."""
        self.brake        = 0
        self.target_speed = self.slalom_speed

        if self.avoid_direction is None:
            self._end_avoidance()
            return

        t       = self._now() - self._avoid_start_t
        d_weave = self.odom_distance - self._avoid_mark
        d_phase = self.odom_distance - self._phase_mark

        # --- Hareketsizlik koruması: manevra gerçekleşmiyorsa savurma ---
        if (self._motion_ok and t > self.stall_timeout
                and d_weave < self.stall_min_distance):
            self._explain(
                f"SLALOM {t:.1f} s'de sadece {d_weave:.2f} m ilerledi "
                f"(arac hareket etmiyor) -> OBSTACLE_STOP")
            self._abort_avoidance()
            return

        # Emniyet tavanı: odometri beslenmiyorsa/donduysa sonsuza kalma
        timeout = t > self.slalom_max_time

        if self.avoid_phase == "escape":
            if self.avoid_direction == "left":
                self.steering_angle = 70; self.signal_status = 2
            else:
                self.steering_angle = 20; self.signal_status = 1
            # Faz 1 biter: yeterince yana çıkıldı VEYA önü açıldı (algı
            # tabanlı erken çıkış — engel artık yolumuzda değilse kaçmaya
            # devam etmenin anlamı yok).
            if self._motion_ok:
                done = (d_phase >= self.slalom_out_distance
                        or self.front_distance > self.slow_distance)
            else:
                done = t >= self.slalom_out_time
            if done or timeout:
                self.avoid_phase = "return"
                self._phase_mark = self.odom_distance

        elif self.avoid_phase == "return":
            if self.avoid_direction == "left":
                self.steering_angle = 25; self.signal_status = 1
            else:
                self.steering_angle = 65; self.signal_status = 2
            if self._motion_ok:
                done = d_weave >= self.slalom_weave_distance
            else:
                done = t >= self.slalom_weave_time
            if done or timeout:
                self._weave_finished()

        else:                      # savunma: bilinmeyen faz
            self.avoid_phase = "escape"
            self._phase_mark = self.odom_distance

    def _weave_finished(self):
        """Bir weave tamamlandı: yola devam mı, yeni weave mi, dur mu?"""
        self.slalom_count += 1
        if self.front_distance > self.slow_distance:
            self._explain(
                f"SLALOM bitti ({self.slalom_count} engel gecildi) -> serit")
            self._end_avoidance()
            return
        if self.slalom_count >= self.slalom_max_weaves:
            # Weave tavanı doldu, engel hâlâ önde -> slalom çözmüyor.
            self._explain(
                f"SLALOM {self.slalom_count} weave sonunda engel gecilemedi "
                f"(front={self.front_distance:.1f}) -> OBSTACLE_STOP")
            self._abort_avoidance()
            return
        # FIX (2026-07-21): eskiden yön körlemesine ters çevriliyordu
        # (`right if left else left`) — lidar'a hiç sorulmuyordu. Artık
        # hangi tarafın gerçekten açık olduğu yeniden değerlendirilir.
        direction = self._pick_avoid_direction()
        if direction is None:
            self._explain(
                f"SLALOM weave #{self.slalom_count} bitti, iki taraf da kapali "
                f"(left={self.left_distance:.1f} right={self.right_distance:.1f}) "
                f"-> OBSTACLE_STOP")
            self._abort_avoidance()
            return
        self._begin_weave(direction)
        self._explain(
            f"SLALOM weave #{self.slalom_count} bitti, engel devam "
            f"(front={self.front_distance:.1f}) -> {direction} yone yeni weave")

    def _abort_avoidance(self):
        """Slalom çözmüyor -> savurmayı bırak, dur. Yol gerçekten açılana
        kadar (_obstacle_stop_control) yeniden slaloma girilmez."""
        self.avoid_blocked   = True
        self.avoid_direction = None
        self.avoid_phase     = None
        self.slalom_count    = 0
        self.steering_angle  = 45
        self.signal_status   = 3
        self._set_state(DriveState.OBSTACLE_STOP)
        self._stop_vehicle()

    def _end_avoidance(self):
        self.steering_angle  = 45
        self.signal_status   = 0
        self.avoid_direction = None
        self.avoid_phase     = None
        self.slalom_count    = 0
        self.avoid_blocked   = False   # yol açıldı -> slalom tekrar serbest
        self._avoid_trigger_since = None
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
    def _lane_blend(self):
        """Kontrol node'una "şerit çıktısını ne kadar karıştır" der (0..1).
        Kaçınma sırasında şerit tamamen atılmamalı: eskiden OBSTACLE_AVOID'da
        direksiyon sabit 70/25/20/65 idi ve şerit yok sayılıyordu (araçta
        slalom süresinin %30-97'sinde geçerli şerit verisi VARDI)."""
        if self.state == DriveState.OBSTACLE_AVOID:
            if self.avoid_phase == "return":
                return self.avoid_lane_blend_return
            return self.avoid_lane_blend_escape
        return 0.0

    def get_decision(self):
        return {
            "state":            self.state.name,
            "steering_angle":   int(self.steering_angle),
            "target_speed_kmh": float(self.target_speed),
            "brake":            int(self.brake),
            "signal_status":    int(self.signal_status),
            "speed_limit":      float(self.speed_limit),
            "avoid_phase":      self.avoid_phase,
            "lane_blend":       float(self._lane_blend()),
        }
