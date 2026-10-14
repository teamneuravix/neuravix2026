#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YARISMA HEADING KONVANSIYONU DENETIMI
=====================================
geojson'daki 'heading' alaninin Kuzey'den SAAT YONUNDE mi (pusula) yoksa
Dogu'dan saat yonunun TERSINE mi (matematik/ENU) olculdugu belirsizdi.

Yontem: biz bu pistte zaten tur attik. start ve hedef noktalarinin harita
karsiliklarina en yakin gectgimiz yerlerdeki KENDI yaw'imiz, dogru
konvansiyonun verdigi aciya yakin cikmali (ayni yon ya da tam ters -- pist
iki yonlu surulmus olabilir, o yuzden 180 katlarina da bakiyoruz).
"""
import math, json, importlib.util
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



spec = importlib.util.spec_from_file_location('yd', _bul(
    _os.path.join(_BURA, 'yarisma_donusum.py'),
    '/home/balman/neuravix_exp/yarisma_donusum.py'))
yd = importlib.util.module_from_spec(spec); spec.loader.exec_module(yd)
Rm, _, _, _ = yd.yukle()
ACI = math.degrees(math.atan2(Rm[1, 0], Rm[0, 0]))

P = np.load(_bul(_os.path.join(_BURA, 'yer_tanima_db.npz'),
                 '/home/balman/neuravix_exp/analiz/yt_db_genis_duz.npz'))['POZ']
G = json.load(open(_os.path.join(_BURA, 'teknik_kontrol.geojson')))


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


print(f'harita<-ENU donme acisi: {ACI:.2f}°\n')
print(f'{"nokta":<8}{"h":>8}{"A pusula":>10}{"B ENU":>10}{"bizim yaw":>11}'
      f'{"|A-biz|":>9}{"|B-biz|":>9}{"yakinlik":>10}')
for f in G['features']:
    p = f['properties']
    if p['name'] == 'datum':
        continue
    m = yd.yerel_to_harita(p['local_x'], p['local_y'])
    h = p['heading']
    A = wrap(90.0 - h + ACI)          # pusula: Kuzey'den saat yonunde
    B = wrap(h + ACI)                 # ENU: Dogu'dan saat yonu tersine
    d = np.hypot(P[:, 0] - m[0], P[:, 1] - m[1])
    k = np.argsort(d)[:40]            # en yakin 40 poz
    yaw = math.degrees(math.atan2(np.sin(P[k, 2]).mean(), np.cos(P[k, 2]).mean()))
    # pist iki yonlu surulmus olabilir -> 180'e mod hata
    eA = min(abs(wrap(A - yaw)), abs(wrap(A - yaw + 180)))
    eB = min(abs(wrap(B - yaw)), abs(wrap(B - yaw + 180)))
    print(f'{p["name"]:<8}{h:8.2f}{A:10.2f}{B:10.2f}{yaw:11.2f}'
          f'{eA:9.1f}{eB:9.1f}{d[k].mean():9.2f} m')
