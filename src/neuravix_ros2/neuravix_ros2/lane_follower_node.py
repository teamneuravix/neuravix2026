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
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import String

# Vision
from cv_bridge import CvBridge
import cv2
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
    def __init__(self, Kp=0.08, Ki=0.001, Kd=0.01, i_term_max=10.0, i_leak=0.98):
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
            return None

        # ustteki bozuk BEV bolgesi silinir (fit_far_frac parametreli, eski
        # sabit 0.55 = ~5.8 m; bkz. __init__'teki ILERI BAKIS aciklamasi)
        y_min = int(self.img_h * self.fit_far_frac)
        keep = ys >= y_min
        ys = ys[keep]
        xs = xs[keep]

        if len(xs) < max(15, self.fit_min_points // 2):
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
            return None

        try:
            # Agirlik: uss BUYUDUKCE fit yakin satirlara kilitlenir ve ileri
            # bakis islevsiz kalir (uzatilan dogru yine burun tegetidir).
            # fit_weight_pow=1 -> pencerenin tamami katkida bulunur.
            if self.fit_weight_pow > 0:
                w = (ys / np.max(ys)) ** self.fit_weight_pow
            else:
                w = None

            poly = np.polyfit(ys, xs, self.fit_degree, w=w)

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
            #     2.5 -> ~%75  / %100    IQR ~55/39  <- SECILEN
            #     3.0 -> %78.5 / %100    IQR 56/39
            #     5.0 -> %86.7 / %100    IQR 78/39   <- IQR firliyor = COP giriyor
            # IQR 3.0'a kadar sabit; 2.5 kazancin cogunu alip 5.0 ucurumundan
            # emniyetli uzaklikta kaliyor. Yatay cizgileri (dur cizgisi, yaya
            # gecidi) elemeye devam eder -- onlarin egimi cok daha buyuktur.
            slope = float(np.polyval(np.polyder(poly), self.y_eval))
            if abs(slope) > self.fit_max_slope:
                return None

            return poly

        except Exception:
            return None

    def _egim(self, lp, rp, y):
        """Seridin y satirindaki yonu (dx/dy). Iki fit varsa ortalamasi.
        Yon onizlemesi (heading feedforward) icin kullanilir: BEV'de saga
        kivrilan seritte dx/dy < 0 olur."""
        e = [float(np.polyval(np.polyder(p), y))
             for p in (lp, rp) if p is not None]
        return (sum(e) / len(e)) if e else None

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
        for poly, col in ((left_poly, (255, 0, 0)), (right_poly, (0, 0, 255))):
            if poly is None:
                continue
            pts = [(self.poly_x(poly, y), y) for y in ys]
            for i in range(len(pts) - 1):
                cv2.line(bev_img, pts[i], pts[i + 1], col, 2)

        # --- MERKEZ (sari) ve REFERANS MERKEZ (yesil) ---
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
        self.src_pts = np.float32([
            [170, 357],   # bottom-left
            [639, 358],   # bottom-right
            [367, 210],   # top-right
            [312, 210],   # top-left
        ])

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
        self.declare_parameter("fit_degree", 1)
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
        self.declare_parameter("fit_min_span_frac", 0.05)  # eski sabit: 0.15
        # Egim kilavuzu: bkz. fit_lane_poly icindeki ayrintili olcum notu.
        # Eski sabit 1.0 virajda gecerli fitleri eliyordu (tek-fit karelerinin
        # %81.5'i bu kurala takiliyordu).
        self.declare_parameter("fit_max_slope", 2.5)      # eski sabit: 1.0
        self.fit_max_slope = float(self.get_parameter("fit_max_slope").value)
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
        self.declare_parameter("heading_gain", 30.0)
        self.heading_gain = float(self.get_parameter("heading_gain").value)
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
        self.declare_parameter("err_offset", 0.0)
        self.err_offset = float(self.get_parameter("err_offset").value)
        self.err_hist = deque()      # (t, err) -> son ~3 sn kayan ortalama

        # Hatanin METRE karsiligi: err_m = err_px * lane_width_m / lane_w_px.
        # lane_w_px, iki fit de varken y_eval'de olculur ve EMA ile yumusatilir.
        # Gercek pistte iki beyaz cizgi arasi olculdu (2026-07-20): yer yer
        # degisken ama cogu yerde ~2.96 m -> 3.0 aliniyor. CARLA seritleri 3.5 m,
        # simde istenirse -p lane_width_m:=3.5 ile geri alinabilir.
        self.declare_parameter("lane_width_m", 3.0)
        self.lane_width_m = float(self.get_parameter("lane_width_m").value)
        self.lane_w_px = None

        # Load YOLO
        share_dir = get_package_share_directory("neuravix_ros2")
        model_path = os.path.join(share_dir, "models", "best_yolo11.pt")
        self.model = YOLO(model_path)
        self.get_logger().info("YOLO loaded.")

        # ROS
        # camera_topic parametreli: sim'de CARLA overlay çıktısı, gerçek
        # araçta launch'tan Zed2 topic'ine (örn. /zed/zed_node/rgb/image_rect_color)
        # yönlendirilir. tabela_tespit_node.py / obstacle_lidar_node.py ile
        # aynı desen (camera_topic / lidar_topic parametreleri).
        self.declare_parameter("camera_topic", "/carla/ego_vehicle/rgb_overlay/image")
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
            f"agirlik^{self.fit_weight_pow:.0f}, derece={self.fit_degree} | "
            f"Kp={self.pid.Kp} err_offset={self.err_offset:.0f}px "
            f"lane_width={self.lane_width_m} m")

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
        results = self.model(img, verbose=False)
        masks = []
        for r in results:
            if r.masks is not None:
                for m in r.masks.data:
                    masks.append(m.cpu().numpy())

        center_x_bev = self.img_w // 2
        lane_x = center_x_bev
        # Seridin y_eval'deki YONU (dx/dy). Yon onizlemesi icin; fit yoksa None
        lane_slope = None

        # Eğer hiç maske yoksa fallback
        left_poly = self.left_prev
        right_poly = self.right_prev
        bev = None            # BEV teshis goruntusu icin (maske yoksa None)

        if len(masks) == 0:
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
                    lane_x = (lx + rx) // 2
                    lane_slope = self._egim(left_poly, right_poly, y_eval)
                elif left_poly is not None:
                    lane_x = self.poly_x(left_poly, y_eval) + self._half_lane()
                    lane_slope = self._egim(left_poly, None, y_eval)
                elif right_poly is not None:
                    lane_x = self.poly_x(right_poly, y_eval) - self._half_lane()
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

            # Polyfit
            lp = self.fit_lane_poly(left_mask)
            rp = self.fit_lane_poly(right_mask)

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
            if lp is not None:
                left_poly = lp
            if rp is not None:
                right_poly = rp

            # BU karede iki serit de fit edildiyse integral guvenli (Bug 3)
            self._both_detected = (lp is not None and rp is not None)

            y_eval = self.y_eval          # ileri bakis (lookahead_frac)

            if left_poly is not None and right_poly is not None:
                lane_x = (self.poly_x(left_poly, y_eval) +
                          self.poly_x(right_poly, y_eval)) // 2
                lane_slope = self._egim(left_poly, right_poly, y_eval)
            elif left_poly is not None:
                lane_x = self.poly_x(left_poly, y_eval) + self._half_lane()
                lane_slope = self._egim(left_poly, None, y_eval)
            elif right_poly is not None:
                lane_x = self.poly_x(right_poly, y_eval) - self._half_lane()
                lane_slope = self._egim(None, right_poly, y_eval)

        # Save polynomials
        self.left_prev = left_poly
        self.right_prev = right_poly

        # DRAW BEV → image projection
        overlay = original.copy()

        # Left
        if left_poly is not None:
            ys = np.linspace(self.img_h * 0.55, self.img_h - 1, 40).astype(int)
            pts = [(self.poly_x(left_poly, y), y) for y in ys]
            imgpts = self.bev_to_image(pts)
            for i in range(len(imgpts) - 1):
                cv2.line(overlay, tuple(imgpts[i]), tuple(imgpts[i+1]), (255, 0, 0), 3)

        # Right
        if right_poly is not None:
            ys = np.linspace(self.img_h * 0.55, self.img_h - 1, 40).astype(int)
            pts = [(self.poly_x(right_poly, y), y) for y in ys]
            imgpts = self.bev_to_image(pts)
            for i in range(len(imgpts) - 1):
                cv2.line(overlay, tuple(imgpts[i]), tuple(imgpts[i+1]), (0, 0, 255), 3)

        # Center line (yellow)
        bottom = int(self.img_h * 0.90)
        top = int(self.img_h * 0.55)
        # ILERI BAKIS ISARETI (mor yatay cizgi): serit merkezinin OLCULDUGU
        # satir. Viraj sorununu ayiklarken bunun ne kadar ileride oldugunu
        # gormek kritik — eskiden 0.90 (burun, ~2.2 m) sabitti.
        lk_img = self.bev_to_image([(int(self.img_w * 0.15), self.y_eval),
                                    (int(self.img_w * 0.85), self.y_eval)])
        if len(lk_img) == 2:
            cv2.line(overlay, tuple(lk_img[0]), tuple(lk_img[1]), (255, 0, 255), 2)
            cv2.putText(overlay, f"{self.lookahead_m:.1f}m",
                        (tuple(lk_img[1])[0] + 4, tuple(lk_img[1])[1] + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        cen_pts = [(lane_x, bottom), (lane_x, top)]
        cen_img = self.bev_to_image(cen_pts)
        if len(cen_img) == 2:
            cv2.line(overlay, tuple(cen_img[0]), tuple(cen_img[1]), (0, 255, 255), 3)

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
            w_px = (self.poly_x(right_poly, self.y_eval)
                    - self.poly_x(left_poly, self.y_eval))
            if w_px > 80:   # fiziksel olarak anlamsiz dar/ters fitleri sayma
                self.lane_w_px = (float(w_px) if self.lane_w_px is None
                                  else 0.9 * self.lane_w_px + 0.1 * w_px)

        # Steering
        if self.lane_lost:
            err = 0.0        # serit yokken err_offset notr 45'i bozmasin
        else:
            err = lane_x - center_x_bev - self.err_offset
            # YON ONIZLEMESI (heading feedforward): fit'in y_eval'deki EGIMI
            # seridin o noktadaki yonunu verir. Yalnizca konum hatasina bakmak
            # "viraja girdikten SONRA tepki" demektir -- araçta gozlenen tam da
            # buydu: sag viraja girerken direksiyon once notr/hafif sol kaliyor,
            # ancak hata 80+ px'e ciktiginda saga kiriyordu. Egim terimi virajin
            # BASLADIGINI hata buyumeden haber verir.
            # Isaret: BEV'de saga kivrilan seritte dx/dy < 0; saga kirmak icin
            # err POZITIF olmali (steer = 45 - Kp*err) -> err -= k*egim.
            # k=30 GERCEK kayitla kapali cevrimde secildi (450 kare, olu bant 5):
            #     k=0   -> ort hata 0.42 m, son 0.25 m, maks ham 10.2
            #     k=30  -> ort hata 0.24 m, son 0.08 m, maks ham  8.0   <- EN IYI
            #     k=60  -> ort hata 0.39 m, son 0.30 m
            #     k=100 -> ort hata 0.40 m, son 0.49 m
            # Yani hem daha isabetli hem daha YUMUSAK direksiyon.
            if self.heading_gain and lane_slope is not None:
                err -= self.heading_gain * lane_slope
        # kayan ortalama (3 sn) -> kalibrasyon degeri overlay'den okunsun
        self.err_hist.append((t, err))
        while self.err_hist and t - self.err_hist[0][0] > 3.0:
            self.err_hist.popleft()
        avg_err = sum(e for _, e in self.err_hist) / len(self.err_hist)
        # Conditional integration (Bug 3): integrali yalnizca iki serit de
        # goruldu VE hata bandda iken birikir -> sistematik bias mihlamaz.
        allow_i = self._both_detected and (abs(err) <= self.i_error_band)
        out = self.pid.calculate(err, allow_integral=allow_i)
        steer = 45 - out  #0.05 olcekleme
        steer = max(15, min(75, int(steer))) #sınırlandırma

        # Hata: piksel + (serit genisligi biliniyorsa) METRE karsiligi
        if self.lane_w_px:
            err_m = err * self.lane_width_m / self.lane_w_px
            err_txt = f"Error: {int(err)}px ({err_m:+.2f}m)"
        else:
            err_txt = f"Error: {int(err)}px"
        lw_txt = "-" if self.lane_w_px is None else f"{int(self.lane_w_px)}px"
        cv2.putText(overlay, f"AvgErr: {avg_err:+.1f}  LaneW: {lw_txt}", (10, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(overlay, err_txt, (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(overlay, f"Steering: {steer}", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        msg = String()
        msg.data = f"2,{steer}"
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
    except KeyboardInterrupt:
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
