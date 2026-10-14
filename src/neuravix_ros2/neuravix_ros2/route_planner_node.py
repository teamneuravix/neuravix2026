#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROUTE PLANNER / MISSION NODE  (Neuravix — kavsak-karar modeli)
==============================================================
Kurulacagi yer: carla-ros2-ws/src/neuravix_ros2/neuravix_ros2/route_planner_node.py

MIMARI: Arkadasin YENI decision_brain'i icrayi (dönüs/park/durak/sakinma) ve
HOOK'lari yapmis:  request_passenger_stop(), request_park(), turn tetikleri.
Bu node MISSION/ROTA katmanidir: GEOJSON oku -> GPS->map -> graf üstünde A* ->
DOGRU ANDA arkadasin hook'larini /master üzerinden cagirir.

/master ID_PLANNER(5) komut sözlesmesi (control node bunlari brain'e yönlendirir):
    "5,1,<isaretli_derece>"   TURN   (+ sol / - sag; brain heading-gated döner)
    "5,2,0"                   PASSENGER  -> BUS_STOP
    "5,3,0"                   PARK       -> PARK_SEARCH
    "5,0,0"                   RESUME/abort (serit takibe dön)

⚠️ UC ALAN ZORUNLU. neuravix_control_node_real.py master_cb'si ID_PLANNER icin
   len(data) < 3 olan mesaji "Planner mesaji eksik" diye ATIYOR. Iki alanli
   "5,2" gonderirsek beyne HIC ulasmaz. Bu yuzden dolgu sifir konuyor.
Brain yamasi: route_planner_BRAIN_PATCH.md

⚠️ pose_topic MAP-cerceveli olmali: /amcl_pose (AMCL + GNSS gozetmeni). Graf map'te.
   yer_tanima ARTIK KULLANILMIYOR -- capraz oturum dogrulugu olculdu ve kotu cikti
   (22 tohumlamanin medyan hatasi 6.8 m). Bkz. ~/Desktop/maps/OKU.md.
"""
import json, math, os
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseWithCovarianceStamped

R_EARTH = 6378137.0
ID_PLANNER = 5


def yaw_from_quat(q):
    return math.atan2(2.0*(q.w*q.z+q.x*q.y), 1.0-2.0*(q.y*q.y+q.z*q.z))

def norm(a):
    return (a + math.pi) % (2*math.pi) - math.pi


class RoutePlanner(Node):
    def __init__(self):
        super().__init__("route_planner")
        gp = lambda n, v: self.declare_parameter(n, v).value
        # Varsayilan yollar BU DOSYANIN yaninda aranir; boylece paket baska bir
        # makineye kopyalandiginda da argumansiz calisir. Yarisma gunu geojson'u
        # yine de -p geojson:=... ile verilmeli (bkz. README_HANDOFF.md).
        # VERI YOLU (20.08.2026 entegrasyonda degistirildi). Orijinali
        # dosyanin YANINDA ariyordu; `colcon build --symlink-install` ile
        # kurulu modul src'ye SEMBOLIK BAG oldugu icin __file__ install
        # dizinini gosterir ve veri dosyalari orada bulunmaz. Artik once
        # paketin share/data dizinine bakilir (setup.py oraya kuruyor),
        # bulunamazsa eski "dosyanin yani" davranisina duser.
        try:
            from ament_index_python.packages import get_package_share_directory
            _pay = os.path.join(get_package_share_directory("neuravix_ros2"), "data")
        except Exception:
            _pay = None
        _yan = os.path.dirname(os.path.abspath(__file__))

        def _y(ad):
            if _pay:
                c = os.path.join(_pay, ad)
                if os.path.exists(c):
                    return c
            return os.path.join(_yan, ad)
        # ⚠️ VARSAYILAN GEOJSON = YARIS GUNUNUN DOSYASI (24.08.2026).
        # Eskiden teknik_kontrol.geojson idi ve "-p geojson:=" unutulursa
        # arac SESSIZCE BASKA BIR GOREVI kosuyordu. Yine de dosya adi
        # kombinasyona ozeldir: baska bir kombinasyon gelirse -p ile verilmeli.
        # Bu yuzden asagida yuklenen dosyanin TAM YOLU log'a basiliyor --
        # kalkista o satiri okumadan gaz verme.
        # 3. GUN (26.08.2026): dort kombinasyonun DORDU DE pakete kondu
        # (src/neuravix_ros2/data/). Araca dosya kopyalamak gerekmiyor;
        # kombinasyon degisirse SADECE ADI yeter:
        #     -p geojson:=kombinasyon_001.geojson
        # Cikplak ad verilirse asagida _y() ile paketin data/ dizininde
        # aranir; tam yol verilirse aynen kullanilir.
        self.geojson_p = gp("geojson", "kombinasyon_003.geojson")
        if not os.path.isabs(self.geojson_p) and not os.path.exists(self.geojson_p):
            self.geojson_p = _y(self.geojson_p)
        self.graph_p   = gp("graph",   _y("route_graph_refined.json"))
        self.datum_p   = gp("datum",   _y("datum_yt.npz"))
        pose_topic     = gp("pose_topic", "/amcl_pose")
        master_topic   = gp("master_topic", "/master")
        self.trig      = float(gp("trigger_dist", 6.0))   # lokalizasyon %90=3.26m, 4m riskli
        self.tthr      = math.radians(float(gp("turn_angle_thresh_deg", 40.0)))
        # Bu acinin ustundeki "donus" aslinda CIKMAZA girip geri donmedir
        # (durak cebi / park girisi). TURN olarak yayinlanmaz -- bkz. _build_mission.
        self.dead   = float(gp("dead_end_deg", 150.0))
        # DURAK/PARK KAPISI: passenger/park komutundan sonra siradaki olay
        # (genelde ayni node'daki donus) araç kalkana dek BEKLER.
        #
        # ⚠️ Onceki surum bunu "node'dan resume_dist kadar uzaklas" diye olcuyordu
        # ve HIC TUTMUYORDU: olay tetigi node'a trigger_dist (6 m) kala
        # atesleniyor, kapi ise 2.5 m'de aciliyor -- yani kapi daha kuruldugu anda
        # acikti. Olculdu: arac hic kimildamadan "5,2" ve "5,1,-87" ard arda gitti.
        #
        # Yeni kural, uc sart birden:
        #   (a) en az stop_min_hold_s saniye gecmis olacak,
        #   (b) arac node'a EN YAKIN yaklastigi noktadan resume_dist kadar
        #       UZAKLASMIS olacak (yani gercekten kalkmis),
        #   (c) stop_max_hold_s sert zaman asimi -- kapi hicbir kosulda misyonu
        #       kilitleyemez (durak manevrasi beklenmedik giderse yarisi bitirmek
        #       kilitli kalmaktan iyidir).
        self.resume_dist = float(gp("resume_dist", 2.5))
        self.hold_min = float(gp("stop_min_hold_s", 5.0))
        self.hold_max = float(gp("stop_max_hold_s", 30.0))
        # _route_pos ileri bakma penceresi (rota indeksi adedi)
        self.pencere = int(gp("ilerleme_penceresi", 4))
        # TABELA ILE YENIDEN PLANLAMA (2. gun: girilmez / donus yasak tabelalari
        # rastgele konumlanip rotayi degistirebiliyor)
        self.tabela_aktif = bool(gp("tabela_yeniden_planla", True))
        self.tabela_menzil = float(gp("tabela_menzil_m", 18.0))
        self.tabela_teyit = int(gp("tabela_teyit", 3))
        # olay noktasini rota boyunca bu kadar gectiysek "kacirdik" sayilir
        self.gecis_payi = float(gp("gecis_payi_m", 20.0))
        # TEKNIK KONTROL hedefi (22.08.2026). Eskiden hedefte HIC komut
        # gonderilmiyordu ("barier durdurur"); yani durma tamamen lidara
        # birakilmisti. Sartname: hedefe ulasamamak da, hedefi gecip engele
        # carpmak da basarisizlik. Artik iki kademe gonderiliyor:
        #   trig (6 m) icinde  -> 5,4,1  yaklasma (slalom yasak + hiz tavani)
        #   hedef_dur_m icinde -> 5,4,0  DUR (MISSION_END, cikis yok)
        self.hedef_dur_m = float(gp("hedef_dur_m", 2.0))
        # HEDEFI GECINCE HEMEN DUR (22.08 arac olcumu). "5,4,0" sonrasi durusu
        # yalnizca beynin surunme butcesine + lidar'a birakmak, bariyerin
        # gorunmedigi kosularda araci hedefi 2.4-4.5 m gecmis halde birakti
        # (tk_0822_1418 / _1424). Konumu bilen taraf burasi: hedefe olan
        # mesafe ARTMAYA basladiginda (= en yakin noktadan gecildi) "5,4,2"
        # gonderilir ve arac oldugu yerde durur.
        self.hedef_gecis_pay = float(gp("hedef_gecis_pay_m", 0.5))
        # ---- ROTA PLANI (24.08.2026) ----
        # A* en KISA yolu secer; yaris stratejisi ise "sag seritte kal, sadece
        # sol donuslerle turu at, U donusu yapma" olabilir. Olculdu
        # (kombinasyon_200, gorev_3 haric): serbest A* 249 m'lik OUT-AND-BACK
        # rotayi seciyor (gorev_1'e gidip ayni yoldan donuyor, 8 geri donus);
        # ara nokta 18,19,20 (grafin uc `viraj` dugumu = pistin uc kosesi)
        # zorlandiginda 178 m'lik SAAT YONU TERSI tur cikiyor, 3 sol donus,
        # SIFIR geri donus.
        # Bicim:  "18,gorev_1,19,20,gorev_2,park_giris"
        #   SAYI  -> yalnizca ROTA dugumu; olay URETMEZ (bkz. _zincirle).
        #   ISIM  -> geojson ozelligi; olayi (passenger/park/goal) aynen uretir.
        # 'start' bastadir, yazilmaz. Bos birakilirsa ESKI davranis: start +
        # gorev_N (sirali) + park_giris/hedef. Listeye yazilmayan gorev noktasi
        # ROTAYA GIRMEZ -- atlamak icin ayri parametreye gerek yok.
        self.rota_plani = [
            (int(t) if t.strip().isdigit() else t.strip())
            for t in str(gp("rota_plani", "")).split(",") if t.strip()]
        # ---- GOREV DUGUMUNU KENARA ALMA ----
        # Gorev noktalari grafta YAPRAK (tek komsulu) ama fiilen yolun
        # USTUNDELER (olculdu: node 47 kenar 29-30'a 2.20 m, node 54 kenar
        # 33-32'ye 0.89 m). Yaprak modelleme, sahada olmayan bir U donusu
        # URETIYOR: rota dugume gidip ayni kenardan geri cikiyor.
        # Bicim: "47:29-30,54:33-32" -> 29-30 kenari silinir, 29-47 ve 47-30
        # eklenir; boylece nokta yolun UZERINDE bir duraga donusur.
        # ⚠️ Grafin dosyasi DEGISMEZ, yalnizca bellekteki kopya. Baska
        # kombinasyonlarin rotalari etkilenmez.
        self.kenara_al = str(gp("kenara_al", ""))
        # ---- DURAK/PARK ICIN AYRI TETIK MESAFESI (24.08.2026) ----
        # trigger_dist tek basina IKI FARKLI isi goruyordu:
        #   DONUS -> manevranin BASLAMASI icin ~R kadar erken tetik gerekir
        #            (R = 3.26 m, yani 3-3.5 m).
        #   DURAK -> aracin dogru YERDE DURMASI gerekir. Sartname: aracin ON UC
        #            NOKTASI noktanin en fazla 1 m onunde/gerisinde olacak.
        # Hesap (kenara_al ile nokta ROTANIN UZERINDE oldugu icin):
        #   yanal ofset L ~ 1.5 m (arac sag seritte, graf cizgisi seridin solunda)
        #   boylamsal = sqrt(D^2 - L^2)
        #   komuttan duruşa kat edilen yol S ~ 1.4 m (2 s hizalama ~1.1 m + fren)
        #   on uc = base_link + front_overhang (0.41 m)
        #   |boylamsal - S - 0.41| <= 1.0  ->  boylamsal 0.8..2.8 m  ->  D 1.7..3.2
        # Orta deger ~2.3 m. ⚠️ ALT SINIR YANAL OFSETTIR: D, aracin noktaya en
        # yakin yaklasmasindan KUCUKSE olay HIC atesLENMEZ.
        # ⚠️ S bir HESAP, olcum degil. Ilk kosudan sonra bag'den olcun:
        # "5,2" komutunun gonderildigi /gnss_pose ile aracin durdugu /gnss_pose
        # arasindaki mesafe = S. Sonra bu parametreyi ona gore duzeltin.
        # 0 = kapali, trigger_dist kullanilir (eski davranis).
        self.durak_mesafe = float(gp("durak_mesafe", 0.0))
        # ---- DONUS ACISI ARACIN GERCEK YONUNDEN (24.08.2026) ----
        # Eskiden aci rotanin GEOMETRISINDEN onceden hesaplaniyordu
        # (e["deg"]) ve aracin komut anindaki gercek yonu HIC kullanilmiyordu.
        # Iki olculmus sorun:
        #  1) tk_0822: donus CIKIS yon hatasi -7.5 ve -14.7 derece; tek basina
        #     -14.7, 8.2 m'de 1.05 m yanal kayma = seridin ucte biri. Arac
        #     viraja egik girerse cikista da egik cikiyor.
        #  2) kombinasyon_200 park donusu: yayinlanan -95.1, aracin FIZIKSEL
        #     olarak yapmasi gereken -80.2 (14.9 derece FAZLA). Sebep: surus
        #     dizisi gorev_noktasi 54'u atiyor, dolayisiyla aci "33'ten
        #     geliyorum" varsayimiyla hesaplaniyor; arac ise 54'ten geliyor.
        # Cozum: planner komutu atesledigi anda self.yaw'i BILIYOR. Aci
        #   deg = norm(<sonraki segmentin yonu> - <aracin o anki yaw'i>)
        # olarak hesaplanir. Boylece hem egik girisi hem de yukaridaki surus
        # sikismasini kendiliginden duzeltir.
        # ⚠️ GUVENLIK: sonuc geometrik degerin +-donus_yaw_pay'i disina
        # cikamaz; yaw bozuksa hata sinirli kalir. Kapatmak: donus_yaw:=false
        self.donus_yaw = bool(gp("donus_yaw", True))
        self.donus_yaw_pay = float(gp("donus_yaw_pay", 30.0))
        # ---- ROTADAN SAPMA SINIRI ----
        # _yay (rota boyu ilerleme) araci rota poligonuna izdusurerek olculur.
        # Arac rotadan TAMAMEN ciktiginda izdusum yine bir deger uretir ve
        # ilerleme SAHTE sekilde ilerler. `pist_17tem_2` izinde olculdu:
        # haritalama surusu ust sol koseden sonra ortadaki ic tura sapiyor ve
        # ilerleme, arac pistin ortasindayken (34.9, 43.8) gorev_2 duragini
        # (node 54 = 19.0, 36.6 -- 16 m otede) atesliyordu.
        # Cozum: izdusum bu mesafeden uzaksa ilerleme GUNCELLENMEZ. Olculen
        # normal serit sapmasi en fazla 5.7 m oldugu icin 10 m rahat bir pay.
        self.rota_sapma_max = float(gp("rota_sapma_max", 10.0))
        # ---- PARK'I HEDEF GIBI ELE AL (24.08.2026) ----
        # "5,3" -> beynin PARK_SEARCH/PARKING'i, GERCEK ARACTA HIC KOSMADI ve
        # yarisma park alanina uymuyor (24.08 fotograflari: genis acik apron,
        # boyali cepler, gezici bariyerler):
        #   * PARK_SEARCH _is_blocking_state'de DEGIL -> serit olayi (20 Hz)
        #     park hizini ve direksiyonu her karede eziyor,
        #   * obstacle_event PARK_SEARCH/PARKING'de erken donuyor -> FREN
        #     KARARI YOK, yalnizca hiz tavani var,
        #   * PARKING'e gecis sarti `front<3.0 ve right>3.5`; acik apronda
        #     front 99 okur, yani gecis hic olmaz ve arac alani durmadan gecer,
        #   * `right>3.5` sarti zaten 21.07 oncesi ID-4 anlamina gore yazilmis
        #     (o zaman left/right YANAL bosluktu, artik BOYLAMSAL klerans).
        # Bu parametre acikken park_giris olayi "goal" olarak uretilir, yani
        # teknik kontrolde ARACTA CALISMIS olan iki kademeli durma yolu:
        #   5,4,1 (yaklasma: slalom yasak + hiz tavani)
        #   5,4,0 (MISSION_END: surunerek yaklas, engelde ya da hedef_creep_m
        #          sonunda dur -- ve bir daha kalkma)
        #   5,4,2 (noktanin en yakinindan gecildi -> HEMEN dur)
        # Sonuc: arac park alanina girer, biraz surunur ve durur. Cep secmez.
        self.park_hedef_gibi = bool(gp("park_hedef_gibi", False))
        # ---- START DUGUMU ARACIN ONUNDE OLMALI (25.08.2026) ----
        # _nearest yalnizca MESAFEYE bakiyordu. start_park_005'te olculdu:
        # arac (30.26, 5.61)'de +10 derece (DOGUYA) bakiyor, en yakin dugum
        # node 1 (7.5 m) ama o 170.8 derece ARKADA. Rota [1, 11, 32, 55]
        # cikiyor, yani "once geri git". Arac geri gidemez.
        # Artik start dugumu, aracin yonune gore +-start_on_aci icinde kalan
        # dugumler arasindan secilir (burada node 0, 16.1 m, +4.7 derece).
        # 180 vermek eski davranisa doner.
        self.start_on_aci = float(gp("start_on_aci_deg", 90.0))
        # ---- PARK BOLGESI KAPISI (25.08.2026) ----
        # Beyin "P" tabelasini gordugu ANDA PARK_SEARCH'e geciyordu ve o
        # durumda ENGEL FRENI KAPALI (obstacle_event erken donuyor), ustelik
        # serit olayi hizi/direksiyonu her karede eziyor. 2. gunde tabelalar
        # aktif ve rota park alanina gidiyor -- yol kenarinda gorulen bir P
        # tabelasi araci yolun ortasinda park moduna sokabilirdi.
        # Artik izin KONUMA bagli: arac park noktasina park_bolge_m'den
        # yakinsa planner bir kez "5,3,1" gonderir ve beyin P tabelasini
        # ancak ondan SONRA kabul eder (o da park_sign_distance = 8 m icinde).
        # 12.0: park yoluna donulen kavsak (node 32) park noktasina 10.8 m,
        # yani izin arac park yoluna GIRERKEN cikiyor. 25 m denendi ve cok
        # erkendi -- arac daha ana yoldayken (node 11) izin veriyordu.
        self.park_bolge_m = float(gp("park_bolge_m", 12.0))
        # ---- TUNEL (25.08.2026) ----
        # Tunel icinde serit tespiti karanlikta guvenilmez; istenen davranis
        # "seridi ortala, 45 derece DUZ cik". Tabelaya guvenmek yerine KONUM
        # kullanilir: grafta iki `tunel_giris` dugumu arasindaki kenar tunelin
        # kendisidir (21-22, 14.2 m). Arac o kenarin uzerindeyken beyne
        # "5,5,1" gider, ciktiginda "5,5,0".
        self.tunel_yari_en = float(gp("tunel_yari_en_m", 5.0))
        # ---- TUNEL ONCELIGI (26.08.2026, operator karari) ----
        # True iken: aracin ONUNDEKI tunel kenarina GIDEN rota kenarlari
        # tabela ile KAPATILAMAZ. Yani "ileri mecburi" gibi bir levha tunel
        # donusunu yasaklasa bile arac tunele girer.
        # GEREKCE (sartname puanlari): tunelden gecmek +200; buna karsilik
        # bir tabela ihlali -50 VE "tum isaretlere uygun hareket" +50 bonusu
        # da kaybedilir -> 100 puanlik takas. Net +100.
        # ⚠️ YALNIZCA TUNELE GIDEN KENARLAR muaf tutulur. Ayni tabelanin
        # kapattigi DIGER cikislar aynen kapanir ve tunel gecildikten sonra
        # muafiyet biter -- yani tabelalar genel olarak YOK SAYILMAZ.
        self.tunel_oncelik = bool(gp("tunel_oncelik", False))
        # ---- SON GOREV: burada DUR VE KAL (26.08.2026) ----
        # Adi verilen gorev noktasinin durak beklemesi bittikten sonra beyne
        # "5,4,0" gonderilir -> MISSION_END (terminal, cikis yok). Amac
        # puani bankaya yazip kalan riski almamak.
        # ⚠️ Yaninda `hedef_creep_m:=0.0` verilmeli, yoksa MISSION_END
        # durmadan once sürünerek ilerler ve araci duraktan cikarir.
        # Bos string = kapali (varsayilan davranis: gorevlere devam).
        self.son_gorev = str(gp("son_gorev", "")).strip()
        # Durak komutundan kac saniye sonra DUR gonderilecek. Beynin durak
        # dizilimi: align 2 s + bekle 17 s + cikis 2 s = 21 s. 19 s, aracin
        # 17 saniyelik SABIT beklemesi bittigi an ama CIKIS fazi baslamadan
        # once demek -- boylece sartnamenin 15-20 s duraklama kosulu saglanir
        # ve arac duraktan HIC hareket etmeden MISSION_END'e gecer.
        # (Kapinin kendi kalkis/zaman asimi mantigini beklemek 2.5 m'lik bir
        # ilerleme demekti; olculdu.)
        self.son_gorev_bekle = float(gp("son_gorev_bekle", 19.0))
        self._son_gorev_dur_gonderildi = False
        # ---- ROTADAN CIKINCA OTOMATIK YENIDEN PLANLAMA ----
        # rota_sapma_max ilerlemeyi donduruyordu ama GERI DONUS yolu yoktu:
        # arac (tabela, engel, surucu, serit hatasi -- sebep ne olursa olsun)
        # rotadan cikarsa ilerleme kalici olarak durur ve ARKADAKI HICBIR OLAY
        # ATESLEMEZ. Artik sapma bu sure boyunca surerse planner aracin
        # ONUNDEKI en yakin dugumden kalan goreve YENI ROTA kurar.
        # Boylece planner'in "her karardan haberdar olmasi" tabela tabela
        # sayilarak degil, SONUCA bakilarak saglanir.
        self.sapma_sure = float(gp("rota_sapma_sure_s", 3.0))
        self.sapma_max_replan = int(gp("rota_sapma_max_replan", 3))

        d = np.load(self.datum_p, allow_pickle=True)
        self.R = np.array(d["R"]); self.t = np.array(d["t"])
        self.la0 = float(d["la0"]); self.lo0 = float(d["lo0"])
        # ⚠️ yasak kumesi _build_mission'dan ONCE kurulmali: A* onu okuyor.
        self.yasak = set()          # tabela ile kapatilan yonlu gecisler (u,v)
        self._tabela_say = {}       # tabela teyit sayaci
        self._tamamlanan = set()    # bitmis mission noktalari
        self._plan_no = 0
        self._load_graph(self.graph_p)
        self._build_mission(self.geojson_p)
        self._yay_kur()

        self.pos = None; self.yaw = None
        self.ev_i = 0          # sradaki olay
        self.done = set()
        self._gate = None           # durak/park kapisi: {"xy","t0","best"}
        self._salindi = None        # kapi yeni acildi -> SONRAKI olay geciktirilmisti;
                                    # ne atlanir ne de yaklasma testine takilir
        self._ilerleme = 0          # rota ilerleme indeksi (bkz. _route_pos)
        self._park_izni_gonderildi = False   # "5,3,1" bir kez gider
        self._tunelde = False                # "5,5,1/0" kenar tetikli
        self._sapma_t0 = None                # sapmanin basladigi an
        self._rotaya_girdi = False           # arac rotaya BIR KEZ oturdu mu
        self._oto_replan = 0                 # kac kez otomatik yeniden planlandi
        self._rota_sapma = 0.0      # aracin rotaya dik uzakligi [m]
        self._sapma_uyardi = False
        self._yay = 0.0             # rota uzerinde kat edilen yol [m]
        self._hedef_yaklasma_gonderildi = False   # 5,4,1 bir kez gonderilir
        self._hedef_dur_gonderildi = False        # 5,4,0 gonderildi mi
        self._hedef_min_d = None                  # hedefe gorulen en kucuk mesafe
        self._seg = 0               # su anki rota segmenti
        self.pub = self.create_publisher(String, master_topic, 10)
        self.create_subscription(PoseWithCovarianceStamped, pose_topic, self._pose_cb, 10)
        if self.tabela_aktif:
            self.create_subscription(String, master_topic, self._master_cb, 20)
        self.create_timer(0.1, self._loop)
        self.get_logger().info(f"route_planner hazir. {len(self.events)} olay.")

    # ---------- graf ----------
    def _kenara_al_uygula(self, E):
        """`kenara_al` tarifine gore yaprak gorev dugumlerini kenarin uzerine
        tasir. Bkz. __init__'teki uzun not."""
        if not self.kenara_al.strip():
            return E
        kenar = {tuple(sorted(e)) for e in map(tuple, E)}
        for parca in self.kenara_al.split(","):
            parca = parca.strip()
            if not parca:
                continue
            try:
                L, ab = parca.split(":")
                a, b = ab.split("-")
                L, a, b = int(L), int(a), int(b)
            except ValueError:
                self.get_logger().error(f"kenara_al bicimi hatali: '{parca}' "
                                        "(beklenen 'L:a-b') -- ATLANDI")
                continue
            if max(L, a, b) >= len(self.N):
                self.get_logger().error(f"kenara_al: {parca} icinde gecersiz "
                                        "node id -- ATLANDI")
                continue
            if tuple(sorted((a, b))) not in kenar:
                self.get_logger().error(f"kenara_al: {a}-{b} kenari grafta YOK "
                                        "-- ATLANDI")
                continue
            E = [e for e in E if tuple(sorted(map(int, e))) != tuple(sorted((a, b)))]
            E = E + [[a, L], [L, b]]
            kenar.discard(tuple(sorted((a, b))))
            kenar.update({tuple(sorted((a, L))), tuple(sorted((L, b)))})
            self.get_logger().info(
                f"kenara_al: node {L} artik {a}-{b} kenarinin UZERINDE "
                "(yaprak degil) -- U donusu gerekmiyor")
        return E

    def _load_graph(self, path):
        g = json.load(open(path)); self.N = g["nodes"]
        E = self._kenara_al_uygula(g["edges"])
        # "gorev_noktasi" = yarismanin kendi yolcu/park/hedef noktalari, 2026-08-20'de
        # grafa eklendi. Bunlar YAPRAK (tek kenarli), yani A* onlarin USTUNDEN
        # gecemez -- sadece hedef olabilirler. road listesine girmeleri gerekiyor
        # cunku rota hedefleri yalnizca buradan seciliyor.
        #
        # NEDEN EKLENDILER: yarisma noktalari kavsak node'larina medyan 5.1 m
        # (%90 8.9 m) uzaktaydi ve 233 kombinasyonun 40'inda IKI yolcu noktasi
        # ayni kavsak node'una dusuyordu. wp_index o indeksi ezdigi icin bir
        # yolcu alma olayi SESSIZCE kayboluyordu (olculdu: 1. gunun 224
        # kombinasyonunun 40'inda 3 yerine 2 yolcu olayi uretiliyordu).
        self.road = [i for i, n in enumerate(self.N)
                     if n["type"] in ("kavsak", "viraj", "roundabout", "tunel_giris",
                                      "gorev_noktasi")]
        # TUNEL kenarlari: iki ucu da `tunel_giris` olan kenarlar
        self.tunel_kenar = [(a, b) for a, b in E
                            if self.N[a]["type"] == "tunel_giris"
                            and self.N[b]["type"] == "tunel_giris"]
        self.adj = {i: [] for i in range(len(self.N))}
        for a, b in E:
            w = math.hypot(self.N[a]["map_x"]-self.N[b]["map_x"], self.N[a]["map_y"]-self.N[b]["map_y"])
            self.adj[a].append((b, w)); self.adj[b].append((a, w))

    def gps2map(self, la, lo):
        e = math.radians(lo-self.lo0)*R_EARTH*math.cos(math.radians(self.la0))
        n = math.radians(la-self.la0)*R_EARTH
        return (np.array([e, n]) - self.t) @ self.R.T

    def _nearest(self, p, cands=None):
        cands = self.road if cands is None else cands
        return min(cands, key=lambda i: (self.N[i]["map_x"]-p[0])**2 + (self.N[i]["map_y"]-p[1])**2)

    def _start_dugum(self, p):
        """Start dugumu = EN YAKIN degil, ARACIN ONUNDEKI en yakin.
        Gerekce ve olcum __init__'teki start_on_aci notunda."""
        if self._start_hdg is None or self.start_on_aci >= 180.0:
            return self._nearest(p, self.road)
        lim = math.radians(self.start_on_aci)
        on = []
        for i in self.road:
            d = np.array([self.N[i]["map_x"], self.N[i]["map_y"]]) - np.asarray(p)
            r = float(np.linalg.norm(d))
            if r < 1e-6:
                return i
            if abs(norm(math.atan2(d[1], d[0]) - self._start_hdg)) <= lim:
                on.append((r, i))
        if not on:
            self.get_logger().warn(
                f"start yonunun +-{self.start_on_aci:.0f} derecesinde dugum YOK "
                "-> en yakina donuluyor (arac geri gitmek zorunda kalabilir)")
            return self._nearest(p, self.road)
        r, i = min(on)
        self.get_logger().info(
            f"start dugumu: node {i} ({r:.1f} m, aracin ONUNDE)")
        return i

    def _wp_dugum(self, tok, feats=None):
        """Waypoint belirtecini graf dugumune cevir.
        int  -> dogrudan node id (ara nokta), str -> geojson noktasina en yakin."""
        if isinstance(tok, int):
            return tok
        f = feats if feats is not None else self.feats
        return self._nearest(f[tok], self._reach)

    def _reachable_from(self, s):
        """s'den road grafında ulaşılabilen düğümler (rota hedefi bunlardan seçilir)."""
        seen = {s}; st = [s]
        while st:
            u = st.pop()
            for v, _ in self.adj[u]:
                if v in self.road and v not in seen:
                    seen.add(v); st.append(v)
        return seen

    def _yay_kur(self):
        """Rota poligonunun kumulatif yay uzunlugu."""
        self.S = [0.0]
        for k in range(1, len(self.route)):
            self.S.append(self.S[-1] + self._dist(self.route[k-1], self.route[k]))

    def _route_pos(self):
        """Rota üzerindeki ILERLEME indeksi (kaçırılan olay tespiti için).

        ⚠️ GLOBAL argmin KULLANILAMAZ. Rota görev ceplerine sapıp geri dönüyor,
        yani aynı node rotada birkaç kez geçiyor (ör. kombinasyon_001'de node 28
        indeks 3, 9 ve 11'de). Global argmin, araç indeks 3'teyken 10'u
        döndürüyor ve arkadaki olaylar "kaçırıldı" sanılıp ATILIYORDU --
        ölçüldü (2026-08-20): 1. gün kombinasyon_001'de gorev_1 yolcu alma
        komutu ile iki dönüş komutu bu yüzden hiç gönderilmiyordu.

        Bunun yerine yalnızca ILERI bakan dar bir pencerede ara ve ilerlemeyi
        monoton tut. Lokalizasyon sıçrasa bile ilerleme geri gitmez; en kötü
        ihtimalle atlama mantığı devreye girmez -- güvenli taraf.
        """
        return self._ilerleme

    def _ilerlemeyi_guncelle(self):
        """Rota UZERINDE kat edilen yolu (yay uzunlugu) izler. Her tikte cagrilir.

        ⚠️ "En yakin rota dugumu" ile ilerleme olculemez. Iki sebep:
          1) Rota gorev ceplerine sapip geri donuyor, ayni dugum birkac kez
             geciyor (kombinasyon_001'de dugum 28 indeks 3, 9, 11'de).
          2) Bazi gorev cepleri baska bir kenarin TAM USTUNDE duruyor --
             ornegin dugum 49, 20->33 yolunun uzerinde 5.5 m ileride. Arac
             daha 33'e giderken "49'a vardim" sanilip indeks firliyordu.
        Olculdu (2026-08-20): bu iki etki 233 kombinasyonun 16'sinda ardisik
        iki yolcu alma olayindan birini dusuruyordu.

        Cozum: araci ILERI bakan dar bir segment penceresinde poligona izdusur,
        yay uzunlugunu al, monoton tut. Yay uzunlugu sapmalari da dogru sayar.
        """
        if self.pos is None:
            return
        p = self.pos
        en_iyi = None
        k0 = self._seg
        for k in range(k0, min(len(self.route) - 1, k0 + self.pencere)):
            a = np.array([self.N[self.route[k]]["map_x"], self.N[self.route[k]]["map_y"]])
            b = np.array([self.N[self.route[k+1]]["map_x"], self.N[self.route[k+1]]["map_y"]])
            v = b - a
            L2 = float(v @ v)
            t = 0.0 if L2 < 1e-9 else max(0.0, min(1.0, float((p - a) @ v) / L2))
            q = a + v * t
            d = float(np.linalg.norm(p - q))
            yay = self.S[k] + t * math.sqrt(L2)
            if en_iyi is None or d < en_iyi[0]:
                en_iyi = (d, yay, k)
        if en_iyi is None:
            return
        _, yay, k = en_iyi
        self._rota_sapma = en_iyi[0]
        if en_iyi[0] <= self.rota_sapma_max:
            self._rotaya_girdi = True
        if en_iyi[0] > self.rota_sapma_max:
            # Rotadan cok uzaktayiz: bu izdusum ilerleme SAYILMAZ.
            if not getattr(self, "_sapma_uyardi", False):
                self._sapma_uyardi = True
                self.get_logger().warn(
                    f"rotadan {en_iyi[0]:.1f} m sapildi (> {self.rota_sapma_max:.1f}) "
                    "-- ilerleme donduruldu, olaylar Oklid yedegine dustu")
            return
        self._sapma_uyardi = False
        if yay > self._yay:
            self._yay = yay
            self._seg = k
        # eski API'yi koru: en yakin rota indeksi ~ yay uzunlugundan
        while (self._ilerleme + 1 < len(self.S)
               and self.S[self._ilerleme + 1] <= self._yay):
            self._ilerleme += 1

    def _astar(self, s, g):
        import heapq
        h = lambda i: math.hypot(self.N[i]["map_x"]-self.N[g]["map_x"], self.N[i]["map_y"]-self.N[g]["map_y"])
        oq=[(h(s),0,s)]; came={}; gs={s:0}
        while oq:
            _, gc, u = heapq.heappop(oq)
            if u == g: break
            for v, w in self.adj[u]:
                if (u, v) in self.yasak: continue
                ng = gc+w
                if v not in gs or ng < gs[v]: gs[v]=ng; came[v]=u; heapq.heappush(oq,(ng+h(v),ng,v))
        p=[g]
        while p[-1]!=s:
            if p[-1] not in came: return []
            p.append(came[p[-1]])
        return p[::-1]

    def _hdg(self, a, b):
        return math.atan2(self.N[b]["map_y"]-self.N[a]["map_y"], self.N[b]["map_x"]-self.N[a]["map_x"])

    def _gps_hdg_to_map(self, bearing_deg):
        """GPS pusula bearing (0=kuzey, CW) -> MAP-çerçeve heading (rad)."""
        b = math.radians(bearing_deg)
        v_enu = np.array([math.sin(b), math.cos(b)])   # (doğu, kuzey)
        vm = v_enu @ self.R.T
        return math.atan2(vm[1], vm[0])

    def _dist(self, a, b):
        return math.hypot(self.N[a]["map_x"]-self.N[b]["map_x"], self.N[a]["map_y"]-self.N[b]["map_y"])

    def _astar_turn(self, s, g, in_hdg, turn_w=8.0):
        """DÖNÜŞ-CEZALI A*: state=(node, prev). Maliyet = mesafe + turn_w·|dönüş açısı|.
        in_hdg = araç start heading'i (ilk dönüş ona göre ölçülür). Böylece:
          (1) heading-aware ilk hamle (geri/yan başlama pahalı),
          (2) zigzag yerine tek-temiz-köşe rotasını yeğler.
        Düz A* mesafe-eşitliğinde zigzag seçebiliyordu; bu onu çözer."""
        import heapq
        oq = [(self._dist(s, g), 0.0, s, None)]; seen = {}; came = {}; goalprev = None
        while oq:
            _, gc, u, prev = heapq.heappop(oq)
            if u == g: goalprev = prev; break
            k = (u, prev)
            if k in seen and seen[k] <= gc: continue
            seen[k] = gc
            inh = self._hdg(prev, u) if prev is not None else in_hdg
            for v, w in self.adj[u]:
                if v == prev: continue                      # anında geri dönme yok
                if (u, v) in self.yasak: continue           # tabela ile kapatildi
                turn = abs(norm(self._hdg(u, v) - inh))
                ng = gc + w + turn_w * turn
                nk = (v, u)
                if nk not in seen or ng < seen.get(nk, 1e18):
                    came[nk] = (u, prev); heapq.heappush(oq, (ng + self._dist(v, g), ng, v, u))
        path = [g]; cur = (g, goalprev)
        while cur[1] is not None:
            path.append(cur[1]); cur = came[cur]
        return path[::-1]

    def _olaylari_kur(self, route, giris_hdg=None):
        """Rotadan surus dizisini ve olay listesini uretir."""
        # ⚠️ SON gorev noktasi HARIC. Ara noktalarda arac cebe girip GERI
        # CIKIYOR, o yuzden sapma elenmeli. Ama SON nokta (hedef / park_giris)
        # bir cikis manevrasi icermiyor: oraya giris rotanin gercek son
        # hamlesidir. Elenirse hem o donus komutu kayboluyor hem de rota
        # dogrulamasi yanlis sey karsilastiriyordu (olculdu: teknik kontrolde
        # node 4'teki +90° sol donus dusuyor, dogrulama "gereken +90, planner
        # -0" diye hatali uyari veriyordu).
        surus = []                    # (node, orijinal rota indeksi)
        for k, b in enumerate(route):
            if self.N[b]["type"] == "gorev_noktasi" and k != len(route) - 1:
                continue
            if surus and surus[-1][0] == b:
                surus[-1] = (b, k)    # sapmadan geri dondük: SON indeksi tut,
                continue              # donus sapma bitince tetiklensin
            surus.append((b, k))
        self.surus = surus

        self.events = []
        self.cikmazlar = []
        # ⚠️ ILK DUGUMDEKI DONUS (24.08.2026). Dongu j=1'den basliyordu, yani
        # route[0]'daki donus YAPISAL OLARAK hic olay uretmiyordu: donus olayi
        # "onceki dugum" ister, ilk dugumun oncesi ARACIN KENDISIDIR. Start
        # yonu (_start_hdg) A*'in MALIYETINDE kullaniliyor ama komuta
        # cevrilmiyordu.
        #   Olculdu (kombinasyon_200): start (35.97, 6.62) yon +10 derece,
        #   10.3 m ileride node 0 bir T kavsagi (bati=node 1, dogu=node 4 +10,
        #   kuzey=node 39 +105) ve rota kuzeyi istiyor -> +88 SOL donus.
        #   Komut gitmedigi icin arac duz doguya devam eder, rotadan cikar ve
        #   ARKASINDAKI HICBIR OLAY tetiklenmez: _yay, S[1]+gecis_payi'ni
        #   gecemedigi icin "kacirildi" mantigi da devreye girmez, misyon
        #   sessizce durur. Ilk dugumde 88 derecelik bir donus cikmasi kaza
        #   degil: 0->39 ile 0->4 rotalarinin maliyeti 128.1 / 128.0, yani
        #   A* berabere kalan iki yoldan donuslu olani secebiliyor.
        # giris_hdg = route[0]'a VARIS yonu: ilk planda aracin start heading'i,
        # yeniden planlamada o anki gelis yonu. None ise eski davranis (j=1).
        bas = 0 if (giris_hdg is not None and len(surus) >= 2) else 1
        for j in range(bas, len(surus) - 1):
            b, c = surus[j][0], surus[j+1][0]
            k = surus[j][1]
            xy = (self.N[b]["map_x"], self.N[b]["map_y"])
            if True:
                gelis = giris_hdg if j == 0 else self._hdg(surus[j-1][0], b)
                dth = norm(self._hdg(b, c) - gelis)
                derece = math.degrees(dth)
                if abs(derece) >= self.dead:
                    # CIKMAZ: arac girdigi yerden geri cikiyor (durak cebi, park
                    # girisi). Brain'e "5,1,-180" gondermek yanlis olur -- heading
                    # gated donus 180'i yerinde yapamaz, bu bir manevra isi.
                    # Manevrayi zaten hemen arkasindan gelen passenger/park olayi
                    # tetikliyor. Net donus hesabina dahil kalir (asagi bak).
                    self.cikmazlar.append((b, derece))
                elif abs(dth) >= self.tthr:
                    self.events.append({"kind": "turn", "ri": k, "node": b, "xy": xy,
                                        "deg": derece, "approach": gelis,
                                        "cikis": self._hdg(b, c)})

        # WAYPOINT olaylari ORIJINAL rota uzerinden -- son indeks DAHIL.
        # (Onceki surumde dongu range(1, len(route)-1) idi ve wp_index'in son
        #  anahtari tam olarak len(route)-1 oldugu icin SON mission noktasi hic
        #  olay uretmiyordu: yarisin park komutu "5,3" HIC gonderilmiyordu.)
        for k in range(1, len(route)):
            if k not in self.wp_index:
                continue
            b = route[k]; nm = self.wp_index[k]
            if nm == "park_giris":
                kind = "goal" if self.park_hedef_gibi else "park"
            elif nm.startswith("gorev"):
                kind = "passenger"
            else:
                kind = "goal"
            self.events.append({"kind": kind, "ri": k, "node": b,
                                "xy": (self.N[b]["map_x"], self.N[b]["map_y"]), "name": nm})
        # Aynı ri'de: passenger/park/goal ÖNCE, turn SONRA. Fiziksel sıra: node'a
        # gel -> durakta dur -> kalkarken dön. (Eskiden turn önce ekleniyordu.)
        self.events.sort(key=lambda e: (e["ri"], 0 if e["kind"] in ("passenger", "park", "goal") else 1))
        return self.events

    def _zincirle(self, wp_nodes, adlar, in_hdg):
        """Waypoint dugumlerini segment segment A* ile tam rotaya cevirir.
        KOPUK segment = RuntimeError: kopuk rotayla yola cikmaktansa hic cikma."""
        route = [wp_nodes[0]]
        wp_index = {}
        for k in range(1, len(wp_nodes)):
            if in_hdg is not None:
                seg = self._astar_turn(wp_nodes[k-1], wp_nodes[k], in_hdg)
            else:
                seg = self._astar(wp_nodes[k-1], wp_nodes[k])
            if not seg or seg[0] != wp_nodes[k-1] or seg[-1] != wp_nodes[k]:
                raise RuntimeError(
                    f"ROTA KOPUK: {adlar[k-1]}->{adlar[k]} "
                    f"(node {wp_nodes[k-1]}->{wp_nodes[k]}) yol yok.")
            route += seg[1:]
            if adlar[k] is not None:      # None = yalnizca ROTA dugumu (ara
                wp_index[len(route)-1] = adlar[k]   # nokta), olay uretmez
            if len(seg) >= 2:
                in_hdg = self._hdg(seg[-2], seg[-1])
        return route, wp_index

    # ---------- mission (geojson -> sirali olaylar) ----------
    def _build_mission(self, path):
        self.get_logger().warn(f"GEOJSON DOSYASI: {path}")
        gj = json.load(open(path)); feats = {}; names = []
        for f in gj["features"]:
            nm = f["properties"].get("name", ""); names.append(nm)
            lo, la = f["geometry"]["coordinates"]; feats[nm] = self.gps2map(la, lo)
        self.get_logger().info(f"GEOJSON feature adları: {names}")
        if "start" not in feats:
            raise RuntimeError("GEOJSON'da 'start' YOK — mission kurulamaz.")
        # heading'ler (map çerçevesinde) — ilk hamle + rota doğrulaması için
        self._bearings = {f["properties"].get("name"): f["properties"].get("heading")
                          for f in gj["features"] if f["properties"].get("heading") is not None}
        self._start_hdg = (self._gps_hdg_to_map(self._bearings["start"])
                           if "start" in self._bearings else None)
        # start düğümü (tüm road'dan) + ULAŞILABİLİR küme (rota hedefleri bundan)
        start_node = self._start_dugum(feats["start"])
        self._reach = self._reachable_from(start_node)
        # ⚠️ SIRA ONEMLI: yarisma sartnamesi "1. yolcu alma noktasi ILK, 3. SON
        # olmalidir" diyor. Bu yuzden gorev_N adlari SAYIYA gore siralanir --
        # alfabetik siralama gorev_10'u gorev_2'nin onune atardi.
        ham = [k for k in feats if k.startswith("gorev_")]
        gorev, bozuk = [], []
        for k in ham:
            try:
                gorev.append((int(k.split("_")[1]), k))
            except (IndexError, ValueError):
                bozuk.append(k)
        gorev.sort()
        if bozuk:
            self.get_logger().error(
                f"gorev_N formatina uymayan adlar ATLANDI: {bozuk} -- bunlar rotaya GIRMEDI")
        nolar = [n for n, _ in gorev]
        if nolar and nolar != list(range(1, len(nolar) + 1)):
            self.get_logger().warn(
                f"gorev numaralari 1..N degil: {nolar}. Sirali islenecek ama "
                "bir nokta eksik/yinelenmis olabilir -- GEOJSON'u kontrol et.")
        gorev = [k for _, k in gorev]
        tail  = [k for k in ("park_giris", "hedef") if k in feats]
        if not gorev and not tail:
            self.get_logger().warn(
                f"GEOJSON'da gorev_N / park_giris / hedef YOK (adlar tutmuyor olabilir: {names}). "
                "Sadece 'start' var — rota üretilmeyecek.")
        if self.rota_plani:
            bilinmeyen = [t for t in self.rota_plani
                          if isinstance(t, str) and t not in feats]
            if bilinmeyen:
                raise RuntimeError(
                    f"rota_plani'nda GEOJSON'da olmayan ad(lar): {bilinmeyen}. "
                    f"Mevcut adlar: {sorted(feats)}")
            uzak = [t for t in self.rota_plani
                    if isinstance(t, int) and (t >= len(self.N) or t not in self._reach)]
            if uzak:
                raise RuntimeError(
                    f"rota_plani'ndaki {uzak} node(lar)i gecersiz ya da start'tan "
                    "ULASILAMAZ -- rota kurulamaz.")
            seq = ["start"] + self.rota_plani
            atlanan = [k for k in gorev + tail if k not in seq]
            self.get_logger().warn(
                f"ROTA PLANI verildi: {seq}"
                + (f" | LISTEDE OLMAYAN gorev noktalari ROTAYA GIRMIYOR: {atlanan}"
                   if atlanan else ""))
        else:
            seq = ["start"] + gorev + tail
        self.get_logger().info(f"Mission dizisi: {seq}")
        wp_nodes = [self._wp_dugum(nm, feats) for nm in seq]
        # ⚠️ seq[0] her zaman "start" ve onun dugumu YON DUYARLI secilmisti
        # (_start_dugum). _wp_dugum yeniden en-yakini bulur ve o secimi
        # EZERDI -- start_park_005'te tam bu oluyordu: _start_dugum node 0
        # (onde) diyordu, wp_nodes[0] yine node 1 (arkada) oluyordu.
        wp_nodes[0] = start_node
        for nm, wn in zip(seq, wp_nodes):
            if not isinstance(nm, str):
                continue              # ara nokta: zaten node'un kendisi
            d = math.hypot(self.N[wn]["map_x"]-feats[nm][0], self.N[wn]["map_y"]-feats[nm][1])
            if d > 8.0:
                self.get_logger().warn(f"'{nm}' en yakın ULAŞILABİLİR node'a {d:.1f}m uzak — rota kaba olabilir.")
        # yeniden planlama bunlari kullanacak
        self.seq = seq
        self.feats = feats
        self._park_xy = feats.get("park_giris")   # park bolgesi kapisi icin
        if self._start_hdg is not None:
            self.get_logger().info(f"start heading (map) = {math.degrees(self._start_hdg):.0f}° -> dönüş-cezalı rota")
        route, self.wp_index = self._zincirle(
            wp_nodes, [nm if isinstance(nm, str) else None for nm in seq],
            self._start_hdg)
        self.route = route
        # OLAYLAR: kavsak dönüsleri + mission noktalari (sirali)
        # ⚠️ Bu dongu SON rota indeksini de kapsamak ZORUNDA. Onceki surumde
        # range(1, len(route)-1) idi; wp_index'in son anahtari tam olarak
        # len(route)-1 oldugu icin SON mission noktasi hicbir zaman olay
        # uretmiyordu. Pratikte: yarisin son adimi park_giris -> "5,3" PARK
        # komutu HIC gonderilmiyordu (teknik kontrolde hedef olayi da yoktu).
        # Donus olayi bir sonraki node'u gerektirir, o yuzden yalnizca o
        # k < len(route)-1 ile sinirli.
        # SURUS DIZISI: gorev noktalari grafta YAPRAK. Rota onlara sapip geri
        # donuyor (... 12 -> 26 -> 44(yaprak) -> 26 -> 13 ...) ve node 26'da
        # +46.9° / -140.4° gibi IKI SAHTE donus uretiyor -- oysa gercek manevra
        # 12 -> 26 -> 13, tek ve kucuk bir donus. Yapraklari cikarip ardisik
        # tekrarlari sikistirinca geriye gercek surus dizisi kaliyor.
        # (Olculdu 2026-08-20: bu duzeltmeden once 233 kombinasyonda 156 tane
        #  140-149°'lik sahte donus komutu uretiliyordu.)
        self._olaylari_kur(route, self._start_hdg)
        self.get_logger().info(f"ROTA ({len(route)} node): {route}")
        for nd, dg in self.cikmazlar:
            self.get_logger().info(
                f"  node {nd}: {dg:+.0f}° = cikmaz donusu (durak cebi/park girisi) -- "
                "TURN yayinlanmiyor, manevrayi brain yapacak")
        for i, e in enumerate(self.events):
            extra = f"{e['deg']:.0f}° {'SOL' if e.get('deg',0)>0 else 'SAG'}" if e["kind"]=="turn" else e.get("name","")
            self.get_logger().info(f"  OLAY {i}: {e['kind']:9} @node {e['node']} ({e['xy'][0]:.1f},{e['xy'][1]:.1f}) {extra}")

        # --- ROTA DOĞRULAMA: dönüşlerin toplamı = GeoJSON heading değişimi (map) ---
        # Araç start heading'inden hedef heading'ine dönmeli; rota bunu üretmiyorsa GRAF HATALI.
        final_name = seq[-1]
        if self._start_hdg is None:
            self.get_logger().warn("start heading yok -> rota dogrulamasi ATLANDI")
        elif final_name not in self._bearings:
            self.get_logger().warn(f"'{final_name}' heading'i yok -> rota dogrulamasi ATLANDI")
        if self._start_hdg is not None and final_name in self._bearings:
            want = math.degrees(norm(self._gps_hdg_to_map(self._bearings[final_name]) - self._start_hdg))
            # ⚠️ 'got' OLAY toplamindan hesaplanamaz: cikmaz donusleri (±180)
            # artik olay olarak yayinlanmiyor ama arac o donusu FIZIKSEL olarak
            # yapiyor. Rotanin ilk ve son segmenti arasindaki net aciyi kullan --
            # esiklerden ve filtrelerden bagimsiz, dogrudan geometri.
            # ⚠️ Referans nokta ARACIN START HEADING'i, rotanin ilk segmenti
            # DEGIL. Onceki surum ilk segmenti kullaniyordu; arac start'ta
            # rotanin ilk kenariyla ayni yone bakmak zorunda olmadigi icin
            # aradaki fark dogrudan hataya giriyordu. Ustelik yarisin 233
            # kombinasyonunun 232'sinde istenen net donus tam ±180° -- yani
            # sarma yuzunden zaten ayirt edici degil. Bu haliyle karsilastirma
            # sadelesiyor: "rota hedefe DOGRU YONDEN variyor mu".
            sr = self.surus
            got = (math.degrees(norm(self._hdg(sr[-2][0], sr[-1][0]) - self._start_hdg))
                   if len(sr) >= 2 else 0.0)
            self.get_logger().info(f"ROTA DOĞRULAMA: gereken net dönüş={want:+.0f}°, planner={got:+.0f}°")
            if abs(norm(math.radians(got - want))) > math.radians(35):
                self.get_logger().error(
                    f"⚠️ ROTA TUTARSIZ: net dönüş {got:+.0f}° ama GeoJSON {want:+.0f}° istiyor "
                    f"(fark {got-want:+.0f}°). Graf start→{final_name} arasını YANLIŞ yönlendiriyor "
                    "(zigzag/eksik köşe). Grafı düzeltmeden GÜVENME.")

    # ---------- tabela ile yeniden planlama ----------
    # decision_brain'deki sinif id'leriyle AYNI olmali.
    GIRILMEZ, SAGA_DON_YASAK, SOLA_DON_YASAK = 1, 9, 10
    # EMREDICI YON TABELALARI (25.08.2026 eklendi). Eskiden planner bunlari
    # HIC okumuyordu: beyin tabelayi gorup 12 m icinde FIZIKSEL olarak
    # doniyor, planner ise rotasinin degistiginden habersiz kaliyordu.
    # Sonuc: arac rotadan cikiyor, rota_sapma_max (10 m) ilerlemeyi donduruyor
    # ve ARKASINDAKI HICBIR OLAY ATESLEMIYOR -- arac rotasiz kaliyor.
    # Artik planner da ayni tabelayi okuyup grafta o kavsakta izin verilen
    # YON DISINDAKI tum cikislari kapatiyor; boylece yeni rota tabelaya uyar
    # ve iki taraf ayni yone gider.
    ILERI_SOL, ILERI_SAG, SOLA_DON, SAGA_DON, ILERI = 2, 3, 4, 8, 22
    # tabela -> o kavsakta IZIN VERILEN yonler
    ZORUNLU_YON = {SOLA_DON: ("sol",), SAGA_DON: ("sag",), ILERI: ("duz",),
                   ILERI_SOL: ("duz", "sol"), ILERI_SAG: ("duz", "sag")}

    def _master_cb(self, msg):
        """Beyinle AYNI /master hattini dinler, yalnizca YASAKLAYICI tabelalari
        okur: "3,<sinif>,<mesafe>,...".

        ⚠️ Emredici tabelalara (sola don, ileri sag ...) planner KARISMAZ.
        Onlari beyin zaten icra ediyor; ikisi ayni anda yon degistirirse
        catisirlar. Planner yalnizca "buradan gidilemez" bilgisini alip
        GRAFI kisitlar ve kalan gorevlere yeni rota kurar -- yani ne yapilacagi
        degil, NEREDEN GIDILECEGI kararini gunceller.
        """
        if not self.tabela_aktif or self.pos is None:
            return
        p = msg.data.split(',')
        try:
            if int(float(p[0])) != 3:
                return
            sinif = int(float(p[1]))
            mesafe = float(p[2])
        except (IndexError, ValueError):
            return
        if (sinif not in (self.GIRILMEZ, self.SAGA_DON_YASAK, self.SOLA_DON_YASAK)
                and sinif not in self.ZORUNLU_YON):
            return
        if mesafe > self.tabela_menzil:
            return
        n = self._tabela_say.get(sinif, 0) + 1        # beyin gibi teyit say
        self._tabela_say[sinif] = n
        if n < self.tabela_teyit:
            return
        self._tabela_say[sinif] = 0
        self._tabelaya_uy(sinif)

    def _onumdeki_kavsak(self):
        """Rotada onumuzdeki ilk kavsak: (onceki, kavsak, sonraki) rota indeksi."""
        for k in range(max(1, self._ilerleme), len(self.route) - 1):
            b = self.route[k]
            if self.N[b]["type"] not in ("kavsak", "viraj", "roundabout"):
                continue
            d = math.hypot(self.N[b]["map_x"] - self.pos[0], self.N[b]["map_y"] - self.pos[1])
            if d <= self.tabela_menzil + self.trig:
                return k
        return None

    def _son_gorev_zamanla(self):
        """son_gorev'in duraginda bekleme suresi dolduysa DUR gonder."""
        if (not self.son_gorev or self._son_gorev_dur_gonderildi
                or self._gate is None):
            return
        if self._gate.get("ad") != self.son_gorev:
            return
        if self._now() - self._gate["t0"] < self.son_gorev_bekle:
            return
        g = self._gate
        self._gate = None
        self._salindi = g["node"]
        self._son_gorev_kontrol(g)

    def _son_gorev_kontrol(self, g):
        """son_gorev'in duragi bittiyse beyne DUR (5,4,0) gonder ve orada kal."""
        if not self.son_gorev or self._son_gorev_dur_gonderildi:
            return
        if g.get("ad") != self.son_gorev:
            return
        self._send(4, 0)
        self._son_gorev_dur_gonderildi = True
        self.get_logger().warn(
            f"SON GOREV '{self.son_gorev}' tamamlandi -> '5,4,0' gonderildi: "
            "arac BURADA DURACAK ve bir daha hareket etmeyecek (MISSION_END).")

    def _tunel_koruma_kenarlari(self):
        """tunel_oncelik acikken tabelanin KAPATAMAYACAGI kenarlar:
        aracin bulundugu yerden ONUNDEKI tunel kenarina kadar olan rota
        kenarlari. Tunel geride kaldiysa (veya rotada yoksa) bos kume."""
        if not self.tunel_oncelik or not self.tunel_kenar:
            return set()
        tk = {tuple(sorted(e)) for e in self.tunel_kenar}
        ti = None
        for i in range(len(self.route) - 1):
            if tuple(sorted((self.route[i], self.route[i + 1]))) in tk:
                ti = i
                break
        if ti is None or ti < self._ilerleme:
            return set()          # tunel rotada yok ya da geride kaldi
        kor = set()
        for i in range(max(0, self._ilerleme), ti + 1):
            kor.add((self.route[i], self.route[i + 1]))
            kor.add((self.route[i + 1], self.route[i]))
        return kor

    def _tabelaya_uy(self, sinif):
        k = self._onumdeki_kavsak()
        if k is None:
            self.get_logger().warn(
                f"tabela {sinif} gorundu ama menzilde rota kavsagi yok -- yok sayildi")
            return
        J = self.route[k]
        onceki = self.route[k-1]
        gelis = self._hdg(onceki, J)
        def _yon(v):
            """J'den v'ye cikis, gelis yonune gore: sol / sag / duz."""
            dth = math.degrees(norm(self._hdg(J, v) - gelis))
            return "sol" if dth >= 40.0 else ("sag" if dth <= -40.0 else "duz")
        kapatilan = []
        if sinif == self.GIRILMEZ:
            kapatilan = [(J, self.route[k+1])]
        elif sinif in self.ZORUNLU_YON:
            # EMREDICI: izin verilen yon DISINDAKI her cikisi kapat.
            # ⚠️ GELDIGIN KENAR DA KAPANIR. Yasaklayici tabelalarda (sola/saga
            # donus yasak) geri kenari acik birakmak zararsizdi, ama emredici
            # tabelada A* onu KACIS YOLU olarak kullaniyordu: olculdu, SAGA DON
            # @node 39'da rota [39, 0, 1, ...] cikti -- yani arac tabelaya
            # uymak yerine geri donuyordu. "Saga mecburi" geri gitmeye de izin
            # vermez.
            izin = self.ZORUNLU_YON[sinif]
            for v, _ in self.adj[J]:
                if v == onceki or _yon(v) not in izin:
                    kapatilan.append((J, v))
        else:
            yasak_yon = "sol" if sinif == self.SOLA_DON_YASAK else "sag"
            for v, _ in self.adj[J]:
                if v == onceki:
                    continue
                if _yon(v) == yasak_yon:
                    kapatilan.append((J, v))
        kapatilan = [e for e in kapatilan if e not in self.yasak]
        # TUNEL ONCELIGI: tunele giden kenarlar kapatilamaz (bkz. __init__).
        # ⚠️ GIRILMEZ DAHIL HER TABELA (26.08.2026, operator karari -- once
        # GIRILMEZ muaf tutulmustu, sonra o muafiyet KALDIRILDI). Tunel
        # oncelikliyken tunele giden kenari HICBIR tabela kapatamaz; sebep
        # dolasik yolun olculen maliyeti: +25.6 m, +2 adet 90 derecelik donus
        # ve ~47 saniye. Her donus cikista ~1.9 m serit kaymasi birakiyor ve
        # serit ihlali -50/ihlal; yani dolasmak muhtemelen tabela ihlalinden
        # (-50 ceza + kaybedilen +50 bonus) daha pahali.
        kor = self._tunel_koruma_kenarlari()
        if kor:
            muaf = [e for e in kapatilan if e in kor]
            if muaf:
                kapatilan = [e for e in kapatilan if e not in kor]
                self.get_logger().warn(
                    f"TUNEL ONCELIGI: {muaf} kenari tabelaya RAGMEN acik "
                    "birakildi (tunel +200 > tabela ihlali -100). Diger "
                    f"kapatmalar aynen uygulaniyor: {kapatilan or 'yok'}")
        if not kapatilan:
            return
        self.yasak.update(kapatilan)
        ad = {self.GIRILMEZ: "GIRILMEZ", self.SAGA_DON_YASAK: "SAGA DONUS YASAK",
              self.SOLA_DON_YASAK: "SOLA DONUS YASAK", self.SOLA_DON: "SOLA DON",
              self.SAGA_DON: "SAGA DON", self.ILERI: "ILERI MECBURI",
              self.ILERI_SOL: "ILERI VEYA SOL",
              self.ILERI_SAG: "ILERI VEYA SAG"}.get(sinif, f"tabela {sinif}")
        self.get_logger().warn(
            f"{ad} @node {J}: kapatilan gecisler {kapatilan} -> yeniden planlaniyor")
        self._yeniden_planla(J, gelis)

    def _yeniden_planla(self, bas_node, in_hdg):
        """Kalan gorevlere yeni rota kur. BASARISIZ OLURSA ESKI PLAN KALIR --
        yarisin ortasinda plansiz kalmaktansa eski planla devam etmek yegdir."""
        # ---- ARA NOKTALAR (int): ONCE KORU, OLMAZSA DUS (26.08.2026) ----
        # Eskiden kosulsuz DUSURULUYORDU. Gerekcesi dogruydu (arkada kalmis
        # bir ara nokta araci geri dondurebilir) ama yan etkisi olculdu:
        # 3. gun rotasinda `40` ara noktasi gorev_2'nin CIKIS acisini +126
        # dereceden +29 dereceye indiriyor. 52 bir gorev_noktasi oldugu icin
        # surus dizisinden atlanir ve orada TURN KOMUTU YAYINLANMAZ -- yani
        # +126 derece, aracin serit takibiyle donmesi beklenen (ve donemedigi)
        # bir aci demek. Tabela yuzunden yapilan bir yeniden planlama bu
        # koruyucu ara noktayi da silince gorev_2 cikisi surulemez hale
        # geliyordu.
        # Cozum: once TAMAMLANMAMIS gorevlerden SONRA gelen ara noktalarla
        # dene; A* yol bulamazsa (tabela o yolu kapattiysa) ara noktalari
        # atip tekrar dene. Boylece:
        #   - tabela tuneli kapatirsa tunel BIRAKILIR (yasak kazanir),
        #   - kapatmadigi ara noktalar (or. `40`) KORUNUR.
        kalan_ad = [nm for nm in self.seq[1:]
                    if isinstance(nm, str) and nm not in self._tamamlanan]
        if not kalan_ad:
            self.get_logger().info("kalan gorev yok, yeniden planlamaya gerek yok")
            return
        # ⚠️ ARA NOKTA SECIMI ROTA ILERLEMESINE GORE, seq sirasina gore DEGIL
        # (26.08.2026'da duzeltildi). Once "ilk tamamlanmamis gorevden sonraki
        # ara noktalar" alinmisti; ama tunel ara noktalari (22, 21) seq'te
        # gorev_1'den ONCE geldigi icin arac tunele HENUZ GIRMEDEN yapilan bir
        # yeniden planlamada dusuyorlardi -> tabela tuneli iptal ediyordu.
        # Dogru olcut: ara nokta rota uzerinde ONUMUZDE mi (idx >= _ilerleme)?
        # Geride kalan ara nokta araci geri dondurur, o yuzden atilir.
        kalan_tam = []
        for nm in self.seq[1:]:
            if isinstance(nm, str):
                if nm not in self._tamamlanan:
                    kalan_tam.append(nm)
                continue
            try:
                idx = self.route.index(nm)
            except ValueError:
                idx = None
            if idx is None or idx >= self._ilerleme:
                kalan_tam.append(nm)
        eski = (self.route, self.wp_index, self.events, self.S,
                self.ev_i, self._ilerleme, self._yay, self._seg)
        son_hata = None
        for deneme, kalan in (("ara noktalarla", kalan_tam), ("ara noktasiz", kalan_ad)):
            wp = [bas_node] + [self._wp_dugum(nm) for nm in kalan]
            adlar = [None] + [(nm if isinstance(nm, str) else None) for nm in kalan]
            try:
                route, wp_index = self._zincirle(wp, adlar, in_hdg)
                self.route, self.wp_index = route, wp_index
                self._olaylari_kur(route, in_hdg)
                self._yay_kur()
                if deneme == "ara noktasiz" and kalan_tam != kalan_ad:
                    self.get_logger().warn(
                        "yeniden planlama: ara noktalar (tunel/gecis) DUSURULDU -- "
                        "tabelanin kapattigi yol zorunluydu")
                son_hata = None
                break
            except Exception as ex:
                son_hata = ex
                (self.route, self.wp_index, self.events, self.S,
                 self.ev_i, self._ilerleme, self._yay, self._seg) = eski
        if son_hata is not None:
            self.get_logger().error(
                f"YENIDEN PLANLAMA BASARISIZ ({son_hata}) -- ESKI PLANLA devam ediliyor. "
                "Tabelanin kapattigi yol tek cikissa graf o bolgede eksik olabilir.")
            return
        kalan = kalan_ad
        self.ev_i = 0
        self._ilerleme = 0
        self._yay = 0.0
        self._seg = 0
        self._gate = None
        self._salindi = None
        self._hedef_yaklasma_gonderildi = False
        self._hedef_dur_gonderildi = False
        self._hedef_min_d = None
        self._plan_no += 1
        self.get_logger().warn(
            f"YENI PLAN #{self._plan_no}: {len(route)} node, {len(self.events)} olay, "
            f"kalan gorev {kalan}")
        for i, e in enumerate(self.events):
            ek = (f"{e['deg']:.0f}°" if e["kind"] == "turn" else e.get("name", ""))
            self.get_logger().info(f"  YENI OLAY {i}: {e['kind']:9} @node {e['node']} {ek}")

    # ---------- runtime ----------
    def _pose_cb(self, msg):
        p = msg.pose.pose.position
        self.pos = np.array([p.x, p.y]); self.yaw = yaw_from_quat(msg.pose.pose.orientation)

    def _now(self):
        """Saniye. Ayri metot cunku benzetimde sahte saatle degistirilebiliyor."""
        return self.get_clock().now().nanoseconds * 1e-9

    def _send(self, *fields):
        m = String(); m.data = ",".join(str(x) for x in (ID_PLANNER,)+fields); self.pub.publish(m)

    def _park_izni(self):
        """Arac park bolgesine girdi mi? Girdiyse beyne BIR KEZ izin ver.
        Bkz. __init__'teki park_bolge_m notu. Olay listesinden BAGIMSIZ
        calisir -- park olayi tuketilmis olsa bile izin gitmis olur."""
        if self._park_izni_gonderildi or self._park_xy is None:
            return
        d = math.hypot(self.pos[0] - self._park_xy[0], self.pos[1] - self._park_xy[1])
        if d <= self.park_bolge_m:
            self._send(3, 1)
            self._park_izni_gonderildi = True
            self.get_logger().warn(
                f"PARK BOLGESINE GIRILDI ({d:.1f} m <= {self.park_bolge_m:.0f}) "
                "-> beyne 'P tabelasini kabul edebilirsin' izni gonderildi")

    def _tunel_kontrol(self):
        """Arac tunel kenarinin uzerinde mi? Kenar tetikli olarak beyne bildir."""
        icinde = False
        for a, b in self.tunel_kenar:
            A = np.array([self.N[a]["map_x"], self.N[a]["map_y"]])
            B = np.array([self.N[b]["map_x"], self.N[b]["map_y"]])
            v = B - A; L2 = float(v @ v)
            if L2 < 1e-6:
                continue
            t = float((self.pos - A) @ v) / L2
            if not (0.0 <= t <= 1.0):
                continue
            if float(np.linalg.norm(self.pos - (A + v * t))) <= self.tunel_yari_en:
                icinde = True
                break
        if icinde != self._tunelde:
            self._tunelde = icinde
            self._send(5, 1 if icinde else 0)
            self.get_logger().warn("TUNELE GIRILDI -> beyne 'duz (45) sur' "
                                   if icinde else "TUNELDEN CIKILDI -> serit takibi")

    def _onumdeki_dugum(self):
        """Aracin ONUNDEKI en yakin yol dugumu (yeniden planlama baslangici)."""
        if self.yaw is None:
            return self._nearest(self.pos)
        aday = []
        for i in self.road:
            d = np.array([self.N[i]["map_x"], self.N[i]["map_y"]]) - self.pos
            r = float(np.linalg.norm(d))
            if r < 1e-6:
                return i
            if abs(norm(math.atan2(d[1], d[0]) - self.yaw)) <= math.radians(90.0):
                aday.append((r, i))
        return min(aday)[1] if aday else self._nearest(self.pos)

    def _sapma_kontrol(self):
        """Rotadan uzun sure ciktiysak kalan goreve YENI rota kur."""
        # ⚠️ ARAC ROTAYA GIRMEDEN SAPMA OLCULEMEZ. Start noktasi rotanin ilk
        # dugumunun 16 m gerisinde olabiliyor (start_park_005) ve o mesafe
        # "rotadan cikti" sanilip HEMEN yeniden planlamaya sokuyordu --
        # olculdu: 2. gunun ilk donus komutu (node 0) bu yuzden kayboldu.
        if not self._rotaya_girdi or self._oto_replan >= self.sapma_max_replan:
            return
        if self._rota_sapma <= self.rota_sapma_max:
            self._sapma_t0 = None
            return
        if self._sapma_t0 is None:
            self._sapma_t0 = self._now()
            return
        if self._now() - self._sapma_t0 < self.sapma_sure:
            return
        self._sapma_t0 = None
        self._oto_replan += 1
        n = self._onumdeki_dugum()
        self.get_logger().warn(
            f"ROTADAN CIKILDI ({self._rota_sapma:.1f} m, {self.sapma_sure:.0f} s) "
            f"-> node {n}'den YENIDEN PLANLANIYOR ({self._oto_replan}. kez)")
        self._yeniden_planla(n, self.yaw if self.yaw is not None else 0.0)

    def _loop(self):
        if self.pos is None:
            return
        self._tunel_kontrol()
        self._park_izni()
        if self.ev_i >= len(self.events):
            # ⚠️ SON OLAY TUKETILDIKTEN SONRA DA CALISMALI: son_gorev'in DUR
            # komutu buradan gidiyor ve olay listesi coktan bitmis oluyor.
            # Eskiden bu return yuzunden "5,4,0" HIC gonderilmiyordu.
            self._son_gorev_zamanla()
            return
        self._ilerlemeyi_guncelle()
        self._sapma_kontrol()
        # KALKIŞ KAPISI (bkz. __init__'teki uzun not)
        # SON GOREV bittiyse artik hicbir komut gonderilmez: beyin zaten
        # MISSION_END'de (terminal) ve gelen komutlari yok sayiyor; yayina
        # devam etmek yalnizca log'u kirletir ve "neden hala komut gidiyor"
        # sorusunu dogurur.
        if self._son_gorev_dur_gonderildi:
            return
        if self._gate is not None:
            g = self._gate
            d = math.hypot(self.pos[0]-g["xy"][0], self.pos[1]-g["xy"][1])
            g["best"] = min(g["best"], d)          # en yakin yaklasma
            gecen = self._now() - g["t0"]
            if gecen >= self.hold_max:
                self.get_logger().warn(
                    f"durak/park kapisi {gecen:.0f} s sonra ZAMAN ASIMI ile aciliyor "
                    f"(kalkis algilanamadi; en yakin {g['best']:.1f} m, su an {d:.1f} m)")
                self._salindi = g["node"]; self._gate = None
                self._son_gorev_kontrol(g)
            elif gecen >= self.hold_min and d > g["best"] + self.resume_dist:
                self.get_logger().info(
                    f"araç kalktı ({gecen:.0f} s durdu, en yakin {g['best']:.1f} m -> "
                    f"{d:.1f} m) -> sonraki olay serbest")
                self._salindi = g["node"]; self._gate = None
                self._son_gorev_kontrol(g)
            else:
                return                              # hâlâ durakta
        e = self.events[self.ev_i]
        dist = math.hypot(self.pos[0]-e["xy"][0], self.pos[1]-e["xy"][1])
        # KAÇIRILAN OLAY ATLAMA: araç bu olayın rota indeksini geçtiyse ve tetiklenmediyse,
        # ev_i'yi burada takma — atla ki arkadaki olaylar bloke olmasın.
        # ⚠️ Kapisi YENI acilan duragin node'undaki olayi ATLAMA. Kapi olayi
        # bilerek geciktiriyor; o gecikme yuzunden "arac ilerledi" deyip
        # dusurmek, durak cikisindaki donus komutunu yok ediyordu (olculdu).
        # ATLAMA: yalnizca arac olayin noktasini rota boyunca gecis_payi
        # metreden fazla GECTIYSE. Amac tek bir kacan olayin butun misyonu
        # kilitlemesini onlemek; erken atlamak komut kaybettirdigi icin pay
        # bilerek genis tutuldu.
        # ⚠️ HEDEF olayi ATLANMAZ: atlanirsa arac yolu kapatan bariyere dogru
        # komutsuz ilerler. Gecilmisse asagida zaten DUR gonderiliyor.
        # DURAK/PARK icin ayri esik (bkz. durak_mesafe): donusun erken
        # tetiklenmesi gerekir, duragin ise DOGRU YERDE durmasi.
        esik = (self.durak_mesafe
                if (self.durak_mesafe > 0.0 and e["kind"] in ("passenger", "park"))
                else self.trig)
        # ---- ROTA BOYU (BOYLAMSAL) TETIK (24.08.2026) ----
        # Oklid mesafe YANAL SAPMAYLA KIRLENIYOR: graf cizgisi seridin
        # solunda, arac sag seritte. `pist_17tem_2` haritalama surusunde
        # olculdu -- arac graf cizgisinin +2.0 .. +5.7 m SAGINDAN gecmis
        # (saat yonu tersi turda sag serit = DIS serit). Sonucu:
        #   trigger_dist 3.3 ile node 20 (en yakin 3.71 m) ve node 32
        #     (3.62 m) donusleri HIC ateslenmiyor -> misyon kiriliyor,
        #   durak_mesafe 2.3 ile gorev_2 (3.44 m) duragi HIC ateslenmiyor.
        # Cozum: kalan mesafeyi rota UZERINDE olc. S[ri] olayin yay
        # uzunlugu, _yay aracin rotaya izdusurulmus ilerlemesi; farki
        # yanal sapmadan BAGIMSIZ. Boylece "kac metre kala" gercekten
        # boylamsal metre demek oluyor.
        # Oklid ESKI KOSUL OLARAK KALIYOR (VEYA): Oklid >= boylamsal
        # oldugu icin bu yalnizca DAHA COK atesleme demek, yeni bir
        # kacirma yolu acmaz. Rotadan tamamen cikilmissa _yay ilerlemez;
        # o durumda Oklid yedegi hala calisir.
        if (e["kind"] != "goal" and dist > esik and self._salindi is None
                and self._yay > self.S[e["ri"]] + self.gecis_payi):
            self.get_logger().warn(f"OLAY {self.ev_i} ({e['kind']}) KAÇIRILDI (araç ilerledi) -> atlanıyor")
            self.ev_i += 1
            return
        # ⚠️ ri==0 icin YAY UZUNLUGU ANLAMSIZ: arac henuz rotanin uzerinde
        # degil, S[0]=0 ve _yay=0 oldugu icin kalan=0 cikar ve olay ILK POZDA
        # atesler. Olculdu (start_park_005, 25.08): arac start cizgisinde
        # dururken "5,1,90.6" t=0'da gonderildi -- arac yerinde 91 derece
        # sola kirardi. Rotanin ILK dugumune olan mesafe ancak OKLID ile
        # olculebilir; yay, arac rotaya girdikten sonra anlamlidir.
        kalan = dist if e["ri"] == 0 else self.S[e["ri"]] - self._yay
        if kalan > esik and dist > esik:
            return
        if e["kind"] == "turn":
            appr = abs(norm(self.yaw - e["approach"])) < math.radians(60)
            # ⚠️ Durak/park kapisiyle GECIKTIRILEN donus, yaklasma testine takilir:
            # kapi acildiginda arac duraktan cikarken coktan donmeye baslamis
            # olabilir, o zaman |yaw-approach| 60'i asar ve komut HIC gitmez --
            # sonra da "kacirildi" diye atlanir, ustelik arkasindaki olay da
            # ayni sekilde dusebilir (olculdu: node 26'daki donus ve pesinden
            # node 12'deki donus birlikte kayboldu). Ayni node'da bekletildiysek
            # yaklasmayi VARISTA zaten dogrulamistik; testi atla.
            if not appr and self._salindi is not None:
                self.get_logger().info(
                    f"OLAY {self.ev_i}: yaklasma testi ATLANDI (durak kapisiyla geciktirildi)")
                appr = True
            if not appr:  # dogru yönden yaklasmiyorsa bekle
                return
            deg = float(e["deg"])
            if self.donus_yaw and self.yaw is not None and "cikis" in e:
                ham = math.degrees(norm(e["cikis"] - self.yaw))
                deg = max(e["deg"] - self.donus_yaw_pay,
                          min(e["deg"] + self.donus_yaw_pay, ham))
                self.get_logger().info(
                    f"OLAY {self.ev_i}: TURN geometrik {e['deg']:+.0f}° -> "
                    f"aracin yonune gore {ham:+.0f}°"
                    + (f" (PAY ile {deg:+.0f}° kirpildi)" if abs(ham - deg) > 0.5 else ""))
            self._send(1, round(deg, 1))
            self.get_logger().info(f"OLAY {self.ev_i}: TURN {deg:.0f}° gönderildi (dist={dist:.1f}m)")
        elif e["kind"] == "passenger":
            self._send(2, 0)
            self._gate = {"xy": e["xy"], "node": e["node"], "t0": self._now(), "best": dist,
                          "ad": e.get("name")}
            self._tamamlanan.add(e["name"])
            self.get_logger().info(f"OLAY {self.ev_i}: PASSENGER ({e['name']}) gönderildi")
        elif e["kind"] == "park":
            self._send(3, 0)
            self._gate = {"xy": e["xy"], "node": e["node"], "t0": self._now(), "best": dist,
                          "ad": e.get("name")}
            self._tamamlanan.add(e["name"])
            self.get_logger().info(f"OLAY {self.ev_i}: PARK gönderildi")
        else:  # goal (hedef) -- TEKNIK KONTROL: iki kademeli DURMA
            gecti = self._yay > self.S[e["ri"]]
            # ⚠️ DUR esigi de ROTA BOYU olculur (24.08.2026). Oklid ile
            # olculurse, arac hedefin yanindan hedef_dur_m'den UZAK gecerse
            # "5,4,0" HIC gitmez ve MISSION_END kurulmaz -- arac park alanini
            # durmadan gecer. Ozellikle park_hedef_gibi acikken kritik: park
            # alaninda serit ofseti 2-3 m, hedef_dur_m ise 2.0 m.
            # Oklid VEYA olarak kalir (bkz. yukaridaki tetik notu).
            if kalan > self.hedef_dur_m and dist > self.hedef_dur_m and not gecti:
                # Yaklasma kademesi: bir kez gonder, olayi TUKETME.
                if not self._hedef_yaklasma_gonderildi:
                    self._send(4, 1)
                    self._hedef_yaklasma_gonderildi = True
                    self.get_logger().info(
                        f"OLAY {self.ev_i}: HEDEF yaklasmasi (kalan={kalan:.1f}m "
                        f"oklid={dist:.1f}m) -> slalom yasak + hiz tavani")
                return
            if not self._hedef_dur_gonderildi:
                self._send(4, 0)
                self._hedef_dur_gonderildi = True
                self._hedef_min_d = dist
                self.get_logger().info(
                    f"OLAY {self.ev_i}: HEDEF -> DUR gonderildi "
                    f"(dist={dist:.1f}m, gecildi={gecti}); en yakin nokta izleniyor")
                return                      # olayi TUKETME
            # DUR gonderildi -> aracin hedefe EN YAKIN noktadan gecmesini bekle
            if dist < self._hedef_min_d:
                self._hedef_min_d = dist
                return
            if dist <= self._hedef_min_d + self.hedef_gecis_pay:
                return                      # henuz uzaklasmiyor
            self._send(4, 2)
            self._tamamlanan.add(e.get("name", "hedef"))
            self.get_logger().info(
                f"OLAY {self.ev_i}: HEDEF gecildi (en yakin {self._hedef_min_d:.2f} m, "
                f"simdi {dist:.2f} m) -> HEMEN DUR")
        self.ev_i += 1
        self._salindi = None


def main():
    rclpy.init(); node = RoutePlanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except rclpy.executors.ExternalShutdownException:
        pass          # SIGTERM (launch kapatmasi / timeout) -- traceback basma
    finally:
        node.destroy_node(); rclpy.ok() and rclpy.shutdown()


if __name__ == "__main__":
    main()
