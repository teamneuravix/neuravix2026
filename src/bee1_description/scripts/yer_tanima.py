#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YER TANIMA GOZETMENI - AMCL'i aliasing'den LiDAR ile kurtarir
=============================================================
AMCL `map->odom`'u surmeye DEVAM eder; bu dugum ona karismaz. Yalnizca izler:
her taramanin Scan Context tanimlayicisini harita bag'inden kurulmus bir
veritabaninda arar, guvenilir bir eslesme bulursa AMCL'in soyledigi yerle
karsilastirir, uzun sure ayrisirlarsa `/initialpose` ile geri cagirir.

NEDEN (2026-08-17 olcumu, pist_19_3tem veritabani -> pist_17tem_2 sorgu,
FARKLI GUNLERDE cekilmis iki bag, GNSS gercek referansi):
  mevcut 2B /scan ile yer tanima : top-1 %27 dogru, medyan hata 13.6 m
  Scan Context (tam 3B bulut)    : top-1 %67 dogru, medyan hata  2.4 m
  + oran testi (esik 0.90)       : kapsama %53, KESINLIK %100, hata 1.6 m
  aliasing kontrolu: sorgular 10-20 m ayrildiginda veritabaninda ayni yeri
  gosterme orani %0.0; 20 m+ ayrikken %0.02 (144134'te 35). Esleme birebir.

  13.6 m rakamina dikkat: AMCL'de GNSS ile olculen sapma 12.6 m idi. Ayni
  buyukluk. Yani AMCL bozuk degil -- ona verilen gozlem %27 dogrulukta ve
  filtre tam olarak bunu uretiyor. Cozum filtreyi ayarlamak degil, gozleme
  atilan bilgiyi geri koymak.

NEDEN GNSS GOZETMENI DEGIL (2026-08-13'te denendi, basarisiz):
  GNSS gercek dunyada yasiyor, harita ise kendi burulmus cercevesinde
  (~12 m). Duzeltilmek istenen aliasing hatasi 20-26 m; iki dagilim ust uste
  binince hicbir esik ikisini ayiramadi. Yer tanima TAMAMEN harita
  cercevesinde calisir -- veritabani pozlari haritayi ureten kosudan gelir,
  burulma iki tarafta da ayni oldugu icin SADELESIR. Ayrica GNSS yon vermez;
  Scan Context'in sutun kaydirmasi verir (olculdu: medyan yaw hatasi 7 derece,
  %94'u 30 derece icinde) -- 180 derecelik belirsizligi kiran sey budur.

VARSAYILAN KAPALI degil ama launch'ta `use_yer_tanima` varsayilani false;
yani hicbir mevcut kosu bu dugumu baslatmaz.
"""

import math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from sensor_msgs.msg import PointCloud2
from geometry_msgs.msg import PoseWithCovarianceStamped
import sensor_msgs_py.point_cloud2 as pc2
import tf2_ros


class YerTanima(Node):
    def __init__(self):
        super().__init__('yer_tanima')

        self.declare_parameter('db_path', '')
        self.declare_parameter('lidar_topic', '/velodyne_points')
        # Her taramayi islemek gereksiz; ~2 Hz yeterli (arac saniyede ~1 m).
        self.declare_parameter('her_n_tarama', 5)
        # Oran testi: en iyi eslesme, BASKA BIR YERDEKI en iyiden bu kadar
        # kucuk olmali. Olculdu: 0.90'da kesinlik %100 / kapsama %53,
        # 0.95'te kesinlik %92.5. Kesinlik kapsamadan onemli -- yanlis
        # tohumlama AMCL'i duzeltmek yerine bozar.
        self.declare_parameter('oran_esigi', 0.90)
        # Oran testinde "baska yer" sayilmak icin gereken mesafe.
        self.declare_parameter('rakip_uzakligi_m', 15.0)
        # AMCL ile ayrisma bu kadari asarsa mudahale dusunulur. Yer tanima
        # kendi hatasi 1.6 m, AMCL'in mesru hatasi ~0.5 m -> 4 m ikisiyle de
        # aciklanamaz.
        self.declare_parameter('esik_m', 4.0)
        self.declare_parameter('sustain_s', 1.5)
        self.declare_parameter('min_aralik_s', 4.0)
        # Ilk guvenilir eslesmede kosulsuz tohumla: AMCL'in elle girilen
        # baslangic pozu yanlissa bastan duzelir (RViz'den tiklamaya gerek yok).
        self.declare_parameter('acilista_tohumla', True)
        self.declare_parameter('seed_std_xy', 1.5)
        self.declare_parameter('seed_std_yaw_deg', 15.0)
        # false: yalnizca olcer ve raporlar, MUDAHALE ETMEZ.
        self.declare_parameter('enabled', True)

        g = lambda n: self.get_parameter(n).value
        path = g('db_path')
        if not path:
            self.get_logger().error('db_path verilmedi -- dugum is yapmayacak')
            raise SystemExit(1)

        z = np.load(path)
        self.NR, self.NS = int(z['NR']), int(z['NS'])
        self.RMAX, self.RMIN = float(z['RMAX']), float(z['RMIN'])
        self.ZG_PCT = float(z['ZG_PCT'])
        self.POZ = z['POZ']
        D = z['D'].astype(np.float64)
        # Sutun-normalize (her sektor kendi icinde) -- cevrimdisi olcumle AYNI.
        Dn = D / (np.linalg.norm(D, axis=1, keepdims=True) + 1e-9)
        self.Dflat = np.ascontiguousarray(Dn.reshape(len(D), -1))
        self.n_db = len(D)

        self.oran = g('oran_esigi')
        self.rakip = g('rakip_uzakligi_m')
        self.esik = g('esik_m')
        self.sustain = g('sustain_s')
        self.min_int = g('min_aralik_s')
        self.bootstrap = g('acilista_tohumla')
        self.sxy = g('seed_std_xy')
        self.syaw = math.radians(g('seed_std_yaw_deg'))
        self.enabled = g('enabled')
        self.her_n = max(1, int(g('her_n_tarama')))

        self.buf = tf2_ros.Buffer(cache_time=Duration(seconds=10))
        self.lis = tf2_ros.TransformListener(self.buf, self)
        self.pub = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        # RViz'de gormek icin: yer tanimanin soyledigi yer
        self.pub_dbg = self.create_publisher(PoseWithCovarianceStamped,
                                             '~/aday_poz', 10)
        self.create_subscription(PointCloud2, g('lidar_topic'), self.on_scan, 5)

        self.k = 0
        self.n_kabul = 0
        self.n_tohum = 0
        self.bad_since = None
        self.last_seed = None
        self.dsum = 0.0
        self.seeded_once = False

        self.get_logger().info(
            f'yer_tanima: {self.n_db} kayit ({self.NR}x{self.NS}, rmax {self.RMAX:.0f} m) '
            f'| oran {self.oran} esik {self.esik} m | '
            f'{"AKTIF" if self.enabled else "SADECE IZLIYOR"}')

    # ---- tanimlayici: yer_tanima_db.py ile BIREBIR AYNI olmali -----------
    def scan_context(self, x, y, z):
        r = np.hypot(x, y)
        ang = np.arctan2(y, x)
        hal = (r > 5) & (r < 25)
        zg = np.percentile(z[hal], self.ZG_PCT) if hal.sum() > 100 else -1.35
        h = z - zg
        g = np.full((self.NR, self.NS), -1e3)
        s = (r >= self.RMIN) & (r <= self.RMAX)
        if s.sum() < 100:
            return None
        ri = (r[s] / self.RMAX * self.NR).astype(np.int32).clip(0, self.NR - 1)
        si = ((ang[s] + np.pi) / (2 * np.pi) * self.NS).astype(np.int32).clip(0, self.NS - 1)
        np.maximum.at(g, (ri, si), h[s])
        g[g < -1e2] = 0.0
        return g

    def ara(self, Q):
        """Veritabaninda ara. Doner: (indis, kaydirma, oran) ya da None.

        Kaydirmayi VERITABANINA degil SORGUYA uygularız: 60 kaydirma tek bir
        (60 x 1200) matris olur ve arama TEK matmul'e iner (~15 ms).
        Isaret kuralı cevrimdisi olcumle ayni kalir:
            roll(D, sh) ~ Q   <=>   D ~ roll(Q, -sh)
        """
        Qn = Q / (np.linalg.norm(Q, axis=0, keepdims=True) + 1e-9)
        S = np.stack([np.roll(Qn, -sh, axis=1).ravel() for sh in range(self.NS)])
        sim = self.Dflat @ S.T / self.NS            # (n_db, NS)
        d = 1.0 - sim
        sh_best = np.argmin(d, axis=1)
        d_best = d[np.arange(self.n_db), sh_best]

        j1 = int(np.argmin(d_best))
        d1 = float(d_best[j1])
        uzak = np.linalg.norm(self.POZ[:, :2] - self.POZ[j1, :2], axis=1) > self.rakip
        if not uzak.any():
            return None
        d2 = float(d_best[uzak].min())
        oran = d1 / max(d2, 1e-12)
        if oran >= self.oran:
            return None
        return j1, int(sh_best[j1]), oran

    def on_scan(self, msg):
        self.k += 1
        if self.k % self.her_n:
            return
        a = pc2.read_points(msg, field_names=('x', 'y', 'z'), skip_nans=True)
        Q = self.scan_context(np.asarray(a['x'], np.float64),
                              np.asarray(a['y'], np.float64),
                              np.asarray(a['z'], np.float64))
        if Q is None:
            return
        hit = self.ara(Q)
        if hit is None:
            return
        j, sh, oran = hit
        self.n_kabul += 1

        # yaw: sutun kaydirmasindan. Isaret cevrimdisi dogrulandi
        # (medyan hata 7 derece, %94'u 30 derece icinde).
        x, y, yaw_db = self.POZ[j]
        yaw = yaw_db - sh * (2 * math.pi / self.NS)

        dbg = self.poz_msg(msg.header.stamp, x, y, yaw)
        self.pub_dbg.publish(dbg)

        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        # ⚠️ Tohumlamanin ZAMAN DAMGASI, taramanin damgasi OLAMAZ.
        # AMCL /initialpose'u alinca o damgada base_link->odom donusumunu arar;
        # tarama damgasi TF tamponunun kapsadigi araligin disinda kalinca mesaji
        # SESSIZCE ATAR ("Failed to transform initial pose in time").
        # 2026-08-18'de olculdu: tohumlamalarin %50-81'i boyle kayboluyordu --
        # yani gozetmen calisiyor gorunuyor ama duzeltmelerin cogu AMCL'e hic
        # ulasmiyordu. Cozum: TF'ten DONEN damgayi kullanmak; o damganin
        # tamponda oldugu tanim geregi kesindir.
        seed_stamp = msg.header.stamp
        try:
            tr = self.buf.lookup_transform('map', 'base_link', rclpy.time.Time())
            ax = tr.transform.translation.x; ay = tr.transform.translation.y
            dist = math.hypot(x - ax, y - ay)
            seed_stamp = tr.header.stamp
        except Exception:
            dist = float('inf')                     # AMCL henuz poz vermiyor

        if math.isfinite(dist):
            self.dsum += dist
            if self.n_kabul % 40 == 0:
                self.get_logger().info(
                    f'eslesme #{self.n_kabul} oran {oran:.2f} | AMCL ile fark {dist:.1f} m '
                    f'(ortalama {self.dsum/self.n_kabul:.1f} m) | tohumlama {self.n_tohum}')

        acilis = self.bootstrap and not self.seeded_once
        if not acilis:
            if dist < self.esik:
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
            self.get_logger().warn(f'[izleme] {dist:.1f} m ayrisma -- mudahale KAPALI')
            self.bad_since = None
            return

        self.pub.publish(self.poz_msg(seed_stamp, x, y, yaw))
        self.n_tohum += 1
        self.last_seed = t
        self.bad_since = None
        self.seeded_once = True
        self.get_logger().warn(
            f'TOHUMLAMA #{self.n_tohum}{" (acilis)" if acilis else ""}: '
            f'kayit {j}, oran {oran:.2f}, AMCL ile fark '
            f'{dist:.1f} m -> ({x:.1f}, {y:.1f}) yaw {math.degrees(yaw):+.0f}')

    def poz_msg(self, stamp, x, y, yaw):
        m = PoseWithCovarianceStamped()
        m.header.stamp = stamp
        m.header.frame_id = 'map'
        m.pose.pose.position.x = float(x)
        m.pose.pose.position.y = float(y)
        m.pose.pose.orientation.z = math.sin(yaw / 2.0)
        m.pose.pose.orientation.w = math.cos(yaw / 2.0)
        c = [0.0] * 36
        c[0] = c[7] = self.sxy ** 2
        c[35] = self.syaw ** 2
        m.pose.covariance = c
        return m


def main():
    rclpy.init()
    try:
        n = YerTanima()
    except SystemExit:
        rclpy.shutdown(); return
    try:
        rclpy.spin(n)
    except KeyboardInterrupt:
        pass
    finally:
        n.get_logger().info(
            f'ozet: {n.n_kabul} kabul edilen eslesme, {n.n_tohum} tohumlama, '
            f'ortalama AMCL farki {(n.dsum/max(n.n_kabul,1)):.1f} m')
        rclpy.shutdown()


if __name__ == '__main__':
    main()
