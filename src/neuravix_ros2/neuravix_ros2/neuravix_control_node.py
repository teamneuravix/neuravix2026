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
from rclpy.executors import ExternalShutdownException
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

        # use_planner (VARSAYILAN False, gerçek node ile aynı): pure-pursuit +
        # konum-tabanlı A* KAPALI. Böylece araç sabit kodlu ROUTE'u (CARLA
        # pistine özel koordinatlar) körlemesine izlemez; REAKTİF sürer
        # (şerit + tabela + engel/slalom). Slalomun/şeridin GERÇEK davranışını
        # görmek için bunu kapalı tut. CARLA pistinde waypoint takibini test
        # etmek istersen: -p use_planner:=true
        # NOT: ROUTE o pistin koordinatlarına özeldir; açıkken "güzel şerit
        # tutma" perception değil, ezberlenmiş yol takibidir.
        self.declare_parameter('use_planner', False)
        self.use_planner = self.get_parameter(
            'use_planner').get_parameter_value().bool_value

        # HIZ PARAMETRELERI (2026-08-13, CARLA slalom testi):
        # decision_brain'in varsayilani 12 km/h idi ve simde cok yuksekti.
        # Lidar 10 Hz + k-of-n zaman filtresi (~0.2 s) => engel mesafesi
        # kareler arasinda 12 km/h'de (3.33 m/s) ~0.33 m, filtre gecikmesiyle
        # ~0.7 m sicrar; avoid_confirm_time (0.3 s) dolmadan stop_distance
        # (2.2 m) asilir ve arac slaloma HIC giremeden OBSTACLE_STOP'a duser
        # (13.08 log'u: front 5.6 -> 2.4 -> 2.1 -> DUR).
        # Beyin sinifinin kendi varsayilani DEGISTIRILMEDI: gercek arac
        # (neuravix_control_node_real) ayni beyni kullaniyor.
        # 2026-08-14: 8 km/h de yuksek kaldi. CARLA -quality-level=Low
        # cokuyor, yani FPS'i grafikten kazanamiyoruz; onun yerine araci
        # yavaslatiyoruz. Serit dugumu ~2-3 FPS: 3 km/h'de (0.83 m/s) iki
        # kare arasi ~0.4 m yol var, 8 km/h'de ~1.1 m idi.
        self.declare_parameter('default_speed_kmh', 3.0)
        self.declare_parameter('slow_speed_kmh', 2.0)
        self.declare_parameter('slalom_speed_kmh', 2.0)
        self.brain.default_speed = float(
            self.get_parameter('default_speed_kmh').value)
        self.brain.slow_speed = float(
            self.get_parameter('slow_speed_kmh').value)
        self.brain.slalom_speed = float(
            self.get_parameter('slalom_speed_kmh').value)
        # SURUNME HIZI (19.08.2026). Engel avoid_distance icinde ama acilacak
        # taraf yoksa kullanilir; bkz. decision_brain.blocked_speed.
        # ZORUNLU KAPI: slow_speed'i ASAMAZ. Aksi halde "cikis yok" durumu
        # normal yavaslamadan HIZLI olurdu — CARLA'da tam bu olurdu
        # (8p slow_speed_kmh:=2.0 geciyor, blocked varsayilani 2.5).
        self.declare_parameter('blocked_speed_kmh', 1.2)
        self.brain.blocked_speed = min(
            float(self.get_parameter('blocked_speed_kmh').value),
            self.brain.slow_speed)
        # turn_speed (6) ve park_speed (3) beyinde sabit; 3 km/h normal hizda
        # bunlar normalden HIZLI olurdu (donuste hizlanmak = ters davranis).
        self.brain.turn_speed = min(self.brain.turn_speed,
                                    self.brain.default_speed)
        self.brain.park_speed = min(self.brain.park_speed,
                                    self.brain.default_speed)
        self.brain.target_speed = self.brain.default_speed

        # YOL SERIT SAYISI (2026-08-14). Lidar serit bilmez; bos omuz 99
        # okur ve karsi seridi hep yener -> arac yolun disina kaciyordu.
        # 0..1 = "en sag serittesin, solunda bir serit var" (2 seritli gorev
        # yolu) ve SAGA kacis yasak. 3 seritli yolda lane_max:=2.
        self.declare_parameter('lane_min', 0)
        self.declare_parameter('lane_max', 1)
        self.brain.lane_min = int(self.get_parameter('lane_min').value)
        self.brain.lane_max = int(self.get_parameter('lane_max').value)

        # Tam serit degisiminde hedeflenen yanal ofset = SERIT GENISLIGI.
        # Beyin varsayilani 3.0 (pist olcusu); CARLA Town04 seridi 3.5 m ve
        # 3.0 ile arac komsu seridin merkezine varmadan, orta kesikli cizginin
        # uzerinde kaliyordu (14.08 gozlemi).
        self.declare_parameter('slalom_lateral_target', 3.0)
        self.brain.slalom_lateral_target = float(
            self.get_parameter('slalom_lateral_target').value)

        # "KENDI SERIDIME DON" refleksinin esigi. Arac komsu seritte paralel
        # giderken kendi seridi bu kadar acilinca hemen doner.
        #   12.0 (varsayilan) : yol davranisi. Sol serit KARSI YON; kendi
        #                       seridin bosalir bosalmaz donmek dogrudur.
        #   999               : slalom davranisi. Kendi seridi bosalsa bile
        #                       donme; ancak BULUNDUGUN serit kapaninca
        #                       (front) serit degistir -> zik-zak.
        # 14.08 kosusu: kendi seridi 11 m'de acildi ve arac front=9.9 iken
        # dondu. Yol icin dogru, koni slalomu icin erken.
        # Ard arda kac VERIMSIZ weave'den sonra "slalom cozmuyor" denip
        # durulacagi ve bir weave'in "verimli" sayilmasi icin gereken yol
        # (bkz. decision_brain._weave_finished). Yarisma pistinde engeller
        # 5-8 m arayla; her weave sonrasi bir sonraki engel zaten 6 m'nin
        # icinde oldugu icin sayac eskiden birikiyor ve 3. engelde arac
        # basarili bir slalomun ortasinda duruyordu.
        # CARLA direksiyonunu gercek aracin donus yaricapina indirger
        # (bkz. publish_commands). 1.0 = eski davranis.
        self.declare_parameter('carla_steer_scale', 1.0)
        self.carla_steer_scale = float(
            self.get_parameter('carla_steer_scale').value)

        # VIRAJ BASTIRMA ESIGI (17.08.2026 parametre yapildi). Beyin, serit
        # acisinin hizli EMA'si ile yavas tabani arasindaki fark bu degeri
        # asinca "virajdayim" deyip SLALOMU BASTIRIR (bkz. _note_lane_angle).
        # CARLA kosusunda serit cikisi 42 etrafinda +-5.5 salindigi icin bu
        # yanlislikla tetiklendi: yol duz (Town04 road 25, 50 m'de 2.1 derece)
        # ama arac "VIRAJ -> slalom bastirildi" deyip engelin onunde durdu.
        # Gercek araca ait varsayilan (6.0) DEGISTIRILMEDI — orada serit
        # cikisi daha temiz ve viraj bastirma gercek bir ihtiyac.
        # HEDEF SERITTE GEREKEN BOSLUK (17.08.2026 parametre yapildi).
        # Kacis manevrasi R=3.07 m'de 1.5 m yanali 2.64 m'de tamamliyor;
        # 5.0 m istemek 2.4 m fazladan sart demek. CARLA kosusunda sol
        # 4.1 m acikken "IKI TARAF DA KAPALI" deyip engelin onunde durdu.
        # Gercek arac varsayilani (5.0) DEGISTIRILMEDI: orada karsi seritte
        # trafik olabilir ve muhafazakar olmak dogru.
        # WEAVE "ORTALANDI" ESIGI (17.08.2026 parametre yapildi). Hizalanma
        # fazi |yanal| bu degerin altina inince biter. 0.60 m, 2.96 m'lik
        # seritte serit yarisinin %40'i — CARLA kosularinda arac weave'i
        # 0.42-0.43 m kaymis bitirip serit takibine oyle donuyordu.
        # Gercek arac varsayilani (0.60) DEGISTIRILMEDI.
        self.declare_parameter('slalom_align_lateral', 0.6)
        self.brain.slalom_align_lateral = float(
            self.get_parameter('slalom_align_lateral').value)

        self.declare_parameter('side_min_clear', 5.0)
        self.brain.side_min_clear = float(
            self.get_parameter('side_min_clear').value)

        self.declare_parameter('curve_lane_dev', 6.0)
        self.brain.curve_lane_dev = float(
            self.get_parameter('curve_lane_dev').value)

        self.declare_parameter('slalom_max_weaves', 3)
        self.brain.slalom_max_weaves = int(
            self.get_parameter('slalom_max_weaves').value)
        self.declare_parameter('slalom_progress_distance', 3.0)
        self.brain.slalom_progress_distance = float(
            self.get_parameter('slalom_progress_distance').value)

        self.declare_parameter('slalom_return_free', 12.0)
        self.brain.slalom_return_free = float(
            self.get_parameter('slalom_return_free').value)
        self.declare_parameter('return_home_when_free', False)
        self.brain.return_home_when_free = bool(
            self.get_parameter('return_home_when_free').value)
        self.declare_parameter('slalom_pass_max_distance', 20.0)
        self.brain.slalom_pass_max_distance = float(
            self.get_parameter('slalom_pass_max_distance').value)
        # Gectigim seritte engel bu mesafeye girince serit degistir. 4.5 =
        # ilk engelin esigiyle ayni (tam kilit). 8.0 -> iki katmanli davranis.
        self.declare_parameter('slalom_pass_front_min', 4.5)
        self.brain.slalom_pass_front_min = float(
            self.get_parameter('slalom_pass_front_min').value)

        # Kirmizi isik emniyet supabi (bkz. decision_brain.red_light_timeout).
        # 0 = kapali. Supap acildiginda KIRMIZI_ISIK'a red_light_release_cooldown
        # kadar cooldown konur, yoksa ayni yanlis tespit araci hemen kilitler.
        self.declare_parameter('red_light_timeout', 40.0)
        self.brain.red_light_timeout = float(
            self.get_parameter('red_light_timeout').value)
        self.declare_parameter('red_light_release_cooldown', 15.0)
        self.brain.red_light_release_cooldown = float(
            self.get_parameter('red_light_release_cooldown').value)

        # Durustan kalkis gazi: 3 km/h hedefte Kff+Kp ~0.20 gaz uretir, bu
        # duran araci kimildatmaya yetmeyebilir ve integral 0.033/s ile cok
        # yavas toparlar. Arac neredeyse duruyorken tabana bas.
        self.declare_parameter('start_throttle', 0.35)
        self.declare_parameter('start_speed_ms', 0.30)
        self.start_throttle = float(self.get_parameter('start_throttle').value)
        self.start_speed_ms = float(self.get_parameter('start_speed_ms').value)

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

        # YANAL OFSET DOGRULAMA (14.08.2026). Beynin _lateral degeri yaw
        # entegralinden gelen bir OLU HESAP: 30 m'lik, buyuk direksiyon
        # salinimli bir manevrada birikmis hata tasiyabilir. "bitis yanal
        # ofset 2.40 m" ya gercek (arac kaydi) ya da tahmin hatasi — ikisinde
        # yapilacak sey zit. Weave basinda/sonunda CARLA odometrisinden
        # GERCEK yanal yer degistirmeyi olcup yan yana basiyoruz.
        self._weave_ref = None     # (x, y, yaw) weave basindaki poz

        # Şerit verisi tazelik takibi
        self._lane_steer      = 45
        self._lane_steer_time = 0.0
        self._LANE_FRESH_SEC  = 0.5

        self._last_log_state = None
        self._last_log_event = None
        self._last_hb_time   = 0.0

        self.timer = self.create_timer(0.05, self.control_loop)  # 20 Hz

        self.get_logger().info(
            f"NeuraVix Decision/Control node v2 started "
            f"(Bee1 + CARLA, 20 Hz, use_planner={self.use_planner} -> "
            f"{'pure-pursuit+A* ACIK (ROUTE takibi)' if self.use_planner else 'REAKTIF: serit+tabela+engel, waypoint YOK'})"
            f" | hiz: normal={self.brain.default_speed:.1f} "
            f"yavas={self.brain.slow_speed:.1f} "
            f"slalom={self.brain.slalom_speed:.1f} "
            f"donus={self.brain.turn_speed:.1f} km/h "
            f"(kalkis gazi {self.start_throttle:.2f})"
            f" | serit araligi {self.brain.lane_min}..{self.brain.lane_max} "
            f"(baslangic {self.brain.lane_index}), "
            f"slalom yanal hedef {self.brain.slalom_lateral_target:.1f} m, "
            f"donus politikasi="
            + (f"YOL (kendi serit >= {self.brain.slalom_return_free:.0f} m "
               f"acilinca don)" if self.brain.return_home_when_free else
               f"SLALOM (ancak bulundugum serit kapaninca don, "
               f"front<{self.brain.slalom_pass_front_min:.1f} veya "
               f"{self.brain.slalom_pass_max_distance:.0f} m yedek)"))

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

        # A* grid güncelleme (pist 0-73 m → grid 0-59 hücre) — SADECE planlama
        # açıkken. odom_x/y/yaw yukarıda her durumda saklanır (yaw slalom
        # fazları için şart); kapalıyken yalnız konum-tabanlı A* devre dışı.
        if self.use_planner:
            gx = int(self.odom_x * GRID_SCALE)
            gy = int(self.odom_y * GRID_SCALE)
            self.brain.update_position(gx, gy)

    # ----------------------------------------------------------------
    # FIX: Pure-pursuit — mevcut waypointe doğru Alkar açısı hesaplar
    # Odometri gelmemişse None döner (FSM tek başına devam eder)
    # ----------------------------------------------------------------
    def _pure_pursuit_steer(self):
        if not self.use_planner:
            return None          # planlama kapalı -> waypoint direksiyonu yok
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
            # ID-4'un yanal klerans profili "P" isaretcisiyle baslar ve P bir
            # SAYI DEGIL. Eskiden butun alanlar tek seferde float'a
            # ceviriliyordu; profil eklenince her ID-4 mesaji ValueError verip
            # TAMAMEN dusuyordu (17.08.2026 CARLA kosusu: arac tum surus
            # boyunca hic engel verisi almadi ve bariyere girdi). Artik
            # isaretciden ONCESI sayisal alanlar, sonrasi ayri ayristirilir.
            sayisal = parts[:parts.index('P')] if 'P' in parts else parts
            data  = [float(x) for x in sayisal]
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
            # ID-4 GENISLEMESI (17.08.2026): "...,P,y0,dy,c0,c1,..." yanal
            # klerans profili. Isaretci yoksa (eski lidar surumu, fail-safe)
            # profil None gecer ve beyin eski davranisina duser.
            prof = y0 = dy = None
            ham = [p.strip() for p in msg.data.split(',')]
            if 'P' in ham:
                k = ham.index('P')
                try:
                    y0, dy = float(ham[k + 1]), float(ham[k + 2])
                    prof = [float(v) for v in ham[k + 3:]]
                except (ValueError, IndexError):
                    prof = y0 = dy = None
            self.brain.obstacle_event(front=data[1], left=data[2], right=data[3],
                                      profile=prof, profile_y0=y0, profile_dy=dy)

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
        # Mesafe + YAW tabanlı slalom: CARLA hız geri beslemesi m/s, yaw
        # odometri quaternion'ından. Slalom fazları (escape/return) baş
        # açısıyla biter (Hata B, 2026-08-10) — yaw beslenmezse mesafe/zaman
        # yedeğine düşer, ki o da sıkı açıda 99° dönüp toparlayamıyordu.
        # x/y de veriliyor: yanal ofset yaw integrali yerine KONUMDAN olculur
        # (bkz. decision_brain.update_motion). Gercek aracta da ayni yol —
        # orada konum /odometry/filtered'dan (can_odom + slam_toolbox) gelir.
        self.brain.update_motion(speed_mps=self.current_speed,
                                 yaw=self.odom_yaw,
                                 x=self.odom_x, y=self.odom_y)
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
        self._olc_yanal(decision)

    def _olc_yanal(self, d):
        """Beynin yaw-entegralli yanal tahminini GERCEK odometriyle olc.

        Weave basinda konumu+yonu kaydeder, weave bitince aradaki yer
        degistirmenin baslangic yonune DIK bilesenini hesaplar. Beynin
        _lateral'i ile ayni tanim, ama entegral yerine iki gercek konumdan.
        Fark buyukse sorun kontrolde degil TAHMINDE demektir.
        """
        faz = d.get('avoid_phase')
        if faz is not None:
            if self._weave_ref is None and self.odom_x is not None \
                    and self.odom_yaw is not None:
                self._weave_ref = (self.odom_x, self.odom_y, self.odom_yaw)
            return
        if self._weave_ref is None:
            return
        x0, y0, yaw0 = self._weave_ref
        self._weave_ref = None
        if self.odom_x is None:
            return
        dx, dy = self.odom_x - x0, self.odom_y - y0
        # REP-103: +y sol. Baslangic yonune dik bilesen (sol pozitif).
        gercek  = -dx * math.sin(yaw0) + dy * math.cos(yaw0)
        tahmin  = float(self.brain._lateral)
        ileri   = dx * math.cos(yaw0) + dy * math.sin(yaw0)
        # ETKIN DONUS YARICAPI (17.08.2026). Manevranin "cok mu donuyoruz"
        # sorusu ancak boyle olculur: ileri/yanal ciftinden tek-yay
        # gecerse donus acisi ve yaricap cikar. CARLA'nin araci gercek
        # Bee1'den keskin donuyordu (olculen R=1.09 m; Bee1 limiti 3.10 m)
        # ve carla_steer_scale bunu duzeltmek icin var — bu satir olcegin
        # tuttugunu tek bakista gosterir.
        ek = ""
        if abs(ileri) > 0.05 or abs(gercek) > 0.05:
            th = 2.0 * math.atan2(abs(gercek), max(abs(ileri), 1e-6))
            if math.sin(th) > 1e-3:
                R = abs(ileri) / math.sin(th)
                ek = (f" | donus={math.degrees(th):.0f} deg R={R:.2f} m "
                      f"(Bee1 limiti 3.10 m)")
        self.get_logger().warn(
            f"[YANAL OLCUM] weave sonu: beyin tahmini={tahmin:+.2f} m | "
            f"odometriden GERCEK={gercek:+.2f} m | fark={gercek - tahmin:+.2f} m "
            f"| ileri gidilen={ileri:.1f} m{ek}")

    def _log_decision(self, d):
        st  = d['state']
        ev  = self.brain.last_event
        now = time.time()
        changed = (st != self._last_log_state) or (ev != self._last_log_event)
        if changed or (now - self._last_hb_time > 2.0):
            tag = "[KARAR]" if changed else "[DURUM]"
            # use_planner kapaliyken ROUTE hic okunmaz (_pure_pursuit_steer ilk
            # satirda None doner, update_position cagrilmaz, wp_idx artmaz) —
            # ama log yine "wp=0/25" yazdigi icin waypoint hesaba giriyormus
            # gibi gorunuyordu. ROUTE'a DOKUNULMADI, sadece metin duzeltildi.
            if not self.use_planner:
                wp_info = "wp=KAPALI"
            else:
                wp_info = (f"wp={self.wp_idx}/{len(ROUTE)}"
                           if self.odom_x is not None else "wp=?")
            self.get_logger().info(
                f"{tag} state={st} | steer={d['steering_angle']} "
                f"hiz={d['target_speed_kmh']:.0f} fren={d['brake']} "
                f"sinyal={d['signal_status']} serit={d.get('lane_index', 0)} "
                f"{wp_info} | sebep: {ev}")
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
        #
        # carla_steer_scale (17.08.2026, ÖLÇÜLDÜ): CARLA'nın aracı gerçek
        # Bee1'den ÇOK daha keskin dönüyor. Pist koşusunda weave sonu ölçümü
        # ileri 1.0 m / yanal 1.51 m verdi -> dönüş 113°, R=1.09 m, yani
        # ~60° teker açısı. Bee1'in mekanik limiti 31° (R=3.10 m). Yani
        # CARLA'da FSM 75 ("tam kilit") gerçekte olmayan bir manevra yapıyor;
        # burada ayarlanan slalom araca aktarılamaz, üstelik araç yan dönüp
        # ön sektörü duvara bakar hale geliyordu. Ölçek CARLA'yı aracın
        # gerçek dönüş yarıçapına indirir: 31/59.6 ≈ 0.52.
        # Varsayılan 1.0 = eski davranış (geniş Town04 kurulumları bozulmasın).
        carla_steer = max(-1.0, min(1.0,
                                    -steer_centered * self.carla_steer_scale / 45.0))

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

            # Duran araci kimildat (bkz. start_throttle). Sadece hedefe DOGRU
            # giderken: hedefi zaten gecmissek (err<=0) tabana basmak sacma.
            if self.current_speed < self.start_speed_ms and err > 0.0:
                throttle = max(throttle, self.start_throttle)

            ctrl.throttle = float(max(0.0, min(0.6, throttle)))
            ctrl.brake    = 0.0

        self.pub_carla_ctrl.publish(ctrl)

    def publish_debug(self, d):
        st = String(); st.data = str(d['state'])
        self.pub_state.publish(st)

        # SLALOM ALANLARI EKLENDI (20.08.2026). Eskiden dump yalnizca bu bes
        # alani tasiyordu; 08-20 slalom kayitlarinda arac 32 saniye
        # OBSTACLE_AVOID'da kalip bariyere girdi ve HANGI FAZDA oldugu
        # bag'den cikarilamadi — teshis icin gereken tam da o alanlardi.
        # Faz kodu: 0=yok 1=escape 2=pass 3=return 4=align
        _FAZ = {"escape": 1.0, "pass": 2.0, "return": 3.0, "align": 4.0}
        dump = Float32MultiArray()
        dump.data = [
            float(d['steering_angle']),
            float(d['target_speed_kmh']),
            float(d['brake']),
            float(d['signal_status']),
            float(d['speed_limit']),
            _FAZ.get(d.get('avoid_phase'), 0.0),
            float(getattr(self.brain, '_lateral', 0.0) or 0.0),
            float(getattr(self.brain, '_weave_lat', 0.0) or 0.0),
            float(d.get('lane_index', 0)),
            float(self.brain.front_distance),
            float(self.brain.left_distance),
            float(self.brain.right_distance),
        ]
        self.pub_decision.publish(dump)


# ================================================================
# Giriş Noktası
# ================================================================
def main(args=None):
    rclpy.init(args=args)
    node = DecisionControlNode()
    # KAPANIS (20.08.2026 duzeltildi, dort dugumde tutarli hale getirildi).
    # SIGTERM/Ctrl+C geldiginde rclpy context'i DISARIDAN kapatiyor; spin()
    # ExternalShutdownException firlatiyor ve finally'deki rclpy.shutdown()
    # "rcl_shutdown already called" ile patliyordu. Ikisi de calisma hatasi
    # DEGIL ama arac log'unun sonuna traceback biraktiklari icin gercek bir
    # hatayi gizleyebiliyorlardi. (can_odom'da ayni sey 13.07'de duzeltilmisti.)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
