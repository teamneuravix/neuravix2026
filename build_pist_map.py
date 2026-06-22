"""
Robotaksi Pist - FULLY JUNCTIONED OpenDRIVE (image.png + duzgun topoloji)
========================================================================
v4 - 3 sira ada + 10 m yol genisligi + dogru donel ada konumu/capi:
  - 3 satir x 3 sutun blok grid (image.png referans)
  - Yol genisligi RW=10 m (kullanici olcumu 0.01 km)
  - TUNEL: V1xH2 = (26, 47) sol-ust ic kavsak, 2 ada etrafinda
  - DONEL ADA: V2xH1 = (47, 26) sag-alt ic kavsak, cap 10 m
  - Adalar+dis cevre arasi ve adalar arasi yollarda kesikli serit
    (broken roadMark zaten center lane'de)
  - 16 grid kavsagi: 4 kose + 8 kenar T + 2 ic 4-way + TUNEL + RA

Geometri:
  VX = [5, 26, 47, 68]   - 4 dikey yol centerline
  HY = [5, 26, 47, 68]   - 4 yatay yol centerline
  BLK = 11x11, RW = 10
  Park annex dogu kenarda (J102 NE'de T)
  3 D durak cevrede
"""

import json
import math
import os

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon as MplPoly
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PI = math.pi

# ===========================================================================
# 1) GEOMETRI (kullanici olcumleri: 0.01 km = 10 m, image.png referans)
# ===========================================================================
LW = 3.0                       # tek serit genisligi (CARLA arac standart)
RW = 10.0                      # yol genisligi (= adalar/cevre arasi mesafe)
BLK_W = 11.0
BLK_H = 11.0
NCOL, NROW = 3, 3              # 3 sutun x 3 satir ada

VX = [RW/2 + i * (RW + BLK_W) for i in range(NCOL + 1)]    # [5, 26, 47, 68]
HY = [RW/2 + j * (RW + BLK_H) for j in range(NROW + 1)]    # [5, 26, 47, 68]
MAIN_W = VX[-1] + RW/2         # 73
MAIN_H = HY[-1] + RW/2         # 73

# TUNEL: V1 dikey yolu uzerinde, B1 ile B2 arasi yol segmentinin ortasinda
# (image.png stili: tunel bir kavsakta degil, blok hizasinda yol uzerinde)
# V_(1, 1) segmenti = V1 uzerinde HY[1] ile HY[2] arasi segment
TUN_SEG_I, TUN_SEG_J = 1, 1
TUN_CX = VX[TUN_SEG_I]                              # 26
TUN_CY = (HY[TUN_SEG_J] + HY[TUN_SEG_J + 1]) / 2    # 36.5 (B1, B2 merkez y)
TUN_LEN = 9.0                                       # tunel objesi uzunlugu (m)

# DONEL ADA: V2 x H1 = (47, 26) - sag-alt ic kavsak
# Kullanici: "2. satir ile 3. satir arasinda, 2. sutun ile 3. sutun arasinda, cap 0.01 km"
RA_I, RA_J = 2, 1
RA_CX, RA_CY = VX[RA_I], HY[RA_J]
RA_OUTER_R = 5.0               # CAP 10 m -> R 5 m (kullanici olcumu)
RA_ISLAND_R = 2.0
RA_LANE_R = (RA_ISLAND_R + RA_OUTER_R) / 2     # 3.5

# Junction radii
JR = RW / 2                    # 5.0 (normal grid)
JR_RA = RA_OUTER_R             # 5.0 (donel ada kavsagi)

# Parking annex (dogu kenarda) — DUZ DIKDORTGEN
# Park: x=73..90, y=43..63 -> pist sag kenarina yapisik, sag-ust koseden 10 m mesafede,
# 20 m uzunlugunda. Slotlar SOL sutunda, sag taraf aisle (manevra/giris koridoru).
# Pist <-> park baglantisi: J111 (E2) 4-yon kavsak -> dogu park girisi (y=HY[2]=47).
PARK_X = MAIN_W                # 73 (pist sag kenarina yapisik)
PARK_W = 17.0
PARK_TOP_GAP = 10.0            # sag-ust koseden mesafe
PARK_H = 20.0                  # park uzunlugu
PARK_Y = MAIN_H - PARK_TOP_GAP - PARK_H   # 43 (alt kenar) — ust kenar = 63
PARK_ENTRY_Y = HY[2]           # 47 (E2 kavsagi seviyesi — park y araliginin icinde)
PARK_ENTRY_JID = 111           # J111 (E2) artik 4-way: N-S + W cevre + E park girisi

# Block visual positions: 3x3 grid + KML d1 ek adasi
# Her ada hem preview'da hem de CARLA'da bir "ghost road" (shoulder lane)
# ile dolduruluyor -> arac asla bos alana dusmez.
row_cols = [3, 3, 3]  # A, B, C
BLOCKS = []
for r in range(NROW):
    by = HY[r] + RW / 2
    cols = row_cols[r]
    for c in range(cols):
        bx = VX[c] + RW / 2
        if r == 0:
            row_label = "A"
        elif r == 1:
            row_label = "B"
        else:
            row_label = "C"
        label = f"{row_label}{c+1}"
        BLOCKS.append((bx, by, BLK_W, BLK_H, label))
# Ek ada: KML'deki d1 - park alani slot alaninin uzerinde, kucuk dikey bloc
# (slot alani y=52-63 oldugu icin onun ustunde y=64-69'da konumlandirildi)
#BLOCKS.append((75.0, 64.0, 3.0, 5.0, "d1"))

# Donel ada ic adasi: (RA_CX, RA_CY) merkezinde, RA_ISLAND_R*2 boyutunda
# ghost road olarak eklenir -> "cizili ada" gorunumu (beyaz solid kenar, duz yuzey)
# Bot-left koşesi = (RA_CX - RA_ISLAND_R, RA_CY - RA_ISLAND_R)
_RA_ISL_BL = (RA_CX - RA_ISLAND_R, RA_CY - RA_ISLAND_R)
BLOCKS.append((_RA_ISL_BL[0], _RA_ISL_BL[1],
               2 * RA_ISLAND_R, 2 * RA_ISLAND_R, "RA_isl"))

# Tunelin gorsel boyutu (preview icin) ve etrafindaki 2 ucgen ada
# image.png'deki gibi tunelin south girisi yaninda ve north cikisi yaninda
TUN_W_VIS = RW - 1.0           # 9 m (yol genisliginden biraz dar)
TUN_H_VIS = TUN_LEN            # 9 m (segment uzunlugunun cogu)
_tw, _tl = TUN_W_VIS / 2, TUN_H_VIS / 2
TUN_ADA_1 = [(TUN_CX + _tw, TUN_CY - _tl),
             (TUN_CX + _tw + 1.6, TUN_CY - _tl - 0.3),
             (TUN_CX + _tw, TUN_CY - _tl - 1.6)]
TUN_ADA_2 = [(TUN_CX - _tw, TUN_CY + _tl),
             (TUN_CX - _tw - 1.6, TUN_CY + _tl + 0.3),
             (TUN_CX - _tw, TUN_CY + _tl + 1.6)]

# DURAKLAR (visual):
#  - 3 DIS durak: perimeter (dis cevre) disinda asfalt-cep seklinde
#      side = "W"|"S"|"N"|"E", along = perimetre uzerindeki konum,
#      w_along = cep uzunlugu (perimetreye paralel), depth = perimetreden dis yon
#  - 1 IC durak: B3 adasinin icinde (B3 = (52, 31)..(63, 42))
DURAKLAR = [
    # D-sol: B1 adasinin ALT kenarina (bitisine) hizali -> y = 31
    dict(kind="dis", side="W", along=31.0,
         w_along=7.0, depth=3.5, label="D-sol"),
    # D-alt: TUNEL'in orta noktasina (V1 = x=26) hizali
    dict(kind="dis", side="S", along=TUN_CX,
         w_along=7.0, depth=3.5, label="D-alt"),
    dict(kind="ic", cx=53.5, cy=36.5, w=2.5, h=6.0, label="D-ic"),
]

# ===========================================================================
# 1.5) MISYON: spawn + obje listesi
# ===========================================================================
# Spawn: J102 NE kosesi yakini, H3 ust yolunun KUZEY seridi (dis cevre, adalardan
# uzak). Yon = bati (CCW). Lane id=+1 (sol serit, native heading=east).
SPAWN_X = 72.0                   # J102 kavsak ortasi yakini - engelden ~14.5 m geride
SPAWN_Y = HY[3] + LW / 2         # 69.5 - kuzey serit ortasi (dis cevre)
SPAWN_Z = 0.5
SPAWN_YAW = 180.0                # batiya bakiyor

# Misyon objeleri (tabela, engel, trafik isigi) - dunya koordinati.
# Konumlar dis cevre (kuzey) seritte; engel ise sol serit icinde (slalom).
MISYON_OBJELERI = [
    dict(kind="sign", type_name="ileri_git",
         x=53.0, y=HY[3] + LW + 1.0, hdg=PI,
         label="ILERI GIT",
         note="J109 dogusu, H3 dis cevre (kuzey); CCW bati yonune giden surucuye"),
    dict(kind="obstacle",
         x=57.5, y=HY[3] + LW / 2,
         w=1.4, h=1.4,
         label="ENGEL",
         note="C3 merkez x, H3 sol serit (kuzey lane id=+1) - slalom test"),
    dict(kind="traffic_light",
         x=36.5, y=HY[3] + LW + 1.0,
         label="ISIK",
         note="C2 merkez x, H3 dis cevre (kuzey); kirmizi-sari-yesil"),
    dict(kind="sign", type_name="sag_don",
         x=31.0, y=HY[3] + LW + 1.0, hdg=PI,
         label="SAGA DON",
         note="J108 dogusu, H3 dis cevre (kuzey); CCW surucuye guneye don sinyali"),
    dict(kind="sign", type_name="tunel",
         x=TUN_CX - LW - 1.0, y=44.0, hdg=3 * PI / 2,
         label="TUNEL",
         note="Tunelin J114 (kuzey) tarafi; guneye giden surucuye tunel uyarisi"),
]

TOTAL_W = PARK_X + PARK_W
TOTAL_H = max(MAIN_H, PARK_Y + PARK_H)

# ===========================================================================
# 2) ID counters
# ===========================================================================
_rid = [0]
def new_rid():
    _rid[0] += 1
    return _rid[0]


# ===========================================================================
# 3) OpenDRIVE XML helpers
# ===========================================================================

def lane_section(lane_w=LW):
    return f"""
        <laneSection s="0">
          <left><lane id="1" type="driving" level="false">
            <link/>
            <width sOffset="0" a="{lane_w}" b="0" c="0" d="0"/>
            <roadMark sOffset="0" type="solid" weight="standard" color="white" width="0.25"/>
          </lane></left>
          <center><lane id="0" type="none" level="false">
            <roadMark sOffset="0" type="broken" weight="standard" color="white" width="0.25"/>
          </lane></center>
          <right><lane id="-1" type="driving" level="false">
            <link/>
            <width sOffset="0" a="{lane_w}" b="0" c="0" d="0"/>
            <roadMark sOffset="0" type="solid" weight="standard" color="white" width="0.25"/>
          </lane></right>
        </laneSection>"""


def lane_section_shoulder(half_w):
    """Shoulder (suruculuk olmayan, duz) lanes - ada yuzeyleri icin.
    Beyaz solid roadMark ile ada siniri belli edilir."""
    return f"""
        <laneSection s="0">
          <left><lane id="1" type="shoulder" level="false">
            <link/>
            <width sOffset="0" a="{half_w}" b="0" c="0" d="0"/>
            <roadMark sOffset="0" type="solid" weight="standard" color="white" width="0.15"/>
          </lane></left>
          <center><lane id="0" type="none" level="false"/></center>
          <right><lane id="-1" type="shoulder" level="false">
            <link/>
            <width sOffset="0" a="{half_w}" b="0" c="0" d="0"/>
            <roadMark sOffset="0" type="solid" weight="standard" color="white" width="0.15"/>
          </lane></right>
        </laneSection>"""


def make_island_patch(rid, name, cx, cy, w, h, objects_xml="", signals_xml=""):
    """Standalone ghost road - bir ada/park alani yuzeyi.
    Yon N (heading=PI/2), uzunluk=h, toplam genislik=w (yariya bolunmus)."""
    return make_road(rid, name, cx, cy - h/2, PI/2, h,
                     lanes_xml=lane_section_shoulder(w/2),
                     objects_xml=objects_xml, signals_xml=signals_xml)


def lane_section_base(half_w):
    """Base layer ghost road - RoadMark YOK (yoksa pist disinda outline cizer).
    Genel asfalt-rengi zemin verir."""
    return f"""
        <laneSection s="0">
          <left><lane id="1" type="shoulder" level="false">
            <link/>
            <width sOffset="0" a="{half_w}" b="0" c="0" d="0"/>
          </lane></left>
          <center><lane id="0" type="none" level="false"/></center>
          <right><lane id="-1" type="shoulder" level="false">
            <link/>
            <width sOffset="0" a="{half_w}" b="0" c="0" d="0"/>
          </lane></right>
        </laneSection>"""


def make_base_layer(rid, cx, cy, w, h, z_offset=-0.02):
    """Pistin altina koca shoulder ghost road - 'asfalt zemin' yerine gecer.
    z_offset hafifce eksi (yollar ustte kalsin, z-fighting olmasin)."""
    return f"""
  <road name="BaseLayer" length="{h:.4f}" id="{rid}" junction="-1">
    <link></link>
    <type s="0" type="town"><speed max="30" unit="km/h"/></type>
    <planView>
      <geometry s="0" x="{cx:.4f}" y="{cy - h/2:.4f}" hdg="{PI/2:.6f}" length="{h:.4f}">
        <line/>
      </geometry>
    </planView>
    <elevationProfile><elevation s="0" a="{z_offset:.4f}" b="0" c="0" d="0"/></elevationProfile>
    <lateralProfile/>
    <lanes>{lane_section_base(w/2)}
    </lanes>
    <objects></objects>
    <signals></signals>
  </road>"""


def make_pocket_road(rid, name, side, along, w_along, depth,
                     signals_xml="", objects_xml=""):
    """Dis durak cebi: cevre yola YAPISIK.
    Cep'in ic kenari, cevre yolun dis serit kenari ile cakisir;
    cep oradan dis yone (depth kadar) uzanir.
    W cevresi (V0): ic kenar = VX[0] - LW (lane dis kenari);
                    cep merkez x = (VX[0] - LW) - depth/2
    Benzer mantik S/E/N icin."""
    half = depth / 2
    kw = dict(lanes_xml=lane_section(lane_w=half),
              signals_xml=signals_xml, objects_xml=objects_xml)
    if side == "W":
        x_c = (VX[0] - LW) - half
        return make_road(rid, name, x_c, along - w_along/2, PI/2, w_along, **kw)
    elif side == "E":
        x_c = (VX[-1] + LW) + half
        return make_road(rid, name, x_c, along - w_along/2, PI/2, w_along, **kw)
    elif side == "S":
        y_c = (HY[0] - LW) - half
        return make_road(rid, name, along - w_along/2, y_c, 0, w_along, **kw)
    elif side == "N":
        y_c = (HY[-1] + LW) + half
        return make_road(rid, name, along - w_along/2, y_c, 0, w_along, **kw)


def barrier_object(obj_id, s, t, length, name="wall", height=1.0,
                   width=0.3, hdg=0.0):
    """OpenDRIVE <object type="barrier"> - 3D bariyer/duvar (esmini render eder).
    s/t hedef yola gore, length yol uzunlugu boyunca, hdg yola gore aci."""
    return (
        f'<object id="{obj_id}" type="barrier" name="{name}_{obj_id}" '
        f's="{s:.3f}" t="{t:.3f}" zOffset="0" '
        f'length="{length:.3f}" width="{width:.3f}" height="{height:.3f}" '
        f'hdg="{hdg:.3f}" pitch="0" roll="0" validLength="0" orientation="none"/>'
    )


def obstacle_object(obj_id, s, t, length, width, name="engel", height=0.8):
    """OpenDRIVE <object type="obstacle"> - engel (slalom icin)."""
    return (
        f'<object id="{obj_id}" type="obstacle" name="{name}_{obj_id}" '
        f's="{s:.3f}" t="{t:.3f}" zOffset="0" '
        f'length="{length:.3f}" width="{width:.3f}" height="{height:.3f}" '
        f'hdg="0" pitch="0" roll="0" validLength="0" orientation="none"/>'
    )


# ---------------------------------------------------------------------------
# EXTRA_PER_ROAD: Misyon objeleri + bariyerler.
# Anahtar = yol adi (V{i}_{j} / H{j}_{i} / Cep_X / Pist_ust_uzanti vs.),
# Deger  = {"signals": "...", "objects": "..."} - make_road'a inject edilir.
# ---------------------------------------------------------------------------
EXTRA_PER_ROAD = {}

def _add_to_road(road_name, signals="", objects=""):
    e = EXTRA_PER_ROAD.setdefault(road_name, {"signals": "", "objects": ""})
    e["signals"] += signals
    e["objects"] += objects

def _extra_for(road_name):
    e = EXTRA_PER_ROAD.get(road_name, {})
    return e.get("signals", ""), e.get("objects", "")


def painted_rect_object(obj_id, s, t, length, width, name="mark", height=0.02):
    """Genel boyali dikdortgen decal (<object> outline).
    Park ayraci, serit isareti, vs. icin kullanilir."""
    half_l, half_w = length / 2, width / 2
    return (
        f'<object id="{obj_id}" type="none" name="{name}_{obj_id}" '
        f's="{s:.3f}" t="{t:.3f}" zOffset="0.01" '
        f'length="{length:.3f}" width="{width:.3f}" height="{height:.3f}" '
        f'hdg="0" pitch="0" roll="0" validLength="0" orientation="none">'
        f'<outline>'
        f'<cornerLocal u="{-half_l:.3f}" v="{-half_w:.3f}" z="0" height="{height}"/>'
        f'<cornerLocal u="{half_l:.3f}" v="{-half_w:.3f}" z="0" height="{height}"/>'
        f'<cornerLocal u="{half_l:.3f}" v="{half_w:.3f}" z="0" height="{height}"/>'
        f'<cornerLocal u="{-half_l:.3f}" v="{half_w:.3f}" z="0" height="{height}"/>'
        f'</outline></object>'
    )


def park_line_object(obj_id, s, t, length, lateral_span, height=0.02):
    """Park ayraci ince cizgi (geriye-uyumlu wrapper)."""
    return painted_rect_object(obj_id, s, t, length, lateral_span,
                                name="park_div", height=height)


def road_markings_xml(start_obj_id, seg_len, lane_w=LW,
                      dash=2.0, gap=3.0, mark_w=0.20):
    """Bir yol segmenti icin serit boyalari (CARLA'da decal olarak gorunur):
       - Solid kenar cizgileri (sol + sag, t = +/- lane_w)
       - Center'da broken/kesikli cizgi (t=0, dash-gap deseninde)

    Donus: (xml_string, next_obj_id)"""
    xml = ""
    obj_id = start_obj_id
    # Solid kenar cizgileri - tum segment boyunca
    xml += painted_rect_object(obj_id, seg_len/2, +lane_w, seg_len, mark_w,
                                name="edgeL")
    obj_id += 1
    xml += painted_rect_object(obj_id, seg_len/2, -lane_w, seg_len, mark_w,
                                name="edgeR")
    obj_id += 1
    # Center broken (kesikli) - cok sayida kisa dash
    period = dash + gap
    n_dashes = max(1, int(seg_len / period))
    total_pattern = n_dashes * period - gap
    margin = max(0.0, (seg_len - total_pattern) / 2)
    for k in range(n_dashes):
        s_dash = margin + k * period + dash / 2
        if s_dash + dash/2 > seg_len or s_dash - dash/2 < 0:
            continue
        xml += painted_rect_object(obj_id, s_dash, 0.0, dash, mark_w,
                                    name="cdash")
        obj_id += 1
    return xml, obj_id


# Trafik isareti tipi -> OpenDRIVE/StVO kodu, baslik
_SIGNAL_TYPES = {
    "parking":       ("314", "Park yapilabilir"),
    "no_parking":    ("286", "Park yasak"),
    "bus_stop":      ("224", "Otobus duragi"),
    "ileri_git":     ("209", "Ileri git"),
    "sag_don":       ("211", "Saga don"),
    "tunel":         ("327", "Tunel"),
    "traffic_light": ("1000001", "Trafik isigi"),  # CARLA: 3-light vertical (1000003=bisiklet!)
}

def signal_xml(sig_id, s, t, kind, h_offset=0.0):
    """OpenDRIVE <signal> - trafik isareti (parking/no_parking/bus_stop).
    traffic_light tipi otomatik dynamic=yes set eder - CARLA bunu canli
    trafik isigi olarak instantiate eder."""
    code, label = _SIGNAL_TYPES.get(kind, ("0", "Generic"))
    dynamic = "yes" if kind == "traffic_light" else "no"
    height = "3.5" if kind == "traffic_light" else "0.7"
    return (
        f'<signal id="{sig_id}" name="{label}" s="{s:.3f}" t="{t:.3f}" '
        f'dynamic="{dynamic}" orientation="+" zOffset="0.3" '
        f'country="OpenDRIVE" type="{code}" subtype="-1" value="0" '
        f'hOffset="{h_offset:.2f}" pitch="0" roll="0" height="{height}" width="0.7"/>'
    )

def _link_xml(pred, succ):
    parts = []
    if pred:
        k, e, c = pred
        cp = f' contactPoint="{c}"' if c else ""
        parts.append(f'<predecessor elementType="{k}" elementId="{e}"{cp}/>')
    if succ:
        k, e, c = succ
        cp = f' contactPoint="{c}"' if c else ""
        parts.append(f'<successor elementType="{k}" elementId="{e}"{cp}/>')
    return "".join(parts)

def make_road(rid, name, x, y, hdg, length,
              pred=None, succ=None, junction="-1",
              kind="line", curvature=0.0,
              lanes_xml=None, objects_xml="", signals_xml=""):
    geom = "<line/>" if kind == "line" else f'<arc curvature="{curvature:.6f}"/>'
    if lanes_xml is None:
        lanes_xml = lane_section()
    return f"""
  <road name="{name}" length="{length:.4f}" id="{rid}" junction="{junction}">
    <link>{_link_xml(pred, succ)}</link>
    <type s="0" type="town"><speed max="30" unit="km/h"/></type>
    <planView>
      <geometry s="0" x="{x:.4f}" y="{y:.4f}" hdg="{hdg:.6f}" length="{length:.4f}">
        {geom}
      </geometry>
    </planView>
    <elevationProfile><elevation s="0" a="0" b="0" c="0" d="0"/></elevationProfile>
    <lateralProfile/>
    <lanes>{lanes_xml}
    </lanes>
    <objects>{objects_xml}</objects>
    <signals>{signals_xml}</signals>
  </road>"""


# ===========================================================================
# 4) Junction helpers
# ===========================================================================

def _in_lane(b):
    return -1 if b["cp"] == "end" else 1

def _connecting_road(rid, name, b_in, b_out, cx, cy, jid, jr=JR):
    """Connecting road from b_in edge to b_out edge inside junction."""
    edge_in = (cx + jr * math.cos(b_in["hdg_out"]),
               cy + jr * math.sin(b_in["hdg_out"]))
    edge_out = (cx + jr * math.cos(b_out["hdg_out"]),
                cy + jr * math.sin(b_out["hdg_out"]))
    h_in = (b_in["hdg_out"] + PI) % (2*PI)
    h_out = b_out["hdg_out"]
    d_hdg = ((h_out - h_in + PI) % (2*PI)) - PI

    pred = ("road", b_in["rid"], b_in["cp"])
    succ = ("road", b_out["rid"], b_out["cp"])

    if abs(d_hdg) < 0.01:
        length = math.hypot(edge_out[0]-edge_in[0], edge_out[1]-edge_in[1])
        return make_road(rid, name, edge_in[0], edge_in[1], h_in, length,
                         pred=pred, succ=succ, junction=str(jid))
    else:
        R = jr
        curv = 1.0/R if d_hdg > 0 else -1.0/R
        return make_road(rid, name, edge_in[0], edge_in[1], h_in,
                         R * abs(d_hdg), pred=pred, succ=succ,
                         kind="arc", curvature=curv, junction=str(jid))


def corner_junction(jid, cx, cy, b1, b2):
    """2-way corner (90°). Each direction = 1 arc connecting road."""
    rid1 = new_rid()
    xml1 = _connecting_road(rid1, f"J{jid}_a", b1, b2, cx, cy, jid)
    rid2 = new_rid()
    xml2 = _connecting_road(rid2, f"J{jid}_b", b2, b1, cx, cy, jid)
    junc = f"""
  <junction id="{jid}" name="corner_{jid}">
    <connection id="1" incomingRoad="{b1['rid']}" connectingRoad="{rid1}" contactPoint="start">
      <laneLink from="{_in_lane(b1)}" to="-1"/></connection>
    <connection id="2" incomingRoad="{b2['rid']}" connectingRoad="{rid2}" contactPoint="start">
      <laneLink from="{_in_lane(b2)}" to="-1"/></connection>
  </junction>"""
    return [xml1, xml2], junc


def t_junction(jid, cx, cy, m1, m2, side):
    """T-junction: 6 connecting roads (all turn pairs)."""
    roads = []; conns = []; cid = 1
    pairs = [(m1, m2), (m2, m1),
             (m1, side), (side, m1),
             (m2, side), (side, m2)]
    for b_in, b_out in pairs:
        rid = new_rid()
        roads.append(_connecting_road(rid, f"J{jid}_{cid}", b_in, b_out, cx, cy, jid))
        conns.append((cid, b_in["rid"], rid, _in_lane(b_in), -1))
        cid += 1
    conns_xml = "\n    ".join(
        f'<connection id="{c}" incomingRoad="{ir}" connectingRoad="{cr}" contactPoint="start"><laneLink from="{fr}" to="{to}"/></connection>'
        for c, ir, cr, fr, to in conns
    )
    junc = f"""
  <junction id="{jid}" name="t_{jid}">
    {conns_xml}
  </junction>"""
    return roads, junc


def four_way_junction(jid, cx, cy, b_N, b_E, b_S, b_W, jr=JR, objects_inside=""):
    """4-way junction: 12 connecting roads (4 straight + 8 turn)."""
    branches = [b_N, b_E, b_S, b_W]
    roads = []; conns = []; cid = 1
    for b_in in branches:
        for b_out in branches:
            if b_in is b_out:
                continue
            rid = new_rid()
            road_xml = _connecting_road(rid, f"J{jid}_{cid}", b_in, b_out, cx, cy, jid, jr=jr)
            # TUNEL object icin: tum connecting road'lara cover ekle
            if objects_inside and (b_in is b_N or b_in is b_S):
                # Sadece duz N-S yonu icin tunnel objesi koy (tek bir yere)
                if b_out is (b_S if b_in is b_N else b_N):
                    # Replace <objects></objects> with object xml
                    road_xml = road_xml.replace("<objects></objects>",
                                                 f"<objects>{objects_inside}</objects>")
            roads.append(road_xml)
            conns.append((cid, b_in["rid"], rid, _in_lane(b_in), -1))
            cid += 1
    conns_xml = "\n    ".join(
        f'<connection id="{c}" incomingRoad="{ir}" connectingRoad="{cr}" contactPoint="start"><laneLink from="{fr}" to="{to}"/></connection>'
        for c, ir, cr, fr, to in conns
    )
    junc = f"""
  <junction id="{jid}" name="4way_{jid}">
    {conns_xml}
  </junction>"""
    return roads, junc


def roundabout_junction(jid, cx, cy, lane_r, b_N, b_E, b_S, b_W):
    """Roundabout: 4 arc segments (CCW), birbirlerine + cevre yollarina baglanir."""
    branches = {"N": b_N, "E": b_E, "S": b_S, "W": b_W}

    curv = 1.0 / lane_r
    seg_len = PI * lane_r / 2.0

    # arc[i]: theta0 -> theta0 + 90° CCW
    # arc[0]: theta0=0    (east edge) heading=PI/2 (kuzeye), ends at theta=PI/2 (north edge)
    # arc[1]: theta0=PI/2 (north edge) heading=PI (batiya), ends at theta=PI (west edge)
    # arc[2]: theta0=PI   (west edge) heading=3PI/2 (gineye), ends at theta=3PI/2 (south edge)
    # arc[3]: theta0=3PI/2 (south edge) heading=0 (doguya), ends at theta=2PI=0 (east edge)
    arc_data = []
    for i, th0 in enumerate([0.0, PI/2, PI, 3*PI/2]):
        x0 = cx + lane_r * math.cos(th0)
        y0 = cy + lane_r * math.sin(th0)
        hdg = th0 + PI/2
        arc_data.append((i, x0, y0, hdg))

    arc_ids = [new_rid() for _ in arc_data]
    arcs_xml = []
    for (i, x0, y0, hdg), rid in zip(arc_data, arc_ids):
        # arc[i] ends at arc[(i+1)%4]'s start
        next_arc_id = arc_ids[(i + 1) % 4]
        prev_arc_id = arc_ids[(i - 1) % 4]
        arcs_xml.append(make_road(
            rid, f"RA_arc_{i}",
            x0, y0, hdg, seg_len,
            kind="arc", curvature=curv,
            junction=str(jid),
            pred=("road", prev_arc_id, "end"),
            succ=("road", next_arc_id, "start"),
        ))

    # Connections: her giris yolu (N, E, S, W) hangi arc'a bagli
    # b_W: bati'dan dogu'ya geliyor (cp=end, hdg_out=PI), east-bound vehicle hits west arc
    #   girisinden cikan arc: theta0=PI (arc[2]) -> guneye doner
    # b_S: guney'den kuzeye geliyor (cp=end, hdg_out=3PI/2), north-bound vehicle hits south arc
    #   girisinden cikan arc: theta0=3PI/2 (arc[3]) -> doguya doner
    # b_E: dogu'dan bati'ya geliyor (cp=start, hdg_out=0), west-bound enters east arc
    #   girisinden cikan arc: theta0=0 (arc[0]) -> kuzeye doner
    # b_N: kuzey'den guneye geliyor (cp=start, hdg_out=PI/2), south-bound enters north arc
    #   girisinden cikan arc: theta0=PI/2 (arc[1]) -> batiya doner
    connections = [
        (1, b_W["rid"], arc_ids[2], _in_lane(b_W), -1),
        (2, b_S["rid"], arc_ids[3], _in_lane(b_S), -1),
        (3, b_E["rid"], arc_ids[0], _in_lane(b_E), -1),
        (4, b_N["rid"], arc_ids[1], _in_lane(b_N), -1),
    ]
    conns_xml = "\n    ".join(
        f'<connection id="{c}" incomingRoad="{ir}" connectingRoad="{cr}" contactPoint="start"><laneLink from="{fr}" to="{to}"/></connection>'
        for c, ir, cr, fr, to in connections
    )
    junc = f"""
  <junction id="{jid}" name="roundabout_{jid}">
    {conns_xml}
  </junction>"""
    return arcs_xml, junc


def tunnel_obj(s_start, length, name="Tunel"):
    return (f'<tunnel s="{s_start:.4f}" length="{length:.4f}" name="{name}" '
            f'id="1" type="standard" lighting="0.4" daylight="0.05"/>')


# ===========================================================================
# 5) Yol agi - 3x3 grid (4x4 kavsak topolojisi)
# ===========================================================================
# Junction ID haritalama: (i, j) -> JID
# i = sutun index (0..NCOL), j = satir index (0..NROW)
#
# Layout (j artan = y artan = kuzey):
#   J103(NW)  J108(N1)  J109(N2)  J102(NE+park)         <- HY[3]=68
#   J105(W2)  J114(I3)  J113(I4)  J111(E2)              <- HY[2]=47
#   J104(W1)  J112(I1)  J130 RA   J110(E1)              <- HY[1]=26
#   J100(SW)  J106(S1)  J107(S2)  J101(SE)              <- HY[0]=5
#   VX[0]=5   VX[1]=26  VX[2]=47  VX[3]=68
# TUNEL ayri: V1 uzerinde rid_V[(1,1)] segmentinin ortasinda (kavsak degil, yol uzeri obje)
JID = {
    (0, 0): 100, (3, 0): 101, (3, 3): 102, (0, 3): 103,    # 4 kose
    (0, 1): 104, (0, 2): 105,                              # bati T
    (3, 1): 110, (3, 2): 111,                              # dogu T
    (1, 0): 106, (2, 0): 107,                              # guney T
    (1, 3): 108, (2, 3): 109,                              # kuzey T
    (1, 1): 112, (1, 2): 114, (2, 2): 113,                 # 3 ic 4-way
    (RA_I, RA_J): 130,                                     # RA
}


def _jr_at(i, j):
    if (i, j) == (RA_I, RA_J): return JR_RA
    return JR


def _compute_misyon_extras():
    """MISYON_OBJELERI uzantilarini EXTRA_PER_ROAD'a ekler (OpenDRIVE signal/object).
    Konumlar onceden hesaplandi (preview ile ayni mantik)."""
    # Yol baglama tablosu (etiketle eslesir, world->road donusum elle):
    #  ileri_git (53,71)  -> H3_2 baslangic (52,68), s=1, t=+3
    #  sag_don   (31,71)  -> H3_1 baslangic (31,68), s=0.5, t=+3
    #  isik      (36.5,71)-> H3_1 baslangic (31,68), s=5.5, t=+3
    #  engel     (57.5,69.5)->H3_2 baslangic (52,68), s=5.5, t=+1.5 (sol serit)
    #  tunel     (22,52)  -> V1_2 baslangic (26,52) hdg=PI/2, s=0.5, t=+4
    bindings = {
        "ILERI GIT": ("H3_2", 1.0, +3.0),
        "ENGEL":     ("H3_2", 5.5, +1.5),
        "ISIK":      ("H3_1", 5.5, +3.0),
        "SAGA DON":  ("H3_1", 0.5, +3.0),
        "TUNEL":     ("V1_2", 0.5, +4.0),
    }
    sig_id = 9500
    obj_id = 9700
    for m in MISYON_OBJELERI:
        lbl = m["label"]
        if lbl not in bindings:
            continue
        road_name, s, t = bindings[lbl]
        if m["kind"] == "sign":
            sig = signal_xml(sig_id, s, t, m["type_name"])
            _add_to_road(road_name, signals=sig)
            sig_id += 1
        elif m["kind"] == "traffic_light":
            sig = signal_xml(sig_id, s, t, "traffic_light")
            sig = sig.replace('dynamic="no"', 'dynamic="yes"')
            _add_to_road(road_name, signals=sig)
            sig_id += 1
        elif m["kind"] == "obstacle":
            obs = obstacle_object(obj_id, s, t, m.get("w", 1.4), m.get("h", 1.4),
                                   name="engel_C3", height=0.8)
            _add_to_road(road_name, objects=obs)
            obj_id += 1


def _compute_barrier_extras():
    """Dis cevre yollarina + dis cep yollarina + ust uzantiya bariyer ekler."""
    bar_id = 9800
    bar_h = 1.0
    bar_t = LW + 0.4  # serit dis kenarindan 0.4 m disarida

    # H0 (guney cevre) - outer = t<0; H3 (kuzey cevre) - outer = t>0
    for i in range(NCOL):
        seg_len = VX[i + 1] - VX[i] - 2 * JR
        # H0 (guney) outer = t<0 (guney = saga - native east heading)
        rn0 = f"H0_{i}"
        if not _cep_overlaps_H(0, i):
            _add_to_road(rn0, objects=barrier_object(bar_id, seg_len / 2, -bar_t,
                                                     seg_len, height=bar_h))
            bar_id += 1
        else:
            # D-alt cep agzi: y=HY[0]=5 cevresinde, cep along=26 -> x=22.5..29.5
            for sub_s, sub_len in _segment_minus_cep_x(i, 0, "S"):
                _add_to_road(rn0, objects=barrier_object(
                    bar_id, sub_s + sub_len / 2, -bar_t, sub_len, height=bar_h))
                bar_id += 1
        # H3 (kuzey) outer = t>0
        rn3 = f"H3_{i}"
        _add_to_road(rn3, objects=barrier_object(bar_id, seg_len / 2, +bar_t,
                                                  seg_len, height=bar_h))
        bar_id += 1

    # V0 (bati cevre) - outer = t>0 (bati = sola - native PI/2 heading)
    # V3 (dogu cevre) - outer = t<0 (dogu = saga)
    for j in range(NROW):
        seg_len = HY[j + 1] - HY[j] - 2 * JR
        rn0 = f"V0_{j}"
        if not _cep_overlaps_V(0, j):
            _add_to_road(rn0, objects=barrier_object(bar_id, seg_len / 2, +bar_t,
                                                     seg_len, height=bar_h))
            bar_id += 1
        else:
            # D-sol cep agzi: along=31 -> y=27.5..34.5; V0_1 = y=31..42
            for sub_s, sub_len in _segment_minus_cep_y(0, j, "W"):
                _add_to_road(rn0, objects=barrier_object(
                    bar_id, sub_s + sub_len / 2, +bar_t, sub_len, height=bar_h))
                bar_id += 1
        rn3 = f"V3_{j}"
        # V3_2 (j=2): y=52..63, park sag tarafa baglanir AMA park ayri ghost road.
        # Park notch'i V3 araliginda DEGIL (park y=43..63 yer kaplar, V3_2 y=52..63).
        # Park'in y araligi V3_2'nin alt yarisini overlap eder. Ama park ayri ghost
        # road oldugu icin V3'un dis kenarinda bariyer olabilir (V3 lane'ine engel olmaz).
        _add_to_road(rn3, objects=barrier_object(bar_id, seg_len / 2, -bar_t,
                                                  seg_len, height=bar_h))
        bar_id += 1

    # Dis ceplerin DIS kenarlarinda bariyer
    for d in DURAKLAR:
        if d.get("kind") != "dis":
            continue
        cep_name = f"Cep_{d['label']}"
        wa, dp = d["w_along"], d["depth"]
        # Cep heading: W/E -> PI/2, S/N -> 0
        # Outer = pist'ten en uzak yon:
        if d["side"] == "W":
            t_out = +(dp / 2 + 0.2)   # bati
        elif d["side"] == "E":
            t_out = -(dp / 2 + 0.2)
        elif d["side"] == "S":
            t_out = -(dp / 2 + 0.2)   # guney
        else:  # N
            t_out = +(dp / 2 + 0.2)
        # Uzun dis kenar
        _add_to_road(cep_name, objects=barrier_object(
            bar_id, wa / 2, t_out, wa, name=f"wall_{d['label']}", height=bar_h))
        bar_id += 1
        # Iki uctan kisa bariyer (cep'in ic dis tarafini kapatir)
        # s=0.15 ve s=wa-0.15, hdg=PI/2 (yola dik)
        _add_to_road(cep_name, objects=barrier_object(
            bar_id, 0.15, 0, dp, name=f"wall_{d['label']}_uc", height=bar_h, hdg=PI/2))
        bar_id += 1
        _add_to_road(cep_name, objects=barrier_object(
            bar_id, wa - 0.15, 0, dp, name=f"wall_{d['label']}_uc", height=bar_h, hdg=PI/2))
        bar_id += 1

    # Pist_ust_uzanti (J102'den dogu): kuzey, guney ve dogu (dead-end) bariyerleri
    tue_len = (PARK_X + PARK_W) - (VX[3] + JR)   # 17
    _add_to_road("Pist_ust_uzanti", objects=barrier_object(
        bar_id, tue_len / 2, +bar_t, tue_len, name="wall_TUE_N", height=bar_h))
    bar_id += 1
    _add_to_road("Pist_ust_uzanti", objects=barrier_object(
        bar_id, tue_len / 2, -bar_t, tue_len, name="wall_TUE_S", height=bar_h))
    bar_id += 1
    # Dead-end dogu ucu: yola dik
    _add_to_road("Pist_ust_uzanti", objects=barrier_object(
        bar_id, tue_len - 0.15, 0, 2 * LW + 0.6, name="wall_TUE_E",
        height=bar_h, hdg=PI/2))
    bar_id += 1


def _cep_overlaps_H(j, i):
    """H{j}_{i} segmenti uzerinde bir dis cep agzi var mi?"""
    if j not in (0, 3):
        return False
    side = "S" if j == 0 else "N"
    x0 = VX[i] + JR
    x1 = VX[i + 1] - JR
    for d in DURAKLAR:
        if d.get("kind") == "dis" and d["side"] == side:
            cep_x0 = d["along"] - d["w_along"] / 2
            cep_x1 = d["along"] + d["w_along"] / 2
            if cep_x0 < x1 and cep_x1 > x0:
                return True
    return False


def _cep_overlaps_V(i, j):
    """V{i}_{j} segmenti uzerinde bir dis cep agzi var mi?"""
    if i not in (0, 3):
        return False
    side = "W" if i == 0 else "E"
    y0 = HY[j] + JR
    y1 = HY[j + 1] - JR
    for d in DURAKLAR:
        if d.get("kind") == "dis" and d["side"] == side:
            cep_y0 = d["along"] - d["w_along"] / 2
            cep_y1 = d["along"] + d["w_along"] / 2
            if cep_y0 < y1 and cep_y1 > y0:
                return True
    return False


def _segment_minus_cep_x(i, j, side):
    """H{j}_{i} segmentini dis cep x-mouth'larindan kesip alt segmentler dondurur.
    Donus: [(s_start, length), ...] - segment kendi koordinatinda (s=0 at x=VX[i]+JR)."""
    seg_x0 = VX[i] + JR
    seg_x1 = VX[i + 1] - JR
    seg_len = seg_x1 - seg_x0
    cuts = []
    for d in DURAKLAR:
        if d.get("kind") == "dis" and d["side"] == side:
            cep_x0 = max(d["along"] - d["w_along"] / 2, seg_x0)
            cep_x1 = min(d["along"] + d["w_along"] / 2, seg_x1)
            if cep_x0 < cep_x1:
                cuts.append((cep_x0 - seg_x0, cep_x1 - seg_x0))
    cuts.sort()
    sub_segs = []
    prev = 0
    for c0, c1 in cuts:
        if c0 > prev:
            sub_segs.append((prev, c0 - prev))
        prev = max(prev, c1)
    if prev < seg_len:
        sub_segs.append((prev, seg_len - prev))
    return sub_segs


def _segment_minus_cep_y(i, j, side):
    """V{i}_{j} segmentini dis cep y-mouth'larindan keser. Benzer mantik."""
    seg_y0 = HY[j] + JR
    seg_y1 = HY[j + 1] - JR
    seg_len = seg_y1 - seg_y0
    cuts = []
    for d in DURAKLAR:
        if d.get("kind") == "dis" and d["side"] == side:
            cep_y0 = max(d["along"] - d["w_along"] / 2, seg_y0)
            cep_y1 = min(d["along"] + d["w_along"] / 2, seg_y1)
            if cep_y0 < cep_y1:
                cuts.append((cep_y0 - seg_y0, cep_y1 - seg_y0))
    cuts.sort()
    sub_segs = []
    prev = 0
    for c0, c1 in cuts:
        if c0 > prev:
            sub_segs.append((prev, c0 - prev))
        prev = max(prev, c1)
    if prev < seg_len:
        sub_segs.append((prev, seg_len - prev))
    return sub_segs


def build_network():
    EXTRA_PER_ROAD.clear()
    _compute_misyon_extras()
    _compute_barrier_extras()

    roads = []
    junctions = []
    mark_obj_id = [5000]   # serit isareti object id counter (liste = mutable)

    # ----- BASE LAYER - pistin altinda asfalt-rengi koca zemin -----
    # Pist main = 73x73, park annex x'i 73->90'a uzanir. Margin ile 100x85
    # alani kapla (x: -5..95, y: -6..79). Yollar/adalar bunun ustune biner.
    # z_offset=-0.02 -> tum gercek yollar bunun ustunde renderlanir.
    base_rid = new_rid()
    roads.append(make_base_layer(base_rid, cx=45.0, cy=36.5,
                                  w=100.0, h=85.0, z_offset=-0.02))

    # ----- DIKEY YOL SEGMENTLERI -----
    # Her VX[i] icin, j=0..NROW-1: HY[j]+jr(i,j) -> HY[j+1]-jr(i,j+1)
    rid_V = {}   # (i, j) -> rid: VX[i] uzerinde HY[j] -> HY[j+1] segmenti
    for i in range(NCOL + 1):
        for j in range(NROW):
            jr_a = _jr_at(i, j)
            jr_b = _jr_at(i, j + 1)
            y0 = HY[j] + jr_a
            y1 = HY[j + 1] - jr_b
            seg_len = y1 - y0
            # TUNEL: V_(1,1) segmentinin ortasina tunel objesi yerlestir
            obj_xml = ""
            if (i, j) == (TUN_SEG_I, TUN_SEG_J):
                tun_s = max(0.0, (seg_len - TUN_LEN) / 2)
                tun_l = min(TUN_LEN, seg_len)
                obj_xml = tunnel_obj(tun_s, tun_l, "Tunel_ic")
            # Serit boyalari (solid kenar + center kesikli) - decal object'ler
            marks, mark_obj_id[0] = road_markings_xml(mark_obj_id[0], seg_len)
            obj_xml += marks
            # Misyon obje + bariyer ekstralar
            extra_sigs, extra_objs = _extra_for(f"V{i}_{j}")
            obj_xml += extra_objs
            rid = new_rid()
            roads.append(make_road(
                rid, f"V{i}_{j}", VX[i], y0, PI/2, seg_len,
                pred=("junction", str(JID[(i, j)]), None),
                succ=("junction", str(JID[(i, j + 1)]), None),
                objects_xml=obj_xml,
                signals_xml=extra_sigs,
            ))
            rid_V[(i, j)] = rid

    # ----- YATAY YOL SEGMENTLERI -----
    rid_H = {}   # (i, j) -> rid: HY[j] uzerinde VX[i] -> VX[i+1] segmenti
    for j in range(NROW + 1):
        for i in range(NCOL):
            jr_a = _jr_at(i, j)
            jr_b = _jr_at(i + 1, j)
            x0 = VX[i] + jr_a
            x1 = VX[i + 1] - jr_b
            seg_len = x1 - x0
            # Serit boyalari + misyon/bariyer ekstralar
            marks, mark_obj_id[0] = road_markings_xml(mark_obj_id[0], seg_len)
            extra_sigs, extra_objs = _extra_for(f"H{j}_{i}")
            rid = new_rid()
            roads.append(make_road(
                rid, f"H{j}_{i}", x0, HY[j], 0, seg_len,
                pred=("junction", str(JID[(i, j)]), None),
                succ=("junction", str(JID[(i + 1, j)]), None),
                objects_xml=marks + extra_objs,
                signals_xml=extra_sigs,
            ))
            rid_H[(i, j)] = rid

    # ----- PARK ENTRY (J111 E2'den dogu'ya park alanina) -----
    # Park artik daha alcakta (y=43..63), giris J111 (y=47) uzerinden.
    # Koridor kaldirildi: PARK_H=20 = 2*RW oldugu icin pc_len=0 olur.
    rid_PE = new_rid()
    pe_x0 = VX[3] + JR
    pe_len = (PARK_X + PARK_W/2) - pe_x0
    pe_marks, mark_obj_id[0] = road_markings_xml(mark_obj_id[0], pe_len)
    roads.append(make_road(
        rid_PE, "Park_giris", pe_x0, PARK_ENTRY_Y, 0, pe_len,
        pred=("junction", str(PARK_ENTRY_JID), None),
        objects_xml=pe_marks,
    ))

    # ----- PIST UST UZANTISI (J102 NE'den dogu'ya, park bitisine kadar) -----
    # Dead-end yol: J102 kavsagindan dogu (y=HY[3]=68) yonunde, x=73..90 (park
    # alaninin dogu kenarina denk gelir). Park alanina dokunmaz; ayri bir uzanti.
    rid_TUE = new_rid()
    tue_x0 = VX[3] + JR                         # 73
    tue_len = (PARK_X + PARK_W) - tue_x0        # 17
    tue_marks, mark_obj_id[0] = road_markings_xml(mark_obj_id[0], tue_len)
    tue_sigs, tue_objs = _extra_for("Pist_ust_uzanti")
    roads.append(make_road(
        rid_TUE, "Pist_ust_uzanti", tue_x0, HY[3], 0, tue_len,
        pred=("junction", "102", None),
        objects_xml=tue_marks + tue_objs,
        signals_xml=tue_sigs,
    ))

    # ----- DAL DICT'LERI (her kavsak icin N/E/S/W komsu yol) -----
    def b_N(i, j):
        if (i, j) in rid_V:
            return {"rid": rid_V[(i, j)], "hdg_out": PI/2, "cp": "start"}
        return None
    def b_S(i, j):
        if (i, j - 1) in rid_V:
            return {"rid": rid_V[(i, j - 1)], "hdg_out": 3*PI/2, "cp": "end"}
        return None
    def b_E(i, j):
        if (i, j) in rid_H:
            return {"rid": rid_H[(i, j)], "hdg_out": 0, "cp": "start"}
        return None
    def b_W(i, j):
        if (i - 1, j) in rid_H:
            return {"rid": rid_H[(i - 1, j)], "hdg_out": PI, "cp": "end"}
        return None

    # ----- KAVSAKLARI URET -----
    for (i, j), jid in JID.items():
        cx, cy = VX[i], HY[j]
        bN, bE, bS, bW = b_N(i, j), b_E(i, j), b_S(i, j), b_W(i, j)

        if jid == 130:    # DONEL ADA
            r, juc = roundabout_junction(jid, cx, cy, RA_LANE_R,
                b_N=bN, b_E=bE, b_S=bS, b_W=bW)
        elif jid == PARK_ENTRY_JID:  # park girisi olan kavsak
            # PE_branch: kavsaktan dogu yonune (park alanina) cikan kol
            PE_branch = {"rid": rid_PE, "hdg_out": 0, "cp": "start"}
            if bN is None and bE is None:        # NE kosesi (J102): T - W + S + E_park
                r, juc = t_junction(jid, cx, cy, m1=bW, m2=bS, side=PE_branch)
            elif bE is None:                     # E kenari T (orn. J111): 4-way ekleyerek
                r, juc = four_way_junction(jid, cx, cy,
                    b_N=bN, b_E=PE_branch, b_S=bS, b_W=bW, jr=JR)
            else:
                raise RuntimeError(f"PARK_ENTRY_JID={jid} icin uygun topoloji yok")
        elif jid == 102:  # NE kosesi: yeni Pist_ust_uzanti dogu kolu (T)
            TUE_branch = {"rid": rid_TUE, "hdg_out": 0, "cp": "start"}
            r, juc = t_junction(jid, cx, cy, m1=bW, m2=bS, side=TUE_branch)
        else:
            present = [b for b in (bN, bE, bS, bW) if b]
            n = len(present)
            if n == 2:    # KOSE
                r, juc = corner_junction(jid, cx, cy, present[0], present[1])
            elif n == 3:  # KENAR T
                if bN is None:
                    r, juc = t_junction(jid, cx, cy, m1=bW, m2=bE, side=bS)
                elif bS is None:
                    r, juc = t_junction(jid, cx, cy, m1=bW, m2=bE, side=bN)
                elif bE is None:
                    r, juc = t_junction(jid, cx, cy, m1=bN, m2=bS, side=bW)
                else:  # bW is None
                    r, juc = t_junction(jid, cx, cy, m1=bN, m2=bS, side=bE)
            elif n == 4:  # IC 4-way (TUN/RA disinda)
                r, juc = four_way_junction(jid, cx, cy,
                    b_N=bN, b_E=bE, b_S=bS, b_W=bW, jr=JR)
            else:
                continue
        roads += r
        junctions.append(juc)

    # ----- ADA YUZEYLERI (BLOCKS) - CARLA mesh icin ghost road -----
    # Her ada bir standalone ghost road (shoulder lanes) ile dolduruluyor.
    # Boylece CARLA'da arac bos alana dusmez, ada yuzeyi duz beyaz cizili gorunur.
    for bx, by, bw, bh, label in BLOCKS:
        rid = new_rid()
        cx_b, cy_b = bx + bw/2, by + bh/2
        roads.append(make_island_patch(rid, f"Ada_{label}", cx_b, cy_b, bw, bh))

    # ----- DIS DURAK CEPLERI + otobus duragi tabelasi + serit boyalari -----
    sig_id = 7000
    for d in DURAKLAR:
        if d.get("kind") == "dis":
            rid = new_rid()
            cep_sig = signal_xml(sig_id, d["w_along"] / 2, 0.0, "bus_stop")
            sig_id += 1
            # Serit boyalari (cep dar oldugu icin lane_w = depth/2)
            cep_marks, mark_obj_id[0] = road_markings_xml(
                mark_obj_id[0], d["w_along"], lane_w=d["depth"]/2)
            # Cep dis kenarlarinda bariyer (Pist'e dusmemek icin)
            cep_extra_sigs, cep_extra_objs = _extra_for(f"Cep_{d['label']}")
            roads.append(make_pocket_road(rid, f"Cep_{d['label']}",
                d["side"], d["along"], d["w_along"], d["depth"],
                signals_xml=cep_sig + cep_extra_sigs,
                objects_xml=cep_marks + cep_extra_objs))

    # ----- PARK ALANI dolgu + slot ayraclari + tabelalar -----
    # Park: x=73..90, y=53..73 (17 x 20). Slotlar SADECE SOL sutunda (x=73..81.5).
    # Sag sutun (x=81.5..90) aisle/manevra koridoru (Park_giris buradan icer).
    park_objs_xml = ""
    obj_id = 9000
    slot_h = 2.5
    n_slot = int(round(PARK_H / slot_h))    # 8 slot
    half_col = PARK_W / 4                    # 4.25 (sol sutun ortasi t-offset, isareti -)
    col_len = PARK_W / 2 - 0.5               # ~8.0 (slot cizgisi yan uzunlugu)
    for k in range(n_slot + 1):              # 9 ayrac (0..8)
        s_pos = k * slot_h
        park_objs_xml += park_line_object(obj_id, s_pos, -half_col, 0.15, col_len)
        obj_id += 1

    # Tabela: no_parking (alttaki 2. slot ortasi), parking (ustteki 2. slot ortasi) — sol sutun
    park_sigs_xml = ""
    park_sigs_xml += signal_xml(8001, slot_h * 1.5,            -half_col, "no_parking")
    park_sigs_xml += signal_xml(8002, slot_h * (n_slot - 1.5), -half_col, "parking")

    rid_PA = new_rid()
    roads.append(make_island_patch(rid_PA, "Park_zemin",
        PARK_X + PARK_W/2, PARK_Y + PARK_H/2, PARK_W, PARK_H,
        objects_xml=park_objs_xml, signals_xml=park_sigs_xml))

    return roads, junctions


# ===========================================================================
# 6) OpenDRIVE yazici
# ===========================================================================

def write_opendrive(roads_xml, junctions_xml, path):
    body = "\n".join(roads_xml)
    juncs = "\n".join(junctions_xml)
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<OpenDRIVE>
  <header revMajor="1" revMinor="5" name="Robotaksi_Pist_Full" version="3.0"
          date="2026-06-10T00:00:00"
          north="{TOTAL_H:.2f}" south="0" east="{TOTAL_W:.2f}" west="0"
          vendor="full-junction-builder">
    <geoReference><![CDATA[+proj=tmerc +lat_0=40.78996 +lon_0=29.50904 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs]]></geoReference>
  </header>
{body}
{juncs}
</OpenDRIVE>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"[xodr] {len(roads_xml)} yol, {len(junctions_xml)} junction -> {path}")


# ===========================================================================
# 7) Preview
# ===========================================================================

def preview(path):
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_aspect("equal")
    ax.set_facecolor("#2b2b2b")
    fig.patch.set_facecolor("#1c1c1c")

    ASPHALT = "#3c3c3c"; ISLAND = "#f4f4f4"; EDGE = "#e8e8e8"; DASH = "#f0f0f0"

    # Tum asfalt alanlari KENARSIZ ciz, sonradan tek bir dis kontur polygonu ekle.
    ax.add_patch(Rectangle((0, 0), MAIN_W, MAIN_H,
        facecolor=ASPHALT, edgecolor='none', zorder=1))
    # Park: duz dikdortgen (x=73..90, y=43..63)
    ax.add_patch(Rectangle((PARK_X, PARK_Y), PARK_W, PARK_H,
        facecolor=ASPHALT, edgecolor='none', zorder=1))
    # Pist ust uzantisi: J102'den dogu, x=73..90 at y=HY[3]+/-LW (6 m yol genisligi)
    ax.add_patch(Rectangle((PARK_X, HY[3] - LW), PARK_W, 2 * LW,
        facecolor=ASPHALT, edgecolor='none', zorder=1.5))

    # Dis durak cepleri (cevre yola YAPISIK): asfalt dolgu, kenarsiz.
    for d in DURAKLAR:
        if d.get("kind") != "dis":
            continue
        wa, dp = d["w_along"], d["depth"]
        s = d["side"]
        if s == "W":
            cx_, cy_ = (VX[0] - LW) - dp/2, d["along"]
            cw, ch = dp, wa
        elif s == "E":
            cx_, cy_ = (VX[-1] + LW) + dp/2, d["along"]
            cw, ch = dp, wa
        elif s == "S":
            cx_, cy_ = d["along"], (HY[0] - LW) - dp/2
            cw, ch = wa, dp
        elif s == "N":
            cx_, cy_ = d["along"], (HY[-1] + LW) + dp/2
            cw, ch = wa, dp
        ax.add_patch(Rectangle((cx_ - cw/2, cy_ - ch/2), cw, ch,
            facecolor=ASPHALT, edgecolor='none', zorder=1.5))

    for bx, by, bw, bh, label in BLOCKS:
        ax.add_patch(FancyBboxPatch((bx, by), bw, bh,
            boxstyle="round,pad=0,rounding_size=1.6",
            facecolor=ISLAND, edgecolor=EDGE, linewidth=1.6, zorder=3))
        ax.text(bx + bw/2, by + bh/2, label, ha="center", va="center",
                color="#9a9a9a", fontsize=9, zorder=4)

    # Yol orta serit kesikli cizgileri (her grid yolunun orta cizgisi)
    # KML referans: kesikli serit ~2 m dash + ~3 m gap
    def dash(x0, y0, x1, y1):
        ax.plot([x0, x1], [y0, y1], color=DASH, lw=1.0, ls=(0, (4, 3)),
                alpha=0.9, zorder=5)

    # Dikey yol orta serit cizgileri (her V uzerinde, kavsaklari atlayarak)
    for i in range(NCOL + 1):
        for j in range(NROW):
            jr_a = _jr_at(i, j)
            jr_b = _jr_at(i, j + 1)
            dash(VX[i], HY[j] + jr_a, VX[i], HY[j + 1] - jr_b)

    # Yatay yol orta serit cizgileri
    for j in range(NROW + 1):
        for i in range(NCOL):
            jr_a = _jr_at(i, j)
            jr_b = _jr_at(i + 1, j)
            dash(VX[i] + jr_a, HY[j], VX[i + 1] - jr_b, HY[j])

    # TUNEL (V1 yolunda B1-B2 arasi yol uzeri obje)
    ax.add_patch(FancyBboxPatch(
        (TUN_CX - TUN_W_VIS/2, TUN_CY - TUN_H_VIS/2),
        TUN_W_VIS, TUN_H_VIS,
        boxstyle="round,pad=0,rounding_size=0.8",
        facecolor="#2f6fe0", edgecolor="white", linewidth=1.6, zorder=7))
    ax.text(TUN_CX, TUN_CY, "T Ü N E L", ha="center", va="center", rotation=90,
            color="white", fontsize=10, fontweight="bold", zorder=8)
    for ada in (TUN_ADA_1, TUN_ADA_2):
        ax.add_patch(MplPoly(ada, closed=True, facecolor=ISLAND,
                     edgecolor=EDGE, linewidth=1.2, zorder=6))

    # Roundabout
    ax.add_patch(Circle((RA_CX, RA_CY), RA_OUTER_R, facecolor=ASPHALT,
        edgecolor=EDGE, linewidth=1.8, zorder=4))
    th = np.linspace(0, 2*PI, 120)
    ax.plot(RA_CX + RA_LANE_R*np.cos(th), RA_CY + RA_LANE_R*np.sin(th),
            color=DASH, lw=1.0, ls=(0, (5, 5)), zorder=5)
    ax.add_patch(Circle((RA_CX, RA_CY), RA_ISLAND_R, facecolor="#37c24a",
        edgecolor="white", linewidth=1.6, zorder=6))

    # Duraklar (cep asfalti zaten yukarida cizildi; burada sadece D markeri/ic durak)
    for d in DURAKLAR:
        if d["kind"] == "dis":
            wa, dp = d["w_along"], d["depth"]
            s = d["side"]
            if s == "W":   mx, my = (VX[0] - LW) - dp/2, d["along"]
            elif s == "E": mx, my = (VX[-1] + LW) + dp/2, d["along"]
            elif s == "S": mx, my = d["along"], (HY[0] - LW) - dp/2
            elif s == "N": mx, my = d["along"], (HY[-1] + LW) + dp/2
            # Mavi D markeri (durak tabelasi)
            ax.add_patch(Circle((mx, my), 1.2,
                facecolor="#2f6fe0", edgecolor="white",
                linewidth=1.2, zorder=8))
            ax.text(mx, my, "D", ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold", zorder=9)
        elif d["kind"] == "ic":
            # B3 icinde durak (mavi dikdortgen)
            x, y = d["cx"] - d["w"]/2, d["cy"] - d["h"]/2
            ax.add_patch(FancyBboxPatch((x, y), d["w"], d["h"],
                boxstyle="round,pad=0,rounding_size=0.4",
                facecolor="#2f6fe0", edgecolor="white",
                linewidth=1.4, zorder=7))
            ax.text(d["cx"], d["cy"], "D", ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold",
                    rotation=90, zorder=8)

    # ---- Tek bir dis kontur polygonu (pist + park + cepler birlikte) ----
    # CCW yonde dis sinir koordinatlari (sol-alt baslangic).
    outline = []
    # G dis cevre (sol-alttan saga, S-cep notch'u dahil)
    outline.append((0.0, 0.0))
    s_dur = [d for d in DURAKLAR if d.get("kind") == "dis" and d["side"] == "S"]
    for d in sorted(s_dur, key=lambda d: d["along"]):
        wa, dp = d["w_along"], d["depth"]
        outline.append((d["along"] - wa/2, 0.0))
        outline.append((d["along"] - wa/2, (HY[0] - LW) - dp))
        outline.append((d["along"] + wa/2, (HY[0] - LW) - dp))
        outline.append((d["along"] + wa/2, 0.0))
    outline.append((MAIN_W, 0.0))
    # E dis cevre: pist sag kenari yukari -> park notch -> geri -> ust uzanti notch -> ust
    outline.append((MAIN_W, PARK_Y))
    outline.append((PARK_X + PARK_W, PARK_Y))
    outline.append((PARK_X + PARK_W, PARK_Y + PARK_H))
    outline.append((MAIN_W, PARK_Y + PARK_H))
    # Pist ust uzanti notch (y=HY[3]-LW .. HY[3]+LW, x=73..90)
    outline.append((MAIN_W, HY[3] - LW))
    outline.append((PARK_X + PARK_W, HY[3] - LW))
    outline.append((PARK_X + PARK_W, HY[3] + LW))
    outline.append((MAIN_W, HY[3] + LW))
    outline.append((MAIN_W, MAIN_H))
    # K dis cevre (sagdan sola)
    outline.append((0.0, MAIN_H))
    # B dis cevre (yukaridan asagi, W-cep notch'u dahil)
    w_dur = [d for d in DURAKLAR if d.get("kind") == "dis" and d["side"] == "W"]
    for d in sorted(w_dur, key=lambda d: -d["along"]):
        wa, dp = d["w_along"], d["depth"]
        outline.append((0.0, d["along"] + wa/2))
        outline.append(((VX[0] - LW) - dp, d["along"] + wa/2))
        outline.append(((VX[0] - LW) - dp, d["along"] - wa/2))
        outline.append((0.0, d["along"] - wa/2))
    outline.append((0.0, 0.0))
    ax.add_patch(MplPoly(outline, closed=True,
        facecolor='none', edgecolor=EDGE, linewidth=2.0, zorder=11))

    # Park slot lines (XODR ile ayni): SADECE SOL sutun (x=73..81.5), y=53..73
    slot_h_p = 2.5
    n_slot_p = int(round(PARK_H / slot_h_p))
    for i in range(n_slot_p + 1):
        yy = PARK_Y + i * slot_h_p
        ax.plot([PARK_X + 0.5, PARK_X + PARK_W/2 - 0.5], [yy, yy],
                color=EDGE, lw=0.8, zorder=3)

    # Junction noktalari (JID dict'inden otomatik)
    for (i, j), jid in JID.items():
        jx, jy = VX[i], HY[j]
        suf = "(TUN)" if jid == 120 else "(RA)" if jid == 130 else ""
        ax.add_patch(Circle((jx, jy), 0.5, facecolor="#ff5252",
                            edgecolor="white", linewidth=0.6, zorder=9))
        ax.text(jx + 0.6, jy + 0.6, f"J{jid}{suf}", color="#ff8a80",
                fontsize=6, zorder=10)

    # ---- MISYON OBJELERI ----
    for m in MISYON_OBJELERI:
        mx_, my_ = m["x"], m["y"]
        if m["kind"] == "sign":
            ax.add_patch(Rectangle((mx_ - 0.7, my_ - 0.7), 1.4, 1.4,
                facecolor="#ffb000", edgecolor="white", linewidth=1.2, zorder=10))
            ax.text(mx_, my_ + 1.4, m["label"], ha="center", va="bottom",
                    color="#ffd45e", fontsize=6, fontweight="bold", zorder=11)
        elif m["kind"] == "obstacle":
            ax.add_patch(Rectangle((mx_ - m["w"]/2, my_ - m["h"]/2), m["w"], m["h"],
                facecolor="#ff3030", edgecolor="white", linewidth=1.5, zorder=10))
            ax.text(mx_, my_ + m["h"]/2 + 0.6, m["label"], ha="center", va="bottom",
                    color="#ff6f6f", fontsize=6, fontweight="bold", zorder=11)
        elif m["kind"] == "traffic_light":
            ax.add_patch(Rectangle((mx_ - 0.7, my_ - 1.6), 1.4, 3.2,
                facecolor="#181818", edgecolor="white", linewidth=1.0, zorder=10))
            for dy_, col in [(+1.05, "#ff3030"), (0, "#ffd24a"), (-1.05, "#3ae65c")]:
                ax.add_patch(Circle((mx_, my_ + dy_), 0.4,
                    facecolor=col, edgecolor="white", linewidth=0.5, zorder=11))
            ax.text(mx_, my_ + 2.0, m["label"], ha="center", va="bottom",
                    color="white", fontsize=6, fontweight="bold", zorder=12)

    # ---- MISYON WAYPOINT YOLU (CCW rota) ----
    wps = lap_waypoints()
    wp_x = [w[0] for w in wps]
    wp_y = [w[1] for w in wps]
    ax.plot(wp_x, wp_y, color="#3ae6ff", lw=1.4, ls="-",
            alpha=0.85, zorder=9, marker='o', markersize=3.0)
    ax.text(wp_x[-1] + 1, wp_y[-1] + 1, "PARK", ha="left", va="bottom",
            color="#3ae6ff", fontsize=7, fontweight="bold", zorder=12)

    # Spawn (yeni: J102 yakini, batiya bakiyor)
    sx, sy = SPAWN_X, SPAWN_Y
    ax.add_patch(Circle((sx, sy), 0.8, facecolor="#ff7a3c",
                        edgecolor="white", linewidth=1.0, zorder=12))
    # Spawn yon oku (yaw=180 -> bati)
    yaw_rad = math.radians(SPAWN_YAW)
    ax.annotate("", xy=(sx + 4*math.cos(yaw_rad), sy + 4*math.sin(yaw_rad)),
                xytext=(sx, sy),
                arrowprops=dict(arrowstyle="->", color="#ff7a3c", linewidth=2),
                zorder=12)
    ax.text(sx + 2, sy + 2.5, "Spawn (J102)", color="#ff7a3c",
            fontsize=8, fontweight="bold", zorder=12)

    ax.set_xlim(-RW - 2, TOTAL_W + 2)
    ax.set_ylim(-RW - 2, TOTAL_H + 2)
    ax.set_xlabel("X (m)", color="#cccccc")
    ax.set_ylabel("Y (m)", color="#cccccc")
    ax.tick_params(colors="#999999")
    ax.set_title("Robotaksi Pist v3 - tam baglantili junction'lar",
                 color="#eeeeee")
    ax.grid(True, alpha=0.12, color="white")
    fig.tight_layout()
    fig.savefig(path, dpi=130, facecolor="#1c1c1c")
    plt.close(fig)
    print(f"[preview] -> {path}")


# ===========================================================================
# 8) JSON + spawn script
# ===========================================================================

def lap_waypoints():
    """Misyon rotasi: J102 baslangic -> CCW H3 bati (engelde SLALOM)
    -> J108'de guneye don -> tunelden gec -> D-alt duragi -> dogu H0
    -> kuzey V3 -> J111 park girisi -> park yapilabilir slot."""
    H_OUTER_N = HY[3] + LW / 2     # 69.5 - H3 kuzey (sol) serit - CCW bati yonu
    H_OUTER_S = HY[3] - LW / 2     # 66.5 - H3 guney (sag) serit - slalom kacis serit
    H_BOTTOM_S = HY[0] - LW / 2    #  3.5 - H0 guney serit (CCW dogu yonu)
    V_W_SOUTH = TUN_CX - LW / 2    # 24.5 - V1 bati serit (CCW guney yonu)
    V_E_NORTH = VX[3] + LW / 2     # 69.5 - V3 dogu serit (CCW kuzey yonu)
    # Park yapilabilir slot (ust slot, "parking" tabelasinin oldugu yer)
    slot_h = 2.5
    n_slot = int(round(PARK_H / slot_h))
    park_ok_y = PARK_Y + slot_h * (n_slot - 1.5)        # ust slot ortasi
    park_ok_x = PARK_X + PARK_W / 2 - PARK_W / 4        # sol sutun ortasi
    # Engel @ (57.5, 69.5) - kuzey serit. Slalom: kuzey -> guney -> kuzey.
    return [
        (SPAWN_X,     SPAWN_Y),       # 1. baslangic (J102 yakini, kuzey serit)
        # --- SLALOM (engel etrafinda serit degisimi) ---
        (61.0,        H_OUTER_N),     # 2. engel oncesi yaklasim
        (59.0,        H_OUTER_S),     # 3. guneye serit degisimi (engel basliyor)
        (55.0,        H_OUTER_S),     # 4. engeli guney serit ile gec
        (52.0,        H_OUTER_N),     # 5. kuzey serite geri don (slalom bitis)
        # --- C2 trafik isigi, sonra J108 ---
        (40.0,        H_OUTER_N),     # 6. trafik isigi onunde (kirmizi/yesil)
        (28.0,        H_OUTER_N),     # 7. J108 onunde (saga don tabelasi)
        # --- J108'de guneye don, tunelden gec ---
        (V_W_SOUTH,   60.0),          # 8. V1_2 ile guney
        (V_W_SOUTH,   TUN_CY),        # 9. tunel ortasi
        (V_W_SOUTH,   15.0),          # 10. V1_0 ile guney
        (TUN_CX,      0.25),          # 11. D-alt duragi (cep merkez)
        # --- H0 dogu, V3 kuzey, park girisi ---
        (32.0,        H_BOTTOM_S),    # 12. H0 dogu - durakdan sonra
        (60.0,        H_BOTTOM_S),    # 13. H0 dogu - J101 yakini
        (V_E_NORTH,   15.0),          # 14. V3_0 kuzey
        (V_E_NORTH,   40.0),          # 15. V3_1 kuzey
        (V_E_NORTH,   PARK_ENTRY_Y),  # 16. J111 (park girisi 4-way)
        (PARK_X + PARK_W/2, PARK_ENTRY_Y),  # 17. Park_giris yolu
        (park_ok_x,   park_ok_y),     # 18. park yapilabilir slot
    ]

def write_layout_json(path):
    out = dict(
        meta=dict(main_w=MAIN_W, main_h=MAIN_H, total_w=TOTAL_W, total_h=TOTAL_H,
                  lane_width=LW, road_width=RW, junction_radius=JR,
                  junction_radius_ra=JR_RA),
        vertical_roads_x=VX, horizontal_roads_y=HY,
        blocks=[dict(x=b[0], y=b[1], w=b[2], h=b[3], label=b[4]) for b in BLOCKS],
        tunnel=dict(cx=TUN_CX, cy=TUN_CY, length=TUN_LEN, width=TUN_W_VIS,
                    type="road-object", on_road_segment="V1_1"),
        roundabout=dict(cx=RA_CX, cy=RA_CY, island_r=RA_ISLAND_R,
                        outer_r=RA_OUTER_R, lane_r=RA_LANE_R, junction_id=130),
        duraklar=DURAKLAR,
        parking=dict(x=PARK_X, y=PARK_Y, w=PARK_W, h=PARK_H,
                     entry_y=PARK_ENTRY_Y, junction_id=PARK_ENTRY_JID),
        spawn=dict(x=SPAWN_X, y=SPAWN_Y, z=SPAWN_Z, yaw=SPAWN_YAW),
        misyon_objeleri=MISYON_OBJELERI,
        waypoints=[dict(x=x, y=y) for x, y in lap_waypoints()],
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"[json] -> {path}")

def write_spawn_script(path):
    wps = lap_waypoints()
    wp_lines = ",\n    ".join(f"carla.Location(x={x:.2f}, y={y:.2f}, z=0.5)"
                             for x, y in wps)
    script = f'''#!/usr/bin/env python3
"""CARLA Pist - spawn (J102 yakini, CCW misyon) + waypoint takip."""
import argparse, math, os, time
import carla

XODR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pist.xodr")
SPAWN = carla.Transform(carla.Location(x={SPAWN_X:.2f}, y={SPAWN_Y:.2f}, z={SPAWN_Z:.2f}),
                        carla.Rotation(yaw={SPAWN_YAW:.1f}))
WAYPOINTS = [
    {wp_lines}
]

def load_map(client):
    with open(XODR, encoding="utf-8") as f:
        xodr = f.read()
    params = carla.OpendriveGenerationParameters(
        vertex_distance=1.0, max_road_length=50.0,
        wall_height=1.0, additional_width=1.0,
        smooth_junctions=True, enable_mesh_visibility=True)
    return client.generate_opendrive_world(xodr, params)

def spawn(world):
    bp = world.get_blueprint_library().filter("vehicle.tesla.model3")[0]
    try:
        v = world.spawn_actor(bp, SPAWN)
    except RuntimeError:
        v = world.spawn_actor(bp, world.get_map().get_spawn_points()[0])
    spec = world.get_spectator()
    spec.set_transform(carla.Transform(
        carla.Location(x=v.get_location().x, y=v.get_location().y, z=55),
        carla.Rotation(pitch=-90)))
    return v

def follow(v, wps):
    c = carla.VehicleControl()
    for wp in wps:
        for _ in range(500):
            loc = v.get_location()
            if loc.distance(wp) < 2.5: break
            yaw = v.get_transform().rotation.yaw
            t = math.degrees(math.atan2(wp.y - loc.y, wp.x - loc.x))
            d = (t - yaw + 540) % 360 - 180
            c.throttle, c.steer, c.brake = 0.35, max(-1.0, min(1.0, d/45)), 0.0
            v.apply_control(c); time.sleep(0.05)
    c.throttle, c.brake = 0.0, 1.0
    v.apply_control(c)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", action="store_true")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=2000)
    a = ap.parse_args()
    client = carla.Client(a.host, a.port); client.set_timeout(20.0)
    world = load_map(client) if a.load else client.get_world()
    time.sleep(2)
    v = spawn(world)
    try: follow(v, WAYPOINTS)
    finally: v.destroy()

if __name__ == "__main__":
    main()
'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"[spawn] -> {path}")


def write_scenario_xosc(path):
    """esmini icin manuel kontrol scenarosu.
    Ego entity'sine InteractiveController atanir VE ActivateControllerAction
    ile aktiflestirilir (esminiController = InteractiveController).
    Klavye kontrolu: ok/WASD - gas/fren/yon.
    Kullanim:
       esmini --osc pist_scenario.xosc --window 100 100 1600 900
    """
    h_rad = math.radians(SPAWN_YAW)
    xosc = f'''<?xml version="1.0" encoding="UTF-8"?>
<OpenSCENARIO>
  <FileHeader revMajor="1" revMinor="2" date="2026-06-14T00:00:00"
              description="Robotaksi Pist - tek ego (manuel kontrol)"
              author="build_pist_map"/>
  <ParameterDeclarations/>
  <CatalogLocations/>
  <RoadNetwork>
    <LogicFile filepath="pist.xodr"/>
  </RoadNetwork>
  <Entities>
    <ScenarioObject name="Ego">
      <Vehicle name="car_white" vehicleCategory="car">
        <ParameterDeclarations/>
        <Performance maxSpeed="55" maxAcceleration="10" maxDeceleration="10"/>
        <BoundingBox>
          <Center x="1.4" y="0.0" z="0.9"/>
          <Dimensions width="2.0" length="5.0" height="1.8"/>
        </BoundingBox>
        <Axles>
          <FrontAxle maxSteering="0.523598" wheelDiameter="0.6" trackWidth="1.7"
                     positionX="2.8" positionZ="0.3"/>
          <RearAxle  maxSteering="0.0"      wheelDiameter="0.6" trackWidth="1.7"
                     positionX="0.0" positionZ="0.3"/>
        </Axles>
        <Properties>
          <Property name="model_id" value="0"/>
        </Properties>
      </Vehicle>
      <ObjectController>
        <Controller name="InteractiveDriver">
          <Properties>
            <Property name="esminiController" value="InteractiveController"/>
          </Properties>
        </Controller>
      </ObjectController>
    </ScenarioObject>
  </Entities>
  <Storyboard>
    <Init>
      <Actions>
        <Private entityRef="Ego">
          <PrivateAction>
            <TeleportAction>
              <Position>
                <WorldPosition x="{SPAWN_X:.3f}" y="{SPAWN_Y:.3f}" z="0"
                               h="{h_rad:.6f}" p="0" r="0"/>
              </Position>
            </TeleportAction>
          </PrivateAction>
          <PrivateAction>
            <ControllerAction>
              <ActivateControllerAction longitudinal="true" lateral="true"/>
            </ControllerAction>
          </PrivateAction>
        </Private>
      </Actions>
    </Init>
    <Story name="MainStory">
      <Act name="MainAct">
        <ManeuverGroup name="MainGroup" maximumExecutionCount="1">
          <Actors selectTriggeringEntities="false">
            <EntityRef entityRef="Ego"/>
          </Actors>
        </ManeuverGroup>
        <StartTrigger>
          <ConditionGroup>
            <Condition name="StartCond" delay="0" conditionEdge="rising">
              <ByValueCondition>
                <SimulationTimeCondition value="0" rule="greaterOrEqual"/>
              </ByValueCondition>
            </Condition>
          </ConditionGroup>
        </StartTrigger>
      </Act>
      <StopTrigger/>
    </Story>
    <StopTrigger/>
  </Storyboard>
</OpenSCENARIO>
'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(xosc)
    print(f"[xosc] -> {path}")


def write_misyon_xosc(path, speed=6.0):
    """esmini icin OTO-DEMO misyon scenarosu: aracin slalom + tum rota'yi
    otomatik takip ettigi version. FollowTrajectoryAction (position mode)."""
    wps = lap_waypoints()
    # Kumulatif zaman (sabit hiz ile)
    times = [0.0]
    for i in range(1, len(wps)):
        dx = wps[i][0] - wps[i - 1][0]
        dy = wps[i][1] - wps[i - 1][1]
        dist = math.hypot(dx, dy)
        times.append(times[-1] + dist / speed)
    # Polyline vertex XML'i
    vertices = []
    for i, ((x, y), t) in enumerate(zip(wps, times)):
        if i < len(wps) - 1:
            nx, ny = wps[i + 1]
            h = math.atan2(ny - y, nx - x)
        else:
            h = math.atan2(y - wps[i - 1][1], x - wps[i - 1][0])
        vertices.append(
            f'              <Vertex time="{t:.3f}">\n'
            f'                <Position>\n'
            f'                  <WorldPosition x="{x:.3f}" y="{y:.3f}" '
            f'z="{SPAWN_Z:.3f}" h="{h:.4f}" p="0" r="0"/>\n'
            f'                </Position>\n'
            f'              </Vertex>'
        )
    polyline = "\n".join(vertices)
    h_init = math.radians(SPAWN_YAW)

    xosc = f'''<?xml version="1.0" encoding="UTF-8"?>
<OpenSCENARIO>
  <FileHeader revMajor="1" revMinor="2" date="2026-06-14T00:00:00"
              description="Robotaksi Misyon Demo - slalom + tunel + durak + park"
              author="build_pist_map"/>
  <ParameterDeclarations/>
  <CatalogLocations/>
  <RoadNetwork>
    <LogicFile filepath="pist.xodr"/>
  </RoadNetwork>
  <Entities>
    <ScenarioObject name="Ego">
      <Vehicle name="car_white" vehicleCategory="car">
        <ParameterDeclarations/>
        <Performance maxSpeed="55" maxAcceleration="10" maxDeceleration="10"/>
        <BoundingBox>
          <Center x="1.4" y="0.0" z="0.9"/>
          <Dimensions width="2.0" length="5.0" height="1.8"/>
        </BoundingBox>
        <Axles>
          <FrontAxle maxSteering="0.523598" wheelDiameter="0.6" trackWidth="1.7"
                     positionX="2.8" positionZ="0.3"/>
          <RearAxle  maxSteering="0.0"      wheelDiameter="0.6" trackWidth="1.7"
                     positionX="0.0" positionZ="0.3"/>
        </Axles>
        <Properties>
          <Property name="model_id" value="0"/>
        </Properties>
      </Vehicle>
    </ScenarioObject>
  </Entities>
  <Storyboard>
    <Init>
      <Actions>
        <Private entityRef="Ego">
          <PrivateAction>
            <TeleportAction>
              <Position>
                <WorldPosition x="{SPAWN_X:.3f}" y="{SPAWN_Y:.3f}" z="{SPAWN_Z:.3f}"
                               h="{h_init:.6f}" p="0" r="0"/>
              </Position>
            </TeleportAction>
          </PrivateAction>
          <PrivateAction>
            <RoutingAction>
              <FollowTrajectoryAction>
                <Trajectory name="MisyonRotasi" closed="false">
                  <ParameterDeclarations/>
                  <Shape>
                    <Polyline>
{polyline}
                    </Polyline>
                  </Shape>
                </Trajectory>
                <TimeReference>
                  <Timing domainAbsoluteRelative="relative" scale="1" offset="0"/>
                </TimeReference>
                <TrajectoryFollowingMode followingMode="position"/>
              </FollowTrajectoryAction>
            </RoutingAction>
          </PrivateAction>
        </Private>
      </Actions>
    </Init>
    <Story name="MainStory">
      <Act name="MainAct">
        <ManeuverGroup name="MainGroup" maximumExecutionCount="1">
          <Actors selectTriggeringEntities="false">
            <EntityRef entityRef="Ego"/>
          </Actors>
        </ManeuverGroup>
        <StartTrigger>
          <ConditionGroup>
            <Condition name="StartCond" delay="0" conditionEdge="rising">
              <ByValueCondition>
                <SimulationTimeCondition value="0" rule="greaterOrEqual"/>
              </ByValueCondition>
            </Condition>
          </ConditionGroup>
        </StartTrigger>
      </Act>
      <StopTrigger/>
    </Story>
    <StopTrigger/>
  </Storyboard>
</OpenSCENARIO>
'''
    with open(path, "w", encoding="utf-8") as f:
        f.write(xosc)
    print(f"[xosc-misyon] -> {path}")


# ===========================================================================
if __name__ == "__main__":
    print(f"[geom] ana {MAIN_W:.0f}x{MAIN_H:.0f} m + park {PARK_W:.0f}x{PARK_H:.0f}")
    print(f"[geom] VX={VX}, HY={HY}")
    print(f"[geom] TUNEL (yol obj) @ ({TUN_CX},{TUN_CY}), RA J130 @ ({RA_CX},{RA_CY})")
    roads, junctions = build_network()
    write_opendrive(roads, junctions, os.path.join(HERE, "pist.xodr"))
    preview(os.path.join(HERE, "pist_preview.png"))
    write_layout_json(os.path.join(HERE, "pist_layout.json"))
    write_spawn_script(os.path.join(HERE, "spawn_ve_rota.py"))
    write_scenario_xosc(os.path.join(HERE, "pist_scenario.xosc"))
    write_misyon_xosc(os.path.join(HERE, "pist_misyon.xosc"))
    print(f"\n[OK] {len(junctions)} junction + {len(roads)} yol uretildi.")
