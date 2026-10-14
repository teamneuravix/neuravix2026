#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNSS GÖZETMENİ - AMCL'i aliasing'den kurtarır (mimari (a))
==========================================================
AMCL `map->odom`'u sürmeye DEVAM eder; bu node ona karışmaz. Yalnızca izler:
GNSS'in söylediği yer ile AMCL'in söylediği yer uzun süre ayrışırsa, AMCL'i
`/initialpose` ile GNSS'in gösterdiği yere geri çağırır.

NEDEN (2026-08-12/13 ölçümü, pist_C_19_3tem haritası + pist_17tem_2 bag'i):
  Başarısızlık modu 1-2 m'lik drift DEĞİL, 10-100 m'lik ALIASING: pistin bir
  kenarı ile karşı kenarı birbirine benziyor, parçacık bulutu yanlış olana
  oturuyor. map->odom düzeltmesi 134 m ve 176 dereceye kadar çıktı.
  Ölçüldü: "kilitli" (tarama haritaya oturuyor) sayılan pozların yalnızca %8'i
  gerçekten doğru yerdeymiş -- kalan %92 ikna edici biçimde YANLIŞ. Tarama iki
  yeri de eşit iyi açıklıyor; hangisinin doğru olduğunu söyleyecek BAĞIMSIZ bir
  bilgi gerekiyor. 2 metrelik GNSS bunun için fazlasıyla yeterli.

NEDEN navsat_transform_node DEĞİL:
  O node bir EKF'i beslemek için tasarlanmış. Bize füzyon değil, yalnızca
  "GNSS nerede diyor" karşılaştırması lazım. Datum zaten ölçüldüğü için
  dönüşümü burada iki satırda yapmak daha az parça, daha az kırılma noktası.

DATUM (bu haritaya ÖZEL, harita değişirse yeniden ölçülmeli):
  pist_C_19_3tem için GNSS izi, AMCL'in doğru kilitlendiği pozlara RANSAC ile
  hizalanarak bulundu; iç nokta artığı 1.99 m (GNSS'in kendi doğruluğu kadar).

YAW BELİRSİZLİĞİ:
  Aliasing çoğu zaman 180 derecelik bir hata. GNSS tek başına yön vermez, ama
  ardışık fix'lerden gidiş yönü (course over ground) çıkarılabilir. Araç yeterince
  yol aldıysa bu yön, map çerçevesine çevrilip yeniden tohumlamada kullanılır --
  180 derece belirsizliğini kıran şey budur. Araç yavaşsa yön güvenilmez, o
  durumda AMCL'in kendi yaw'ı korunur (konum yine de düzeltilir).
"""

import math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import PoseWithCovarianceStamped
import tf2_ros

R_EARTH = 6378137.0


class GnssSupervisor(Node):
    def __init__(self):
        super().__init__('gnss_supervisor')

        # --- Datum: haritanın coğrafi referansı (analiz/datum.npz'den) ---
        self.declare_parameter('datum_lat', 40.79041010)
        self.declare_parameter('datum_lon', 29.50912636)
        # map +x ekseninin ENU doğusuna göre açısı
        self.declare_parameter('datum_yaw_deg', -149.20)

        # --- Tetikleme eşikleri ---
        # GNSS doğruluğu ~2 m, AMCL'in meşru hatası ~0.5 m. 5 m'lik bir ayrışma
        # ölçüm gürültüsüyle açıklanamaz; neredeyse kesin aliasing.
        self.declare_parameter('threshold_m', 5.0)
        # Tek bir kötü fix yüzünden müdahale etmemek için ayrışma SÜRMELİ.
        self.declare_parameter('sustain_s', 2.0)
        # Art arda tohumlama AMCL'e toparlanma fırsatı vermez.
        self.declare_parameter('min_interval_s', 5.0)
        # Gidiş yönü bu hızın altında güvenilmez (2 m gürültü / yavaş araç).
        self.declare_parameter('min_speed_for_heading', 0.4)
        self.declare_parameter('gnss_topic', '/gnss')
        # Yeniden tohumlamada AMCL'e bildirilen belirsizlik. GNSS'in gerçek
        # doğruluğu; 0.34 m'lik alıcı-hassasiyeti DEĞİL. Fazla küçük verilirse
        # AMCL parçacıkları dar toplar ve LiDAR'ın kazandığı inceliği kaybeder.
        self.declare_parameter('seed_std_xy', 2.0)
        self.declare_parameter('seed_std_yaw_deg', 25.0)
        # false: yalnızca ölçer/raporlar, MÜDAHALE ETMEZ. Önce böyle koşup
        # eşiklerin doğru olduğunu görmek için.
        self.declare_parameter('enabled', True)

        # DENEY: gozetmeni belirli bir zaman araliginda SUSTUR (tunel benzetimi).
        # Olcum icin: AMCL desteksiz kalinca ne kadar surede ne kadar kayiyor?
        # Sifir birakilirsa kor pencere yok. Zaman, ilk GNSS mesajindan itibaren
        # gecen saniye (bag basi).
        self.declare_parameter('kor_baslangic_s', 0.0)
        self.declare_parameter('kor_sure_s', 0.0)

        g = lambda n: self.get_parameter(n).value
        self.lat0, self.lon0 = g('datum_lat'), g('datum_lon')
        yaw = math.radians(g('datum_yaw_deg'))
        self.R = np.array([[math.cos(yaw), -math.sin(yaw)],
                           [math.sin(yaw),  math.cos(yaw)]])
        self.datum_yaw = yaw
        self.th = g('threshold_m')
        self.sustain = g('sustain_s')
        self.min_int = g('min_interval_s')
        self.min_spd = g('min_speed_for_heading')
        self.enabled = g('enabled')
        self.sxy = g('seed_std_xy')
        self.kor_bas = g('kor_baslangic_s')
        self.kor_sure = g('kor_sure_s')
        self.syaw = math.radians(g('seed_std_yaw_deg'))

        self.buf = tf2_ros.Buffer(cache_time=Duration(seconds=10))
        self.lis = tf2_ros.TransformListener(self.buf, self)
        self.pub = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        self.create_subscription(NavSatFix, g('gnss_topic'), self.on_fix, 10)

        self.prev = None          # (t, x, y) map frame'de onceki GNSS
        self.t0 = None            # ilk GNSS mesajinin zamani (kor pencere icin)
        self.kor_maks = 0.0       # kor pencerede goruleni en buyuk ayrisma
        self.kor_sayac = 0
        self.bad_since = None
        self.last_seed = None
        self.n_seed = 0
        self.n_fix = 0
        self.dsum = 0.0

        self.get_logger().info(
            f"gnss_supervisor: datum ({self.lat0:.7f}, {self.lon0:.7f}) "
            f"yaw {math.degrees(yaw):+.2f}° | esik {self.th} m / {self.sustain} s | "
            f"{'AKTIF' if self.enabled else 'SADECE IZLIYOR'}")

    def to_map(self, lat, lon):
        """WGS84 -> yerel ENU -> map frame.

        ⚠️ DONME YONU: burada `R.T @ p` var, `R @ p` DEGIL.
        Datum, GNSS izini harita pozlarina oturtan uyumdan cikarildi ve o uyum
        numpy'de SATIR-vektor konvansiyonuyla yazilmisti (P @ R). Sutun-vektor
        karsiligi R.T @ p'dir. Ilk yazimda `R @ p` yazilmisti; bu, donmeyi TERS
        uyguladigi icin GNSS'i haritanin disina koyuyordu -- olculdu: dogru
        konvansiyonda izin %100'u harita sinirlari icinde, ters olaninda %25.
        Gozetmen de araci surekli haritanin disina tohumluyordu (2026-08-13).
        """
        e = math.radians(lon - self.lon0) * R_EARTH * math.cos(math.radians(self.lat0))
        n = math.radians(lat - self.lat0) * R_EARTH
        return self.R.T @ np.array([e, n])

    def on_fix(self, msg):
        if not math.isfinite(msg.latitude) or abs(msg.latitude) < 1e-3:
            return
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        p = self.to_map(msg.latitude, msg.longitude)

        # AMCL'in soyledigi yer
        try:
            tr = self.buf.lookup_transform('map', 'base_link', rclpy.time.Time())
        except Exception:
            return
        # Tohumlamanin damgasi icin TF'ten DONEN damgayi kullaniyoruz (asagida
        # m.header.stamp = tr.header.stamp). GNSS mesajinin kendi damgasi TF
        # tamponunun az disinda kalabiliyor ve AMCL
        # "Failed to transform initial pose in time" uyarisi basiyor.
        # ⚠️ DUZELTME (2026-08-19): o uyari tohumlamayi REDDETMEZ -- nav2_amcl
        # handleInitialPose icinde odom duzeltmesini birim matris alip devam
        # eder, hemen ardindan "Setting pose" basar. 0.66 m/s'de kacan duzeltme
        # ~1 cm. Yani bu satir dogru ama hayati degil; uyariya bakip "gozetmen
        # calismiyor" sonucuna VARMA.
        a = np.array([tr.transform.translation.x, tr.transform.translation.y])

        d = float(np.linalg.norm(p - a))
        self.n_fix += 1
        self.dsum += d
        if self.t0 is None:
            self.t0 = t
        kor = (self.kor_sure > 0.0
               and self.kor_bas <= t - self.t0 < self.kor_bas + self.kor_sure)
        if self.n_fix % 100 == 0:
            self.get_logger().info(
                f"GNSS-AMCL ayrisma: anlik {d:.1f} m, ortalama {self.dsum/self.n_fix:.1f} m, "
                f"tohumlama {self.n_seed}")

        # gidis yonu (course over ground) -- 180 derece belirsizligini kirar
        head = None
        if self.prev is not None:
            dt = t - self.prev[0]
            step = p - self.prev[1]
            if dt > 1e-3 and np.linalg.norm(step) / dt > self.min_spd:
                head = math.atan2(step[1], step[0])   # zaten map frame'de
        self.prev = (t, p)

        if kor:
            # KOR PENCERE: olcuyoruz ama tohumlamiyoruz.
            self.kor_maks = max(self.kor_maks, d)
            self.kor_sayac += 1
            if self.kor_sayac % 8 == 0:
                self.get_logger().warn(
                    f"[KOR] t+{t - self.t0:.0f} s (kor icinde {t - self.t0 - self.kor_bas:.0f} s): "
                    f"ayrisma {d:.2f} m, kor pencerede maks {self.kor_maks:.2f} m")
            self.bad_since = None
            return
        if self.kor_sure > 0.0 and t - self.t0 >= self.kor_bas + self.kor_sure \
                and self.kor_sayac > 0:
            self.get_logger().warn(
                f"[KOR BITTI] {self.kor_sure:.0f} s desteksiz: MAKS AYRISMA {self.kor_maks:.2f} m, "
                f"cikista {d:.2f} m")
            self.kor_sayac = 0

        if d < self.th:
            self.bad_since = None
            return
        if self.bad_since is None:
            self.bad_since = t
            return
        if t - self.bad_since < self.sustain:
            return
        if self.last_seed is not None and t - self.last_seed < self.min_int:
            return
        if not self.enabled:
            self.get_logger().warn(f"[izleme] {d:.1f} m ayrisma surdu -- mudahale KAPALI")
            self.bad_since = None
            return

        # yaw: gidis yonu varsa onu kullan, yoksa AMCL'in kendi yaw'ini koru
        q = tr.transform.rotation
        cur_yaw = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
        yaw = head if head is not None else cur_yaw
        src = 'GNSS yonu' if head is not None else 'AMCL yaw korundu'

        m = PoseWithCovarianceStamped()
        m.header.stamp = tr.header.stamp
        m.header.frame_id = 'map'
        m.pose.pose.position.x, m.pose.pose.position.y = float(p[0]), float(p[1])
        m.pose.pose.orientation.z = math.sin(yaw / 2.0)
        m.pose.pose.orientation.w = math.cos(yaw / 2.0)
        c = [0.0] * 36
        c[0] = c[7] = self.sxy ** 2
        c[35] = self.syaw ** 2
        m.pose.covariance = c
        self.pub.publish(m)

        self.n_seed += 1
        self.last_seed = t
        self.bad_since = None
        self.get_logger().warn(
            f"YENIDEN TOHUMLAMA #{self.n_seed}: {d:.1f} m ayrisma {self.sustain} s surdu "
            f"-> ({p[0]:.1f}, {p[1]:.1f}) yaw {math.degrees(yaw):+.0f}° [{src}]")


def main():
    rclpy.init()
    n = GnssSupervisor()
    try:
        rclpy.spin(n)
    except KeyboardInterrupt:
        pass
    finally:
        n.get_logger().info(
            f"ozet: {n.n_fix} fix, ortalama ayrisma "
            f"{(n.dsum/n.n_fix if n.n_fix else 0):.1f} m, {n.n_seed} tohumlama")
        rclpy.shutdown()


if __name__ == '__main__':
    main()
