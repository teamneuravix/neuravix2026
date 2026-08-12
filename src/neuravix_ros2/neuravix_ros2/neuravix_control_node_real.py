#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Team NeuraVix - TEKNOFEST 2026 Robotaksi (Hazır Araç) — GERÇEK ARAÇ (Bee1)
Karar Beyni (FSM) + ROS 2 Köprüsü, CARLA'sız

Karar mantığı decision_brain.py'dedir (CARLA'dan bağımsız, sim node ile ortak).
Bu dosya gerçek araca özel I/O katmanıdır. CAN sözleşmesi "2026 Araç Kullanıcı
Dokümanı" (smart_can_stuff / smart_can_msgs) esas alınarak yazılmıştır:

  - Direksiyon + hız: aracın HAZIR PID katmanı kullanılıyor
    (/beemobs/steering_target_value, /beemobs/speed_target_value, std_msgs/Float64).
    ⚠️ 2026-07-18: speed_pid_node hedefi Float64 dinliyor (önceki Float32
    varsayımı DDS tip eşleşmemesiyle hiç ulaşmıyordu). Varsayılan artık
    Float64; steering_pid_node teyit edilmedi, Float32 çıkarsa
    -p targets_float64:=false ile eski davranışa dönülür.
    Araç bu değerlere göre kendi ayarlı PID'iyle (steering_pid.yaml/thrt_pid.yaml)
    alt seviye PWM/pedal hesabını kendisi yapıyor; biz ham
    AUTONOMOUS_SteeringMot_Control / RC_THRT_DATA ile uğraşmıyoruz.
    ÇÖZÜLDÜ (2026-07-13 ölçümü): steering_target_value ham FeedbackSteeringAngle
    birimindedir (steering_pid hedef ile feedback'i doğrudan karşılaştırır).
    Ölçüm: düz=2, tam sol=-21, tam sağ=+26. FSM steering_angle>45=SOL, <45=SAĞ;
    ham sol=negatif -> gain NEGATİF. Varsayılanlar buna göre ayarlandı:
      hedef = (steering_angle-45)*(-0.75) + 2.0   (ham kilit -21..+26'ya clamp)
    2026-07-20 (debug_control5 bag analizi): auto-offset varsayılan olarak
    KAPATILDI, offset sabit 2.0 ve hedefe MUTLAK kilit clamp'i eklendi —
    auto-offset her restartta düz-olmayan tekerleği "düz" sayıp hatayı
    biriktiriyordu (-1 -> -3 -> -7 -> -8 -> -16; sonunda "düz" komutu tam sol).
    ⚠️ Kalan tek doğrulama: SOL komut fiziksel SOLA mı? Ters ise
    -p steer_target_gain:=0.78 (işareti çevir). PID,
    hedef topiğe 3 döngü boyunca mesaj gelmezse devreden çıkıyor; bu yüzden
    control_loop HER tikte (state ne olursa olsun) bu topiklere yayın yapar.
  - Fren: PID katmanı YOK, ham /beemobs/AUTONOMOUS_BrakePedalControl kullanılıyor
    (smart_can_msgs/Autonomousbrakepedalcontrol).
  - Kontak/vites/sinyal/acil durum: /beemobs/rc_unittoOmux
    (smart_can_msgs/Rcunittoomux). Node açılışta RC_Ignition=1 + vites=DRIVE
    gönderir (auto_ignition parametresiyle kapatılabilir — araçta ilk testte
    kontak elle/joystick ile açılacaksa false yapın). Acil durum
    (/safety/emergency_stop) hem FSM'i durdurur hem CAN'deki
    autonomous_emergency alanını 1 yapar (donanım seviyesinde motor tahrikini
    keser).

NOT (2026-07-11): smart_can_msgs artık GERÇEK paket (araç ekibinden alınan
smart_can_msgs.zip/smart_can_stuff.zip, src/smart_can_msgs'e wholesale swap
edildi) — mesaj TİP adları artık sadece ilk harfi büyük (dosya adından
türetilir, örn. Rcunittoomux, Autonomousbrakepedalcontrol), alan adları da
TASLAK'tan farklı (örn. rc_selection_gear -> rc_selectiongear). Aşağıdaki
alan adları buna göre güncellendi; topic isimleri smart_can_stuff'ın
launch/pid_params.yaml + scripts/beemobs.py dosyalarındaki kullanımla
karşılaştırılıp doğrulandı (rc_unittoOmux / AUTONOMOUS_BrakePedalControl /
steering_target_value / speed_target_value hepsi aynı isimde kaldı).
can2ros.cpp/ros2can.cpp kaynağı (src.zip) parola korumalı, elde edilemedi —
gerçek CAN alan aralıkları/ölçekleri (özellikle fren ACC/PER varsayılanları)
hâlâ araç başında doğrulanmalı.

TODO (araç günü / CAN dökümanı netleşince):
  - steering_target_value / speed_target_value birimleri doğrulanmadı.
  - Fren PER değeri şu an ikili (0/100); kademeli fren isteniyorsa
    decision_brain'e bir "brake_intensity" çıktısı eklenip buraya bağlanabilir.
  - El freni (AUTONOMOUS_HB_MotorControl) hiç kullanılmıyor (park/son durma
    senaryosu netleşince eklenecek).
  - Hız/direksiyon geri beslemesi (FB_VehicleSpeed, FeedbackSteeringAngle) şu an
    dinlenmiyor; sadece komut gönderiliyor, kapalı çevrim doğrulama yok.
"""

import time
import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Float64, Bool, String, Float32MultiArray
from nav_msgs.msg import Odometry
from smart_can_msgs.msg import (
    Rcunittoomux, Autonomousbrakepedalcontrol, Feedbacksteeringangle,
    Fbvehiclespeed,
)

from .decision_brain import (
    Alkar_Function4, ROUTE, WP_REACH, WP_STR_GAIN, GRID_SCALE,
    ID_LANE, ID_SIGN, ID_OBSTACLE, ID_PLANNER,
)

# rc_unittoOmux.rc_selectiongear değerleri (CAN: RC_SelectionGear)
GEAR_NEUTRAL = 0
GEAR_DRIVE   = 1
GEAR_REVERSE = 2


# ================================================================
# ROS 2 NODE
# ================================================================
class DecisionControlNodeReal(Node):
    def __init__(self):
        super().__init__('neuravix_decision_control_node_real')

        self.declare_parameter('odom_topic', '/odometry/filtered')
        # use_planner=false (VARSAYILAN): araç REAKTİF sürer (lane+tabela+engel);
        # pure-pursuit ve konum-tabanlı A* karar DEVRE DIŞI. ROUTE CARLA pistine
        # özel/anlamsız olduğu için, odom (EKF/slam) aksa bile hayalet rotaya
        # direksiyon verilmez. Gerçek rota + mission sequencer hazır olunca true.
        self.declare_parameter('use_planner', False)
        self.declare_parameter('auto_ignition', True)
        # steering_pid, hedefi (steering_target_value) FeedbackSteeringAngle ile
        # DOĞRUDAN karşılaştırır -> hedef, ham FeedbackSteeringAngle birimindedir.
        # FSM: steering_angle>45=SOL (+centered), <45=SAĞ (-centered).
        # Ham: sol=negatif, sağ=pozitif -> gain NEGATİF (yoksa ters kırar).
        #   hedef = (steering_angle-45)*gain + offset  (ham kilit menziline clamp)
        # KALİBRASYON MODELİ (2026-07-19, sağlamlaştırıldı):
        #   hedef = offset + clamp((steering_angle-45)*gain, delta_left, delta_right)
        #   hedef = clamp(hedef, steer_raw_min, steer_raw_max)   # mekanik kilit
        # - offset = DÜZ konumun ham FeedbackSteeringAngle değeri (ölçüm: 2).
        # - gain (mekanik oran) + delta_left/right (düzden tam kilide ham sapma):
        #   MEKANİK, sabit. Tam kilitte bir kez ölçülür, değişmez.
        # 2026-07-13 tam-kilit ölçümü (düz=2, sol=-21, sağ=+26 -> sapma ~-22/+23,
        #   gain ~-0.75). Kumandayla ölçüm kilide varmadığı için güvenilmez.
        self.declare_parameter('steer_target_gain', -0.75)
        # DEĞİŞTİ 2026-07-20: 0.0 -> 2.0 (ölçülmüş düz ham değeri) ve auto-offset
        # varsayılan olarak KAPALI. Gerekçe (debug_control5 bag analizi): node
        # 5 kez yeniden başlatıldı, auto-offset her seferinde o anki (düz OLMAYAN)
        # tekerleği "düz" sandı ve hata cırcır gibi birikti: -1 -> -3 -> -7 -> -8
        # -> -16. Son restarttan sonra FSM "düz" (45) derken hedef sabit -16, yani
        # neredeyse tam sol kilit; araç düz komutta daire çizer.
        self.declare_parameter('steer_target_offset', 2.0)
        # Düzden tam-kilide ham sapma (mekanik limit, clamp). Sol negatif.
        self.declare_parameter('steer_delta_left', -22.0)
        self.declare_parameter('steer_delta_right', 23.0)
        # MUTLAK ham hedef sınırı (mekanik kilit, 2026-07-13 ölçümü sol=-21/sağ=26).
        # delta clamp'i yalnız SAPMA'yı sınırlar; offset sonradan eklendiği için
        # kaymış bir offset hedefi kilidin ötesine taşıyabiliyordu (bag'de -34.75
        # gönderildi, feedback -37/-38'e dayandı = direksiyon motoru stopta zorluyor).
        self.declare_parameter('steer_raw_min', -21.0)
        self.declare_parameter('steer_raw_max', 26.0)
        # AUTO-OFFSET (varsayılan KAPALI, yukarıdaki gerekçe): açılırsa node
        # başlarken feedback'i okuyup offset yapar. ⚠️ ŞART: tekerler fiziksel
        # olarak DÜZ olmalı. Yakalanan değer steer_target_offset'ten
        # steer_auto_offset_max_dev'den fazla saparsa REDDEDİLİR (cırcır koruması).
        self.declare_parameter('steer_auto_offset', False)
        self.declare_parameter('steer_auto_offset_max_dev', 5.0)
        self.declare_parameter('steer_feedback_topic', '/beemobs/FeedbackSteeringAngle')
        # CAN hız geri beslemesi — mesafe tabanlı slalom için yol integrali.
        # speed_fb_scale: fb_reelvehiclespeed_kmh (uint8, aşağı yuvarlıyor) ->
        # m/s. can_odom_node ile aynı kalibre değer (0.31627, GPS/Kabsch ile
        # ölçülen %14 eksik sayma düzeltmesi dahil).
        self.declare_parameter('speed_feedback_topic', '/beemobs/FB_VehicleSpeed')
        self.declare_parameter('speed_fb_scale', 0.31627)
        # Hareket gözcüsü: bu kadar saniye gaz istenip hiç hız görülmezse bağır.
        self.declare_parameter('motion_watchdog_sec', 5.0)
        # Auto-offset için kaç örnek ortalanacak (ilk ~saniye).
        self.declare_parameter('steer_auto_offset_samples', 20)
        self.declare_parameter('brake_per_on', 100)
        # Araca yayınlanan hız hedefinin tavanı (km/h). FSM ne isterse istesin
        # /beemobs/speed_target_value bunu aşmaz — araç gazı dengesiz verdiği
        # için ilk testlerde düşük tutuluyor; -p max_speed_kmh:=X ile yükselt.
        self.declare_parameter('max_speed_kmh', 5.0)
        # FSM hiz hedeflerini araca yayinlamadan once carpan olcek. FSM
        # sabitleri (decision_brain.py: default 12, turn/slow 6, slalom 4,
        # park 3 km/h) sim icin ayarli; gercek aracta speed_target birimi ~2.4x
        # (5 gonderildi -> ~12 km/h olcudu 2026-07-18), yani olceksiz hepsi
        # ~2.4 kat hizli. Bu olcek TUM state'leri orantili dusurur (donus<seyir
        # yapisi korunur), max_speed_kmh ise mutlak tavan olarak ustte kalir:
        #   gonderilen = min(FSM_hedefi * speed_target_scale, max_speed_kmh)
        # Varsayilan 0.15: gercek arac icin guvenli dusuk hizlar ->
        #   seyir(12)~4.3, yavas/donus(6)~2.2, slalom(4)~1.4, park(3)~1.1 km/h
        #   (gercek ~ gonderilen * 2.4, 2026-07-18 tek olcumune gore).
        # Araca gore -p speed_target_scale:=X ile ayarla; 1.0 = FSM ham degerleri
        # (gercek ~12 km/h seyir -- fazla hizli, sadece kalibrasyon icin).
        self.declare_parameter('speed_target_scale', 0.15)
        # SOFT-START (Bug 5): hız hedefi 0'dan tama tek tik'te sıçramasın ->
        # birim/sn artış sınırı. Kalkış yumuşar (aracın speed PID step-response'u
        # + auto_ignition ile eşzamanlı DRIVE sarsıntısını azaltır). Yavaşlama/
        # fren ANINDA (güvenlik), sadece hızlanma rampalı. 0 = rampa kapalı.
        self.declare_parameter('speed_ramp_up', 0.6)
        # Hedef topiklerinin mesaj tipi. Araçtaki speed_pid_node'un Float64
        # dinlediği 2026-07-18'de doğrulandı (Float32 hiç eşleşmiyordu);
        # steering_pid_node Float32 çıkarsa -p targets_float64:=false yapın.
        self.declare_parameter('targets_float64', True)

        odom_topic = self.get_parameter('odom_topic').get_parameter_value().string_value
        self.use_planner = self.get_parameter('use_planner').get_parameter_value().bool_value
        self.auto_ignition = self.get_parameter('auto_ignition').get_parameter_value().bool_value
        self.steer_target_gain = self.get_parameter('steer_target_gain').get_parameter_value().double_value
        self.steer_target_offset = self.get_parameter('steer_target_offset').get_parameter_value().double_value
        self.steer_delta_left = self.get_parameter('steer_delta_left').get_parameter_value().double_value
        self.steer_delta_right = self.get_parameter('steer_delta_right').get_parameter_value().double_value
        self.steer_raw_min = self.get_parameter('steer_raw_min').get_parameter_value().double_value
        self.steer_raw_max = self.get_parameter('steer_raw_max').get_parameter_value().double_value
        self.brake_per_on = self.get_parameter('brake_per_on').get_parameter_value().integer_value
        self.max_speed_kmh = self.get_parameter('max_speed_kmh').get_parameter_value().double_value
        self.speed_target_scale = self.get_parameter('speed_target_scale').get_parameter_value().double_value
        self.speed_ramp_up = self.get_parameter('speed_ramp_up').get_parameter_value().double_value
        self._speed_cmd = 0.0   # soft-start için rampalanan mevcut hız komutu
        self.steer_auto_offset = self.get_parameter('steer_auto_offset').get_parameter_value().bool_value
        self._auto_off_max_dev = self.get_parameter(
            'steer_auto_offset_max_dev').get_parameter_value().double_value
        # Auto-offset reddedilirse geri dönülecek referans (ölçülmüş düz değeri)
        self._offset_fallback = self.steer_target_offset
        steer_fb_topic = self.get_parameter('steer_feedback_topic').get_parameter_value().string_value
        speed_fb_topic = self.get_parameter('speed_feedback_topic').get_parameter_value().string_value
        self.speed_fb_scale = self.get_parameter('speed_fb_scale').get_parameter_value().double_value
        self._auto_off_n = self.get_parameter('steer_auto_offset_samples').get_parameter_value().integer_value

        # Auto-offset durumu: başlangıçta feedback örneklerini toplar, yeterince
        # gelince ortalamayı steer_target_offset yapar (bir kez). Yakalanana
        # kadar sabit param offset kullanılır (ilk komutlar çılgın olmasın).
        self._auto_off_samples = []
        self._auto_off_done = not self.steer_auto_offset  # kapalıysa hiç yakalama

        self.brain = Alkar_Function4()

        # --- Bee1 CAN çıkışları ---
        self.pub_omux = self.create_publisher(Rcunittoomux, '/beemobs/rc_unittoOmux', 10)
        self.pub_brake = self.create_publisher(
            Autonomousbrakepedalcontrol, '/beemobs/AUTONOMOUS_BrakePedalControl', 10)
        # PID hedef değerleri (araç tarafı alt seviye PWM/pedal hesabını kendi yapar)
        self._target_cls = (
            Float64
            if self.get_parameter('targets_float64').get_parameter_value().bool_value
            else Float32
        )
        self.pub_steer_target = self.create_publisher(
            self._target_cls, '/beemobs/steering_target_value', 10)
        self.pub_speed_target = self.create_publisher(
            self._target_cls, '/beemobs/speed_target_value', 10)

        # Debug
        self.pub_state    = self.create_publisher(String, '/neuravix/current_state', 10)
        self.pub_decision = self.create_publisher(Float32MultiArray, '/neuravix/decision_dump', 10)

        # /master perception kanalı (lane_follower, tabela_tespit, obstacle_lidar — değişmedi)
        self.sub_master    = self.create_subscription(String, '/master', self.master_cb, 10)
        self.sub_emergency = self.create_subscription(Bool, '/safety/emergency_stop', self.emergency_cb, 10)
        self._emergency = False

        # Direksiyon feedback (auto-offset + kapalı-çevrim gözlem)
        self.steer_fb = None
        self.sub_steer_fb = self.create_subscription(
            Feedbacksteeringangle, steer_fb_topic, self._steer_fb_cb, 10)

        # Konum geri beslemesi — gerçek lokalizasyon zinciri (slam_toolbox + EKF
        # local) devreye girene kadar bu topic hiç yayınlanmayabilir; bu durumda
        # odom_x hep None kalır ve pure-pursuit/A* konum güncellemesi devre dışı
        # kalır (FSM tek başına şerit+tabela+engel ile sürer).
        self.odom_x   = None
        self.odom_y   = None
        self.odom_yaw = None
        self.sub_odom = self.create_subscription(
            Odometry, odom_topic, self._odom_cb, 10)

        # --- Katedilen mesafe: MESAFE TABANLI SLALOM'un ölçüsü (2026-07-21) ---
        # Slalom fazları artık saate değil yol alınan mesafeye bağlı (araçta
        # 6.0 s süren bir weave boyunca araç 0.00 m gitmişti). İki kaynak var,
        # odometri varsa o tercih edilir; yoksa CAN hızı integre edilir.
        #   - odometri (can_odom/slam/EKF): _odom_cb konumdan yol toplar
        #   - CAN hızı: fb_reelvehiclespeed_kmh (uint8, 1 km/h adım -> kaba)
        # Not: her ikisi de yoksa decision_brain otomatik olarak eski zaman
        # tabanlı slaloma düşer (bkz. Alkar_Function4.update_motion).
        self._trav_dist = 0.0        # odometriden toplanan yol (m)
        self._trav_prev = None
        self.can_speed_mps = None
        self.can_speed_time = 0.0
        self._no_motion_since = None
        self.motion_watchdog_sec = self.get_parameter(
            'motion_watchdog_sec').get_parameter_value().double_value
        self.sub_can_speed = self.create_subscription(
            Fbvehiclespeed, speed_fb_topic, self._can_speed_cb, 10)

        # Waypoint indeksi (pure-pursuit için) — ROUTE CARLA pistine özeldir,
        # gerçek pist/rota (yarış günü GEOJSON) hazır olana kadar anlamsızdır
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
            f"NeuraVix Decision/Control node (GERÇEK ARAÇ) started, "
            f"odom_topic='{odom_topic}', speed_fb='{speed_fb_topic}' "
            f"(x{self.speed_fb_scale:.5f} -> mesafe tabanli slalom), "
            f"use_planner={self.use_planner}, "
            f"auto_ignition={self.auto_ignition}, "
            f"max_speed={self.max_speed_kmh:.1f} km/h, speed_scale={self.speed_target_scale:.2f}, "
            f"steer gain={self.steer_target_gain:.2f} delta=[{self.steer_delta_left:.0f},{self.steer_delta_right:.0f}] "
            f"offset={self.steer_target_offset:.1f} auto_offset={self.steer_auto_offset} "
            f"ham_limit=[{self.steer_raw_min:.0f},{self.steer_raw_max:.0f}], 20 Hz.")

    # ----------------------------------------------------------------
    # Odometri callback — standart nav_msgs/Odometry, kaynağı fark etmez
    # ----------------------------------------------------------------
    def _steer_fb_cb(self, msg):
        # Ham int8 direksiyon feedback'i (düz=?, sol=neg, sağ=poz).
        self.steer_fb = int(msg.feedbacksteeringangle)
        if self._auto_off_done:
            return
        # Başlangıçta tekerler DÜZ varsayımıyla offset'i yakala.
        self._auto_off_samples.append(self.steer_fb)
        if len(self._auto_off_samples) >= self._auto_off_n:
            captured = sum(self._auto_off_samples) / len(self._auto_off_samples)
            self._auto_off_done = True
            # CIRCIR KORUMASI (2026-07-20): tekerler düz değilken başlatılırsa
            # yakalanan değer "düz"ü kaydırır ve her restartta hata birikir
            # (bag'de -1 -> -3 -> -7 -> -8 -> -16). Ölçülmüş düz değerinden
            # fazla sapan yakalamayı kabul etme.
            if abs(captured - self._offset_fallback) > self._auto_off_max_dev:
                self.get_logger().warn(
                    f"AUTO-OFFSET REDDEDİLDİ: yakalanan={captured:.1f}, "
                    f"beklenen düz={self._offset_fallback:.1f} "
                    f"(sapma > {self._auto_off_max_dev:.1f}). Tekerler düz "
                    f"değilken başlatılmış olabilir -> offset "
                    f"{self._offset_fallback:.1f} olarak KALIYOR.")
                self.steer_target_offset = self._offset_fallback
                return
            self.steer_target_offset = float(captured)
            self.get_logger().info(
                f"AUTO-OFFSET yakalandı: düz feedback={captured:.1f} "
                f"-> steer_target_offset={self.steer_target_offset:.1f} "
                f"({len(self._auto_off_samples)} örnek). Tekerler düz değilse "
                f"node'u tekerler düzken yeniden başlatın.")

    def _can_speed_cb(self, msg):
        """CAN hız geri beslemesi -> mesafe tabanlı slalom için hız kaynağı."""
        self.can_speed_mps = float(msg.fb_reelvehiclespeed_kmh) * self.speed_fb_scale
        self.can_speed_time = time.time()

    def _check_motion(self, cmd_speed):
        """HAREKET GÖZCÜSÜ (2026-07-21, algi8 bag analizi).

        algi8'de node 170 s boyunca hız hedefi yayınladı (ort 2.63), FSM 15 s
        slalom yaptı, direksiyon hedefi -16.8..+20.8 arası savruldu — ama araç
        HİÇ kıpırdamadı: FB_VehicleSpeed 0, FB_MotorDriver.vehiclerpm 0,
        plustripdistance 0 ve /beemobs/RC_THRT_DATA'ya TEK BİR mesaj bile
        yayınlanmamıştı. Sebep kodda değil: gaz zinciri kopuktu
        (speed_pid_node -> /beemobs/rcthrtdata -> **throttle_relay** ->
        /beemobs/RC_THRT_DATA -> can_handler). Karşılaştırma: algi7'de
        RC_THRT_DATA vardı (pedal 62-77) ve araç yürüdü (rpm 44, trip 4135).

        Bu sessiz başarısızlık hiçbir yerde uyarı üretmiyordu. Artık üretiyor:
        gaz istiyoruz ama geri besleme sıfırsa ne yapılacağını da söyleyerek
        bağırıyor. Gözcü yalnızca CAN hız geri beslemesi GERÇEKTEN akıyorken
        çalışır — yoksa 'hareket yok' ile 'veri yok' ayırt edilemezdi."""
        now = time.time()
        fresh = (self.can_speed_mps is not None
                 and now - self.can_speed_time < 1.0)
        if not fresh or cmd_speed <= 0.0:
            self._no_motion_since = None
            return
        if self.can_speed_mps > 0.0:
            self._no_motion_since = None
            return
        if self._no_motion_since is None:
            self._no_motion_since = now
            return
        if now - self._no_motion_since >= self.motion_watchdog_sec:
            self.get_logger().error(
                f"HAREKET YOK: {now - self._no_motion_since:.0f} s'dir hiz hedefi "
                f"{cmd_speed:.2f} yayinlaniyor ama FB_VehicleSpeed 0. Gaz zinciri "
                f"muhtemelen kopuk -> 'ros2 topic hz /beemobs/RC_THRT_DATA' bos ise "
                f"throttle_relay (ve speed_fb_relay) calismiyor demektir: "
                f"'ros2 run bee1_description throttle_relay'. Fren/vites de kontrol et.",
                throttle_duration_sec=10.0)

    def _odom_cb(self, msg):
        # Katedilen yol (mesafe tabanlı slalomun tercih edilen kaynağı):
        # ardışık konumlar arası öteleme toplanır. use_planner'dan bağımsız —
        # rota anlamsız olsa bile "ne kadar yol gittim" bilgisi geçerlidir.
        px, py = msg.pose.pose.position.x, msg.pose.pose.position.y
        if self._trav_prev is not None:
            step = math.hypot(px - self._trav_prev[0], py - self._trav_prev[1])
            if step < 5.0:            # sıçrama/yeniden lokalizasyon zıplamasını yut
                self._trav_dist += step
        self._trav_prev = (px, py)

        self.odom_x = msg.pose.pose.position.x
        self.odom_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.odom_yaw = math.atan2(siny, cosy)

        # use_planner kapalıyken odom saklanır (log/debug) ama konum-tabanlı
        # karar (A* grid) beslenmez -> hayalet CARLA rotası riski yok.
        if self.use_planner:
            gx = int(self.odom_x * GRID_SCALE)
            gy = int(self.odom_y * GRID_SCALE)
            self.brain.update_position(gx, gy)

    # ----------------------------------------------------------------
    # Pure-pursuit — mevcut waypointe doğru Alkar açısı hesaplar.
    # Odometri gelmemişse None döner (FSM tek başına devam eder).
    # ----------------------------------------------------------------
    def _pure_pursuit_steer(self):
        if not self.use_planner:
            return None          # planner kapalı: FSM/lane çıktısı kullanılır
        if self.odom_x is None:
            return None
        if self.wp_idx >= len(ROUTE):
            return None

        wp = ROUTE[self.wp_idx]
        dx = wp['x'] - self.odom_x
        dy = wp['y'] - self.odom_y

        if math.hypot(dx, dy) < WP_REACH and self.wp_idx < len(ROUTE) - 1:
            self.wp_idx += 1
            wp = ROUTE[self.wp_idx]
            dx = wp['x'] - self.odom_x
            dy = wp['y'] - self.odom_y

        target_yaw = math.atan2(dy, dx)
        err_rad = (target_yaw - self.odom_yaw + math.pi) % (2 * math.pi) - math.pi
        err_deg = math.degrees(err_rad)

        steer = int(45 + err_deg * WP_STR_GAIN)
        return max(15, min(75, steer))

    # ----------------------------------------------------------------
    # /master parser — sim ile birebir aynı
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
        self._emergency = bool(msg.data)
        self.brain.emergency_event(active=self._emergency)

    # ----------------------------------------------------------------
    # Ana döngü — sim ile aynı hibrit direksiyon karıştırması
    # ----------------------------------------------------------------
    def control_loop(self):
        # Katedilen mesafe + YAW'ı beyne ver (slalom fazlarının ölçüsü).
        # Slalom escape/return artık baş açısıyla biter (Hata B, 2026-08-10);
        # yaw odometriden gelir (slam_toolbox/EKF çıktısı). Yaw yoksa mesafe,
        # o da yoksa zaman yedeğine düşer. odom_yaw None ise update_motion
        # güvenle yok sayar.
        if self._trav_prev is not None:
            self.brain.update_motion(distance=self._trav_dist, yaw=self.odom_yaw)
        elif (self.can_speed_mps is not None
                and time.time() - self.can_speed_time < 1.0):
            self.brain.update_motion(speed_mps=self.can_speed_mps, yaw=self.odom_yaw)

        self.brain._update_state_machine()
        decision = self.brain.get_decision()

        lane_fresh = (time.time() - self._lane_steer_time) < self._LANE_FRESH_SEC

        if decision['state'] == 'LANE_FOLLOW':
            wp_steer = self._pure_pursuit_steer()

            if wp_steer is not None and lane_fresh:
                blended = int(0.55 * wp_steer + 0.45 * self._lane_steer)
                decision['steering_angle'] = max(15, min(75, blended))
            elif wp_steer is not None:
                decision['steering_angle'] = wp_steer
            # wp_steer is None: odometri yok, FSM çıktısı kullanılır

        elif lane_fresh and decision.get('lane_blend', 0.0) > 0.0:
            # KAÇINMA SIRASINDA ŞERİDİ TAMAMEN BIRAKMA (2026-07-21):
            # eskiden OBSTACLE_AVOID'da FSM'in sabit 70/25/20/65 değeri ham
            # gidiyordu; oysa araçta slalom süresinin %30-97'sinde geçerli
            # şerit verisi vardı. Kaçış fazında şerit az (engelden kaçmak
            # önce gelir), dönüş fazında baskın ağırlıkla karışır.
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
            if not self.use_planner:
                wp_info = "planner=off (reaktif)"
            elif self.odom_x is not None:
                wp_info = f"wp={self.wp_idx}/{len(ROUTE)}"
            else:
                wp_info = "wp=? (odom yok)"
            # Araca giden GERCEK hiz hedefi = FSM hedefi max_speed_kmh ile
            # kirpilmis (fren varsa 0). Log'da hem komut hem parantez icinde
            # FSM ham hedefi gosterilir (12 gibi ham deger yaniltmasin).
            hiz_cmd = 0.0 if int(d['brake']) else min(
                float(d['target_speed_kmh']) * self.speed_target_scale, self.max_speed_kmh)
            self.get_logger().info(
                f"{tag} state={st} | steer={d['steering_angle']} "
                f"hiz={hiz_cmd:.1f}(fsm={d['target_speed_kmh']:.0f}) fren={d['brake']} "
                f"sinyal={d['signal_status']} {wp_info} | sebep: {ev}")
            self._last_log_state = st
            self._last_log_event = ev
            self._last_hb_time   = now

    # ----------------------------------------------------------------
    # Çıktı: kontak/vites/sinyal/acil durum (rc_unittoOmux) +
    # direksiyon/hız PID hedefi + ham fren
    # ----------------------------------------------------------------
    def publish_commands(self, d):
        steer_centered = float(d['steering_angle']) - 45.0  # 0=düz, +/-30 sol/sağ
        speed_kmh      = min(float(d['target_speed_kmh']) * self.speed_target_scale,
                             self.max_speed_kmh)
        brake          = int(d['brake'])
        signal         = int(d['signal_status'])

        # rc_unittoOmux'taki sinyal alanını FSM kararına göre güncelle
        omux_signal = Rcunittoomux()
        omux_signal.rc_ignition = 1 if self.auto_ignition else 0
        omux_signal.rc_selectiongear = GEAR_DRIVE if self.auto_ignition else GEAR_NEUTRAL
        omux_signal.rc_signalstatus = signal
        omux_signal.autonomous_emergency = 1 if self._emergency else 0
        self.pub_omux.publish(omux_signal)

        # Direksiyon + hız: PID hedef değerleri (⚠️ birim doğrulanmadı, bkz. dosya başı TODO)
        steer_msg = self._target_cls()
        # hedef = offset(auto) + clamp(sapma, mekanik_sol, mekanik_sağ)
        # offset auto-yakalandığı için zaman içinde kayan sıfıra bağışık;
        # delta clamp mekanik kilit dışına komut gitmesini engeller.
        delta = steer_centered * self.steer_target_gain
        delta = max(self.steer_delta_left, min(self.steer_delta_right, delta))
        target = self.steer_target_offset + delta
        # MUTLAK kilit clamp'i (2026-07-20): delta clamp'i sapmayı sınırlar ama
        # offset üstüne eklendiği için hedef mekanik kilidin ötesine çıkabiliyordu.
        target = max(self.steer_raw_min, min(self.steer_raw_max, target))
        steer_msg.data = float(target)
        self.pub_steer_target.publish(steer_msg)

        # SOFT-START rampası (Bug 5): hızlanma sınırlı, yavaşlama/fren anında.
        speed_target = 0.0 if brake else speed_kmh
        if speed_target <= self._speed_cmd or self.speed_ramp_up <= 0.0:
            self._speed_cmd = speed_target                      # yavaşla/fren: anında
        else:
            step = self.speed_ramp_up * 0.05                    # birim/tik (20 Hz)
            self._speed_cmd = min(speed_target, self._speed_cmd + step)
        speed_msg = self._target_cls(); speed_msg.data = float(self._speed_cmd)
        self.pub_speed_target.publish(speed_msg)
        self._check_motion(self._speed_cmd)

        # Fren: ham CAN mesajı (PID katmanı yok)
        brk = Autonomousbrakepedalcontrol()
        brk.autonomous_brakepedalmotor_en = 1
        brk.autonomous_brakemotor_voltage = 1
        brk.autonomous_brakepedalmotor_acc = 10000
        brk.autonomous_brakepedalmotor_per = self.brake_per_on if brake else 0
        self.pub_brake.publish(brk)

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
    node = DecisionControlNodeReal()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
