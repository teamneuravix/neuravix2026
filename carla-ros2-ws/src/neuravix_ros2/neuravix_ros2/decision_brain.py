#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NeuraVix karar beyni (FSM) - CARLA'dan / gerçek araçtan bağımsız çekirdek.

neuravix_control_node.py (CARLA sim) ve neuravix_control_node_real.py (gerçek
Bee1 aracı) bu modülü ortak kullanır. Bu dosyada CARLA'ya veya araca özel hiçbir
şey olmamalı — sadece /master mesajlarından karar üreten saf mantık. Sim/gerçek
farkı sadece o iki dosyadaki ROS I/O (mesaj tipi, topic adı) katmanındadır.
"""

import time
import math
from enum import Enum

from .astar_planner import AStarPlanner


# ================================================================
# ROTA — pist_layout.json koordinatları (pist/OpenDRIVE)
# carla-ros-bridge: ros_x = pist_x, ros_y = pist_y
# NOT: Bu ROUTE CARLA pistine özeldir. Gerçek arac/pist için anlamsızdır;
# odometri gelmezse (gerçek araçta ilk fazda olduğu gibi) pure-pursuit
# devre dışı kalır ve FSM tek başına (şerit+tabela+engel) sürer.
# ================================================================
WP_REACH    = 4.0    # (m) waypoint'e ulaşma eşiği
WP_STR_GAIN = 0.7    # heading hatası (°) → Alkar birim katsayısı

ROUTE = [
    dict(x=72.0, y=70.0),
    dict(x=67.0, y=70.0),
    dict(x=64.0, y=65.5),
    dict(x=60.0, y=65.5),
    dict(x=56.0, y=70.0),
    dict(x=45.0, y=70.0),
    dict(x=34.0, y=70.0),
    dict(x=29.0, y=70.0),
    dict(x=25.0, y=64.0),
    dict(x=24.5, y=55.0),
    dict(x=24.5, y=45.0),
    dict(x=26.0, y=36.5),
    dict(x=26.0, y=26.0),
    dict(x=36.0, y=23.5),
    dict(x=47.0, y=25.0),
    dict(x=47.0, y=33.0),
    dict(x=51.0, y=36.5),
    dict(x=53.0, y=36.5),
    dict(x=49.0, y=40.0),
    dict(x=47.0, y=47.0),
    dict(x=58.0, y=47.0),
    dict(x=68.0, y=47.0),
    dict(x=73.0, y=50.0),
    dict(x=78.0, y=55.0),
    dict(x=78.0, y=59.0),
]

# pist 73x73 m → A* grid 60x60 hücre
GRID_SCALE = 60.0 / 73.0


# ================================================================
# /master mesaj id'leri
# ================================================================
ID_LANE     = 2
ID_SIGN     = 3
ID_OBSTACLE = 4
ID_PLANNER  = 5


# ================================================================
# TABELA / IŞIK SINIF ID'LERİ
# ================================================================
TRESPASS       = 0
GIRILMEZ       = 1
ILERI_SOL      = 2
ILERI_SAG      = 3
SOLA_DON       = 4
HIZ_20         = 5
HIZ_30         = 6
HIZ_20B        = 7
SAGA_DON       = 8
SAGA_DON_YASAK = 9
SOLA_DON_YASAK = 10
DUR            = 11
PARK_YASAK     = 12
PARK           = 13
DURAK          = 14
KIRMIZI_ISIK   = 15
SARI_ISIK      = 16
YESIL_ISIK     = 17
ENGELLI_PARK   = 18
KAVSAK         = 19
YAYA_GECIDI    = 20
IKI_YON        = 21
ILERI          = 22
TUNEL          = 23

SIGN_NAMES = {
    TRESPASS: "trespass", GIRILMEZ: "girilmez", ILERI_SOL: "ileri_sol",
    ILERI_SAG: "ileri_sag", SOLA_DON: "sola_don", HIZ_20: "hiz_20",
    HIZ_30: "hiz_30", HIZ_20B: "hiz_20b", SAGA_DON: "saga_don",
    SAGA_DON_YASAK: "saga_don_yasak", SOLA_DON_YASAK: "sola_don_yasak",
    DUR: "dur", PARK_YASAK: "park_yasak", PARK: "park", DURAK: "durak",
    KIRMIZI_ISIK: "kirmizi_isik", SARI_ISIK: "sari_isik",
    YESIL_ISIK: "yesil_isik", ENGELLI_PARK: "engelli_park", KAVSAK: "kavsak",
    YAYA_GECIDI: "yaya_gecidi", IKI_YON: "iki_yon", ILERI: "ileri",
    TUNEL: "tunel",
}


# ================================================================
# DURUM MAKİNESİ
# ================================================================
class DriveState(Enum):
    LANE_FOLLOW       = 0
    RED_LIGHT_STOP    = 1
    STOP_SIGN         = 2
    CROSSWALK_STOP    = 3
    BUS_STOP          = 4
    TURN_LEFT         = 5
    TURN_RIGHT        = 6
    GO_STRAIGHT_LEFT  = 7
    GO_STRAIGHT_RIGHT = 8
    OBSTACLE_STOP     = 9
    OBSTACLE_AVOID    = 10
    PARK_SEARCH       = 11
    PARKING           = 12
    EMERGENCY         = 13


# ================================================================
# KARAR BEYNİ (FSM)
# ================================================================
class Alkar_Function4:

    def __init__(self):
        self.steering_angle = 45
        self.target_speed   = 12.0
        self.brake          = 0
        self.signal_status  = 0
        self.state          = DriveState.LANE_FOLLOW

        self.default_speed = 12.0
        self.slow_speed    = 6.0
        self.turn_speed    = 6.0    # FIX: 5.0 → 6.0 km/h (dönüş yayı ~11m @ R≈7m)
        self.park_speed    = 3.0
        self.speed_limit   = 20.0

        self.image_center = (1280 / 2, 720 / 2)

        self.sign_counts        = {i: 0 for i in range(24)}
        self.last_sign_time     = {}
        self.sign_confirm_count = 3
        self.sign_window_sec    = 2.0
        self.sign_cooldown      = {}
        self.default_cooldown   = 4.0

        self.state_start_time      = time.time()
        self.red_light_seen_time   = 0.0
        self.green_light_seen_time = 0.0

        self.stop_wait_sec      = 3.0
        self.crosswalk_wait_sec = 5.0

        self.bus_stop_align_time = 2.0
        self.bus_stop_wait_sec   = 17.0
        self.bus_stop_exit_time  = 2.0

        self.left_turn_angle          = 73
        self.right_turn_angle         = 17
        self.turn_recover_angle_left  = 50   # FIX: 55 → 50 (daha agresif düzeltme)
        self.turn_recover_angle_right = 40   # FIX: 35 → 40

        self.stop_distance        = 2.2
        # ESIKLER AYRILDI (2026-07-21, algi2/3/4 bag analizi): eskiden
        # slow_distance hem "yavaşla" hem "slaloma gir" eşiğiydi; 9 slalom
        # girişinin 7'si front 4.45-4.99 m'de, yani eşiğin tam dibinde
        # tetiklenmişti. Artık 5 m sadece yavaşlatır (şeritte kalınır),
        # slaloma girmek için engelin avoid_distance'a kadar yaklaşması VE
        # tetiğin avoid_confirm_time boyunca sürmesi gerekir.
        self.slow_distance        = 6.0   # yavaşla, şeridi bırakma
        # 3.0 -> 4.5 (2026-08-03, masa simülasyonu bulgusu): onay süresi
        # boyunca araç yaklaşmaya devam ediyor; geç tetikte weave başlarken
        # front stop_distance'ın dibine iniyor — o mesafede tam kilitle bile
        # engelin yanından dönmeye GEOMETRİK yer kalmıyor (R=L/tan(31°)≈3.1 m).
        # Pist engeli 1.4 m GENİŞ kutu: köşesi ön koridor kenarında uzun süre
        # kaldığından 4.0 bile dardı (escape ortasında front 1.0'a düşüp acil
        # koruma tetikleniyordu); 4.5 + slow_distance 6.0 ile manevra, engel
        # köşesi koridordan çıkmadan acil eşiğe inmeden tamamlanıyor.
        self.avoid_distance       = 4.5   # bundan yakınsa kaçınmaya gir
        # 0.5 -> 0.3 (2026-08-03): obstacle_lidar zaten k-of-n zaman filtresi
        # uyguluyor (2 kare ~0.2 s onay); burada ikinci uzun onay araca
        # gereksiz yol kat ettiriyordu. Toplam onay ~0.5 s'de kalır.
        self.avoid_confirm_time   = 0.3   # s, tetik bu kadar sürmeli
        # İKİ KADEMELİ YAN BOŞLUK EŞİĞİ (2026-08-13): yan sektörler KOMŞU
        # ŞERİDİN kendisine bakıyor (side_offset=3.0), değer o şeritteki
        # BOYLAMSAL boşluk. Karar:
        #   boşluk >= safe_side_distance (13) -> TAM şerit değişimi (3.0 m):
        #       tam değişim + geri dönüş ~12 m ileri yol tutar, hedef şeritteki
        #       bir sonraki engele bundan az yer varsa tam değişim çarpışır.
        #   side_min_clear (5) <= boşluk < 13 -> SIĞ kaçış (dar mod, 1.55 m):
        #       hedef şeritte yakın engel var (sıkışık/çapraz slalom dizisi) ama
        #       kendi engelimizi geçecek kadar öne boşluk var; iki şeridin
        #       ayırıcı hattı üzerinden geçilir, komşu şeridin engel bandına
        #       hiç girilmez. Eski tek eşik (10) bu durumda manevrayı tamamen
        #       reddedip aracı beklemeye alıyordu — yarışta ardışık YAKIN
        #       engellerde ilk engel yine SOLdan geçilmeli (gereksinim; S6).
        #   boşluk < 5 -> o taraf kapalı (örn. bitişik karşı araç) -> girilmez.
        self.safe_side_distance   = 13.0
        self.side_min_clear       = 5.0
        # Zincirleme slalom: dönüş öncesi, DÖNÜLECEK şeride bakılır (kaçış
        # solaysa sağ sektör). Orada bundan az boşluk varsa şeride dönülmez,
        # komşu şeritte paralel geçişe devam edilir (arka arkaya engeller tek
        # geçişte aşılır); boşluk açılınca dönüş başlar.
        # 8 -> 12 (2026-08-13, masa sim S7): AYNI yöndeki ardışık engellerde
        # "aradan dön + yeniden kaç" geometrik olarak pahalı — dönüş (~5 m) ilk
        # engeli geçtikten çok sonra biter, ardından yeni kaçış (~5 m) için
        # ~13 m'den az boşluk kalırsa araç ikinci engele kaçışı tamamlayamadan
        # girip acil durur (S7, 15 m arayla iki engel: front=1.0'da DUR).
        # 12 m eşik: bu boşluğun altında ARADAN DÖNÜLMEZ, komşu şeritte kalınıp
        # ikisi de tek geçişte aşılır (güvenli yarış çizgisi), sonuncudan sonra
        # dönülür. Çapraz (S5, engel komşu şeritte) etkilenmez: orada dönülecek
        # şerit (kendi şeridimiz) boştur -> home=99 >= 12 -> yine döner.
        self.slalom_return_free   = 12.0  # m
        self.obstacle_replan_wait = 3.0
        self.avoid_direction      = None
        self._avoid_trigger_since = None

        # --- Slalom: ÜÇ FAZLI weave (2026-08-03) ---
        # Eski iki fazlı yapı (kaç -> dön) engelin YANINDAN GEÇME adımını hiç
        # içermiyordu: ~2 m kaçıştan sonra hemen şeride dönülüyor, araç daha
        # engelin hizasına gelmeden üstüne geri kırıyordu. İkinci hata: kaçış
        # fazı "front açıldı" koşuluyla erken bitiyordu — front sektörü ARAÇLA
        # birlikte döner; araç 15-20° dönünce engel sektörden çıkar ("önüm
        # açıldı" YANILGISI) ama engel hâlâ şeridin üstündedir. Sonuç: testere.
        # Yeni yapı:
        #   escape : yana kır. yaw besleniyorsa gerçek YANAL OFSET hedefine
        #            kadar, yoksa yol mesafesine göre.
        #   pass   : düzel, engelin yanından paralel GEÇ (sabit mesafe; yaw
        #            varsa şeride paralel tutan küçük düzeltme uygulanır).
        #   return : şeride dön. yaw varsa yanal ofset ~0'a inince biter.
        # Faz bitişleri ASLA front'a bağlanmaz (dönen sektör yanılgısı); front
        # yalnız weave SONUNDA "engel hâlâ önümde mi" kontrolünde kullanılır —
        # o anda araç şeride ~paralel olduğu için sektör doğru yöne bakar.
        # Weave kompakt tutulur (masa sim bulgusu): TEKNOFEST slalomunda
        # engeller ~10 m arayla dizilir; toplam weave yolu ~8 m'yi aşarsa bir
        # sonraki engele manevra payı kalmaz.
        self.slalom_speed           = 4.0   # km/h, weave sırasında hedef hız
        # 3.0 = ŞERİT GENİŞLİĞİ (pist_layout.json meta.lane_width; gerçek
        # pistte ~2.96 ölçüldü) -> kaçış hedefi KOMŞU ŞERİDİN MERKEZİ, yani
        # tam şerit değişimi: sağ şeritten sola geç, engeli geç, sağa dön.
        # Pist engeli 1.4 m geniş ve şerit ortasında: 1.4 m'lik eski hedefle
        # kenar payı ~0.17 m kalıyordu (araç yarım genişlik 0.53 + engel yarım
        # 0.7). obstacle_lidar'ın side_offset'i de 3.0'a çekildi — "sol boş"
        # kararı artık hedef şeridin kendisine bakıyor; ikisi tutarlı olmalı.
        self.slalom_lateral_target  = 3.0   # m, kaçışta hedef yanal ofset (yaw varsa)
        # DAR MOD ofseti (2026-08-13): hedef şeritte yakın engel varken tam
        # şerit değişimi yerine iki şeridin AYIRICI HATTI üzerinden sığ geçiş.
        # 1.55 = kendi engelimizi geçmeye yeter (0.7 engel + 0.53 araç + pay)
        # ama komşu şeridin engel bandına (şerit merkezi ±0.7 -> y>2.3) girmez
        # ve geçilen engel front koridorunun (±0.7) kenarına takılmaz.
        self.slalom_lateral_tight   = 1.55  # m, dar mod kaçış ofseti
        self.slalom_lateral_done    = 0.3   # m, dönüşte "şeride vardı" eşiği (yaw varsa)
        # Yaw'sız yedek mesafeler ~yarım-S yay uzunluğu (tam kilit R≈3.06,
        # 1.5 m yanal için yay ≈ 3.2 m) — 3.0 m hedefle tutarlı tutuldu.
        self.slalom_out_distance    = 3.2   # m, kaçış fazı yolu (yaw yoksa)
        self.slalom_pass_distance   = 2.0   # m, paralel geçiş fazı yolu
        self.slalom_return_distance = 3.2   # m, dönüş fazı yolu (yaw yoksa)
        self.slalom_align_done_deg  = 8.0   # °, hizalanma bitti eşiği (yaw varsa)
        self.slalom_align_distance  = 1.2   # m, hizalanma fazı yolu (yaw yoksa)
        self.slalom_max_time        = 20.0  # s, weave EMNIYET tavanı (odometri ölürse)
        # KAÇINMA SIRASINDA ÇARPIŞMA KORUMASI (2026-08-03 — eski kodda YOKTU:
        # OBSTACLE_AVOID boyunca engel mesafeleri tamamen yok sayılıyordu,
        # dönüş fazında engelin üstüne sürerken hiçbir fren yoktu). pass/return
        # fazlarında front < stop_distance -> dur; escape'te burun henüz engele
        # dönük olabileceği için daha sıkı (daha yakın) acil eşik kullanılır.
        self.avoid_emergency_front  = 1.0   # m, escape fazında acil durma eşiği
        # Hareketsizlik koruması: bu sürede bu kadar bile ilerlemediyse manevra
        # gerçekleşmiyor demektir — direksiyonu savurmayı bırak, dur.
        self.stall_timeout         = 4.0   # s
        self.stall_min_distance    = 0.25  # m
        # Şerit karışımı (kontrol node'u kullanır): kaçışta şerit büyük ölçüde
        # yok sayılır; geçişte HİÇ karışmaz (şeridin dışındayız, şerit takipçisi
        # bizi engelin üstüne geri çekerdi); dönüş fazında merkeze çeker.
        self.avoid_lane_blend_escape = 0.15
        self.avoid_lane_blend_pass   = 0.0
        self.avoid_lane_blend_return = 0.55
        # Zaman tabanlı YEDEK (hiç hareket kaynağı beslenmezse, ör. sim):
        self.slalom_out_time    = 2.0
        self.slalom_pass_time   = 2.0
        self.slalom_return_time = 2.0
        self.slalom_align_time  = 1.0
        self.slalom_count     = 0      # geçilen engel sayısı (debug)
        self.avoid_phase      = None   # 'escape' | 'pass' | 'return' | 'align'
        # SONSUZ WEAVE KORUMASI (2026-07-20, debug_control5 bag analizi):
        # araç ilerlemiyorken (fren/rampa/engel gerçekten geçilemiyor) engel
        # önde kaldığı için her weave sonunda ters yöne yenisi açılıyor ve
        # direksiyon 18-24 sn boyunca 70<->20 arası savruluyordu. Bu kadar
        # weave'den sonra slalom bırakılır, OBSTACLE_STOP'a düşülür ve yol
        # gerçekten açılana (front > slow_distance) kadar yeniden slaloma
        # girilmez.
        self.slalom_max_weaves = 3
        self.avoid_blocked     = False  # True: slalom denendi, çözemedi -> dur

        # --- VİRAJDA SAHTE SLALOM BASTIRMA (2026-07-21, nursena tabanına
        # graft edildi 2026-08-10) --------------------------------------------
        # Virajda pist kenarı/bariyer DÜZ ego koridoruna (|y|<corridor, 30 m'ye
        # kadar) girip gerçek engel gibi görünür: ~15 m yarıçapta bariyer
        # ~4.9 m'de tetik bandına düşer, araç viraj ortasında açık-döngü weave
        # başlatıp pisti terk ederdi. Koridoru eğmek lidar'a direksiyon
        # beslemeyi gerektirir; onun yerine viraj, şerit açısından tespit edilip
        # slalom GİRİŞİ bastırılır (yavaşlar ve gerekirse durur; sadece savurma
        # manevrası yapılmaz). Şerit çıktısının sıfır noktası koşudan koşuya
        # kaydığı için (algi7 +4.1, algi8 -1.7) hızlı EMA ile koşuya özel yavaş
        # bir taban EMA'nın FARKINA bakılır (sabit 45'e değil).
        self.curve_lane_dev   = 6.0    # |hızlı-yavaş| bunu aşarsa viraj
        self.curve_hold_time  = 1.0    # s, viraj bittikten sonra da bastır
        self.curve_ema_fast   = 0.30   # ~3-4 karelik tepki
        self.curve_ema_slow   = 0.01   # ~100 karelik taban (koşu kayması)
        self._lane_fast       = None
        self._lane_slow       = None
        self._curve_until     = 0.0

        self.front_distance = 99.0
        self.left_distance  = 99.0
        self.right_distance = 99.0

        # --- Hareket (mesafe tabanlı slalom için) ---
        # update_motion() ile dışarıdan beslenir. Hiç beslenmezse
        # _motion_ok False kalır ve slalom otomatik olarak eski zaman
        # tabanlı davranışa döner (sim/odometrisiz çalışma bozulmasın).
        self.odom_distance  = 0.0     # monoton katedilen mesafe (m)
        self.speed_mps      = 0.0
        self.yaw            = None    # araç yönü (rad, update_motion(yaw=...))
        self._yaw_ok        = False
        self._motion_ok     = False
        self._last_motion_t = None
        self._avoid_mark    = 0.0     # weave başındaki odom_distance
        self._phase_mark    = 0.0     # faz başındaki odom_distance
        self._avoid_start_t = 0.0
        self._phase_start_t = 0.0     # faz başlangıç zamanı (zaman yedeği için)
        self._weave_yaw_ref = 0.0     # weave başındaki yön (yanal ofset referansı)
        self._lateral       = 0.0     # weave başına göre yanal ofset (m, sol +)
        self._weave_lat     = self.slalom_lateral_target  # bu weave'in ofset hedefi

        self.park_forbidden   = False
        self.emergency_active = False
        self.last_event       = "baslangic: LANE_FOLLOW"

        # resolution=1.0: bu katmanda konumlar GRID_SCALE ile hücreye çevrilmiş
        # 0..59 grid koordinatı — planner'ın "dünya" birimi de hücre olmalı,
        # yoksa plan_path metre sanıp 0.5'e bölerek grid dışına taşar (IndexError)
        self.planner = AStarPlanner(grid_width=60, grid_height=60, resolution=1.0)
        # FIX: current_position artık update_position() ile odometriden güncelleniyor
        self.current_position = (2, 2)
        self.goal_position    = (50, 50)
        self.path = self.planner.plan_path(self.current_position, self.goal_position)

    # ------------------------------------------------------------
    # FIX: Dışarıdan çağrılarak gerçek araç konumunu grid'e yazar
    # ------------------------------------------------------------
    def update_position(self, grid_x, grid_y):
        self.current_position = (
            max(0, min(59, grid_x)),
            max(0, min(59, grid_y)),
        )

    # ------------------------------------------------------------
    # Katedilen mesafe — slalom fazlarının ölçüsü (2026-07-21)
    # ------------------------------------------------------------
    def update_motion(self, speed_mps=None, distance=None, yaw=None):
        """Mesafe tabanlı slalomu besler. İki kaynaktan biri yeter:
          distance  : odometriden gelen MUTLAK katedilen yol (m, monoton)
          speed_mps : anlık hız; kendi saatimizle integre edilir
          yaw       : araç yönü (rad, isteğe bağlı). Verilirse slalomun yanal
                      ofseti GERÇEK geometriyle ölçülür: kaçış fazı "yeterince
                      yana çıktım mı"yı, dönüş fazı "şeride geri geldim mi"yi
                      bununla anlar (2026-08-03). Verilmezse fazlar yol
                      mesafesiyle ilerler (eski davranış).
        Hiç çağrılmazsa slalom zaman tabanlı yedeğe düşer."""
        now = self._now()
        prev_d = self.odom_distance
        if distance is not None:
            self.odom_distance = float(distance)
            self._motion_ok = True
        elif speed_mps is not None:
            self.speed_mps = max(0.0, float(speed_mps))
            if self._last_motion_t is not None:
                dt = now - self._last_motion_t
                if 0.0 < dt < 1.0:        # uzun boşlukları yut (donma/yeniden başlama)
                    self.odom_distance += self.speed_mps * dt
            self._motion_ok = True
        if yaw is not None:
            self.yaw = float(yaw)
            self._yaw_ok = True
        # Yanal ofset: weave başındaki yöne DİK bileşenin yol integrali.
        # Sadece kaçınma sırasında toplanır; _begin_weave sıfırlar.
        step = self.odom_distance - prev_d
        if (step > 0.0 and self._yaw_ok and self.yaw is not None
                and self.state == DriveState.OBSTACLE_AVOID):
            self._lateral += math.sin(self.yaw - self._weave_yaw_ref) * step
        self._last_motion_t = now

    # ------------------------------------------------------------
    # Yardımcılar
    # ------------------------------------------------------------
    def _now(self): return time.time()

    def _set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.state_start_time = self._now()

    def _explain(self, msg):
        self.last_event = msg

    def _elapsed(self): return self._now() - self.state_start_time

    def _cooldown_ok(self, sign_id):
        return self._now() >= self.sign_cooldown.get(sign_id, 0.0)

    def _start_cooldown(self, sign_id, sec=None):
        self.sign_cooldown[sign_id] = self._now() + (
            sec if sec is not None else self.default_cooldown)

    def _stop_vehicle(self):
        self.target_speed   = 0.0
        self.brake          = 1
        self.steering_angle = 45

    def _move_vehicle(self, speed=None):
        self.brake = 0
        req = speed if speed is not None else self.default_speed
        self.target_speed = min(req, self.speed_limit)

    def _smooth_angle(self, old_angle, new_angle, alpha=0.35):
        return int((1 - alpha) * old_angle + alpha * new_angle)

    # ------------------------------------------------------------
    # Viraj tespiti — sahte slalomu bastırmak için (graft 2026-08-10)
    # ------------------------------------------------------------
    def _note_lane_angle(self, lane_angle):
        """Şerit açısını iki EMA ile izler: yavaş olan bu koşudaki "düz"ün
        nerede olduğunu öğrenir, hızlı olan anlık durumu takip eder. İkisi
        arasındaki fark viraj göstergesidir — sabit 45'e göre ölçmek, şerit
        çıktısının koşudan koşuya kayan sıfır noktası yüzünden çalışmıyordu.

        OBSTACLE_AVOID sırasında BİLEREK güncellenmez: slalomda direksiyon
        zaten kasten kırılıyor, şerit de eğik görünüyor — bunu viraj sanırsak
        kendi slalomumuz sonraki weave'leri bastırırdı."""
        if self.state == DriveState.OBSTACLE_AVOID:
            return
        a = float(lane_angle)
        if self._lane_fast is None:          # ilk kare: iki EMA da oradan başlar
            self._lane_fast = self._lane_slow = a
            return
        self._lane_fast = (self.curve_ema_fast * a
                           + (1.0 - self.curve_ema_fast) * self._lane_fast)
        self._lane_slow = (self.curve_ema_slow * a
                           + (1.0 - self.curve_ema_slow) * self._lane_slow)
        if abs(self._lane_fast - self._lane_slow) > self.curve_lane_dev:
            self._curve_until = self._now() + self.curve_hold_time

    def _in_curve(self):
        """Viraj içinde (veya çıkışından curve_hold_time geçmemiş) miyiz?"""
        return self._now() < self._curve_until

    def _is_blocking_state(self):
        blocking = {
            DriveState.RED_LIGHT_STOP, DriveState.STOP_SIGN,
            DriveState.CROSSWALK_STOP, DriveState.BUS_STOP,
            DriveState.TURN_LEFT, DriveState.TURN_RIGHT,
            DriveState.GO_STRAIGHT_LEFT, DriveState.GO_STRAIGHT_RIGHT,
            DriveState.OBSTACLE_STOP, DriveState.OBSTACLE_AVOID,
            DriveState.PARKING, DriveState.EMERGENCY,
        }
        return self.state in blocking

    # ------------------------------------------------------------
    # Olaylar
    # ------------------------------------------------------------
    def lane_detect_event(self, data):
        try:
            lane_angle = float(data[1])
        except (IndexError, ValueError, TypeError):
            return

        # Viraj tespitini her şerit karesinde besle — bloke durumlarda bile,
        # yoksa OBSTACLE_STOP'tan çıkarken viraj bilgisi bayat olurdu.
        self._note_lane_angle(lane_angle)

        if self.emergency_active:
            self._set_state(DriveState.EMERGENCY)
            self._stop_vehicle()
            return

        self._update_state_machine()

        if self._is_blocking_state():
            return

        # Şerit açısını FSM'e yaz; control_loop'ta waypoint ile karıştırılır
        fused = max(15, min(75, lane_angle))
        self.steering_angle = self._smooth_angle(self.steering_angle, fused)
        # HIZ YARIŞI DÜZELTMESİ (2026-08-03): eskiden burada koşulsuz
        # default_speed yazılıyordu ve obstacle_event'in "5 m'de yavaşla"
        # (slow_speed) kararını her şerit karesinde geri eziyordu — hedef hız
        # 12<->6 arasında titreşiyor, araç engele yavaşlamadan yaklaşıyordu.
        # Engel yavaşlatma bandındaysak şerit takibi hızı yükseltmez.
        if self.front_distance < self.slow_distance:
            self._move_vehicle(self.slow_speed)
        else:
            self._move_vehicle(self.default_speed)

    def sign_detect_event(self, data):
        try:
            sign     = int(data[1])
            distance = float(data[2])
            w        = int(data[5])
            h        = int(data[6])
        except (IndexError, ValueError, TypeError):
            return

        if sign == 24:
            sign = ILERI_SAG
        elif sign == 25:
            sign = ILERI_SOL

        if self.emergency_active:
            self._set_state(DriveState.EMERGENCY)
            self._stop_vehicle()
            return

        if not self._update_sign_counter(sign): return
        if not self._cooldown_ok(sign):         return

        name = SIGN_NAMES.get(sign, str(sign))
        self._explain(f"TABELA {name} (id={sign}, d={distance:.1f}m, h={h}) -> islendi")

        if sign in (HIZ_20, HIZ_20B):
            self.speed_limit   = 20.0
            self.default_speed = min(self.default_speed, 12.0)
            self._start_cooldown(sign, 5.0)

        elif sign == HIZ_30:
            self.speed_limit   = 30.0
            self.default_speed = min(self.default_speed, 15.0)
            self._start_cooldown(sign, 5.0)

        elif sign == KIRMIZI_ISIK:
            if distance < 12.0:
                self.red_light_seen_time = self._now()
                self._set_state(DriveState.RED_LIGHT_STOP)
                self._start_cooldown(sign, 1.0)
                self._explain(f"KIRMIZI ISIK (d={distance:.1f}) -> DUR")
            else:
                self._explain(f"KIRMIZI ISIK ama uzak (d={distance:.1f}) -> bekle")

        elif sign == SARI_ISIK:
            if distance < 10.0:
                self.target_speed = self.slow_speed
                self._explain(f"SARI ISIK (d={distance:.1f}) -> yavasla")

        elif sign == YESIL_ISIK:
            self.green_light_seen_time = self._now()
            if self.state == DriveState.RED_LIGHT_STOP:
                self._set_state(DriveState.LANE_FOLLOW)
                self._move_vehicle(self.default_speed)
                self._explain("YESIL ISIK -> DEVAM (kirmizidan cikildi)")
            else:
                self._explain("YESIL ISIK -> devam")
            self._start_cooldown(sign, 1.0)

        elif sign == DUR:
            if distance < 9.0:
                self._set_state(DriveState.STOP_SIGN)
                self._start_cooldown(sign, 8.0)
                self._explain(f"DUR tabelasi (d={distance:.1f}) -> 3sn DUR")

        elif sign == YAYA_GECIDI:
            if distance < 12.0:
                self._set_state(DriveState.CROSSWALK_STOP)
                self._start_cooldown(sign, 10.0)

        elif sign == DURAK:
            if distance < 10.0:
                if self.state != DriveState.BUS_STOP:
                    self._set_state(DriveState.BUS_STOP)
                    self._start_cooldown(sign, 30.0)
                    self._explain(f"DURAK (d={distance:.1f}) -> duraga yanas + bekle")

        elif sign == SOLA_DON:
            if distance < 12.0:
                self._begin_left_turn()
                self._explain(f"SOLA DON tabelasi (d={distance:.1f}) -> SOLA DONUS")

        elif sign == SOLA_DON_YASAK:
            self._start_cooldown(sign, 6.0)

        elif sign == SAGA_DON:
            if distance < 12.0:
                self._begin_right_turn()
                self._explain(f"SAGA DON tabelasi (d={distance:.1f}) -> SAGA DONUS")

        elif sign == SAGA_DON_YASAK:
            self._start_cooldown(sign, 6.0)

        elif sign == GIRILMEZ:
            self._start_cooldown(sign, 6.0)

        elif sign == ILERI_SOL:
            if distance < 12.0:
                self._begin_straight_then_left()

        elif sign == ILERI_SAG:
            if distance < 12.0:
                self._begin_straight_then_right()

        elif sign == ILERI:
            if self.state in (DriveState.TURN_LEFT, DriveState.TURN_RIGHT,
                              DriveState.GO_STRAIGHT_LEFT,
                              DriveState.GO_STRAIGHT_RIGHT):
                self._set_state(DriveState.LANE_FOLLOW)
            self._start_cooldown(sign, 4.0)

        elif sign == PARK_YASAK:
            self.park_forbidden = True
            self._start_cooldown(sign, 8.0)

        elif sign == PARK:
            if not self.park_forbidden and distance < 10.0:
                if self.state not in (DriveState.PARKING, DriveState.PARK_SEARCH):
                    self._set_state(DriveState.PARK_SEARCH)
                    self._start_cooldown(sign, 10.0)
                    self._explain(f"PARK (d={distance:.1f}) -> park arama")

        elif sign == TUNEL:
            self.steering_angle = 45
            self.target_speed   = min(self.target_speed, self.slow_speed)
            self._start_cooldown(sign, 6.0)
            self._explain(f"TUNEL (d={distance:.1f}) -> duz + yavasla")

        elif sign == IKI_YON:
            if self.target_speed > self.slow_speed:
                self.target_speed = self.slow_speed
            self._start_cooldown(sign, 5.0)

    def obstacle_event(self, front=None, left=None, right=None):
        if front is not None: self.front_distance = float(front)
        if left  is not None: self.left_distance  = float(left)
        if right is not None: self.right_distance = float(right)

        if self.emergency_active:
            self._set_state(DriveState.EMERGENCY)
            self._stop_vehicle()
            return

        if self.state == DriveState.OBSTACLE_AVOID:
            # ÇARPIŞMA KORUMASI (2026-08-03): eskiden kaçınma sırasında engel
            # verisi tamamen yok sayılıyordu — dönüş fazında engelin üstüne
            # sürerken hiçbir fren yoktu. Eşik olarak stop_distance DEĞİL sıkı
            # acil eşik kullanılır: manevra boyunca burun kasıtlı olarak
            # şeride/engele açılı döner, front sektörü geçici olarak yol
            # kenarını/bariyeri veya geçilmekte olan engelin kenarını tarar;
            # stop_distance (2.2) her sağlıklı slalomu keserdi (masa sim
            # bulgusu). Düşük slalom hızında (≈1.1 m/s) 1 m'lik marj güvenli
            # duruşa yeter. front=0 (lidar fail-safe) her fazda durdurur.
            lim = self.avoid_emergency_front
            if self.front_distance < lim:
                self._explain(
                    f"KACINMADA COK YAKIN ENGEL front={self.front_distance:.1f} "
                    f"(faz={self.avoid_phase}) -> DUR")
                self._pause_avoidance()
            return
        if self.state in (DriveState.PARKING, DriveState.PARK_SEARCH):
            return

        # FIX: self.current_position artık gerçek konumla güncelleniyor;
        # makul yan mesafe yoksa planner'a engel ekleme (false-positive önleme)
        if (self.planner is not None
                and self.front_distance < self.slow_distance
                and (self.left_distance > 1.0 or self.right_distance > 1.0)):
            cx, cy = self.current_position
            self.planner.add_obstacle(min(59, int(cx + 2)), cy, safety_margin=2)
            self.path = self.planner.replan_if_needed(
                self.current_position, self.goal_position)

        # FSM'in açık şekilde durmaya/beklemeye karar verdiği durumları ezme
        if self.state in (DriveState.RED_LIGHT_STOP, DriveState.STOP_SIGN,
                          DriveState.CROSSWALK_STOP, DriveState.BUS_STOP,
                          DriveState.EMERGENCY):
            return

        # --- Engel algılama eşiği (genel, reaktif) ---
        # İKİ KADEMELI (2026-07-21): slow_distance yavaşlatır, avoid_distance
        # kaçınmaya sokar. Böylece 5 m'de görülen bir şey için 3 saniyelik
        # açık-döngü manevraya girilmez; önce yavaşlanır, engel gerçekten
        # yaklaşır ve avoid_confirm_time boyunca kalıcı olursa kaçınılır.
        if self.front_distance >= self.slow_distance:
            self._avoid_trigger_since = None
            return

        if self.avoid_blocked:
            # Slalom tavanı dolmuştu ve yol hâlâ kapalı -> tekrar slaloma
            # girme (sonsuz weave koruması), dur ve bekle.
            self._set_state(DriveState.OBSTACLE_STOP)
            self._stop_vehicle()
            self.signal_status = 3
            return

        # ÇOK YAKIN -> KAÇINMAYA GİRME, DUR (2026-08-03, masa sim bulgusu):
        # bu kontrol eskiden weave girişinden SONRA geliyordu; stop_distance
        # altındayken bile slalom başlatılabiliyor, çarpışma koruması onu
        # kesiyor ve dur-kalk döngüsünde araç santim santim engele
        # sürükleniyordu. stop_distance altında manevra için geometrik yer
        # yoktur (tam kilit dönüş yarıçapı ~3.1 m) — tek doğru hamle durmak.
        if self.front_distance < self.stop_distance:
            self._set_state(DriveState.OBSTACLE_STOP)
            self._stop_vehicle()
            self.signal_status = 3
            self._explain(f"ENGEL front={self.front_distance:.1f} cok yakin -> DUR")
            return

        # Tetik kalıcılığı: yalnızca avoid_distance içindeyken sayaç işler.
        if self.front_distance < self.avoid_distance:
            if self._avoid_trigger_since is None:
                self._avoid_trigger_since = self._now()
            held = self._now() - self._avoid_trigger_since
        else:
            self._avoid_trigger_since = None
            held = 0.0

        # VİRAJDA slalom GİRİŞİ bastırılır (graft 2026-08-10): pist kenarı düz
        # koridora girip gerçek engel gibi göründüğünden, virajda açık-döngü
        # weave pisti terk ettirir. Araç yine yavaşlar ve çok yakınsa (yukarıda
        # stop_distance) durur; sadece savurma manevrası yapılmaz.
        in_curve = self._in_curve()

        if held >= self.avoid_confirm_time and not in_curve:
            direction = self._pick_avoid_direction()
            if direction is not None:
                # Boş taraf var -> DURMADAN doğrudan slaloma gir (akıcı geçiş)
                self.slalom_count = 0
                self._begin_weave(direction)
                self._explain(
                    f"ENGEL front={self.front_distance:.1f} (>{self.avoid_confirm_time}s) "
                    f"-> SLALOM {direction} (durmadan)")
                return

        # slow_distance ile avoid_distance arası (veya virajda): YAVAŞLA, şeritte kal.
        self._move_vehicle(self.slow_speed)
        if in_curve:
            self._explain(f"ENGEL front={self.front_distance:.1f} -> yavasla "
                          f"(VIRAJ: slalom bastirildi)")
        else:
            self._explain(f"ENGEL front={self.front_distance:.1f} -> yavasla (seritte kal)")

    def planner_event(self, data):
        try:
            self.goal_position = (int(float(data[1])), int(float(data[2])))
        except (IndexError, ValueError, TypeError):
            return
        self.path = self.planner.plan_path(self.current_position, self.goal_position)

    def emergency_event(self, active=True):
        self.emergency_active = bool(active)
        if self.emergency_active:
            self._set_state(DriveState.EMERGENCY)
            self._stop_vehicle()
            self.signal_status = 3
        else:
            self.signal_status = 0
            self._set_state(DriveState.LANE_FOLLOW)

    # ------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------
    def _update_state_machine(self):
        if self.state == DriveState.EMERGENCY:
            self._stop_vehicle(); self.signal_status = 3; return
        if self.state == DriveState.OBSTACLE_STOP:
            self._obstacle_stop_control(); return
        if self.state == DriveState.RED_LIGHT_STOP:
            self._stop_vehicle(); return
        if self.state == DriveState.STOP_SIGN:
            self._stop_vehicle()
            if self._elapsed() >= self.stop_wait_sec:
                self._set_state(DriveState.LANE_FOLLOW)
                self._move_vehicle(self.default_speed)
            return
        if self.state == DriveState.CROSSWALK_STOP:
            self._stop_vehicle()
            if (self._elapsed() >= self.crosswalk_wait_sec
                    and self.front_distance > self.slow_distance):
                self._set_state(DriveState.LANE_FOLLOW)
                self._move_vehicle(self.default_speed)
            return
        if self.state == DriveState.BUS_STOP:
            self._bus_stop_control(); return
        if self.state == DriveState.TURN_LEFT:
            self._left_turn_control(); return
        if self.state == DriveState.TURN_RIGHT:
            self._right_turn_control(); return
        if self.state == DriveState.GO_STRAIGHT_LEFT:
            self._straight_then_left_control(); return
        if self.state == DriveState.GO_STRAIGHT_RIGHT:
            self._straight_then_right_control(); return
        if self.state == DriveState.OBSTACLE_AVOID:
            self._obstacle_avoid_control(); return
        if self.state == DriveState.PARK_SEARCH:
            self._park_search_control(); return
        if self.state == DriveState.PARKING:
            self._parking_control(); return

    # ------------------------------------------------------------
    # Tabela doğrulama
    # ------------------------------------------------------------
    def _update_sign_counter(self, sign):
        now = self._now()
        if sign not in self.last_sign_time:
            self.last_sign_time[sign] = now
            self.sign_counts[sign] = 1
            return False
        if now - self.last_sign_time[sign] <= self.sign_window_sec:
            self.sign_counts[sign] += 1
        else:
            self.sign_counts[sign] = 1
        self.last_sign_time[sign] = now
        return self.sign_counts[sign] >= self.sign_confirm_count

    # ------------------------------------------------------------
    # Dönüş başlatıcılar
    # ------------------------------------------------------------
    def _begin_left_turn(self):
        self.signal_status = 2
        self._set_state(DriveState.TURN_LEFT)
        self._start_cooldown(SOLA_DON, 10.0)

    def _begin_right_turn(self):
        self.signal_status = 1
        self._set_state(DriveState.TURN_RIGHT)
        self._start_cooldown(SAGA_DON, 10.0)

    def _begin_straight_then_left(self):
        self.signal_status = 2
        self._set_state(DriveState.GO_STRAIGHT_LEFT)
        self._start_cooldown(ILERI_SOL, 12.0)

    def _begin_straight_then_right(self):
        self.signal_status = 1
        self._set_state(DriveState.GO_STRAIGHT_RIGHT)
        self._start_cooldown(ILERI_SAG, 12.0)

    # ------------------------------------------------------------
    # Manevra kontrolleri
    # FIX: Dönüş süreleri kalibre edildi.
    # 6 km/h = 1.67 m/s, steer=73 → R≈7m, 90° yay=11m → ~6.6s
    # faz1=5.5s (tam direksiyon), faz2=8.5s (3s düzeltme)
    # NOT: Bu süreler hesap tahminidir; CARLA testinde araç modeline
    #      ve kavşak genişliğine göre ince ayar gerekebilir.
    # ------------------------------------------------------------
    def _left_turn_control(self):
        t = self._elapsed()
        self.brake = 0
        self.target_speed = self.turn_speed
        if t < 5.5:      # FIX: 4.0 → 5.5s
            self.steering_angle = self.left_turn_angle
        elif t < 8.5:    # FIX: 6.0 → 8.5s
            self.steering_angle = self.turn_recover_angle_left
        else:
            self.signal_status  = 0
            self.steering_angle = 45
            self._set_state(DriveState.LANE_FOLLOW)

    def _right_turn_control(self):
        t = self._elapsed()
        self.brake = 0
        self.target_speed = self.turn_speed
        if t < 5.5:      # FIX: 4.0 → 5.5s
            self.steering_angle = self.right_turn_angle
        elif t < 8.5:    # FIX: 6.0 → 8.5s
            self.steering_angle = self.turn_recover_angle_right
        else:
            self.signal_status  = 0
            self.steering_angle = 45
            self._set_state(DriveState.LANE_FOLLOW)

    def _straight_then_left_control(self):
        t = self._elapsed()
        self.brake = 0
        self.target_speed = self.turn_speed
        if t < 3.0:
            self.steering_angle = 45
        elif t < 8.5:    # FIX: 7.0 → 8.5s
            self.steering_angle = self.left_turn_angle
        elif t < 11.0:   # FIX: 9.0 → 11.0s
            self.steering_angle = self.turn_recover_angle_left
        else:
            self.signal_status  = 0
            self.steering_angle = 45
            self._set_state(DriveState.LANE_FOLLOW)

    def _straight_then_right_control(self):
        t = self._elapsed()
        self.brake = 0
        self.target_speed = self.turn_speed
        if t < 3.0:
            self.steering_angle = 45
        elif t < 8.5:    # FIX: 7.0 → 8.5s
            self.steering_angle = self.right_turn_angle
        elif t < 11.0:   # FIX: 9.0 → 11.0s
            self.steering_angle = self.turn_recover_angle_right
        else:
            self.signal_status  = 0
            self.steering_angle = 45
            self._set_state(DriveState.LANE_FOLLOW)

    # ------------------------------------------------------------
    # Engel kontrolleri
    # ------------------------------------------------------------
    def _pick_avoid_direction(self):
        """Boş tarafı seç (genel, piste bağımsız). Geri dönüş:
        'left' / 'right' / None (iki taraf da kapalı).
        Eşik side_min_clear'dır (2026-08-13): hedef şeritte en az SIĞ kaçışa
        yetecek boşluk aranır; tam mı sığ mı gidileceğine _begin_weave karar
        verir (boşluk >= safe_side_distance ise tam şerit değişimi). Eskiden
        eşik doğrudan safe_side_distance idi ve hedef şeritte yakın engel
        varken (S6 sıkışık çapraz) manevra tamamen reddediliyordu."""
        left_ok  = self.left_distance  > self.side_min_clear
        right_ok = self.right_distance > self.side_min_clear
        if not left_ok and not right_ok:
            return None
        if left_ok and not right_ok:
            return "left"
        if right_ok and not left_ok:
            return "right"
        # İkisi de uygun -> daha geniş olanı seç (eşitlikte sol)
        return "left" if self.left_distance >= self.right_distance else "right"

    def _obstacle_stop_control(self):
        self._stop_vehicle()
        self.signal_status = 3
        if self.front_distance > self.slow_distance:
            self.signal_status  = 0
            self.avoid_blocked  = False   # yol açıldı -> slalom tekrar serbest
            self._avoid_trigger_since = None
            self._set_state(DriveState.LANE_FOLLOW)
            return
        if self.avoid_blocked:
            # Slalom denendi ve engel geçilemedi -> yol gerçekten açılana kadar
            # bekle (tekrar slaloma girip direksiyonu savurma).
            return
        if self._elapsed() > self.obstacle_replan_wait:
            # stop_distance'tan yakında weave BAŞLATMA (2026-08-03): duruştan
            # tam kilitle bile engelin yanından dönecek yer ancak ~2.2 m'de
            # açılıyor; daha yakında tek güvenli davranış beklemek.
            if self.front_distance < self.stop_distance:
                return
            direction = self._pick_avoid_direction()
            if direction is not None:
                self.slalom_count = 0
                self._begin_weave(direction)

    def _begin_weave(self, direction):
        """Yeni bir weave başlat: yön + mesafe/zaman/yanal işaretleri sıfırla.
        slalom_count'a DOKUNMAZ (çağıran yönetir)."""
        # MOD SEÇİMİ (2026-08-13): hedef şeritteki boşluğa göre tam / sığ kaçış.
        # Bol boşluk -> komşu şerit merkezine tam değişim; dar boşluk (hedef
        # şeritte yakın engel, sıkışık/çapraz slalom dizisi) -> ayırıcı hat
        # üzerinden sığ geçiş, komşu şeridin engel bandına girilmez.
        clear = (self.left_distance if direction == "left"
                 else self.right_distance)
        self._weave_lat = (self.slalom_lateral_target
                           if clear >= self.safe_side_distance
                           else self.slalom_lateral_tight)
        self.avoid_direction  = direction
        self.avoid_phase      = "escape"
        self._avoid_mark      = self.odom_distance
        self._phase_mark      = self.odom_distance
        self._avoid_start_t   = self._now()
        self._phase_start_t   = self._avoid_start_t
        # Yanal ofset referansı: weave başındaki yön = "şerit yönü" kabulü
        self._weave_yaw_ref   = (self.yaw
                                 if (self._yaw_ok and self.yaw is not None)
                                 else 0.0)
        self._lateral         = 0.0
        self._avoid_trigger_since = None
        self.signal_status    = 2 if direction == "left" else 1
        self._set_state(DriveState.OBSTACLE_AVOID)

    def _phase_next(self, new_phase):
        self.avoid_phase    = new_phase
        self._phase_mark    = self.odom_distance
        self._phase_start_t = self._now()

    def _obstacle_avoid_control(self):
        """SLALOM: üç fazlı weave (2026-08-03) — escape (yana kır),
        pass (engelin yanından paralel geç), return (şeride dön).

        Faz bitişlerinde ölçü öncelik sırası:
          1) yaw + odometri varsa: GERÇEK YANAL OFSET (escape/return için)
          2) sadece odometri varsa: katedilen yol
          3) hiçbiri yoksa: saat (eski yedek davranış)
        front'a bakarak faz BİTİRİLMEZ: front sektörü araçla birlikte döner,
        araç birkaç derece dönünce engel sektörden çıkıp "önüm açıldı"
        yanılgısı doğurur (eski kodun tam slalom yapamamasının ana nedeni).
        Çarpışma koruması obstacle_event içindedir (her lidar karesinde)."""
        self.brake        = 0
        self.target_speed = self.slalom_speed

        if self.avoid_direction is None:
            self._end_avoidance()
            return

        t        = self._now() - self._avoid_start_t
        t_phase  = self._now() - self._phase_start_t
        d_weave  = self.odom_distance - self._avoid_mark
        d_phase  = self.odom_distance - self._phase_mark
        left     = (self.avoid_direction == "left")
        # Kaçış yönünde pozitif yanal ilerleme (m)
        lat      = self._lateral if left else -self._lateral
        lat_ok   = self._yaw_ok and self._motion_ok

        # --- Hareketsizlik koruması: manevra gerçekleşmiyorsa savurma ---
        if (self._motion_ok and t > self.stall_timeout
                and d_weave < self.stall_min_distance):
            self._explain(
                f"SLALOM {t:.1f} s'de sadece {d_weave:.2f} m ilerledi "
                f"(arac hareket etmiyor) -> OBSTACLE_STOP")
            self._abort_avoidance()
            return

        # Emniyet tavanı: odometri beslenmiyorsa/donduysa sonsuza kalma
        timeout = t > self.slalom_max_time

        # Heading hatası (şerit yönüne göre, sol pozitif) — pass/align kullanır
        if self._yaw_ok and self.yaw is not None:
            err_deg = math.degrees(
                ((self.yaw - self._weave_yaw_ref + math.pi)
                 % (2 * math.pi)) - math.pi)
        else:
            err_deg = None

        if self.avoid_phase == "escape":
            # TAM KİLİT + YARIM-OFSET GEÇİŞİ (2026-08-03, S-viraj geometrisi):
            # tam kilitle yanal hedefin YARISINA gelince karşı kırmaya geçilir
            # (pass fazı); simetrik S sonunda araç tam ofsete burnu DÜZ varır.
            # Hedefin tamamı beklenirse burun 45-50° açılıyor ve sonraki
            # fazlar açıyı toparlamak için metrelerce yol yiyordu (masa sim).
            self.steering_angle = 75 if left else 15
            self.signal_status  = 2 if left else 1
            if lat_ok:
                done = lat >= 0.5 * self._weave_lat
            elif self._motion_ok:
                done = d_phase >= self.slalom_out_distance
            else:
                done = t_phase >= self.slalom_out_time
            if done or timeout:
                self._phase_next("pass")

        elif self.avoid_phase == "pass":
            # S-virajın ikinci yarısı + paralel geçiş: burun şerit yönüne
            # KUVVETLİ P-kontrolle çekilir (karşı kırma), hizalanınca düz
            # gider. Engelin yanından bu fazda geçilir.
            if err_deg is not None:
                self.steering_angle = int(max(15, min(75, 45 - 1.5 * err_deg)))
            else:
                self.steering_angle = 45
            self.signal_status = 2 if left else 1
            aligned = (err_deg is None
                       or abs(err_deg) <= self.slalom_align_done_deg)
            if self._motion_ok:
                done = aligned and d_phase >= self.slalom_pass_distance
            else:
                done = t_phase >= self.slalom_pass_time
            if done or timeout:
                # ZİNCİRLEME (2026-08-03): dönmeden önce DÖNÜLECEK şeride bak
                # (kaçış solaysa orijinal şerit SAĞ sektördedir — araç komşu
                # şeritte paralelken o sektör tam eski şeridimizi tarar).
                # Orada yakın engel varsa (arka arkaya slalom engelleri)
                # şeride dönme; paralel geçişe devam et, boşluk açılınca dön.
                home = self.right_distance if left else self.left_distance
                if timeout or home >= self.slalom_return_free:
                    self._phase_next("return")
                elif done and d_phase < self.slalom_pass_distance + 0.2:
                    self._explain(
                        f"SLALOM gecis uzatildi: donulecek serit dolu "
                        f"({'sag' if left else 'sol'}={home:.1f} m < "
                        f"{self.slalom_return_free:.0f})")

        elif self.avoid_phase == "return":
            # Şeride dönüş S'inin ilk yarısı: ofsetin yarısı inilince align
            # karşı kırmayla tamamlar (escape/pass simetriği).
            self.steering_angle = 25 if left else 65
            self.signal_status  = 1 if left else 2
            if lat_ok:
                done = lat <= max(self.slalom_lateral_done,
                                  0.5 * self._weave_lat)
            elif self._motion_ok:
                done = d_phase >= self.slalom_return_distance
            else:
                done = t_phase >= self.slalom_return_time
            if done or timeout:
                self._phase_next("align")

        elif self.avoid_phase == "align":
            # HİZALAN (dönüş S'inin ikinci yarısı): burun şerit yönüne
            # kilitlenir; weave ancak hizalanınca biter — front sektörü o anda
            # doğru yöne baktığı için weave-sonu engel kontrolü ve arka arkaya
            # engellerin zincirlenmesi güvenilir olur.
            if err_deg is not None:
                self.steering_angle = int(max(15, min(75, 45 - 1.5 * err_deg)))
                done = abs(err_deg) <= self.slalom_align_done_deg
            elif self._motion_ok:
                self.steering_angle = 45
                done = d_phase >= self.slalom_align_distance
            else:
                self.steering_angle = 45
                done = t_phase >= self.slalom_align_time
            if done or timeout:
                self._weave_finished()

        else:                      # savunma: bilinmeyen faz
            self._phase_next("escape")

    def _weave_finished(self):
        """Bir weave tamamlandı: yola devam mı, yeni weave mi, dur mu?"""
        self.slalom_count += 1
        if self.front_distance > self.slow_distance:
            self._explain(
                f"SLALOM bitti ({self.slalom_count} engel gecildi) -> serit")
            self._end_avoidance()
            return
        if self.slalom_count >= self.slalom_max_weaves:
            # Weave tavanı doldu, engel hâlâ önde -> slalom çözmüyor.
            self._explain(
                f"SLALOM {self.slalom_count} weave sonunda engel gecilemedi "
                f"(front={self.front_distance:.1f}) -> OBSTACLE_STOP")
            self._abort_avoidance()
            return
        # FIX (2026-07-21): eskiden yön körlemesine ters çevriliyordu
        # (`right if left else left`) — lidar'a hiç sorulmuyordu. Artık
        # hangi tarafın gerçekten açık olduğu yeniden değerlendirilir.
        direction = self._pick_avoid_direction()
        if direction is None:
            self._explain(
                f"SLALOM weave #{self.slalom_count} bitti, iki taraf da kapali "
                f"(left={self.left_distance:.1f} right={self.right_distance:.1f}) "
                f"-> OBSTACLE_STOP")
            self._abort_avoidance()
            return
        self._begin_weave(direction)
        self._explain(
            f"SLALOM weave #{self.slalom_count} bitti, engel devam "
            f"(front={self.front_distance:.1f}) -> {direction} yone yeni weave")

    def _pause_avoidance(self):
        """Kaçınmayı güvenli duruşla YARIDA KES (çarpışma koruması).
        avoid_blocked KİLİTLEMEZ: _obstacle_stop_control bekleyip yol/yan
        açılınca yeniden dener — her deneme tam duruştan başladığı için
        güvenlidir."""
        self.avoid_direction = None
        self.avoid_phase     = None
        self.slalom_count    = 0
        self.steering_angle  = 45
        self.signal_status   = 3
        self._avoid_trigger_since = None
        self._set_state(DriveState.OBSTACLE_STOP)
        self._stop_vehicle()

    def _abort_avoidance(self):
        """Slalom çözmüyor -> savurmayı bırak, dur. Yol gerçekten açılana
        kadar (_obstacle_stop_control) yeniden slaloma girilmez."""
        self._pause_avoidance()
        self.avoid_blocked = True

    def _end_avoidance(self):
        self.steering_angle  = 45
        self.signal_status   = 0
        self.avoid_direction = None
        self.avoid_phase     = None
        self.slalom_count    = 0
        self.avoid_blocked   = False   # yol açıldı -> slalom tekrar serbest
        self._avoid_trigger_since = None
        self._set_state(DriveState.LANE_FOLLOW)

    # ------------------------------------------------------------
    # Durak
    # ------------------------------------------------------------
    def _bus_stop_control(self):
        t = self._elapsed()
        if t < self.bus_stop_align_time:
            self.brake          = 0
            self.target_speed   = self.park_speed
            self.steering_angle = 25
            self.signal_status  = 1
            return
        wait_end = self.bus_stop_align_time + self.bus_stop_wait_sec
        if t < wait_end:
            self._stop_vehicle()
            self.signal_status = 3
            return
        exit_end = wait_end + self.bus_stop_exit_time
        if t < exit_end:
            self.brake          = 0
            self.target_speed   = self.park_speed
            self.steering_angle = 65
            self.signal_status  = 2
            return
        self.signal_status  = 0
        self.steering_angle = 45
        self._move_vehicle(self.default_speed)
        self._set_state(DriveState.LANE_FOLLOW)

    # ------------------------------------------------------------
    # Park
    # ------------------------------------------------------------
    def _park_search_control(self):
        self.brake         = 0
        self.target_speed  = self.park_speed
        self.signal_status = 1
        if self.front_distance < 3.0 and self.right_distance > 3.5:
            self._set_state(DriveState.PARKING)

    def _parking_control(self):
        if self.left_distance > 4.0:
            self.steering_angle = 65
        elif self.right_distance > 4.0:
            self.steering_angle = 25
        else:
            self.steering_angle = 45
        self.brake        = 0
        self.target_speed = self.park_speed
        if self.front_distance < 1.5:
            self._stop_vehicle()
            self.signal_status = 3

    # ------------------------------------------------------------
    # Çıktı
    # ------------------------------------------------------------
    def _lane_blend(self):
        """Kontrol node'una "şerit çıktısını ne kadar karıştır" der (0..1).
        Kaçınma sırasında şerit tamamen atılmamalı: eskiden OBSTACLE_AVOID'da
        direksiyon sabit 70/25/20/65 idi ve şerit yok sayılıyordu (araçta
        slalom süresinin %30-97'sinde geçerli şerit verisi VARDI)."""
        if self.state == DriveState.OBSTACLE_AVOID:
            if self.avoid_phase in ("return", "align"):
                return self.avoid_lane_blend_return
            if self.avoid_phase == "pass":
                # Geçiş fazında şerit KARIŞMAZ: araç bilerek şeridin dışında,
                # şerit takipçisi onu engelin üstüne geri çekerdi.
                return self.avoid_lane_blend_pass
            return self.avoid_lane_blend_escape
        return 0.0

    def get_decision(self):
        return {
            "state":            self.state.name,
            "steering_angle":   int(self.steering_angle),
            "target_speed_kmh": float(self.target_speed),
            "brake":            int(self.brake),
            "signal_status":    int(self.signal_status),
            "speed_limit":      float(self.speed_limit),
            "avoid_phase":      self.avoid_phase,
            "lane_blend":       float(self._lane_blend()),
        }
