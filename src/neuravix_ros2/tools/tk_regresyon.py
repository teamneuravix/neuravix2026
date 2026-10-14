#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEKNIK KONTROL REGRESYON TESTI  (masa, ROS'suz)
================================================
    python3 src/neuravix_ros2/tools/tk_regresyon.py

Kapsam (hepsi ARAC OLCUMUNE dayanir, bkz. CLAUDE.md "TEKNIK KONTROL" ve
"tk_0822 bag'leri" bolumleri):

  1. HEDEF yaklasmasi (5,4,1): slalom girisi bastirilir AMA lidar durmasi
     bozulmaz. Olculen tablo: front 2.5 m -> yavasla, 2.0 m -> DUR.
  2. Regresyon: ayni engel, yaklasma YOKKEN slalom yapilmali.
  3. HEDEF (5,4,0): surunerek yaklas; durusu lidar ya da creep butcesi verir.
  4. 5,4,2: hedef gecildi -> HEMEN dur (tk_0822'de surunme butcesi araci
     hedefi 2.4-4.5 m asirmisti).
  5. MISSION_END TERMINAL: serit / engel / tabela / planner donusu araci
     kaldiramaz; yalnizca hedef alt komutlari (cmd==4) muaf.
  6. Komutlu donus + engel: slalom YOK, durma esigi siki (1.0 m), kesilirse
     kalan sure saklanir ve yol acilinca donus TAMAMLANIR.
  7. Kapali cevrim donus: fazlari yaw bitirir. CIKIS hatasi olculur --
     caprazligi belirleyen odur (1418 -7.5 der toparladi, 1424 -14.7 toparlamadi).
  8. Yaw yoksa eski sure tabanli yol korunur (regresyon yok).

Cikis: 0 = hepsi gecti, 1 = en az bir madde kaldi.
"""
import math
import os
import sys
import time

_BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_BURA))          # .../src/neuravix_ros2

import neuravix_ros2.decision_brain as db                       # noqa: E402
from neuravix_ros2.decision_brain import Alkar_Function4, DriveState  # noqa: E402

_ok = 0
_fail = 0


def chk(ad, kosul, detay=""):
    global _ok, _fail
    if kosul:
        _ok += 1
    else:
        _fail += 1
        print(f"  FAIL  {ad}   {detay}")


def bekle(b, saniye, **kw):
    """Gercek saatle besle (onay sureleri duvar saatine bagli)."""
    t0 = time.time()
    while time.time() - t0 < saniye:
        b.obstacle_event(**kw)
        b.lane_detect_event(["2", "45"])
        b._update_state_machine()
        time.sleep(0.05)


# ----------------------------------------------------------------------
# Arac direksiyon dinamigi -- slalom_0822_1157 bag'inden kalibre edildi:
#   komut 73 (tam sol) -> yaw hizi ~2.5 s'de 9.5 der/s'ye tirmandi
#   komut 50 (toparlama) -> kararli ~4.5 der/s
# Dogrulama: bu modelle ESKI (sure tabanli) kod 7.3 s / +48 der veriyor,
# bag'de olculen 7.3 s / +46 der.
# ----------------------------------------------------------------------
KOMUT_HIZ = {73: 9.5, 50: 4.5, 45: 0.0, 17: -9.5, 40: -4.5}
SLEW = 4.0        # der/s^2, tekerlek hiz siniri


class _Saat:
    t = 0.0


def donus_kos(hedef, yaw_besle=True, dt=0.05, tmax=45.0):
    """Sahte saatle bir PLANNER_TURN kos. (cikis_hatasi, oturan_hata, sure)"""
    gercek = db.time.time
    db.time.time = lambda: _Saat.t
    try:
        _Saat.t = 1000.0
        b = Alkar_Function4()
        b.lane_detect_event(["2", "45"])
        if yaw_besle:
            b.update_motion(distance=0.0, yaw=0.0)
        b.planner_event(["5", "1", str(hedef)])
        yaw = 0.0
        yr = 0.0
        t = 0.0
        while t < tmax and b.state == DriveState.PLANNER_TURN:
            hz = KOMUT_HIZ.get(int(b.steering_angle), 0.0)
            yr += max(-SLEW * dt, min(SLEW * dt, hz - yr))
            yaw += math.radians(yr) * dt
            t += dt
            _Saat.t += dt
            if yaw_besle:
                b.update_motion(distance=t * 1.7, yaw=yaw)
            b._update_state_machine()
        cikis = math.degrees(yaw)
        for _ in range(int(3.5 / dt)):     # tekerlek merkeze donerken kalan donus
            yr += max(-SLEW * dt, min(SLEW * dt, -yr))
            yaw += math.radians(yr) * dt
        return cikis - hedef, math.degrees(yaw) - hedef, t
    finally:
        db.time.time = gercek


def main():
    print("1) HEDEF yaklasmasi: slalom bastirilir, LIDAR DURMASI calisir")
    beklenen = {99.0: 'LANE_FOLLOW', 5.5: 'LANE_FOLLOW', 4.0: 'LANE_FOLLOW',
                2.5: 'LANE_FOLLOW', 2.0: 'OBSTACLE_STOP', 1.0: 'OBSTACLE_STOP',
                0.0: 'OBSTACLE_STOP'}
    for front, bek in beklenen.items():
        b = Alkar_Function4()
        b.lane_detect_event(["2", "45"])
        b.planner_event(["5", "4", "1"])
        bekle(b, 0.7, front=front, left=99.0, right=99.0)
        chk(f"front={front} -> {bek}", b.state.name == bek, b.state.name)
        if front <= 2.0:
            chk(f"front={front} fren", b.brake == 1)
        else:
            chk(f"front={front} hiz tavani", b.target_speed <= b.hedef_speed + 1e-6,
                b.target_speed)

    print("2) Regresyon: yaklasma YOKKEN ayni engel slalom yapmali")
    b = Alkar_Function4()
    b.lane_detect_event(["2", "45"])
    bekle(b, 0.7, front=4.0, left=99.0, right=99.0)
    chk("slalom", b.state == DriveState.OBSTACLE_AVOID, b.state.name)

    print("3) HEDEF (5,4,0): surunerek yaklas, lidar/limit durdurur")
    b = Alkar_Function4()
    b.lane_detect_event(["2", "45"])
    b.update_motion(distance=0.0)
    b.planner_event(["5", "4", "1"])
    b.planner_event(["5", "4", "0"])
    b._update_state_machine()
    chk("MISSION_END", b.state == DriveState.MISSION_END, b.state.name)
    chk("suruniyor", 0 < b.target_speed <= b.hedef_speed, b.target_speed)
    b.update_motion(distance=1.5)
    b.obstacle_event(front=1.8, left=0.0, right=0.0)
    b._update_state_machine()
    chk("lidar durdurdu", b.target_speed == 0.0 and b.brake == 1)
    chk("hala MISSION_END", b.state == DriveState.MISSION_END, b.state.name)

    b = Alkar_Function4()
    b.lane_detect_event(["2", "45"])
    b.update_motion(distance=0.0)
    b.planner_event(["5", "4", "0"])
    b.obstacle_event(front=99.0, left=99.0, right=99.0)
    b.update_motion(distance=b.hedef_creep_m - 0.2)
    b._update_state_machine()
    chk("limit oncesi gidiyor", b.target_speed > 0, b.target_speed)
    b.update_motion(distance=b.hedef_creep_m + 0.2)
    b._update_state_machine()
    chk("creep limitinde durdu", b.target_speed == 0.0 and b.brake == 1, b.target_speed)

    b = Alkar_Function4()
    b.lane_detect_event(["2", "45"])
    b.planner_event(["5", "4", "0"])          # update_motion hic cagrilmadi
    b._update_state_machine()
    chk("odometrisiz -> guvenli dur", b.target_speed == 0.0 and b.brake == 1,
        b.target_speed)

    print("4) 5,4,2: hedef gecildi -> HEMEN dur")
    b = Alkar_Function4()
    b.lane_detect_event(["2", "45"])
    b.update_motion(distance=0.0)
    b.planner_event(["5", "4", "1"])
    b.planner_event(["5", "4", "0"])
    b._update_state_machine()
    chk("once suruniyor", b.target_speed > 0, b.target_speed)
    b.planner_event(["5", "4", "2"])
    b._update_state_machine()
    chk("5,4,2 -> hiz 0", b.target_speed == 0.0, b.target_speed)
    chk("5,4,2 -> fren", b.brake == 1)
    b.update_motion(distance=5.0)
    b._update_state_machine()
    chk("mesafe artsa da kalkmaz", b.target_speed == 0.0)

    b = Alkar_Function4()
    b.lane_detect_event(["2", "45"])
    b.planner_event(["5", "4", "2"])
    b._update_state_machine()
    chk("5,4,2 dogrudan da durdurur",
        b.state == DriveState.MISSION_END and b.target_speed == 0.0 and b.brake == 1,
        b.state.name)

    print("5) MISSION_END terminal")
    b.lane_detect_event(["2", "70"])
    chk("serit ezemez", b.state == DriveState.MISSION_END and b.target_speed == 0.0)
    b.obstacle_event(front=99.0, left=99.0, right=99.0)
    b._update_state_machine()
    chk("yol acilinca kalkmaz", b.state == DriveState.MISSION_END, b.state.name)
    b.sign_detect_event(["3", "17", "5.0", "0", "0", "40", "40"])   # YESIL_ISIK
    chk("yesil isik ezemez", b.state == DriveState.MISSION_END and b.target_speed == 0.0)
    b.planner_event(["5", "1", "70"])
    chk("planner donusu ezemez", b.state == DriveState.MISSION_END, b.state.name)
    b.planner_event(["5", "0", "0"])
    chk("iptal ezemez", b.state == DriveState.MISSION_END, b.state.name)
    b._update_state_machine()
    chk("dongu hala durduruyor", b.target_speed == 0.0 and b.brake == 1)

    print("6) Komutlu donus + engel")
    for front in (5.0, 4.0, 2.0, 1.5):
        b = Alkar_Function4()
        b.lane_detect_event(["2", "45"])
        b.planner_event(["5", "1", "70"])
        bekle(b, 1.2, front=front, left=99.0, right=99.0)
        chk(f"front={front}: donus suruyor (slalom/dur YOK)",
            b.state == DriveState.PLANNER_TURN, b.state.name)
    b = Alkar_Function4()
    b.lane_detect_event(["2", "45"])
    b.planner_event(["5", "1", "70"])
    time.sleep(0.4)
    b.obstacle_event(front=0.7, left=99.0, right=99.0)
    chk("cok yakin -> DUR", b.state == DriveState.OBSTACLE_STOP, b.state.name)
    chk("fren", b.brake == 1)
    chk("kalan sure saklandi", b._pturn_kalan is not None and b._pturn_kalan > 0,
        b._pturn_kalan)
    b.obstacle_event(front=99.0, left=99.0, right=99.0)
    b._update_state_machine()
    chk("yol acilinca donus TAMAMLANIYOR", b.state == DriveState.PLANNER_TURN,
        b.state.name)
    b._update_state_machine()
    chk("sola kiriyor", b.steering_angle > 45, b.steering_angle)
    b2 = Alkar_Function4()
    b2.lane_detect_event(["2", "45"])
    b2.planner_event(["5", "1", "70"])
    time.sleep(0.3)
    b2.obstacle_event(front=0.0, left=0.0, right=0.0)
    chk("fail-safe donuste de durdurur",
        b2.state == DriveState.OBSTACLE_STOP and b2.brake == 1, b2.state.name)

    print("7) Kapali cevrim donus -- CIKIS hatasi (caprazligi bu belirler)")
    for h in (40.0, 70.0, 90.0, 110.0, -70.0, -90.0):
        cikis, oturan, sure = donus_kos(h)
        chk(f"donus {h:+.0f}: cikis {cikis:+.1f} der", abs(cikis) < 3.0, f"{cikis:+.1f}")
        chk(f"donus {h:+.0f}: oturan {oturan:+.1f} der", abs(oturan) < 3.0,
            f"{oturan:+.1f}")

    print("8) Yaw YOKSA eski sure tabanli yol korunur")
    cikis, oturan, sure = donus_kos(70.0, yaw_besle=False)
    chk("sure ~7.3 s", 6.8 < sure < 7.8, f"{sure:.1f}")

    print()
    print(f"SONUC: {_ok} gecti, {_fail} kaldi")
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
