#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tabela_tespit_node'un DERINLIK -> MESAFE yolunu ROS grafigi olmadan sinar.

Calistirma (workspace kokunden):
    python3 src/neuravix_ros2/tools/derinlik_mesafe_testi.py

Dugum ornegi `object.__new__` ile kuruluyor: rclpy init, kamera, model ya da
CARLA/ZED gerekmez -- sinanan sey saf mesafe mantigi. Amac, arac gununde ilk
kez denenen bir kod yolu birakmamak.
"""
import os, sys, numpy as np
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))          # .../src/neuravix_ros2

from neuravix_ros2.tabela_tespit_node import TabelaTespitNode, Detection   # noqa: E402
from neuravix_ros2.decision_brain import DUR, KIRMIZI_ISIK                 # noqa: E402

W, H = 1280, 720
gecti = basarisiz = 0


class _Logger:
    def warn(self, *a, **k): pass
    def info(self, *a, **k): pass
    def error(self, *a, **k): pass


def dugum(**over):
    n = object.__new__(TabelaTespitNode)
    n.get_logger = lambda: _Logger()
    n._warn_times = {}
    n.depth_topic = '/test/depth'
    n.use_depth = True
    n.depth_max_age = 0.15
    n.depth_roi_ratio = 0.5
    n.depth_min_valid_ratio = 0.15
    n.depth_min_m, n.depth_max_m = 0.4, 40.0
    n.camera_to_bumper = 0.0
    n.allow_bbox_fallback = True
    n.distance_constant, n.light_distance_constant = 362.0, 218.0
    n.depth_buffer_size = 10
    n.depth_buf = deque(maxlen=10)
    n.depth_msg_count = 0
    n.depth_qos_depth = 10
    n._olculen = 0
    n._yedege_dusen = 0
    n._son_rapor = 0.0
    n.start_time = 0.0
    # Kolaylik: depth_frame= / depth_stamp= verilirse halka tampona konur.
    kare, damga = over.pop('depth_frame', None), over.pop('depth_stamp', None)
    for k, v in over.items():
        setattr(n, k, v)
    if kare is not None:
        n.depth_buf.append((damga if damga is not None else 0.0, kare))
    return n


def det(x1=600, y1=300, x2=660, y2=380, ad='DUR_TT-2'):
    return Detection(bbox=np.array([x1, y1, x2, y2]), confidence=0.9,
                     class_id=0, class_name=ad)


def kontrol(ad, kosul, ayrinti=''):
    global gecti, basarisiz
    if kosul:
        gecti += 1
        print(f'  [OK]   {ad}')
    else:
        basarisiz += 1
        print(f'  [HATA] {ad}  {ayrinti}')


print('--- derinlik olcumu ---')

# 1) Temiz derinlik -> OLCULDU (src=1)
n = dugum(depth_frame=np.full((H, W), 7.5, np.float32), depth_stamp=100.0,
          depth_msg_count=5)
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 100.02)
kontrol('duz 7.5 m sahne -> olculdu', src == 1 and abs(d - 7.5) < 1e-3, f'{d=} {src=}')

# 2) Kutuya sizan arka plan medyani bozmamali
dep = np.full((H, W), 30.0, np.float32)
dep[310:370, 610:650] = 6.0                      # kutunun ic bolgesi = tabela
n = dugum(depth_frame=dep, depth_stamp=100.0, depth_msg_count=5)
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 100.0)
kontrol('kenarlardaki uzak arka plan medyani bozmuyor',
        src == 1 and abs(d - 6.0) < 1e-3, f'{d=} {src=}')

# 3) Bayat derinlik karesi -> yedege dus
n = dugum(depth_frame=np.full((H, W), 7.5, np.float32), depth_stamp=100.0,
          depth_msg_count=5)
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 101.0)
kontrol('1 sn bayat derinlik -> tahmine dusuyor',
        src == 0 and abs(d - 362.0 / 80) < 1e-6, f'{d=} {src=}')

# 4) Gecersiz piksel (NaN/0) cogunluktaysa olcum reddedilmeli
dep = np.full((H, W), np.nan, np.float32)
dep[310:315, 610:615] = 5.0                      # ~%2 gecerli
n = dugum(depth_frame=dep, depth_stamp=100.0, depth_msg_count=5)
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 100.0)
kontrol('cogunlugu NaN olan kutu reddediliyor', src == 0, f'{d=} {src=}')

# 5) Menzil disi degerler elenmeli (CARLA gokyuzu = 1000 m)
dep = np.full((H, W), 1000.0, np.float32)
dep[310:370, 610:650] = 12.0
n = dugum(depth_frame=dep, depth_stamp=100.0, depth_msg_count=5)
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 100.0)
kontrol('menzil disi (1000 m) pikseller eleniyor',
        src == 1 and abs(d - 12.0) < 1e-3, f'{d=} {src=}')

# 6) Derinlik cozunurlugu farkliysa bbox olceklenmeli
dep = np.full((360, 640), 25.0, np.float32)
dep[155:185, 305:325] = 9.0                      # yari cozunurlukte ayni bolge
n = dugum(depth_frame=dep, depth_stamp=100.0, depth_msg_count=5)
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 100.0)
kontrol('yari cozunurluklu derinlik dogru olcekleniyor',
        src == 1 and abs(d - 9.0) < 1e-3, f'{d=} {src=}')

# 7) Tampon offset'i dusulmeli
n = dugum(depth_frame=np.full((H, W), 7.5, np.float32), depth_stamp=100.0,
          depth_msg_count=5, camera_to_bumper=1.2)
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 100.0)
kontrol('kamera->tampon offset dusuluyor', abs(d - 6.3) < 1e-3, f'{d=}')

# 7b) YOLO gecikmesi: islenen RGB karesi geride kalir, tamponda ondan DAHA
#     YENI kareler birikir. Eslestirme "en yeni"yi degil "en yakin"i secmeli;
#     yoksa bbox eski karedeki konumu gosterirken derinlik yeni kareden
#     okunur -- yanlis piksel, ve gereksiz yere tahmine dusme.
n = dugum(depth_msg_count=9)
for t, m in ((99.8, 3.0), (99.9, 4.0), (100.0, 7.5), (100.1, 11.0), (100.2, 15.0)):
    n.depth_buf.append((t, np.full((H, W), m, np.float32)))
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 100.0)
kontrol('en YAKIN derinlik karesi seciliyor (en yenisi degil)',
        src == 1 and abs(d - 7.5) < 1e-3, f'{d=} {src=}')

# 7c) Tamponun tamami esik disindaysa gercekten bayattir -> yedek
n = dugum(depth_msg_count=9)
for t, m in ((98.0, 3.0), (98.1, 4.0), (98.2, 5.0)):
    n.depth_buf.append((t, np.full((H, W), m, np.float32)))
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 100.0)
kontrol('tamponun tamami bayatsa tahmine dusuyor', src == 0, f'{d=} {src=}')

print('--- yedek (bbox tahmini) ---')

# 8) Isik ve tabela AYRI sabit kullanmali
n = dugum()
d_t, _ = n._resolve_distance(det(), DUR, 100, (H, W, 3), 100.0)
d_i, _ = n._resolve_distance(det(ad='Kirmizi_Isik'), KIRMIZI_ISIK, 100, (H, W, 3), 100.0)
kontrol('isik ve tabela ayri sabitte',
        abs(d_t - 3.62) < 1e-6 and abs(d_i - 2.18) < 1e-6, f'{d_t=} {d_i=}')

# 9) Yedek kapaliysa mesafe URETILMEMELI
n = dugum(allow_bbox_fallback=False)
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 100.0)
kontrol('yedek kapali + derinlik yok -> mesafe uretilmiyor',
        d is None and src == -1, f'{d=} {src=}')

# 10) use_depth=False -> hep tahmin
n = dugum(use_depth=False, depth_frame=np.full((H, W), 7.5, np.float32),
          depth_stamp=100.0)
d, src = n._resolve_distance(det(), DUR, 80, (H, W, 3), 100.0)
kontrol('use_depth=False derinligi yok sayiyor', src == 0, f'{d=} {src=}')

print('--- depth_callback encoding ---')


class _Msg:
    def __init__(self, arr, enc, big=False):
        self.height, self.width = arr.shape
        self.encoding, self.is_bigendian = enc, big
        self.data = arr.tobytes()
        self.header = type('h', (), {'stamp': type('s', (), {'sec': 5, 'nanosec': 500_000_000})()})()


n = dugum()
n.depth_callback(_Msg(np.full((4, 4), 3.25, np.float32), '32FC1'))
kontrol('32FC1 metre olarak okunuyor',
        len(n.depth_buf) == 1 and abs(n.depth_buf[0][1][0, 0] - 3.25) < 1e-6
        and abs(n.depth_buf[0][0] - 5.5) < 1e-9, f'{list(n.depth_buf)=}')

n = dugum()
n.depth_callback(_Msg(np.full((4, 4), 3250, np.uint16), '16UC1'))
kontrol('16UC1 milimetreden metreye ceviriliyor',
        len(n.depth_buf) == 1 and abs(n.depth_buf[0][1][0, 0] - 3.25) < 1e-6)

n = dugum()
n.depth_callback(_Msg(np.full((4, 4), 1.0, np.float32), 'bgr8'))
kontrol('bilinmeyen encoding kullanilmiyor',
        len(n.depth_buf) == 0 and n.depth_msg_count == 0)

print('--- /master tel formati ---')


class _Pub:
    """Sahte publisher: yayinlanan ham metni saklar."""
    def __init__(self): self.son = None
    def publish(self, m): self.son = m.data


def yayinla(n, sign_id=DUR, **kw):
    n.sign_id_map = {0: sign_id}
    n.master_pub = _Pub()
    n.publish_sign_to_master(det(**kw), (H, W, 3), 100.0)
    return n.master_pub.son


# bbox 600,300,660,380 -> cx=630 cy=340 w=60 h=80
n = dugum(depth_frame=np.full((H, W), 7.5, np.float32), depth_stamp=100.0,
          depth_msg_count=5)
kontrol('olculen mesafe 8 alanli yayinlaniyor',
        yayinla(n) == '3,11,7.50,630,340,60,80,1', yayinla(n))

n = dugum()
kontrol('yedek mesafe src=0 ile isaretleniyor',
        yayinla(n) == '3,11,4.53,630,340,60,80,0', yayinla(n))

n = dugum(allow_bbox_fallback=False)
kontrol('olcum yoksa ve yedek kapaliysa HIC yayin yok', yayinla(n) is None)

print('--- beyin: ID-3 uctan uca ---')

from neuravix_ros2.decision_brain import Alkar_Function4, DriveState        # noqa: E402


def besle(b, sign, mesafe, src=None, kez=6):
    """Ayni tabelayi birkac kez besler (beyin ard arda teyit istiyor)."""
    alanlar = ["3", str(sign), f"{mesafe}", "640", "360", "40", "40"]
    if src is not None:
        alanlar.append(str(src))
    for _ in range(kez):
        b.sign_detect_event(alanlar)


b = Alkar_Function4()
besle(b, KIRMIZI_ISIK, 4.0, src=1)
kontrol('kirmizi isik 4.0 m (olculdu) -> RED_LIGHT_STOP',
        b.state == DriveState.RED_LIGHT_STOP, b.state)

b = Alkar_Function4()
besle(b, KIRMIZI_ISIK, 6.0, src=1)
kontrol('kirmizi isik 6.0 m -> henuz durmuyor',
        b.state != DriveState.RED_LIGHT_STOP, b.state)

b = Alkar_Function4()
besle(b, DUR, 4.0, src=1)
kontrol('DUR tabelasi 4.0 m -> STOP_SIGN',
        b.state == DriveState.STOP_SIGN, b.state)

# Eski 7 alanli mesaj (src yok): src alani opsiyonel, geriye donuk uyumlu olmali.
b = Alkar_Function4()
besle(b, KIRMIZI_ISIK, 4.0, src=None)
kontrol('7 alanli eski mesaj hala isleniyor',
        b.state == DriveState.RED_LIGHT_STOP, b.state)

print(f'\n{gecti} gecti, {basarisiz} basarisiz')
sys.exit(1 if basarisiz else 0)
