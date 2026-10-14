#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tabela mesafesini bir rosbag'den olcer / dogrular.

IKI MOD:

1) --mod hareket  (derinlik KAYITTA YOKKEN de calisir)
   Hareketten olcek. d = K/h ve d(t) = d0 - s(t) ise:
        s(t) = d0 - K * (1/h(t))
   s(t) arac hizindan integre edilen yol. (1/h, s) dogrusal regresyonunun
   egimi dogrudan K'yi verir. Bu olcum ODAK UZAKLIGINDAN ve NESNENIN
   FIZIKSEL BOYUTUNDAN BAGIMSIZDIR -- yedek formulun sabitleri boyle olculdu.

   Uyari: CAN hizi tam sayi km/h. Arac yavas surulduyse (0-3 km/h) nicemleme
   K'nin MUTLAK degerine ~%30 belirsizlik katar; iki nesnenin ORANI saglamdir.

2) --mod derinlik (kayitta derinlik topic'i VARSA)
   Her tespit icin bbox'tan okunan ZED derinligini, bbox yuksekliginden
   turetilen tahminle yan yana basar. Arac gununde "derinlik gercekten
   dogru mu" sorusunun cevabi budur.

Ornek:
    python3 src/neuravix_ros2/tools/tabela_mesafe_kalibre.py \
        --bag /media/myozen/T7/neuravix/joystick_46/joystick_46_0.db3 \
        --mod hareket --sinif DUR_TT-2 --sabit 362
"""
import argparse
import os
import sqlite3
import struct
import sys

import numpy as np

try:
    import cv2
    from ultralytics import YOLO
except ImportError as e:                                    # pragma: no cover
    sys.exit(f"'{e.name}' yok. Masaustu analiz kurulumu icin: "
             "export PYTHONPATH=$HOME/lane_libs:$PYTHONPATH")

HERE = os.path.dirname(os.path.abspath(__file__))
VARSAYILAN_MODEL = os.path.join(os.path.dirname(HERE), "models", "makarayizabi2.pt")


# --------------------------------------------------------------------------
# CDR ayristirma (rosbag2 sqlite3; ROS kurulumuna ihtiyac duymadan)
# --------------------------------------------------------------------------
def _atla_str(d, o):
    ln = struct.unpack_from('<I', d, o)[0]
    return o + 4 + ln


def parse_image(d):
    """sensor_msgs/Image -> (stamp_sn, encoding, yukseklik, genislik, ham_dizi)."""
    o = 4
    sec, nsec = struct.unpack_from('<iI', d, o); o += 8
    o = _atla_str(d, o)
    o = (o + 3) // 4 * 4
    h, w = struct.unpack_from('<II', d, o); o += 8
    ln = struct.unpack_from('<I', d, o)[0]
    enc = d[o + 4:o + 4 + ln - 1].decode(); o += 4 + ln
    o += 1                                   # is_bigendian
    o = (o + 3) // 4 * 4
    o += 4                                   # step
    dlen = struct.unpack_from('<I', d, o)[0]; o += 4
    return sec + nsec * 1e-9, enc, h, w, (d, o, dlen)


def goruntu_bgr(paket):
    _, enc, h, w, (d, o, dlen) = paket
    arr = np.frombuffer(d, np.uint8, dlen, o)
    if enc in ('bgra8', 'rgba8'):
        img = arr.reshape(h, w, 4)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR if enc == 'bgra8' else cv2.COLOR_RGBA2BGR)
    if enc == 'bgr8':
        return arr.reshape(h, w, 3)
    if enc == 'rgb8':
        return cv2.cvtColor(arr.reshape(h, w, 3), cv2.COLOR_RGB2BGR)
    raise ValueError(f'desteklenmeyen RGB encoding: {enc}')


def derinlik_metre(paket):
    _, enc, h, w, (d, o, dlen) = paket
    if enc.lower() in ('32fc1', '32fc'):
        return np.frombuffer(d, np.float32, dlen // 4, o).reshape(h, w)
    if enc.lower() == '16uc1':
        return np.frombuffer(d, np.uint16, dlen // 2, o).reshape(h, w).astype(np.float32) / 1000.0
    raise ValueError(f'desteklenmeyen derinlik encoding: {enc}')


# --------------------------------------------------------------------------
def topic_id(c, ad):
    r = c.execute("SELECT id FROM topics WHERE name=?", (ad,)).fetchone()
    return r[0] if r else None


def yol_profili(c, hiz_topic):
    """CAN hizindan katedilen yolu integre eder -> (t dizisi, s dizisi)."""
    tid = topic_id(c, hiz_topic)
    if tid is None:
        sys.exit(f"'{hiz_topic}' bag'de yok. --hiz-topic ile dogrusunu verin.")
    t, v = [], []
    for ts, d in c.execute('SELECT timestamp,data FROM messages WHERE topic_id=? '
                           'ORDER BY timestamp', (tid,)):
        _kmh, reel_kmh, _ms = struct.unpack_from('<BBB', d, 4)
        t.append(ts / 1e9); v.append(reel_kmh / 3.6)
    t, v = np.array(t), np.array(v)
    s = np.concatenate([[0.0], np.cumsum(np.diff(t) * (v[:-1] + v[1:]) / 2)])
    print(f"hiz: {len(t)} mesaj, {t[-1]-t[0]:.0f} sn, max {v.max()*3.6:.0f} km/h, "
          f"toplam yol {s[-1]:.1f} m")
    if v.max() * 3.6 <= 3:
        print("  UYARI: hiz tam sayi km/h ve arac cok yavas -> K'nin MUTLAK "
              "degerinde ~%30 belirsizlik var (oranlar yine de saglam).")
    return t, s


def tespitler(c, img_tid, model, sinif, lo, hi, adim):
    """Verilen kare araliginda hedef sinifi arar -> [(idx, t, h, bbox), ...]."""
    kareler = [(r[0], r[1] / 1e9) for r in
               c.execute('SELECT id,timestamp FROM messages WHERE topic_id=? '
                         'ORDER BY timestamp', (img_tid,))]
    hi = min(hi, len(kareler)) if hi else len(kareler)
    out = []
    for i in range(lo, hi, adim):
        mid, ts = kareler[i]
        d = c.execute('SELECT data FROM messages WHERE id=?', (mid,)).fetchone()[0]
        img = goruntu_bgr(parse_image(d))
        r = model(img, conf=0.35, imgsz=640, verbose=False)[0]
        en_iyi = None
        for b in (r.boxes or []):
            if model.names[int(b.cls[0])] != sinif:
                continue
            x1, y1, x2, y2 = b.xyxy[0].tolist()
            if en_iyi is None or (y2 - y1) > en_iyi[0]:
                en_iyi = (y2 - y1, np.array([x1, y1, x2, y2]))
        if en_iyi:
            out.append((i, ts, en_iyi[0], en_iyi[1]))
    return out, kareler


def mod_hareket(det, t_s, s_cum, sabit):
    if len(det) < 8:
        sys.exit(f"yeterli tespit yok ({len(det)}) -- kare araligini genisletin")
    ts = np.array([d[1] for d in det])
    hh = np.array([d[2] for d in det])
    s = np.interp(ts, t_s, s_cum)
    m = np.gradient(hh) > -0.5                     # yalnizca yaklasma fazi
    x, s, hh = 1.0 / hh[m], s[m], hh[m]
    A = np.vstack([x, np.ones_like(x)]).T
    (egim, d0), *_ = np.linalg.lstsq(A, s, rcond=None)
    K = -egim
    rms = float(np.sqrt(np.mean((A @ [egim, d0] - s) ** 2)))
    print(f"\n  {len(det)} tespit ({len(x)} yaklasma karesi), "
          f"h {hh.min():.0f}..{hh.max():.0f} px, yol {s.max()-s.min():.1f} m")
    print(f"  OLCULEN SABIT K = {K:.0f}    (karsilastirma: {sabit})")
    print(f"  -> kod/gercek = {sabit/K:.2f}x ; ilk gorulme {d0-s.min():.1f} m ; "
          f"regresyon RMS {rms:.2f} m")
    for i in (0, len(x) // 2, len(x) - 1):
        print(f"     h={hh[i]:5.0f}px -> gercek {K/hh[i]:5.2f} m | "
              f"formul {sabit/hh[i]:5.2f} m")


def mod_derinlik(c, det, kareler, dep_tid, roi=0.5, lo_m=0.4, hi_m=40.0, sabit=362.0):
    dkareler = [(r[0], r[1] / 1e9) for r in
                c.execute('SELECT id,timestamp FROM messages WHERE topic_id=? '
                          'ORDER BY timestamp', (dep_tid,))]
    dts = np.array([t for _, t in dkareler])
    print(f"\n  {'kare':>6} {'h(px)':>6} {'ZED(m)':>8} {'formul(m)':>10} {'fark':>7}")
    farklar = []
    for idx, ts, h, bbox in det:
        j = int(np.argmin(np.abs(dts - ts)))
        if abs(dts[j] - ts) > 0.15:
            continue
        d = c.execute('SELECT data FROM messages WHERE id=?', (dkareler[j][0],)).fetchone()[0]
        dep = derinlik_metre(parse_image(d))
        x1, y1, x2, y2 = bbox
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        rw, rh = max(1, (x2 - x1) * roi / 2), max(1, (y2 - y1) * roi / 2)
        sub = dep[int(max(0, cy - rh)):int(cy + rh + 1),
                  int(max(0, cx - rw)):int(cx + rw + 1)]
        ok = np.isfinite(sub) & (sub >= lo_m) & (sub <= hi_m)
        if ok.sum() < 0.15 * sub.size:
            print(f"  {idx:>6} {h:>6.0f} {'gecersiz':>8}")
            continue
        zed = float(np.median(sub[ok]))
        tahmin = sabit / max(h, 1)
        farklar.append(tahmin - zed)
        print(f"  {idx:>6} {h:>6.0f} {zed:>8.2f} {tahmin:>10.2f} {tahmin-zed:>+7.2f}")
    if farklar:
        f = np.array(farklar)
        print(f"\n  formul - ZED: ort {f.mean():+.2f} m, std {f.std():.2f} m, "
              f"|max| {np.abs(f).max():.2f} m")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--bag', required=True, help='rosbag2 .db3 dosyasi')
    ap.add_argument('--mod', choices=('hareket', 'derinlik'), default='hareket')
    ap.add_argument('--sinif', required=True, help="model sinif adi, orn. DUR_TT-2")
    ap.add_argument('--model', default=VARSAYILAN_MODEL)
    ap.add_argument('--rgb-topic', default='/zed/zed_node/rgb/image_rect_color')
    ap.add_argument('--depth-topic', default='/zed/zed_node/depth/depth_registered')
    ap.add_argument('--hiz-topic', default='/beemobs/FB_VehicleSpeed')
    ap.add_argument('--sabit', type=float, default=362.0,
                    help='karsilastirilacak bbox sabiti (tabela 362 / isik 218)')
    ap.add_argument('--lo', type=int, default=0, help='baslangic kare indeksi')
    ap.add_argument('--hi', type=int, default=0, help='bitis kare indeksi (0=son)')
    ap.add_argument('--adim', type=int, default=1)
    A = ap.parse_args()

    c = sqlite3.connect(f'file:{A.bag}?mode=ro', uri=True)
    img_tid = topic_id(c, A.rgb_topic)
    if img_tid is None:
        print("bag'deki topic'ler:")
        for r in c.execute('SELECT name,type FROM topics'):
            print('   ', r[0], r[1])
        sys.exit(f"\n'{A.rgb_topic}' yok -- --rgb-topic ile dogrusunu verin.")

    model = YOLO(A.model)
    if A.sinif not in model.names.values():
        sys.exit(f"'{A.sinif}' modelde yok. Siniflar: {sorted(model.names.values())}")

    if A.mod == 'hareket':
        t_s, s_cum = yol_profili(c, A.hiz_topic)
        det, _ = tespitler(c, img_tid, model, A.sinif, A.lo, A.hi, A.adim)
        mod_hareket(det, t_s, s_cum, A.sabit)
    else:
        dep_tid = topic_id(c, A.depth_topic)
        if dep_tid is None:
            sys.exit(f"'{A.depth_topic}' bag'de yok -- derinlik kaydedilmemis. "
                     "'--mod hareket' kullanin.")
        det, kareler = tespitler(c, img_tid, model, A.sinif, A.lo, A.hi, A.adim)
        mod_derinlik(c, det, kareler, dep_tid, sabit=A.sabit)


if __name__ == '__main__':
    main()
