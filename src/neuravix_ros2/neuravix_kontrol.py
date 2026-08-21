#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SADECE CARLA SİMÜLASYONU - gerçek araca taşınmayacak.
`carla.Client` API'sine doğrudan bağlanan bağımsız bir test scriptidir (ROS
node/console_script değildir); ROS köprüsü/karar node'u ÇALIŞMIYORKEN elle
çalıştırılır. Gerçek yarışta kullanılan pipeline neuravix_control_node_real.py
+ decision_brain.py'dir.

Pist Misyon - Koordinat Tabanli Otonom Surus (pure-pursuit)
============================================================
Algilama/FSM YOK. Onceden tanimli waypoint rotasini takip eder:
  1. Baslar (H3 ust yol, batiya)
  2. Engeli (x=63) SLALOM ile ge+ tekrar sag seride doner
  3. sola_don tabelasinin oldugu kavsaktan (J108, x=26) SOLA doner
  4. V1'de tunele girer
  5. Tunelin karsisindaki duraga (D-ic ~53.5,36.5) gider, 3 sn DURUR
  6. Park alanina yonelir, "park yapilabilir" slotta (78,59) PARK eder

Koordinatlar pist_layout.json ile ayni (OpenDRIVE). CARLA'ya (x, -y) cevrilir.
ROUTE listesini duzenleyerek rotayi degistirebilirsin.

ONCE: CARLA + load_pist_world (+ istege bagli spawn_pist_props) calismis olmali.
Bu script aracı KENDISI surer (bridge/kontrol node CALISMASIN - cakisir).

Kullanim:
    python3 pist_misyon_otonom.py
    python3 pist_misyon_otonom.py --spawn   # ego yoksa kendi spawn etsin
"""
import argparse
import math
import sys
import time

try:
    import carla
except ImportError:
    sys.exit("carla paketi yok")


# ===========================================================================
# ROTA (pist/OpenDRIVE koordinati). speed = m/s. action: None/"slow"/"stop3"/"park"
# ===========================================================================
ROUTE = [
    # --- 1) Baslangic + ENGEL SLALOM (H3 bati, SAG serit y=70; engel x=63) ---
    dict(x=72.0, y=70.0, speed=4.0, durum="SERIT_TAKIP", sebep="baslangic - H3 bati, sag serit"),
    dict(x=67.0, y=70.0, speed=3.0),
    dict(x=64.0, y=66.0, speed=2.5, durum="ENGEL_SLALOM", sebep="engel x=63 - sol seride kac"),
    dict(x=60.0, y=66.0, speed=2.5),   # engeli gec
    dict(x=56.0, y=70.0, speed=2.5, durum="SERIT_TAKIP", sebep="engel gecildi - sag seride don"),
    dict(x=45.0, y=70.0, speed=4.0),
    dict(x=34.0, y=70.0, speed=3.5),

    # --- 2) sola_don -> J108 SOLA DON -> V1 GUNEY, SAG serit x=24 ---
    dict(x=29.0, y=70.0, speed=2.5),
    dict(x=25.0, y=64.0, speed=2.0, durum="SOLA_DON", sebep="J108 sola don tabelasi - guneye don"),
    dict(x=24.0, y=55.0, speed=3.0),

    # --- 3) V1 TUNEL (merkez-guvenli x~25.5) ---
    dict(x=24.5, y=45.0, speed=2.5),
    dict(x=25.5, y=36.5, speed=2.0, action="slow", durum="TUNEL", sebep="tunel - yavasla, duz git"),
    dict(x=24.0, y=30.0, speed=2.5),

    # --- 4) GUNEYE devam -> ALT DIS DURAK (D-alt, x=26 alt cep), PARALEL dur ---
    dict(x=24.0, y=20.0, speed=3.0, durum="SERIT_TAKIP", sebep="V1 guneye - duraga dogru"),
    dict(x=25.0, y=9.0,  speed=2.0),
    dict(x=28.0, y=4.0,  speed=1.5, durum="DURAGA_YANAS", sebep="alt durak - cebe paralel yanas"),
    dict(x=30.0, y=3.5,  speed=1.2, action="stop3", durum="DURAK", sebep="DURAK - 3 sn dur"),

    # --- 5) H0 DOGU (sag serit y=3.5) -> SE kose SOLA -> V3 KUZEY (sag serit x=70) ---
    dict(x=42.0, y=3.5,  speed=3.5, durum="SERIT_TAKIP", sebep="H0 doguya, sag serit"),
    dict(x=58.0, y=3.5,  speed=3.5),
    dict(x=64.0, y=4.0,  speed=2.0, durum="SOLA_DON", sebep="SE kose sola don tabelasi - kuzeye don"),
    dict(x=70.0, y=10.0, speed=2.0),
    dict(x=70.0, y=30.0, speed=3.5, durum="SERIT_TAKIP", sebep="V3 kuzeye, sag serit"),
    dict(x=70.0, y=50.0, speed=2.5),

    # --- 5b) PARK: V3'ten DOGUYA direkt slot'a PARALEL gir (aisle/geri YOK) ---
    dict(x=70.0, y=58.5, speed=1.8, durum="PARK_MANEVRA", sebep="park alanina paralel girilecek"),
    dict(x=74.0, y=59.0, speed=1.3),   # SAGA (doguya) don -> park alanina gir
    dict(x=78.0, y=59.0, speed=1.0, action="park", durum="PARK", sebep="PARK YAPILABILIR slot - tamamlandi"),
]

REACH = 3.0          # waypoint'e bu kadar yaklasinca sonrakine gec (m)
STEER_GAIN = 1/45.0  # heading hatasi -> direksiyon
SPAWN = dict(x=72.0, y=69.5, z=0.5, yaw=180.0)   # pist_layout spawn


# pist(OpenDRIVE) -> CARLA y cevirimi. Cogu kurulumda y NEGATIFLENIR.
# Arac ters yone giderse --no-flip ile kapat (bazi haritalar flip'siz).
FLIP_Y = True


def pist_to_carla_loc(x, y, z=0.0):
    return carla.Location(x=x, y=(-y if FLIP_Y else y), z=z)


def find_or_spawn_ego(world, do_spawn):
    # 1) Mevcut ego var mi - birkac kez dene (yeni baglandiysa gec kaydolur)
    for _ in range(6):
        vehs = list(world.get_actors().filter("vehicle.*"))
        for a in vehs:
            if a.attributes.get("role_name") in ("ego_vehicle", "hero", "ego"):
                #print(f"[ego] mevcut ego bulundu: {a.type_id} id={a.id}")
                return a, False
        if vehs:
            # role eslesmedi ama ARAC VAR -> ilkini kullan (tek arac varsa o ego'dur)
            a = vehs[0]
            #print(f"[ego] role eslesmedi; ilk arac kullaniliyor: {a.type_id} "
            #f"role='{a.attributes.get('role_name', '')}' id={a.id}")
            return a, False
        time.sleep(0.5)

    if not do_spawn:
        #print("[ego] mevcut arac yok. KENDI koymak icin: python3 ... --spawn")
        return None, False

    bp = world.get_blueprint_library().filter("vehicle.micro.microlino")
    bp = bp[0] if bp else world.get_blueprint_library().filter("vehicle.*")[0]
    bp.set_attribute("role_name", "ego_vehicle")

    # Spawn etrafindaki PROP'lari (bariyer vs) temizle -> arac uzerine binmesin.
    # 4 m yaricap: spawn noktasindaki perimetre/bariyer parcalarini siler;
    # engel (x=63, ~9 m uzak) ETKILENMEZ, slalom icin durur.
    want = pist_to_carla_loc(SPAWN["x"], SPAWN["y"], 0.5)
    cleared = 0
    for a in world.get_actors():
        if ("prop" in a.type_id) and a.get_location().distance(want) < 4.0:
            try:
                a.destroy(); cleared += 1
            except Exception:
                pass
    #if cleared:
        #print(f"[ego] spawn etrafindaki {cleared} prop temizlendi (arac binmesin)")

    # 2) Istenen spawn noktasinda, ALCAK z'den basla (yuksek z = dususte burun kalkar)
    for z in (0.3, 0.5, 1.0, 2.0):
        tf = carla.Transform(
            pist_to_carla_loc(SPAWN["x"], SPAWN["y"], z),
            carla.Rotation(yaw=-SPAWN["yaw"]))
        ego = world.try_spawn_actor(bp, tf)
        if ego is not None:
            print(f"[ego] spawn @ ({SPAWN['x']},{SPAWN['y']},z={z}) yaw={SPAWN['yaw']}")
            return ego, True

    # 3) Cakisma surdu -> haritanin gecerli spawn noktalarindan EN YAKIN'i dene
    #print("[ego] istenen noktada cakisma; harita spawn noktasi deneniyor...")
    want = pist_to_carla_loc(SPAWN["x"], SPAWN["y"], 0.5)
    sps = world.get_map().get_spawn_points()
    sps.sort(key=lambda sp: sp.location.distance(want))
    for sp in sps[:10]:
        ego = world.try_spawn_actor(bp, sp)
        if ego is not None:
            #print(f"[ego] harita spawn noktasinda kuruldu @ "
            #f"({sp.location.x:.1f}, {sp.location.y:.1f})")
            return ego, True

    #print("[ego] HICBIR noktada spawn edilemedi. Once mevcut araclari/prop'lari "
          #"temizle (spawn_pist_props.py --clean) veya SPAWN konumunu degistir.")
    return None, False


def follow_spectator(world, ego_tf):
    spec = world.get_spectator()
    fwd = ego_tf.get_forward_vector()
    loc = ego_tf.location
    spec.set_transform(carla.Transform(
        carla.Location(x=loc.x - fwd.x * 8.0, y=loc.y - fwd.y * 8.0, z=loc.z + 5.0),
        carla.Rotation(pitch=-15.0, yaw=ego_tf.rotation.yaw)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=2000)
    ap.add_argument("--spawn", action="store_true", help="ego yoksa kendi spawn et")
    ap.add_argument("--cleanup", action="store_true",
                    help="cikista spawn edilen araci sil (varsayilan: silme, kalsin)")
    ap.add_argument("--no-flip", action="store_true",
                    help="pist->CARLA y NEGATIFLEME (arac ters yone giderse kullan)")
    ap.add_argument("--no-spectator", action="store_true")
    args = ap.parse_args()

    global FLIP_Y
    FLIP_Y = not args.no_flip

    client = carla.Client(args.host, args.port)
    client.set_timeout(15.0)
    world = client.get_world()
    #print(f"[carla] Map: {world.get_map().name}")

    ego, spawned = find_or_spawn_ego(world, args.spawn)
    if ego is None:
        return

    # --- TESHIS: arac konumu vs ilk waypoint hedefi (flip dogru mu?) ---
    el = ego.get_location()
    w0 = ROUTE[0]
    t0 = pist_to_carla_loc(w0["x"], w0["y"])
    d0 = math.hypot(t0.x - el.x, t0.y - el.y)
    #print(f"[teshis] arac CARLA konumu: ({el.x:.1f}, {el.y:.1f})")
    #print(f"[teshis] WP0 hedef CARLA  : ({t0.x:.1f}, {t0.y:.1f})  (flip_y={FLIP_Y})")
    #print(f"[teshis] aradaki mesafe   : {d0:.1f} m")
    if d0 > 25.0:
        #print("[teshis] !! Arac ile rota basi COK UZAK. y-flip muhtemelen ters.")
        #print("         --no-flip ile (veya flip'siz calisiyorsan flip'li) tekrar dene.")
        pass

    idx = 0
    wait_until = 0.0
    parked = False
    cur_durum = None
    #print(f"[misyon] {len(ROUTE)} waypoint - basliyor.")

    def log_karar(durum, sebep, steer_deg, speed, tgt):
        # neuravix_control_node'daki [KARAR] cikti tarzi - durum degisince basar
        print(f"[KARAR] durum={durum} | steer={steer_deg} "
              f"hiz={speed:.1f}/{tgt:.1f} | sebep: {sebep}")

    try:
        while True:
            now = time.time()
            tf = ego.get_transform()
            loc = tf.location
            vel = ego.get_velocity()
            speed = math.hypot(vel.x, vel.y)   # m/s

            if not args.no_spectator:
                follow_spectator(world, tf)

            # --- PARK bitti: dur, el freni ---
            if parked:
                ego.apply_control(carla.VehicleControl(
                    throttle=0.0, brake=1.0, hand_brake=True))
                time.sleep(0.05)
                continue

            # --- DURAK beklemesi ---
            if now < wait_until:
                ego.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))
                time.sleep(0.05)
                continue

            wp = ROUTE[idx]
            tx, ty = wp["x"], -wp["y"]   # CARLA
            dx, dy = tx - loc.x, ty - loc.y
            dist = math.hypot(dx, dy)

            # --- Pure-pursuit direksiyon ---
            target_yaw = math.degrees(math.atan2(dy, dx))
            err = (target_yaw - tf.rotation.yaw + 180.0) % 360.0 - 180.0
            steer = max(-1.0, min(1.0, err * STEER_GAIN))
            steer_deg = int(45 - steer * 45)   # 0-90 (45=duz, >45 sol, <45 sag)

            # --- DURUM degisince [KARAR] yaz (neuravix_control tarzi) ---
            durum = wp.get("durum")
            if durum and durum != cur_durum:
                cur_durum = durum
                log_karar(durum, wp.get("sebep", ""), steer_deg, speed,
                          wp.get("speed", 3.0))

            # --- Waypoint'e ulasildi mi ---
            if dist < REACH:
                act = wp.get("action")
                if act == "stop3":
                    print(f"[KARAR] durum=DURAK | steer={steer_deg} hiz=0.0 | "
                          f"sebep: duraga ulasildi -> 3 sn DUR")
                    wait_until = now + 3.0
                    idx += 1
                    continue
                if act == "park":
                    print(f"[KARAR] durum=PARK | steer={steer_deg} hiz=0.0 | "
                          f"sebep: park slotuna ulasildi -> TAMAMLANDI")
                    parked = True
                    continue
                idx += 1
                if idx >= len(ROUTE):
                    print("[misyon] rota bitti, duruluyor.")
                    parked = True
                continue

            # --- Hiz kontrolu (basit P) ---
            tgt = wp.get("speed", 3.0)
            if wp.get("action") == "slow":
                tgt = min(tgt, 2.0)
            throttle, brake = 0.0, 0.0
            if speed > tgt + 1.0:
                brake = 0.3
            else:
                throttle = max(0.0, min(0.5, 0.35 * (tgt - speed)))

            ego.apply_control(carla.VehicleControl(
                throttle=float(throttle), steer=float(steer), brake=float(brake)))
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nPark Yapildi. Pist görevi tamamlandi.")
    finally:
        # Araci DURDUR ama SILME -> tekrar calistirinca bulunur, pencerede kalir.
        # Silmek istersen: --cleanup ile calistir.
        try:
            ego.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0,
                                                   hand_brake=True))
        except Exception:
            pass
        if spawned and args.cleanup:
            time.sleep(0.3)
            try:
                ego.destroy()
                print("[ego] arac silindi (--cleanup).")
            except Exception:
                pass


if __name__ == "__main__":
    main()
