#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GERÇEK ARAÇ - TASLAK odometri kaynağı (rev2).
CAN geri beslemesinden (hız + direksiyon açısı + vites) bisiklet (Ackermann)
kinematik modeliyle "odom -> base_link" TF'i ve nav_msgs/Odometry üretir.

rev7 değişiklikleri (2026-07-20, pist_19_3tem bag'i ile ODOM TEŞHİSİ):
  ⚠️ rev6'nın VARSAYILANI GERİ ALINDI: use_imu_orientation artık False,
     use_imu_yaw artık True (gyro entegre). Sebep ÖLÇÜLDÜ:
     bag'den can_odom birebir yeniden hesaplanıp üç yaw kaynağı
     karşılaştırıldı (247 m'lik sürüş, kapalı pist turu):
       mutlak_yaw (rev6) -> tur kapanma hatası 100.4 m  (yörünge hiç kapanmıyor)
       gyro_entegre      -> tur kapanma hatası  10.3 m  (tertemiz dikdörtgen tur)
       tan_steer         -> tur kapanma hatası  30.6 m
     Kök neden: XSENS'in mutlak yaw'ı MANYETOMETRE referanslı; pistin ÇELİK
     BARİYERLERİ manyetik alanı bozuyor. Tüm sürüşte toplam yaw değişimi
     mutlak=+149.6° iken gyro=+273.6° -- AHRS gerçek dönüşü ~124° EKSİK
     sayıyor. İşaret/konvansiyon sorunu DEĞİL (d(yaw)/dt ile gyro korelasyonu
     +0.80, yani NED/ENU ters çevirme yok) -- referansın kendisi bozuk.
  - Sonuç: manyetik ortamı bozuk pistlerde mutlak AHRS yaw KULLANILMAMALI.
    Gyro bias'ı (yavaş, düzgün) slam scan-matching'in düzeltebildiği türden;
    manyetik hata (büyük, sistematik) değil. Bozuk prior slam'i de boğuyordu:
    "harita sonlarında kayma" şikayetinin asıl kaynağı buydu.
  - Mutlak yaw'ı yine de denemek istersen: use_imu_orientation:=true
    (açık alanda, çelik bariyer yokken mantıklı olabilir).

rev6 değişiklikleri (2026-07-18, pisttem18 bag'i ile offline haritalama):
  - use_imu_orientation parametresi (varsayılan True): yaw artık gyro
    angular_velocity.z ENTEGRE EDİLEREK değil, XSENS AHRS'nin MUTLAK
    orientation quaternion'undan alınır. İlk IMU örneği referans (yaw_offset)
    olarak yakalanır, sonrası yaw = (mutlak_yaw - yaw_offset) -> odom yine
    (0,0,0)'dan başlar ama yaw entegrasyon biriktirmediği için gyro bias'ı
    ARTIK KAYMAZ (drift'siz). Sebep: pisttem18 haritasının sonlarında görülen
    yaw kayması gyro entegrasyonundan geliyordu; bag'in /imu/data'sında geçerli
    orientation (ör. z=-0.864 w=0.504) mevcut olduğu echo ile doğrulandı.
  - Öncelik sırası: use_imu_orientation (mutlak, drift'siz) > use_imu_yaw
    (gyro entegre, bias birikir) > tan(steer) kinematik model. IMU imu_timeout
    süredir bayatsa yine tan(steer)'e düşülür. Eski gyro-entegre davranışını
    geri istersen: use_imu_orientation:=false use_imu_yaw:=true.

rev5 değişiklikleri (2026-07-13, 5. araç oturumu / output11 bulguları):
  - steer_feedback_gain/offset ARTIK KALİBRE (araçta ölçüldü, 2026-07-13):
    ham feedbacksteeringangle düz=2, tam sol=-21, tam sağ=26 (int8).
    Spec limitleri (iç 32.5°/dış 30.0°) -> eşdeğer bisiklet açısı ~31.25°.
    gain = -(31.25° rad) / ortalama(|Δsol|=23, |Δsağ|=24) = -0.02322 rad/birim
    (ham negatif = fiziksel SOL; REP-103'te pozitif steer = sol dönüş olduğu
    için işaret negatif). offset = 2.0. Çözünürlük ~1.33°/birim, sol/sağ
    asimetrisi ±%2 -- tek lineer gain yeterli. İlk sürüşte işaret doğrulaması:
    sola dönerken steer_rad POZİTİF olmalı (odom sola kıvrılmalı).
  - speed_topic varsayılanı /beemobs/fbvehiclespeed -> /beemobs/FB_VehicleSpeed.
    rev4'te pid_params.yaml'daki speed_pid feedback topic'ine güvenilmişti ama
    araçta /beemobs/fbvehiclespeed'in yayınlandığı hiç DOĞRULANMADI;
    /beemobs/FB_VehicleSpeed ise iki kez canlı echo'landı (5. oturum).
    Sonuç: hız callback'i hiç ateşlenmedi -> stale-guard v=0 -> odom origin'de
    dondu -> slam_toolbox minimum_travel_distance'ı hiç geçemedi -> harita yok.
  - Hız alanı fb_reelvehiclespeed_ms -> fb_reelvehiclespeed_kmh: üç alan da
    uint8 (msg dosyasından doğrulandı). _ms alanı 1 m/s çözünürlüklü, yani
    haritalama hızında (5-10 km/h) 0<->1<->2 zıplar; _kmh alanı 1 km/h
    (~0.28 m/s) çözünürlüklü, düşük hızda çok daha kullanılabilir.
    speed_scale varsayılanı bu yüzden tekrar 0.27778 (km/h -> m/s) oldu.
  - İleride daha ince hız gerekirse: Fbmotordriver.vehiclerpm uint16 --
    rpm->m/s kalibrasyonu (aktarma oranı + teker yarıçapı) araçta ölçülmeli.
    plustripdistance (uint16) da doğrudan yol sayacı olabilir, birimi bilinmiyor.

rev4 değişiklikleri (2026-07-11): gerçek smart_can_msgs paketine (araç
ekibinden alınan smart_can_msgs.zip/smart_can_stuff.zip, src/smart_can_msgs'e
wholesale swap edildi) geçiş:
  - Mesaj TİP adları artık Fbvehiclespeed / Feedbacksteeringangle /
    Fbmotordriver (dosya adından türetilir, sadece ilk harf büyük).
  - FbVehicleSpeed'in fb_reel_vehicle_speed_ms (float32) alanı yerine gerçek
    pakette fb_reelvehiclespeed_ms (uint8) var -- adı zaten m/s dediği için
    speed_scale varsayılanı 1.0'a çekildi (eskiden km/h->m/s çeviriyordu).
    ⚠️ uint8 olması çözünürlüğün DBC'de ölçeklendiğini düşündürüyor
    (can2ros.cpp kaynağı parola korumalı, doğrulanamadı) -- araç başında
    speed_scale'in gerçekten 1.0 mı olduğu ölçülmeli.
  - FeedbackSteeringAngle.feedback_steering_angle (float32) ->
    feedbacksteeringangle (int8); gain/offset kalibrasyonu hâlâ gerekiyor.
  - FbMotorDriver.gear_status_from_motor alan adı DEĞİŞMEDİ (aynı kaldı).
  - speed_topic varsayılanı /beemobs/FB_VehicleSpeed -> /beemobs/fbvehiclespeed
    (smart_can_stuff/launch/pid_params.yaml'daki speed_pid_node
    feedback_value_topic ile eşleşecek şekilde). steering_topic
    (/beemobs/FeedbackSteeringAngle) aynı dosyada birebir doğrulandı,
    değişmedi. gear_topic hâlâ doğrulanmadı (PID config'inde referans yok).

rev3 değişiklikleri (2026-07-10):
  4) use_imu_yaw parametresi: true yapılırsa yaw_rate, tan(steer) kinematik
     modelinden DEĞİL doğrudan IMU gyro'dan (angular_velocity.z) alınır.
     XSENS MTI-680 gyro'su steer kalibrasyon hatasından ve teker kaymasından
     etkilenmez -> yaw kayması ciddi azalır. IMU verisi imu_timeout süredir
     gelmiyorsa otomatik olarak tan(steer) modeline geri düşülür.
     Varsayılan false: ilk testte kinematik model, ikinci testte IMU denenir.

rev2 değişiklikleri (2026-07-10):
  1) speed_scale parametresi eklendi (varsayılan 0.27778 = km/h -> m/s).
     Araç dokümanına göre /beemobs/FB_VehicleSpeed alanı FB_VehicleSpeed_KMh,
     yani KM/H cinsinden. Eski kod m/s varsayıyordu -> odometri 3.6x hızlı
     koşuyordu. Gerçek birim farklı çıkarsa sadece bu parametre değişir.
  2) NEUTRAL viteste artık v=0 zorlanmıyor (coasting/yokuş yuvarlanması
     odometriye yansır). Sadece BİLİNMEYEN vites değerinde v=0.
  3) Stale-data koruması: hız mesajı speed_timeout süredir gelmiyorsa
     (CAN köprüsü düştü vb.) v=0 kabul edilir ve uyarı loglanır. Böylece
     eski hız değeri sonsuza kadar entegre edilmez.

⚠️ TASLAK / DOĞRULANMAMIŞ — araç günü mutlaka kalibre edilmeli:
  - steer_feedback_gain/offset: KALİBRE EDİLDİ 2026-07-13 (bkz. rev5 notu);
    ilk sürüşte sadece işaret doğrulaması kaldı (sola dönüş -> steer_rad > 0).
  - speed_scale: varsayılan km/h->m/s. Araçta düşük hızda düz 10 m sürüp
    odom x'inin ~10 m çıktığı doğrulanmalı.
  - wheelbase: BEE1 dingil mesafesi 1860 mm (dokümandan), değişmez.
  - Gear sabitleri (0/1/2) TASLAK varsayım; gerçek smart_can_msgs gelince
    'ros2 interface show' ile doğrulanmalı.
  - Saf dead reckoning: yaw zamanla kayar; düzeltme slam_toolbox'ın
    scan-matching'i (map->odom) ile gelir.

Kullanım:
    ros2 run bee1_description can_odom --ros-args \\
        -p steer_feedback_gain:=... -p steer_feedback_offset:=... \\
        -p speed_scale:=0.27778
"""

import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

from smart_can_msgs.msg import Fbvehiclespeed, Feedbacksteeringangle, Fbmotordriver

GEAR_NEUTRAL = 0
GEAR_DRIVE = 1
GEAR_REVERSE = 2


class CanOdomNode(Node):
    def __init__(self):
        super().__init__('can_odom_node')

        self.declare_parameter('speed_topic', '/beemobs/FB_VehicleSpeed')
        self.declare_parameter('steering_topic', '/beemobs/FeedbackSteeringAngle')
        self.declare_parameter('gear_topic', '/beemobs/FB_MotorDriver')
        self.declare_parameter('odom_topic', '/odometry/can_wheel')
        self.declare_parameter('wheelbase', 1.86)  # BEE1 dingil mesafesi (m)
        # ⚠️ Aşağıdakiler araç günü doğrulanacak/kalibre edilecek
        # 2026-07-17 GPS ile kalibre: bag'deki /gnss yer-gerçeğine karşı
        # (Kabsch) odom %14 az sayıyordu -> 0.27778 x 1.139 = 0.31627.
        # Sebep: fb_reelvehiclespeed_kmh uint8 (tam sayı km/h), sürekli aşağı
        # yuvarlama toplamda mesafeyi kısaltıyor. Yeni değerle GPS yolu 431 m,
        # odom 382 m, Kabsch ölçek 1.000 (test: scratchpad/odom_kalibre.py).
        self.declare_parameter('speed_scale', 0.31627)  # fb_reelvehiclespeed_kmh -> m/s (GPS-kalibre)
        # Kalibre 2026-07-13 (bkz. rev5 notu): düz=2, tam sol=-21, tam sağ=26
        self.declare_parameter('steer_feedback_gain', -0.02322)  # ham değer -> radyan (negatif: ham(-)=sol)
        self.declare_parameter('steer_feedback_offset', 2.0)     # düz gidişte okunan ham değer
        self.declare_parameter('speed_timeout', 0.5)         # sn; hız mesajı bundan eskiyse v=0
        # rev7: varsayılan gyro entegre. Mutlak AHRS yaw pist ölçümünde 10x kötü
        # çıktı (manyetometre çelik bariyerden bozuluyor) -- bkz. rev7 notu.
        self.declare_parameter('use_imu_yaw', True)            # true: yaw_rate IMU gyro'dan (entegre) -- VARSAYILAN
        self.declare_parameter('use_imu_orientation', False)   # true: yaw XSENS AHRS mutlak orientation'dan (manyetik ortam temizse)
        self.declare_parameter('imu_topic', '/imu/data')      # XSENS sürücü çıktısı (araçta doğrula)
        self.declare_parameter('imu_timeout', 0.3)            # sn; IMU bundan eskiyse tan(steer)'e düş
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('publish_tf', True)
        self.declare_parameter('rate_hz', 50.0)

        gp = lambda name: self.get_parameter(name).get_parameter_value()
        self.speed_topic = gp('speed_topic').string_value
        self.steering_topic = gp('steering_topic').string_value
        self.gear_topic = gp('gear_topic').string_value
        self.odom_topic = gp('odom_topic').string_value
        self.wheelbase = gp('wheelbase').double_value
        self.speed_scale = gp('speed_scale').double_value
        self.steer_gain = gp('steer_feedback_gain').double_value
        self.steer_offset = gp('steer_feedback_offset').double_value
        self.speed_timeout = gp('speed_timeout').double_value
        self.use_imu_yaw = gp('use_imu_yaw').bool_value
        self.use_imu_orientation = gp('use_imu_orientation').bool_value
        self.imu_topic = gp('imu_topic').string_value
        self.imu_timeout = gp('imu_timeout').double_value
        self.odom_frame = gp('odom_frame').string_value
        self.base_frame = gp('base_frame').string_value
        self.publish_tf = gp('publish_tf').bool_value
        rate_hz = gp('rate_hz').double_value

        # Dead-reckoning durumu (her başlatmada (0,0,0)'dan başlar)
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.speed_ms = 0.0
        self.steer_rad = 0.0
        self.gear = GEAR_NEUTRAL
        self._last_speed_time = None   # None: henüz hiç hız mesajı gelmedi
        self._stale_warned = False
        self.imu_yaw_rate = 0.0
        self.imu_yaw_abs = None        # mutlak yaw (rad, offset düşülmüş); None: henüz orientation gelmedi
        self.imu_yaw_offset = None     # ilk orientation örneği (referans sıfır -> odom 0'dan başlar)
        self._last_imu_time = None
        self._imu_fallback_warned = False

        self.sub_speed = self.create_subscription(
            Fbvehiclespeed, self.speed_topic, self._speed_cb, 10)
        self.sub_steer = self.create_subscription(
            Feedbacksteeringangle, self.steering_topic, self._steer_cb, 10)
        self.sub_gear = self.create_subscription(
            Fbmotordriver, self.gear_topic, self._gear_cb, 10)

        self.sub_imu = None
        if self.use_imu_yaw or self.use_imu_orientation:
            self.sub_imu = self.create_subscription(
                Imu, self.imu_topic, self._imu_cb, 50)

        self.pub_odom = self.create_publisher(Odometry, self.odom_topic, 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self._last_time = self.get_clock().now()
        self.timer = self.create_timer(1.0 / rate_hz, self._integrate)

        self.get_logger().info(
            f"CAN odom node (TASLAK rev5) started: wheelbase={self.wheelbase}m, "
            f"speed_topic={self.speed_topic}, speed_scale={self.speed_scale}, "
            f"steer_gain={self.steer_gain} steer_offset={self.steer_offset} (kalibre 2026-07-13), "
            f"{rate_hz}Hz, publish_tf={self.publish_tf}, "
            f"use_imu_yaw={self.use_imu_yaw} use_imu_orientation={self.use_imu_orientation}" +
            (f" (topic: {self.imu_topic})" if (self.use_imu_yaw or self.use_imu_orientation) else ""))

    def _speed_cb(self, msg):
        # uint8 km/h alanı: _ms alanından daha ince çözünürlük (rev5 notu).
        self.speed_ms = float(msg.fb_reelvehiclespeed_kmh) * self.speed_scale
        self._last_speed_time = self.get_clock().now()
        if self._stale_warned:
            self.get_logger().info('Hız geri beslemesi tekrar geliyor.')
            self._stale_warned = False

    def _steer_cb(self, msg):
        self.steer_rad = (float(msg.feedbacksteeringangle) - self.steer_offset) * self.steer_gain

    def _imu_cb(self, msg):
        self.imu_yaw_rate = float(msg.angular_velocity.z)
        # MUTLAK yaw: XSENS AHRS orientation quaternion'undan (drift'siz).
        # İlk örnek referans yakalanır -> odom (0,0,0)'dan başlar.
        q = msg.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                         1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        if self.imu_yaw_offset is None:
            self.imu_yaw_offset = yaw
        self.imu_yaw_abs = math.atan2(math.sin(yaw - self.imu_yaw_offset),
                                      math.cos(yaw - self.imu_yaw_offset))
        self._last_imu_time = self.get_clock().now()
        # Kurtarma info log'u _integrate içindeki mod dalında verilir
        # (mutlak mı gyro mu ayrımını yapabilmek için).

    def _gear_cb(self, msg):
        self.gear = int(msg.gear_status_from_motor)

    def _integrate(self):
        now = self.get_clock().now()
        dt = (now - self._last_time).nanoseconds * 1e-9
        self._last_time = now
        if dt <= 0.0:
            return

        # Stale-data koruması: hız mesajı hiç gelmediyse ya da timeout'u
        # aştıysa entegrasyona 0 hızla devam et (eski değeri sürükleme).
        speed_ok = (
            self._last_speed_time is not None and
            (now - self._last_speed_time).nanoseconds * 1e-9 <= self.speed_timeout
        )
        if not speed_ok:
            if self._last_speed_time is not None and not self._stale_warned:
                self.get_logger().warn(
                    f'Hız geri beslemesi {self.speed_timeout}s içinde gelmedi '
                    f'(CAN köprüsü çalışıyor mu?) -> v=0 kabul ediliyor.')
                self._stale_warned = True
            v = 0.0
        elif self.gear == GEAR_REVERSE:
            v = -self.speed_ms
        elif self.gear in (GEAR_DRIVE, GEAR_NEUTRAL):
            # NEUTRAL: coasting/yuvarlanma da harekettir; hız feedback'i
            # neyse onu kullan (yön bilgisi yok -> ileri varsayılır).
            v = self.speed_ms
        else:
            # Bilinmeyen vites değeri: güvenli taraf, hareket yok say.
            v = 0.0

        # --- Yaw kaynağı (öncelik: mutlak orientation > gyro entegre > kinematik) ---
        imu_fresh = (
            self._last_imu_time is not None and
            (now - self._last_imu_time).nanoseconds * 1e-9 <= self.imu_timeout
        )

        # Konum entegrasyonu her modda mevcut yaw ile (küçük dt -> ihmal edilebilir hata)
        self.x += v * math.cos(self.yaw) * dt
        self.y += v * math.sin(self.yaw) * dt

        if self.use_imu_orientation and imu_fresh and self.imu_yaw_abs is not None:
            # MUTLAK yaw: entegrasyon YOK -> gyro bias birikmez (drift'siz).
            self.yaw = self.imu_yaw_abs
            yaw_rate = self.imu_yaw_rate           # twist raporu için (bilgi amaçlı)
            if self._imu_fallback_warned:
                self.get_logger().info('IMU verisi tekrar geliyor, mutlak yaw aktif.')
                self._imu_fallback_warned = False
        elif self.use_imu_yaw and imu_fresh:
            # Gyro hızı entegrasyonu (teker kaymasından etkilenmez ama bias birikir).
            yaw_rate = self.imu_yaw_rate
            self.yaw = math.atan2(
                math.sin(self.yaw + yaw_rate * dt),
                math.cos(self.yaw + yaw_rate * dt))
            if self._imu_fallback_warned:
                self.get_logger().info('IMU verisi tekrar geliyor, gyro yaw aktif.')
                self._imu_fallback_warned = False
        else:
            # IMU yok/bayat ya da IMU modları kapalı -> tan(steer) kinematik model.
            if (self.use_imu_orientation or self.use_imu_yaw) and not self._imu_fallback_warned:
                self.get_logger().warn(
                    f'IMU verisi yok/bayat ({self.imu_topic}) -> '
                    f'tan(steer) kinematik modeline düşüldü.')
                self._imu_fallback_warned = True
            yaw_rate = (v / self.wheelbase) * math.tan(self.steer_rad)
            self.yaw = math.atan2(
                math.sin(self.yaw + yaw_rate * dt),
                math.cos(self.yaw + yaw_rate * dt))

        qz = math.sin(self.yaw / 2.0)
        qw = math.cos(self.yaw / 2.0)

        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = v
        odom.twist.twist.angular.z = yaw_rate
        self.pub_odom.publish(odom)

        if self.publish_tf:
            t = TransformStamped()
            t.header.stamp = now.to_msg()
            t.header.frame_id = self.odom_frame
            t.child_frame_id = self.base_frame
            t.transform.translation.x = self.x
            t.transform.translation.y = self.y
            t.transform.rotation.z = qz
            t.transform.rotation.w = qw
            self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = CanOdomNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # Ctrl+C'de launch/rclpy shutdown'ı zaten başlatmış olabilir; ikinci
        # çağrı RCLError fırlatıp "process has died, exit code 1" gösteriyordu
        # (6. oturum, output12) -- kozmetik ama log kirletiyor.
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
