#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLALOM MASA TESTİ — CARLA'sız, ROS'suz.
================================================================
decision_brain.Alkar_Function4'ü basit bir araç model + sentetik
lidar sektörleriyle (obstacle_lidar_node ile AYNI geometri) kapalı çevrimde
sürer. Amaç: slalom mantığını (üç fazlı weave, çarpışma koruması, yön seçimi)
masaüstünde saniyeler içinde test etmek — CARLA yalnızca SON doğrulama için.

Çalıştırma (workspace herhangi bir yerinden):
    python3 src/neuravix_ros2/slalom_sim.py
Çıktı: konsol özeti + slalom_sim.png (senaryo yörüngeleri)

Eski beyinle karşılaştırma (eski decision_brain kopyası bir pakette ise):
    python3 slalom_sim.py --old-pkg /path/to/old_brain_pkg
"""
import argparse
import math
import os
import sys

# Paket dizinini yola ekle (script src/neuravix_ros2/ altında durur)
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from neuravix_ros2.decision_brain import Alkar_Function4  # noqa: E402


# ================================================================
# Araç modeli 
# ================================================================
WHEELBASE   = 1.86                    # m (spec dokümanından)
# TAM KİLİT AÇISI — ARAÇTA ÖLÇÜLDÜ (19.08.2026, slalom_0819_1318 bag'i).
# Spec 31.25 diyor (iç 32.5 / dış 30.0) ve model bunu kullanıyordu, ama
# gerçek sürüşte araç iki kat geniş dönüyor:
#   kaçış fazı, tekerlek geri beslemesi -19..-22 (kilidin %91'i):
#     yol 3.11 m, dönüş 29.9° -> R = 5.97 m -> teker 17.3°
#   dönüş fazı: yol 2.90 m, dönüş 31.8° -> R = 5.21 m -> teker 19.6°
# Ölçüm kendi içinde tutarlı: yanal 0.83 m + yaw 30.2° -> R = 0.83/(1-cos30.2)
# = 6.1 m, yol/yaw'dan çıkanla aynı. Yaw IMU gyro'dan geliyor, yani
# direksiyon kalibrasyonundan bağımsız.
# Sonuç: ham -21/+26 sınırları GERÇEK MEKANİK KİLİT DEĞİL (CLAUDE.md zaten
# "kumandayla ölçüm kilide varmadığı için güvenilmez" diyordu).
# %91 -> %100 ölçeklenince 19.0°, R = 5.40 m.
# 19.08.2026: kısa süre 19.0'a çekildi (bag'den ölçülen R=5.4 m), sonra kök
# neden bulununca 29.7'ye alındı. Araç kilidin sadece %55'ini kullanıyormuş:
# ham sapma 21'de kesiliyordu, gerçek mekanik kilit ~38. Kontrol düğümünün
# menzili düzeltildi (steer_delta ±36, gain -1.20) -> FSM 75 artık ham sapma
# 36 gönderiyor -> teker 29.7 deg -> R = 3.26 m. Model o değeri yansıtır.
MAX_DELTA   = math.radians(29.7)      # duzeltilmis menzille ulasilan kilit
HALF_WIDTH  = 0.53                    # m (body_width 1.06 / 2)


# ================================================================
# DIREKSIYON AKTUATORU — 20.08.2026'da eklendi.
#
# ONCEDEN BU MODEL YOKTU ve simulator FSM acisini ANINDA teker acisina
# ceviriyordu. Bu yuzden masa suite 7/8 verirken arac sahada takiliyordu:
# faz gecisinde komut tam ters kilide sicriyor, TEKERLEK ORAYA SANIYELER
# SONRA variyor ve o sure boyunca arac hala eski yone donuyor.
#
# OLCUM (lokal_0820_0722 + slalom_0819_1318 bag'leri, 20.08.2026):
#   - tekerlek slew hizi: MEDYAN 10 birim/s (gorulen en yuksek 30)
#   - t=10:23:52'de komut -27'den +38'e sicradi; tekerlek
#     +1s: -15   +2s: +2   +4s: +31   -> sifiri gecmesi 2 SANIYE surdu
#   - o iki saniyede arac hala SOLA donuyordu; yanal ofset hedef 1.7 iken
#     3.0'a cikti (fazla 1.3 m). v*T*sin(theta) = 0.55*3.2*0.67 = 1.18 m,
#     olculen fazlayla birebir.
#   - ham birim <-> teker acisi: sapma 32 -> 31.5 deg (IMU gyro ile, yani
#     direksiyondan BAGIMSIZ olculdu) => ~1 derece / birim.
#
# Kontrolcu (bee1_description/scripts/steering_ctrl.py):
#   delta_pwm = min(max_delta, min_drive + kp*(|hata|-tol))
# max_delta=68 iken |hata|>16.3 icin PWM SABIT kalir -> hiz artmaz.
# ================================================================
DEG_PER_UNIT = 0.98        # olculdu: ham sapma 32 -> 31.5 deg
STEER_STRAIGHT = 2.0       # duz konumun ham degeri
STEER_SLEW = 10.0          # birim/s (max_delta=68 ile OLCULEN medyan)
STEER_TOL = 1.0            # steering_ctrl tolerance: icindeyken motor kapali
# Kontrol dugumunun ham hedef esleme sabitleri (neuravix_control_node_real)
STEER_GAIN = -1.20
STEER_DELTA_L, STEER_DELTA_R = -36.0, 36.0
STEER_RAW_MIN, STEER_RAW_MAX = -34.0, 38.0


# ================================================================
# HIZ OLCEKLEMESI — 20.08.2026'da eklendi.
#
# Simulator FSM'in km/h degerini ARACA DOGRUDAN veriyordu. Gercek dugum
# (neuravix_control_node_real._cmd_speed) ise once olcekliyor:
#     s = min(fsm_kmh * speed_target_scale, max_speed_kmh)
#     s = max(s, min_speed_kmh)          # s > 0 iken
# Araçta kullanilan degerlerle (scale 0.25) FSM'in 4.0 km/h'si araca
# 1.2 km/h olarak gidiyor. Simulator ise 4.0'i oldugu gibi suruyordu, yani
# GERCEK ARACIN 3-5 KATI HIZLA.
#
# Bu, direksiyon gecikmesiyle birleşince simulatoru yaniltiyordu: tekerlek
# donerken simulator 2.9 m yiyor, arac 0.9 m. Sonuc olarak simulatorde weave
# kacis fazinda acil esige carpip kesiliyor, araçta ise devam edip donus
# fazina variyor ve ORADA asiyor. Yani simulator gercegin arizasini degil
# BASKA bir arizayi uretiyordu ve donus fazi hic test edilemiyordu.
SPEED_SCALE = 0.25       # -p speed_target_scale
MIN_SPEED   = 1.2        # -p min_speed_kmh
MAX_SPEED   = 5.0        # -p max_speed_kmh


def arac_hizi(fsm_kmh, brake):
    """FSM km/h -> araca giden gercek hiz hedefi (kontrol dugumunun aynisi)."""
    if brake:
        return 0.0
    s = min(float(fsm_kmh) * SPEED_SCALE, MAX_SPEED)
    if s > 0.0 and MIN_SPEED > 0.0:
        s = max(s, MIN_SPEED)
    return s


def fsm_to_raw(steer_alkar):
    """FSM acisi (15..75) -> araca gonderilen HAM direksiyon hedefi."""
    sap = (float(steer_alkar) - 45.0) * STEER_GAIN
    sap = max(STEER_DELTA_L, min(STEER_DELTA_R, sap))
    return max(STEER_RAW_MIN, min(STEER_RAW_MAX, STEER_STRAIGHT + sap))


class Vehicle:
    def __init__(self, x=0.0, y=0.0, yaw=0.0):
        self.x, self.y, self.yaw = x, y, yaw
        self.v = 0.0          # m/s
        self.dist = 0.0       # katedilen yol (m)
        self.raw = STEER_STRAIGHT   # tekerlegin GERCEK ham konumu

    def step(self, steer_alkar, target_kmh, brake, dt):
        target_v = arac_hizi(target_kmh, brake) / 3.6
        tau = 0.35 if (brake or target_v < self.v) else 1.2   # fren/yavaşlama hızlı
        self.v += (target_v - self.v) * min(1.0, dt / tau)
        if self.v < 0.02 and target_v == 0.0:
            self.v = 0.0
        # --- direksiyon aktuatoru: hedefe SLEW hiziyla yaklasir ---
        hedef = fsm_to_raw(steer_alkar)
        hata = hedef - self.raw
        if abs(hata) > STEER_TOL:
            adim = STEER_SLEW * dt
            self.raw += math.copysign(min(adim, abs(hata)), hata)
        # ham -> teker acisi. Ham POZITIF = fiziksel SAG = negatif yaw.
        delta = math.radians(-(self.raw - STEER_STRAIGHT) * DEG_PER_UNIT)
        self.yaw += self.v / WHEELBASE * math.tan(delta) * dt
        self.x += self.v * math.cos(self.yaw) * dt
        self.y += self.v * math.sin(self.yaw) * dt
        self.dist += self.v * dt


# ================================================================
# Sanal lidar — obstacle_lidar_node.py ile AYNI sektör geometrisi
# (side_offset=3.0 / side_corridor=1.5: 2026-08-03 pist ölçüsü güncellemesi)
# ================================================================
CORRIDOR   = 0.70
# 17.08.2026: pist şerit genişliği ÖLÇÜLDÜ = 2.96 m (lane_follower'ın lane_w_px
# değeri; bir şeridin iki çizgisi arası). Yan sektör sınırları ona göre:
#   yakın kenar 1.48 = orta çizgi -> kendi şeridimizdeki engel yan sektöre
#     girmesin (engel yarı-eni 0.60-0.75 m).
#   uzak kenar  4.00 = sol duvarın (1.5*2.96 = 4.44) 0.44 m berisi.
# merkez=(1.48+4.00)/2=2.74, yarı genişlik=(4.00-1.48)/2=1.26.
# Bu sayılar obstacle_lidar_node'a launch'tan geçilenlerle AYNI olmalı —
# ayrılırlarsa bu dosya gerçeği değil bir kurguyu test eder.
PIST_SERIT = 2.96
SIDE_OFF   = 2.74
SIDE_CORR  = 1.26
BUMPER     = 0.233
X_MIN      = 0.5
SIDE_X_MIN = -1.86
MAX_RANGE  = 30.0
CLEAR      = 99.0


def sector_distances(veh, points):
    """Dünya koordinatlı engel noktalarını araç çerçevesine çevirip
    front/left/right kleransını hesaplar (obstacle_lidar semantiği)."""
    cy, sy = math.cos(veh.yaw), math.sin(veh.yaw)
    fx, lx, rx = [], [], []
    near = 0
    for (px, py) in points:
        dx, dy = px - veh.x, py - veh.y
        xv = dx * cy + dy * sy          # araç ileri ekseni
        yv = -dx * sy + dy * cy         # araç sol ekseni (+y sol)
        if xv >= MAX_RANGE:
            continue
        if abs(yv) <= CORRIDOR:
            if X_MIN < xv:
                fx.append(xv)
            elif BUMPER < xv <= X_MIN:  # near-field guard
                near += 1
        if abs(yv - SIDE_OFF) < SIDE_CORR and SIDE_X_MIN < xv:
            lx.append(xv)
        if abs(yv + SIDE_OFF) < SIDE_CORR and SIDE_X_MIN < xv:
            rx.append(xv)
    front = 0.0 if near >= 4 else (max(0.0, min(fx) - BUMPER) if fx else CLEAR)
    left  = max(0.0, min(lx) - BUMPER) if lx else CLEAR
    right = max(0.0, min(rx) - BUMPER) if rx else CLEAR
    return front, left, right


# Yanal klerans profili — obstacle_lidar_node._profil ile AYNI geometri.
PROF_Y_MAX = 3.5
PROF_STEP  = 0.5


def lateral_profile(veh, points):
    """Her yanal kutu icin boylamsal klerans (arac cercevesi, +y sol).

    Beyin bunu "kendi seridim su an -_lateral yanimda, orada ne var?"
    sorusunu sormak icin kullanir; sabit yan sektorler bunu cevaplayamiyor
    cunku arac kaymisken bariyeri tariyorlar.
    """
    cy, sy = math.cos(veh.yaw), math.sin(veh.yaw)
    n = int(round(2.0 * PROF_Y_MAX / PROF_STEP)) + 1
    kova = [[] for _ in range(n)]
    for (px, py) in points:
        dx, dy = px - veh.x, py - veh.y
        xv = dx * cy + dy * sy
        if not (X_MIN < xv < MAX_RANGE):
            continue
        yv = -dx * sy + dy * cy
        for i in range(n):
            yc = -PROF_Y_MAX + i * PROF_STEP
            if abs(yv - yc) <= CORRIDOR:
                kova[i].append(xv)
    return [max(0.0, min(k) - BUMPER) if k else CLEAR for k in kova]


def circle_pts(cx, cy, r, n=48):
    return [(cx + r * math.cos(a), cy + r * math.sin(a))
            for a in [2 * math.pi * i / n for i in range(n)]]


def box_pts(cx, cy, w, h, step=0.15):
    """Dikdörtgen engel çevre noktaları (pist engeli 1.4x1.4 m kutu)."""
    pts = []
    hw, hh = w / 2.0, h / 2.0
    nx = max(2, int(w / step)); ny = max(2, int(h / step))
    for i in range(nx + 1):
        x = cx - hw + w * i / nx
        pts += [(x, cy - hh), (x, cy + hh)]
    for i in range(ny + 1):
        y = cy - hh + h * i / ny
        pts += [(cx - hw, y), (cx + hw, y)]
    return pts


def wall_pts(x0, y0, x1, y1, step=0.25):
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / step))
    return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n)
            for i in range(n + 1)]


# ================================================================
# Şerit takipçisi vekili: şerit merkezi y=0 varsayımıyla basit açı üretir
# (gerçekte lane_follower'ın /master ID-2 çıktısının yerine geçer)
# ================================================================
def lane_steer_proxy(veh):
    # y>0 = şeridin solundayız -> sağa kır (<45); yaw>0 = sola bakıyoruz -> sağa
    return max(15.0, min(75.0, 45.0 - 25.0 * veh.y - 55.0 * veh.yaw))


# ================================================================
# Senaryo koşucusu — kontrol düğümünün 20 Hz döngüsünü taklit eder
# ================================================================
# T VARSAYILANI 60 -> 120 s (20.08.2026). Hiz olceklemesi eklendikten sonra
# arac gercek araç gibi ~1.2 km/h suruyor (onceden 4-10 km/h); 60 saniye
# 20 m'lik bir senaryoyu bitirmeye YETMIYOR ve senaryolar "sure doldu" diye
# OBSTACLE_AVOID'da kalip basarisiz sayiliyordu.
def run_scenario(brain_cls, obstacles, walls=(), T=120.0, dt=0.05,
                 feed_yaw=True, label=""):
    veh = Vehicle()
    brain = brain_cls()
    clock = {"t": 0.0}
    brain._now = lambda: clock["t"]        # beyin duvar saatine değil sim saatine baksın

    # PİST AYARLARI — araçta launch'tan geçilenlerle AYNI olmalı.
    # Beynin varsayılanları geniş yol içindir (lateral_target=3.0 = tam şerit
    # değişimi); 2.96 m'lik pistte o hedef 2. engelin tam içine götürür.
    # Bu blok olmadan simülatör araçta çalışacak ayarı DEĞİL, varsayılanları
    # test eder — 17.08.2026'da tam bu yüzden suite 5/5 verirken CARLA
    # kilitleniyordu.
    for k, v in PIST_PARAMS.items():
        setattr(brain, k, v)

    pts = []
    for ob in obstacles:
        if len(ob) == 4:            # (x, y, w, h) kutu
            pts += box_pts(*ob)
        else:                       # (x, y, r) daire
            pts += circle_pts(*ob)
    for w in walls:
        pts += wall_pts(*w)

    log = {"t": [], "x": [], "y": [], "yaw": [], "steer": [], "v": [],
           "state": [], "phase": [], "min_clear": 1e9, "events": []}
    next_obs = 0.0
    last_state = None

    n_steps = int(T / dt)
    for i in range(n_steps):
        clock["t"] = i * dt

        # 10 Hz engel algısı (obstacle_lidar rate_hz=10)
        if clock["t"] >= next_obs - 1e-9:
            f, l, r = sector_distances(veh, pts)
            brain.obstacle_event(front=f, left=l, right=r,
                                 profile=lateral_profile(veh, pts),
                                 profile_y0=-PROF_Y_MAX, profile_dy=PROF_STEP)
            next_obs += 0.1

        # ~20 Hz şerit algısı
        brain.lane_detect_event([2, lane_steer_proxy(veh)])

        # 20 Hz kontrol döngüsü (control_loop eşdeğeri)
        try:
            if feed_yaw:
                # KONUM DA VERILIR (17.08.2026). Her iki kontrol dugumu de
                # x/y besliyor ve beyin yanal ofseti KONUMDAN olcuyor; sadece
                # distance+yaw verilirse olu-hesap yaw integraline duser ve
                # 20 m'de ~1.8 m sapar (CLAUDE.md). O fark yuzunden bu suite
                # arac ayariyla ayni sonucu vermiyordu.
                brain.update_motion(distance=veh.dist, yaw=veh.yaw,
                                    x=veh.x, y=veh.y)
            else:
                # feed_yaw=False: odometrisiz gerilemeyi test eder (zaman
                # tabanli fazlar) — kasitli olarak konum da verilmez.
                brain.update_motion(distance=veh.dist)
        except TypeError:                   # eski beyin: yaw parametresi yok
            brain.update_motion(distance=veh.dist)
        brain._update_state_machine()
        d = brain.get_decision()

        steer = float(d["steering_angle"])
        lb = float(d.get("lane_blend", 0.0))
        if d["state"] == "LANE_FOLLOW":
            pass                            # FSM çıktısı zaten şerit açısı (planner off)
        elif lb > 0.0:
            steer = (1.0 - lb) * steer + lb * lane_steer_proxy(veh)

        veh.step(steer, d["target_speed_kmh"], d["brake"], dt)

        # Engele en yakın geçiş (araç merkezinden nokta bulutuna)
        for (px, py) in pts:
            dd = math.hypot(px - veh.x, py - veh.y)
            if dd < log["min_clear"]:
                log["min_clear"] = dd

        st = d["state"]
        if st != last_state:
            log["events"].append((clock["t"], st, brain.last_event))
            last_state = st
        log["t"].append(clock["t"]); log["x"].append(veh.x)
        log["y"].append(veh.y); log["yaw"].append(veh.yaw)
        log["steer"].append(steer); log["v"].append(veh.v * 3.6)
        log["state"].append(st); log["phase"].append(d.get("avoid_phase"))

    # --- Değerlendirme ---
    obs_max_x = max((o[0] for o in obstacles), default=0.0)
    end_y, end_x = veh.y, veh.x
    collided = log["min_clear"] < (HALF_WIDTH + 0.05)
    passed = end_x > obs_max_x + 2.0 if obstacles else True
    returned = abs(end_y) < 0.6
    log["result"] = {
        "label": label, "collided": collided, "passed": passed,
        "returned": returned, "end": (end_x, end_y),
        "min_clear": log["min_clear"],
        "final_state": log["state"][-1] if log["state"] else "?",
    }
    log["obstacles"] = obstacles
    log["walls"] = walls
    return log


def summarize(log):
    r = log["result"]
    verdict = []
    verdict.append("CARPISTI!" if r["collided"]
                   else f"temiz (min {r['min_clear']:.2f} m)")
    verdict.append("engeli GECTI" if r["passed"] else "engeli GECEMEDI")
    verdict.append("seride dondu" if r["returned"]
                   else f"seritten uzak (y={r['end'][1]:+.2f})")
    print(f"\n=== {r['label']} ===")
    print("  Sonuc:", " | ".join(verdict), f"| son durum: {r['final_state']}")
    for (t, st, ev) in log["events"]:
        print(f"  t={t:5.1f}s  {st:15s} {ev}")


def plot(logs, out_png):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("(matplotlib yok — grafik atlandi)")
        return
    n = len(logs)
    fig, axes = plt.subplots(n, 1, figsize=(11, 3.2 * n), squeeze=False)
    for ax, log in zip((a for row in axes for a in row), logs):
        r = log["result"]
        ax.axhline(0, color="0.7", ls="--", lw=1)      # sag serit merkezi (biz)
        ax.axhline(3.0, color="0.8", ls="--", lw=1)    # sol serit merkezi
        ax.axhline(1.5, color="0.85", lw=1)            # serit cizgisi
        ax.axhline(-1.5, color="0.85", lw=1); ax.axhline(4.5, color="0.85", lw=1)
        for ob in log["obstacles"]:
            if len(ob) == 4:
                ox, oy, ow, oh = ob
                ax.add_patch(mpatches.Rectangle((ox - ow / 2, oy - oh / 2),
                                                ow, oh, color="tab:red", alpha=0.8))
            else:
                ax.add_patch(mpatches.Circle((ob[0], ob[1]), ob[2],
                                             color="tab:red", alpha=0.8))
        for (x0, y0, x1, y1) in log["walls"]:
            ax.plot([x0, x1], [y0, y1], color="k", lw=3)
        ok = (not r["collided"]) and r["passed"]
        ax.plot(log["x"], log["y"], color="tab:green" if ok else "tab:orange", lw=2)
        ax.set_title(f"{r['label']} — "
                     f"{'CARPISTI' if r['collided'] else 'temiz'}, "
                     f"{'gecti' if r['passed'] else 'GECEMEDI'}, "
                     f"min klerans {r['min_clear']:.2f} m")
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
        ax.set_ylim(-3.2, 5.5); ax.set_aspect("equal", adjustable="datalim")
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_png, dpi=130)
    print(f"\nGrafik: {out_png}")


# PİST GEOMETRİSİ (carla-pist/pist_layout.json, 2026-08-03):
#   şerit genişliği 3.0 m; biz sağ şerit merkezinde (y=0), sol (karşı) şerit
#   merkezi y=+3.0; sağ yol kenarı bariyeri şerit kenarının ~0.5 m dışında
#   (y=-2.0). Pist slalom engeli: 1.4 x 1.4 m kutu, şerit ortasında.
BARRIER_R = [(2.0, -2.0, 30.0, -2.0)]     # sağ kenar bariyeri (eski senaryolar)

# --- GERÇEK PİST: iki yanda bariyer, arada iki şerit ----------------------
# 17.08.2026, CARLA koşusundan bulunan hata bu senaryolarla üretilir.
# Duvarlar aracın ARKASINDAN başlar (x=-5): gerçekte bariyer aracın yanında
# da vardır ve yan sektör SIDE_X_MIN=-2.51'den itibaren bakar. Eski
# BARRIER_R x=2.0'dan başlıyordu, yani araç hizasında duvar YOKTU — bu
# yüzden masa suiti 5/5 verirken CARLA'da araç kilitleniyordu.
DUVAR_SAG =  -PIST_SERIT / 2.0        # -1.48
DUVAR_SOL =  1.5 * PIST_SERIT         # +4.44 (SADECE karsilastirma icin)

# GERCEK PISTTE SADECE SAG BARIYER VAR (17.08.2026, operator duzeltmesi).
# Ilk kurulumda iki yana da duvar konmustu ve bulunan "arac acilyinca on
# koridor duvari goruyor" kilitlenmesi TAMAMEN o uydurma SOL duvardan
# kaynaklaniyordu. Sag bariyer araci saga kacmaktan alikoyar (senaryo icin
# gerekli); solda ise acik alan vardir.
PIST_DUVAR = [(-5.0, DUVAR_SAG, 60.0, DUVAR_SAG)]

# Iki yanli hali sadece "ya iki tarafi da kapali olsaydi" karsilastirmasi
# icin duruyor; varsayilan senaryolarda KULLANILMAZ.
PIST_DUVAR_IKI_YAN = PIST_DUVAR + [(-5.0, DUVAR_SOL, 60.0, DUVAR_SOL)]

# Araca gidecek ayarlar (launch dosyasiyla senkron tutulacak).
#   slalom_lateral_target 1.5 : engel yari-eni 0.65 + arac yari-eni 0.53 =
#     1.18 gerekli; 1.5 pay birakir. Beynin varsayilani 3.0 (tam serit
#     degisimi) 2.96 m'lik pistte 2. engelin ICINE goturur.
#   slalom_escape_steer varsayilan 75 (tam kilit) BIRAKILDI: 62 denendi,
#     kacis yetismeyip front 1.0'a dusuyor ve S1 bozuluyor. Dar pistteki
#     asil sorun donme acisi degil, ON KORIDORUN acilyken duvari gormesi;
#     onu front_trust_deg kapisi cozuyor.
PIST_PARAMS = {
    "slalom_lateral_target": 1.5,
    # Profil geldigi icin "kendi seridim acildi -> don" kapisi artik
    # guvenilir (eskiden sabit yan sektor bariyeri gorup hep 0 veriyordu).
    "return_home_when_free": True,
}

def pist_engelleri(n=3, ilk=12.0, ara=7.0, en=1.30, derinlik=0.5):
    """Dönüşümlü slalom dizisi: EGO şeridi -> KARŞI şerit -> EGO ...
    (yarışma düzeni: sağ-sol-sağ, 3 engel, 5-8 m arayla)."""
    return [(ilk + k * ara, 0.0 if k % 2 == 0 else PIST_SERIT, en, derinlik)
            for k in range(n)]
SCENARIOS = [
    # (etiket, engeller [(x,y,r) daire | (x,y,w,h) kutu], duvarlar)
    ("S1 pist engeli (1.4m kutu) -> tam serit degisimi",
     [(12.0, 0.0, 1.4, 1.4)], BARRIER_R, "pass"),
    ("S2 iki pist engeli arka arkaya (10 m ara)",
     [(12.0, 0.0, 1.4, 1.4), (22.0, 0.0, 1.4, 1.4)], BARRIER_R, "pass"),
    ("S3 sol seritte karsi arac var -> gecme, dur",
     [(12.0, 0.0, 1.4, 1.4), (13.0, 3.0, 4.5, 1.9)], BARRIER_R, "stop"),
    ("S4 yol tamamen kapali -> guvenli durmali",
     [(12.0, 0.0, 1.4, 1.4)],
     BARRIER_R + [(11.8, -2.0, 11.8, 4.5)], "stop"),
    # Gerçek alternasyonlu slalom: engel 1 SAĞ şeritte (bizim şerit),
    # engel 2 SOL şeritte. Beklenen: sola geç, engel 1'i geç; sol şeritteki
    # engel 2'yi görüp sağ şeride dön (dönülecek şerit boş — engel 1 geride
    # kaldı) ve engel 2'nin yanından kendi şeridimizden geç.
    ("S5 sagda engel -> sola gec; solda engel -> saga don",
     [(12.0, 0.0, 1.4, 1.4), (22.0, 3.0, 1.4, 1.4)], BARRIER_R, "pass"),

    # ---- GERCEK PIST (17.08.2026) — CARLA'daki kilitlenmeyi ureten senaryo
    # 2.96 m serit, IKI YANDA bariyer, 3 engel sag-sol-sag 7 m arayla.
    # CARLA'da olan: arac 1. engeli geciyor, yanal +1.18'de kaliyor, o anda
    # HER IKI yan sektor de duvara denk gelip 0 okuyor, "gidecek acik serit
    # YOK" deyip duruyor.
    ("P1 pist: 3 engel sag-sol-sag, 7 m ara, SAG bariyer",
     pist_engelleri(3, 12.0, 7.0), PIST_DUVAR, "pass"),
    ("P2 pist: dar aralik 5 m",
     pist_engelleri(3, 12.0, 5.0), PIST_DUVAR, "pass"),
    ("P3 pist: gecis serididin tamami kapali -> DURMALI",
     pist_engelleri(1, 12.0) + [(14.0, PIST_SERIT, 1.4, 8.0)],
     PIST_DUVAR, "stop"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-pkg", help="eski decision_brain kopyasinin paket dizini "
                                      "(karsilastirma icin)")
    ap.add_argument("--no-yaw", action="store_true",
                    help="yaw beslemesini kapat (yol-mesafesi yedegini test et)")
    ap.add_argument("--out", default=os.path.join(_HERE, "slalom_sim.png"))
    args = ap.parse_args()

    brains = [("YENI", Alkar_Function4)]
    if args.old_pkg:
        sys.path.insert(0, os.path.dirname(os.path.abspath(args.old_pkg)))
        pkg = os.path.basename(os.path.normpath(args.old_pkg))
        old_mod = __import__(f"{pkg}.decision_brain", fromlist=["Alkar_Function4"])
        brains.append(("ESKI", old_mod.Alkar_Function4))

    logs = []
    for tag, cls in brains:
        for (label, obstacles, walls, expect) in SCENARIOS:
            log = run_scenario(cls, obstacles, walls,
                               feed_yaw=not args.no_yaw,
                               label=f"[{tag}] {label}")
            log["result"]["expect"] = expect
            summarize(log)
            logs.append(log)
    plot(logs, args.out)

    # Genel karar: beklenti senaryo başına ("pass" = temiz geç + şeride dön,
    # "stop" = geçmeye kalkma, çarpışmadan güvenli dur)
    yeni = [l["result"] for l in logs if l["result"]["label"].startswith("[YENI]")]
    fails = []
    for r in yeni:
        if r["collided"]:
            fails.append(r)
        elif r["expect"] == "pass" and not (r["passed"] and r["returned"]):
            fails.append(r)
        elif r["expect"] == "stop" and r["passed"]:
            fails.append(r)
    print("\n" + ("TUM YENI-SENARYOLAR BASARILI"
                  if not fails else f"{len(fails)} senaryo BASARISIZ"))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
