#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YER TANIMA VERITABANI KURUCU (cevrimdisi)
=========================================
Harita bag'inden Scan Context tanimlayici veritabani uretir. Her kayit:
    tanimlayici (20 halka x 60 sektor) + HARITA CERCEVESINDEKI poz + yay uzunlugu

NEDEN BU IS GORUYOR (2026-08-17 olcumu, pist_19_3tem -> pist_17tem_2 capraz oturum):
  Sorgu taramalari GNSS'e gore ayni yerdeyken, veritabaninda da ayni kaydi
  buluyor: yay farki medyan 0.5 m (rastgele eslesmede 86 m).
  Sorgu 10-20 m ayrildiginda ayni kaydi gosterme orani %0.0,
  20 m+ ayrildiginda %0.02 -> ALIASING YOK, esleme birebir.
  Oran testi esigi 0.90'da: kapsama %53, KESINLIK %100, konum hatasi 1.6 m.

  Kiyas: mevcut 2B /scan boru hattiyla ayni test top-1 %27 dogru, hata 13.6 m.
  (Bu 13.6 m, AMCL'de GNSS ile olculen 12.6 m sapmayla ayni buyukluk -- yani
  AMCL'in hatasi filtrenin degil, ona verilen gozlemin bilgi icerigidir.)

NEDEN GNSS DEGIL:
  Veritabani pozlari haritayla AYNI SLAM kosusundan gelir, yani haritanin
  kendi (burulmus) cercevesindedir. Burulma her iki tarafta da ayni oldugu
  icin SADELESIR. GNSS ise gercek dunyada yasiyordu; harita ile arasindaki
  ~12 m burulma, duzeltilmek istenen 20-26 m'lik hatayla ayni mertebedeydi ve
  hicbir esik ikisini ayiramiyordu. Yer tanima tamamen harita cercevesinde
  calistigi icin bu sorun ortadan kalkar.

KULLANIM:
  python3 yer_tanima_db.py <bag_dizini> <poz.csv> <cikti.npz> [stride]

  poz.csv: pose_logger.py ciktisi (t,x,y,yaw), HARITAYI ureten kosudan.
  ⚠️ Poz dosyasi haritayi ureten kosuyla AYNI kosudan olmali; farkli kosudan
  gelirse veritabani ile harita ayni cerceveyi paylasmaz.
"""

import sys, sqlite3, math
import numpy as np
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2

# --- TANIMLAYICI PARAMETRELERI ---------------------------------------------
# ⚠️ Bu degerler yer_tanima.py (cevrimici dugum) ile AYNI olmak ZORUNDA.
# npz'ye yazilirlar ve dugum yuklerken karsilastirir; uyusmazsa hata verir.
NR, NS = 20, 60          # halka x sektor
RMAX = 40.0              # haritayla ayni menzil (max_laser_range 40)
RMIN = 0.5
ZG_PCT = 3.0             # zemin yuksekligi: 5-25 m halkasinin bu yuzdeligi


def zemin_yuksekligi(r, z):
    """Zemini her taramada YENIDEN kestir. Sabit bir yukseklik kullanmak yanlis:
    montaj yuksekligi bag'den bag'e 1.29-1.41 m olculdu ve arac yunusluyor."""
    hal = (r > 5) & (r < 25)
    return np.percentile(z[hal], ZG_PCT) if hal.sum() > 100 else -1.35


def scan_context(x, y, z):
    """Scan Context: kutup izgarasi, hucre degeri = zemine gore MAKS yukseklik.
    Tum 3B bulutu kullanir -- 2B /scan'in attigi dikey yapiyi korur."""
    r = np.hypot(x, y)
    ang = np.arctan2(y, x)
    h = z - zemin_yuksekligi(r, z)
    g = np.full((NR, NS), -1e3)
    s = (r >= RMIN) & (r <= RMAX)
    ri = (r[s] / RMAX * NR).astype(np.int32).clip(0, NR - 1)
    si = ((ang[s] + np.pi) / (2 * np.pi) * NS).astype(np.int32).clip(0, NS - 1)
    np.maximum.at(g, (ri, si), h[s])
    g[g < -1e2] = 0.0
    return g


def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(1)
    bag, pozcsv, out = sys.argv[1], sys.argv[2], sys.argv[3]
    stride = int(sys.argv[4]) if len(sys.argv) > 4 else 4

    import glob, os
    db3 = sorted(glob.glob(os.path.join(bag, '*.db3')))
    if not db3:
        print(f'!! {bag} icinde .db3 yok'); sys.exit(1)
    cur = sqlite3.connect(db3[0]).cursor()
    tp = {r[1]: r[0] for r in cur.execute('select id,name from topics')}

    P = np.loadtxt(pozcsv, delimiter=',', skiprows=1)
    if P.ndim != 2 or len(P) < 50:
        print(f'!! poz dosyasi yetersiz: {pozcsv}'); sys.exit(1)
    tp_, px, py, pyaw = P[:, 0], P[:, 1], P[:, 2], P[:, 3]
    pyaw_u = np.unwrap(pyaw)
    print(f'poz: {len(P)} satir, {tp_[0]:.1f} .. {tp_[-1]:.1f} s')

    rows = cur.execute('select timestamp,data from messages where topic_id=? order by timestamp',
                       (tp['/velodyne_points'],)).fetchall()[::stride]
    tV = np.array([t / 1e9 for t, _ in rows])

    # SLAM baslamadan onceki / bittikten sonraki taramalarin pozu yok
    ok = (tV >= tp_[0]) & (tV <= tp_[-1])
    print(f'tarama: {len(rows)} (stride {stride}), poz araliginda olan: {ok.sum()}')

    D, PZ, T = [], [], []
    for k, (_, dd) in enumerate(rows):
        if not ok[k]:
            continue
        m = deserialize_message(dd, PointCloud2)
        a = pc2.read_points(m, field_names=('x', 'y', 'z'), skip_nans=True)
        D.append(scan_context(np.asarray(a['x'], np.float64),
                              np.asarray(a['y'], np.float64),
                              np.asarray(a['z'], np.float64)))
        PZ.append([np.interp(tV[k], tp_, px), np.interp(tV[k], tp_, py),
                   np.interp(tV[k], tp_, pyaw_u)])
        T.append(tV[k])
        if len(D) % 200 == 0:
            print(f'  {len(D)} kayit', flush=True)

    D = np.array(D, np.float32); PZ = np.array(PZ); T = np.array(T)
    arc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(PZ[:, :2], axis=0), axis=1))])
    # ardisik kayitlarin ortalama araligi -- konum cozunurlugunu belirler
    step = np.median(np.diff(arc))
    print(f'\n{len(D)} kayit | yay uzunlugu {arc[-1]:.0f} m | kayit araligi medyan {step:.2f} m')
    if arc[-1] < 50:
        print('!! UYARI: yay uzunlugu cok kisa -- pozlar hatali olabilir')

    np.savez_compressed(out, D=D, POZ=PZ, T=T, ARC=arc,
                        NR=NR, NS=NS, RMAX=RMAX, RMIN=RMIN, ZG_PCT=ZG_PCT)
    print(f'yazildi: {out}')


if __name__ == '__main__':
    main()
