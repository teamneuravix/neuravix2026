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
MAX_DELTA   = math.radians(31.25)     # tam kilit eşdeğer ön teker açısı
HALF_WIDTH  = 0.53                    # m (body_width 1.06 / 2)


class Vehicle:
    def __init__(self, x=0.0, y=0.0, yaw=0.0):
        self.x, self.y, self.yaw = x, y, yaw
        self.v = 0.0          # m/s
        self.dist = 0.0       # katedilen yol (m)

    def step(self, steer_alkar, target_kmh, brake, dt):
        target_v = 0.0 if brake else target_kmh / 3.6
        tau = 0.35 if (brake or target_v < self.v) else 1.2   # fren/yavaşlama hızlı
        self.v += (target_v - self.v) * min(1.0, dt / tau)
        if self.v < 0.02 and target_v == 0.0:
            self.v = 0.0
        delta = (float(steer_alkar) - 45.0) / 30.0 * MAX_DELTA
        self.yaw += self.v / WHEELBASE * math.tan(delta) * dt
        self.x += self.v * math.cos(self.yaw) * dt
        self.y += self.v * math.sin(self.yaw) * dt
        self.dist += self.v * dt


# ================================================================
# Sanal lidar — obstacle_lidar_node.py ile AYNI sektör geometrisi
# (side_offset=3.0 / side_corridor=1.5: 2026-08-03 pist ölçüsü güncellemesi)
# ================================================================
CORRIDOR   = 0.70
SIDE_OFF   = 3.0      # komşu şerit merkezi (pist şerit genişliği 3.0 m)
SIDE_CORR  = 1.5      # yan koridor yarı genişliği
BUMPER     = 0.233
X_MIN      = 0.5
SIDE_X_MIN = -2.51
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
def run_scenario(brain_cls, obstacles, walls=(), T=60.0, dt=0.05,
                 feed_yaw=True, label=""):
    veh = Vehicle()
    brain = brain_cls()
    clock = {"t": 0.0}
    brain._now = lambda: clock["t"]        # beyin duvar saatine değil sim saatine baksın

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
            brain.obstacle_event(front=f, left=l, right=r)
            next_obs += 0.1

        # ~20 Hz şerit algısı
        brain.lane_detect_event([2, lane_steer_proxy(veh)])

        # 20 Hz kontrol döngüsü (control_loop eşdeğeri)
        try:
            if feed_yaw:
                brain.update_motion(distance=veh.dist, yaw=veh.yaw)
            else:
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
BARRIER_R = [(2.0, -2.0, 30.0, -2.0)]     # sağ kenar bariyeri
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
