#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUNEL (ustu-yanlari kapali kutu) KOORDINATLARI
==============================================
Kaynak: pist_final.pgm haritasindaki iki duvar. Duvarlar y=31.4..47.1
arasinda 100+ hucre/metre yogunlukla surekli; genislik boyunca 6.48-6.56 m
(cok kararli). Merkez cizgi bu iki duvarin ortasindan gecirildi.

DOGRULAMA: pist_17tem_2 bag'inde arac tunelden gecerken GNSS surekli akiyordu.
Aracin GNSS konumu tum gecis boyunca iki duvarin ARASINDA kaldi ve merkez
cizginin +1.5 m saginda seyretti -- bu, haritanin olculmus genel burulmasiyla
(medyan 1.54 m) ayni buyuklukte. Yani tunel duvarlari haritanin geri kalani
kadar dogru.

⚠️ LiDAR ile "tavan" tespiti giris/cikis icin KULLANILAMAZ: VLP-16'nin dikey
gorus alani ±15°, yani 3 m mesafede en fazla 0.8 m yukariyi gorur. Tavani
ancak 5-8 m ILERIDEN gorur, bu yuzden tavan sinyali portali ~4 m erken
baslatir. Giris/cikis duvarlardan alinmalidir.

Cikti: harita cercevesi + WGS84 + yarisma yerel cercevesi (x=Kuzey, y=Dogu).
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
RE = 6378137.0

# --- haritadan olculen tunel ---
EGIM, KESI = -0.1883, 64.426       # merkez: x = EGIM*y + KESI
Y_GIRIS, Y_CIKIS = 31.40, 47.10    # duvarlarin y araligi (harita cercevesi)
GENISLIK = 6.53


def merkez(yv):
    return np.array([EGIM * yv + KESI, yv])


def harita_to_wgs(mx, my):
    Rm, tm, la0, lo0 = yd.yukle()
    E, N = np.array([mx, my]) @ Rm + tm
    return la0 + math.degrees(N / RE), lo0 + math.degrees(E / (RE * math.cos(math.radians(la0))))


def main():
    g, c = merkez(Y_GIRIS), merkez(Y_CIKIS)
    eksen = math.degrees(math.atan2(c[1] - g[1], c[0] - g[0]))
    boy = float(np.linalg.norm(c - g))
    print(f'TUNEL: {boy:.2f} m uzunlugunda, {GENISLIK:.2f} m genisliginde')
    print(f'harita cercevesinde eksen yonu {eksen:+.2f}°  (giristen cikisa)\n')
    print(f'{"":<12}{"harita x":>10}{"harita y":>10}{"enlem":>13}{"boylam":>13}'
          f'{"yar. local_x":>14}{"yar. local_y":>14}')
    for ad, p in (('GIRIS', g), ('ORTA', (g + c) / 2), ('CIKIS', c)):
        la, lo = harita_to_wgs(p[0], p[1])
        yl = yd.harita_to_yerel(p[0], p[1])
        print(f'{ad:<12}{p[0]:10.2f}{p[1]:10.2f}{la:13.7f}{lo:13.7f}{yl[0]:14.2f}{yl[1]:14.2f}')

    # duvar uc noktalari (planlayici icin kutu)
    n = np.array([1.0, -EGIM]); n /= np.linalg.norm(n)     # eksene dik
    print(f'\nduvarlar (harita cercevesi):')
    kose = {}
    for ad, s in (('SOL', -1), ('SAG', +1)):
        for uc, p in (('giris', g), ('cikis', c)):
            q = p + s * (GENISLIK / 2) * n
            kose[f'{ad}_{uc}'] = q
            print(f'  {ad:<4} {uc:<6} ({q[0]:7.2f}, {q[1]:7.2f})')

    ozet = {'harita': {'giris': g.tolist(), 'cikis': c.tolist(),
                       'eksen_deg': eksen, 'uzunluk_m': boy, 'genislik_m': GENISLIK,
                       'koseler': {k: v.tolist() for k, v in kose.items()}},
            'wgs84': {ad: list(harita_to_wgs(*p)) for ad, p in (('giris', g), ('cikis', c))},
            'yarisma_yerel': {ad: yd.harita_to_yerel(*p).tolist()
                              for ad, p in (('giris', g), ('cikis', c))}}
    yol = _os.path.join(_BURA, 'tunel.json')
    json.dump(ozet, open(yol, 'w'), indent=2)
    print(f'\nyazildi: {yol}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
