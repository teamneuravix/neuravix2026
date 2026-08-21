#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ŞERİT TAKİBİ — GERÇEK KAYITLA HİBRİT KAPALI ÇEVRİM TESTİ
=========================================================
`serit_kapali_cevrim.py` maskeleri KUSURSUZ üretiyordu; bu yüzden YOLO
kalitesini, BEV homografisini ve gerçek pist geometrisini test etmiyordu.
Bu script o boşluğu kapatır: maskeler GERÇEK ZED kaydından, YOLO'nun kendi
çıktısından gelir.

FİKİR — neden bu mümkün:
  Kayıt sırasında araç belli bir yörünge izledi. Biz "araç o yörüngeden Δy
  metre yanda ve Δψ radyan farklı yönelimde olsaydı kamera ne görürdü?"
  sorusunu, kuşbakışı maskeyi ötelleyip döndürerek yaklaşık olarak
  cevaplayabiliriz (düz zeminde geçerli). Böylece kontrolcünün komutu
  gördüğü görüntüyü ETKİLER -> gerçek kapalı çevrim.

  Kayıttaki yörünge "yol" rolünü üstlenir; araç ondan sapabilir, kontrolcü
  geri çekmeye çalışır. Ölçtüğümüz şey: sapma yakınsıyor mu, salınıyor mu,
  yoksa büyüyüp şeritten çıkıyor mu.

ARTIK TEST EDİLENLER (kusursuz maskeli testte edilmeyenler):
  ✓ YOLO segmentasyon kalitesi (gerçek maskeler, kayıp kareler dahil)
  ✓ BEV homografisinin gerçek geometriyle uyumu
  ✓ gerçek pist eğrilikleri, değişken şerit genişliği, bariyerler
  ✓ direksiyon ölü bandı (--olu-bant)

HÂLÂ YAKLAŞIM OLAN:
  - Sahne yeniden RENDER edilmiyor; maske düzlemsel olarak taşınıyor. Büyük
    sapmalarda (>1.5 m) perspektif/örtüşme hataları büyür.
  - Kayıttaki aracın kendi hızı/yörüngesi sabit; biz sadece yanal sapmayı
    simüle ediyoruz.

KULLANIM:
    python3 src/neuravix_ros2/tools/serit_bag_cevrim.py
    python3 ... --baslangic-hata 0.8 --olu-bant 5
    python3 ... --karsilastir          # eski/yeni ayar
Önce önbellek üretilmeli (bir kez, YOLO ile) — yoksa script nasıl yapılacağını
söyler.
"""
import argparse
import math
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
for _p in (os.path.expanduser("~/lane_libs"),):
    if os.path.isdir(_p):
        sys.path.insert(1, _p)


def _eksik(modul, cozum):
    print(f"\n  HATA: '{modul}' bulunamadi.\n  Cozum:\n    {cozum}\n")
    sys.exit(1)


try:
    import numpy as np
    import cv2
    import rclpy
except ModuleNotFoundError as e:
    _eksik(e.name, "source /opt/ros/humble/setup.bash")
try:
    from neuravix_ros2.lane_follower_node import LaneFollowerNode
except ModuleNotFoundError as e:
    if e.name in ("ultralytics", "torch", "cv2"):
        _eksik(e.name, "export PYTHONPATH=$HOME/lane_libs:$PYTHONPATH")
    raise

ONBELLEK = os.path.expanduser("~/.cache/neuravix_serit_ardisik.pkl")
WHEELBASE = 1.86
STEER_RAW_STRAIGHT = 2.0
# 19-20.08.2026'da GUNCELLENDI. Eski degerler (-21/26, gain -0.75) aracin
# kilidin sadece %55'ini kullanmasina yol aciyordu; IMU gyro ile bagimsiz
# olculdu: ham sapma 32 -> teker 31.5 deg -> R = 3.03 m (spec'in tam kilidi).
# Kontrol dugumunun varsayilanlariyla AYNI olmali, yoksa bu arac gercek
# araci degil eski davranisi modeller.
STEER_RAW_MIN, STEER_RAW_MAX = -34.0, 38.0
STEER_FB_GAIN = -0.02322
FSM_TO_RAW_GAIN = -1.20
# ⚠️ MODELLENMEYEN: direksiyon SLEW hizi (olculdu: ~10 birim/s surdurulen,
# 12-18 tepe). Bu araca eklenmedi; slalom_sim.py'de var. Yani buradaki
# sonuclar tekerlegin ANINDA vardigi bir dunyayi varsayar ve gercekten
# IYIMSERDIR — ozellikle keskin viraj girislerinde.


def aci_to_delta(angle):
    raw = (angle - 45.0) * FSM_TO_RAW_GAIN + STEER_RAW_STRAIGHT
    raw = max(STEER_RAW_MIN, min(STEER_RAW_MAX, raw))
    return (raw - STEER_RAW_STRAIGHT) * STEER_FB_GAIN, raw


def kaydir_dondur(bev, dy_m, dpsi, n):
    """Kuşbakışı maskeyi, araç Δy metre yanda / Δψ radyan dönük olsaydı
    görünecek hâle getir.
      - Araç SOLA kaydıysa (Δy>0) yol görüntüde SAĞA kayar  -> +x
      - Araç SOLA döndüyse (Δψ>0) yol saat yönünde döner
    Dönme merkezi aracın kendi konumu (d=0), o da BEV'de görüntünün
    ALTINDA kalır; satırı mesafe eşlemesinden hesaplanır."""
    px_per_m = n.PX_PER_M
    # d=0'in BEV satiri (goruntu disinda olabilir)
    fr0 = (0.0 - n.D_FAR_M) / (n.D_NEAR_M - n.D_FAR_M)
    row0 = n.BEV_FAR_ROW + fr0 * (n.BEV_NEAR_ROW - n.BEV_FAR_ROW)
    merkez = (n.img_w / 2.0, row0)
    M = cv2.getRotationMatrix2D(merkez, math.degrees(dpsi), 1.0)
    M[0, 2] += dy_m * px_per_m          # yanal oteleme
    return cv2.warpAffine(bev, M, (n.img_w, n.img_h), flags=cv2.INTER_NEAREST)


def serit_acisi(n, bev):
    MID = n.img_w // 2
    lm = np.zeros_like(bev); rm = np.zeros_like(bev)
    lm[:, :MID] = bev[:, :MID]; lm[:, MID - 70:] = 0
    rm[:, MID:] = bev[:, MID:]; rm[:, :MID + 70] = 0
    lp, rp = n.fit_lane_poly(lm), n.fit_lane_poly(rm)
    # TAZE fit sayimi (bayat left_prev/right_prev'e DUSMEDEN once)
    taze = int(lp is not None) + int(rp is not None)
    if lp is not None:
        n.left_prev = lp
    if rp is not None:
        n.right_prev = rp
    lp = lp if lp is not None else n.left_prev
    rp = rp if rp is not None else n.right_prev
    if lp is None and rp is None:
        n.pid.reset()
        return 45.0, 0.0, 0
    ye = n.y_eval
    if lp is not None and rp is not None:
        w = n.poly_x(rp, ye) - n.poly_x(lp, ye)
        if w > 80:
            n.lane_w_px = (float(w) if n.lane_w_px is None
                           else 0.9 * n.lane_w_px + 0.1 * w)
        _lx, _rx = n.poly_x(lp, ye), n.poly_x(rp, ye)
        lane_x = (_lx + _rx) / 2.0
        # SON olculen ofsetler (node'daki cb() ile ayni) -- tek fite dusulunce
        # bunlar kullanilir, gecis suruklu olur
        n.off_sol, n.off_sag = lane_x - _lx, _rx - lane_x
    elif lp is not None:
        lane_x = n._tek_fit_merkez(lp, True, ye)
    else:
        lane_x = n._tek_fit_merkez(rp, False, ye)
    err = lane_x - MID - n.err_offset
    # YON ONIZLEMESI — node'un cb() icindeki hesabin aynisi. Bu satir olmazsa
    # arac node'da acik olan bir ozelligi test ETMEZ ve performansi dusuk gosterir.
    egim = n._egim(lp, rp, ye)
    if n.heading_gain and egim is not None:
        err -= n.heading_gain * egim
    n._both_detected = (taze == 2)
    out = n.pid.calculate(err, allow_integral=(taze == 2 and abs(err) <= n.i_error_band))
    return max(15.0, min(75.0, 45.0 - out)), err, taze


def kos(n, kareler, HW, dt, hiz_ms, olu_bant=0.0, baslangic_hata=0.0):
    H, W = HW
    dy, dpsi = baslangic_hata, 0.0
    n.pid.reset(); n.left_prev = n.right_prev = None; n.lane_w_px = None
    hist = []
    for p in kareler:
        raw = (np.unpackbits(p)[:H * W].reshape(H, W) * 255).astype(np.uint8)
        m = n.combine_masks([raw.astype(np.float32) / 255.0], (H, W))
        m[:int(H * 0.40), :] = 0
        bev = kaydir_dondur(n.bev_warp(m), dy, dpsi, n)
        aci, err_px, taze = serit_acisi(n, bev)
        delta, ham = aci_to_delta(aci)
        if olu_bant and abs(ham - STEER_RAW_STRAIGHT) < olu_bant:
            delta = 0.0
        hist.append((dy, aci, ham, taze, err_px))
        # bisiklet modeli: kayittaki yorungeye GORE sapmanin degisimi
        dpsi += hiz_ms * math.tan(delta) / WHEELBASE * dt
        dy += hiz_ms * math.sin(dpsi) * dt
        if abs(dy) > 4.0:
            break
    a = np.array(hist, dtype=float)
    return dict(dy=a[:, 0], aci=a[:, 1], ham=a[:, 2], taze=a[:, 3],
                err=a[:, 4])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hiz", type=float, default=2.0)
    ap.add_argument("--olu-bant", type=float, default=0.0)
    ap.add_argument("--baslangic-hata", type=float, default=0.5,
                    help="baslangicta yanal sapma (m) — kontrolcu toparlamali")
    ap.add_argument("--karsilastir", action="store_true")
    ap.add_argument("--onbellek", default=ONBELLEK)
    a = ap.parse_args()

    if not os.path.exists(a.onbellek):
        print(f"\n  Onbellek yok: {a.onbellek}")
        print("  Once ardisik kareler + YOLO maskeleri uretilmeli.")
        print("  (ZED bag'inden bir kez; ayrintili komut icin ekibe danisin)\n")
        sys.exit(1)
    kareler, HW, dt = pickle.load(open(a.onbellek, "rb"))

    rclpy.init()
    try:
        n = LaneFollowerNode()
    except Exception as e:
        if "not found, searching" in str(e):
            _eksik("neuravix_ros2 (ament)",
                   "cd ~/Desktop/carla-ros2-ws && source install/setup.bash")
        raise
    n.show_window = False

    print(f"\nGERCEK KAYIT: {len(kareler)} ardisik kare, dt={dt:.4f}s "
          f"({len(kareler)*dt:.1f} s)")
    print(f"HIZ {a.hiz:.1f} m/s | olu bant {a.olu_bant:.1f} ham | "
          f"baslangic sapmasi {a.baslangic_hata:.2f} m\n")

    ayarlar = ([("ESKI (0.90*H, w^4)", 0.90, 4.0), ("YENI (0.65*H, w^1)", 0.65, 1.0)]
               if a.karsilastir else
               [("MEVCUT AYAR", n.lookahead_frac, n.fit_weight_pow)])
    print(f"{'ayar':22}{'ort|hata|':>12}{'maks':>8}{'son':>8}"
          f"{'maks ham':>10}{'2-fit%':>8}{'0-fit%':>8}{'sonuc':>18}")
    for ad, lk, wp in ayarlar:
        n.lookahead_frac, n.fit_weight_pow = lk, wp
        n.y_eval = int(n.img_h * lk)
        r = kos(n, kareler, HW, dt, a.hiz, a.olu_bant, a.baslangic_hata)
        # ASIL OLCUT: kontrolcunun KENDI olctugu serit hatasi. (Kayittaki
        # insan surucunun yorungesinden sapma DEGIL -- surucu de serit
        # ortasinda olmayabilir, o yuzden dy bir hata olcusu degildir.)
        em = np.abs(r["err"]) / n.PX_PER_M
        son = em[-max(1, len(em) // 5):].mean()      # son %20
        iki = 100.0 * np.mean(r["taze"] == 2)
        sifir = 100.0 * np.mean(r["taze"] == 0)
        sonuc = ("YAKINSAMADI" if son > 0.6 else
                 "kismen" if son > 0.3 else "YAKINSADI")
        print(f"{ad:22}{em.mean():>11.2f}m{em.max():>7.2f}m{son:>7.2f}m"
              f"{np.abs(r['ham']).max():>10.1f}{iki:>7.0f}%{sifir:>7.0f}%{sonuc:>18}")
    print("\n  |serit hatasi| = kontrolcunun olctugu merkez sapmasi (metre)")
    print("  'son' = son %20'lik dilimin ortalamasi -> yakinsadi mi")
    rclpy.shutdown()


if __name__ == "__main__":
    main()
