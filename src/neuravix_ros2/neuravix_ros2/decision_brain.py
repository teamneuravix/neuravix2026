#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NeuraVix karar beyni (FSM) - CARLA'dan / gerçek araçtan bağımsız çekirdek.

neuravix_control_node.py (CARLA sim) ve neuravix_control_node_real.py (gerçek
Bee1 aracı) bu modülü ortak kullanır. Bu dosyada CARLA'ya veya araca özel hiçbir
şey olmamalı — sadece /master mesajlarından karar üreten saf mantık. Sim/gerçek
farkı sadece o iki dosyadaki ROS I/O (mesaj tipi, topic adı) katmanındadır.
"""

import re
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

# 24/25: eski sonyaris.pt'nin ek sinifllari; sign_detect_event icinde hala
# ILERI_SAG/ILERI_SOL'a cevriliyor (ham id yayinlayan eski bir dugume karsi
# savunma). Yeni sinif adi -> id esleme yolu bunlari zaten dogru id ile
# yayinlar, yani normal akista kullanilmazlar.
ADA_ETRAFINDA   = 26
ISIKLI_TABELA   = 27
SAGDAN_GIDINIZ  = 28
SOLDAN_GIDINIZ  = 29
SERIT_DUZENLEME = 30

SIGN_NAMES = {
    TRESPASS: "trespass", GIRILMEZ: "girilmez", ILERI_SOL: "ileri_sol",
    ILERI_SAG: "ileri_sag", SOLA_DON: "sola_don", HIZ_20: "hiz_20",
    HIZ_30: "hiz_30", HIZ_20B: "hiz_20b", SAGA_DON: "saga_don",
    SAGA_DON_YASAK: "saga_don_yasak", SOLA_DON_YASAK: "sola_don_yasak",
    DUR: "dur", PARK_YASAK: "park_yasak", PARK: "park", DURAK: "durak",
    KIRMIZI_ISIK: "kirmizi_isik", SARI_ISIK: "sari_isik",
    YESIL_ISIK: "yesil_isik", ENGELLI_PARK: "engelli_park", KAVSAK: "kavsak",
    YAYA_GECIDI: "yaya_gecidi", IKI_YON: "iki_yon", ILERI: "ileri",
    TUNEL: "tunel", ADA_ETRAFINDA: "ada_etrafinda_donunuz",
    ISIKLI_TABELA: "isikli_trafik_levhasi", SAGDAN_GIDINIZ: "sagdan_gidiniz",
    SOLDAN_GIDINIZ: "soldan_gidiniz", SERIT_DUZENLEME: "serit_duzenleme",
}


# ================================================================
# MODEL SINIF ADI -> KANONIK ID  (18.08.2026)
# ================================================================
# NEDEN: tabela_tespit_node eskiden YOLO'nun ham sinif indeksini dogrudan
# /master'a basiyordu. Bu tablo ise sonyaris.pt'nin (26 sinif, Ingilizce)
# indekslerinden tureme. Aktif model best6.pt'nin (22 sinif, Turkce) indeks
# duzeni tamamen farkli oldugu icin sozlesme sessizce kirilmisti: model
# "PARK" (11) gorunce beyin DUR (11) okuyup duruyor, "SagdanGidiniz" (15)
# gorunce KIRMIZI_ISIK (15) okuyup fren yapiyordu.
#
# COZUM: /master'daki id KANONIKTIR ve asagidaki sabitlerle tanimlidir; model
# indeksi degildir. Tespit dugumu, modelin sinif ADINI bu tabloyla kanonik
# id'ye cevirip oyle yayinlar. Sonuc: model degistiginde (best6 -> eda ->
# ayri isik modeli -> birlesik model) beyin ve iki kontrol dugumu hic
# degismez; yeni bir model yalnizca buraya birkac ad ekletir.
#
# Tanimadigi adi olan sinif YAYINLANMAZ (uydurma id uretmektense sessiz
# kalmak guvenli) ve dugum acilista bir kez uyarir.
#
# Hiz limiti tabelalari (HIZ_20/30/20B) bilincli olarak eslenmemistir:
# 2026 veri setinde yoklar ve yarismada gerekmiyorlar. Sabitleri ve FSM
# dallari sonyaris.pt uyumlulugu icin duruyor.
#
# Isik renkleri (KIRMIZI/SARI/YESIL) best6'da YOK. Ayri egitilecek isik
# modelinin adlari (red_light/kirmizi/... ) asagida hazir bekliyor: o model
# ayni /master ID-3 formatiyla yayin yapinca beyin degisiklik gerektirmez.
# best6'nin "IsikliTrafikLevhasi" sinifi bir LEVHADIR, isigin kendisi degil
# -> ISIKLI_TABELA'ya eslenir, FSM'de karsiligi yoktur (davranis uretmez).

_SIGN_TR = str.maketrans({
    'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 'Ğ': 'G', 'ğ': 'g',
    'Ü': 'U', 'ü': 'u', 'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c',
})


def _sign_key(name):
    """Sinif adini esleme anahtarina indirger: Turkce harfler sadelestirilir,
    kucuk harfe cevrilir, alfanumerik olmayan her sey atilir.
    'IleriMecburiYön' -> 'ilerimecburiyon', 'no_left turn' -> 'nolefturn'."""
    s = str(name).translate(_SIGN_TR).lower()
    return ''.join(ch for ch in s if ch.isalnum())


# kanonik id -> o id'ye karsilik gelen model sinif adlari (tum modeller)
_SIGN_ALIASES = {
    TRESPASS:        ("trespass_sign", "trespass"),
    GIRILMEZ:        ("no_entry", "GirisiOlmayanYol", "girilmez"),
    ILERI_SOL:       ("straight_or_left_only", "IleriVeSolaMecburiYon", "ileri_sol"),
    ILERI_SAG:       ("straight_or_right_only", "IleriVeSagaMecburiYon", "ileri_sag"),
    SOLA_DON:        ("left_only_ahead", "IleridenSola", "SolaMecburiYon", "sola_don"),
    HIZ_20:          ("20_speed_limit_end",),
    HIZ_30:          ("30_speed_limit",),
    HIZ_20B:         ("20_speed_limit",),
    SAGA_DON:        ("right_only_ahead", "IleridenSaga", "SagaMecburiYon", "saga_don"),
    SAGA_DON_YASAK:  ("no_right_turn", "SagaDonulmez"),
    SOLA_DON_YASAK:  ("no_left turn", "no_left_turn", "SolaDonulmez"),
    DUR:             ("stop", "DUR"),
    PARK_YASAK:      ("no_parking", "ParkEtmekYasak"),
    PARK:            ("park", "PARK"),
    DURAK:           ("bus_stop", "DURAK"),
    KIRMIZI_ISIK:    ("red_light", "red", "kirmizi_isik", "kirmizi"),
    SARI_ISIK:       ("yellow_light", "yellow", "amber", "sari_isik", "sari"),
    YESIL_ISIK:      ("green_light", "green", "yesil_isik", "yesil"),
    ENGELLI_PARK:    ("disabled_park", "engelli_park"),
    KAVSAK:          ("junction", "kavsak"),
    YAYA_GECIDI:     ("pedestrian_past", "YayaGecidi", "crosswalk", "yaya_gecidi"),
    IKI_YON:         ("two_side_past", "IkiYonluYol", "IkiYonluYol_2",
                      "IkiYonluYol_images", "iki_yon"),
    ILERI:           ("ahead", "IleriMecburiYön", "ileri"),
    TUNEL:           ("tunnel", "TUNEL"),
    ADA_ETRAFINDA:   ("AdaEtrafindaDonunuz", "roundabout"),
    ISIKLI_TABELA:   ("IsikliTrafikLevhasi",),
    SAGDAN_GIDINIZ:  ("SagdanGidiniz",),
    SOLDAN_GIDINIZ:  ("SoldanGidiniz",),
    SERIT_DUZENLEME: ("SerıtDuzenlemeLevhasi", "SeritDuzenlemeLevhasi"),
}

SIGN_NAME_TO_ID = {}
for _sid, _names in _SIGN_ALIASES.items():
    for _nm in _names:
        _k = _sign_key(_nm)
        if _k in SIGN_NAME_TO_ID and SIGN_NAME_TO_ID[_k] != _sid:
            raise ValueError(f"tabela adi cakismasi: {_nm!r}")
        SIGN_NAME_TO_ID[_k] = _sid
del _sid, _names, _nm, _k


# Bazi modeller sinif adina resmi levha kodunu ekliyor: "DUR_TT-2",
# "DURAK_B-22", "ADA_ETRAFINDA_DONUNUZ_TT-37". Duz ad eslemesi bunlari
# kaciriyordu ve eslenmeyen sinif YAYINLANMADIGI icin arac DUR tabelasinda
# hic durmuyordu (20.08.2026, Yasin_Her_Sey.pt). Ad bulunamazsa sondaki
# kod eki atilip bir kez daha denenir.
_KOD_EKI = re.compile(r"[_\s-]+[A-Za-z]{1,3}[-_]?\d+\s*$")


def canonical_sign_id(class_name):
    """Model sinif adini kanonik /master ID-3 sinif id'sine cevirir.
    Taninmayan ad icin None doner (cagiran taraf yayin yapmamalidir)."""
    sid = SIGN_NAME_TO_ID.get(_sign_key(class_name))
    if sid is None:
        kisa = _KOD_EKI.sub("", str(class_name))
        if kisa != str(class_name):
            sid = SIGN_NAME_TO_ID.get(_sign_key(kisa))
    return sid


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
        # _smooth_angle'in kesirli ic durumu (bkz. _smooth_angle): tamsayiya
        # yuvarlama her karede tekrarlanirsa kucuk duzeltmeler yutulur.
        self._steer_f       = None
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
        # KIRMIZI ISIK EMNIYET SUPABI (18.08.2026)
        # RED_LIGHT_STOP'tan cikisin tek yolu YESIL_ISIK gormekti; zaman asimi,
        # mesafe siniri, alternatif cikis yoktu. Bu onu tek KILITLI durum
        # yapiyordu (STOP_SIGN 3 sn, CROSSWALK_STOP 5 sn sonra kendi cikar).
        # Iki gercek senaryo araci kalici durduruyordu:
        #   1) Yanlis tespit: DUR tabelasi kirmizi sekizgen; 2 sinifli isik
        #      modeli 400 dogrulama karesinde 10 kez DUR'a 'red' dedi. Tabela
        #      goruste kaldigi surece durum surekli tazelenir, arac hic kalkmaz.
        #   2) Gercek kirmizi: arac isigin altina fazla sokulup isik kadraj
        #      disinda kalirsa yesili HIC goremez.
        # Cozum: duruma GIRISTEN itibaren mutlak tavan. Bilerek "kirmiziyi en
        # son gorme zamani" DEGIL — yanlis tespitte tabela hep goruste oldugu
        # icin o sayac hic dolmaz ve supap ise yaramazdi.
        # 40 sn: normal bir isik dongusu bunun altinda; supap yalnizca gercek
        # kilitlenmede devreye girer. 0 = kapali (eski davranis).
        self.red_light_timeout = 40.0
        # Supap actiktan sonra ayni tespit araci hemen tekrar kilitlemesin diye
        # KIRMIZI_ISIK'a uzun cooldown. Yoksa 40 sn dur / 1 sn git dongusu olur
        # (kirmizinin normal cooldown'u 1.0 sn).
        self.red_light_release_cooldown = 15.0

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
        # "KENDİ ŞERİDİME DÖN" refleksi (14.08.2026, operatör kararıyla
        # KAPATILDI). Açıkken araç komşu şeritte paralel giderken kendi
        # şeridi boşalır boşalmaz dönerdi — 14.08 koşusunda bulunduğu şeritte
        # 9.9 m ilerde engel varken bile döndü, çünkü "kendi şeridi" açılmıştı.
        # İki şeritli KAPALI PİSTTE bunun koruduğu bir şey yok: karşı yön
        # trafiği yok, aracın ait olduğu bir şerit de yok — açık olan şeritte
        # gitmek doğru davranış. Kapalıyken dönüş yalnızca BULUNDUĞUN şerit
        # kapanınca (front) ya da mesafe tavanlarıyla olur -> gerçek zig-zag.
        # Karşıdan trafik gelen gerçek bir yolda True yapılmalı; o zaman
        # slalom_return_free eşiği tekrar anlam kazanır.
        self.return_home_when_free = False
        self.obstacle_replan_wait = 3.0
        self.avoid_direction      = None
        self._avoid_trigger_since = None

        # --- ŞERİT İNDEKSİ (2026-08-14) ---
        # Lidar şerit kavramı bilmez, sadece boşluk ölçer: boş bir omuz/banket
        # her zaman 99 okur ve karşı şeridi (içinde başka engel olabilen) hep
        # yener. 14.08 CARLA testlerinde araç bu yüzden defalarca SAĞA, yolun
        # dışına kaçtı — sol=17.5 (2. engel) vs sag=99 (boş omuz).
        # Çözüm: yolun kaç şeridi olduğunu FSM'e söyle.
        #   lane_index : şu an hangi şerit (0 = başlangıç şeridi, +1 sol
        #                komşu, -1 sağ komşu). Kaçış fazında hedef şeride
        #                geçer, dönüşte geri iner — decision_dump'ta görünür.
        #   lane_min/max : yolun sınırları. Varsayılan 0..1 = "en sağ şerittesin
        #                ve solunda bir şerit var" (görev yolu: 2 şeritli).
        #                Bu haliyle SAĞA kaçış geometrik olarak yasak.
        # 3 şeritli bir yolda lane_max=2, ortadan başlıyorsan lane_min=-1.
        self.lane_index = 0
        self.lane_min   = 0
        self.lane_max   = 1
        self._lane_home = 0
        self._return_hard = False
        # Lidar yanal klerans profili (bkz. obstacle_event / _klerans).
        self._profil     = None
        self._profil_y0  = 0.0
        self._profil_dy  = 0.5
        self._profil_t   = None

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
        # Dönüş fazı burun şerit yönüne bu kadar yaklaşınca biter (derece).
        # Tek başına yanal eşiği beklemek aracı 30-45 derece fazla döndürüyordu
        # (bkz. _obstacle_avoid_control "return" bloğu, 19.08.2026 ölçümü).
        # Donus fazi bu kadar ters aci biriktirince biter; kalan yanali
        # align fazi bu aciyla kapatir. Kacisin tepe acisi ~30-40 derece
        # oldugu icin donusun 20'de kesilmesi simetriyi bozmaz.
        # 45 -> 25 (20.08.2026). 45 derece cok genisti: aci tavani ancak
        # burun 45'e vardiginda ateşleniyor, tekerlek 3 s'de ters kilide
        # gidene kadar burun 70+'e savruluyordu. 19.08'de 20 denenmis ve
        # "sim'i bozdu" diye reddedilmisti — o sim direksiyon gecikmesini
        # MODELLEMIYORDU, karar gecersizdi. 25 ile maks aci 54 -> 36 derece.
        self.slalom_return_max_deg = 25.0
        # Donus fazi FSM acisi. None = kacisin aynasi (eski davranis).
        # 25 gibi bir sayi daha yumusak donus verir (bkz. "return" fazi).
        # 25.0 (20.08.2026, gecikmeli masa simulatorunde olculdu). Sabit
        # ayna (=15, tam ters kilit) burnu -34..-72 dereceye savuruyordu;
        # arkadasin saha teshisi bu, dogrulandi. 25 ile P1 bitis acisi
        # -34 -> -7 dereceye indi.
        self.slalom_return_steer = 25.0
        # Yaw'sız yedek mesafeler ~yarım-S yay uzunluğu (tam kilit R≈3.06,
        # 1.5 m yanal için yay ≈ 3.2 m) — 3.0 m hedefle tutarlı tutuldu.
        self.slalom_out_distance    = 3.2   # m, kaçış fazı yolu (yaw yoksa)
        self.slalom_pass_distance   = 2.0   # m, paralel geçiş fazı yolu
        # Paralel geçişin TAVANI: "dönülecek şerit boş" kapısı açılmasa bile
        # bu kadar yol gidilince dönülür (bkz. kapı kilitlenmesi notu).
        # 8 m denendi ve masa suitini bozdu: S2'de (10 m arayla iki engel)
        # geçişin uzun sürmesi MEŞRU, kendi şeridimizde gerçekten engel var.
        # Tarama: 8 m -> S2 başarısız, 10 m ve üstü 5/5.
        # 12 -> 20 m (14.08.2026): 12 m'de tavan, front kuralının ÖNÜNE
        # geçiyordu — CARLA koşusunda geçiş 12 m'yi doldurdu ve dönüş
        # front=5.9 iken tavanla başladı, yani 4.5 m eşiği hiç görülmedi.
        # Tavan bir YEDEK olmalı, asıl karar front'ta. 20 m, 30 m'lik weave
        # tavanının altında kalıp dönüş+hizalanmaya (~4.4 m) yer bırakıyor.
        # Bu tavan yalnızca "gectigim seritte hicbir sey yok" halinde
        # tetiklenir; o durumda da karsi seritte sonsuza kadar kalmamak icin
        # gerekli.
        # 20 -> 4.5 m (17.08.2026, CARLA'da olculdu). Gecis fazi "engelin
        # yanindan gec" fazidir, "karsi seritte bekle" fazi DEGIL. 20 m'lik
        # tavan + return_home_when_free=False birlesince arac engeli gectikten
        # sonra karsi seritte 14 METRE oyalaniyor ve ancak onundeki SONRAKI
        # engel 4.5 m'ye girince donmeye calisiyor — o an tam kilitle saga
        # kirip sag bariyere 0.9 m yaklasip duruyordu.
        # Donusumlu slalomun dogru ritmi: cik -> engeli gec -> HEMEN don ->
        # sonraki engelde tekrar cik. Engeli gecmek icin gereken yol:
        # tetik 3.1 + arac boyu 2.74 + engel derinligi ~1.1 = 6.9 m; kacis
        # fazi ~3 m'sini zaten harciyor, gerisi 4 m civari.
        self.slalom_pass_max_distance = 20.0  # m (emniyet tavani)
        # Gectigim seritte onum bu kadar kapanirsa mesafe tavanini bekleme,
        # hemen sende dön. grace: fazin ilk metresinde bakma (kacistan yeni
        # cikarken on sektor gecilen engelin kenarini yalayabilir).
        # 8.0 -> 4.5 (14.08.2026, operatör kararı): "1. engel 4.5 m'de manevra
        # yapıyor, 2. engelde niye yapmasın" — eşik artık ikisinde de aynı.
        # Bu değer avoid_distance'a EŞİT olduğu için, yukarıdaki "geçtiğim
        # şeritte engel" kuralı (fonksiyonda daha ÖNCE bakılır) devreye girer
        # ve dönüş TAM KİLİTLE yapılır — yani kaçışın aynısı. 8.0'a çekilirse
        # iki katmanlı davranış geri gelir: 8 m'de yumuşak dönüş, 4.5 m'de
        # sert. Uyarı olarak kalsın: manevranın kendi yol bütçesi 4.4 m.
        self.slalom_pass_front_min   = 4.5   # m
        self.slalom_pass_front_grace = 1.0   # m
        self.slalom_return_distance = 3.2   # m, dönüş fazı yolu (yaw yoksa)
        self.slalom_align_done_deg  = 8.0   # °, hizalanma bitti eşiği (yaw varsa)
        self.slalom_align_lateral   = 0.6   # m, "şeride ortalandı" eşiği
        # Hizalanmada yanal hatayı kapatan P kazancı (birim/m). 2.5 m ofset
        # -> 10 birim direksiyon (45 -> 35). Açı terimi (1.5/derece) baskın
        # kalsın diye küçük tutuldu; büyütmek salınım riski taşır.
        self.slalom_align_lat_gain  = 4.0
        # Geçiş fazında yanal HEDEFİ tutan P kazancı (birim/m). Bisiklet
        # modeliyle süpürüldü — kaçış 1.75 m'de bıraktıktan sonra 14 m'de
        # varılan ofset ve o sırada oluşan en büyük burun açısı:
        #    3 -> 2.35 m ( 2.7°)   6 -> 2.78 m ( 5.6°)
        #   10 -> 3.16 m ( 9.1°)  15 -> 3.38 m (13.1°)  20 -> 3.47 m (16.7°)
        # 10 seçildi: hedefin %90'ına varıyor, burun 9°'yi geçmiyor (front
        # sektörü fazla eğilmesin) ve 30 m boyunca salınım yok, tek yönlü
        # yaklaşıyor. Daha büyük kazanç araci gecis boyunca acili surdurur.
        # 10 -> 35 (17.08.2026, CARLA'da olculdu). Gecis fazinin direksiyonu
        # "45 - 1.5*bas_hatasi + kazanc*eksik_yanal" — yani yanal P + bas D.
        # 10'luk kazanc bas terimini yenemiyordu: iki CARLA kosusunda da arac
        # 1.5 m hedefin 1.2-1.4'unde takilip 15 m boyunca neredeyse duz gitti
        # (direksiyon 43-45). Sonucu su: yanal 1.19'da kalan arac kendi
        # seridindeki SONRAKI engeli hala on koridorunda goruyor (koridor
        # 0.49..1.89, engel +-0.65) ve "gectigim seritte engel var" deyip
        # geri donuyor -> sag bariyere giriyor. Hedefe varsaydi koridor
        # 0.80..2.20 olacakti ve engel hic gorunmeyecekti.
        self.slalom_pass_lat_gain   = 35.0
        self.slalom_align_distance  = 1.2   # m, hizalanma fazı yolu (yaw yoksa)
        self.slalom_max_time        = 20.0  # s, weave EMNIYET tavanı (odometri ölürse)
        # Asıl tavan bu: hızdan bağımsız. Bütçe, geçiş fazı tavanına kadar
        # uzadığında: escape 3.2 + pass 12.0 + return 3.2 + align 1.2 = 19.6 m.
        # 25 m denendi ve dar kaldı (kapı hiç açılmayan senaryoda weave 23.5 m
        # sürdü, tavana 1.5 m kala bitti); 30 m ~%50 pay bırakıyor. Bu tavana
        # çarpmak artık gerçek bir anormallik demektir, normal işleyiş değil.
        self.slalom_max_distance    = 30.0  # m
        # KAÇINMA SIRASINDA ÇARPIŞMA KORUMASI (2026-08-03 — eski kodda YOKTU:
        # OBSTACLE_AVOID boyunca engel mesafeleri tamamen yok sayılıyordu,
        # dönüş fazında engelin üstüne sürerken hiçbir fren yoktu). pass/return
        # fazlarında front < stop_distance -> dur; escape'te burun henüz engele
        # dönük olabileceği için daha sıkı (daha yakın) acil eşik kullanılır.
        # KACIS FAZI CIKIS ESIGI (20.08.2026'da parametre oldu, once 0.5 sabitti).
        # Tasarim: simetrik S -> kacis yanal hedefin YARISINI alir, karsi
        # kirma digerini getirir. Bu, tekerlegin ANINDA ters kilide gittigini
        # varsayar. GERCEKTE tekerlek 10 birim/s doner; kilitten kilide
        # 72 birim = 7.2 s ve o sure boyunca arac ESKI yone donmeye devam
        # eder. Olculdu (lokal_0820_0722): hedef 1.7 m iken yanal 3.0'a
        # cikti, fazla 1.3 m. Bu yuzden kacis daha ERKEN bitmeli.
        # 0.5 -> 0.30 (20.08.2026, olculdu). Kacis fazi yanalin YARISINDA
        # bitiyordu; ama yanal bas acisinin GECIKMELI gostergesi ve tekerlek
        # ters kilide 3 s'de gittigi icin faz bittikten sonra da yanal
        # birikmeye devam ediyor. Aractaki sonuc: hedef 1.7 iken yanal 2.85.
        # 0.30 ile masa siminde yanal tepe 2.51 -> 1.82 (hedefe oturdu).
        self.slalom_escape_lat_frac = 0.30
        # DIREKSIYON GECIKMESI TELAFISI (20.08.2026, olculdu).
        # Tekerlek 10 birim/s doner (steering_ctrl max_delta=68 ile);
        # kilitten kilide 72 birim = 7.2 s. Faz kontrolculeri "su anki
        # hataya" gore komut verirse, tekerlek varana kadar arac eski yone
        # donmeye devam eder ve her faz asar. Bu yuzden hata, yaw hiziyla
        # steer_lead_time saniye ILERI tasinir (klasik lead kompanzasyonu):
        #     err_etkin = err + steer_lead_time * yaw_hizi
        # VARSAYILAN 0 (KAPALI) — 20.08.2026 masa taramasi: lead acikken suite
        # HER slew degerinde daha kotu cikti (gecikmesiz 7/8 -> 5/8, slew=14'te
        # 6/8 -> 3/8). Sebep: tekerlek hiz siniri BAGLAYICI kisit oldugunda
        # "daha sert kir" demek hicbir sey kazandirmiyor, sadece komutu
        # doyuma itiyor. Kod duruyor cunku direksiyon HIZLANDIKTAN sonra
        # (steering_ctrl max_delta yukseltilince) kalan kucuk gecikme icin
        # dogru arac odur; once slew olculsun, sonra denensin.
        self.steer_lead_time = 0.0    # s  (0 = KAPALI, varsayilan)
        self.avoid_emergency_front  = 1.0   # m, escape fazında acil durma eşiği
        # SIKISIK YAKLASMA HIZI (19.08.2026). Engel avoid_distance icindeyken
        # HENUZ acilacak bir taraf yoksa (iki yan koridor kapali / viraj
        # bastirmasi / onay suruyor) eskiden slow_speed (6 km/h) ile
        # yaklasiliyordu. Masa sim P1'de olculdu: taraf acilana kadar gecen
        # 1.0 s'de arac 1.7 m yaklasip 2.6 m'ye dusuyor, orada baslayan kacis
        # tamamlanamadan acil esige (1.0 m) carpip kalici OBSTACLE_STOP'a
        # dusuyordu. Kacis icin gereken boylamsal yol R=3.26 m'de ~2.5 m —
        # yani manevraya 2.6 m'de girmek matematiksel olarak gec. Suruklenme
        # hizi dusurulunce taraf acildiginda elde 3.5+ m kaliyor.
        self.blocked_speed          = 2.5   # km/h, cikis yokken surunme hizi
        # ÖN OKUMASINA GÜVEN EŞİĞİ (17.08.2026, ölçüldü). Ön koridor araca
        # SABİT ve DÜZ; araç açı yaptığı anda dar pistte yan bariyeri tarar:
        # y=+0.5'te 20° -> duvar front=9.5 m, 31° -> 6.3 m, 44° -> 4.7 m
        # okunur. Yani her weave ortasında "önümde engel var" görünür, oysa
        # görülen duvardır. Bu yüzden weave içindeki YENİDEN PLANLAMA
        # kararları (ikinci engel, erken dönüş) yalnızca burun şerit yönüne
        # yakınken alınır. Acil durma (avoid_emergency_front=1.0 m) BU KAPIYA
        # TABİ DEĞİLDİR — 44°'de duvar 4.7 m okunur, 1.0 m'yi hiç tetiklemez,
        # yani gerçek bir çarpışma riski her açıda durdurur.
        self.front_trust_deg        = 12.0
        # Bu kadar kaymissak "kendi seridime donuyorum" sayilir ve o yonde
        # yan klerans sarti aranmaz (bkz. _pick_avoid_direction).
        self.home_return_lateral    = 0.5
        # Yanal hedefin bu kesrine varmadan "gectigim seritte engel" kurali
        # yon degistirtmez (bkz. _weave_tamamlandi).
        self.weave_done_frac        = 0.85
        # Hareketsizlik koruması: bu sürede bu kadar bile ilerlemediyse manevra
        # gerçekleşmiyor demektir — direksiyonu savurmayı bırak, dur.
        self.stall_timeout         = 4.0   # s
        self.stall_min_distance    = 0.25  # m
        # Şerit karışımı (kontrol node'u kullanır): kaçışta şerit büyük ölçüde
        # yok sayılır; geçişte HİÇ karışmaz (şeridin dışındayız, şerit takipçisi
        # bizi engelin üstüne geri çekerdi); dönüş fazında merkeze çeker.
        self.avoid_lane_blend_escape = 0.15
        self.avoid_lane_blend_pass   = 0.0
        # 0.55 -> 0.15 (17.08.2026, CARLA'da olculdu). Donus fazinda komutun
        # %55'i serit takipcisinden geliyordu ve o "duz git" diyor: FSM 25
        # (belirgin sag) veriyor, araca 36 gidiyordu — neredeyse duz. Sonucu:
        # donus 19 saniye / 11 m surdu, arac yanal 1.4'ten ancak 0.85'e
        # inebildi ve o sirada bir sonraki engele girip durdu. Kacis fazi
        # zaten 0.15 kullaniyor ve duzgun calisiyor; donus de simetrik olmali.
        # Serit takibi weave BITTIKTEN sonra zaten devreye giriyor.
        # 0.15 -> 0.55 (20.08.2026). 17.08'de 0.55'ten 0.15'e CARLA
        # olcumuyle indirilmisti ("serit takipcisi duz git diyor, donusu
        # sulandiriyor") — o CARLA kosusunda direksiyon aninda variyordu.
        # Gercek araçta donus zaten fazla sert; serit katkisi merkezlemeyi
        # geri getiriyor. Gecikmeli simde arkadasin onerisiyle birlikte
        # dogrulandi.
        self.avoid_lane_blend_return = 0.55
        # Zaman tabanlı YEDEK (hiç hareket kaynağı beslenmezse, ör. sim):
        self.slalom_out_time    = 2.0
        self.slalom_pass_time   = 2.0
        self.slalom_return_time = 2.0
        self.slalom_align_time  = 1.0
        # TAMAMLANAN WEAVE sayısı — geçilen ENGEL sayısı DEĞİL. Bir weave
        # (escape->pass->return->align) tek sayılır ama paralel geçiş fazı
        # boyunca birden fazla engelin yanından geçilmiş olabilir; tersine,
        # bir engel için birden çok weave de yapılabilir. slalom_max_weaves
        # bu sayaca bakar. Log metinleri buna göre yazılmalı: "1 engel
        # geçildi" demek yanıltıcıydı (14.08.2026'da tam bu soruldu).
        self.slalom_count     = 0
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
        # Bu kadar yol alan weave "ilerleme" sayilir ve slalom_count sifirlanir
        # (bkz. _weave_finished). Kacis fazi tek basina ~3 m surer; yerinde
        # sallanan arac bu esigi asamaz, pisti gecen arac her weave'de asar.
        self.slalom_progress_distance = 3.0
        # Kacis fazinin direksiyonu (45=duz, 75=tam kilit). Bkz.
        # _obstacle_avoid_control escape fazi: tam kilit dar pistte araci
        # 44 derece dondurup kor birakiyordu.
        # 75 = tam kilit = ESKI davranis (varsayilan degismedi). Dar pistte
        # 44 derece dondurur ve arac ON KORIDORDA duvari gorur; asil duzeltme
        # front_trust_deg kapisidir, bu sadece ayar dugmesi olarak duruyor.
        # Olculdu: 62'ye indirmek S1'i bozuyor (kacis yetismiyor, front 1.0'a
        # dusuyor), 67 gecerli bir ara deger.
        self.slalom_escape_steer = 75.0
        self.slalom_total      = 0      # sadece kayit/log icin, tavani etkilemez

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
        self._yaw_rate = None         # deg/s, lead kompanzasyonu icin (EMA)
        self._lateral       = 0.0     # weave başına göre yanal ofset (m, sol +)
        self.pos_x          = 0.0     # odometri konumu (update_motion(x=,y=))
        self.pos_y          = 0.0
        self._pos_ok        = False
        self._weave_pos_ref = None    # weave başındaki (x, y, yaw)
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
    def update_motion(self, speed_mps=None, distance=None, yaw=None,
                      x=None, y=None):
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
        yaw_prev = self.yaw if self._yaw_ok else None
        dt_yaw = (now - self._last_motion_t) if self._last_motion_t else 0.0
        if not (0.0 < dt_yaw < 1.0):
            yaw_prev = None
        if yaw is not None:
            self.yaw = float(yaw)
            self._yaw_ok = True
        if x is not None and y is not None:
            self.pos_x, self.pos_y = float(x), float(y)
            self._pos_ok = True

        # YANAL OFSET — iki kaynak, konum tercih edilir (14.08.2026).
        #
        # 1) KONUMDAN (tercih): weave başındaki konuma göre yer değiştirmenin,
        #    o andaki yöne DİK bileşeni. Tek adımlık geometri, hata birikmez.
        # 2) YAW İNTEGRALİ (yedek): sin(yaw-ref) * adım toplamı. Bu bir ÖLÜ
        #    HESAP ve sürükleniyor — CARLA'da ölçüldü: 20 m'lik bir weave
        #    sonunda tahmin -1.66 m derken gerçek yer değiştirme +0.17 m'ydi,
        #    yani 1.8 m hata. Araç şeritte ortalıyken beyin "kaydım" sanıp
        #    hizalanma terimiyle onu şeritten dışarı itiyordu. Konum yoksa
        #    (eski davranış) yine bu kullanılır.
        # YAW HIZI (20.08.2026) — lead kompanzasyonu icin.
        # Direksiyon motoru 10 birim/s doner; kilitten kilide 7 s. Fazlar
        # "su anki hataya" gore komut verince, tekerlek hedefe varana kadar
        # arac ESKI yone donmeye devam ediyor ve her faz gecisinde asiyor
        # (olculdu: kacis hedefi 1.7 m iken yanal 3.0'a cikti; masa siminde
        # align fazi -31 dereceye savrulup bariyere girdi). Yaw hizi ile
        # "steer_lead_time saniye sonra nerede olacagim" tahmin edilir.
        if (self._yaw_ok and self.yaw is not None
                and yaw_prev is not None and dt_yaw > 1e-3):
            ham = ((self.yaw - yaw_prev + math.pi) % (2 * math.pi)) - math.pi
            anlik = math.degrees(ham) / dt_yaw
            # EMA: yaw gurultusu dogrudan direksiyona gitmesin
            self._yaw_rate = (0.7 * self._yaw_rate + 0.3 * anlik
                              if self._yaw_rate is not None else anlik)
        step = self.odom_distance - prev_d
        if self.state == DriveState.OBSTACLE_AVOID:
            if self._weave_pos_ref is not None and self._pos_ok:
                x0, y0, yaw0 = self._weave_pos_ref
                dx, dy = self.pos_x - x0, self.pos_y - y0
                # REP-103: +y sol. Başlangıç yönüne dik bileşen (sol pozitif).
                self._lateral = -dx * math.sin(yaw0) + dy * math.cos(yaw0)
            elif (step > 0.0 and self._yaw_ok and self.yaw is not None):
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

    def _engel_hiz_tavani(self):
        """Engel durumuna gore izin verilen en yuksek hiz (km/h) veya None.

        BUG A'NIN IKINCI KATI (19.08.2026): 03.08'de lane_detect_event'in
        kosulsuz default_speed yazmasi duzeltilmisti, ama duzeltme
        `slow_distance icindeysen slow_speed` seklinde SABITLENMISTI. Bu
        yuzden obstacle_event'in daha dusuk bir hiz (blocked_speed) yazmasi
        20 Hz'lik serit olayi tarafindan 50 ms icinde geri eziliyordu —
        engel_event 10 Hz, serit 20 Hz. Iki cagirici da artik ayni tavani
        kullanir, boylece hiz yarisi tekrar dogamaz.
        """
        if self.front_distance >= self.slow_distance:
            return None
        # Kacis penceresi kapaniyorsa surun (bkz. blocked_speed).
        if (self.front_distance < self.avoid_distance
                and (self._in_curve() or self._pick_avoid_direction() is None)):
            return self.blocked_speed
        return self.slow_speed

    def _smooth_angle(self, old_angle, new_angle, alpha=0.35):
        """Direksiyon EMA'si — TEK YÖNLÜ KAYMA (RATCHET) DÜZELTİLDİ (2026-08-13).

        Eski hali sonucu `int()` ile KIRPIYORDU. int() pozitif sayıda aşağı
        yuvarlar, dolayısıyla EMA yalnızca AŞAĞI (=SAĞA) tam yakınsıyor,
        YUKARI (=SOLA) her zaman 2 birim eksik kalıyordu:
            hedef 35, mevcut 45 -> 35  (tam)
            hedef 42, mevcut 45 -> 42  (tam)
            hedef 45, mevcut 35 -> 43  (ASLA 45 olmaz)
            hedef 50, mevcut 35 -> 48
        Dahası tek adımlık artış alpha*(hedef-mevcut) < 1 iken int() değeri
        geri kırpıyor: |hedef-mevcut| < 1/alpha ≈ 2.9 olan SOLA düzeltmelerin
        tamamı yutuluyor, SAĞA olanların tamamı geçiyordu. Sonuç: şerit
        "düz" (45) dese bile direksiyon sağda takılı kalır ve açı tek yönde
        iner. 13.08.2026 CARLA testinde tam olarak bu görüldü
        (43 -> 42 -> 42 -> 35 -> 35, hiç yükselmeden) ve araç sağdaki duvara
        sürüklendi. round() simetriktir; kesirli iç durum (_steer_f) da
        0.5 birimden küçük düzeltmelerin yutulmasını engeller.
        """
        base = self._steer_f
        # steering_angle dışarıdan doğrudan yazılmışsa (_stop_vehicle 45'e
        # zorlar, slalom fazları sabit açı yazar) EMA oradan devam etmeli.
        if base is None or abs(base - float(old_angle)) > 1.0:
            base = float(old_angle)
        self._steer_f = (1 - alpha) * base + alpha * float(new_angle)
        return int(round(self._steer_f))

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
        tavan = self._engel_hiz_tavani()
        self._move_vehicle(self.default_speed if tavan is None else tavan)

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

    def obstacle_event(self, front=None, left=None, right=None,
                       profile=None, profile_y0=None, profile_dy=None):
        if front is not None: self.front_distance = float(front)
        if left  is not None: self.left_distance  = float(left)
        if right is not None: self.right_distance = float(right)
        # YANAL KLERANS PROFILI (17.08.2026). Yoksa None kalir ve tum
        # kullanicilar eski davranisa duser — gercek aracta lidar profil
        # yaymayan bir surumdeyse hicbir sey bozulmaz.
        if profile:
            self._profil     = [float(c) for c in profile]
            self._profil_y0  = float(profile_y0)
            self._profil_dy  = float(profile_dy)
            self._profil_t   = self._now()

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
            # YOL AÇILDI -> hız kısıtını da kaldır (2026-08-13). Eskiden burada
            # sadece `return` vardı; slow_speed'i geri alan TEK yer
            # lane_detect_event'ti. Şerit düğümü kapalıyken (ya da şerit
            # kaybındayken) araç engel çoktan geçtikten sonra bile 6 km/h'de
            # asılı kalıyordu — 13.08 CARLA log'unda "front=4.9 -> yavasla"
            # olayı, engel görüş alanından çıktıktan sonra 6 saniye boyunca
            # ekranda kaldı (olay metni de hız de güncellenmiyordu).
            if self.state == DriveState.LANE_FOLLOW:
                self._move_vehicle(self.default_speed)
            return

        if self.avoid_blocked:
            # Slalom tavanı dolmuştu ve yol hâlâ kapalı -> tekrar slaloma
            # girme (sonsuz weave koruması), dur ve bekle.
            self._set_state(DriveState.OBSTACLE_STOP)
            self._stop_vehicle()
            self.signal_status = 3
            # Gerekçe yazılmazsa önceki olay metni ekranda asılı kalır ve
            # "neden slalom yapmıyor" sorusu cevapsız görünür (2026-08-13).
            self._explain(
                f"ENGEL front={self.front_distance:.1f} -> DUR | slalom kilidi "
                f"(avoid_blocked): {self.slalom_max_weaves} weave denendi, yol "
                f"{self.slow_distance:.1f} m acilana kadar tekrar denenmez")
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
                    f"ENGEL front={self.front_distance:.1f} onay={held:.1f}s "
                    f"sol={self.left_distance:.1f} sag={self.right_distance:.1f} "
                    f"-> SLALOM {direction} (durmadan)")
                return

        # SLALOM YAPILMADI — NEDEN? (2026-08-13)
        # Eskiden burada tek bir "yavasla (seritte kal)" cumlesi vardi ve
        # slalomun neden atlandigi log'dan ANLASILMIYORDU: dort ayri gerekce
        # ayni metni basiyordu (engel henuz uzak / onay suresi dolmadi / viraj
        # bastirmasi / iki yan koridor da kapali). "Bazen slalom yapiyor bazen
        # yapmiyor, belli degil" sikayetinin kaynagi buydu. Davranis
        # DEGISMEDI, sadece gerekce yazdiriliyor.
        if in_curve:
            neden = "VIRAJ -> slalom bastirildi"
        elif self.front_distance >= self.avoid_distance:
            neden = (f"engel henuz uzak (slalom icin <{self.avoid_distance:.1f} "
                     f"gerekiyor)")
        elif held < self.avoid_confirm_time:
            neden = f"onay suruyor {held:.1f}/{self.avoid_confirm_time:.1f}s"
        else:
            # Bir taraf "kapali" gorunurken mesafesi 99 olabilir: o yonde
            # SERIT olmadigi icin (lane_min/lane_max) reddedilmistir. Sebebi
            # ayirt edilebilsin diye ikisi ayri yazilir.
            def _tarif(ad, mesafe, yon):
                if not self._lane_var(yon):
                    return f"{ad}=SERIT YOK"
                return f"{ad}={mesafe:.1f}"
            neden = (f"IKI TARAF DA KAPALI: "
                     f"{_tarif('sol', self.left_distance, 'left')} "
                     f"{_tarif('sag', self.right_distance, 'right')}, "
                     f"gereken >{self.side_min_clear:.1f} "
                     f"(serit={self.lane_index}, izin {self.lane_min}..{self.lane_max})")
        # Cikis yolu yoksa SURUN (bkz. blocked_speed): engel avoid_distance
        # icinde ama slalom baslatilamiyorsa, kalan mesafeyi hizla yemek
        # manevra penceresini kapatir.
        tavan = self._engel_hiz_tavani()
        self._move_vehicle(self.slow_speed if tavan is None else tavan)
        self._explain(f"ENGEL front={self.front_distance:.1f} -> yavasla | {neden}")

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
            self._stop_vehicle()
            if (self.red_light_timeout > 0
                    and self._elapsed() >= self.red_light_timeout):
                # Kosulsuz birak: "yol acikken birak" demek, onu surekli kapali
                # goren bir engel varsa kilidi geri getirirdi. Serbest birakilan
                # arac zaten OBSTACLE_STOP'a takilir, o yol guvenli.
                self._set_state(DriveState.LANE_FOLLOW)
                self._move_vehicle(self.default_speed)
                self._start_cooldown(KIRMIZI_ISIK, self.red_light_release_cooldown)
                self._explain(
                    f"KIRMIZI ISIK zaman asimi ({self.red_light_timeout:.0f} sn, "
                    f"yesil gorulmedi) -> SERIT TAKIBI")
            return
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
    def _lane_var(self, direction):
        """O yöne kaçarsak GERÇEK bir şeride mi geçeriz? (bkz. lane_index)

        Boşluk ölçümü tek başına yetmiyor: omuz/banket/boş arazi de "boş"
        okunur. Bu kontrol yolun kaç şeridi olduğunu bilir, o yüzden asfaltın
        dışına kaçmayı boşluk ne kadar cazip görünürse görünsün reddeder.
        İki taraf da yasaksa _pick_avoid_direction None döner ve araç durur —
        yolun dışına çıkmaktansa durmak doğru davranıştır.
        """
        hedef = self.lane_index + (1 if direction == "left" else -1)
        return self.lane_min <= hedef <= self.lane_max

    def _klerans(self, yan):
        """Arac cercevesinde `yan` metre yandaki koridorda boylamsal klerans.

        `yan` POZITIF = SOL (REP-103). Profil yoksa None doner ve cagiran
        eski davranisina duser.

        Bu, front/left/right'in cevaplayamadigi soruyu cevaplar: o ucu ARACA
        SABIT sektorlerdir ve aracin serit merkezinde oldugunu varsayarlar.
        Weave ortasinda arac kaymistir; kendi seridi artik `-_lateral`
        yanindadir, sabit side_offset'te DEGIL. Sag bariyerli pistte sag
        sektor hep 0 okudugu icin "kendi seridime donebilir miyim" sorusu
        hicbir zaman evet cevabi alamiyordu.
        """
        if not self._profil:
            return None
        i = int(round((yan - self._profil_y0) / self._profil_dy))
        if i < 0 or i >= len(self._profil):
            return None
        return self._profil[i]

    def _weave_tamamlandi(self, lat):
        """Yanal hedefe (buyuk olcude) varildi mi?

        Varilmadan gelen "onumde engel var" sinyali, KENDI seridimizde
        kalan engelin hala koridora degmesi olabilir — o durumda dogru
        tepki geri donmek DEGIL, manevrayi bitirmektir. CARLA'da tam bu
        oldu: yanal 1.19/1.50 iken sonraki engel goruldu, FSM "gectigim
        serit kapali" deyip saga tam kilit kirdi ve sag bariyere girdi.
        Yanal olculemiyorsa (lat None) eski davranis korunur.
        """
        if lat is None:
            return True
        return lat >= self.weave_done_frac * self._weave_lat

    def _front_guvenilir(self, err_deg):
        """Burun şerit yönüne yakınken ön okuması anlamlıdır.

        Açılıyken ön koridor (araca sabit, düz, 30 m) dar pistte yan
        bariyeri tarar ve gerçek bir engelmiş gibi okunur. Heading
        beslenmiyorsa (err_deg None) eski davranış korunur: güven.
        """
        if err_deg is None:
            return True
        return abs(err_deg) <= self.front_trust_deg

    def _pick_avoid_direction(self):
        """Boş tarafı seç (genel, piste bağımsız). Geri dönüş:
        'left' / 'right' / None (iki taraf da kapalı).
        Eşik side_min_clear'dır (2026-08-13): hedef şeritte en az SIĞ kaçışa
        yetecek boşluk aranır; tam mı sığ mı gidileceğine _begin_weave karar
        verir (boşluk >= safe_side_distance ise tam şerit değişimi). Eskiden
        eşik doğrudan safe_side_distance idi ve hedef şeritte yakın engel
        varken (S6 sıkışık çapraz) manevra tamamen reddediliyordu."""
        # EVE DONUS KAPISI (17.08.2026, olculdu). Yan sektorler ARACA SABIT
        # ve "bir serit yana kacarsam ne var" sorusunu, aracin SERIT
        # MERKEZINDE oldugu varsayimiyla cevaplar. Weave ortasinda arac
        # zaten kaymistir; o an sektor hedef seridi degil, onun OTESINI
        # tarar. Olculen ornek: arac sol seritte (yanal +1.5), kendi
        # seridine donmesi gerekiyor, ama sag sektor kendi seridimizi degil
        # onun disindaki SAG BARIYERI goruyor -> sag=0.0 -> "gidecek acik
        # serit YOK" -> dur. Oysa donulecek yer az once cikilan seritti.
        #
        # Bu yuzden GERI DONUS yonunde yan klerans sarti aranmaz; sinir
        # yine lane_min/lane_max'tir (yoldan cikilmaz) ve onumuzdeki engel
        # zaten front ile ayrica kontrol edilir. Ileri (eve UZAKLASAN) yon
        # icin sart aynen gecerlidir.
        eve_donus = None
        if self._pos_ok and abs(self._lateral) > self.home_return_lateral:
            eve_donus = "right" if self._lateral > 0.0 else "left"

        left_ok  = ((self.left_distance > self.side_min_clear
                     or eve_donus == "left")
                    and self._lane_var("left"))
        right_ok = ((self.right_distance > self.side_min_clear
                     or eve_donus == "right")
                    and self._lane_var("right"))
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
            # FRENİ DE BIRAK (2026-08-13): bu fonksiyon en başta
            # _stop_vehicle() çağırıyor (fren=1, hız=0) ve eskiden buradan
            # freni bırakmadan LANE_FOLLOW'a geçiliyordu. Freni geri alan tek
            # yer lane_detect_event'ti; şerit düğümü yavaşken (13.08 CARLA
            # testinde YOLO 3 FPS) araç saniyelerce "LANE_FOLLOW ama fren=1,
            # hız=0" durumunda kalıyordu — log'da state LANE_FOLLOW <->
            # OBSTACLE_STOP arasında gidip gelirken hız hep 0'dı ve araç hiç
            # hareket etmedi.
            self._move_vehicle(self.default_speed)
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
        self._lane_home       = self.lane_index   # dönüşte hedef şerit
        self._return_hard     = False            # bkz. "return" fazı
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
        # Konum referansı: yanal ofset bundan GEOMETRİK olarak ölçülür
        # (bkz. update_motion). Konum beslenmiyorsa None kalır ve yaw
        # integrali yedeğe düşer.
        self._weave_pos_ref   = ((self.pos_x, self.pos_y, self.yaw)
                                 if (self._pos_ok and self._yaw_ok
                                     and self.yaw is not None) else None)
        self._avoid_trigger_since = None
        self.signal_status    = 2 if direction == "left" else 1
        self._set_state(DriveState.OBSTACLE_AVOID)

    def _phase_next(self, new_phase):
        # ŞERİT İNDEKSİ faz sınırlarında güncellenir. Fazlar tam da şerit
        # çizgisinin geçildiği anlarda değişiyor: "pass" hedef ofsetin
        # YARISINDA başlar (yani komşu şeride girerken), "align" da dönüş
        # ofsetinin yarısında (yani kendi şeridimize girerken). Böylece
        # lane_index aracın fiziksel olarak bulunduğu şeridi gösterir.
        if new_phase == "pass":
            self.lane_index = self._lane_home + (
                1 if self.avoid_direction == "left" else -1)
        elif new_phase == "align":
            self.lane_index = self._lane_home
            # SERT MOD BURADA BITER (14.08.2026). _return_hard hem "return"
            # hem "align" fazini etkiliyordu: align'in isi zaten SERIDE
            # ORTALANMAK ve bunu en iyi serit takipcisi yapar, ama sert modda
            # onun agirligi 0.55 yerine 0.15'e dusuyordu. 3 engelli zincir
            # kosusunda sonuc su oldu: tam kilitli donusten sonra hizalanma
            # direksiyonu 70'te doydu, arac seridin SAGINA tasti ve 3. engel
            # hem front hem SOL sektore girdi (sol=3.2 -> 0.9), "iki taraf da
            # kapali" deyip durdu. Sert kirisin yeri serit DEGISTIRME fazi;
            # ortalanma her zaman yumusak ve serit destekli olmali.
            self._return_hard = False
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

        # EMNİYET TAVANI — mesafe tabanlı (2026-08-14).
        # Eskiden sadece süreydi (slalom_max_time=20 s). Manevranın mesafe
        # bütçesi ~9.6 m olduğu için tavan HIZA bağlıydı: 4 km/h'de 8.6 s
        # yeterken slalom hızı 2 km/h'ye indirilince manevra tavanı aştı ve
        # weave TIMEOUT ile bitti (14.08 CARLA log'u: slalom tam 20.05 s
        # sürdü = tavanın kendisi). Timeout her fazı "bitti" saydığı için
        # dönüş + hizalanma hiç çalışmadı; araç şeride ortalanmadan
        # LANE_FOLLOW'a döndü ve 1. engelin yanında sola kaymış kaldı.
        # Mesafe tabanlı tavan hızdan bağımsızdır; süre yalnızca odometri
        # beslenmiyorken yedek kalır. Hareketsizlik zaten stall guard'da.
        if self._motion_ok:
            timeout = d_weave > self.slalom_max_distance
        else:
            timeout = t > self.slalom_max_time

        # Heading hatası (şerit yönüne göre, sol pozitif) — pass/align kullanır
        if self._yaw_ok and self.yaw is not None:
            err_deg = math.degrees(
                ((self.yaw - self._weave_yaw_ref + math.pi)
                 % (2 * math.pi)) - math.pi)
            # Lead: tekerlek hedefe varana kadar donmeye devam edecek.
            if self.steer_lead_time > 0.0 and self._yaw_rate is not None:
                err_deg += self.steer_lead_time * self._yaw_rate
        else:
            err_deg = None

        if self.avoid_phase == "escape":
            # TAM KİLİT + YARIM-OFSET GEÇİŞİ (2026-08-03, S-viraj geometrisi):
            # tam kilitle yanal hedefin YARISINA gelince karşı kırmaya geçilir
            # (pass fazı); simetrik S sonunda araç tam ofsete burnu DÜZ varır.
            # Hedefin tamamı beklenirse burun 45-50° açılıyor ve sonraki
            # fazlar açıyı toparlamak için metrelerce yol yiyordu (masa sim).
            # KACIS DIREKSIYONU parametre (17.08.2026, olculdu). Eskiden
            # sabit 75/15 yani TAM KILIT idi. Tam kilitte R=3.07 m ve 0.75 m
            # yanal kazanmak 41 derece bas acisi istiyor; 5.92 m'lik pistte
            # 44 derece donmus arac KORDUR — on koridor sol duvara bakar
            # (olculdu: front=4.34 aslinda duvardi), iki yan sektor de duvarin
            # icine duser, "gidecek acik serit YOK" deyip durur. Sektor
            # geometrisini duzeltmek bunu cozmez; arac fazla donuyordu.
            # 60 -> kilidin ~%50'si -> R~6.65 m -> ayni yanal 25 derecede.
            sap = self.slalom_escape_steer - 45.0
            self.steering_angle = int(round(45 + sap if left else 45 - sap))
            self.signal_status  = 2 if left else 1
            if lat_ok:
                done = lat >= self.slalom_escape_lat_frac * self._weave_lat
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
                # YANAL HEDEFİ TUT (14.08.2026, ölçüldü). Burada eskiden
                # yalnızca AÇI kontrolü vardı; kaçış fazı hedefin YARISINDA
                # bittiği için kalan yarıyı "S'in ikinci yarısı getirir"
                # varsayılıyordu. Getirmiyor: yanal ofset konumdan dürüstçe
                # ölçülünce araç 3.5 m hedefin sadece 2.2'sine çıkıp orada
                # kalıyor — yani tam şerit çizgisinin üstünde. (Önceki
                # koşularda log 3.5 yazıyordu ama o, sürüklenmiş yaw
                # integraliydi.) Şimdi geçiş fazı eksik ofseti de kapatıyor.
                # Açı terimi baskın kalır; yanal terim yalnızca hedefe kadar
                # iter, hedef aşılırsa işaret dönüp geri çeker.
                aci = 45.0 - 1.5 * err_deg
                if lat_ok:
                    eksik = self._weave_lat - lat        # + ise daha çok kaç
                    aci += (self.slalom_pass_lat_gain * eksik
                            * (1.0 if left else -1.0))
                self.steering_angle = int(max(15, min(75, aci)))
            else:
                self.steering_angle = 45
            self.signal_status = 2 if left else 1
            aligned = (err_deg is None
                       or abs(err_deg) <= self.slalom_align_done_deg)
            if self._motion_ok:
                done = aligned and d_phase >= self.slalom_pass_distance
            else:
                done = t_phase >= self.slalom_pass_time

            # IKINCI ENGEL: gectigim seritte engel avoid_distance'a girdiyse
            # donusu KARAR olarak ver, script olarak degil (14.08.2026,
            # operator onerisi). Iki farki var:
            #   1) HIZALANMA BEKLEMEZ. Asagidaki erken donus kurali
            #      `done`a bagli, yani burun serit yonune gelmeden calismaz;
            #      arac hala kirikken engel yaklasirsa devreye giremiyordu.
            #   2) Yonu _pick_avoid_direction'a SORAR. Scripted "return"
            #      donulecek seride bakmadan doner; donulecek serit de
            #      kapaliysa dogru davranis donmek degil DURMAKTIR.
            # Esik neden avoid_distance (4.5) ve daha genis degil: bu bir
            # SON CARE. Normal durumda slalom_pass_front_min (8 m) once
            # tetiklenir — manevra 3.2+1.2=4.4 m yol istiyor, 4.5 m'de
            # baslamak 0.1 m pay birakir. 4.5 m'ye kadar inildiyse zaten
            # bir sey ters gitmis demektir; o noktada tek dogru soru
            # "gidecek acik serit var mi" sorusudur.
            if (self.avoid_phase == "pass"
                    and self.front_distance < self.avoid_distance
                    and self._front_guvenilir(err_deg)
                    and self._weave_tamamlandi(lat)):
                yon = self._pick_avoid_direction()
                if yon is None:
                    self._explain(
                        f"SLALOM gectigim seritte engel "
                        f"(front={self.front_distance:.1f}) ve gidecek acik "
                        f"serit YOK (sol={self.left_distance:.1f} "
                        f"sag={self.right_distance:.1f}) -> DUR")
                    self._pause_avoidance()
                    return
                self._explain(
                    f"SLALOM gectigim seritte engel "
                    f"(front={self.front_distance:.1f} < "
                    f"{self.avoid_distance:.1f}) -> {yon} seride gec "
                    f"(tam kilit)")
                self._return_hard = True     # kaçış kadar sert dön
                self._phase_next("return")
                return

            if done or timeout:
                # ZİNCİRLEME (2026-08-03): dönmeden önce DÖNÜLECEK şeride bak
                # (kaçış solaysa orijinal şerit SAĞ sektördedir — araç komşu
                # şeritte paralelken o sektör tam eski şeridimizi tarar).
                # Orada yakın engel varsa (arka arkaya slalom engelleri)
                # şeride dönme; paralel geçişe devam et, boşluk açılınca dön.
                # HOME ARTIK PROFILDEN (17.08.2026). Eskiden sabit yan
                # sektor okunuyordu (side_offset=2.74); arac kaymisken o
                # sektor kendi seridimizi degil onun otesindeki BARIYERI
                # tariyor ve hep 0 veriyordu -> "serit acildi" kapisi hic
                # acilmiyor, arac karsi seritte 14 m oyalanip son anda tam
                # kilitle kirip bariyere giriyordu. Kendi seridimiz su an
                # -_lateral yanimizda; profil oraya dogrudan bakabiliyor.
                home_p = self._klerans(-lat if left else lat)
                home = (home_p if home_p is not None
                        else (self.right_distance if left else self.left_distance))
                # KAPI KİLİTLENEBİLİYOR (14.08.2026): araç komşu şeritte
                # paralel giderken kendi şeridini tarayan sektör (2..4 m sağ)
                # engelin YANINDAYKEN engeli görür — bu normaldir ve engel
                # arka tamponu geçince home 99'a çıkıp kapı açılır (aynı gün
                # ölçüldü: "SERIT ACILDI (sag=99 >= 12)").
                #   AMA yol kenarında sürekli bir yapı varsa (bariyer, duvar,
                #   korkuluk) o da aynı sektöre girer ve kapı HİÇ açılmaz:
                #   test için eklenen sağ duvarla araç 45 s / 25 m boyunca
                #   "pass" fazında kaldı, weave ancak emniyet tavanıyla bitti
                #   ve o süre boyunca şerit karışımı 0 olduğu için şerit
                #   takibi de yoktu. Gerçek pist iki taraftan bariyerli, yani
                #   bu durum sahada BEKLENEN durumdur.
                # Bu yüzden mesafe tavanı bir yedek olarak duruyor: o kadar
                # yol gidildiyse engel çoktan geride kalmıştır; dönüşün kendi
                # yakın-engel koruması (avoid_abort_distance) devrede kalır.
                # GECTIGIM SERIDIN ONU KAPANIYORSA ERKEN DON (14.08.2026).
                # Olculdu: karsi seritte paralel giderken front 27 -> 6.06 m'ye
                # indi (karsi seritteki 2. engel, araca gore y=-0.1 m yani tam
                # on koridorda) ama hicbir sey olmadi; donus yine 12 m mesafe
                # tavaniyla basladi. Yani "gectigim seridin onu dolu" bilgisi
                # elde VARDI ve kullanilmiyordu.
                #   Not: dosya basindaki "front'a bakarak faz BITIRILMEZ"
                #   kurali front ACIK gorununce erken bitirmeye karsi; burada
                #   ters yon var — front DOLU oldugu icin erken donuyoruz, bu
                #   fail-safe tarafta. Yine de fazin ilk metresinde bakilmaz:
                #   kacistan yeni cikarken on sektor gecilmekte olan engelin
                #   kenarini yalayabilir.
                on_kapaniyor = (d_phase >= self.slalom_pass_front_grace
                                and self.front_distance
                                < self.slalom_pass_front_min
                                and self._front_guvenilir(err_deg))
                pass_bitti = d_phase >= self.slalom_pass_max_distance
                # Donusu DORT sey tetikleyebiliyor. Hangisi oldugu log'dan
                # okunamiyordu (mesaj sadece ikisinde basiliyordu) ve 14.08
                # kosusunda "erken donus kurali mi calisti, mesafe tavani mi"
                # sorusu veriyle cevaplanamadi. Artik gecis HER ZAMAN sebebini
                # yazar — sirala oncelikli, ilk gecerli olan raporlanir.
                if timeout:
                    tetik = f"EMNIYET TAVANI ({d_weave:.0f} m)"
                elif on_kapaniyor:
                    tetik = (f"ON KAPANIYOR (front={self.front_distance:.1f} "
                             f"< {self.slalom_pass_front_min:.0f})")
                elif (self.return_home_when_free
                        and home >= self.slalom_return_free):
                    tetik = (f"SERIT ACILDI ({'sag' if left else 'sol'}="
                             f"{home:.0f} >= {self.slalom_return_free:.0f})")
                elif pass_bitti:
                    tetik = (f"GECIS TAVANI ({d_phase:.0f} m, "
                             f"{'sag' if left else 'sol'}={home:.0f} m hic "
                             f"acilmadi)")
                else:
                    tetik = None
                if tetik is not None:
                    self._explain(f"SLALOM serite donuluyor -> {tetik}")
                    self._phase_next("return")
                elif done:
                    # Kapı kapalıyken SESSİZ beklenmemeli: 14.08 log'unda
                    # araç bu fazda 14 s boyunca hiçbir açıklama basmadan
                    # bekledi (eski koşul d_phase'i 0.2 m'lik bir pencereye
                    # sıkıştırıyordu, mesaj bir kez bile çıkmadı) ve neden
                    # dönmediği log'dan anlaşılamadı. Mesafe metreye
                    # yuvarlanır ki her tick'te tekrar basılmasın.
                    # Yanal ofset de yazilir: "donulecek serit" sektoru arac
                    # SERIT DEGISTIRMISSE kendi seridimizi tarar, YARIM
                    # kalmissa yol kenarini tarar ve hep dolu okur. Hangisi
                    # oldugunu ancak gercek ofset soyler.
                    yanal = (f"{lat:.1f}/{self._weave_lat:.1f} m"
                             if lat_ok else "olculemiyor")
                    # front DA yazilir: gectigimiz seridin onunde bir sey
                    # yaklasiyorsa (karsi seritteki 2. engel) bu satirdan
                    # gorulsun — yoksa soruyu cevaplamak icin /master'i ayrica
                    # dinlemek gerekiyordu.
                    # Mesaj politikaya gore degisir: refleks kapaliyken
                    # "donulecek serit dolu" demek yaniltici olurdu, cunku
                    # o serit bos olsa da donmuyoruz.
                    if self.return_home_when_free:
                        nicin = (f"donulecek serit dolu "
                                 f"({'sag' if left else 'sol'}={home:.0f} m < "
                                 f"{self.slalom_return_free:.0f})")
                    else:
                        nicin = (f"seritte kalmaya devam "
                                 f"({'sag' if left else 'sol'}={home:.0f} m, "
                                 f"donus icin front<"
                                 f"{self.slalom_pass_front_min:.1f} bekleniyor)")
                    self._explain(
                        f"SLALOM gecis suruyor: {nicin} | front="
                        f"{self.front_distance:.1f} - {d_weave:.0f}/"
                        f"{self.slalom_max_distance:.0f} m, yanal {yanal}")

        elif self.avoid_phase == "return":
            # Şeride dönüş S'inin ilk yarısı: ofsetin yarısı inilince align
            # karşı kırmayla tamamlar (escape/pass simetriği).
            # DÖNÜŞ İKİ SERTLİKTE (14.08.2026, operatörün tespiti):
            # "1. engel 4.5 m'de manevra yapıyor, 2. engelde niye yapmasın?"
            # Doğru soru. Aradaki fark mesafe bütçesi DEĞİL, direksiyon
            # yetkisi: kaçış 75/15 (45'ten ±30, tam kilit), dönüş 25/65
            # (±20, %67). İlk engel 4.5 m'de temiz geçiyor çünkü tam kilitle
            # kaçıyor; aynı eşikte yumuşak dönüş yetişmiyordu.
            # Engel tetiklediyse dönüş de kaçış kadar sert olur -> 4.5 m
            # eşiği ikisinde de aynı anlama gelir. Rutin dönüş (şerit açıldı,
            # geçiş tavanı) yumuşak kalır: orada acele yok, sert kırmak
            # aracı gereksiz savurur.
            # DONUS KACISIN AYNASI OLMALI (17.08.2026, CARLA'da olculdu).
            # Kacis sapmasi 30 (FSM 75), donus sapmasi ise 20 (FSM 25) idi —
            # asimetrik. Sonucu: kacis 2.6 m'de biterken donus 3.5 m istiyor
            # ve pratikte cok daha kotu cikti: 12 saniye / 8.6 m boyunca
            # donuldu, yanal 1.4'ten ancak 0.78'e indi. Arac o sure boyunca
            # burnu saga donuk kaldigi icin on koridor sag bariyeri tarayip
            # "cok yakin engel" deyip durdu. Simetrik S icin donus sapmasi
            # kacisla ayni olmali; _return_hard artik ek bir sey degil, ayni
            # deger (zaten tam kilitti).
            # DONUS SERTLIGI ARTIK PARAMETRE (20.08.2026). 17.08'de donus
            # "kacisin aynasi" olarak SABITLENMISTI ve gerekcesi CARLA
            # olcumuydu; o simulatorde direksiyon ANINDA hedefe variyordu.
            # Gercek arac 10 birim/s doner ve 08-20 kayitlarinda (1212/1216)
            # sabit tam-ters-kilit donus burnu -59..-72 dereceye savurdu.
            # slalom_return_steer=None -> ayna (eski davranis, varsayilan),
            # sayi verilirse dogrudan o FSM acisi kullanilir (ornek 25 = daha
            # yumusak sag donus). _return_hard hala aynayi zorlar.
            if self.slalom_return_steer is None or self._return_hard:
                sap = self.slalom_escape_steer - 45.0
            else:
                sap = 45.0 - float(self.slalom_return_steer)
            self.steering_angle = int(round(45 - sap if left else 45 + sap))
            self.signal_status  = 1 if left else 2
            # BURUN DUZELINCE DONUS BITER (19.08.2026, aracta olculdu —
            # slalom_0819_1318). Cikis testi SADECE yanal ofsete bakiyordu ve
            # bas acisini yok sayiyordu. Olculen sonuc:
            #   t=182  yanal +2.24  yaw  +3    burun DUZ, faz devam etti
            #   t=188  yanal +1.31  yaw -33    hala saga kiriyor
            #   t=190  yanal +0.51  yaw -46    yeni kacis acildi
            #   t=202  yanal -3.29             baslangicin 3.3 m SAGINDA
            # Arac karsi seride gecerken 33-46 derece saga donup kendi
            # seridini de asti ve durak alanina girdi (operator fotografi).
            # Sebep: donus fazi S'in IKINCI YARISIDIR, isi bas acisini
            # sifirlamaktir. Yanal esigi (0.5*hedef) o anda hala asilmamis
            # olabiliyor — ozellikle kacis buyuk bir aciyla bittiyse, cunku
            # o aci donus boyunca yanali BUYUTMEYE devam ediyor (t=176'da
            # 1.24 -> t=182'de 2.24). Yani yanal esigi beklemek, aracin
            # gereginden cok donmesini garanti ediyordu.
            # Artik iki sarttan HANGISI once gerceklesirse faz biter; kalan
            # yanali align fazi yumusakca kapatir (zaten onun isi).
            # ACI TAVANI (19.08.2026, aractan olculdu — slalom_0819_1318).
            # Cikis testi SADECE yanal ofsete bakiyordu. Donus fazi kucuk bir
            # bas acisiyla basliyor (pass fazi onu zaten sifirlamis) ama yanal
            # hala hedefin ustunde olabiliyor; o zaman faz yanal esigine
            # inene kadar sag kilitte kaliyor ve BU SURE BOYUNCA ters yonde
            # aci biriktiriyor. Olculen:
            #   t=182  yanal +2.24  yaw  +3   donus basladi
            #   t=188  yanal +1.31  yaw -33   hala sag kilitte
            #   t=190  yanal +0.51  yaw -46   yeni kacis acildi
            #   t=202  yanal -3.29            baslangicin 3.3 m SAGINDA
            # Arac kendi seridini asip durak alanina girdi (operator
            # fotografi). Kalan yanali align fazi zaten kapatir — ustelik
            # bunu tam da bu birikmis aciyla yapar, cunku align burnu
            # duzeltirken arac yana kaymaya devam eder. Yani aciyi
            # sinirlamak yanali kapatmayi engellemez, sadece asiriya
            # kacmasini keser.
            aci_tavani = (err_deg is not None
                          and abs(err_deg) >= self.slalom_return_max_deg)
            if lat_ok:
                done = (lat <= max(self.slalom_lateral_done,
                                   0.5 * self._weave_lat)
                        or aci_tavani)
            elif self._motion_ok:
                done = d_phase >= self.slalom_return_distance or aci_tavani
            else:
                done = t_phase >= self.slalom_return_time or aci_tavani
            if done or timeout:
                self._phase_next("align")

        elif self.avoid_phase == "align":
            # HİZALAN (dönüş S'inin ikinci yarısı): burun şerit yönüne
            # kilitlenir; weave ancak hizalanınca biter — front sektörü o anda
            # doğru yöne baktığı için weave-sonu engel kontrolü ve arka arkaya
            # engellerin zincirlenmesi güvenilir olur.
            if err_deg is not None:
                # YANAL TERİM ŞART (14.08.2026, ölçüldü). Eskiden burada
                # sadece AÇI kontrolü vardı: 45 - 1.5*err_deg. Burun şerit
                # yönüne gelir gelmez direksiyon 45 oluyor ve araç yanal
                # hatası ne olursa olsun DÜMDÜZ gidiyordu — hatayı kapatacak
                # hiçbir terim yok. abs() düzeltmesiyle bitiş testi artık
                # doğru şekilde "olmadı" diyor, ama araç ofseti kapatamadığı
                # için weave 30 m emniyet tavanına çarpıp yine kaymış
                # bitiyordu (CARLA: "bitis yanal ofset 2.57 m").
                # _lateral > 0 = şeridin SOLUNDA -> sağa kır (açı < 45).
                # Açı terimi baskın kalır (Stanley benzeri kaskad): yanal
                # terim burnu çevirir, açı terimi savrulmayı toparlar.
                aci = 45.0 - 1.5 * err_deg
                if lat_ok:
                    aci -= self.slalom_align_lat_gain * self._lateral
                self.steering_angle = int(max(15, min(75, aci)))
                # SINYAL KOMUTU TAKIP ETMELI (20.08.2026, iki slalom
                # kaydinda bulundu — arkadasin gozlemi).
                # align fazi signal_status'u HIC yazmiyordu; donus fazinin
                # biraktigi deger (sola kacistan sonra "SAG") oldugu gibi
                # kaliyordu. Olculdu: 1212 t=138-144 ve 1216 t=68-90 boyunca
                # sinyal SAG yanarken FSM direksiyonu 70 (yani SOLA) idi.
                # Disaridan bakan (hakem, diger surucu) ters bilgi aliyor.
                # Olu bant: 45'e 5 birimden yakinken sinyal sondurulur,
                # yoksa kucuk duzeltmelerde sinyal titrer.
                if self.steering_angle > 50:
                    self.signal_status = 2      # sola kiriyoruz
                elif self.steering_angle < 40:
                    self.signal_status = 1      # saga kiriyoruz
                else:
                    self.signal_status = 0      # duze yakin -> sinyal yok
                done = abs(err_deg) <= self.slalom_align_done_deg
                # ŞERİDE ORTALAN (2026-08-14): burun düz olması yetmiyor.
                # "return" fazı ofsetin YARISINDA bitiyor (lat <= 0.5*
                # _weave_lat, yani ~1.5 m) ve kalan mesafeyi kapatmak
                # align'ın işi; ama eskiden align yalnızca AÇIYA bakıyordu,
                # burun düzelir düzelmez weave bitiyordu. Sonuç: araç kendi
                # şeridinin ~1.5 m solunda "hizalandım" deyip çıkıyor,
                # sonraki engel de bu yüzden ön koridora giriyordu.
                if lat_ok:
                    # MUTLAK DEGER SART (14.08.2026, olculdu). lat ISARETLI:
                    # kacis solaysa donuste _lateral 3.5 -> 0 -> EKSIYE iner.
                    # Isaretli test (lat <= 0.6) araci seridin obur tarafina
                    # 2 m gecmisken de "hizalandim" saydiriyordu — CARLA
                    # zincir kosusu tam bunu yazdi: "bitis yanal ofset 2.07 m".
                    # Sonucu: bir sonraki engel hem front hem yan sektore
                    # giriyor, "iki taraf da kapali" deyip duruyordu.
                    done = done and abs(lat) <= self.slalom_align_lateral
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
        self.slalom_total += 1

        # ILERLEME SAYACI SIFIRLAR (17.08.2026, pist olculeriyle bulundu).
        # slalom_max_weaves aracin YERINDE direksiyon sallamasini kesmek icin
        # var (20.07 kaydi: 0 km/h'de 18-24 s'lik weave'ler). Ama yarisma
        # pistinde engeller 5-8 m arayla dizilir; her weave bittiginde bir
        # SONRAKI engel zaten slow_distance (6.0 m) icindedir, dolayisiyla
        # _end_avoidance cagrilmaz ve sayac birikir. 3. engelde arac basarili
        # bir slalom ortasindayken "gecemiyorum" deyip DURURDU.
        #
        # Ayirt edici olcut weave SAYISI degil, o weave'de YOL ALINIP
        # alinmadigidir: yerinde sallanan arac mesafe kat etmez, pisti
        # geçen arac her weave'de bir engel araligi kadar ilerler.
        d_weave = self.odom_distance - self._avoid_mark
        if self._motion_ok and d_weave >= self.slalom_progress_distance:
            self.slalom_count = 0

        # ESIK slow_distance DEGIL avoid_distance (17.08.2026, olculdu).
        # Weave bitince "yol acik mi" testi slow_distance (6.0) idi; 5 m
        # arayla dizilmis slalomda bir sonraki engel weave biter bitmez
        # hep 6 m'nin ICINDE oldugu icin arac serit takibine HIC donemiyor,
        # oracikta yeni bir weave acmak zorunda kaliyordu. O anda yan
        # sektorler bir sonraki engeli ve sag bariyeri gorup "iki taraf da
        # kapali" diyerek durduruyordu — oysa arac kendi seridine donmustu
        # ve onundeki engel henuz 5-6 m otedeydi.
        # avoid_distance (4.5) dogru esik: "simdi kacinmam gereken bir sey
        # var mi". Yoksa serit takibine don; yaklasinca normal tetik zaten
        # yeni weave'i baslatir. Aradaki 4.5-6.0 bandinda arac yavaslar.
        # BURUN ACIKKEN "engel devam ediyor" KARARI VERME (20.08.2026).
        # Weave bitiminde ON okumasi, burun serit yonunden sapmisken dar
        # pistte YAN BARIYERI tarar. Masa siminde olculdu: tek engelli S1'de
        # engel coktan geride kalmisken front=5.1 okundu ve arac ORTADA
        # ENGEL YOKKEN ikinci bir weave acti, sonra seride hic donemedi.
        # Ayni guard weave ICI yeniden planlamada zaten vardi
        # (_front_guvenilir / front_trust_deg), burada eksikti.
        # Burun acikken karar ERTELENIR: yol acikmis gibi serit takibine
        # donulur, engel gercekten varsa normal tetik (avoid_confirm_time
        # onayiyla) birazdan yeni weave'i zaten baslatir.
        err_deg = None
        if self._yaw_ok and self.yaw is not None:
            err_deg = math.degrees(
                ((self.yaw - self._weave_yaw_ref + math.pi)
                 % (2 * math.pi)) - math.pi)
        if (self.front_distance > self.avoid_distance
                or not self._front_guvenilir(err_deg)):
            # Bitisteki YANAL OFSET: weave seride ortalanarak mi bitti, yoksa
            # kaymis mi? Kayarsa bir sonraki engel hem front hem yan sektore
            # girer ve "iki taraf da kapali" yanilgisi dogar (14.08 zincir
            # kosusunda 3. engelin tetiginde sol=6.3 okundu; solda engel yok,
            # okunan sey ego seridindeki engelin ta kendisiydi).
            kalan = (f", bitis yanal ofset {abs(self._lateral):.2f} m"
                     if (self._yaw_ok and self._motion_ok) else "")
            self._explain(
                f"SLALOM bitti ({self.slalom_total}. weave tamamlandi, "
                f"yol acik){kalan} -> serit")
            self._end_avoidance()
            return
        if self.slalom_count >= self.slalom_max_weaves:
            # Weave tavanı doldu, engel hâlâ önde -> slalom çözmüyor.
            self._explain(
                f"SLALOM {self.slalom_count} weave denendi, engel gecilemedi "
                f"(front={self.front_distance:.1f}) -> OBSTACLE_STOP")
            self._abort_avoidance()
            return
        # FIX (2026-07-21): eskiden yön körlemesine ters çevriliyordu
        # (`right if left else left`) — lidar'a hiç sorulmuyordu. Artık
        # hangi tarafın gerçekten açık olduğu yeniden değerlendirilir.
        direction = self._pick_avoid_direction()
        if direction is None:
            self._explain(
                f"SLALOM weave #{self.slalom_total} bitti, iki taraf da kapali "
                f"(left={self.left_distance:.1f} right={self.right_distance:.1f}) "
                f"-> OBSTACLE_STOP")
            self._abort_avoidance()
            return
        self._begin_weave(direction)
        self._explain(
            f"SLALOM weave #{self.slalom_total} bitti, engel devam "
            f"(front={self.front_distance:.1f}) -> {direction} yone yeni weave")

    def _pause_avoidance(self):
        """Kaçınmayı güvenli duruşla YARIDA KES (çarpışma koruması).
        avoid_blocked KİLİTLEMEZ: _obstacle_stop_control bekleyip yol/yan
        açılınca yeniden dener — her deneme tam duruştan başladığı için
        güvenlidir."""
        self.avoid_direction = None
        self.avoid_phase     = None
        self.slalom_count    = 0
        self.slalom_total    = 0
        self.lane_index      = self._lane_home   # manevra yarıda kaldı ->
        self.steering_angle  = 45                # kendi şeridimizi varsay
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
        self.slalom_total    = 0
        self.lane_index      = self._lane_home   # weave kendi şeridinde biter
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
                # SERT DÖNÜŞ = kaçış (14.08.2026): engel tetiklediyse dönüş
                # bir manevradır, rutin şeride yerleşme değil. Karışım 0.55
                # kalırsa FSM'in tam kilidi tekerlekte tam kilit OLMAZ —
                # ölçüldü: FSM 25 derken yayınlanan 37 (0.45x25 + 0.55x46),
                # sert 15 de ancak 32 olurdu, yani 5 birim fark. Kaçış fazı
                # zaten 0.15 kullanıyor; simetri için sert dönüş de öyle.
                if self._return_hard:
                    return self.avoid_lane_blend_escape
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
            "lane_index":       int(self.lane_index),
        }
