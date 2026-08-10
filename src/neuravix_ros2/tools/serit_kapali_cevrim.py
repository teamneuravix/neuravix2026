#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ŞERİT TAKİBİ KAPALI ÇEVRİM TESTİ — simülasyon ve gerçek araç OLMADAN
=====================================================================
Neden var: şerit takibinin virajı alıp almadığını görmek için tek yol CARLA
ya da araç sanılıyordu. Oysa YOLO dışındaki HER ŞEY (BEV fit, ileri bakış,
PID, açı->ham direksiyon dönüşümü, aracın tepkisi) masada kapalı çevrimde
sınanabilir. Bu script sanal bir pist + bisiklet modeli araç kurar, her
karede GERÇEK `lane_follower_node` fonksiyonlarını çağırır ve aracın şeridi
tutup tutmadığını ölçer.

Ne test EDİLİR:
  - fit_lane_poly (fit penceresi, ağırlık, derece, eğim kılavuzu)
  - ileri bakış (lookahead_frac / y_eval)
  - PIDController (Kp/Ki/Kd, anti-windup, leaky integral)
  - açı -> ham direksiyon dönüşümü (control node'daki formülün aynısı)
  - kapalı çevrim kararlılık: yanal hata yakınsıyor mu, salınıyor mu

Ne test EDİLMEZ (bilerek):
  - YOLO segmentasyonu (maskeler sanal olarak, KUSURSUZ üretilir)
  - BEV homografisinin (src_pts) gerçeğe uygunluğu
  - gerçek pist geometrisi (değişken şerit genişliği, bariyerler, kavşaklar)
  ⇒ Bunlar icin KARDES ARAC: `serit_bag_cevrim.py` — ayni kapali cevrimi
    GERCEK ZED kaydinin YOLO maskeleriyle kosar. Bu script saf kontrol/geometri
    dogrulamasi icindir; algi kalitesi sorusunu o digeri cevaplar.
  - gerçek direksiyon motorunun davranisi (yalnizca --olu-bant ile MODELLENIR;
    olculen degerler: dururken ~5, >=3 km/h ~2 ham birim)

KULLANIM:
    # torch/ultralytics gerekiyor (lane_follower_node YOLO import ediyor)
    python3 src/neuravix_ros2/tools/serit_kapali_cevrim.py
    python3 .../serit_kapali_cevrim.py --hiz 1.0 --gurultu 3
    python3 .../serit_kapali_cevrim.py --karsilastir     # eski/yeni ayar
"""
import argparse
import math
import os
import sys

# ⚠️ SIRA ÖNEMLİ: yol ayarı numpy'den ÖNCE olmalı. Aksi halde sistemin/ROS'un
# numpy'si (1.21.5) önce yüklenir ve izole dizindeki matplotlib "numpy>=1.23"
# isteyip patlar. Bu yüzden import'lar aşağıda, yol kurulumundan sonra.
# .../src/neuravix_ros2  (icinde neuravix_ros2/ python paketi var).
# DIKKAT: bir ust dizin (.../src) YANLIS -- orada da 'neuravix_ros2' adinda bir
# klasor var ama o paketin KOKU, icinde lane_follower_node.py yok. O yol
# eklenirse "No module named 'neuravix_ros2.lane_follower_node'" alinir.
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
# YOLO/torch izole bir dizine kurulduysa (masaüstü offline analiz kurulumu)
for _p in (os.path.expanduser("~/lane_libs"),):
    if os.path.isdir(_p):
        sys.path.insert(1, _p)


def _eksik(modul, cozum):
    print(f"\n  HATA: '{modul}' bulunamadi.\n  Cozum:\n    {cozum}\n")
    sys.exit(1)


try:
    import numpy as np                                           # noqa: E402
    import rclpy                                                 # noqa: E402
except ModuleNotFoundError as e:
    _eksik(e.name, "source /opt/ros/humble/setup.bash")
try:
    from neuravix_ros2.lane_follower_node import (                # noqa: E402
        LaneFollowerNode)
except ModuleNotFoundError as e:
    if e.name in ("ultralytics", "torch", "cv2"):
        _eksik(e.name,
               "export PYTHONPATH=$HOME/lane_libs:$PYTHONPATH\n"
               "    (masaustu offline analiz kurulumu; aracin Docker "
               "imajinda bunlar zaten var)")
    raise

# --- BEV ölçekleme: node'un kendi src_pts/dst_pts ve ZED iç parametrelerinden
# türetildi (fy=262, cy=181 @640x360, kamera yüksekliği ~1.15 m) -------------
BEV_NEAR_ROW, BEV_FAR_ROW = 342, 36
D_NEAR_M, D_FAR_M = 1.71, 10.34
PX_PER_M = 125.5            # 384 BEV px = 3.06 m
LANE_W_M = 3.0              # gerçek pistte ölçülen (~2.96 m)

# --- Araç (URDF bee1_robotaxi + 2026-07-13 direksiyon kalibrasyonu) --------
WHEELBASE = 1.86
STEER_RAW_STRAIGHT = 2.0
STEER_RAW_MIN, STEER_RAW_MAX = -21.0, 26.0
STEER_FB_GAIN = -0.02322    # ham birim -> rad
FSM_TO_RAW_GAIN = -0.75     # (aci-45)*gain + offset  (control node'daki formül)


def row_to_m(row):
    fr = (row - BEV_FAR_ROW) / (BEV_NEAR_ROW - BEV_FAR_ROW)
    return D_FAR_M + fr * (D_NEAR_M - D_FAR_M)


def aci_to_delta_rad(angle):
    """FSM açısı (45=düz, >45=SOL) -> tekerlek açısı (rad, +=sol).
    neuravix_control_node_real.py ile birebir aynı zincir."""
    raw = (angle - 45.0) * FSM_TO_RAW_GAIN + STEER_RAW_STRAIGHT
    raw = max(STEER_RAW_MIN, min(STEER_RAW_MAX, raw))
    return (raw - STEER_RAW_STRAIGHT) * STEER_FB_GAIN, raw


# ==========================================================================
# SANAL PİST
# ==========================================================================
def pist_kur(segmentler, ds=0.05):
    """segmentler: [(uzunluk_m, yaricap_m veya None(duz)), ...]
    yaricap > 0 = SOLA döner. Döner: (x, y, theta, kappa) dizileri."""
    xs, ys, th, kp = [0.0], [0.0], [0.0], [0.0]
    for uzunluk, R in segmentler:
        kappa = 0.0 if not R else 1.0 / R
        n = max(1, int(uzunluk / ds))
        for _ in range(n):
            t = th[-1] + kappa * ds
            xs.append(xs[-1] + ds * math.cos(t))
            ys.append(ys[-1] + ds * math.sin(t))
            th.append(t)
            kp.append(kappa)
    return (np.array(xs), np.array(ys), np.array(th), np.array(kp))


def pist_hata(pist, x, y, yaw, son_i=0):
    """Araç pozundan yanal hata (e), yönelim hatası (psi) ve eğrilik (kappa).
    e > 0 = araç şeridin SOLUNDA."""
    px, py, pth, pkp = pist
    lo = max(0, son_i - 200)
    hi = min(len(px), son_i + 2000)
    d2 = (px[lo:hi] - x) ** 2 + (py[lo:hi] - y) ** 2
    i = lo + int(np.argmin(d2))
    dx, dy = x - px[i], y - py[i]
    # yol yönüne dik bileşen: +y_yol = sol
    e = -math.sin(pth[i]) * dx + math.cos(pth[i]) * dy
    psi = math.atan2(math.sin(yaw - pth[i]), math.cos(yaw - pth[i]))
    return e, psi, pkp[i], i


def maske_uret(node, e, psi, kappa, gurultu_px=0.0, rng=None):
    """Şerit çizgilerini BEV maskesi olarak çiz.
    Araç çerçevesinde d ileride yolun yanal konumu:
        y_yol(d) = -e - d*tan(psi) + d^2*kappa/2      (+y = sol)
    BEV'de x sağa artar -> x_bev = merkez - y_yol*PX_PER_M."""
    h, w = node.img_h, node.img_w
    lm = np.zeros((h, w), np.uint8)
    rm = np.zeros((h, w), np.uint8)
    half_px = LANE_W_M / 2.0 * PX_PER_M
    tan_psi = math.tan(max(-1.2, min(1.2, psi)))
    for row in range(int(h * 0.28), h):
        d = row_to_m(row)
        if d <= 0.2:
            continue
        y_yol = -e - d * tan_psi + 0.5 * kappa * d * d
        cx = w / 2.0 - y_yol * PX_PER_M
        if gurultu_px and rng is not None:
            cx += rng.normal(0.0, gurultu_px)
        for m, s in ((lm, -1.0), (rm, +1.0)):
            x = int(round(cx + s * half_px))
            if 3 <= x < w - 3:
                m[row, x - 3:x + 4] = 255
    return lm, rm


def serit_acisi(node, lm, rm):
    """GERÇEK pipeline: fit -> y_eval -> err -> PID -> açı (15..75)."""
    lp, rp = node.fit_lane_poly(lm), node.fit_lane_poly(rm)
    if lp is not None:
        node.left_prev = lp
    if rp is not None:
        node.right_prev = rp
    lp = lp if lp is not None else node.left_prev
    rp = rp if rp is not None else node.right_prev
    if lp is None and rp is None:
        node.pid.reset()
        return 45.0, False

    ye = node.y_eval
    if lp is not None and rp is not None:
        w_px = node.poly_x(rp, ye) - node.poly_x(lp, ye)
        if w_px > 80:
            node.lane_w_px = (float(w_px) if node.lane_w_px is None
                              else 0.9 * node.lane_w_px + 0.1 * w_px)
        lane_x = (node.poly_x(lp, ye) + node.poly_x(rp, ye)) / 2.0
    elif lp is not None:
        lane_x = node.poly_x(lp, ye) + node._half_lane()
    else:
        lane_x = node.poly_x(rp, ye) - node._half_lane()

    err = lane_x - node.img_w / 2.0 - node.err_offset
    node._both_detected = (lp is not None and rp is not None)
    allow_i = node._both_detected and abs(err) <= node.i_error_band
    out = node.pid.calculate(err, allow_integral=allow_i)
    return max(15.0, min(75.0, 45.0 - out)), True


# ==========================================================================
# KOŞUM
# ==========================================================================
def kos(node, pist, hiz_ms, dt=0.05, gurultu_px=0.0, tohum=0,
        baslangic_hata=0.0, sure=None, olu_bant=0.0):
    """olu_bant: direksiyon motorunun ÖLÜ BANDI (ham birim). Duran/çok yavaş
    araçta lastik sürtünmesi motorun yenebileceğinden fazla; komut bu eşiği
    aşmazsa tekerlek HİÇ dönmez. 2026-07-21 algi bag ölçümü:
      0 km/h  -> hedef-tekerlek ort. hata 5.3 ham, korelasyon +0.40
      >=3 km/h-> 1.9 ham, korelasyon +0.90
    Yani düşük hızda ~5, hareket halinde ~2 ham birim ölü bant vardır.
    Kritik sonuç: eski ayar R=12 m viraj için yalnızca 1.8 ham komut ediyordu
    -- ölü bandın TAMAMEN içinde -> tekerlek dönmüyor -> 'viraja girince
    dönmüyor' şikayeti. Yeni ayar 6.75 ham komut ediyor, eşiği aşar."""
    rng = np.random.default_rng(tohum)
    px, py, pth, _ = pist
    yol_uzunlugu = 0.05 * (len(px) - 1)
    # araç yolun başında, istenen yanal hatayla
    x = px[0] - math.sin(pth[0]) * baslangic_hata
    y = py[0] + math.cos(pth[0]) * baslangic_hata
    yaw = pth[0]
    node.pid.reset()
    node.left_prev = node.right_prev = None
    node.lane_w_px = None

    i = 0
    kayit = []
    adim = int((sure or (yol_uzunlugu / hiz_ms)) / dt)
    for _ in range(adim):
        e, psi, kappa, i = pist_hata(pist, x, y, yaw, i)
        if abs(e) > 6.0:                      # şeritten tamamen çıktı
            kayit.append((e, psi, 45.0, 0.0))
            break
        lm, rm = maske_uret(node, e, psi, kappa, gurultu_px, rng)
        aci, _ = serit_acisi(node, lm, rm)
        delta, raw = aci_to_delta_rad(aci)
        if olu_bant and abs(raw - STEER_RAW_STRAIGHT) < olu_bant:
            delta = 0.0            # komut ölü bandın içinde -> tekerlek dönmez
        kayit.append((e, psi, aci, raw))
        # bisiklet modeli
        yaw += hiz_ms * math.tan(delta) / WHEELBASE * dt
        x += hiz_ms * math.cos(yaw) * dt
        y += hiz_ms * math.sin(yaw) * dt
        if i >= len(px) - 300:
            break
    a = np.array(kayit)
    return dict(e=a[:, 0], psi=a[:, 1], aci=a[:, 2], raw=a[:, 3],
                bitti=(i >= len(px) - 400))


def ayarla(node, lookahead, w_pow, derece, far=0.55):
    node.lookahead_frac = lookahead
    node.fit_far_frac = far
    node.fit_weight_pow = w_pow
    node.fit_degree = derece
    node.y_eval = int(node.img_h * lookahead)


PIST = [(15, None), (40, 20), (15, None), (35, -15), (20, None), (30, 30)]
PIST_ADI = "düz15 → SOL R20 (40m) → düz15 → SAĞ R15 (35m) → düz20 → SOL R30"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hiz", type=float, default=2.0, help="m/s (2.0 = 7.2 km/h)")
    ap.add_argument("--gurultu", type=float, default=0.0, help="maske gurultusu (px)")
    ap.add_argument("--baslangic-hata", type=float, default=0.0, help="m")
    ap.add_argument("--olu-bant", type=float, default=0.0,
                    help="direksiyon olu bandi, ham birim (olculen: dururken ~5, "
                         "hareket halinde ~2). 0 = ideal aktuator")
    ap.add_argument("--karsilastir", action="store_true",
                    help="eski (0.90/w^4) ve yeni (0.65/w^1) ayari kiyasla")
    a = ap.parse_args()

    rclpy.init()
    try:
        node = LaneFollowerNode()
    except Exception as e:
        if "not found, searching" in str(e):
            # get_package_share_directory: YOLO agirliklarinin yolu icin
            # ament index gerekiyor -> workspace overlay'i source edilmeli
            _eksik("neuravix_ros2 (ament paket dizini)",
                   "cd ~/Desktop/carla-ros2-ws && source install/setup.bash\n"
                   "    (once bir kez: colcon build --symlink-install "
                   "--base-paths src --packages-select neuravix_ros2)")
        raise
    node.show_window = False
    pist = pist_kur(PIST)

    print(f"\nPİST: {PIST_ADI}")
    print(f"HIZ : {a.hiz:.1f} m/s ({a.hiz*3.6:.1f} km/h)   "
          f"gürültü: {a.gurultu:.0f} px   başlangıç hatası: {a.baslangic_hata:.1f} m"
          f"   ölü bant: {a.olu_bant:.1f} ham")
    print(f"İLERİ BAKIŞ: 0.90*H = {row_to_m(int(360*0.90)):.1f} m | "
          f"0.65*H = {row_to_m(int(360*0.65)):.1f} m\n")

    ayarlar = ([("ESKİ  (0.90*H, w^4)", 0.90, 4.0, 1),
                ("YENİ  (0.65*H, w^1)", 0.65, 1.0, 1)]
               if a.karsilastir else
               [("MEVCUT AYAR", node.lookahead_frac,
                 node.fit_weight_pow, node.fit_degree)])

    print(f"{'ayar':22}{'ort|hata|':>11}{'maks|hata|':>12}"
          f"{'son|hata|':>11}{'maks ham':>10}{'sonuç':>22}")
    for ad, lk, wp, dg in ayarlar:
        ayarla(node, lk, wp, dg)
        r = kos(node, pist, a.hiz, gurultu_px=a.gurultu,
                baslangic_hata=a.baslangic_hata, olu_bant=a.olu_bant)
        e = np.abs(r["e"])
        # salınım: hata işaret değişimi sıklığı
        sgn = np.sign(r["e"])
        flip = np.mean(sgn[1:] != sgn[:-1]) if len(sgn) > 1 else 0
        if e.max() > 5.0:
            sonuc = "ŞERİTTEN ÇIKTI"
        elif e.max() > LANE_W_M / 2:
            sonuc = "şerit dışına taştı"
        elif flip > 0.25:
            sonuc = "salınımlı ama içinde"
        else:
            sonuc = "ŞERİTTE KALDI"
        print(f"{ad:22}{e.mean():>10.2f}m{e.max():>11.2f}m"
              f"{e[-1]:>10.2f}m{np.abs(r['raw']).max():>10.1f}{sonuc:>22}")

    print(f"\n  |hata| = yanal sapma (şerit yarı genişliği {LANE_W_M/2:.2f} m)")
    print(f"  maks ham: direksiyon komutu; mekanik kilit "
          f"{STEER_RAW_MIN:.0f}..{STEER_RAW_MAX:.0f}")
    rclpy.shutdown()


if __name__ == "__main__":
    main()
