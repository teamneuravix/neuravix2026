#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lokal bag'leri icin puanlama.  python3 puanla_lokal.py TAG:BAG ..."""
import sys, sqlite3, math, csv, os
import numpy as np
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import NavSatFix

#   BAG_DIR   : cozulmus .db3 dosyalarinin bulundugu klasor
#   DATUM_NPZ : varsayilan <script>/../datum_yt.npz
#   OUT       : run_lokal3.sh ile ayni cikti klasoru
S = os.environ.get('BAG_DIR', '.').rstrip('/') + '/'
_BURA = os.path.dirname(os.path.abspath(__file__))
_DATUM = os.environ.get('DATUM_NPZ', os.path.join(_BURA, '..', 'datum_yt.npz'))
OUT = os.environ.get('OUT', '/tmp/loc')
z = np.load(_DATUM)
R, t, la0, lo0 = z['R'], z['t'], float(z['la0']), float(z['lo0'])
RE = 6378137.0
_g = {}


def gnss(b):
    if b in _g:
        return _g[b]
    c = sqlite3.connect(S + b + '.db3').cursor()
    tp = {n: i for i, n in c.execute('select id,name from topics')}
    G = []
    for ts, d in c.execute('select timestamp,data from messages where topic_id=? order by timestamp',
                           (tp['/gnss'],)):
        m = deserialize_message(d, NavSatFix)
        if not math.isfinite(m.latitude):
            continue
        E = math.radians(m.longitude - lo0) * RE * math.cos(math.radians(la0))
        N = math.radians(m.latitude - la0) * RE
        G.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9,
                  *((np.array([E, N]) - t) @ R.T)))
    _g[b] = np.array(G)
    return _g[b]


def main():
    print(f'{"kosu":<10}{"n":>6}{"medyan":>9}{"%90":>8}{"maks":>8}   '
          f'{"DURURKEN":>10}{"HAREKETTE":>11}   tohum')
    for arg in sys.argv[1:]:
        tag, b = arg.split(':')
        G = gnss(b)
        v = np.r_[0, np.hypot(np.diff(G[:, 1]), np.diff(G[:, 2])) / np.diff(G[:, 0])]
        P = []
        yol = f'{OUT}/{tag}_poz.csv'
        if not os.path.exists(yol):
            print(f'{tag:<10} (dosya yok)'); continue
        with open(yol) as f:
            for r in csv.reader(f):
                try: P.append((float(r[0]), float(r[1]), float(r[2])))
                except (ValueError, IndexError): pass
        P = np.array(P)
        e, hz = [], []
        for T, x, y in P:
            k = int(np.argmin(np.abs(G[:, 0] - T)))
            if abs(G[k, 0] - T) > 0.3:
                continue
            e.append(math.hypot(x - G[k, 1], y - G[k, 2])); hz.append(v[k])
        e = np.array(e); hz = np.array(hz)
        # ilk 20 s: AMCL varsayilan pozdan geliyor, gozetmenin oturtmasi icin pay
        m = (np.array([T for T, _, _ in P][:len(e)]) - P[0, 0]) > 20
        e, hz = e[m], hz[m]
        dur = e[hz < 0.1]; har = e[hz >= 0.1]
        log = f'{OUT}/{tag}_loc.log'
        th = sum(1 for l in open(log, errors='ignore') if 'YENIDEN TOHUMLAMA' in l) \
             if os.path.exists(log) else -1
        f2 = lambda a: f'{np.median(a):.2f}' if len(a) else '  --'
        print(f'{tag:<10}{len(e):>6}{np.median(e):>8.2f}m{np.percentile(e,90):>7.2f}{e.max():>8.2f}   '
              f'{f2(dur):>10}{f2(har):>11}   {th}')


if __name__ == '__main__':
    raise SystemExit(main())
