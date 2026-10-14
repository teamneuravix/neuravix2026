#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Updated on Tue June 3 2025
Otonom Araç Tabela Tespit Algoritması - CARLA Entegrasyonu
ROS2 Node Implementation

Özellikler:
- CARLA kamera topic'inden görüntü alma
- Preprocessing (CLAHE, Gaussian Blur, Sharpening)
- Confidence Threshold ve NMS ayarları
- Temporal Filtering (ardışık frame tutarlılığı)
- İstatistik takibi
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque
from dataclasses import dataclass
from typing import List, Optional
import time

from ament_index_python.packages import get_package_share_directory
from rclpy.qos import (qos_profile_sensor_data, QoSProfile,
                       QoSReliabilityPolicy, QoSHistoryPolicy)
import os

# /master ID-3'te yayinlanan sinif id'si KANONIKTIR (decision_brain'de
# tanimli), YOLO'nun model ici indeksi degil. Cevrimi ad uzerinden
# decision_brain yapar; boylece model degistiginde beyin/kontrol dugumleri
# degismez. Bkz. decision_brain.py "MODEL SINIF ADI -> KANONIK ID".
from .decision_brain import (canonical_sign_id, SIGN_NAMES,
                             KIRMIZI_ISIK, SARI_ISIK, YESIL_ISIK)


@dataclass
class Detection:
    """Tek bir tespit için veri yapısı"""
    bbox: np.ndarray      # [x1, y1, x2, y2]
    confidence: float
    class_id: int
    class_name: str
    # Mesafe cozumlemesi publish_sign_to_master icinde doldurulur; overlay
    # ayni degeri cizsin diye Detection uzerinde tasinir (sahada kalibrasyon
    # ekrandaki degeri okuyarak yapiliyor).
    distance: Optional[float] = None
    distance_src: int = 0          # 1 = ZED derinligi, 0 = bbox tahmini


class TemporalFilter:
    """
    Temporal Filtering: Ardışık frame'lerde tutarlılık sağlar
    Yanlış pozitifleri azaltır, kararlı tespitler üretir
    """

    def __init__(self, buffer_size: int = 5, min_hits: int = 3, iou_threshold: float = 0.4):
        self.buffer_size = buffer_size
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.buffer: deque = deque(maxlen=buffer_size)

    def calculate_iou(self, box1: np.ndarray, box2: np.ndarray) -> float:
        """İki bounding box arasındaki IoU hesapla"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0

    def find_similar_detection(self, det: Detection, frame_dets: List[Detection]) -> Optional[Detection]:
        """Verilen tespite benzer tespit bul"""
        best_match = None
        best_iou = self.iou_threshold

        for other in frame_dets:
            if det.class_id != other.class_id:
                continue
            iou = self.calculate_iou(det.bbox, other.bbox)
            if iou > best_iou:
                best_iou = iou
                best_match = other
        return best_match

    def update(self, detections: List[Detection]) -> List[Detection]:
        """Yeni tespitleri filtrele ve kararlı olanları döndür"""
        self.buffer.append(detections)

        if len(self.buffer) < self.min_hits:
            return detections

        stable_detections = []

        for det in detections:
            hit_count = 0
            confidence_sum = det.confidence
            bbox_sum = det.bbox.copy().astype(float)

            for frame_dets in list(self.buffer)[:-1]:
                similar = self.find_similar_detection(det, frame_dets)
                if similar is not None:
                    hit_count += 1
                    confidence_sum += similar.confidence
                    bbox_sum += similar.bbox

            if hit_count >= self.min_hits - 1:
                total_hits = hit_count + 1
                smoothed_det = Detection(
                    bbox=(bbox_sum / total_hits).astype(int),
                    confidence=confidence_sum / total_hits,
                    class_id=det.class_id,
                    class_name=det.class_name
                )
                stable_detections.append(smoothed_det)

        return stable_detections

    def reset(self):
        """Buffer'ı temizle"""
        self.buffer.clear()


class ImagePreprocessor:
    """Görüntü ön işleme sınıfı"""

    def __init__(self,
                 enable_clahe: bool = True,
                 enable_denoise: bool = True,
                 enable_sharpen: bool = False,
                 clahe_clip_limit: float = 2.0,
                 clahe_grid_size: tuple = (8, 8),
                 blur_kernel_size: int = 3):

        self.enable_clahe = enable_clahe
        self.enable_denoise = enable_denoise
        self.enable_sharpen = enable_sharpen
        self.clahe_clip_limit = clahe_clip_limit
        self.clahe_grid_size = clahe_grid_size
        self.blur_kernel_size = blur_kernel_size

        if self.enable_clahe:
            self.clahe = cv2.createCLAHE(
                clipLimit=self.clahe_clip_limit,
                tileGridSize=self.clahe_grid_size
            )

        self.sharpen_kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

    def apply_clahe(self, frame: np.ndarray) -> np.ndarray:
        """CLAHE ile kontrast iyileştirme"""
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = self.clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    def apply_denoise(self, frame: np.ndarray) -> np.ndarray:
        """Hafif Gaussian blur ile gürültü azaltma"""
        return cv2.GaussianBlur(frame, (self.blur_kernel_size, self.blur_kernel_size), 0)

    def apply_sharpen(self, frame: np.ndarray) -> np.ndarray:
        """Keskinleştirme filtresi"""
        return cv2.filter2D(frame, -1, self.sharpen_kernel)

    def process(self, frame: np.ndarray) -> np.ndarray:
        """Tüm aktif ön işlemleri uygula"""
        processed = frame.copy()

        if self.enable_clahe:
            processed = self.apply_clahe(processed)
        if self.enable_denoise:
            processed = self.apply_denoise(processed)
        if self.enable_sharpen:
            processed = self.apply_sharpen(processed)

        return processed


class TabelaTespitNode(Node):
    def __init__(self):
        super().__init__('tabela_tespit_node')

        # ============== TEMEL PARAMETRELER ==============
        #self.declare_parameter('camera_topic', '/carla/ego_vehicle/rgb_front/image')
        # VARSAYILAN GERCEK ARAC (26.08.2026). Parametre unutulursa dugumun
        # SESSIZCE hicbir sey yayinlamamasi yerine araca bakmasi yeglenir --
        # lane_follower'da da ayni karar verilmisti.
        # ⚠️ CARLA'da BU IKISI DE ELLE GECILMELI (ikisi AYNI kaynagi
        # gostermeli, yoksa derinlik hic gelmez ve dugum sessizce bbox
        # tahminine duser):
        #   -p camera_topic:=/carla/ego_vehicle/rgb_overlay/image
        #   -p depth_topic:=/carla/ego_vehicle/rgb_overlay/depth
        self.declare_parameter('camera_topic', '/zed/zed_node/rgb/image_rect_color')
        # Yuklenecek agirlik dosyasi (share/neuravix_ros2/models altinda).
        # Parametre oldugu icin ayni dugum ikinci bir ornekle farkli bir model
        # calistirabilir: tabelalar best6.pt, trafik isiklari ayri egitilmis
        # 2 sinifli model (green/red). Ikisi de /master'a KANONIK id yayinlar,
        # beyin ikisini de ayirt etmeden dogru isler.
        self.declare_parameter('model_file', 'makarayizabi2.pt')
        # YOLO cikarim cozunurlugu. best6 640'ta egitildi; 960'ta egitilen
        # modeller (eda.pt, isik modeli) 640'ta kucuk nesneyi kacirabilir.
        # ⚠️ VARSAYILAN MODELE UYDURULDU (25.08.2026): makarayizabi2.pt
        # imgsz=960 ile egitildi, ultralytics ise tahminde egitim boyutunu
        # KULLANMAZ, kendi varsayilani 640'tir. 640'ta trafik isigi gibi
        # kucuk nesneler kaciyor. 640'a donmek: -p imgsz:=640
        # (Bu satir ZED-derinlik birlestirmesinde geri getirildi: gelen
        #  surumde 640'a donmustu, o dal bu duzeltmeden onceki tabandan
        #  ayrilmisti.)
        self.declare_parameter('imgsz', 960)
        # Yayinlanan topic'lerin on eki. Iki ornek ayni anda kosarken
        # ikincisine farkli bir on ek verilmeli, yoksa debug/processed
        # topic'leri ve kayit dosya adlari cakisir.
        self.declare_parameter('topic_prefix', 'tabela')
        # ============== MESAFE: ZED DERINLIGI BIRINCIL (25.08.2026) ==========
        # Bu tarihe kadar mesafe TEK basina 2B bbox yuksekliginden turetiliyordu:
        #     d = sabit / h,   sabit = odak * nesnenin GERCEK yuksekligi
        # Yani yontem, her tabelanin fiziksel boyutunu dogru bilmeyi sart
        # kosuyordu -- ve bilmiyorduk. joystick_46 bag'i (gercek arac, ZED
        # 1280x720) uzerinde hareketten olcek yontemiyle olculdu: arac hizindan
        # integre edilen yol s(t) ile 1/h dogrusal regresyonu, ki bu odak
        # uzakligindan ve nesne boyutundan BAGIMSIZDIR:
        #     DUR tabelasi : gercek sabit ~362, kodda 450  -> %24 FAZLA bildirim
        #     yesil isik   : gercek sabit ~218, kodda 150  -> %31 EKSIK bildirim
        # Iki nesne turu TERS yonlerde sapiyordu; tek bir duzeltme carpani
        # ikisini birden duzeltemez. Cozum sabiti daha iyi tahmin etmek degil,
        # mesafeyi TAHMIN ETMEYI BIRAKMAK: ZED zaten her piksel icin metre
        # veriyor ve nesne boyutu denklemden tamamen cikiyor.
        #
        # Derinlik topic'i: ZED wrapper `depth_registered`i SOL REKTIFIYE
        # goruntuye hizali yayinlar, yani `rgb/image_rect_color` uzerinde
        # bulunan bbox pikselleri dogrudan indekslenebilir.
        # VARSAYILAN, `camera_topic` ile AYNI KAYNAGI gosterir (CARLA overlay).
        # Ikisinin varsayilanlari farkli kaynaklara bakarsa simulasyonda
        # derinlik hic gelmez ve dugum sessizce tahmine duser -- tam da
        # kaldirmaya calistigimiz sessiz hata. Gercek araçta IKISI BIRDEN
        # repoint edilir:
        #   -p camera_topic:=/zed/zed_node/rgb/image_rect_color
        #   -p depth_topic:=/zed/zed_node/depth/depth_registered
        self.declare_parameter('depth_topic', '/zed/zed_node/depth/depth_registered')
        self.declare_parameter('use_depth', True)
        # RGB karesiyle derinlik karesi arasinda kabul edilen azami zaman farki.
        # Senkron abonelik (message_filters) BILEREK kullanilmadi: derinlik hic
        # gelmezse senkronizer RGB'yi de bloklar ve tabela tespiti tamamen
        # susardi. Bunun yerine son derinlik karesi saklanir ve yasi burada
        # kontrol edilir. 28 Hz'de bir kare ~36 ms; 150 ms ~4 kare tolerans.
        self.declare_parameter('depth_max_age', 0.15)
        # Saklanan derinlik karesi sayisi. TEK kare saklamak YETMIYOR: YOLO
        # cikarimi ~200 ms surdugu icin islenen RGB karesi kuyrukta geride
        # kalir, elde tutulan derinlik ise ondan DAHA YENI olur. O zaman
        # (a) yas esigi asilir ve gereksiz yere tahmine dusulur, (b) daha
        # kotusu, eslestirilseydi bbox eski karedeki konumu gosterirken
        # derinlik yeni kareden okunurdu -- arac ilerlemis, tabela ekranda
        # kaymis, YANLIS pikseller orneklenmis olurdu. Bu yuzden son N kare
        # saklanir ve RGB'nin zaman damgasina EN YAKIN olan secilir.
        # 28 Hz'de 10 kare ~360 ms gecmis; 720p float32'de ~37 MB.
        self.declare_parameter('depth_buffer_size', 10)
        # Derinlik aboneliginin kuyruk derinligi. sensor_data profili 5 tutar;
        # YOLO cikarimi ~160 ms surdugu ve o sure boyunca callback isleyemedigi
        # icin 28 Hz'lik bir derinlik akisinda kuyruk tasip kareler DUSER.
        # Daha derin kuyruk, bir cikarim penceresi boyunca gelen karelerin
        # tamamini tutar. (Bu, agdaki parca kaybini COZMEZ -- onu tasima
        # katmani belirler; bkz. tabela_mesafe.md "bant genisligi".)
        self.declare_parameter('depth_qos_depth', 10)
        # bbox'in ORTA bolgesinin orani. Kenarlar direge, gokyuzune, arkadaki
        # binaya tasar ve medyani bozar; sadece ic bolge orneklenir.
        self.declare_parameter('depth_roi_ratio', 0.5)
        # ROI'de gecerli piksel orani bunun altindaysa olcum REDDEDILIR.
        # Yari dolu bir kutunun medyani sessizce yanlis olur; reddedip yedege
        # dusmek, yanlis bir olcumu "olculdu" diye yayinlamaktan iyidir.
        self.declare_parameter('depth_min_valid_ratio', 0.15)
        # Makul menzil. ZED2 stereo bunun disinda deger uretse de guvenilmez.
        self.declare_parameter('depth_min_m', 0.4)
        self.declare_parameter('depth_max_m', 40.0)
        # Kamera optik merkezi -> on tampon (m). ID-4 engel mesafeleri ON
        # TAMPON referansli; ID-3 de ayni referansta olsun ki beyindeki
        # esikler iki kaynak icin ayni seyi ifade etsin. Gercek aracta
        # olculup verilmeli (ZED govde onunde -> pozitif deger).
        # 0.0 -> 0.205 (26.08.2026). Sartname olcumu ARACIN ON UC NOKTASINI
        # referans aliyor ("Araclarin olcumleri, aracin on tarafinin en uc
        # noktasinin konumunu ... ifade eder"). URDF: on burun on aksin
        # 0.410 m onunde, kamera 0.205 m onunde -> aradaki fark 0.205 m.
        # Boylece ID-3'un <distance> alani da ID-4 gibi ON TAMPON referansli
        # olur ve beyindeki esikler dogrudan sartnamenin olcusuyle karsilastirilir.
        self.declare_parameter('camera_to_bumper', 0.205)
        # Derinlik gecersizken bbox tahminine dusulsun mu. Kapatilirsa o
        # tespit HIC yayinlanmaz (beyin tabelayi gormemis olur). Varsayilan
        # acik: yarista tabelayi tamamen kaybetmektense isaretli tahmin.
        self.declare_parameter('allow_bbox_fallback', True)
        # YEDEK formulun sabitleri. 450/150 degil, yukarida anlatilan bag
        # olcumunun sonucu: yedek de artik derinlikle AYNI BIRIMDE (gercek
        # metre) sonuc verir. Ayni alanda iki farkli olcek dolasmasi, bu
        # degisiklikte kurtulmaya calistigimiz hatanin ta kendisiydi.
        # NOT: bag'deki CAN hizi tam sayi km/h (0..3) oldugu icin bu iki
        # sabitin MUTLAK degerinde ~%30 belirsizlik var; oranlari saglam.
        # Derinlik akiyorken bu sabitler zaten kullanilmaz.
        self.declare_parameter('distance_constant', 362.0)        # eski: 450.0
        self.declare_parameter('light_distance_constant', 218.0)  # eski: 150.0
        self.declare_parameter('publish_output', True)
        self.declare_parameter('show_display', True)
        # Pencere gerektirmeyen debug cikisi: annotated frame kucultulup JPEG
        # olarak /neuravix/tabela_debug/compressed'e basilir (lane_follower'daki
        # /neuravix/lane_debug/compressed ile ayni desen). Gercek aracta
        # laptoptan rqt_image_view ile kablosuz izlenir.
        self.declare_parameter('publish_debug_image', True)
        # Gosterim penceresi boyutu (kucuk pencere)
        self.declare_parameter('display_width', 640)
        self.declare_parameter('display_height', 360)

        # ============== CONFIDENCE & NMS PARAMETRELERI ==============
        self.declare_parameter('confidence_threshold', 0.35)
        self.declare_parameter('iou_threshold', 0.45)
        self.declare_parameter('max_detections', 100)

        # ============== PREPROCESSING PARAMETRELERI ==============
        self.declare_parameter('enable_preprocessing', True)
        self.declare_parameter('enable_clahe', True)
        self.declare_parameter('enable_denoise', True)
        self.declare_parameter('enable_sharpen', False)
        self.declare_parameter('clahe_clip_limit', 2.0)

        # ============== TEMPORAL FILTER PARAMETRELERI ==============
        self.declare_parameter('enable_temporal_filter', True)
        self.declare_parameter('temporal_buffer_size', 5)
        self.declare_parameter('temporal_min_hits', 3)
        self.declare_parameter('temporal_iou_threshold', 0.4)

        # Parametreleri al
        share_dir = get_package_share_directory('neuravix_ros2')  # ROS2 share klasörü
        self.model_file = self.get_parameter('model_file').get_parameter_value().string_value
        model_path = os.path.join(share_dir, "models", self.model_file)
        self.imgsz = self.get_parameter('imgsz').get_parameter_value().integer_value
        self.topic_prefix = self.get_parameter('topic_prefix').get_parameter_value().string_value
        self.distance_constant = self.get_parameter('distance_constant').get_parameter_value().double_value
        self.light_distance_constant = self.get_parameter(
            'light_distance_constant').get_parameter_value().double_value
        self.depth_topic = self.get_parameter('depth_topic').get_parameter_value().string_value
        self.use_depth = self.get_parameter('use_depth').get_parameter_value().bool_value
        self.depth_max_age = self.get_parameter('depth_max_age').get_parameter_value().double_value
        self.depth_buffer_size = self.get_parameter(
            'depth_buffer_size').get_parameter_value().integer_value
        self.depth_qos_depth = self.get_parameter(
            'depth_qos_depth').get_parameter_value().integer_value
        self.depth_roi_ratio = self.get_parameter('depth_roi_ratio').get_parameter_value().double_value
        self.depth_min_valid_ratio = self.get_parameter(
            'depth_min_valid_ratio').get_parameter_value().double_value
        self.depth_min_m = self.get_parameter('depth_min_m').get_parameter_value().double_value
        self.depth_max_m = self.get_parameter('depth_max_m').get_parameter_value().double_value
        self.camera_to_bumper = self.get_parameter('camera_to_bumper').get_parameter_value().double_value
        self.allow_bbox_fallback = self.get_parameter(
            'allow_bbox_fallback').get_parameter_value().bool_value
        self.camera_topic = self.get_parameter('camera_topic').get_parameter_value().string_value
        self.publish_output = self.get_parameter('publish_output').get_parameter_value().bool_value
        self.show_display = self.get_parameter('show_display').get_parameter_value().bool_value
        self.publish_debug = self.get_parameter('publish_debug_image').get_parameter_value().bool_value
        if self.show_display and not os.environ.get('DISPLAY'):
            self.show_display = False
            self.get_logger().warn(
                'DISPLAY yok: pencere kapatildi. Goruntu icin '
                '/neuravix/tabela_debug/compressed topic\'ini izleyin (rqt_image_view).')
        self.display_width = self.get_parameter('display_width').get_parameter_value().integer_value
        self.display_height = self.get_parameter('display_height').get_parameter_value().integer_value

        # Confidence & NMS parametreleri
        self.confidence_threshold = self.get_parameter('confidence_threshold').get_parameter_value().double_value
        self.iou_threshold = self.get_parameter('iou_threshold').get_parameter_value().double_value
        self.max_detections = self.get_parameter('max_detections').get_parameter_value().integer_value

        # Preprocessing parametreleri
        self.enable_preprocessing = self.get_parameter('enable_preprocessing').get_parameter_value().bool_value
        enable_clahe = self.get_parameter('enable_clahe').get_parameter_value().bool_value
        enable_denoise = self.get_parameter('enable_denoise').get_parameter_value().bool_value
        enable_sharpen = self.get_parameter('enable_sharpen').get_parameter_value().bool_value
        clahe_clip_limit = self.get_parameter('clahe_clip_limit').get_parameter_value().double_value

        # Temporal filter parametreleri
        self.enable_temporal_filter = self.get_parameter('enable_temporal_filter').get_parameter_value().bool_value
        temporal_buffer_size = self.get_parameter('temporal_buffer_size').get_parameter_value().integer_value
        temporal_min_hits = self.get_parameter('temporal_min_hits').get_parameter_value().integer_value
        temporal_iou_threshold = self.get_parameter('temporal_iou_threshold').get_parameter_value().double_value

        # ============== YOLO MODEL ==============
        self.get_logger().info(f'YOLO modeli yükleniyor: {model_path}')
        try:
            self.model = YOLO(model_path)
            self.get_logger().info('YOLO modeli başarıyla yüklendi')
        except Exception as e:
            self.get_logger().error(f'YOLO modeli yüklenemedi: {str(e)}')
            raise

        # ===== SINIF ID ESLEME (model indeksi -> kanonik /master id) =====
        self._build_sign_id_map()

        # ============== PREPROCESSOR ==============
        if self.enable_preprocessing:
            self.preprocessor = ImagePreprocessor(
                enable_clahe=enable_clahe,
                enable_denoise=enable_denoise,
                enable_sharpen=enable_sharpen,
                clahe_clip_limit=clahe_clip_limit
            )
            self.get_logger().info('Image preprocessor başlatıldı')

        # ============== TEMPORAL FILTER ==============
        if self.enable_temporal_filter:
            self.temporal_filter = TemporalFilter(
                buffer_size=temporal_buffer_size,
                min_hits=temporal_min_hits,
                iou_threshold=temporal_iou_threshold
            )
            self.get_logger().info(f'Temporal filter başlatıldı (buffer={temporal_buffer_size}, min_hits={temporal_min_hits})')

        # ============== ROS2 BRIDGE ==============
        self.bridge = CvBridge()

        # CARLA kamerasından görüntü al (Subscriber)
        # sensor_data QoS (best-effort): ZED wrapper gibi gercek kamera
        # suruculeri best-effort yayinlayabilir; reliable abonelik onlarla
        # eslesmez. CARLA'nin reliable yayiniyla da uyumlu.
        self.subscription = self.create_subscription(
            Image,
            self.camera_topic,
            self.image_callback,
            qos_profile_sensor_data
        )
        self.get_logger().info(f'Kamera topic\'ine abone olundu: {self.camera_topic}')

        # ============== ZED DERINLIK ABONELIGI ==============
        # Son kare saklanir, RGB karesiyle zaman damgasi karsilastirilir.
        # Bilerek senkron degil: derinlik olmadiginda RGB yolu calismaya
        # devam etmeli (bkz. depth_max_age parametre notu).
        self._warn_times = {}
        # (stamp_sn, metre cinsinden float32 array) halka tamponu
        self.depth_buf = deque(maxlen=max(1, self.depth_buffer_size))
        self.depth_msg_count = 0
        # Eslestirme istatistigi: derinlikten mi olculdu, yedege mi dusuldu.
        # Arac gununde "derinlik gercekten kullaniliyor mu" sorusunun sayisal
        # cevabi; overlay'e ve duzenli log satirina bu girer.
        self._olculen = 0
        self._yedege_dusen = 0
        self._son_rapor = 0.0
        if self.use_depth:
            depth_qos = QoSProfile(
                reliability=QoSReliabilityPolicy.BEST_EFFORT,
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=max(1, self.depth_qos_depth))
            self.depth_sub = self.create_subscription(
                Image, self.depth_topic, self.depth_callback, depth_qos)
            self.get_logger().info(f'Derinlik topic\'ine abone olundu: {self.depth_topic}')
        else:
            self.get_logger().warn(
                'use_depth=False -> mesafeler bbox TAHMINI olacak (ID-3 src=0)')

        # İşlenmiş görüntüyü yayınla (Publisher)
        if self.publish_output:
            self.processed_pub = self.create_publisher(
                Image,
                f'/{self.topic_prefix}_tespit/processed_image',
                10
            )
            self.get_logger().info('İşlenmiş görüntü publisher oluşturuldu')

        # Karar katmanına tabela bilgisi gönder (-> /master)
        # Format: "3,<sign_id>,<distance>,<cx>,<cy>,<w>,<h>"
        self.master_pub = self.create_publisher(String, '/master', 10)
        self.get_logger().info('Master publisher (/master) oluşturuldu')

        self.debug_pub = (
            self.create_publisher(CompressedImage,
                                  f'/neuravix/{self.topic_prefix}_debug/compressed', 10)
            if self.publish_debug else None
        )

        # Pencere bir kez kuruldu mu. Baslik topic on ekinden turetilir:
        # tabela ve isik dugumleri ayni anda kostugunda iki pencere ayni
        # isimde olursa hangisinin ne oldugu anlasilmiyor.
        self._win_ready = False
        self._win_name = f"Tespit [{self.topic_prefix}] - {self.model_file}"

        # ============== VIDEO KAYDI ('r' tusu) ==============
        # 'r' tusu ile kayit baslar/durur. annotated_frame (tespit kutulu)
        # ~/neuravix_kayit/ altina yazilir.
        self.video_writer = None
        self._video_path  = None

        # İstatistikler
        self.stats = {
            'total_detections': 0,
            'filtered_detections': 0,
            'frames_processed': 0
        }
        self.start_time = time.time()
        self.current_frame = 0

        self.get_logger().info('=' * 50)
        self.get_logger().info('Tabela Tespit Node başlatıldı')
        self.get_logger().info(f'  - Model: {self.model_file} (imgsz={self.imgsz})')
        self.get_logger().info(
            '  - Mesafe kaynagi: ' +
            (f'ZED derinligi ({self.depth_topic})' if self.use_depth
             else 'KAPALI -> yalniz bbox tahmini'))
        self.get_logger().info(
            f'  - Yedek bbox sabitleri: tabela {self.distance_constant} / '
            f'isik {self.light_distance_constant} | yedek '
            f'{"ACIK" if self.allow_bbox_fallback else "KAPALI"}')
        self.get_logger().info(f'  - Kamera->tampon offset: {self.camera_to_bumper} m')
        self.get_logger().info(f'  - Topic on eki: {self.topic_prefix}')
        self.get_logger().info(f'  - Confidence threshold: {self.confidence_threshold}')
        self.get_logger().info(f'  - IoU threshold: {self.iou_threshold}')
        self.get_logger().info(f'  - Preprocessing: {self.enable_preprocessing}')
        self.get_logger().info(f'  - Temporal filter: {self.enable_temporal_filter}')
        self.get_logger().info('=' * 50)
        self.get_logger().info(' kamera bağlantısı bekleniyor...')

    def _toggle_record(self, frame):
        """'r' tusu: kaydi baslat / durdur."""
        if self.video_writer is None:
            h, w = frame.shape[:2]
            out_dir = os.path.expanduser("~/neuravix_kayit")
            os.makedirs(out_dir, exist_ok=True)
            ts = time.strftime("%Y%m%d_%H%M%S")
            self._video_path = os.path.join(out_dir, f"{self.topic_prefix}_tespit_{ts}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.video_writer = cv2.VideoWriter(self._video_path, fourcc, 20.0, (w, h))
            self.get_logger().info(f'[REC] Kayit BASLADI: {self._video_path}')
        else:
            self.video_writer.release()
            self.get_logger().info(f'[REC] Kayit DURDU: {self._video_path}')
            self.video_writer = None

    def image_callback(self, msg):
        """CARLA kamerasından gelen görüntüyü işle"""
        try:
            # ROS Image -> OpenCV formatına çevir
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.current_frame += 1
            self._check_depth_health()

            # 1. PREPROCESSING
            if self.enable_preprocessing:
                processed_frame = self.preprocessor.process(frame)
            else:
                processed_frame = frame

            # 2. YOLO DETECTION
            results = self.model(
                processed_frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                max_det=self.max_detections,
                imgsz=self.imgsz,
                verbose=False
            )
            print(f"[DEBUG] Frame {self.current_frame} - Raw results: {len(results[0].boxes)} nesne")
            for box in results[0].boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = self.model.names[cls]
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                print(f"  -> {label}: %{conf*100:.1f} | Konum: ({int(x1)},{int(y1)}) - ({int(x2)},{int(y2)})")

            # Tespitleri çıkar
            raw_detections = self.extract_detections(results)
            raw_count = len(raw_detections)
            self.stats['total_detections'] += raw_count

            # 3. TEMPORAL FILTERING
            if self.enable_temporal_filter and len(raw_detections) > 0:
                filtered_detections = self.temporal_filter.update(raw_detections)
            else:
                filtered_detections = raw_detections

            filtered_count = len(filtered_detections)
            self.stats['filtered_detections'] += filtered_count
            self.stats['frames_processed'] += 1

            # Tespit logla
            if filtered_count > 0:
                self.get_logger().info(f'Tespit: {filtered_count} tabela (raw: {raw_count})')

            # Karar katmanına tespitleri /master üzerinden gönder.
            # Derinlik eslestirmesi icin bu karenin zaman damgasi gerekiyor.
            stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            for det in filtered_detections:
                self.publish_sign_to_master(det, frame.shape, stamp)

            # 4. GÖRÜNTÜLEME
            annotated_frame = self.draw_detections(frame, filtered_detections)
            annotated_frame = self.add_info_overlay(annotated_frame, raw_count, filtered_count)

            # ROS2 publish
            if self.publish_output:
                try:
                    ros_image = self.bridge.cv2_to_imgmsg(annotated_frame, "bgr8")
                    self.processed_pub.publish(ros_image)
                except Exception as e:
                    self.get_logger().warn(f'Görüntü yayınlanamadı: {str(e)}')

            # Kayit aktifse, ekranda gosterilen annotated_frame'i videoya yaz
            if self.video_writer is not None:
                self.video_writer.write(annotated_frame)

            # Debug JPEG topic'i (pencere gerektirmez, wifi'ye uygun boyut)
            if self.debug_pub is not None:
                small = cv2.resize(annotated_frame,
                                   (self.display_width, self.display_height))
                ok, buf = cv2.imencode('.jpg', small,
                                       [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ok:
                    dbg = CompressedImage()
                    dbg.header = msg.header
                    dbg.format = 'jpeg'
                    dbg.data = buf.tobytes()
                    self.debug_pub.publish(dbg)

            # Ekranda göster (orijinal - tam boyut)
            if self.show_display:
                cv2.imshow(self._win_name, annotated_frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    self.get_logger().info('Kullanıcı çıkış yaptı')
                    self.print_statistics()
                    self.cleanup()
                elif key == ord('s'):
                    screenshot_path = os.path.expanduser(
                        f'~/neuravix_kayit/screenshot_{self.current_frame}.png')
                    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                    cv2.imwrite(screenshot_path, annotated_frame)
                    self.get_logger().info(f'Screenshot kaydedildi: {screenshot_path}')
                elif key == ord('r'):          # kaydi baslat/durdur
                    self._toggle_record(annotated_frame)

        except Exception as e:
            self.get_logger().error(f'Frame işlenirken hata: {str(e)}')

    def _build_sign_id_map(self):
        """Modelin sinif indekslerini kanonik /master id'lerine esler.

        Esleme MODEL SINIF ADI uzerinden yapilir (indeks uzerinden DEGIL):
        best6.pt (22 sinif, Turkce) ile eski sonyaris.pt (26 sinif, Ingilizce)
        farkli indeks duzenlerine sahip ve beyin sonyaris duzenine gore
        yazilmisti. Ham indeks yayinlamak "PARK -> DUR", "SagdanGidiniz ->
        KIRMIZI_ISIK" gibi sessiz ve tehlikeli yanlis kararlar uretiyordu.

        Taninmayan sinif adi eslenmez ve YAYINLANMAZ; burada bir kez WARN
        dusulur. Yeni bir model takildiginda acilistaki bu tablo, eksik ad
        olup olmadigini ilk bakista gosterir.
        """
        self.sign_id_map = {}
        eslenmeyen = []
        for cls_id, cls_name in sorted(self.model.names.items()):
            canon = canonical_sign_id(cls_name)
            if canon is None:
                eslenmeyen.append(f'{cls_id}:{cls_name}')
            else:
                self.sign_id_map[cls_id] = canon

        self.get_logger().info('--- Tabela sinif eslemesi (model -> /master) ---')
        for cls_id, cls_name in sorted(self.model.names.items()):
            canon = self.sign_id_map.get(cls_id)
            if canon is None:
                self.get_logger().info(f'  {cls_id:>2} {cls_name:<24} -> (yok, yayinlanmaz)')
            else:
                self.get_logger().info(
                    f'  {cls_id:>2} {cls_name:<24} -> {canon:>2} {SIGN_NAMES.get(canon, "?")}')
        self.get_logger().info(
            f'--- {len(self.sign_id_map)}/{len(self.model.names)} sinif eslendi ---')
        if eslenmeyen:
            self.get_logger().warn(
                'Kanonik karsiligi olmayan sinif(lar): ' + ', '.join(eslenmeyen) +
                ' | decision_brain.py icindeki _SIGN_ALIASES tablosuna eklenmeli.')

    def depth_callback(self, msg):
        """ZED derinlik karesini metre cinsine cevirip saklar.

        Iki encoding desteklenir: 32FC1 (metre, ZED wrapper varsayilani) ve
        16UC1 (milimetre, openni uyumluluk modu). Bilinmeyen encoding sessizce
        yok sayilmaz -- uyarilir, cunku yanlis olcekli bir derinlik "olculdu"
        etiketiyle yayinlanirsa bbox tahmininden daha tehlikelidir.
        """
        try:
            enc = msg.encoding.lower()
            if enc in ('32fc1', '32fc'):
                arr = np.frombuffer(msg.data, dtype=np.float32)
            elif enc == '16uc1':
                arr = np.frombuffer(msg.data, dtype=np.uint16).astype(np.float32) / 1000.0
            else:
                self._warn_throttled(
                    '_denc', f"Desteklenmeyen derinlik encoding'i: '{msg.encoding}' "
                             f"-> derinlik kullanilmiyor", period=15.0)
                return
            if msg.is_bigendian:
                arr = arr.byteswap()
            stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            self.depth_buf.append((stamp, arr.reshape(msg.height, msg.width)))
            self.depth_msg_count += 1
        except Exception as e:
            self._warn_throttled('_dcb', f'Derinlik karesi islenemedi: {e}', period=15.0)

    def _warn_throttled(self, key: str, mesaj: str, period: float = 5.0):
        """Ayni uyariyi kare basina degil, `period` saniyede bir kez basar."""
        now = time.time()
        if now - self._warn_times.get(key, 0.0) >= period:
            self._warn_times[key] = now
            self.get_logger().warn(mesaj)

    def _check_depth_health(self):
        """Derinlik bekleniyor ama hic gelmiyorsa duzenli araliklarla uyarir.

        2026-07-11'de araçta ZED wrapper ayaktaydi, topic'i reklam ediyordu ve
        TEK kare akmiyordu (`node list` bunu gostermez, `topic hz` gosterir).
        Boyle bir durumda sessizce bbox tahminine dusup sonucu metre gibi
        yayinlamak, tam da bu degisiklikle kurtulmaya calistigimiz hata
        sinifina geri donmek olurdu -> gorunur yapiliyor.
        """
        if not self.use_depth:
            return

        # Duzenli rapor: derinlik kac Hz akiyor ve tespitlerin yuzde kaci
        # gercekten OLCULDU. Arac gununde tek bakista gorulmesi gereken sey bu;
        # "derinlik var" ile "derinlik kullanilabiliyor" ayni sey degil.
        simdi = time.time()
        if simdi - self._son_rapor >= 15.0:
            self._son_rapor = simdi
            gecen = max(1e-6, simdi - self.start_time)
            toplam = self._olculen + self._yedege_dusen
            if toplam:
                self.get_logger().info(
                    f'[derinlik] {self.depth_msg_count} kare '
                    f'(~{self.depth_msg_count / gecen:.1f} Hz) | '
                    f'olculen {self._olculen}/{toplam} '
                    f'(%{100 * self._olculen / toplam:.0f})')

        if self.depth_msg_count > 0:
            return
        if simdi - self.start_time < 5.0:
            return
        self._warn_throttled(
            '_no_depth',
            f"'{self.depth_topic}' uzerinden HIC derinlik karesi gelmedi -> "
            f"mesafeler bbox TAHMINI (ID-3 src=0). Kontrol: "
            f"ros2 topic hz {self.depth_topic}", period=10.0)

    def _en_yakin_derinlik(self, stamp: float):
        """RGB zaman damgasina en yakin derinlik karesini dondurur.

        -> (dizi, yas_sn) ya da (None, None). En yakin kare bile depth_max_age
        disindaysa derinlik gercekten bayattir (surucu durmus / cok yavas) ve
        cagiran yedege duser.
        """
        if not self.depth_buf:
            return None, None
        dep, yas = min(((d, abs(stamp - t)) for t, d in tuple(self.depth_buf)),
                       key=lambda p: p[1])
        return (dep, yas) if yas <= self.depth_max_age else (None, yas)

    def _sample_depth(self, bbox: np.ndarray, frame_shape,
                      dep: np.ndarray) -> Optional[float]:
        """bbox'in ic bolgesinden robust bir derinlik (metre) cikarir.

        Olcum guvenilir degilse None doner ve cagiran yedege duser.
        """
        dh, dw = dep.shape[:2]
        fh, fw = frame_shape[:2]
        # depth_registered sol rektifiye goruntuye hizalidir -> normalde ayni
        # cozunurluk. Wrapper farkli cozunurlukte yayinlarsa sessizce yanlis
        # piksel okumak yerine bbox oranla olceklenir.
        sx, sy = dw / float(fw), dh / float(fh)
        x1, y1, x2, y2 = bbox.astype(float)
        x1, x2, y1, y2 = x1 * sx, x2 * sx, y1 * sy, y2 * sy

        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        rw = max(1.0, (x2 - x1) * self.depth_roi_ratio / 2.0)
        rh = max(1.0, (y2 - y1) * self.depth_roi_ratio / 2.0)
        i0, i1 = int(max(0, cy - rh)), int(min(dh, cy + rh + 1))
        j0, j1 = int(max(0, cx - rw)), int(min(dw, cx + rw + 1))
        if i1 <= i0 or j1 <= j0:
            return None

        roi = dep[i0:i1, j0:j1]
        gecerli = np.isfinite(roi) & (roi >= self.depth_min_m) & (roi <= self.depth_max_m)
        n_gecerli = int(gecerli.sum())
        if n_gecerli == 0 or n_gecerli < self.depth_min_valid_ratio * roi.size:
            # Yanan lamba, dokusuz/parlak yuzey, menzil disi: stereo eslesme
            # deger uretemez. Yari dolu bir kutunun medyani sessizce yanlis
            # olur -> olcumu reddet.
            return None
        # Medyan: kutuya sizan arka plan pikselleri ortalamayi kaydirir.
        return float(np.median(roi[gecerli]))

    def _resolve_distance(self, det: Detection, sign_id: int, h: int,
                          frame_shape, stamp: float):
        """(mesafe_m, kaynak) dondurur. kaynak: 1 = ZED derinligi, 0 = tahmin.

        Derinlik gecersiz ve yedek kapaliysa (None, -1) doner; cagiran o
        tespiti YAYINLAMAZ.
        """
        if self.use_depth and self.depth_buf:
            dep, yas = self._en_yakin_derinlik(stamp)
            if dep is not None:
                d = self._sample_depth(det.bbox, frame_shape, dep)
                if d is not None:
                    self._olculen += 1
                    return max(0.0, d - self.camera_to_bumper), 1
            else:
                self._warn_throttled(
                    '_depth_old',
                    f'En yakin derinlik karesi bile bayat ({yas * 1000:.0f} ms > '
                    f'{self.depth_max_age * 1000:.0f} ms) -> bbox tahmini. '
                    f'Derinlik yayini duruyor ya da cok yavas olabilir.')

        self._yedege_dusen += 1
        if not self.allow_bbox_fallback:
            return None, -1

        # YEDEK: d = sabit / h. Sabitler joystick_46 bag'inden hareketten
        # olcek yontemiyle olculdu (bkz. parametre tanimi) -> derinlikle AYNI
        # birimde, gercek metre. Yine de bir TAHMINDIR ve mesajda src=0 ile
        # isaretlenir; beyin ona olcum muamelesi yapmaz.
        sabit = (self.light_distance_constant
                 if sign_id in (KIRMIZI_ISIK, SARI_ISIK, YESIL_ISIK)
                 else self.distance_constant)
        return max(0.0, sabit / max(h, 1) - self.camera_to_bumper), 0

    def publish_sign_to_master(self, det: Detection, frame_shape, stamp: float):
        """
        Tespit edilen tabelayı /master topic'ine yayınlar.
        Format: "3,<sign_id>,<distance>,<cx>,<cy>,<w>,<h>,<src>"

        <sign_id> KANONIK id'dir (decision_brain sabitleri), modelin sinif
        indeksi degil — bkz. _build_sign_id_map. Eslenmemis sinif yayinlanmaz.

        <distance> GERCEK METREDIR, on tampon referansli (ID-4 engel
        mesafeleriyle ayni referans). <src>: 1 = ZED derinliginden OLCULDU,
        0 = bbox yuksekliginden TAHMIN edildi. 8. alan 25.08.2026'da eklendi;
        sona eklendigi icin eski tuketiciler etkilenmez.
        """
        sign_id = self.sign_id_map.get(det.class_id)
        if sign_id is None:
            return

        x1, y1, x2, y2 = det.bbox.astype(int)
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        w = int(x2 - x1)
        h = int(y2 - y1)

        distance, src = self._resolve_distance(det, sign_id, h, frame_shape, stamp)
        det.distance, det.distance_src = distance, src
        if distance is None:
            # Ne olcum var ne de izin verilen yedek -> SUS. Uydurma bir mesafe
            # yayinlamak, beynin onu olcum sanip DUR/donus tetiklemesi demekti.
            self._warn_throttled(
                '_no_dist',
                f'{det.class_name}: derinlik yok, yedek kapali -> yayinlanmadi')
            return

        msg = String()
        msg.data = f"3,{sign_id},{distance:.2f},{cx},{cy},{w},{h},{src}"
        self.master_pub.publish(msg)

    def extract_detections(self, results) -> List[Detection]:
        """YOLO sonuçlarından Detection listesi çıkar"""
        detections = []

        if results[0].boxes is None:
            return detections

        boxes = results[0].boxes
        for i in range(len(boxes)):
            bbox = boxes.xyxy[i].cpu().numpy()
            conf = float(boxes.conf[i].cpu().numpy())
            cls_id = int(boxes.cls[i].cpu().numpy())
            cls_name = self.model.names[cls_id] if cls_id in self.model.names else str(cls_id)

            detections.append(Detection(
                bbox=bbox,
                confidence=conf,
                class_id=cls_id,
                class_name=cls_name
            ))

        return detections

    def draw_detections(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """Tespitleri frame üzerine çiz"""
        annotated = frame.copy()

        for det in detections:
            x1, y1, x2, y2 = det.bbox.astype(int)
            color = self.get_color_for_class(det.class_id)

            # Bounding box çiz
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Label: mesafe ve KAYNAGI da yaziliyor. Sahada kalibrasyon ve
            # "derinlik gercekten calisiyor mu" kontrolu ekrandan yapiliyor.
            if det.distance is None:
                label = f'{det.class_name}: {det.confidence:.2f}'
            else:
                kaynak = 'ZED' if det.distance_src == 1 else 'tahmin'
                label = (f'{det.class_name}: {det.confidence:.2f} | '
                         f'{det.distance:.1f}m ({kaynak})')

            # Label background
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(annotated,
                          (x1, y1 - label_h - 10),
                          (x1 + label_w, y1),
                          color, -1)

            # Label text
            cv2.putText(annotated, label,
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 1)

        return annotated

    def _depth_durumu(self) -> str:
        """Overlay'de gosterilen mesafe kaynagi ozeti."""
        if not self.use_depth:
            return 'bbox tahmini (use_depth=False)'
        if self.depth_msg_count == 0:
            return 'DERINLIK YOK -> bbox tahmini'
        toplam = self._olculen + self._yedege_dusen
        oran = f' | olculen %{100 * self._olculen / toplam:.0f}' if toplam else ''
        return f'ZED derinligi ({self.depth_msg_count} kare{oran})'

    def get_color_for_class(self, class_id: int) -> tuple:
        """Class ID'ye göre renk döndür"""
        colors = [
            (0, 255, 0),    # Yeşil
            (255, 0, 0),    # Mavi
            (0, 0, 255),    # Kırmızı
            (255, 255, 0),  # Cyan
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Sarı
            (128, 0, 255),  # Mor
            (255, 128, 0),  # Turuncu
        ]
        return colors[class_id % len(colors)]

    def add_info_overlay(self, frame: np.ndarray, raw_count: int, filtered_count: int) -> np.ndarray:
        """Frame'e bilgi overlay'i ekle"""
        overlay = frame.copy()

        # FPS hesapla
        elapsed_time = time.time() - self.start_time
        fps = self.current_frame / elapsed_time if elapsed_time > 0 else 0

        # Yarı saydam arka plan
        cv2.rectangle(overlay, (10, 10), (430, 140), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

        # Bilgiler
        info_lines = [
            f'Frame: {self.current_frame} | FPS: {fps:.1f}',
            f'Raw Detections: {raw_count}',
            f'Filtered: {filtered_count}',
            f'Conf: {self.confidence_threshold} | IoU: {self.iou_threshold}',
            f'Mesafe: {self._depth_durumu()}',
            f'[Q] Cikis | [S] Screenshot'
        ]

        y_offset = 30
        for line in info_lines:
            cv2.putText(frame, line, (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 20

        return frame

    def print_statistics(self):
        """İşlem istatistiklerini yazdır"""
        elapsed_time = time.time() - self.start_time

        self.get_logger().info('=' * 50)
        self.get_logger().info('İŞLEM İSTATİSTİKLERİ')
        self.get_logger().info('=' * 50)
        self.get_logger().info(f'Toplam süre: {elapsed_time:.1f} saniye')
        self.get_logger().info(f'İşlenen frame: {self.stats["frames_processed"]}')
        if elapsed_time > 0:
            self.get_logger().info(f'Ortalama FPS: {self.stats["frames_processed"]/elapsed_time:.1f}')
        self.get_logger().info(f'Toplam ham tespit: {self.stats["total_detections"]}')
        self.get_logger().info(f'Toplam filtrelenmiş tespit: {self.stats["filtered_detections"]}')

        if self.stats['frames_processed'] > 0:
            avg_raw = self.stats['total_detections'] / self.stats['frames_processed']
            avg_filtered = self.stats['filtered_detections'] / self.stats['frames_processed']
            self.get_logger().info(f'Frame başına ortalama tespit (raw): {avg_raw:.2f}')
            self.get_logger().info(f'Frame başına ortalama tespit (filtered): {avg_filtered:.2f}')

            if self.stats['total_detections'] > 0:
                filter_rate = (1 - self.stats['filtered_detections'] / self.stats['total_detections']) * 100
                self.get_logger().info(f'Yanlış pozitif azaltma: {filter_rate:.1f}%')

        self.get_logger().info('=' * 50)

    def cleanup(self):
        """Kaynakları temizle"""
        self.get_logger().info('Kaynaklar temizleniyor...')
        if self.video_writer is not None:   # acik kayit varsa kapat
            self.video_writer.release()
            self.video_writer = None
        cv2.destroyAllWindows()
        self.get_logger().info('Temizlik tamamlandı')
        if rclpy.ok():
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    node = None
    try:
        node = TabelaTespitNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nCtrl+C ile kapatıldı")
    except Exception as e:
        print(f"Node başlatılamadı: {str(e)}")
    finally:
        if node is not None and node.video_writer is not None:
            node.video_writer.release()   # acik kayit varsa kapat
        cv2.destroyAllWindows()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
