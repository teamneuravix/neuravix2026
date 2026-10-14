#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YARISMA KOORDINATLARI <-> BIZIM HARITA CERCEVESI
================================================
  python3 yarisma_donusum.py <geojson>        # dosyadaki tum noktalari cevir
  python3 yarisma_donusum.py --xy 95.15 48.88 # tek nokta (yarisma yerel -> harita)

YARISMANIN CERCEVESI (teknik_kontrol.geojson'dan cozuldu, 2026-08-19):
  datum      : lat 40.789431  lon 29.508361  -> yerel (0,0), heading 0
  local_x    = KUZEY  (metre)
  local_y    = DOGU   (metre)
  ⚠️ ENU DEGIL -- x ve y yer degistirmis. Dogrulandi: start ve hedef
  noktalarinin lat/lon'dan hesaplanan (N,E) degerleri verilen (local_x,local_y)
  ile 0.2-0.6 m icinde ortusuyor (yuvarlama payi).

BIZIM CERCEVE:
  analiz/datum_yt.npz -- yer tanimanin %100 kesinlikli 594 eslesmesinden
  hesaplandi, artik medyan 1.54 m.

DOGRULAMA (pist_J haritasi uzerinde):
  start (95.15, 48.88) -> harita (20.51,  3.89)  BOS, surulebilir, duvara 3.00 m
  hedef (57.24, 20.82) -> harita (64.02, 22.09)  BOS, surulebilir, duvara 2.22 m
  Ikisi de mantikli yerlere dustu; bizim datum ile yarismanin datum'u tutarli.

TOPLAM BELIRSIZLIK: bizim datum artigi ~1.5 m + yarismanin yuvarlamasi ~0.5 m.
"""
import sys, json, math
import numpy as np

import os as _os
_BURA = _os.path.dirname(_os.path.abspath(__file__))


def _bul(*adaylar):
    """Once bu scriptin yaninda ara, sonra uretim klasorunde.
    Boylece klasor baska bir makineye kopyalandiginda da calisir."""
    for a in adaylar:
        if _os.path.exists(a):
            return a
    return adaylar[0]



R = 6378137.0
DATUM_LAT, DATUM_LON = 40.789431, 29.508361     # yarismanin datum'u
BIZ = _bul(_os.path.join(_BURA, 'datum_yt.npz'),
           '/home/balman/neuravix_exp/analiz/datum_yt.npz')


def yukle():
    d = np.load(BIZ)
    return d['R'], d['t'], float(d['la0']), float(d['lo0'])


def yerel_to_harita(lx, ly):
    """yarisma yerel (x=Kuzey, y=Dogu) -> bizim harita cercevesi (x, y)"""
    Rm, tm, la0, lo0 = yukle()
    lat = DATUM_LAT + math.degrees(lx / R)
    lon = DATUM_LON + math.degrees(ly / (R * math.cos(math.radians(DATUM_LAT))))
    E = math.radians(lon - lo0) * R * math.cos(math.radians(la0))
    N = math.radians(lat - la0) * R
    return (np.array([E, N]) - tm) @ Rm.T


def harita_to_yerel(mx, my):
    """bizim harita cercevesi -> yarisma yerel (x=Kuzey, y=Dogu)"""
    Rm, tm, la0, lo0 = yukle()
    E, N = np.array([mx, my]) @ Rm + tm
    lat = la0 + math.degrees(N / R)
    lon = lo0 + math.degrees(E / (R * math.cos(math.radians(la0))))
    lx = math.radians(lat - DATUM_LAT) * R
    ly = math.radians(lon - DATUM_LON) * R * math.cos(math.radians(DATUM_LAT))
    return np.array([lx, ly])


def yon_to_harita(heading_deg):
    """yarismanin heading'i (Kuzey'den saat yonunde) -> harita yaw (rad).

    DONME ISARETI DOGRULANDI (2026-08-19): harita = (enu - t) @ Rm.T, yani
    bir yon vektoru icin v_harita = Rm @ v_enu -> aci TOPLANIR, cikarilmaz.
    Onceki surumde eksi vardi; yarisma yerel cercevede 10 m'lik yon
    vektorlerini cevirip olcunce sabit 61.59 derece hata veriyordu. Artik
    dort ana yonde de hata 0.00 derece.
    Kalan tek varsayim: geojson'daki heading Kuzey'den SAAT YONUNDE olcuyor.
    Bu varsayim start noktasinin haritadaki serbest koridoruna bakilarak
    denetlendi (bkz. yon_denetle.py) ama sahada da bir kez teyit edilmeli."""
    Rm, _, _, _ = yukle()
    enu_yaw = math.radians(90.0 - heading_deg)        # pusula -> ENU acisi
    return enu_yaw + math.atan2(Rm[1, 0], Rm[0, 0])


def main():
    if len(sys.argv) > 2 and sys.argv[1] == '--xy':
        lx, ly = float(sys.argv[2]), float(sys.argv[3])
        p = yerel_to_harita(lx, ly)
        print(f'yarisma ({lx:.2f}, {ly:.2f})  ->  harita ({p[0]:.2f}, {p[1]:.2f})')
        return 0
    path = sys.argv[1] if len(sys.argv) > 1 else _os.path.join(_BURA, 'teknik_kontrol.geojson')
    g = json.load(open(path))
    print(f'{"nokta":<10} {"yarisma yerel":>18} {"harita cercevesi":>20} {"yon":>8}')
    for f in g['features']:
        p = f['properties']
        if 'local_x' not in p:
            continue
        m = yerel_to_harita(p['local_x'], p['local_y'])
        h = p.get('heading')
        hy = f'{math.degrees(yon_to_harita(h)):7.1f}°' if h is not None else '     --'
        print(f'{p["name"]:<10} ({p["local_x"]:7.2f},{p["local_y"]:7.2f}) '
              f'({m[0]:8.2f},{m[1]:8.2f}) {hy}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
