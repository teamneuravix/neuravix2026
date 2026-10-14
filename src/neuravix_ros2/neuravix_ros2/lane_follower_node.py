#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LANE FOLLOWER FINAL VERSION
YOLO + BEV (Bird Eye View) + Clean Polyfit + Stable Steering
Uzun yanlış çizgiler FIX EDILDI
"""

# ROS
from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import String

# Vision
from cv_bridge import CvBridge
import cv2
import math
import numpy as np
import time
from collections import deque
from ultralytics import YOLO
import os

# Debug mouse
clicked_points = []


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        print("Clicked:", (x, y))


# ---------------- PID --------------------
class PIDController:
    def __init__(self, Kp=0.02, Ki=0.001, Kd=0.01, i_term_max=10.0, i_leak=0.98):
        # Kp 0.03 -> 0.02 (2026-08-20). 0.03 dogru olculmustu AMA o olcum
        # steer_target_gain=-0.75 gecerliyken yapildi. 2026-08-19'da gercek
        # dugumde gain -0.75 -> -1.20 oldu (arac mekanik kilidinin ancak %55'ini
        # kullaniyormus) ve Kp buna gore DUSURULMEDI -- ayni serit hatasi artik
        # %60 daha sert direksiyon uretiyor.
        # Iki bagimsiz yol ayni sayiyi veriyor:
        #   (1) asama0_48 kaydinda surucunun ham direksiyonunun olculen serit
        #       hatasina regresyonu: egim 0.0212 (597 ornek, serit takibi
        #       bolgesi) -> Kp = 0.0212/1.20 = 0.0177
        #   (2) davranisi sabit tutmak: 0.03 / (1.20/0.75) = 0.0187
        # 0.02 secildi (iki tahminin ustu, yuvarlak).
        # DERS: `steer_target_gain` degisirse `Kp` ters oranda ayarlanmali --
        # ikisi carpim halinde direksiyona gidiyor, ayri ayri ayarlanamaz.
        # Kd VARSAYILANI 0.01 -> 0.40 (2026-08-19, kapali cevrimde olculdu).
        # ONCE algi dogrulandi (bkz. asagidaki not): serit tahmini gercek yanal
        # sapmayi egim 0.86 / korelasyon 0.999 ile bildiriyor -> hata sinyali
        # SAGLAM, sorun onu direksiyona cevirmede. Yanal hataya saf oransal
        # kontrol araclarda dogasi geregi salinimlidir; sonumleme gerekir.
        # 6 senaryoda (3 sapma x 3 hiz) ortalama son yanal sapma:
        #     Kp 0.010 Kd 0.01 -> 1.47 m   (bugunun ilk duzeltmesi)
        #     Kp 0.010 Kd 0.20 -> 0.40 m
        #     Kp 0.010 Kd 0.40 -> 0.33 m   <- secilen
        #     Kp 0.005 Kd 0.40 -> 0.23 m   (daha iyi; -p steer_kp:=0.005 ile denenebilir)
        #     Kp 0.010 Kd 0.80 -> 1.39 m   (asiri sonumleme, tekrar bozuluyor)
        # Kp 0.01 -> 0.02 (2026-08-19 aksami, GERCEK ARAC VERISIYLE).
        # Asama-0 kaydi (asama0_48, 4.5 dk, surucu joystick ile suruyor,
        # lane_follower sadece dinliyor) 1299 eslesmis ornek verdi. Surucunun
        # ham direksiyonunu kontrolcunun o an OLCTUGU serit hatasina regresyon:
        #     tumu                 egim 0.046  kor +0.27  -> Kp 0.062
        #     hareketli            egim 0.040  kor +0.24  -> Kp 0.053
        #     SERIT TAKIBI bolgesi egim 0.021  kor +0.33  -> Kp 0.028
        #     + makul hata sinirli egim 0.024  kor +0.35  -> Kp 0.033
        # Yani insanin serit takibinde kullandigi etkin kazanc ~0.03; mevcut
        # 0.01 uc kat DUSUK, sabahki 0.08 ise ~2.5 kat YUKSEK'ti.
        # CELISKI COZULDU (ayni gun, daha sonra): bir HIZ meselesiymis.
        # Butun kapali cevrim testlerim 1.5-3.0 m/s'de kosuyordu, ama Asama-0
        # kaydinda GERCEK hiz medyan 3.0 km/h = 0.83 m/s -- yani gercegin
        # 2-4 katinda test etmisim. Aktuatorlu simulasyon iki hizda:
        #     Kp     0.83 m/s (GERCEK)      2.0 m/s
        #     0.01   0.48 m  %100 pistte    0.51 m  %100
        #     0.02   0.96 m  %100           1.71 m  %100
        #     0.03   1.07 m  %100           4.26 m   %75
        #     0.05   1.13 m  %100           --       %0
        #     0.08   2.93 m  %100           --       %0
        # Gercek calisma hizinda HICBIR kazanc araci pistten cikarmiyor.
        # Simulasyonun "yuksek kazanc tehlikeli" itirazi 7 km/h'de gecerliydi,
        # 3 km/h'de degil. Boylece olculen 0.03 guvenlik acisindan da dogrulandi
        # -> DEGER OLCUMDEN, GUVENLIK KONTROLU SIMULASYONDAN.
        # Not: simulasyon dusuk hizda da daha DUSUK Kp'yi "daha iyi" buluyor
        # (0.48 vs 1.07 m) ama bilinen yanliligi var (kaydirilmis BEV goruse
        # yeni girecek cizgileri uretemez, bu duzeltmeyi cezalandirir), ve
        # insanin gercekte kullandigi deger 0.03. Olcume oncelik verildi.
        # ARACTA: salinim gorursen -p steer_kp:=0.02 (yeniden derleme yok).
        # !!! IKI KANIT: gercek veri 0.03, simulasyon dusugu tercih ediyor !!!
        #   - gercek arac verisi        -> 0.03
        #   - aktuatorlu kapali cevrim  -> 0.01 (0.02'de 1.60 m/%100 pistte,
        #                                  0.03'te 3.90 m/%75, 0.04'te %25)
        # Her ikisinin de bilinen zayifligi var: regresyonun korelasyonu dusuk
        # (insan ONGORULU suruyor, kontrolcu tepkisel) ve simulasyon BEV
        # maskesini kaydirdigi icin goruse yeni girecek cizgileri uretemiyor,
        # bu da duzeltmeyi haksiz cezalandiriyor. 0.02 = simulasyonun hala
        # %100 pistte verdigi EN YUKSEK deger ve olculen 0.03'e en yakini.
        # ARACTA ILK TEST: 0.03'u dene ve gozle. Salinim yoksa orada birak;
        # salinirsa 0.02/0.015'e in.  -p steer_kp:=0.03  (yeniden derleme yok)
        # !!! 0.40 KISA SURE VARSAYILAN YAPILDI VE GERI ALINDI (ayni gun) !!!
        # Yukaridaki tablo yalnizca YANAL SAPMAYI olcuyor, DIREKSIYONUN
        # SIDDETINI olcmuyor. Ikinci metrik eklenince tablo tersine dondu --
        # kare-kare direksiyon degisimi (derece, 15 Hz):
        #     Kd 0.01 -> ort 0.06, maks  3   <- fiziksel olarak uygulanabilir
        #     Kd 0.10 -> ort 0.49, maks 25
        #     Kd 0.20 -> ort 0.79, maks 45
        #     Kd 0.40 -> ort 2.68, maks 60   = saniyede 900 derece (!)
        # Gercek direksiyon motoru bunun onda birini yapamaz; ayrica terim
        # analizi Kd=0.40'ta kontrolcunun TUREV-BASKIN hale geldigini gosterdi
        # (D/P orani 3.7x, direksiyon-hata korelasyonu 0.97 -> 0.29), yani
        # direksiyon yanal sapmayi degil kare-kare GURULTUYU takip ediyor.
        # DERS: bu boru hattinda bir kontrol degisikligi TEK metrikle
        # onaylanmamali -- takip hatasi + direksiyon yumusakligi BIRLIKTE.
        # Kd'yi yukseltmek ancak (a) hata sinyali filtrelenirse ve/veya
        # (b) node'a direksiyon HIZ SINIRI eklenirse anlamli olur; ikisi de
        # henuz yapilmadi ve arac verisiyle ayarlanmasi daha dogru.
        # Optimum ICERIDE (0.8'de kotulesiyor) -> kenara kacan monotonik bir
        # trend degil, gercek bir tepe. Her Kp ve heading_gain degerinde Kd
        # buyutmek iyilestirdi.
        # Kp VARSAYILANI 0.08 -> 0.01 (2026-08-19, kapali cevrimde olculdu).
        # 0.08 ASIRI YUKSEKTI: gercek ZED kaydi uzerinde kurulan kapali cevrim
        # testinde (tools/serit_bag_cevrim.py) 6 senaryonun 6'sinda da araci
        # PISTTEN CIKARDI. 3 baslangic sapmasi (0.3/0.5/1.0 m) x 3 hiz
        # (1.5/2.0/3.0 m/s) taramasi, ortalama son yanal sapma:
        #     Kp 0.002 -> 0.73 m  (pistte kalma %100)
        #     Kp 0.010 -> 1.47 m  (%100)   <- secilen
        #     Kp 0.020 -> 3.12 m  (%83)
        #     Kp 0.080 -> pistten cikti (%0)
        # Kontrol deneyi: Kp=0 (hic direksiyon yok) EN KOTU sonucu verdi
        # (1.73 m) -> test direksiyona onyargili degil, kazanc gercekten
        # optimumun cok ustundeymis. Bu, "duz yolda kararsiz" ve "viraji
        # donup sonra bozuluyor" semptomlarinin ders kitabi aciklamasi:
        # asiri kazanc -> asiri duzeltme -> salinim -> sapma.
        # 0.002 simulasyonda daha iyi ama 0.01 secildi: %100 pistte kalma
        # bolgesinde, 5 kat daha muhafazakar, aracta ilk denemede davranisi
        # anlamak daha kolay. Aracta gozleyip steer_kp ile 0.005/0.002'ye
        # inilebilir -- yeniden derleme GEREKMEZ.
        # UYARI: test BEV maskesini kaydirarak sapma taklit ediyor; goruse
        # yeni girecek cizgileri uyduramadigi icin gercekten ZOR. Mutlak
        # sayilar kotumser, GORELI siralama saglam.
        self.Kp = Kp  # Oransal kazanc
        self.Ki = Ki  # Integral kazanc
        self.Kd = Kd  # Turevsel kazanc
        # Anti-windup: Ki*integral teriminin mutlak ust siniri (derece).
        # 2026-07-12 arac testi: sinirsiz integral, sabit kucuk hatayla
        # dakikalar icinde direksiyonu 15/75 uclarina mihladi ve isaret
        # degisince yavasca obur uca surukledi (windup).
        self.i_term_max = i_term_max
        # LEAKY INTEGRATOR: her tik integral *= i_leak. Ki=0.001 cok kucuk
        # oldugu icin integral ~10000'e birikip clamp'te MIHLANIYOR ve kucuk
        # hatayla 500+ frame'de boşalıyordu (2026-07-19 bag: Error kucukken
        # bile steering 36/33 = mihli integral). Sizinti clamp'te sonsuza
        # takilmayi onler; birikmis bias ~birkac saniyede unwind olur.
        self.i_leak = i_leak
        self.prev_err = 0 # Bir cnceki framedeki hata
        self.integral = 0 # Zamana yayilmis hatanin birikimi

    def calculate(self, error, allow_integral=True):
        # CONDITIONAL INTEGRATION (Bug 3): integrali SADECE guvenilir/kucuk-hata
        # durumunda biriktir. Sistematik bias (tek-serit/carpik BEV) varken
        # integral clamp'e dayanip cikisi mihliyordu (45 sn sabit steer=27).
        # allow_integral=False iken integral DONDURULUR (birikmez, bosalmaz).
        self.integral *= self.i_leak     # leaky: her tik biraz sizar (unwind)
        if allow_integral:
            self.integral += error #Her karede hatayi ust uste ekler
        if self.Ki > 0:  # integral katkisini +-i_term_max dereceyle sinirla
            lim = self.i_term_max / self.Ki
            self.integral = max(-lim, min(lim, self.integral))
        der = error - self.prev_err #derivative
        self.prev_err = error #Bir sonraki frame icin referans olarak saklaniyor
        return self.Kp * error + self.Ki * self.integral + self.Kd * der

    def reset(self):
        """Serit kaybinda birikmis hatayi sifirla (bayat integral yeni
        serit bulununca yanlis yone cektirmesin)."""
        self.integral = 0
        self.prev_err = 0


# ---------------- LANE NODE --------------------
class LaneFollowerNode(Node):

    def bev_warp(self, img):
        return cv2.warpPerspective(img, self.M_ipm, (self.img_w, self.img_h))

    def bev_to_image(self, pts):
        if len(pts) == 0:
            return []
        pts_arr = np.array(pts, dtype=np.float32).reshape(-1, 1, 2)
        out = cv2.perspectiveTransform(pts_arr, self.M_ipm_inv)
        return out.reshape(-1, 2).astype(int).tolist()

    # YOLO mask combine
    def combine_masks(self, masks, shape):
        h, w = shape[0], shape[1]
        out = np.zeros((h, w), dtype=np.uint8)
        for m in masks:
            mm = cv2.resize(m, (w, h))
            mm = (mm > 0.5).astype(np.uint8) * 255
            out |= mm

        # KAPAMA (CLOSE): kesikli serit izlerindeki bosluklari doldurur -> buyuk
        # cekirdek faydali. 11x11 = saginda-solunda 5, altinda-ustunde 5 piksel.
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, kernel, 2)
        # ACMA (OPEN): kucuk gurultu lekelerini siler. ⚠️ ESKIDEN BURADA DA
        # 11x11 KULLANILIYORDU VE SERIT IZLERINI YOK EDIYORDU: acma, cekirdekten
        # INCE olan her yapiyi siler; uzaktaki serit cizgileri tam da o
        # kalinliktadir. Ham ZED kaydinda (pist_18_3tem, 161 kare) olculdu:
        #     OPEN 11x11 -> iki serit fit %40.4, hic fit yok %25.5
        #     OPEN  3x3  -> iki serit fit %64.6, hic fit yok %14.9
        # Kalite dusmedi: serit genisliginin IQR'i 37 -> 41 px (ortadaki %50
        # yayilimi ayni). std'nin 33 -> 51 cikmasi birkac aykiri fit yuzunden,
        # toplu bir bozulma degil. 3x3 tek-piksel gurultusunu hala temizler.
        out = cv2.morphologyEx(
            out, cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), 1)
        return out

    # ------------- FINAL POLYFIT -----------------
    def fit_lane_poly(self, mask):
        ys, xs = np.where(mask > 0)
        if len(xs) < self.fit_min_points:
            self._son_fit_red = 'MASKE_KUCUK'
            return None

        # ustteki bozuk BEV bolgesi silinir (fit_far_frac parametreli, eski
        # sabit 0.55 = ~5.8 m; bkz. __init__'teki ILERI BAKIS aciklamasi)
        y_min = int(self.img_h * self.fit_far_frac)
        keep = ys >= y_min
        ys = ys[keep]
        xs = xs[keep]

        if len(xs) < max(15, self.fit_min_points // 2):
            self._son_fit_red = 'MASKE_KUCUK'
            return None

        # Gecerli serit izi mi? BEV'de bir serit cizgisi DIKEY olarak uzundur;
        # gurultu lekesi ise kompakttir. Bu yuzden olcut satir acikligidir.
        # ESKI KILAVUZ HATALIYDI: `np.std(xs) < 5` YATAY yayilima bakiyordu ve
        # tam da ideal durumu -- duz, kameraya hizali serit -- reddediyordu
        # (sentetik test: kusursuz dikey 7 px cizgi -> std=2.0 -> fit YOK).
        # Sonucu: duz bolumlerde iki fit de dusuyor, bayat left_prev/right_prev
        # kullaniliyor, 15 kare sonra lane_lost ile notr 45'e duşuluyordu; yani
        # duz yolda yanal ofset HIC duzeltilmiyordu. Satir acikligi olcutu ayni
        # zamanda yatay cizgileri (dur cizgisi, yaya gecidi) de eler.
        if np.ptp(ys) < self.img_h * self.fit_min_span_frac:
            self._son_fit_red = 'YAYILIM_KISA'
            return None

        try:
            # Agirlik: uss BUYUDUKCE fit yakin satirlara kilitlenir ve ileri
            # bakis islevsiz kalir (uzatilan dogru yine burun tegetidir).
            # fit_weight_pow=1 -> pencerenin tamami katkida bulunur.
            if self.fit_weight_pow > 0:
                w = (ys / np.max(ys)) ** self.fit_weight_pow
            else:
                w = None

            # DERECE 2 + DERECE 1 YEDEK (2026-08-11)
            # Serit viraja girdiginde DOGRU (derece 1) egriyi temsil edemez;
            # fit, ileri-bakis satirinda maskenin gercek merkezinden sapar.
            # Gercek ZED kaydinda olculdu -- fit ile maskenin kendi merkezi
            # arasindaki fark (px), ILERI BAKIS satirinda:
            #     viraj:   derece1 ort 16.7 / %90 49.9   derece2 ort 7.9 / %90 21.4
            #     tum bag: derece1 ort  8.6 / %90 20.4   derece2 ort 4.4 / %90  8.5
            # Yani derece 2 IKI KAT isabetli. Peki neden varsayilan degildi?
            # Cunku daha ONCE yanlis metrikle olculmustu: "kac fit cikiyor"
            # (verim) bakilmis, derece 2 daha az fit uretti diye elenmisti.
            # Isabet olculunce tablo tersine dondu.
            # COZUM: once derece 2 dene, tutmazsa derece 1'e dus. Boylece
            # verim de korunuyor (olculen: viraj %78.5 -> %80.2, tum bag
            # %74.9 -> %75.7) ve isabet iki kat artiyor (16.8 -> 8.5 px).
            # Derece 2 icin veri yeterliligi sarti: parabol az/kisa veriyle
            # asiri uyum yapar, o yuzden en az 40 nokta ve 0.15*H satir
            # acikligi istiyoruz; saglanmazsa dogrudan derece 1.
            # ADAPTIF DERECE: parabolu ancak DOGRUDAN BELIRGIN IYIYSE kullan.
            # Ilk hali "once derece 2, tutmazsa 1" idi; isabeti iyilestirdi ama
            # DUZ yolda parabol gurultuye uyup direksiyonu oynatiyordu (aracta
            # gozlendi: "duz yolda kararsiz"). Cozum: her iki dereceyi de fitle,
            # agirlikli RMS artiklarini kiyasla, derece 2'yi yalnizca artigi
            # fit_deg2_kazanc katsayisindan fazla dusuruyorsa sec. Duz yolda
            # parabolun kazanci yoktur -> otomatik olarak DOGRU kullanilir.
            # Gercek ZED kaydinda olculdu (viraj / tum bag):
            #                      iki fit   isabet(ort)   aci oynamasi   IQR
            #   derece 1           78.5%      16.8 px         0.13 d       56
            #   derece 2 + yedek   80.2%       8.5 px         0.17 d       74
            #   ADAPTIF 0.85       80.2%       9.7 px         0.14 d       49
            # ⚠️ AMA STATIK METRIKLER YANILTTI. Ayni ayarlar KAPALI CEVRIMDE
            # (gercek kayit, olu bant 5, 0.5 m sapmadan) sinandiginda:
            #                   DUZ ort/son 2fit     VIRAJ ort/son 2fit
            #   derece 1        0.25/0.14  100%      0.48/0.53   17%
            #   derece 2 (hep)  0.26/0.18   99%      0.59/0.20   36%   <- SECILEN
            #   adaptif 0.85    0.27/0.19  100%      0.47/0.52   17%
            # Virajda YALNIZCA derece 2 yakinsiyor (son hata 0.20 m); digerleri
            # 0.52'de takiliyor ve iki-fit orani yariya duşuyor. Adaptif kural
            # dongude neredeyse hep derece 1'i seciyor (kaydirilmis maskede
            # parabolun artik avantaji kuculuyor) ve viraj kazancini kaybediyor.
            # Duzdeki bedel kucuk (son hata 0.14 -> 0.18 m), viraj kazanci buyuk.
            # Bu yuzden varsayilan k=1.0 (artigi dusuruyorsa parabol) -- pratikte
            # hemen her karede derece 2. Duz yolda oynama rahatsiz ederse
            # -p fit_deg2_kazanc:=0.6 ile derece-1 davranisina donulur.
            def _fitle(deg):
                if deg == 2 and (len(xs) < 40
                                 or np.ptp(ys) < self.img_h * 0.15):
                    return None, None      # parabol icin veri yetersiz
                try:
                    p = np.polyfit(ys, xs, deg, w=w)
                except Exception:
                    return None, None
                if abs(float(np.polyval(np.polyder(p), self.y_eval))) \
                        > self.fit_max_slope:
                    self._son_fit_red = 'EGIM_REDDI'
                    return None, None      # egim kilavuzu
                art = float(np.sqrt(np.average((np.polyval(p, ys) - xs) ** 2,
                                               weights=w)))
                return p, art

            if self.fit_degree == 2:
                p1, a1 = _fitle(1)
                p2, a2 = _fitle(2)
                if p2 is None:
                    poly = p1
                elif p1 is None:
                    poly = p2
                else:
                    poly = p2 if a2 < self.fit_deg2_kazanc * a1 else p1
            else:
                poly, _ = _fitle(self.fit_degree)
            if poly is None:
                return None

            # Egim cok buyukse yanlis fit'tir (ekrandan capraz gecen cizgi).
            # ⚠️ ESKI SABIT 1.0 VIRAJDA GECERLI FITLERI CÖPE ATIYORDU.
            # Yorumdaki "BEV seritleri dikeydir, egim 0.1-0.6" gozlemi yalnizca
            # DUZ yol icin dogru; virajda serit BEV'de mesru olarak dikleşir.
            # Gercek ZED kaydinin viraj kesitinde (t=227-264 s, 550 kare)
            # olculdu: TEK FIT kalan karelerin %81.5'inde eksik tarafin maskesi
            # VARDI, noktasi ve uzunlugu YETIYORDU -- sadece bu kurala takiliyordu.
            # Belirti: saga viraja girerken sag cizgi elenir, merkez yalnizca sol
            # cizgiden tahmin edilir ve sola kayar (aracta gozlendi).
            # Esik taramasi (viraj kesiti / duz kesit, iki-fit orani | IQR):
            #     1.0 -> %58.4 / %88.2   IQR 51/40   (ESKI)
            #     2.0 -> %72.0 / %100    IQR 54/39
            #     3.0 -> %78.5 / %100    IQR 56/39   <- SECILEN
            #     5.0 -> %86.7 / %100    IQR 78/39
            # TUM BAG (814 kare) ile de dogrulandi: 1.0->%62.2, 2.5->%72.6,
            # 3.0->%74.9, 5.0->%81.1 iki-fit; genislik medyani (457-461 px) ve
            # IQR'i (42-46) TUM esiklerde sabit -> gevsetme cop fit getirmiyor.
            # Kararlilik (ardisik karelerde merkez degisimi) 3.6->5.1 px'e
            # cikiyor; 3.0'da 4.5 px ile makul.
            # SECIM GEREKCESI (fiziksel): y_eval'de egim ~3.0, yaklasik 5.6 m
            # viraj yaricapina karsilik gelir. Aracin tam kilitle alabilecegi en
            # dar viraj L/tan(29 derece) ~ 3.4 m oldugundan 3.0 her surulebilir
            # viraji kapsar. Daha yukarisi fiziksel gerekce olmadan gurultuye
            # kapi acar. Yatay cizgiler (dur cizgisi, yaya gecidi) yine elenir --
            # onlarin egimi bundan cok daha buyuktur.
            # ---- EKSTRAPOLASYON KAPISI ----
            # y_eval verinin ULASTIGI satir araliginin disindaysa polinom
            # oradaki degeri UYDURUYOR demektir. Parabol bu durumda savrulur;
            # dogrusal en azindan monoton kalir.
            if poly is not None:
                _lo, _hi = int(ys.min()), int(ys.max())
                self._son_span = (_lo, _hi)
                _uzak = (0 if _lo <= self.y_eval <= _hi else
                         (_lo - self.y_eval if self.y_eval < _lo
                          else self.y_eval - _hi))
                # Adaptif ileri bakis ACIKKEN mesafe reddi YAPILMAZ: olcum
                # zaten verinin icinde bir satirda yapilacak, ekstrapolasyon
                # olusmayacak. Ikisi ayni sorunu cozer; adaptif olan daha iyi
                # cunku olcumu KAYBETMEZ, sadece ileri bakisi kisaltir.
                if not self.adaptif_lookahead:
                    if _uzak > self.fit_extrap_max_row:
                        self._son_fit_red = 'EKSTRAPOLASYON'
                        return None
                if (not self.adaptif_lookahead) and \
                        _uzak > self.fit_extrap_deg1_row and len(poly) > 2:
                    _p1, _ = _fitle(1)     # parabolu birak, dogruya dus
                    if _p1 is None:
                        return None
                    poly = _p1
                # Fiziksel makuliyet: VERININ ICINDE bir satirda degerlendir
                # (adaptif modda olcum orada yapilacak).
                _yv = max(_lo, min(_hi, self.y_eval))
                _x = float(np.polyval(poly, _yv))
                if not (-0.25 * self.img_w <= _x <= 1.25 * self.img_w):
                    self._son_fit_red = 'GORUNTU_DISI'
                    return None
            return poly

        except Exception:
            self._son_fit_red = 'FIT_HATASI'
            return None

    def _egim(self, lp, rp, y):
        """Seridin y satirindaki yonu (dx/dy). Iki fit varsa ortalamasi.
        Yon onizlemesi (heading feedforward) icin kullanilir: BEV'de saga
        kivrilan seritte dx/dy < 0 olur."""
        e = [float(np.polyval(np.polyder(p), y))
             for p in (lp, rp) if p is not None]
        return (sum(e) / len(e)) if e else None

    def _tek_fit_merkez(self, poly, sol_mu, y_eval):
        """Tek serit gorulen karede serit merkezi.

        NEDEN SABIT YARIM SERIT DEGIL: iki fitten tek fite GECIS aninda merkez
        sicriyordu. Gercek ZED kaydinda olculdu (2026-08-11): ardisik kareler
        arasi normal oynama 2 px iken, gecis aninda medyan 13 px, %90 dilim
        72 px, en fazla 97 px (0.77 m) -- normalin 8.8 KATI. Aracta gorulen
        "sag cizgi kaybolunca serit yana atiliyor" belirtisi tam olarak budur.
        Sabit yarim serit (lane_w_px/2) o anki GERCEK ofseti degil, kareler
        boyunca yumusatilmis bir ORTALAMAYI uyguluyordu.

        COZUM: iki fitin de goruldugu SON karede olculen ofseti sakla ve tek
        fite dusunce onu uygula. Gecis boyunca merkez sureklidir.
        Olculen iyilesme (gecis anindaki sicrama, %90 dilim):
            viraj kesiti: 21 px -> 6 px
            duz kesit   : 11 px -> 2 px
        NOT: bunun EMA ile yumusatilmis hali DENENDI ve ise YARAMADI (sapma
        60 -> 66 px) -- cunku ortalama gecikiyor. Onemli olan SON degeri
        kullanmak."""
        x = self.poly_x(poly, y_eval)
        off = self.off_sol if sol_mu else self.off_sag
        if off is None:                      # henuz hic iki fit gorulmedi
            off = self._half_lane()
        # akil sagligi: ofset makul serit yari genisligi araliginda kalmali
        off = max(self.half_lane_min, min(self.half_lane_max, off))
        return x + off if sol_mu else x - off

    def _half_lane(self):
        """Tek şerit görülen karelerde merkezi tahmin için yarım şerit
        genişliği (BEV px). Ölçülen lane_w_px varsa onun yarısı (makul
        aralığa clamp), yoksa teorik half_lane_bev."""
        if self.lane_w_px:
            return int(max(self.half_lane_min,
                           min(self.half_lane_max, self.lane_w_px / 2.0)))
        return self.half_lane_bev

    # ---------------- ANALITIK IPM -----------------
    def _zemin_to_goruntu(self, d, l, h, th, fx, fy, cx, cy):
        """Zemin noktasi (d ileri, l sol) -> goruntu pikseli (u, v).
        Delik-ignesi kamera, duz zemin, egim th (asagi bakis pozitif):
            z_c = d*cos(th) + h*sin(th)      kamera onu
            y_c = h*cos(th) - d*sin(th)      kamera asagisi
            u = cx - fx*l/z_c ,  v = cy + fy*y_c/z_c"""
        zc = d * np.cos(th) + h * np.sin(th)
        yc = h * np.cos(th) - d * np.sin(th)
        return (cx - fx * l / zc, cy + fy * yc / zc)

    def _analitik_ipm_kur(self):
        """Homografiyi elle tiklanan noktalardan DEGIL, kamera ic
        parametreleri + yukseklik + egimden hesapla. Boylece BEV satiri <->
        mesafe ve piksel <-> metre donusumleri KESIN olur."""
        h = float(self.get_parameter("cam_height_m").value)
        th = np.radians(float(self.get_parameter("cam_pitch_deg").value))
        fx = float(self.get_parameter("cam_fx").value)
        fy = float(self.get_parameter("cam_fy").value)
        cx = float(self.get_parameter("cam_cx").value)
        cy = float(self.get_parameter("cam_cy").value)
        self.bev_near_m = float(self.get_parameter("bev_near_m").value)
        self.bev_far_m = float(self.get_parameter("bev_far_m").value)
        half_w = float(self.get_parameter("bev_half_width_m").value)

        # Zemindeki dikdortgenin 4 kosesi -> BEV'de goruntu dikdortgeni.
        # BEV: satir 0 = en uzak, satir H-1 = en yakin; sutun W/2 = yanal 0.
        zemin = [(self.bev_near_m, +half_w), (self.bev_near_m, -half_w),
                 (self.bev_far_m, -half_w), (self.bev_far_m, +half_w)]
        src = np.float32([self._zemin_to_goruntu(d, l, h, th, fx, fy, cx, cy)
                          for d, l in zemin])
        dst = np.float32([[0, self.img_h - 1], [self.img_w - 1, self.img_h - 1],
                          [self.img_w - 1, 0], [0, 0]])
        self.M_ipm = cv2.getPerspectiveTransform(src, dst)
        self.M_ipm_inv = cv2.getPerspectiveTransform(dst, src)
        self.src_pts = src          # teshis/gorsellestirme icin
        # Analitik modda olcek KESIN — tahmin edilen degerlerin yerini alir
        self.BEV_NEAR_ROW, self.BEV_FAR_ROW = self.img_h - 1, 0
        self.D_NEAR_M, self.D_FAR_M = self.bev_near_m, self.bev_far_m
        self.PX_PER_M = self.img_w / (2.0 * half_w)
        self.get_logger().info(
            f"IPM=analitik: h={h:.3f} m, egim={np.degrees(th):.1f} derece, "
            f"kapsam {self.bev_near_m:.1f}-{self.bev_far_m:.1f} m, "
            f"+-{half_w:.1f} m yanal -> {self.PX_PER_M:.1f} px/m")

    # ---------------- BEV TESHIS GORUNTUSU -----------------
    def _m_to_row(self, d_m):
        """Yerdeki mesafe (m) -> BEV satiri. row_to_m'in tersi."""
        fr = (d_m - self.D_FAR_M) / (self.D_NEAR_M - self.D_FAR_M)
        return int(self.BEV_FAR_ROW + fr * (self.BEV_NEAR_ROW - self.BEV_FAR_ROW))

    def _bev_debug(self, img, bev_mask, left_poly, right_poly, lane_x):
        """Kusbakisi (BEV) teshis goruntusu.

        NEDEN VAR: BEV bu node'un icinde hesaplaniyordu ama disari HIC
        verilmiyordu -- yani homografinin dogru olup olmadigini kimse
        goremiyordu. (Nitekim 11x11 MORPH_OPEN'in maskeyi bozdugu da ancak
        bu gorunturlerle fark edildi.) Iki kritik sorunun cevabi burada:
          1) OLCEK  : metre izgarasi gercekten o mesafelere denk geliyor mu?
                      Sag/sol dikey referanslar (+-1.5 m) gercek serit
                      cizgilerinin uzerine oturuyor mu?
          2) PARALELLIK: duz yolda iki fit BEV'de PARALEL ve DIKEY olmali.
                      Yakinsiyor/uzaklasiyorsa homografi (src_pts) bozuk.
        Ayrica fit'in serit cizgisine mi yoksa BARIYERE mi oturdugu buradan
        bakinca aninda belli olur."""
        bev_img = self.bev_warp(img)
        if bev_mask is not None:
            # YOLO'nun bulduklarini yesil tint ile goster
            tint = np.zeros_like(bev_img)
            tint[:, :, 1] = bev_mask
            bev_img = cv2.addWeighted(bev_img, 1.0, tint, 0.45, 0)

        mid = self.img_w // 2
        # --- METRE IZGARASI (olcek sagmasi) ---
        for d in (2, 4, 6, 8, 10):
            row = self._m_to_row(d)
            if 0 <= row < self.img_h:
                cv2.line(bev_img, (0, row), (self.img_w, row), (90, 90, 90), 1)
                cv2.putText(bev_img, f"{d}m", (4, row - 3),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (160, 160, 160), 1)
        # --- YANAL REFERANS: +-yari serit genisligi (serit genisligi sagmasi) ---
        half_px = int(self.lane_width_m / 2.0 * self.PX_PER_M)
        for s in (-1, 1):
            x = mid + s * half_px
            if 0 <= x < self.img_w:
                cv2.line(bev_img, (x, 0), (x, self.img_h), (90, 90, 90), 1)
        cv2.putText(bev_img, f"gri dikey = +-{self.lane_width_m/2:.2f}m (beklenen serit)",
                    (4, self.img_h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    (160, 160, 160), 1)

        # --- FITLER ---
        ys = np.linspace(int(self.img_h * self.fit_far_frac),
                         self.img_h - 1, 40).astype(int)
        for poly, span, col in ((left_poly, self._span_sol, (255, 0, 0)),
                                (right_poly, self._span_sag, (0, 0, 255))):
            if poly is None:
                continue
            if span:
                y0 = max(int(self.img_h * self.fit_far_frac), int(span[0]))
                y1 = min(self.img_h - 1, int(span[1]))
            else:
                y0, y1 = int(self.img_h * self.fit_far_frac), self.img_h - 1
            if y1 - y0 < 4:
                continue
            pts = [(self.poly_x(poly, y), y)
                   for y in np.linspace(y0, y1, 40).astype(int)]
            for i in range(len(pts) - 1):
                cv2.line(bev_img, pts[i], pts[i + 1], col, 2)

        # --- MERKEZ (sari) ve REFERANS MERKEZ (yesil) ---
        _cp = self.merkez_poly(left_poly, right_poly)
        if _cp is not None:
            _ys = np.linspace(self.img_h - 1, int(self.img_h * self.fit_far_frac),
                              24).astype(int)
            for _i in range(len(_ys) - 1):
                cv2.line(bev_img, (self.poly_x(_cp, _ys[_i]), int(_ys[_i])),
                         (self.poly_x(_cp, _ys[_i + 1]), int(_ys[_i + 1])),
                         (0, 255, 255), 2)
        else:
            cv2.line(bev_img, (int(lane_x), self.img_h - 1),
                     (int(lane_x), int(self.img_h * self.fit_far_frac)),
                     (0, 255, 255), 2)
        ref_x = int(mid + self.err_offset)
        cv2.line(bev_img, (ref_x, self.img_h - 1),
                 (ref_x, int(self.img_h * self.fit_far_frac)), (0, 255, 0), 2)

        # --- ILERI BAKIS SATIRI (mor) ---
        cv2.line(bev_img, (0, self.y_eval), (self.img_w, self.y_eval),
                 (255, 0, 255), 2)
        cv2.putText(bev_img, f"ileri bakis {self.lookahead_m:.1f}m",
                    (self.img_w - 165, self.y_eval - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 1)

        # --- OLCULEN GENISLIK ---
        if self.lane_w_px:
            m = self.lane_w_px / self.PX_PER_M
            cv2.putText(bev_img, f"olculen genislik: {self.lane_w_px:.0f}px "
                        f"= {m:.2f}m", (4, 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        return bev_img

    def poly_x(self, poly, y):
        if poly is None: #Poly yoksa crash olmasin
            return 0
        if len(poly) == 2: #Linear fit icin hizli hesap
            m, b = poly
            return int(m * y + b)
        # fallback ( Eski fitler fallback olarak korunuyor )
        return int(np.polyval(poly, y))

    # ---------------- NODE INIT -----------------
    def __init__(self):
        super().__init__("lane_follower")

        self.bridge = CvBridge() #ROS Image <-> OpenCV cv::Mat donusumu icin CvBridge
        self.img_w = 640
        self.img_h = 360

        # BEV Homografi (Noktalari biz belirledik. Yaris aninda ekrandan kamera acisina gore yol koseleri kontrol edilmeli. Ciktida yolun kenarlarina basinca koordinat degerleri veriliyor.)
        # 2026-07-19: GERÇEK ZED karesinden kalibre edildi (pist_18_3tem bag'i,
        # srcpts_click.py ile tıklandı). Eski CARLA trapezi kaldırıldı (Bug 2).
        # Kenarlar şerit sınırlarını izler (sol=beyaz kesikli, sağ=bariyer).
        # ⚠️ PARAMETRE, SABIT DEGIL. Trapez KAMERAYA ozeldir: asagidaki
        # varsayilan GERCEK ARAC (ZED) kalibrasyonudur. CARLA'nin kamerasi
        # bambaska bir trapez ister ve onu launch/arayuz parametreyle gecer:
        #   ~/Desktop/carla-slalom/slalom_arayuz.py "6. Serit Takip" butonu
        #   -p src_pts:="[72.1,302.6, 567.9,302.6, 384.7,197.5, 255.3,197.5]"
        #   (ureten script: ~/Desktop/carla-slalom/bev_kalibre.py)
        # Sabit gomulu birakilirsa o buton sessizce ZED trapeziyle calisir ve
        # CARLA'da serit takibi bozulur -- hata vermeden.
        # Sira: bottom-left, bottom-right, top-right, top-left.
        _ZED_SRC = [170.0, 357.0, 639.0, 358.0, 367.0, 210.0, 312.0, 210.0]
        self.declare_parameter("src_pts", _ZED_SRC)
        _sp = list(self.get_parameter("src_pts").get_parameter_value().double_array_value)
        if len(_sp) != 8:
            self.get_logger().error(
                f"src_pts 8 sayi olmali (BL,BR,TR,TL), {len(_sp)} geldi -> "
                "varsayilan (ZED) kullaniliyor.")
            _sp = _ZED_SRC
        self.src_pts = np.float32(_sp).reshape(4, 2)

        self.dst_pts = np.float32([
            [self.img_w * 0.20, self.img_h * 0.95],
            [self.img_w * 0.80, self.img_h * 0.95],
            [self.img_w * 0.80, self.img_h * 0.10],
            [self.img_w * 0.20, self.img_h * 0.10],
        ])

        # ================= IPM (kusbakisi) NASIL KURULUYOR =================
        # IKI YOL VAR:
        #
        # 1) "src_pts"  (VARSAYILAN): yukaridaki 4 nokta elle tiklanir.
        #    ✅ SEKLI DOGRU CIKTI (2026-07-21, ham ZED kaydiyla olculdu).
        #    Serit genisliginin BEV satirina gore degisimi (dogru bir
        #    kusbakisinda SABIT olmali) 161 ham karede:
        #        satir 200/240/280/320/350 -> 462/461/456/448/450 px
        #        sabitlik orani 1.026 (%2.6 sapma) = saglikli
        #    ⚠️ ONEMLI DERS: ayni olcum daha once 1.165 cikmis ve "homografi
        #    bozuk" sanilmisti. Gercek sebep homografi DEGIL, combine_masks'teki
        #    11x11 MORPH_OPEN idi: goruntu uzayinda uygulanan o acma, uzaktaki
        #    INCE serit izlerini silip yakindakileri traslayarak mesafeye bagli
        #    yapay bir genislik egimi uretiyordu. Acma 3x3'e indirilince sapma
        #    1.165 -> 1.026'ya dustu. Morfoloji hatasini homografiye yazmayin.
        #    Geriye kalan tek belirsizlik MUTLAK OLCEK: olculen 462 px, kabul
        #    edilen 125.5 px/m ile 3.68 m yapiyor; pistte olculen serit ~2.96 m.
        #    Fitlerden biri bariyere oturuyor olabilir ya da px/m %24 sapmali.
        #    ETKISI KUCUK: err piksel cinsinden ve Kp ile olcekleniyor,
        #    _half_lane() da piksel kullaniyor -> olcek hatasi yalnizca METRE
        #    GOSTERIMLERINI etkiler, direksiyonu etkilemez.
        #
        # 2) "analytic" (OPSIYONEL — su an GEREKLI DEGIL): homografi IC
        #    kamera yuksekligi + egim acisindan HESAPLANIR. Olcek insa geregi
        #    dogru olur; satir<->mesafe ve piksel<->metre kesindir.
        #    Gereken IKI olcum:
        #      cam_height_m : ZED merceginin YERDEN yuksekligi (metre)
        #      cam_pitch_deg: kameranin asagi bakis acisi (telefon su terazisi
        #                     uygulamasi yeter; 0 = tam yatay, + = asagi)
        #    Bunlar olculunce:
        #      ros2 run ... lane_follower --ros-args -p ipm_mode:=analytic \
        #          -p cam_height_m:=<olculen> -p cam_pitch_deg:=<olculen>
        #    Dogrulama: BEV teshis goruntusunde gri dikey referanslar gercek
        #    serit cizgilerinin uzerine oturmali ve metre izgarasi tutmali.
        #
        # NOT: kayitlardan otomatik cozmeyi denedim. Kamera egimi icin iki
        # yontem (goruntudeki gokyuzu-ufuk siniri: +3.5 derece; serit
        # cizgilerinin kaybolma noktasi: +5.4 derece) asagi bakis konusunda
        # HEMFIKIR, ama birbirini tam tutmuyor. Bu tahminlerle kurulan analitik
        # IPM olculdugunde src_pts'ten DAHA KOTU cikti (sabitlik 0.40-0.88 vs
        # 1.026) -> tahminler yeterince iyi degil. Bu yuzden varsayilan
        # src_pts'te birakildi. Analitik moda gecmek icin GERCEK olcum sart.
        self.declare_parameter("ipm_mode", "src_pts")     # 'src_pts'|'analytic'
        self.declare_parameter("cam_height_m", 0.685)     # URDF cam_z (SUPHELI)
        self.declare_parameter("cam_pitch_deg", 5.0)      # asagi bakis (SUPHELI)
        # Kamera ic parametreleri, node'un calistigi olcege (640x360) indirgenmis.
        # ZED camera_info (1280x720): fx=fy=524.3, cx=651.0, cy=361.7
        self.declare_parameter("cam_fx", 262.15)
        self.declare_parameter("cam_fy", 262.15)
        self.declare_parameter("cam_cx", 325.50)
        self.declare_parameter("cam_cy", 180.85)
        # Analitik modda kusbakisinin kapsadigi zemin alani
        # bev_far_m'yi abartma: alcak bir kamerada uzak mesafeler goruntude
        # ufka cok yakin birkac satira sikisir ve BEV'de asiri buyutulup
        # bulanik cikar (h=0.685 m, 5 derece egimde 12 m ile ufuk arasi sadece
        # ~15 piksel). 8 m, fit penceresi (~5.8 m) icin fazlasiyla yeterli.
        self.declare_parameter("bev_near_m", 1.5)
        self.declare_parameter("bev_far_m", 8.0)
        self.declare_parameter("bev_half_width_m", 4.0)

        self.ipm_mode = self.get_parameter("ipm_mode").value
        if self.ipm_mode == "analytic":
            self._analitik_ipm_kur()
        else:
            self.M_ipm = cv2.getPerspectiveTransform(self.src_pts, self.dst_pts)
            self.M_ipm_inv = cv2.getPerspectiveTransform(self.dst_pts, self.src_pts)

        # BEV'de tek şerit çizgisi görülürse merkezi tahmin için yarım şerit
        # genişliği. dst_pts şeridi x in [0.20, 0.80]*img_w'ye koyuyor -> tam
        # genişlik 0.60*img_w, yarısı 0.30*img_w = 192 (img_w=640). Eskiden
        # img_w//4=160 kullanılıyordu -> tek-şerit karelerde 32 px merkez biası
        # -> integral doyup direksiyonu mihliyordu (arkadaş raporu Bug 1).
        self.half_lane_bev = int(self.img_w * 0.30)
        # ⚠️ 192 px TEORİK bir değer (dst_pts'ten türetilmiş), gerçek görüntüde
        # ölçülen değil. 2026-07-20 araç kaydında overlay'deki LaneW ~300 px
        # ölçüldü -> gerçek yarım genişlik ~150 px. Tek şerit görülen karelerde
        # 192 kullanmak merkezi ~42 px yanlış tarafa kaydırıyordu (sağ çizgi
        # görülüyorken merkez 42 px sola -> sürekli sola kırma). Bu yüzden
        # lane_w_px ölçülmüşse ONUN yarısı kullanılır (_half_lane), teorik değer
        # sadece henüz ölçüm yokken fallback.
        self.half_lane_min = int(self.img_w * 0.15)   # 96 px  (makul alt sinir)
        self.half_lane_max = int(self.img_w * 0.40)   # 256 px (makul ust sinir)

        # ================= İLERİ BAKIŞ (look-ahead) =====================
        # VİRAJDA DÖNMEME HATASININ KÖK SEBEBİ (2026-07-21 analizi).
        # Eskiden üç değer de sabitti: y_eval=0.90*H, y_min=0.55*H, ağırlık^4.
        # camera_info'dan (fx=fy=524.3, cy=361.7 @1280x720 -> node 640x360'a
        # ölçekler: fy=262, cy=181) ve src_pts'ten çıkan gerçek karşılıkları:
        #   BEV satır 342 = 1.7 m   |   BEV satır 36 = 10.3 m
        #   y_eval 0.90*H = satır 324 -> şerit merkezi araçtan sadece 2.2 m ötede
        #   y_min  0.55*H = satır 198 -> 5.8 m ötesi fit'e HİÇ girmiyor
        #   ağırlık (ys/max)^4       -> kalan pencerede en yakın satırlar ~11x
        #                               baskın, fit fiilen 1.7-2.5 m'ye kilitli
        # Sonuç: fit, aracın burnundaki TEĞETİ ölçüyor; viraj ancak araç içine
        # girdikten sonra hata üretiyor. Sayısal örnek (R=20 m viraj):
        #   2.2 m'de şerit merkezi kayması = 2.2²/(2R) = 0.12 m = ~15 BEV px
        #     -> Kp*err = 1.2 derece sapma (pratikte sıfır)
        #   4.8 m'de                       = 4.8²/(2R) = 0.58 m = ~72 BEV px
        #     -> Kp*err = 5.8 derece sapma (gerçek kırma)
        # İleri bakış aynı zamanda KARARLILIĞI artırır: yanal ofset tepkisi
        # değişmez (şeritler paralel), üstüne yönelim hatası (heading) sönümü
        # ve viraj öngörüsü eklenir — pure-pursuit'teki lookahead ile aynı etki.
        #
        # lookahead_frac : şerit merkezinin örnekleneceği BEV satırı (H çarpanı).
        #                  BÜYÜK = yakın/miyop, KÜÇÜK = uzağa bakar.
        #                  0.65 -> ~4.8 m; fit penceresinin (5.8 m) içinde kalır,
        #                  yani ekstrapolasyon değil ölçülmüş veriden okur.
        # fit_far_frac   : fit'e girecek en UZAK BEV satırı (eski sabit 0.55).
        #                  Küçültmek daha uzağı katar ama BEV'in üst bölgesi
        #                  src_pts'in dar (55 px) uzak kenarından büyütüldüğü
        #                  için gürültülüdür — 0.55 korunuyor, ihtiyaç olursa
        #                  0.45'e kadar denenebilir.
        # fit_weight_pow : ağırlık üssü. 4 -> yakın satırlar fit'i ele geçirir
        #                  ve uzağa bakmak işe yaramaz (uzatılan doğru yine
        #                  yakın teğet olur). 1 -> pencerenin tamamı katkı verir,
        #                  fit viraj boyunca bir KİRİŞ olur. 0 = ağırlıksız.
        # fit_degree     : 1 = doğru (mevcut), 2 = parabol -> eğriliği doğrudan
        #                  modeller. 2 daha iyi öngörü verir ama gürültüye
        #                  duyarlıdır; gerçek kayıtla doğrulanana kadar 1.
        self.declare_parameter("lookahead_frac", 0.65)
        self.declare_parameter("fit_far_frac", 0.45)
        self.declare_parameter("fit_weight_pow", 1.0)
        self.declare_parameter("fit_degree", 2)
        # Parabol (derece 2) ancak agirlikli RMS artigi dogrununkinin bu
        # katsayisindan KUCUKSE secilir. 1.0 = her zaman parabol (duz yolda
        # gurultuye uyar), 0.0 = asla. Olculen en iyi: 0.85 (bkz. fit_lane_poly).
        self.declare_parameter("fit_deg2_kazanc", 1.0)
        # --- FIT KABUL ESIKLERI (2026-07-21, HAM ZED kaydiyla olculdu) ------
        # pist_18_3tem'in 199 ham karesinde eski esiklerle sonuc FELAKETTI:
        #   iki serit fit %15, tek fit %28, HIC FIT YOK %57
        # Red sebepleri: cok_kisa %40, nokta<80 %30 (kabul yalnizca %27).
        # Esik taramasi (ayni kareler, ayni maskeler):
        #   far .55 / nokta 80 / span .15 -> iki fit %15.3   (ESKI)
        #   far .55 / nokta 80 / span .08 -> iki fit %33.3
        #   far .45 / nokta 25 / span .05 -> iki fit %41.0   (SECILEN)
        #   far .35 / nokta 15 / span .03 -> iki fit %43.2   (getirisi az)
        # KRITIK: olculen serit genisligi TUM ayarlarda 494-495 px kaldi ->
        # gevsetmeyle kurtarilan fitler AYNI seritler, curuk degil. Genislik
        # sacilsaydi cop kabul ediyoruz derdik; sacilmadi.
        # NOT: onceki olcumum (%55 kabul) YANILTICIYDI -- overlay karelerinde
        # uzerine cizilmis mavi/kirmizi serit cizgileri YOLO'yu besliyordu.
        # Ham kamera karesinde gercek oran cok daha dusuk.
        self.declare_parameter("fit_min_points", 25)      # eski sabit: 80
        # 0.05 -> 0.03 (2026-08-18, serit_v2 ile olculdu): yeni model daha
        # ince/kesikli maske uretiyor, eski 0.05 satir-yayilim esigi gecerli
        # cizgileri reddediyordu. Tutulan test bolunmesinde 2-fit %48.7 -> %53.8,
        # fit RMS DEGISMEDI (18.2 px) -> bedelsiz kazanc.
        self.declare_parameter("fit_min_span_frac", 0.03)  # eski sabit: 0.15
        # Egim kilavuzu: bkz. fit_lane_poly icindeki ayrintili olcum notu.
        # Eski sabit 1.0 virajda gecerli fitleri eliyordu (tek-fit karelerinin
        # %81.5'i bu kurala takiliyordu).
        # 3.0 -> 5.0 (2026-08-21). Red-sebep etiketlemesi EGIM_REDDI'nin
        # karelerin %8.7'sini yediğini gosterdi. Tarama (joystick_46):
        #   esik  kor kare  EGIM_REDDI  kilit<80  der/sn
        #   3.0     18.3%      8.7%       0.3%     6.0
        #   5.0     12.3%      2.8%       0.2%     6.6   <- secilen
        #   7.0     11.5%      1.7%       0.2%     6.9
        # Kor kare orani UCTE BIR azaliyor, kilitlenme bozulmuyor.
        # ESKI GEREKCENIN KUSURU: 3.0, "5.6 m viraj yaricapi" diye
        # secilmisti (arac 3.4 m'yi alabiliyor). Ama y_eval'deki egim yalniz
        # YOL EGRILIGI degil, ARACIN SERIDE GORE ACISI da. Arac yalpaladiginda
        # (bu kayitta bilerek yapiliyor) egim buyur ve mesru gozlem atilir.
        # 7.0 az daha kazandiriyor ama gurultuye kapi aciyor; 5.0 orta yol.
        self.declare_parameter("fit_max_slope", 5.0)      # eski sabit: 1.0
        self.fit_max_slope = float(self.get_parameter("fit_max_slope").value)
        self.fit_deg2_kazanc = float(
            self.get_parameter("fit_deg2_kazanc").value)
        self.fit_min_points = int(self.get_parameter("fit_min_points").value)
        self.fit_min_span_frac = float(
            self.get_parameter("fit_min_span_frac").value)

        # --- YON ONIZLEMESI (heading feedforward) ---------------------------
        # Sadece konum hatasina bakan bir kontrolcu viraja GIRDIKTEN SONRA
        # tepki verir. Aracta gozlenen belirti: sag viraja girerken direksiyon
        # once notr/hafif sol kaliyor, ancak hata 80+ px'e ciktiginda saga
        # kiriyordu. Seridin y_eval'deki EGIMI virajin basladigini hata
        # buyumeden haber verir; onu hataya katiyoruz (bkz. cb icindeki kullanim).
        # 0 = kapali (eski davranis).
        # heading_gain 30.0 -> 75.0 (2026-08-20). BU TERIM Kp ILE CARPIM
        # HALINDE CALISIR: hataya katiliyor, sonra cikis Kp ile carpiliyor.
        # 30 degeri Kp=0.08 ve steer_target_gain=-0.75 gecerliyken ayarlanmisti;
        # o zamanki carpim Kp*hg = 2.4. Bugun Kp 0.08->0.02 oldu ve hg
        # yukseltilmedi -> carpim 0.6'ya dustu, yani viraj onizlemesi sessizce
        # 4 KAT ZAYIFLADI. Ayrica donusum kazanci -0.75 -> -1.20 oldu (ayni FSM
        # birimi artik %60 daha cok teker acisi).
        # Ayni FIZIKSEL davranis icin: 2.4 / (1.20/0.75) / 0.02 = 75.
        # Buyukluk kontrolu (BEV anizotropisi 3.54x dahil): egim 1.0 = gercek
        # yon hatasi 15.8 derece; hg=30 ile katki 0.96 derece (gerekenin ~1/16'si),
        # hg=75 ile 2.4 derece. Hala muhafazakar, ama ayarlandigi noktaya donuyor.
        # !!! Bu deger HIC gercek veriyle olculmedi -- Kd ve Ki gibi. Slalom
        # kaydinda seride donus fazlari varsa ucu birden ayni regresyonla olculur.
        # Aractaki ilk kosuda virajda asiri donme gorulurse: -p heading_gain:=45
        # ---- SERIT CIFTI GECERLILIK KAPISI (2026-08-20) ----
        # Eskiden tek kapi "w_px > 80" idi: 80 px'ten genis HER fit cifti
        # "serit" sayiliyordu. Gercek olcum (pist_18_3tem ham ZED, 978 iki-fit
        # karesi): genisligin %11'i 350 px'in ALTINDA, medyan 456. Dar
        # ciftlerde hesaplanan merkez sol fitten ortalama 68 px uzakta --
        # saglikli yarim serit 228 px olduguna gore merkez pratikte
        # CIZGININ USTUNDE. Sonuc: arac bir serit CIZGISINI serit ortasi
        # sanip ona ortalaniyor (aracta gozlenen sikayet buydu; 15:27
        # ekran kaydinda LaneW 96 ve 207 px olcen kareler var).
        # Neden olusuyor: sol/sag ayrimi BEV goruntu merkezine gore yapiliyor
        # (mid-+70). Arac yarim seritten fazla kayinca kendi seridinin SAG
        # cizgisi goruntude merkezin SOLUNA duser ve "sol serit" saniliyor;
        # yanindaki bariyer tabani da "sag serit" oluyor -> 96 px'lik sahte
        # serit. Kapi bunu reddeder, taraf atamasi sureklilikle duzeltilir.
        # ---- SERIT SECIMI (2026-08-20) ----
        # "birlestir": eski yol -- combine_masks TUM YOLO orneklerini tek
        #   maskeye OR'lar, sonra BEV goruntu merkezine gore (mid-+70) ikiye
        #   boler. Uc cizgi gorunurken (bizim sol, bizim sag, bariyer kenari)
        #   hangi ikisinin serit oldugu SECILEMEZ; ayrim konuma kalir ve arac
        #   kaydiginda yanlis cifti secer -- "araci bir cizgiye ortaliyor"
        #   sikayetinin kok sebebi budur.
        # "ornek": her YOLO ORNEGI ayri fitlenir (segmentasyon bunu zaten
        #   veriyor, eskiden atiliyordu), sonra aday cizgiler arasindan
        #   GENISLIGI serit olan ve merkezi surekliliğe en yakin CIFT secilir.
        # Ayni FIZIKSEL cizginin parcalarini birlestirme toleransi (BEV px).
        # YOLO kesikli seridi birden cok ornege boluyor (olculdu, joystick_46:
        # kare basina medyan 8 maske ama tek tek yalnizca 2'si fit veriyor;
        # karelerin %11.5'inde maske VAR ama hic fit YOK -> overlay bayat
        # cizgi gosteriyor, "cizgi:0"). Dash'ler birlestirilmeli, AYRI cizgiler
        # ayri kalmali. 100 px: iki farkli serit cizgisi ~450 px ayri oldugundan
        # guvenli, dash hizalama hatasini yutacak kadar genis.
        # 0 = KAPALI (varsayilan). Gruplama DENENDI ve OLCUMLE REDDEDILDI
        # (joystick_46, 1019 kare): her toleransta taze cift orani dustu
        # (%77.1 -> %62.7..%69.1) ve "hic taze aday yok" orani %11.5'ten
        # duzelmedi (%11.9..%12.1). Yani fit veremeyen maskeler kesikli
        # cizginin parcalari DEGIL, tek baslarina cok kucuk olanlar; onlari
        # birlestirmek kurtarmiyor, iyi fitleri kirletiyor.
        #   tol=40 -> cift %69.1 kilit %5.1 | tol=80 -> %67.9 / %2.0
        #   tol=100 -> %66.0 / %3.1        | KAPALI -> %77.1 / %3.9
        # BARIYER ELEMESI: bir aday "serit cizgisi"nin noktalarinin bu
        # oraninden fazlasi bariyer maskesinin icine dusuyorsa o aday
        # serit degil, bariyerin dibindeki hattir -> elenir. 0 = kapali.
        # Bu, genislik kapisinin YAKALAYAMADIGI vakayi kapatir: 332 px'lik
        # bir cift makul genislikte gorunur (baska bir kayitta medyan 358 px
        # olculdu) ama fitler bariyerin uzerindeyse serit degildir.
        # Olculdu (joystick_46): kapali %4.4 kilit | 0.25 -> %3.1 | 0.35 -> %3.2
        # | 0.50 -> %3.2. Bayat kare orani ve sicrama hicbirinde degismedi,
        # yani eleme bedelsiz. 0.25 secildi.
        # ---- EKSTRAPOLASYON KAPISI (2026-08-21) ----
        # fit_lane_poly, verinin ULASMADIGI satirlara kadar polinomu
        # uzatiyordu. Olculdu (joystick_46 viraj bolumu, 1186 fit):
        #   y_eval veri araliginda      %55.4
        #   EKSTRAPOLASYON              %44.6  (medyan 53, maks 95 satir)
        #   bunlarin %26'si DERECE-2 -> parabol savruluyor
        #   degerlendirmelerin %8.7'si goruntu DISINDA (x<0 veya >640)
        # Ekranda gorulen "mavi cizgi kocaman kivrilip geri donuyor" bu.
        # Sola virajda sol serit gorus alanindan cikiyor, geriye yalnizca
        # yakin alan noktalari kaliyor ve parabol 4.8 m'ye uzatilinca
        # uyduruyor. Cozum: uzagi kesmek -- o zaman kod dogal olarak tek
        # serit + olculen yarim serit yoluna duser (dogru davranis).
        # ---- PATH YASI / GUVENI (PDF onerisi, 2026-08-21) ----
        # Taze merkez uretilemedigi karelerde eski path'i KORU ama guvenini
        # dusur: yas buyudukce direksiyon komutu notre (45) dogru soner.
        # Boylece kisa algilama bosluklari (1-2 kare) sorunsuz koprulenir,
        # UZUN kayipta arac kendini eski, artik gecersiz bir yola kilitlemez.
        # "Tahmin mekanizmasi sinirsiz kullanilmamalidir" (PDF, guvenlik notu).
        # ---- ADAPTIF ILERI BAKIS (2026-08-21) ----
        # Virajda sol serit gorus alanindan cikinca fitin verisi y_eval'e
        # ULASMIYOR. Ekstrapolasyon kapisi bunu dogru sekilde reddediyor, ama
        # o zaman olcum HIC kalmiyor ve arac notre dusuyor -- virajda notr
        # gitmek pistten cikmaktir. Dogrusu: uzagi UYDURMAK yerine verinin
        # DESTEKLEDIGI en uzak satirda olcmek. Virajda daha az ileri gorursun;
        # bu normaldir, olcumu kaybetmek degil.
        # Etkin satir asla y_eval'den YAKIN olamaz diye bir sinir yok; ama
        # asagidaki alt sinir (adaptif_min_m) cok yakina inip gurultuye
        # kilitlenmeyi onler.
        # ---- CIFT ICIN IKI TARAF DA TAZE OLMALI (2026-08-21) ----
        # Olculdu (joystick_46, 2718 kare): tek taze aday bulunan karelerin
        # %66.7'sinde yine de "gecerli cift" olusuyordu -- cunku taze cizgi
        # ONCEKI kareden kalan bayat fitle eslestiriliyor ve genislik kapisi
        # bunu kabul ediyor (bayat cizgi bir kare once gecerliydi). Sonucu:
        # aday=1 karelerde |Yanal| medyani 172 px (aday>=2'de 81-88 px),
        # %90'i 340 px = 1.5 yarim serit. Kare 1204'teki "mavi+sari+kirmizi
        # bariyere yigilmis" goruntusu budur.
        # Bayat + taze karisimi bir OLCUM degildir: arac o kareden beri
        # hareket etti, bayat cizgi artik baska bir yerde.
        self.declare_parameter("cift_ikisi_de_taze", True)
        self.cift_ikisi_de_taze = bool(
            self.get_parameter("cift_ikisi_de_taze").value)
        # ---- TEK ADAYDA TARAF KARARININ CIPASI (2026-08-21) ----
        # ESKI KURAL (sureklilik): "bu benim sol cizgim mi sag cizgim mi"
        # sorusu _son_lane_x'e, yani BIR ONCEKI KARENIN AYNI HESABININ
        # CIKTISINA sorulyordu. Fiziksel cipa yok -> SINIRSIZ POZITIF GERI
        # BESLEME: merkez biraz kayinca kayan merkez bir sonraki karede tarafi
        # teyit ediyor, merkez daha da kayiyor.
        # OLCULDU (joystick_46, 4077 kare, tek-aday karesi %32.3):
        #   |yanal hata| > yarim serit  : 696 kare (%17.1)
        #   > 1.5 yarim serit           : 376 kare (%9.2)
        #   maks                        : 501 px = 3.3 m (bir serit genisliginden fazla)
        #   >=5 kare suren kacis epizodu: 12 adet, en uzunu 172 kare (~11.5 s)
        # Kullanicinin sikayet ettigi iki kare (1208 "yanlis", 1363 "dogru")
        # AYNI mekanizmanin iki isaretidir: 1194-1242 (SOL, maks 379 px) ve
        # 1361-1442 (SAG, maks 380 px). Yani ucuncu kare "saglam kaldi" degil,
        # kacis sadece bariyerden UZAGA dogruydu.
        # YENI KURAL (eksen): cipa ARAC EKSENI -- sabit ve fiziksel. Serit
        # merkezi tanimi geregi eksenin ~yarim serit yakininda olmalidir
        # (olculdu: gecerli cift olan karelerde |merkez-eksen| medyani 86 px,
        # yarim seridi asma orani %0.9). Merkezi eksene EN YAKIN yapan hipotez
        # secilir; bu, cebirsel olarak "ref >= x ise sol" demektir ve onceki
        # tahmine HIC bakmadigi icin geri besleme dongusu kurulamaz.
        # Sureklilik yalnizca BELIRSIZ BANTTA (|x-ref| < taraf_bant_px) devreye
        # girer -- orada iki hipotez de merkezi esit uzakliga koyar, yani
        # geometrinin bilgisi yoktur.
        # ⚠️ VARSAYILAN 'sureklilik'e GERI ALINDI (2026-08-21 aksami). 'eksen'
        # kacisi bitiriyor ama SOL VIRAJDA gerileme uretiyor: bagimsiz referansla
        # (surucunun gercek direksiyonu, /beemobs/FeedbackSteeringAngle -- serit
        # boru hattina hic dokunmayan sinyal) olculdu, tek-aday karelerinde
        # surucuyle isaret uyumu sol virajda %73.1 -> %40.5'e DUSUYOR.
        # Operator de bunu gozle gordu ("viraji donerken disari cikiyor").
        # Lehine olan tum sayilar |merkez - arac ekseni| turevi bir olcutten
        # geliyordu; o olcut virajda DOGRU davranisi cezalandirdigi icin kendi
        # degisikligini kayiran bir olcuttu. Ayrintili dokum CLAUDE.md'de.
        self.declare_parameter("taraf_kural", "sureklilik")  # 'eksen'|'sureklilik'
        self.taraf_kural = str(self.get_parameter("taraf_kural").value)
        self.declare_parameter("taraf_bant_px", 40.0)
        self.taraf_bant_px = float(self.get_parameter("taraf_bant_px").value)
        # ---- TARAF HISTEREZISI: DENENDI ve OLCUMLE REDDEDILDI (varsayilan 0) ----
        # Hipotez: 'eksen' kurali zayif kanitla taraf degistirmeye acik --
        # donme 8 -> 20 cikti ve her donme merkezi 2*yarim serit (~470 px)
        # ziplattigi icin direksiyonda medyan 27 birimlik sicrama uretiyor.
        # Cozum olarak tarafi DEGISTIRMEK icin daha fazla kanit istendi
        # (bant + taraf_hist_px = 40+60 px).
        # OLCULDU (joystick_46, 4077 kare) -- hicbir sey kazandirmadi:
        #   ayar                | |lat|ort  %90  maks  >yari  std   >10br  donme
        #   eksen (hist=0)      |    90.1  173   290   %1.7  8.50     72     20
        #   eksen + hist 60px   |    95.0  193   344   %5.2  8.56     75     13
        # Donme SAYISI dustu (20->13) ama SICRAMA BUYUKLUGU degismedi
        # (medyan 27 ikisinde de) ve toplam direksiyon aktivitesi ayni kaldi
        # (std 8.50 vs 8.56, >10 birim 72 vs 75). Buna karsilik yanal hata
        # her dilimde bozuldu ve en uzun kacis 11 -> 48 kareye cikti.
        # Yani histerezis gecikmeyi geri getiriyor, titremeyi ise cozmuyor.
        # AYRICA denenip reddedildi: "belirsiz kare"yi tamamen reddetmek
        # (iki hipotez de merkezi eksenden > esik uzaga koyuyorsa olcum alma).
        # Donmelerin hepsi |x-ref| ~ 43 px'te, yani yarim serit 235 iken iki
        # hipotez de kotu (192 ve 278 px). Ama bunlari elemek icin tek-aday
        # karelerinin %27-37'sini atmak gerekiyor ve TOPLAM kor kare orani
        # %9.0 -> %17.7-21.0'a cikiyor; beynin ZAYIF/KAYIP fallback'i aracı
        # surekli yavaslatirdi. Ustelik donmeler TITREME DEGIL DUZELTME:
        # her donmede |lat| ~270'ten ~190'a DUSUYOR (salinim orani 4/19).
        # Ikisi de kod olarak durmuyor; tekrar denenmesin diye burada yaziyor.
        self.declare_parameter("taraf_hist_px", 0.0)
        self.taraf_hist_px = float(self.get_parameter("taraf_hist_px").value)
        self.declare_parameter("taraf_hist_s", 0.5)
        self.taraf_hist_s = float(self.get_parameter("taraf_hist_s").value)
        self._son_taraf = None       # en son karar (True=sol)
        self._son_taraf_t = 0.0      # o kararin zamani
        self.declare_parameter("adaptif_lookahead", True)
# 3.5 m secildi (joystick_46, tum kayit, gercek goruntu):
        #   ayar     kisalan  x disari  steer std  |sapma|>15  kilit<80  der/sn
        #   KAPALI     0.0%     370       6.6        6.5%       6.0%      3.6
        #   2.2       39.1%     168      10.4       14.6%       1.7%      8.3
        #   3.0       30.1%      51       9.0       12.1%       1.3%      6.2
        #   3.5       14.4%      40       7.9       10.2%       1.3%      5.4  <-
        # Kilitlenme 4.6 kat, fiziksel olarak imkansiz fit 9 kat azaliyor;
        # direksiyon hizi 5.4 der/sn ile aktuator limitinin (25) cok altinda.
        # Daha kucuk deger ileri bakisi fazla kisaltiyor -> saf takip
        # delta = atan(2L sin(alpha)/Ld) oldugundan Ld kuculunce sertlesiyor.
        # ⚠️ MASA SIMULATORU BUNU TEST EDEMEZ: sentetik maskeler her zaman tum
        # satir araligini kapliyor, adaptif hic tetiklenmiyor (5 ayarda da
        # birebir ayni sonuc). Bu parametre yalniz gercek kayitla ayarlanir.
# 2.8 m (2026-08-21, HAYALET HATA duzeltmesinden SONRA yeniden secildi).
        # Ilk secim 3.5'ti; duzeltme, o esikte karelerin %26.1'inin hic
        # guvenilir olcum almadigini gorunur yapti (arac dortte bir sure
        # sureklilikle gidiyordu). Yeniden tarama (joystick_46, tum kayit):
        #   esik   olcum yok  kilit<80  der/sn  Yanal std
        #   kapali    0.0%      6.0%     3.6      111
        #   2.5       4.4%      1.2%     7.3      148
        #   2.8       8.3%      1.2%     6.3      133   <- secilen
        #   3.0      10.1%      1.3%     5.9      133
        #   3.5      26.1%      1.4%     5.1      129
        # Kilitlenme faydasi HER esikte ayni (%1.2-1.4); fark yalnizca kac
        # karede kor kalindigi. 2.8 kor kareyi 3 kat azaltiyor, direksiyon
        # 6.3 der/sn ile aktuator limitinin (25) hala cok altinda. 2.5 kor
        # kareyi biraz daha azaltiyor ama Yanal dagilimi 148'e bozuluyor.
        self.declare_parameter("adaptif_min_m", 2.8)
        self.adaptif_lookahead = bool(self.get_parameter("adaptif_lookahead").value)
        self.adaptif_min_m = float(self.get_parameter("adaptif_min_m").value)
        # ---- SERIT GUVENI -> KARAR BEYNI (2026-08-21, PDF onerisi) ----
        # ID-2 sozlesmesi genisledi: "2,<steer>" -> "2,<steer>,<guven>,<yas_s>,<durum>"
        # Eski ayristiricilar data[1]'i okumaya devam eder, bozulmaz.
        # durum: TAZE (taze olcum) | TAHMIN (kisa kayip, son path suruluyor)
        #      | ZAYIF (uzayan kayip, hiz dusurulmeli) | KAYIP (guvenilmez)
        # Gerekce (olculdu, joystick_46, hareket halinde): karelerin %22'sinde
        # guvenilir olcum yok; 14 kesinti 0.7 s'den uzun, en uzunu 13.1 s ~ 20 m.
        # Eski davranis: guven sifirlaninca direksiyon notre soner ve arac
        # SURMEYE DEVAM eder. Duz yolda zararsiz, VIRAJDA pist disi.
        # Artik beyin bunu goruyor ve hizi kisabiliyor.
        self.declare_parameter("guven_zayif_s", 0.30)   # bundan sonra ZAYIF
        self.declare_parameter("guven_kayip_s", 1.00)   # bundan sonra KAYIP
        self.guven_zayif_s = float(self.get_parameter("guven_zayif_s").value)
        self.guven_kayip_s = float(self.get_parameter("guven_kayip_s").value)
        self.declare_parameter("path_max_age", 10)    # 0 = sonum tamamen kapali
        # Bayat yolun ALT yetki siniri. 0.0 eski davranistir (tam sifirlama) --
        # olculdu ve virajda araci pist disina birakiyor, bkz. _path_guven.
        # 0.4 baslangic degeridir: beyin ayni anda hizi 4 -> 2 km/h'ye kisip
        # 3 s sonra durduruyor, yani azaltilmis yetki azaltilmis hizla eslesiyor.
        # ⚠️ ARACTA DOGRULANMADI; kapali cevrim gerektirir.
        self.declare_parameter("guven_taban", 0.4)
        self.guven_taban = float(self.get_parameter("guven_taban").value)
        self.path_max_age = int(self.get_parameter("path_max_age").value)
        self.declare_parameter("fit_extrap_max_row", 55)    # bundan otesi RED
        self.declare_parameter("fit_extrap_deg1_row", 20)   # bundan otesi derece-1
        self.fit_extrap_max_row = int(self.get_parameter("fit_extrap_max_row").value)
        self.fit_extrap_deg1_row = int(self.get_parameter("fit_extrap_deg1_row").value)
        self.declare_parameter("bariyer_ele_oran", 0.25)
        self.declare_parameter("bariyer_genislet_px", 12)
        self.bariyer_ele_oran = float(self.get_parameter("bariyer_ele_oran").value)
        self.bariyer_genislet_px = int(self.get_parameter("bariyer_genislet_px").value)
        self.declare_parameter("serit_grup_tol", 0.0)
        self.serit_grup_tol = float(self.get_parameter("serit_grup_tol").value)
        # ---- SAG SERIT KURALI (24.08.2026) ----
        # SORUN: planner donusu yalnizca YAW uzerinde kapali cevrim; cikistaki
        # YANAL konum kontrol edilmiyor (tk_0822'de cikis yon hatasi -7.5 ve
        # -14.7 derece olculdu; tek basina -14.7, 8.2 m'de 1.05 m yanal kayma
        # demek, serit ~3 m). Arac donusten sol seritte cikabiliyor ve serit
        # takipcisi onu orada TUTUYOR -- cunku cift_sec "merkezi _son_lane_x'e
        # en yakin cifti", yani icinde bulundugun seridi seciyor.
        # COZUM: ayri bir manevra durumu YAZILMADI. Kural degisti: solunda
        # KESIK, saginda DUZ cizgi olan ciftler yeglenir, aralarindan EN
        # SAGDAKI secilir. Sol seritteyken bu, hedefi sag seride kaydirir ve
        # MEVCUT PID araci kendiliginde sag serite tasir.
        # KANIT: 200 gercek ZED karesinde olculdu (asama_full) --
        #   kesik cizgi 5 206 piksel / 2.87 parca, duz cizgi 19 606 px / 1.62
        #   parca, yani 3.8 KAT fark. Ayrim guvenilir.
        # ⚠️ Kanit yoksa (hicbir cift kesik-sol degilse) ESKI kural aynen
        # calisir; iki cizgi goruluyorsa (tek serit) zaten tek gecerli cift
        # vardir ve davranis birebir degismez.
        self.declare_parameter("sag_serit", False)
        self.sag_serit = bool(self.get_parameter("sag_serit").value)
        # sag/sol piksel orani: sag cizgi solun bu kati kadar dolgunsa sol
        # cizgi KESIK sayilir. Olculen oran 3.8; 2.0 muhafazakar esik.
        self.declare_parameter("sag_serit_kesik_oran", 2.0)
        self.sag_serit_kesik_oran = float(
            self.get_parameter("sag_serit_kesik_oran").value)
        # Bu kadar pikselden buyuk hedef sicramasi = SERIT DEGISTIRME sayilir
        # ve hiz sinirina tabi olur. Altindaki normal takip hic etkilenmez.
        self.declare_parameter("sag_serit_esik_px", 150.0)
        self.sag_serit_esik_px = float(
            self.get_parameter("sag_serit_esik_px").value)
        # Gecise baslamadan once kac ardisik kare ayni yonu gostermeli
        # (~10 kare = 0.5 s). Tek karelik yanlis algi araci kaydirmasin.
        self.declare_parameter("sag_serit_teyit", 10)
        self.sag_serit_teyit = int(self.get_parameter("sag_serit_teyit").value)
        # Hedefin kayma hizi (BEV px/s). 466 px ~ 3.0 m serit, yani 60 px/s
        # ~ 0.39 m/s yanal: 3 m'lik gecis ~8 s / ~8 m yol. Sinirsiz birakilirsa
        # hedef bir karede 466 px atlar -> Kp 0.03 ile 14 birim direksiyon,
        # ham 20, teker ~20 derece (R~5 m): arac savrulur, ustelik direksiyon
        # 10 birim/s ile zaten yetisemez.
        self.declare_parameter("sag_serit_px_s", 60.0)
        self.sag_serit_px_s = float(self.get_parameter("sag_serit_px_s").value)
        if self.sag_serit and self.serit_grup_tol <= 0.0:
            self.get_logger().warn(
                "sag_serit ACIK ama serit_grup_tol=0 (gruplama KAPALI): kesik "
                "cizginin her parcasi ayri aday oluyor, 'bu cizgi kesik mi' "
                "sorusu guvenilir sorulamaz. -p serit_grup_tol:=100.0 ile "
                "birlikte kullanin.")
        self.declare_parameter("serit_secim", "ornek")
        self.serit_secim = str(self.get_parameter("serit_secim").value).lower()
        self.declare_parameter("lane_w_min_px", 300.0)
        self.declare_parameter("lane_w_max_px", 600.0)
        # olculmus genislik oturduktan sonra izin verilen sapma (orani)
        # PARALELLIK TOLERANSI (2026-08-21). Genislik kapisi TEK satirda
        # (y_eval) bakiyor ve bariyere oturan capraz fiti goremiyor: 1526'da
        # LaneW 329-399 px, yani makul bandin tam ortasi. Dogru bir IPM'de
        # serit cizgileri PARALELDIR -- genislik satirdan satira degismez.
        # Sentetik dogrulama: dikey cift %0.0, ayni egimli viraj %0.0,
        # %3.8 egim farki KABUL; bariyer egim 0.87 -> %27.7 RED, 2.0 -> %64.3.
        # NOT: 794 gercek karede (4 veri seti) hic atesledi -- 1526'nin cifti
        # *paralel ama egik*ti; bu kapi IRAKSAYAN cifti yakalar. Zararsiz
        # emniyet agi, "1526'yi cozer" diye sayilmamali. 0 = kapali.
        self.declare_parameter("cift_paralel_tol", 0.25)
        self.declare_parameter("lane_w_tol", 0.25)
        self.lane_w_min_px = float(self.get_parameter("lane_w_min_px").value)
        self.lane_w_max_px = float(self.get_parameter("lane_w_max_px").value)
        self.lane_w_tol = float(self.get_parameter("lane_w_tol").value)
        self.cift_paralel_tol = float(
            self.get_parameter("cift_paralel_tol").value)
        # ---- DIREKSIYON YASASI (2026-08-20) ----
        # "pid"     : eski davranis -- y_eval satirindaki TEK yanal hata x Kp.
        #             Viraj yalnizca heading_gain terimiyle sizabiliyor.
        # "pursuit" : SAF TAKIP (pure pursuit). Serit ORTA CIZGISI uzerinde
        #             pp_lookahead_m ilerideki noktaya varacak teker acisini
        #             bisiklet geometrisiyle hesaplar:
        #                 delta = atan( 2*L*sin(alpha) / Ld )
        #             L = dingil mesafesi, alpha = hedefe olan aci, Ld = hedefe
        #             olan mesafe. Cikisi GERCEK bir teker acisidir (radyan),
        #             piksel-hatasi degil; viraj dogal olarak islenir cunku
        #             hedef nokta zaten egrinin uzerindedir.
        # Stanley YERINE saf takip secildi: Stanley'in yanal terimi
        # atan(k*e/v) ile HIZA bolunur, bu dugumde hiz bilgisi YOK (hiz geri
        # beslemesi kontrol dugumunde). Saf takip yalnizca geometri ister;
        # dingil mesafesi (1.86 m) dokumandan kesin biliniyor.
# VARSAYILAN "pursuit" (2026-08-20). Masa kapali cevriminde PID uc hizin
        # IKISINDE seritten tasiyor (3.2 ve 7.2 km/h), saf takip UCUNDE de
        # seritte kaliyor; maks yanal hata 1.46-1.56 m -> 1.01 m. Gercek
        # goruntude direksiyon hizi 25 der/sn = aktuator limitinde (PID 19).
        # ARACTA HIC KOSMADI: ilk deneme dusuk hizda, bos alanda, surucu
        # frende yapilmali. Geri donus: -p steer_mode:=pid (derleme gerekmez).
        self.declare_parameter("steer_mode", "pid")
        # Ld SECIMI (2026-08-20, SON olcum -- onceki tablo birim hatasiyla
        # yazilmisti, bkz. asagi). Masa kapali cevrimi (uc hiz) + gercek
        # goruntude (joystick_46) direksiyon hizi:
        #   yasa            masa maks   3 hizda   der/sn   kilit<80
        #   PID                 1.51 m     2/3       3.1     %3.4
        #   saf takip Ld=4.0    0.77 m     3/3       5.6     %3.4
        #   saf takip Ld=4.8    0.87 m     3/3       4.4     %3.4   <- secilen
        #   saf takip Ld=5.5    0.98 m     3/3       4.1     %3.4
        # 4.8 secildi: 4.0'a gore takip hatasi 0.10 m kotu ama direksiyon
        # aktivitesi %21 dusuk, ve hedef nokta tam y_eval satirinda (fitin
        # olculdugu, en guvenilir yer) -- ekstrapolasyon yok.
        # ⚠️ BIRIM HATASI DERSI: onceki tabloda "32 der/sn, aktuator limitini
        # asiyor" yazip Ld=4.8'i elemistim. Kare ATLAYARAK ornekleyip
        # (her 8. kare, 0.29 s ara) farki KOMSU kare sanip 30 ile carpmisim;
        # gercek hiz ~8.5 kat dusuk. Dogru hesap: |dsteer| / (atla/28 Hz).
        # Tum yasalar 3-6 der/sn ile aktuator limitinin (25) cok altinda,
        # yani o kisit hic baglayici degil.
        # Ld 6.79 m'yi ASMAMALI: fit bolgesi (fit_far_frac) orada bitiyor,
        # otesi ekstrapolasyon -> Ld=6.0/6.5 kapali cevrimde 3/3 KAYBEDIYOR
        # (maks 1.55/1.70 m).
        self.declare_parameter("pp_lookahead_m", 4.8)
        self.declare_parameter("wheelbase_m", 1.86)
        # FSM biriminde 1 birim kac derece teker acisi eder.
        # neuravix_control_node_real: steer_target_gain=-1.20 (FSM->ham),
        # olculen ham->teker 0.824 deg/ham -> 1 FSM birimi = 0.99 derece.
        self.declare_parameter("pp_deg_per_unit", 0.99)
        self.steer_mode = str(self.get_parameter("steer_mode").value).lower()
        self.pp_lookahead_m = float(self.get_parameter("pp_lookahead_m").value)
        self.wheelbase_m = float(self.get_parameter("wheelbase_m").value)
        self.pp_deg_per_unit = float(self.get_parameter("pp_deg_per_unit").value)
        self.declare_parameter("heading_gain", 75.0)
        # YON TERIMI DOYUMU (px). Terim -heading_gain*egim'dir ve egim
        # fit_max_slope'a (3.0) kadar kabul edilir -> hg=75'te 225 px, yani
        # BEV yari seridinden (~222 px) BUYUK: TEK bir kotu fit tam serit
        # genisligi kadar direksiyon komut eder. Kapali cevrim taramasi bu
        # bolgeyi hic gormedi (sentetik pistte |egim| medyan 0.74, maks 1.34
        # -> hg=75'te en fazla 101 px). Sinir 110: taranan her seyi aynen
        # gecirir (101 < 110), patolojik olani keser. 0 = sinirsiz.
        # DEGER GERCEK GORUNTUDEN (pist_18_3tem, 1217 kare, hg=75):
        #   medyan 27 | %90 96 | %95 118 | %99 187 | maks 221 px
        #   sinir 110 -> %6.3 doyuyor (COK: mesru viraj bilgisi kirpiliyor)
        #   sinir 150 -> %2.5      <- secilen
        #   sinir 200 -> %0.5
        # 110 ilk olarak SENTETIK pistten secilmisti (orada maks 101 px);
        # sentetik maskede algi gurultusu yok, kuyruk gercekte cok daha agir.
        # 150, taramanin gordugu her seyi (101) ve normal virajlari (%95=118)
        # gecirir, yalnizca ust %2.5'i -- kotu fitlerin yasadigi bolgeyi -- keser.
        # Yarim serit ~218 px oldugundan tek bir kotu fit hala tam serit
        # genisligi komut edemez.
        self.declare_parameter("heading_max_px", 150.0)
        # YON TERIMI HATANIN ISARETINI CEVIREMESIN (2026-08-22, dort gercek
        # kayitta olculdu: joystick_46/47/48 ham ZED + slalom_0821_1526).
        # heading_gain=75 ile yon terimi olculen yanal hatadan buyuk olabiliyor
        # ve toplam hatanin ISARETINI ceviriyor -- arac olculen sapmanin
        # TERSINE kiriliyor. Oran %4 / %9 / %2 / %35. Bu kapi yon terimini
        # "hatayi sifira kadar kucultebilir ama oteye gecemez" ile sinirlar:
        # yanal 0 iken tam ongoru serbest, yanal buyudukce sadece yumusatir.
        # Olculdu: isaret cevirme 8/17/3/69 -> 0, ongoru %90-98 korunuyor,
        # TAZE degismiyor, oynaklik +%3-6. (heading_gain:=0 da cevirmeyi
        # bitiriyor ama ongoruyu TAMAMEN atiyor.)
        self.declare_parameter("heading_no_flip", True)
        self.heading_gain = float(self.get_parameter("heading_gain").value)
        self.heading_max_px = float(self.get_parameter("heading_max_px").value)
        self.heading_no_flip = bool(
            self.get_parameter("heading_no_flip").value)
        self.lookahead_frac = float(self.get_parameter("lookahead_frac").value)
        self.fit_far_frac = float(self.get_parameter("fit_far_frac").value)
        self.fit_weight_pow = float(self.get_parameter("fit_weight_pow").value)
        self.fit_degree = int(self.get_parameter("fit_degree").value)
        self.lookahead_frac = max(0.30, min(0.95, self.lookahead_frac))
        self.fit_degree = 2 if self.fit_degree == 2 else 1
        self.y_eval = int(self.img_h * self.lookahead_frac)

        # Prev polynomials
        self.left_prev = None
        self.right_prev = None

        # Serit kaybi sayaci: model ust uste bu kadar frame hic maske
        # bulamazsa bayat left/right fitler ve PID sifirlanir, notr (45)
        # yayinlanir. 2026-07-12 arac testi: kapali alanda model 53k frame
        # boyunca 0 maske buldu ama node tek bir yanlis tespitin bayat
        # fitiyle + PID windup'iyla surekli 15/75 uclarinda aci yayinladi.
        self.declare_parameter("lane_lost_frames", 15)
        self.lane_lost_frames = int(self.get_parameter("lane_lost_frames").value)
        self.miss_count = 0
        self.lane_lost = False

        # PID
        self.pid = PIDController()
        # Kp ARTIK PARAMETRELI (2026-08-19). Eskiden sinifta sabit yaziliydi,
        # aracta ayarlamak icin kaynagi duzenleyip yeniden derlemek gerekiyordu.
        # Direksiyon kazanci sahada ayarlanmasi en muhtemel degerdir; yarista
        # colcon build yapacak zaman yok. Kullanim:
        #   ros2 run neuravix_ros2 lane_follower --ros-args -p steer_kp:=0.005
        # Kapali cevrim taramasinin ozeti icin PIDController'daki nota bakin.
        # Kd de parametreli: sonumleme sahada ayarlanacak ikinci degerdir.
        #   ros2 run neuravix_ros2 lane_follower --ros-args -p steer_kd:=0.2
        # Guven agirligi doyum noktasi (piksel). 0 = kapali.
        #   ros2 run neuravix_ros2 lane_follower --ros-args -p fit_confidence_px:=0
        # dynamic_typing: kullanici "-p fit_confidence_px:=800" yazinca ROS bunu
        # INTEGER olarak gonderiyor ve DOUBLE tanimli parametre node'u COKERTIYOR.
        # Yaris gununde bu kabul edilemez bir tuzak -> her iki yazim da kabul.
        from rcl_interfaces.msg import ParameterDescriptor
        self.declare_parameter("fit_confidence_px", 800.0,
                               ParameterDescriptor(dynamic_typing=True))
        self.fit_confidence_px = float(self.get_parameter("fit_confidence_px").value)
        self._fit_px = 0
        self._son_lane_x = None   # son GECERLI serit merkezi (sureklilik)
        # sag serit gecisi (bkz. sag_serit parametresi)
        self._lane_x_cmd  = None      # hiz sinirlanmis serit merkezi
        self._gecis_aktif = False     # serit degistirme suruyor mu
        self._gecis_say   = 0         # teyit sayaci
        self._gecis_t     = None      # son karenin zaman damgasi (dt icin)
        self._gecis_adet  = 0         # kac kez serit degistirildi (log)
        self._sag_gecis   = False     # cift_sec kurdu: kural baska serit sectI
        self._cift_red = 0        # ust uste reddedilen cift sayisi
        self._cift_ok = False     # bu karedeki cift gecerli mi
        self._aday_sayisi = 0     # o karede bulunan aday cizgi sayisi
        self._fit_px_ornek = 0
        self._bariyer = None
        self._bariyer_elenen = 0   # bariyerde diye elenen aday sayisi
        self._path_yasi = 0        # son TAZE merkezden bu yana kare
        self._path_guven = 1.0
        self._son_fit_red = None   # fit_lane_poly'nin son red sebebi
        self._kare_red = 'OK'      # bu karede olcum neden alinamadi
        self._red_sayac = {}       # sebep -> kare sayisi (teshis)
        self._son_taze_t = None    # son TAZE olcumun zamani
        self._path_yas_s = 0.0
        self._path_durum = 'TAZE'
        self._son_span = None      # fit_lane_poly'nin son satir araligi
        self._span_sol = self._span_sag = None
        self._sol_taze = self._sag_taze = False
        self._y_etkin = None       # bu karede kullanilan olcum satiri
        self._paralel_red = 0    # paralellik kapisi kac kez atesledi
        self._paralel_sapma = 0.0
        self._lat_err = 0.0   # hatanin yanal bileseni (overlay teshisi)
        self._head_err = 0.0  # hatanin yon-onizleme bileseni
        self.declare_parameter("steer_kd", self.pid.Kd)
        _kd = float(self.get_parameter("steer_kd").value)
        if _kd < 0.0:
            self.get_logger().warn(f"steer_kd={_kd} negatif -> yok sayildi.")
        else:
            self.pid.Kd = _kd
        self.declare_parameter("steer_kp", self.pid.Kp)
        _kp = float(self.get_parameter("steer_kp").value)
        if _kp <= 0.0:
            self.get_logger().warn(
                f"steer_kp={_kp} <= 0 -> direksiyon duzeltmesi KAPALI olur. "
                "Kapali cevrimde bu EN KOTU sonucu vermisti; varsayilana donuluyor.")
        else:
            self.pid.Kp = _kp
        if _kp > 0.03:
            self.get_logger().warn(
                f"steer_kp={_kp} yuksek: kapali cevrim testinde 0.02 uzeri "
                "degerler araci pistten cikardi (bkz. PIDController notu).")

        # Conditional integration (Bug 3): integral yalnizca BU karede iki serit
        # de bulunduysa VE hata |err|<=i_error_band iken birikir. Boylece
        # tek-serit/biasli tahminler integrali doyurup direksiyonu mihlamaz.
        self._both_detected = False
        self.declare_parameter("i_error_band", 40.0)
        self.i_error_band = float(self.get_parameter("i_error_band").value)

        # Error sifir-noktasi kalibrasyonu: src_pts + ZED yanal montaj ofseti
        # nedeniyle arac fiziksel olarak ortadayken err != 0 okunabilir.
        # Kalibrasyon: duz bolumde surucu araci gozle serit ortasinda tutarken
        # overlay'deki AvgErr'i oku, MEVCUT err_offset'in ustune ekle:
        #   -p err_offset:=<mevcut + AvgErr>
        # ERR_OFFSET OLCULDU 2026-08-20: 0.0 -> -71.0 px
        # Kaynak: joystick_46 kaydi, t=24-51 s. Arac 27 saniye DURUYOR ve surucu
        # seridin ortasinda konumlandirmis (operator teyidi: "%90 ortalamisti,
        # dogru serit cizgilerini algiliyor"). O pencerede algi 27 saniye boyunca
        # sabit -71 px okudu (standart sapma SIFIR, LaneW 475 px, iki fit de saglam).
        # Arac fizken ortadayken okunan bu sapma = ZED'in yanal montaj kaymasi +
        # src_pts geometrisi, yani tam olarak bu parametrenin var olma sebebi.
        #
        # CELISKI GORUNUP COZULEN NOKTA (tekrar arastirilmasin): ofset 0 iken
        # kaydin HAREKETLI karelerinin medyani +3 px cikiyor, bu "sapma yok" gibi
        # okunuyordu. Ham karelere bakinca sebebi anlasildi: surucu sururken
        # BARIYERLERDEN kacinip surekli ~0.6 m SOLDA gitmis (t=70 s ve t=130 s
        # karelerinde kamera serit ortasinin belirgin solunda). Iki etki birbirini
        # gotururup toplami sifira yakin gosteriyordu. Yani -71 uygulamak araci
        # bariyere yaklastirmaz, tam tersine gercek serit ortasina getirir:
        # su anki halinde sol pay 0.78 -> 0.18 m'ye dusuyordu.
        # Belirsizlik: operatorun "%90" ifadesi ~+-10 px demek; Kp=0.02 ile bu
        # 0.2 FSM birimi eder, ihmal edilebilir.
        # Aracta ilk kosuda overlay'deki AvgErr sifir civarinda salinmali; sistematik
        # olarak bir tarafta kalirsa ofseti o kadar kaydirin (-p err_offset:=...).
        # -71 -> -67 (2026-08-20 aksam, YENI boru hattiyla yeniden olculdu:
        # cift gecerlilik kapisi eklendikten sonra). joystick_46 kaydinda
        # operatorun bilerek ortaladigi 24-50 s duruş penceresi, 194 kare,
        # medyan -67.0 px, std 0.4 (cift reddi 0 -> kapi bu pencerede pasif,
        # yani fark kapiden degil olcum inceliginden geliyor).
        # ⚠️ AYNI KAYITTAKI DIGER DURUŞLAR COK FARKLI OKUYOR:
        #   2-8 s +87 px (std 1.2) | 191-226 s +23 (std 30) | 238-241 s +65
        # Iki saglam duruş 154 px (~1.0 m) ayri -- cunku arac fiziksel olarak
        # farkli yerlerde duruyordu. err_offset YALNIZCA operatorun bilerek
        # serit ortasina koydugu pencereden okunur; baska bir duruş "aracin o
        # an nerede oldugunu" olcer, kamera montaj sapmasini DEGIL.
        self.declare_parameter("err_offset", -67.0)
        self.err_offset = float(self.get_parameter("err_offset").value)
        self.err_hist = deque()      # (t, err) -> son ~3 sn kayan ortalama

        # ---- err_offset <-> lookahead_frac BAGIMLILIGI (2026-08-20) ----
        # BEV'de "duz ileri" yonu DIKEY DEGIL, egik: kamera sutunu 320'nin
        # karsiligi BEV satir 342'de x=251, satir 36'da x=184 (67 px kayma).
        # Sebep src_pts yamugunun asimetrisi (alt kenar ortasi 404.5, goruntu
        # merkezi 320) + kameranin yol yonune gore yaw'i.
        # SONUC: err_offset yalnizca OLCULDUGU y_eval icin gecerlidir.
        # lookahead_frac degistirilirse ofset sessizce yanlis olur -- bu yuzden
        # asagida hesaplanip loglaniyor ve buyuk sapmada UYARILIYOR.
        try:
            _xs = np.arange(0, self.img_w, 1.0)
            _p = np.float32([[[x, float(self.y_eval)]] for x in _xs])
            _cam = cv2.perspectiveTransform(_p, self.M_ipm_inv).reshape(-1, 2)
            _i = int(np.argmin(np.abs(_cam[:, 0] - self.img_w / 2.0)))
            self._duz_ileri_bev = float(_xs[_i])
            _geo = self._duz_ileri_bev - self.img_w / 2.0
            self.get_logger().info(
                f"BEV geometrisi: y_eval={self.y_eval} satirinda 'duz ileri' "
                f"BEV x={self._duz_ileri_bev:.0f} (merkez {self.img_w//2}), "
                f"geometrik sapma {_geo:+.0f} px | err_offset={self.err_offset:+.0f} px "
                f"| fark {self.err_offset - _geo:+.0f} px = kamera yanal montaj kaymasi")
            if abs(self.err_offset - _geo) > 60.0:
                self.get_logger().warn(
                    f"err_offset ({self.err_offset:+.0f}) ile bu y_eval'in geometrik "
                    f"sapmasi ({_geo:+.0f}) arasinda {abs(self.err_offset-_geo):.0f} px fark var. "
                    "lookahead_frac degistiyse err_offset YENIDEN KALIBRE EDILMELI "
                    "(duz seritte arac ortada, overlay'deki AvgErr okunur).")
        except Exception as _e:
            self.get_logger().warn(f"BEV geometri kontrolu yapilamadi: {_e}")

        # Hatanin METRE karsiligi: err_m = err_px * lane_width_m / lane_w_px.
        # lane_w_px, iki fit de varken y_eval'de olculur ve EMA ile yumusatilir.
        # Gercek pistte iki beyaz cizgi arasi olculdu (2026-07-20): yer yer
        # degisken ama cogu yerde ~2.96 m -> 3.0 aliniyor. CARLA seritleri 3.5 m,
        # simde istenirse -p lane_width_m:=3.5 ile geri alinabilir.
        self.declare_parameter("lane_width_m", 3.0)
        self.lane_width_m = float(self.get_parameter("lane_width_m").value)
        self.lane_w_px = None
        # Iki fitin de goruldugu SON karede olculen merkez-cizgi ofsetleri.
        # Tek fite dusuldugunde bunlar uygulanir (bkz. _tek_fit_merkez).
        self.off_sol = None
        self.off_sag = None

        # Load YOLO
        # MODEL SECIMI PARAMETRELI (2026-08-17). Eskiden dosya adi koda SABIT
        # yazilmisti; models/ klasorunde 9 agirlik durmasina ragmen hangisinin
        # kullanildigi ancak kod okunarak anlasiliyordu ve degistirmek icin
        # kaynagi duzenleyip yeniden derlemek gerekiyordu.
        #   models/ altindaki bir dosya adi   -> paketten yuklenir
        #   mutlak yol (/... ile baslayan)    -> dogrudan o dosya yuklenir
        # Yeni bir agirligi denemek icin:
        #   ros2 run neuravix_ros2 lane_follower --ros-args \
        #       -p model_file:=best_yolo11_v2.pt
        #   ros2 run neuravix_ros2 lane_follower --ros-args \
        #       -p model_file:=/media/taha/T7/lane_egitim/v1/weights/best.pt
        # VARSAYILAN 2026-08-18'de degisti: best_yolo11.pt -> serit_v2.pt
        # serit_v2 = 391 el-etiketli gercek pist karesiyle egitilen yolo11s-seg.
        # Tutulan test bolunmesinde (39 kare, egitimde gorulmedi) olculdu:
        #     maske kalinligi 0.317 -> 0.241 m  (el etiketi tavani 0.238)
        #     fit RMS         22.9  -> 16.3 px
        #     hic fit cikmayan kare %23.1 -> %12.8
        # 2026-08-19: 189 epoch'luk yeniden egitim (C) kuruldu. 120 epoch'luk
        # ilk surum (B) erken kesilmisti - patience hic tetiklenmemisti. C
        # epoch 149'da zirve yapip 189'da erken durdu. B'ye gore kalinlik
        # 0.248->0.241, RMS 18.2->16.3. Kapsam farki (2-fit %53.8->%51.3) tek
        # kareye denk geliyor, 39 karelik test bolunmesinde gurultu.
        # B yedegi: /media/taha/T7/lane_egitim/serit_v2_B_yedek.pt
        # Eski model kesikli ORTA cizgiyi tamamen kaciriyordu, yenisi buluyor.
        # Eskiye donmek icin: -p model_file:=best_yolo11.pt
        self.declare_parameter("model_file", "serit_v2.pt")
        _mf = self.get_parameter("model_file").get_parameter_value().string_value
        if os.path.isabs(_mf):
            model_path = _mf
        else:
            share_dir = get_package_share_directory("neuravix_ros2")
            model_path = os.path.join(share_dir, "models", _mf)
        if not os.path.isfile(model_path):
            raise FileNotFoundError(
                f"YOLO agirligi bulunamadi: {model_path}\n"
                f"  models/ altindakiler paket icin 'colcon build' gerektirir; "
                f"paket disi bir dosya icin MUTLAK yol verin.")
        self.model_yolu = model_path   # harici araclar (tools/) okuyor
        self.model = YOLO(model_path)
        # Guven esigi parametreli: dusuk kontrastli/uzak serit izleri icin
        # asagi cekilebilir. ultralytics varsayilani zaten 0.25.
        self.declare_parameter("yolo_conf", 0.25)
        self.yolo_conf = float(self.get_parameter("yolo_conf").value)
        # Serit sinifinin indeksi. Model 2+ sinifliysa adi 'lane'/'serit' olani
        # bul; tek sinifliysa None -> suzgec kapali (eski modellerle uyumlu).
        # Indeks data.yaml'daki siraya gore degisir, o yuzden ADA gore ariyoruz.
        self._lane_cls = None
        try:
            adlar = dict(self.model.names)
            if len(adlar) > 1:
                for i, ad in adlar.items():
                    if str(ad).strip().lower() in ("lane", "serit", "şerit"):
                        self._lane_cls = int(i)
                        break
                if self._lane_cls is None:
                    self.get_logger().error(
                        f"Model {len(adlar)} sinifli {adlar} ama 'lane' yok -> "
                        "TUM maskeler serit sayilacak (bariyer dahil!). "
                        "data.yaml'daki sinif adini kontrol edin.")
        except Exception as e:
            self.get_logger().warn(f"Sinif adlari okunamadi: {e}")
        self.get_logger().info(
            f"YOLO yuklendi: {model_path} | siniflar={getattr(self.model, 'names', '?')} "
            f"| serit sinif idx={self._lane_cls}")

        # ROS
        # camera_topic parametreli: sim'de CARLA overlay çıktısı, gerçek
        # araçta launch'tan Zed2 topic'ine (örn. /zed/zed_node/rgb/image_rect_color)
        # yönlendirilir. tabela_tespit_node.py / obstacle_lidar_node.py ile
        # aynı desen (camera_topic / lidar_topic parametreleri).
        # VARSAYILAN = GERCEK ARAC (ZED). CARLA tarafi zaten parametreyle
        # geciyor (-p camera_topic:=/carla/ego_vehicle/rgb_front/image),
        # o yuzden varsayilanin araca bakmasi daha guvenli: aracta
        # parametre unutulursa dugum var olmayan bir CARLA topic'ini
        # dinleyip sessizce hicbir sey yayinlamaz.
        self.declare_parameter("camera_topic", "/zed/zed_node/rgb/image_rect_color")
        camera_topic = self.get_parameter("camera_topic").get_parameter_value().string_value

        # Debug goruntu cikisi: pencere (cv2.imshow) yerine/yaninda topic.
        # Gercek aracta container'in DISPLAY'i yok -> pencere acilamaz; overlay
        # JPEG olarak /neuravix/lane_debug/compressed'e basilir, laptoptan
        # rqt_image_view ile kablosuz izlenir. show_window=true olsa bile
        # DISPLAY bos ise pencere otomatik kapatilir (imshow crash onlemi).
        self.declare_parameter("publish_debug_image", True)
        # BEV (kusbakisi) teshis goruntusu ayri bir topic'e basilir. Homografi
        # dogrulugu ancak buradan anlasilir; CPU maliyeti bir warp + JPEG.
        # Yarista kapatmak icin -p publish_bev_image:=false
        self.declare_parameter("publish_bev_image", True)
        self.declare_parameter("show_window", True)
        self.publish_debug = self.get_parameter(
            "publish_debug_image").get_parameter_value().bool_value
        self.show_window = self.get_parameter(
            "show_window").get_parameter_value().bool_value
        if self.show_window and not os.environ.get("DISPLAY"):
            self.show_window = False
            self.get_logger().warn(
                "DISPLAY yok: pencere kapatildi. Goruntu icin "
                "/neuravix/lane_debug/compressed topic'ini izleyin (rqt_image_view).")

        self.pub = self.create_publisher(String, "/master", 10)
        self.debug_pub = (
            self.create_publisher(CompressedImage, "/neuravix/lane_debug/compressed", 10)
            if self.publish_debug else None
        )
        self.publish_bev = self.get_parameter(
            "publish_bev_image").get_parameter_value().bool_value
        self.bev_pub = (
            self.create_publisher(CompressedImage, "/neuravix/bev_debug/compressed", 10)
            if self.publish_bev else None
        )
        # sensor_data QoS (best-effort): ZED wrapper gibi gercek kamera
        # suruculeri best-effort yayinlayabilir; reliable abonelik onlarla
        # eslesmez. CARLA'nin reliable yayiniyla da uyumlu.
        self.sub = self.create_subscription(
            Image, camera_topic, self.cb, qos_profile_sensor_data
        )

        self.prev_time = 0

        # Ileri bakisin METRE karsiligi (kaba): BEV satiri -> mesafe. ZED
        # ic parametreleri (fy=262, cy=181 @640x360) ve src_pts'ten turetildi;
        # kamera yuksekligi ~1.15 m varsayimi. Aracta bu satiri okuyup
        # gercekten uzaga bakildigini dogrula.
        # BEV satir <-> yerdeki mesafe eslemesi. src_pts'in alt/ust kenarinin
        # dst_pts'te dustugu satirlar ve o kenarlarin ZED ic parametrelerinden
        # hesaplanan mesafeleri. ⚠️ MUTLAK OLCEK DOGRULANMADI: kamera
        # yuksekligi ~1.15 m VARSAYIMINA dayaniyor. Ham kayitta olculen serit
        # genisligi 462 px = bu olcekle 3.68 m; pistte olculen ~2.96 m.
        # BEV'in SEKLI dogru (sabitlik 1.026), sorun yalnizca px/m carpani.
        # Etkisi metre GOSTERIMLERIYLE sinirli: err piksel cinsinden Kp ile
        # olcekleniyor, _half_lane() de piksel kullaniyor. BEV teshis
        # goruntusundeki metre izgarasi + gri dikey referanslar bunu gozle
        # sinamak icin var.
        # ⚠️ Bu degerler yalnizca ipm_mode='src_pts' (elle tiklanmis homografi)
        # icin gecerli TAHMINLERDIR. ipm_mode='analytic' ise _analitik_ipm_kur()
        # bunlari KESIN degerlerle zaten doldurdu -> uzerine yazma.
        if self.ipm_mode != "analytic":
            self.BEV_NEAR_ROW, self.BEV_FAR_ROW = 342, 36
            self.D_NEAR_M, self.D_FAR_M = 1.71, 10.34
            self.PX_PER_M = 125.5              # 384 BEV px = 3.06 m
        _fr = (self.y_eval - self.BEV_FAR_ROW) / (self.BEV_NEAR_ROW - self.BEV_FAR_ROW)
        _look_m = self.D_FAR_M + _fr * (self.D_NEAR_M - self.D_FAR_M)
        self.lookahead_m = _look_m
        self.get_logger().info(
            f"Serit takip: ileri bakis={self.lookahead_frac:.2f}*H "
            f"(BEV satir {self.y_eval}) ~ {_look_m:.1f} m | "
            f"fit penceresi={self.fit_far_frac:.2f}*H (~5.8 m'ye kadar), "
            f"agirlik^{self.fit_weight_pow:.0f}, "
            f"derece={self.fit_degree}(adaptif k={self.fit_deg2_kazanc}) | "
            f"egim_siniri={self.fit_max_slope} (eski 1.0) "
            f"min_nokta={self.fit_min_points} min_uzunluk={self.fit_min_span_frac} | "
            f"yon_onizleme={self.heading_gain:.0f}"
            f"(doyum {self.heading_max_px:.0f}px) | "
            f"Kp={self.pid.Kp} err_offset={self.err_offset:.0f}px "
            f"lane_width={self.lane_width_m} m | sag_serit="
            + ("ACIK (kesik oran>=%.1f, esik %.0f px, teyit %d kare, %.0f px/s)"
               % (self.sag_serit_kesik_oran, self.sag_serit_esik_px,
                  self.sag_serit_teyit, self.sag_serit_px_s)
               if self.sag_serit else "kapali")
            + "\n"
            + "  BEV src_pts = "
            + ", ".join(f"({p[0]:.0f},{p[1]:.0f})" for p in self.src_pts)
            + f" | ipm_mode={self.ipm_mode}")

        # ---------------- VIDEO KAYDI ('r' tusu) -----------------
        # 'r' tusu ile kayit baslar/durur. overlay frame'i (BEV serit
        # cizimli) ~/neuravix_kayit/ altina yazilir.
        self.video_writer = None
        self._video_path  = None

    def _toggle_record(self, frame):
        """'r' tusu: kaydi baslat / durdur."""
        if self.video_writer is None:
            h, w = frame.shape[:2]
            out_dir = os.path.expanduser("~/neuravix_kayit")
            os.makedirs(out_dir, exist_ok=True)
            ts = time.strftime("%Y%m%d_%H%M%S")
            self._video_path = os.path.join(out_dir, f"serit_takip_{ts}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.video_writer = cv2.VideoWriter(self._video_path, fourcc, 20.0, (w, h))
            self.get_logger().info(f"[REC] Kayit BASLADI: {self._video_path}")
        else:
            self.video_writer.release()
            self.get_logger().info(f"[REC] Kayit DURDU: {self._video_path}")
            self.video_writer = None

    # ---------------- MAIN CALLBACK -----------------
    # ======================================================================
    # TEK KONTROL YOLU -- cb() ve masa testleri BUNU cagirir.
    # 2026-08-20: tools/serit_kapali_cevrim.py kontrol matematiginin KENDI
    # KOPYASINI tutuyordu ve iki terimi atliyordu: heading_gain (yon
    # onizlemesi) ve fit_confidence_px (guven agirligi). Yani masa testleri
    # aylardir dugumun CALISTIRMADIGI bir kontrolcuyu olcuyordu; heading_gain
    # taramasi 0 ile 120 arasinda birebir ayni sonucu veriyordu (terim hic
    # uygulanmiyordu). Ikinci bir kopya YAZILMAMALIDIR.
    # ======================================================================
    def _row_to_m(self, row):
        """BEV satiri -> aracin onunden metre (_m_to_row'un tersi)."""
        fr = ((row - self.BEV_FAR_ROW) /
              float(self.BEV_NEAR_ROW - self.BEV_FAR_ROW))
        return self.D_FAR_M + fr * (self.D_NEAR_M - self.D_FAR_M)

    def merkez_poly(self, left_poly, right_poly):
        """Serit ORTA CIZGISININ polinomu (BEV x = f(y)).

        Iki fit varsa ortalamalari, tek fit varsa olculen yarim serit kadar
        otelenmis hali. Kontrolcunun "yol"u budur -- eskiden yalnizca y_eval
        satirindaki TEK degeri (lane_x) kullaniliyordu, bu yuzden viraj
        kontrolcuye sadece o tek sayinin icinden sizabiliyordu.
        """
        if left_poly is not None and right_poly is not None:
            return np.polyadd(np.asarray(left_poly), np.asarray(right_poly)) * 0.5
        yari = self._half_lane()
        if left_poly is not None:
            p = np.array(left_poly, float).copy(); p[-1] += yari; return p
        if right_poly is not None:
            p = np.array(right_poly, float).copy(); p[-1] -= yari; return p
        return None

    def bariyer_bev(self, bariyerler, shape):
        """Bariyer maskelerini tek BEV maskesine tasi (genisletilmis)."""
        if not bariyerler or self.bariyer_ele_oran <= 0:
            return None
        h, w = shape[0], shape[1]
        out = np.zeros((h, w), np.uint8)
        for m in bariyerler:
            out |= (cv2.resize(m, (w, h)) > 0.5).astype(np.uint8) * 255
        out[:int(self.img_h * 0.40), :] = 0
        b = self.bev_warp(out)
        if self.bariyer_genislet_px > 0:
            k = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (self.bariyer_genislet_px * 2 + 1,) * 2)
            b = cv2.dilate(b, k, 1)
        return b

    def bariyerde_mi(self, poly, bariyer):
        """Aday cizgi bariyerin uzerinde/dibinde mi? (True = serit DEGIL)"""
        if bariyer is None:
            return False
        ys = np.arange(int(self.img_h * self.fit_far_frac), self.img_h, 4)
        xs = np.polyval(poly, ys).astype(int)
        ok = (xs >= 0) & (xs < self.img_w)
        if int(ok.sum()) < 5:
            return False
        return float((bariyer[ys[ok], xs[ok]] > 0).mean()) > self.bariyer_ele_oran

    def _grupla(self, nokta_kumeleri):
        """Ayni FIZIKSEL cizgiye ait ornekleri birlestir (es-dogrusallik).

        Kesikli serit YOLO'da birden cok ornek olur; tek tek fit vermezler
        ama birlesince verirler. Ayri cizgiler (bizim sag cizgimiz vs
        bariyer kenari) ~450 px ayri oldugu icin birlesmezler.
        """
        ogeler = []
        for ys, xs in nokta_kumeleri:
            if len(xs) < 8:
                continue
            ogeler.append((ys, xs, float(xs.mean()), float(ys.mean()), len(xs)))
        if self.serit_grup_tol <= 0:          # kapali: her ornek kendi grubu
            return [(ys, xs) for ys, xs, *_ in ogeler]
        ogeler.sort(key=lambda o: -o[4])          # en buyuk parca cekirdek
        gruplar = []
        for ys, xs, cx, cy, _ in ogeler:
            yer = None
            for gi, (gys, gxs) in enumerate(gruplar):
                if len(gxs) >= 20 and np.ptp(gys) > 10:
                    try:
                        tahmin = float(np.polyval(np.polyfit(gys, gxs, 1), cy))
                    except Exception:
                        tahmin = float(gxs.mean())
                else:
                    tahmin = float(gxs.mean())
                if abs(tahmin - cx) < self.serit_grup_tol:
                    yer = gi
                    break
            if yer is None:
                gruplar.append((ys, xs))
            else:
                gys, gxs = gruplar[yer]
                gruplar[yer] = (np.concatenate([gys, ys]),
                                np.concatenate([gxs, xs]))
        return gruplar

    def ornek_fitler(self, masks, shape, bariyer=None):
        """YOLO orneklerini cizgi bazinda grupla ve fitle.

        Doner: [(poly, x_at_yeval, piksel_sayisi), ...] soldan saga.
        """
        h, w = shape[0], shape[1]
        ufuk = int(self.img_h * 0.40)
        ymin = int(self.img_h * self.fit_far_frac)
        buyuk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        kucuk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        kumeler = []
        for m in masks:
            mm = (cv2.resize(m, (w, h)) > 0.5).astype(np.uint8) * 255
            mm = cv2.morphologyEx(mm, cv2.MORPH_CLOSE, buyuk, 2)
            mm = cv2.morphologyEx(mm, cv2.MORPH_OPEN, kucuk, 1)
            mm[:ufuk, :] = 0
            b = self.bev_warp(mm)
            ys, xs = np.where(b > 0)
            if len(xs):
                kumeler.append((ys, xs))
        adaylar = []
        for gys, gxs in self._grupla(kumeler):
            b = np.zeros((self.img_h, self.img_w), np.uint8)
            b[np.clip(gys, 0, self.img_h - 1), np.clip(gxs, 0, self.img_w - 1)] = 255
            poly = self.fit_lane_poly(b)
            _sp = self._son_span
            if poly is None:
                continue
            if self.bariyerde_mi(poly, bariyer):
                self._bariyer_elenen += 1
                continue
            adaylar.append((poly, float(self.poly_x(poly, self.y_eval)),
                            int((b[ymin:, :] > 0).sum()), _sp))
        if not adaylar:
            # Hicbir aday cikmadi: son red sebebini kare seviyesine tasi
            self._kare_red = self._son_fit_red or 'FIT_YOK'
        adaylar.sort(key=lambda a: a[1])
        return adaylar

    def _kesik_sol(self, sol, sag):
        """Bu cift 'solunda KESIK, saginda DUZ cizgi olan' bir serit mi?

        Kesik cizgi ayni uzunlukta daha AZ piksel tutar; olculen oran gercek
        ZED karelerinde 3.8 kat (5 206 / 19 606 px). Esik sag_serit_kesik_oran.
        Sag serit boyle bir seritdir: kesik orta cizgi SOLDA, duz kenar SAGDA.
        Arac SOL seritteyken tam tersi olur (duz kenar solda) -- tespit sinyali
        budur.
        """
        p_sol, p_sag = sol[2], sag[2]
        if p_sol <= 0 or p_sag <= 0:
            return False
        return p_sol * self.sag_serit_kesik_oran <= p_sag

    def cift_sec(self, adaylar):
        """Aday cizgilerden en iyi SERIT CIFTINI sec -> (sol_poly, sag_poly).

        Olcut: genislik gecerli olacak; aralarindan merkezi son gecerli
        serit merkezine EN YAKIN olan; esitlikte daha cok pikselli.
        Gecerli cift yoksa (None, None).

        SAG SERIT KURALI (sag_serit=true): once "solu kesik, sagi duz" olan
        ciftlere bakilir ve aralarindan EN SAGDAKI secilir; boyle bir cift
        yoksa yukaridaki eski olcut aynen isler. Gerekce ve olcum
        __init__'teki sag_serit blogunda.
        """
        en, en_skor = None, None
        for i in range(len(adaylar)):
            for j in range(i + 1, len(adaylar)):
                gen = adaylar[j][1] - adaylar[i][1]
                if not self.cift_gecerli(gen):
                    continue
                if not self.cift_paralel(adaylar[i][0], adaylar[j][0]):
                    continue
                merkez = 0.5 * (adaylar[i][1] + adaylar[j][1])
                uzak = (abs(merkez - self._son_lane_x)
                        if self._son_lane_x is not None else 0.0)
                eski_skor = uzak - 0.02 * min(adaylar[i][2], adaylar[j][2])
                # (oncelik, deger) -- oncelik 0 = kanit var, en sagdaki kazanir
                if self.sag_serit and self._kesik_sol(adaylar[i], adaylar[j]):
                    skor = (0, -merkez)
                else:
                    skor = (1, eski_skor)
                if en_skor is None or skor < en_skor:
                    en_skor, en = skor, (adaylar[i], adaylar[j])
        if not en:
            self._span_sol = self._span_sag = None
            return None, None
        # ⚠️ GECIS TETIGI KURALIN KENDISINE BAGLI (24.08.2026 olcumu).
        # Ilk surumde tetik "hedef 150 px'den fazla sicradiysa" idi ve bu
        # SERIT DEGISIMI OLMAYAN sicramalari da yakaliyordu: 400 gercek
        # karede 2 kez yanlis atesledi (kare 1560 ve 5550), ikisinde de
        # gecerli cift TEKTI -- yani secim hic degismemisti, sicrama
        # iki-fit <-> tek-fit gecisinden geliyordu. O sicramalari
        # rampalamak _tek_fit_merkez'in surekliligini bozar. Artik yalnizca
        # "kural KANITLA baska bir seridi sectI" durumu gecis sayilir.
        self._sag_gecis = False
        if (self.sag_serit and en_skor is not None and en_skor[0] == 0
                and self._son_lane_x is not None):
            _mrk = 0.5 * (en[0][1] + en[1][1])
            self._sag_gecis = abs(_mrk - self._son_lane_x) > self.sag_serit_esik_px
        self._span_sol, self._span_sag = en[0][3], en[1][3]
        return en[0][0], en[1][0]

    def tek_aday_taraf(self, aday):
        """Tek cizgi kaldi: SOL mu SAG mi?

        True = bu benim SOL cizgim (yani serit merkezi cizginin SAGINDA).

        Cipa ARAC EKSENIDIR, onceki tahmin DEGIL -- gerekcesi ve olcumu
        `taraf_kural` parametresinin yaninda. Ozetle: merkezi eksene en yakin
        yapan hipotez secilir; belirsiz bantta (iki hipotez de esit uzakta)
        sureklilige dusulur. 'sureklilik' modu eski (kacis ureten) davranistir,
        yalnizca karsilastirma icin durur.
        """
        yari = self._half_lane()
        x = aday[1]
        ref = self.img_w / 2.0 + self.err_offset
        if self._son_lane_x is None:
            return x < ref
        if self.taraf_kural != "eksen":
            return (abs((x + yari) - self._son_lane_x)
                    <= abs((x - yari) - self._son_lane_x))

        geo = ref >= x              # |x+yari-ref| <= |x-yari-ref| (yari > 0)
        kanit = abs(x - ref)
        esik = self.taraf_bant_px
        if self.taraf_hist_px > 0.0:
            # (varsayilan DEGIL -- olcumle reddedildi, bkz. taraf_hist_px)
            simdi = time.time()
            if (self._son_taraf is not None
                    and (simdi - self._son_taraf_t) <= self.taraf_hist_s):
                if geo != self._son_taraf:
                    esik += self.taraf_hist_px
                if kanit < esik:
                    self._son_taraf_t = simdi
                    return self._son_taraf
            self._son_taraf, self._son_taraf_t = (geo if kanit >= esik
                                                  else geo), simdi
        if kanit >= esik:
            return geo
        # Kararsiz bant: geometrinin bilgisi yok, surekliligi kullan.
        return (abs((x + yari) - self._son_lane_x)
                <= abs((x - yari) - self._son_lane_x))

    def etkin_satir(self):
        """Bu karede olcumun yapilacagi BEV satiri.

        Normalde y_eval. Fitlerin verisi oraya ULASMIYORSA (virajda sol serit
        gorus disina cikinca oluyor) uydurma yerine verinin destekledigi EN
        UZAK satira geri cekilir. BEV'de buyuk satir = YAKIN.
        None donerse: veri yalnizca cok yakinda, olcum guvenilmez.
        """
        if not self.adaptif_lookahead:
            return self.y_eval
        los = [sp[0] for sp in (self._span_sol, self._span_sag) if sp]
        if not los:
            return self.y_eval
        lo = max(los)                 # iki fitin de destekledigi en uzak satir
        if lo <= self.y_eval:
            return self.y_eval        # veri zaten yeterince uzagi kapsiyor
        en_yakin = self._m_to_row(self.adaptif_min_m)
        if lo > en_yakin:
            return None               # yalnizca cok yakinda veri var
        return int(lo)

    def cift_paralel(self, sol, sag):
        """Iki fit PARALEL mi? Dogru bir IPM'de serit cizgileri paraleldir.

        REDDETMEK = TEK FITE DUSMEK, kareyi ATMAK DEGIL (2026-08-19 dersi:
        fit atmak kapali cevrimi kotulestirdi, 0.98 -> 4.31 m).
        """
        if self.cift_paralel_tol <= 0 or sol is None or sag is None:
            return True
        d = max(8, int(0.15 * self.img_h))
        y1 = max(0, self.y_eval - d)
        y2 = min(self.img_h - 1, self.y_eval + d)
        if y2 - y1 < 8:
            return True
        w1 = float(self.poly_x(sag, y1) - self.poly_x(sol, y1))
        w2 = float(self.poly_x(sag, y2) - self.poly_x(sol, y2))
        ort = 0.5 * abs(w1 + w2)
        if ort < 1.0:
            return False
        self._paralel_sapma = abs(w2 - w1) / ort
        return self._paralel_sapma <= self.cift_paralel_tol

    def cift_gecerli(self, w_px):
        """Fit cifti genislik olarak gercek bir serit mi?

        Iki kademeli: (a) mutlak makuliyet penceresi, (b) olculmus genislik
        oturduysa ondan sapma orani. (b) kasitli olarak orana dayali --
        BEV olcegi (px/m) oturumlar arasi degisiyor (ayni pistte 358 px ve
        473 px olculdu), sabit metre esigi tasinmaz.
        """
        if not (self.lane_w_min_px <= w_px <= self.lane_w_max_px):
            return False
        if self.lane_w_px and abs(w_px - self.lane_w_px) > self.lane_w_tol * self.lane_w_px:
            return False
        return True

    def _serit_gecis(self, lane_x, serit_kayip):
        """Hedefteki BIR SERIT BOYU sicramayi hiz sinirli hale getirir.

        Yalnizca sag_serit acikken devrededir. sag_serit_esik_px altindaki
        degisimler HIC dokunulmadan gecer -- yani normal serit takibine
        gecikme eklemez; sadece "serit degistiriyorum" buyuklugundeki
        sicramalar rampalanir. Gecis basladiktan sonra hedef geri donerse
        rampa da yon degistirir (sicrama olmaz), hedefe varinca kapanir.
        """
        if not self.sag_serit:
            return lane_x
        if serit_kayip:
            # Serit yok: durumu sifirla ki geri bulununca yapay bir rampa
            # baslamasin (eski davranis korunur).
            self._lane_x_cmd = None
            self._gecis_aktif = False
            self._gecis_say = 0
            return lane_x
        istek = self._sag_gecis        # tek kullanimlik: her kare cift_sec kurar
        self._sag_gecis = False
        simdi = time.time()
        dt = (0.05 if self._gecis_t is None
              else min(0.5, max(1e-3, simdi - self._gecis_t)))
        self._gecis_t = simdi
        hedef = float(lane_x)
        if self._lane_x_cmd is None:
            self._lane_x_cmd = hedef
            return lane_x
        fark = hedef - self._lane_x_cmd
        if self._gecis_aktif:
            # Basladiktan sonra HEDEFE VARANA kadar surer; hedef geri donerse
            # rampa da yon degistirir, sicrama olmaz.
            adim = self.sag_serit_px_s * dt
            if abs(fark) <= adim:
                self._lane_x_cmd = hedef
                self._gecis_aktif = False
                self.get_logger().info(
                    f"SERIT DEGISTIRME bitti (hedef {hedef:.0f} px)")
            else:
                self._lane_x_cmd += adim if fark > 0 else -adim
            return int(round(self._lane_x_cmd))
        if not istek:
            self._gecis_say = 0
            self._lane_x_cmd = hedef          # normal takip: SINIRLAMA YOK
            return lane_x
        self._gecis_say += 1
        if self._gecis_say < self.sag_serit_teyit:
            return int(round(self._lane_x_cmd))   # kanit yetmiyor: kipirdama
        self._gecis_aktif = True
        self._gecis_adet += 1
        self.get_logger().warn(
            f"SERIT DEGISTIRME: hedef {self._lane_x_cmd:.0f} -> {hedef:.0f} px "
            f"({fark:+.0f} px, {self.sag_serit_px_s:.0f} px/s ile) -- kesik "
            f"cizgi solda kalacak sekilde saga geciliyor ({self._gecis_adet}. kez)")
        return int(round(self._lane_x_cmd))

    def _sureklilikle_merkez(self, lx, rx, y_eval):
        """Gecersiz cift -> tek cizgi gibi yorumla, tarafi SUREKLILIK secsin.

        Cift reddedildiginde iki fitten hangisinin kendi seridimizin hangi
        kenari oldugu goruntu konumundan bilinemez (kok sorun zaten bu).
        Dort aday merkez uretilir -- her fit icin "bu benim SOL cizgim" ve
        "bu benim SAG cizgim" -- ve son GECERLI merkeze en yakini secilir.
        Arac saga kaymissa 'bu benim sag cizgim' hipotezi kazanir ve arac
        sola, seride geri yonlendirilir; eski kod bunun tersini yapiyordu.

        Sureklilik yoksa (ilk kareler) eski davranis: orta nokta.
        """
        yari = self._half_lane()
        if self._son_lane_x is None:
            return (lx + rx) / 2.0, None
        adaylar = [(lx + yari, "sol", True), (lx - yari, "sag", False),
                   (rx + yari, "sol", True), (rx - yari, "sag", False)]
        merkez, _, sol_mu = min(adaylar, key=lambda a: abs(a[0] - self._son_lane_x))
        return merkez, sol_mu

    def guven_px(self, left_mask, right_mask):
        """Fit bolgesindeki piksel sayisi (guven agirliginin girdisi).

        fit_far_frac altindaki satirlarda iki maskenin dolu piksellerini
        sayar, AZ olani dondurur (zayif taraf fitin kalitesini belirler).
        """
        ymin = int(self.img_h * self.fit_far_frac)
        pk = [int((m[ymin:, :] > 0).sum())
              for m in (left_mask, right_mask) if m is not None]
        pk = [v for v in pk if v > 0]
        return min(pk) if pk else 0

    def saf_takip_delta(self, center_poly):
        """Saf takip: orta cizgi uzerindeki hedef noktaya teker acisi (rad).

        Pozitif = SAGA. None donerse hedef gecersiz (cagiran PID'e duser).
        """
        if center_poly is None:
            return None
        row = self._m_to_row(self.pp_lookahead_m)
        # Hedef nokta VERININ ICINDE kalmali: virajda ileri bakis kisalir.
        _ye = getattr(self, "_y_etkin", None)
        if _ye is not None and row < _ye:
            row = _ye
        row = int(max(self.img_h * self.fit_far_frac, min(self.img_h - 1, row)))
        ileri = self._row_to_m(row)
        if ileri <= 0.3:
            return None
        # BEV pikselinden arac cercevesine: x ekseni saga pozitif, referans
        # aracin kendi ekseni (merkez + err_offset).
        ref = self.img_w / 2.0 + self.err_offset
        yanal = (self.poly_x(center_poly, row) - ref) / self.PX_PER_M
        Ld = math.hypot(yanal, ileri)
        if Ld < 0.3:
            return None
        alpha = math.atan2(yanal, ileri)
        return math.atan2(2.0 * self.wheelbase_m * math.sin(alpha), Ld)

    def direksiyon_hesapla(self, lane_x, center_x_bev, lane_slope,
                           center_poly=None):
        """Serit merkezi -> FSM direksiyon acisi (15..75). (aci, ham_hata) doner.

        Sira onemli: err_offset -> yon onizlemesi -> PID -> guven agirligi.
        """
        # Iki bilesen AYRI saklanir: overlay'de "hata yanal mi, yon terimi mi?"
        # sorusunu tek bakista cevaplar. err_offset kalibrasyonunda YALNIZ
        # yanal bilesene bakilmali -- yon terimi virajda buyur ve ortalamayi
        # kaydirir, sabit bir kalibrasyon degeri gibi okunmamalidir.
        if self.lane_lost:
            err = self._lat_err = self._head_err = 0.0
        else:
            err = self._lat_err = lane_x - center_x_bev - self.err_offset
            self._head_err = 0.0
            # YON ONIZLEMESI (heading feedforward): fit'in y_eval'deki EGIMI
            # seridin o noktadaki yonunu verir. Yalnizca konum hatasina bakmak
            # "viraja girdikten SONRA tepki" demektir -- araçta gozlenen tam da
            # buydu: sag viraja girerken direksiyon once notr/hafif sol kaliyor,
            # ancak hata 80+ px'e ciktiginda saga kiriyordu. Egim terimi virajin
            # BASLADIGINI hata buyumeden haber verir.
            # Isaret: BEV'de saga kivrilan seritte dx/dy < 0; saga kirmak icin
            # err POZITIF olmali (steer = 45 - Kp*err) -> err -= k*egim.
            if self.heading_gain and lane_slope is not None:
                h = -self.heading_gain * lane_slope
                if self.heading_max_px > 0:
                    h = max(-self.heading_max_px, min(self.heading_max_px, h))
                if self.heading_no_flip and err != 0.0:
                    # h, err'i sifira kadar goturebilir ama isaretini ceviremez
                    h = max(h, -err) if err > 0 else min(h, -err)
                self._head_err = h
                err += h
        # Conditional integration (Bug 3): integral yalnizca iki serit de
        # goruldu VE hata bandda iken birikir -> sistematik bias mihlanmaz.
        allow_i = self._both_detected and (abs(err) <= self.i_error_band)
        out = self.pid.calculate(err, allow_integral=allow_i)
        # GUVEN AGIRLIGI (2026-08-19). Fit bolgesindeki piksel sayisi fitin
        # iyi/kotu olmasini AUC 0.881 ile ayirt ediyor. Az pikselli kareye TAM
        # direksiyon vermek yerine komutu KUCULTUYORUZ; bilgi atilmiyor, sadece
        # etkisi azaliyor. 0 = kapali (eski davranis).
        doyum = self.fit_confidence_px
        if doyum > 0:
            out *= min(1.0, getattr(self, "_fit_px", 0) / float(doyum))
        # PATH GUVENI: bayat path ile tam yetkili direksiyon verilmez.
        out *= getattr(self, "_path_guven", 1.0)

        if self.steer_mode == "pursuit" and not self.lane_lost:
            d = self.saf_takip_delta(center_poly)
            if d is not None:
                # delta pozitif = saga; FSM'de saga gitmek 45'in ALTI.
                self._pp_deg = math.degrees(d)
                out = self._pp_deg / max(1e-6, self.pp_deg_per_unit)
                if doyum > 0:      # guven agirligi saf takipte de gecerli
                    out *= min(1.0, getattr(self, "_fit_px", 0) / float(doyum))
                out *= getattr(self, "_path_guven", 1.0)
            else:
                self._pp_deg = None
        else:
            self._pp_deg = None
        return max(15, min(75, int(45 - out))), err

    def cb(self, msg):
        in_header = msg.header  # asagida 'msg' String ile golgeleniyor
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        img = cv2.resize(frame, (self.img_w, self.img_h))

        original = img.copy()

        # FPS
        t = time.time()
        if self.prev_time != 0:
            fps = int(1 / (t - self.prev_time))
            cv2.putText(original, f"FPS: {fps}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        self.prev_time = t

        # YOLO inference
        self._kare_red = 'OK'
        self._son_fit_red = None
        results = self.model(img, verbose=False, conf=self.yolo_conf)
        masks = []
        bariyerler = []
        for r in results:
            if r.masks is None:
                continue
            # SINIF SUZGECI (2026-08-18). Yeni egitim setinde `barrier` diye
            # ikinci bir sinif var: beyaz plastik bariyerleri ACIKCA etiketleyip
            # modele "beyaz plastik gövde" ile "asfalta boyanmis beyaz cizgi"
            # ayrimini ogretiyoruz -- kalin maske sorununun ana kaynagi bu
            # karisiklikti. Ama o maskeler SERIT DEGIL; buraya girerlerse
            # bariyeri serit sanip fit'i bozarlar. Sadece serit sinifini al.
            # Tek sinifli eski modellerde (best_yolo11.pt) suzgec devre disi.
            for i, m in enumerate(r.masks.data):
                if self._lane_cls is not None and r.boxes is not None:
                    if int(r.boxes.cls[i]) != self._lane_cls:
                        # BARIYER maskesi: serit DEGIL ama ATILMAZ. Pistin
                        # surulebilir koridorunun DIS SINIRINI isaretler ve
                        # bariyer dibindeki beyaz hatta oturan sahte "serit"
                        # adaylarini elemekte kullanilir (bkz. _bariyer_bev).
                        bariyerler.append(m.cpu().numpy())
                        continue
                masks.append(m.cpu().numpy())

        center_x_bev = self.img_w // 2
        # VARSAYILAN = REFERANS, geometrik merkez DEGIL.
        # err = lane_x - center_x_bev - err_offset oldugundan, hicbir olcum
        # yokken lane_x geometrik merkezde birakilirsa err = -err_offset olur
        # (err_offset=-67 ile HAYALET +67 px hata ve steer 43). "Bilmiyorum"
        # durumu NOTR olmali: lane_x = merkez + err_offset -> err = 0.
        lane_x = center_x_bev + self.err_offset
        # Seridin y_eval'deki YONU (dx/dy). Yon onizlemesi icin; fit yoksa None
        lane_slope = None

        # Eğer hiç maske yoksa fallback
        left_poly = self.left_prev
        right_poly = self.right_prev
        bev = None            # BEV teshis goruntusu icin (maske yoksa None)

        if len(masks) == 0:
            self._kare_red = 'YOLO_MASKE_YOK'
            self._both_detected = False   # maske yok -> integral birikmesin
            self.miss_count += 1
            if self.miss_count >= self.lane_lost_frames:
                # SERIT KAYBEDILDI: bayat fitlerle sonsuza dek surme,
                # fitleri ve PID'i sifirla -> lane_x merkezde kalir,
                # err=0, /master'a notr 45 gider (FSM duz devam eder).
                if not self.lane_lost:
                    self.lane_lost = True
                    self.get_logger().warn(
                        f"Serit {self.miss_count} frame'dir gorulmuyor: "
                        "fitler+PID sifirlandi, notr (45) yayinlaniyor.")
                left_poly = None
                right_poly = None
                self.pid.reset()
            else:
                # kisa kesinti: son fitlerle koprule
                y_eval = self.y_eval          # ileri bakis (lookahead_frac)
                if left_poly is not None and right_poly is not None:
                    lx = self.poly_x(left_poly, y_eval)
                    rx = self.poly_x(right_poly, y_eval)
                    if (self.cift_gecerli(rx - lx)
                            and self.cift_paralel(left_poly, right_poly)):
                        lane_x = (lx + rx) // 2
                        lane_slope = self._egim(left_poly, right_poly, y_eval)
                    else:
                        lane_x, _sm = self._sureklilikle_merkez(lx, rx, y_eval)
                        lane_slope = self._egim(left_poly, right_poly, y_eval)
                elif left_poly is not None:
                    lane_x = self._tek_fit_merkez(left_poly, True, y_eval)
                    lane_slope = self._egim(left_poly, None, y_eval)
                elif right_poly is not None:
                    lane_x = self._tek_fit_merkez(right_poly, False, y_eval)
                    lane_slope = self._egim(None, right_poly, y_eval)

        else:
            # NOT: miss_count burada SIFIRLANMAZ. Maske olmasi fit oldugu
            # anlamina gelmiyor (ham kayitta maske %99.5, fit %43) -> sayac
            # asagida, gercekten kullanilabilir fit ciktiginda sifirlanir.
            lane_mask = self.combine_masks(masks, img.shape)

            # Horizon üstünü tamamen sil → kavşak/gölge fix
            horizon = int(self.img_h * 0.40)
            lane_mask[:horizon, :] = 0

            # BEV mask
            bev = self.bev_warp(lane_mask)

            # Left-right split
            mid = self.img_w // 2
            offset = 70

            left_mask = np.zeros_like(bev)
            right_mask = np.zeros_like(bev)

            left_mask[:, :mid] = bev[:, :mid]
            left_mask[:, mid - offset:] = 0

            right_mask[:, mid:] = bev[:, mid:]
            right_mask[:, :mid + offset] = 0

            # GUVEN OLCUSU (2026-08-19): fit bolgesindeki PIKSEL SAYISI.
            # Etiketli tarama (433 kare, yer gercegi = kaydirmasiz kayitta
            # sapma 0) aday olcutleri AUC ile siraladi:
            #     piksel sayisi  0.881  <- en guclu
            #     satir yayilimi 0.855
            #     zamansal sicrama 0.801
            #     fit RMS        0.271  <- TERS calisiyor, kalite gostergesi DEGIL
            # Iyi fitler medyan 2543 piksel, kotuler 964 -> gercekten ayrisiyor.
            # Bunu ESIK olarak kullanmak kapali cevrimde KOTULESTIRDI
            # (0.98 -> 4.31 m): fit reddedilince node bayat fitle koprulur ve
            # manevra sirasinda bayat bilgi gurultulu taze bilgiden zararli.
            # Dogru kullanim AGIRLIK: bkz. asagidaki steer hesabi.
            self._fit_px = (getattr(self, "_fit_px_ornek", 0)
                            if self.serit_secim == "ornek"
                            else self.guven_px(left_mask, right_mask))

            # Polyfit
            if self.serit_secim == "ornek":
                # ORNEK BAZLI: her YOLO cizgisi ayri fitlenir, sonra
                # aralarindan genisligi serit olan ve sureklilikle uyumlu
                # CIFT secilir. Konum-tabanli mid-+70 bolmesi kullanilmaz.
                self._bariyer = self.bariyer_bev(bariyerler, img.shape)
                adaylar = self.ornek_fitler(masks, img.shape, self._bariyer)
                self._aday_sayisi = len(adaylar)
                lp, rp = self.cift_sec(adaylar)
                if lp is None and adaylar:
                    self._kare_red = 'GECERLI_CIFT_YOK'
                    # Gecerli cift yok -> en cok pikselli adayi al, tarafini
                    # sureklilik belirlesin (yanlis tarafa kilitlenmeyi onler).
                    en = max(adaylar, key=lambda a: a[2])
                    if self.tek_aday_taraf(en):
                        lp, rp = en[0], None
                        self._span_sol, self._span_sag = en[3], None
                    else:
                        lp, rp = None, en[0]
                        self._span_sol, self._span_sag = None, en[3]
                if adaylar:
                    self._fit_px_ornek = max(a[2] for a in adaylar)
                else:
                    # HIC aday yok -> eski BIRLESTIRILMIS maskeden dene.
                    # Olculdu (joystick_46): ornek bazli secim karelerin
                    # %11.5'inde hic taze aday uretmiyor; o karelerde overlay
                    # BAYAT cizgi gosteriyordu ("cizgi:0"). Birlestirilmis
                    # maske bu karelerin bir kismini kurtarir; secim avantaji
                    # da kaybolmaz cunku bu yola yalnizca aday YOKKEN girilir.
                    lp = self.fit_lane_poly(left_mask)
                    self._span_sol = self._son_span if lp is not None else None
                    rp = self.fit_lane_poly(right_mask)
                    self._span_sag = self._son_span if rp is not None else None
                    # Bariyer elemesi BU yolda da uygulanmali -- yoksa ornek
                    # bazli secim aday uretemedigi karelerde bariyer dibindeki
                    # hat serit sanilip geri geliyor (kare 2293'te goruldu).
                    if lp is not None and self.bariyerde_mi(lp, self._bariyer):
                        lp = None; self._span_sol = None; self._bariyer_elenen += 1
                    if rp is not None and self.bariyerde_mi(rp, self._bariyer):
                        rp = None; self._span_sag = None; self._bariyer_elenen += 1
                    self._fit_px_ornek = self.guven_px(left_mask, right_mask)
            else:
                lp = self.fit_lane_poly(left_mask)
                self._span_sol = self._son_span if lp is not None else None
                rp = self.fit_lane_poly(right_mask)
                self._span_sag = self._son_span if rp is not None else None

            # ⚠️ BAYAT FIT KORUMASI (2026-07-21, ham ZED olcumu)
            # ESKI HATA: miss_count yalnizca MASKE olmayan kareleri sayiyordu.
            # Ama ham kayitta maske %99.5 bulunuyor, buna karsin karelerin
            # %57'sinde HIC FIT cikmiyordu (maske var, cok kisa/seyrek diye
            # eleniyor). Sonuc: lane_lost hic tetiklenmiyor ve node saniyelerce
            # ONCEKI karelerin fitiyle direksiyon veriyordu -- viraja girerken
            # bayat bir duz-yol fiti kullanmak tam da "viraji almiyor"
            # belirtisini uretir. Artik sayac "KULLANILABILIR FIT yok" halini
            # de sayar; koprulenen bosluk yine lane_lost_frames kadar.
            if lp is None and rp is None:
                self.miss_count += 1
                if self.miss_count >= self.lane_lost_frames:
                    if not self.lane_lost:
                        self.lane_lost = True
                        self.get_logger().warn(
                            f"Maske var ama {self.miss_count} frame'dir GECERLI "
                            "FIT yok: bayat fitler birakildi, notr (45).")
                    left_poly = None
                    right_poly = None
                    self.pid.reset()
            else:
                self.miss_count = 0
                if self.lane_lost:
                    self.lane_lost = False
                    self.get_logger().info("Serit tekrar bulundu.")
            self._sol_taze = lp is not None
            self._sag_taze = rp is not None
            if lp is not None:
                left_poly = lp
            if rp is not None:
                right_poly = rp
            if self.cift_ikisi_de_taze and (self._sol_taze != self._sag_taze):
                if self._kare_red == 'OK':
                    self._kare_red = 'TEK_TARAF_TAZE'
                # Yalniz BIR taraf taze: bayat olani CIFTE SOKMA. Tek-fit
                # yoluna dus (taze cizgi + olculen yarim serit) -- bu, bayat
                # bir cizgiyle sahte bir serit uydurmaktan cok daha iyi.
                if self._sol_taze:
                    right_poly = None
                    self._span_sag = None
                else:
                    left_poly = None
                    self._span_sol = None

            # BU karede iki serit de fit edildiyse integral guvenli (Bug 3)
            self._both_detected = (lp is not None and rp is not None)

            # ADAPTIF ILERI BAKIS: olcum, fitlerin verisinin ULASTIGI en uzak
            # satirda yapilir. Virajda sol serit gorus disina cikinca verisi
            # y_eval'e ulasmaz; oray1 UYDURMAK yerine ileri bakisi kisaltiyoruz.
            # None ise veri yalnizca cok yakinda -> olcum guvenilmez, path yaslanir.
            _ye = self.etkin_satir()
            self._y_etkin = _ye
            if _ye is None:
                self._kare_red = 'ADAPTIF_COK_YAKIN'
                # Veri yalnizca cok yakinda: bu karede GUVENILIR olcum yok.
                # Fitleri silip merkeze snap ETME -- son bilinen serit
                # merkezinden devam et, path yaslansin ve guven sonsun.
                # (Snap etmek hayalet hata uretiyordu; bkz. lane_x varsayilani.)
                left_poly = right_poly = None
                y_eval = self.y_eval
                if self._son_lane_x is not None:
                    lane_x = self._son_lane_x
                _olcum_yok = True
            else:
                _olcum_yok = False
            if True:
                if _ye is not None:
                    y_eval = _ye

            if left_poly is not None and right_poly is not None:
                _lxx = self.poly_x(left_poly, y_eval)
                _rxx = self.poly_x(right_poly, y_eval)
                _gen_ok = self.cift_gecerli(_rxx - _lxx)
                _par_ok = self.cift_paralel(left_poly, right_poly)
                if _gen_ok and not _par_ok:
                    self._paralel_red += 1
                    if (self._paralel_red in (1, 50)
                            or self._paralel_red % 500 == 0):
                        self.get_logger().warn(
                            f"Fit cifti PARALEL DEGIL (genislik satirdan "
                            f"satira %{100 * self._paralel_sapma:.0f} "
                            f"degisiyor > %{100 * self.cift_paralel_tol:.0f}) "
                            f"-> muhtemelen bariyer/yol kenari fitlendi, "
                            f"tek fite dusuldu ({self._paralel_red}. kez)")
                self._cift_ok = _gen_ok and _par_ok
                if self._cift_ok:
                    lane_x = (_lxx + _rxx) // 2
                else:
                    # GECERSIZ CIFT: iki fit bir serit olusturmuyor (cok dar
                    # = ayni cizgi+bariyer, cok genis = birden fazla serit).
                    # Orta noktayi ALMA -- o nokta cizginin ustune duser.
                    lane_x, _ = self._sureklilikle_merkez(_lxx, _rxx, y_eval)
                    self._cift_red += 1
                    if self._cift_red in (1, 20) or self._cift_red % 200 == 0:
                        self.get_logger().warn(
                            f"Gecersiz serit cifti ({_rxx - _lxx:.0f} px, beklenen "
                            f"{self.lane_w_px or 0:.0f}+-%{100*self.lane_w_tol:.0f}) "
                            f"-> sureklilikle tek cizgi yorumu. "
                            f"toplam {self._cift_red}")
                lane_slope = self._egim(left_poly, right_poly, y_eval)
            elif left_poly is not None:
                lane_x = self._tek_fit_merkez(left_poly, True, y_eval)
                lane_slope = self._egim(left_poly, None, y_eval)
            elif right_poly is not None:
                lane_x = self._tek_fit_merkez(right_poly, False, y_eval)
                lane_slope = self._egim(None, right_poly, y_eval)

        # Save polynomials
        self.left_prev = left_poly
        self.right_prev = right_poly

        # DRAW BEV → image projection
        overlay = original.copy()

        # FITLER -- her biri YALNIZ KENDI VERI ARALIGINDA cizilir.
        # Eskiden hepsi 0.55*H..H arasinda ciziliyordu, verisi olmayan yerde de.
        # Sonuc yaniltici: kisa/seyrek bir maskeye oturan DUZ fit, verisi genis
        # olan egri fitle "celisiyor" gibi gorunuyordu (operator gozlemi:
        # "mavi duz bukuluyor, kirmizi parabolik"). Ikisi de dogruydu; yalniz
        # gecerlilik araliklari farkliydi. Artik cizgi bittigi yerde biter.
        for _poly, _span, _col in ((left_poly, self._span_sol, (255, 0, 0)),
                                   (right_poly, self._span_sag, (0, 0, 255))):
            if _poly is None:
                continue
            if _span:
                _y0 = max(int(self.img_h * 0.55), int(_span[0]))
                _y1 = min(self.img_h - 1, int(_span[1]))
            else:                      # bayat fit: araligi bilinmiyor
                _y0, _y1 = int(self.img_h * 0.55), self.img_h - 1
            if _y1 - _y0 < 4:
                continue
            _pts = self.bev_to_image(
                [(self.poly_x(_poly, _y), _y)
                 for _y in np.linspace(_y0, _y1, 40).astype(int)])
            for _i in range(len(_pts) - 1):
                cv2.line(overlay, tuple(_pts[_i]), tuple(_pts[_i + 1]), _col, 3)

        # TAZELIK BURADA hesaplanir, cizimden ONCE (2026-08-21). Asagidaki
        # "PATH YASI" blogu bunu kullanir; iki yerde AYRI hesaplanmamalidir.
        # (Ilk denemede cizim `self._path_durum`'a bakiyordu, ama o degisken
        # cizimden SONRA atandigi icin BIR ONCEKI karenin durumunu okuyordu --
        # kesikli cizim hic gorunmedi. Bir mekanizmanin hic tetiklenmemesi,
        # baglanmadiginin kanitidir.)
        _taze = (((locals().get('lp') is not None)
                  or (locals().get('rp') is not None))
                 and not locals().get('_olcum_yok', False))

        # Center line (yellow)
        bottom = int(self.img_h * 0.90)
        top = int(self.img_h * 0.55)
        # ILERI BAKIS ISARETI (mor yatay cizgi): serit merkezinin OLCULDUGU
        # satir. Viraj sorununu ayiklarken bunun ne kadar ileride oldugunu
        # gormek kritik — eskiden 0.90 (burun, ~2.2 m) sabitti.
        _ylk = self._y_etkin if self._y_etkin is not None else self.y_eval
        lk_img = self.bev_to_image([(int(self.img_w * 0.15), _ylk),
                                    (int(self.img_w * 0.85), _ylk)])
        if len(lk_img) == 2:
            cv2.line(overlay, tuple(lk_img[0]), tuple(lk_img[1]), (255, 0, 255), 2)
            cv2.putText(overlay, f"{self._row_to_m(_ylk):.1f}m",
                        (tuple(lk_img[1])[0] + 4, tuple(lk_img[1])[1] + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        # SARI = serit orta cizgisi. Eskiden (lane_x, alt)-(lane_x, ust) yani
        # TEK bir x'te DIKEY ciziliyordu -> virajda bile duz gorunuyordu ve
        # "merkez donmuyor" izlenimi veriyordu. Artik gercek orta polinomu
        # ornekleniyor, virajda kivriliyor. Bu yalniz cizim degil TESHIS: egri
        # duz kaliyorsa fitler virajı gormuyor demektir.
        # BAYAT YOL KESIKLI CIZILIR (2026-08-21). Operator virajda "sari cizgi
        # anlik yanlis yone donuyor" diye bildirdi; incelendiginde o karelerin
        # ADAPTIF_COK_YAKIN oldugu, cizilen yolun 0.2 s ONCEKI yol oldugu ve
        # komutun zaten notre sonumlendigi goruldu (virajdaki kor karelerde
        # ortalama |steer-45| = 1.3, %78'i notrun 3 birim icinde). Yani arac o
        # bozuk cizgiyi TAKIP ETMIYOR -- ama overlay bayat yolu TAZE yolla
        # birebir ayni ciziyordu, dolayisiyla bakan kisi kontrol hatasi
        # sanıyordu. Kesikli + soluk cizim bu iki durumu ayirir.
        _bayat = not _taze
        _renk = (0, 170, 170) if _bayat else (0, 255, 255)
        _kal = 2 if _bayat else 3

        def _ciz(pts):
            for _i in range(len(pts) - 1):
                if _bayat and _i % 2:          # kesikli
                    continue
                cv2.line(overlay, tuple(pts[_i]), tuple(pts[_i + 1]), _renk, _kal)

        _cp = self.merkez_poly(left_poly, right_poly)
        if _cp is not None:
            _ys = np.linspace(bottom, top, 24).astype(int)
            _ciz(self.bev_to_image([(self.poly_x(_cp, _y), _y) for _y in _ys]))
        else:
            cen_img = self.bev_to_image(
                [(lane_x, _y) for _y in np.linspace(bottom, top, 24).astype(int)])
            _ciz(cen_img)

        # Referans merkez cizgisi (YESIL): arac tam ortadayken sari cizginin
        # oturmasi gereken yer. Sari-yesil acikligi = anlik error (kalibrasyon).
        ref_x = int(center_x_bev + self.err_offset)
        ref_img = self.bev_to_image([(ref_x, bottom), (ref_x, top)])
        if len(ref_img) == 2:
            cv2.line(overlay, tuple(ref_img[0]), tuple(ref_img[1]), (0, 255, 0), 2)

        # Serit genisligi (px): iki fit de varken olculur, EMA ile yumusatilir;
        # tek-fit karelerinde son bilinen genislik korunur (metre donusumu icin).
        # NOT: genislik ARTIK y_eval satirinda olculur (eskiden 0.90 sabitti).
        # _half_lane() tek-serit karelerinde bu degerin yarisini y_eval'de
        # uyguluyor; ikisi ayni satirda olmazsa BEV carpikligi merkezi kaydirir.
        if left_poly is not None and right_poly is not None:
            _yw = self._y_etkin if self._y_etkin is not None else self.y_eval
            _lx = self.poly_x(left_poly, _yw)
            _rx = self.poly_x(right_poly, _yw)
            w_px = _rx - _lx
            # SADECE gecerli cift EMA'yi ve ofsetleri gunceller. Eskiden
            # "w_px > 80" yeterliydi ve 96 px'lik sahte cift hem lane_w_px'i
            # hem off_sol/off_sag'i zehirliyordu; _half_lane() ve
            # _tek_fit_merkez() o zehirli degeri SONRAKI karelerde de
            # kullandigi icin tek bir kotu kare uzun sure etkiliyordu.
            if getattr(self, "_cift_ok", False) and self.cift_gecerli(w_px):
                _c = (_lx + _rx) / 2.0
                self.off_sol = _c - _lx
                self.off_sag = _rx - _c
                self.lane_w_px = (float(w_px) if self.lane_w_px is None
                                  else 0.9 * self.lane_w_px + 0.1 * w_px)

        # PATH YASI: bu karede TAZE fit var mi? (lp/rp taze fitlerdir; maske
        # yoksa veya hepsi elendiyse eski left_prev/right_prev kullanilmistir)
        # _taze YUKARIDA, cizimden once hesaplandi (tek kaynak).
        self._red_sayac[self._kare_red] = self._red_sayac.get(self._kare_red, 0) + 1
        if _taze:
            self._path_yasi = 0
            self._son_taze_t = t
        else:
            self._path_yasi += 1
        # YAS'i saniye cinsinden tut: kare sayisi FPS'e bagli, saniye degil.
        # (Aractaki FPS 13-29 arasi degisiyor; esikler saniyeden verilmeli.)
        self._path_yas_s = (0.0 if self._son_taze_t is None
                            else max(0.0, t - self._son_taze_t))
        self._path_durum = ('TAZE' if self._path_yasi == 0 else
                            'TAHMIN' if self._path_yas_s < self.guven_zayif_s else
                            'ZAYIF' if self._path_yas_s < self.guven_kayip_s else
                            'KAYIP')
        # ---- GUVEN SONUMU: ZAMAN TABANLI + TABAN DEGERLI (2026-08-22) ----
        # ESKI: guven = 1 - _path_yasi / path_max_age  -- yani KARE sayisiyla.
        # Iki kusuru vardi, ikisi de otonom kayitta olculdu:
        #  (1) FPS'E BAGLI. Aractaki FPS 13-29 arasi oynuyor; 10 kare 28 FPS'te
        #      0.36 s, 13 FPS'te 0.77 s. Ayni bayatlik farkli yetki veriyordu.
        #      CLAUDE.md'nin ID-2 yas alani icin yazdigi kuralin ta kendisi:
        #      "yas SANIYE cinsinden tasinir, kare degil".
        #  (2) DURUM MAKINESIYLE UYUMSUZ. Beyin ZAYIF'ta "yavasla ama SUR"
        #      (4 km/h), KAYIP'ta "surun" (2 km/h) diyor; ama guven ZAYIF'ta
        #      zaten 0'a inmis oluyordu -> arac SURUYOR ama direksiyon yetkisi
        #      SIFIR. Olculdu (joystick_46): ZAYIF karelerde medyan guven 0.00,
        #      %94'u 0.5 altinda; KAYIP'ta %100. `slalom_0821_1526` t=46 s'de
        #      gercek hata -365 px (-2.95 m), R=20 m viraj, komut 45 (notr).
        #      Virajda sifir yetkiyle surmek = pist disi.
        # YENI: sonum ZAMANLA ve durum makinesinin ESIKLERIYLE hizali;
        # ayrica TABAN var -- bayat bir yol, hicbir yoldan iyidir.
        # Emniyet gerekcesi: taban yalniz beyin AYNI ANDA hizi kiserken
        # gecerli (ZAYIF 4 km/h, KAYIP 2 km/h, 3 s sonra kontrollu durus).
        # Yani "azaltilmis yetki + azaltilmis hiz", "sifir yetki" degil.
        if self.path_max_age <= 0:
            self._path_guven = 1.0
        elif self._path_yas_s <= self.guven_zayif_s:
            self._path_guven = 1.0
        elif self._path_yas_s >= self.guven_kayip_s:
            self._path_guven = self.guven_taban
        else:
            _f = ((self._path_yas_s - self.guven_zayif_s)
                  / max(1e-3, self.guven_kayip_s - self.guven_zayif_s))
            self._path_guven = 1.0 - _f * (1.0 - self.guven_taban)

        # SAG SERIT GECISI: hedef bir serit boyu sicradiysa (= serit
        # degistiriyoruz) hiz sinirli tasi. Kucuk degisimler dokunulmadan
        # gecer. sag_serit kapaliyken bu cagri lane_x'i aynen dondurur.
        lane_x = self._serit_gecis(lane_x, self.lane_lost)

        # Sureklilik kaynagi: serit kayipken GUNCELLEME (bayat merkez, yanlis
        # tarafa kilitlenmeyi kalicilastirirdi).
        if not self.lane_lost:
            self._son_lane_x = float(lane_x)

        # Steering -- TEK KONTROL YOLU. Kontrol matematigi artik
        # direksiyon_hesapla() icinde; masa testleri de AYNI metodu cagirir
        # (bkz. o metodun basindaki not).
        # heading_gain=30 su kapali cevrim taramasiyla secilmisti (450 kare,
        # olu bant 5): k=0 -> 0.42 m | k=30 -> 0.24 m | k=60 -> 0.39 m |
        # k=100 -> 0.40 m. O tarama Kp=0.08 ve steer_target_gain=-0.75
        # gecerliyken yapildi; bugunku esdegeri icin declare_parameter'daki
        # nota bak.
        steer, err = self.direksiyon_hesapla(
            lane_x, center_x_bev, lane_slope,
            self.merkez_poly(left_poly, right_poly))
        # kayan ortalama (3 sn) -> kalibrasyon degeri overlay'den okunsun
        self.err_hist.append((t, err))
        while self.err_hist and t - self.err_hist[0][0] > 3.0:
            self.err_hist.popleft()
        avg_err = sum(e for _, e in self.err_hist) / len(self.err_hist)

        # Hata: piksel + (serit genisligi biliniyorsa) METRE karsiligi
        if self.lane_w_px:
            err_m = err * self.lane_width_m / self.lane_w_px
            err_txt = f"Error: {int(err)}px ({err_m:+.2f}m)"
        else:
            err_txt = f"Error: {int(err)}px"
        lw_txt = "-" if self.lane_w_px is None else f"{int(self.lane_w_px)}px"
        # CIZGI SOZLUGU -- "yesil neden donmuyor" sorusu tekrar cikmasin:
        # yesil serit ortasi DEGIL, aracin kendi ekseni (merkez+err_offset) ve
        # tanimi geregi dikeydir. Egriye oturmasi gereken SARI'dir.
        _pd = ("path: TAZE" if self._path_yasi == 0 else
               f"path: {self._path_durum} {self._path_yas_s:.2f}s "
               f"guven {self._path_guven:.2f}")
        # SAGA YASLA: sabit x=img_w-210 ile "path: ZAYIF 0.33s guven 0.77"
        # ~250 px surdugu icin sag kenardan tasiyordu ve GUVEN SAYISI
        # gorunmuyordu (operator ekran goruntusunde tespit edildi, 2026-08-22).
        # Guven, bayat karede direksiyon yetkisinin ne kadar kaldigini soyleyen
        # sayidir; kesilmesi teshisi korlestiriyordu.
        (_pw, _ph), _ = cv2.getTextSize(_pd, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.putText(overlay, _pd, (max(2, self.img_w - _pw - 6), 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0) if self._path_yasi == 0 else (0, 165, 255), 1)
        if self.serit_secim == "ornek":
            cv2.putText(overlay, f"cizgi:{self._aday_sayisi}",
                        (self.img_w - 90, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 255), 1)
        cv2.putText(overlay, "mavi=sol  kirmizi=sag  SARI=serit ortasi  "
                    "yesil=arac ekseni", (8, self.img_h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (210, 210, 210), 1)
        if not getattr(self, "_cift_ok", True) and left_poly is not None \
                and right_poly is not None:
            cv2.putText(overlay, "CIFT RED", (self.img_w - 130, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2)
        cv2.putText(overlay, f"AvgErr: {avg_err:+.1f}  LaneW: {lw_txt}", (10, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(overlay, err_txt, (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        # Hatanin ayrisimi: yanal (konum) + yon onizlemesi. err_offset
        # kalibrasyonunda YALNIZ Yanal okunur.
        cv2.putText(overlay,
                    f"  Yanal:{self._lat_err:+.0f}  Yon:{self._head_err:+.0f}",
                    (10, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
        cv2.putText(overlay, f"Steering: {steer}", (10, 172),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        self._son_steer = steer   # harici teshis araclari icin
        msg = String()
        # ID-2 SOZLESMESI: 2,<steer>,<guven>,<yas_s>,<durum>
        # data[1] (steer) yerinde kaldi -> eski ayristiricilar calisir.
        msg.data = (f"2,{steer},{self._path_guven:.2f},"
                    f"{self._path_yas_s:.2f},{self._path_durum}")
        self.pub.publish(msg)

        # Kayit aktifse, ekranda gosterilen overlay'i videoya yaz
        if self.video_writer is not None:
            self.video_writer.write(overlay)

        if self.debug_pub is not None:
            ok, buf = cv2.imencode(".jpg", overlay, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ok:
                dbg = CompressedImage()
                dbg.header = in_header
                dbg.format = "jpeg"
                dbg.data = buf.tobytes()
                self.debug_pub.publish(dbg)

        # BEV teshis goruntusu (homografi/olcek sagmasi icin)
        if self.bev_pub is not None:
            try:
                bev_dbg = self._bev_debug(img, bev, left_poly, right_poly, lane_x)
                ok, buf = cv2.imencode(".jpg", bev_dbg,
                                       [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ok:
                    bmsg = CompressedImage()
                    bmsg.header = in_header
                    bmsg.format = "jpeg"
                    bmsg.data = buf.tobytes()
                    self.bev_pub.publish(bmsg)
            except Exception as exc:
                self.get_logger().warn(f"BEV teshis goruntusu uretilemedi: {exc}",
                                       throttle_duration_sec=10.0)

        if self.show_window:
            cv2.imshow("Original with BEV Lanes", overlay)
            cv2.setMouseCallback("Original with BEV Lanes", mouse_callback)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('r'):          # kaydi baslat/durdur
                self._toggle_record(overlay)


# ---------------- MAIN --------------------
def main(args=None):
    rclpy.init(args=args)
    node = LaneFollowerNode()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        # SIGTERM/Ctrl+C'de 'rcl_shutdown already called' traceback'i birakmasin
        # -- arac log'unun sonunda gercek bir hatayi gizleyebiliyor.
        pass
    finally:
        if node.video_writer is not None:   # acik kayit varsa kapat
            node.video_writer.release()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
