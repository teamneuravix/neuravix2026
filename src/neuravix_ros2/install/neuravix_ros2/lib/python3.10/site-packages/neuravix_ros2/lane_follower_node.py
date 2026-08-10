#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROS 2 Humble (rclpy) Uyumlu Otonom Araç Şerit Takip Algoritması
YOLOv8 + PID Kontrolü ile Görüntü İşleme.
"""
# ROS 2 Kütüphaneleri
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from ament_index_python.packages import get_package_share_directory # YENİ/GEREKLİ IMPORT

# Görüntü İşleme ve Kontrol Kütüphaneleri
from cv_bridge import CvBridge
import cv2
import numpy as np
import time
import math
from ultralytics import YOLO
import os # YENİ/GEREKLİ IMPORT

# --- PID KONTROL FONKSİYONU ---
def get_steering_value_pid(offset_from_center, lane_angle_deg):
    """
    Şerit merkezinden ofset ve şerit açısını kullanarak PID benzeri direksiyon değeri hesaplar.
    """
    K_offset = 0.07 # Merkezi ofset için kazanç
    K_angle = 1.5   # Açı için kazanç
    base_steering = 45 # Merkez (Düz) direksiyon değeri
    
    # P-kontrol benzeri formül
    steering = base_steering + (K_offset * offset_from_center) + (K_angle * lane_angle_deg)
    
    # Değeri güvenli aralıkta tutma (Ör: 15-75 aralığı)
    steering = max(15, min(steering, 75))
    return int(steering)

# --- ROS 2 ŞERİT TAKİP DÜĞÜMÜ SINIFI ---
class LaneFollowerNode(Node):
    """
    ROS 2 Şerit Takip Düğümü Sınıfı
    """
    def __init__(self):
        # Düğümü (Node) Başlatma
        super().__init__('seritTakibi')
        self.get_logger().info('ROS 2 Şerit Takip Düğümü Başlatılıyor.')

        # Sınıf Değişkenleri ve İlk Değer Atamaları
        self.bridge = CvBridge()
        self.prev_frame_time = 0
        self.show_window = True
        self.model = None # Model başlangıçta None olarak ayarlandı

        # --- MODEL YÜKLEME KODU (Şimdi __init__ içinde) ---
        package_name = 'neuravix_ros2'
        try:
            # 1. Paketin kurulum yolunu bul
            share_dir = get_package_share_directory(package_name)
            
            # 2. Model dosyasının tam yolunu oluştur
            # Yüklediğiniz son koda göre 'best_yolo11.pt' kullanılmıştır.
            self.model_path = os.path.join(share_dir,'models', 'best_yolo11.pt')

            # 3. Modeli Yükle
            self.model = YOLO(self.model_path)
            
            self.get_logger().info('YOLO modeli başarıyla yüklendi: %s' % self.model_path)
            
        except Exception as e:
            # ROS 2 Logger ile hata bas
            self.get_logger().error(f"HATA: YOLO modeli yüklenemedi. Yolu kontrol edin: {self.model_path}")
            self.get_logger().error(f"Detay: {e}")
            self.model = None

        if self.model is None:
            self.get_logger().error("Model yüklenmediği için düğüm işlevsiz kalacak!")

        # Publisher: /master topic'ine String mesajı yayınlar (CARLA kontrol komutları için)
        self.publisher_ = self.create_publisher(String, '/master', 10)
        
        # Subscriber: Görüntü topic'ine abone olur
        self.subscription = self.create_subscription(
            Image,
            '/zed2/zed_node/left_raw/image_raw_color',
            self.image_callback, 
            10
        )
        self.subscription # Kullanılmayan değişken uyarısını engeller
        
    def image_callback(self, data):
        """
        Görüntü topic'inden veri geldiğinde çağrılan metot.
        """
        if self.model is None:
            return

        new_frame_time = time.time()
        
        try:
            # ROS Image mesajını OpenCV formatına dönüştürme
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except Exception as e:
            self.get_logger().error(f"CvBridge Hatası: {e}")
            return

        # Görüntü işleme ve kontrol mantığı
        img = cv2.resize(cv_image, (1280, 720)) if cv_image.shape[:2] != (720, 1280) else cv_image.copy()
        original_img = img.copy()

        # FPS Hesaplama
        if self.prev_frame_time != 0:
            fps = 1 / (new_frame_time - self.prev_frame_time)
            cv2.putText(original_img, f"FPS: {int(fps)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        self.prev_frame_time = new_frame_time

        # --- YOLO ve Şerit Tespiti ---
        results = self.model(img, stream=True, verbose=False)
        center_x = img.shape[1] // 2
        masks_info = []
        
        for r in results:
            if r.masks is not None:
                for mask in r.masks.data:
                    mask = mask.cpu().numpy()
                    mask_resized = cv2.resize(mask, (img.shape[1], img.shape[0]))
                    mask_resized = (mask_resized > 0.5).astype(np.uint8)
                    moments = cv2.moments(mask_resized)

                    if moments["m00"] != 0:
                        cx = int(moments["m10"] / moments["m00"])
                        cy = int(moments["m01"] / moments["m00"])
                        
                        # Alt kısımdaki maskeleri filtrele (cy > %85)
                        if cy > img.shape[0] * 0.85:
                            continue

                        # Açı Hesaplama
                        contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        if contours:
                            cnt = max(contours, key=cv2.contourArea)
                            [vx, vy, x0, y0] = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01)
                            angle_rad = math.atan2(vy, vx)
                            angle_deg = math.degrees(angle_rad)
                            
                            # Açı normalizasyonu
                            if angle_deg > 90: angle_deg -= 180
                            elif angle_deg < -90: angle_deg += 180
                            
                            masks_info.append({"cx": cx, "cy": cy, "angle": angle_deg, "mask": mask_resized})

        if not masks_info:
            return

        # En Yakın Sol ve Sağ Şeridi Seçme (Kontrol Mantığı)
        left_mask, right_mask = None, None
        min_left_dist, min_right_dist = float('inf'), float('inf')

        for m in masks_info:
            # Sol Şerit
            if m["cx"] < center_x and (center_x - m["cx"]) < min_left_dist:
                min_left_dist = (center_x - m["cx"])
                left_mask = m
            # Sağ Şerit
            elif m["cx"] > center_x and (m["cx"] - center_x) < min_right_dist:
                min_right_dist = (m["cx"] - center_x)
                right_mask = m

        # Şerit merkezini ve açıyı hesaplama
        offset, angle = 0, 0
        if left_mask and right_mask:
            lane_center_x = (left_mask["cx"] + right_mask["cx"]) // 2
            offset = center_x - lane_center_x
            angle = (left_mask["angle"] + right_mask["angle"]) / 2
        elif left_mask:
            offset = center_x - left_mask["cx"]
            angle = left_mask["angle"]
        elif right_mask:
            offset = center_x - right_mask["cx"]
            angle = right_mask["angle"]

        # Kontrol Değeri Hesaplama ve Yayınlama
        steering_value = get_steering_value_pid(offset, angle)
        
        # ROS 2 Yayınlama
        msg = String()
        msg.data = '2,' + str(steering_value)
        self.publisher_.publish(msg)

        # Görüntüye Metin Ekleme ve Gösterme
        selected_masks = []
        if left_mask: selected_masks.append((left_mask, (255, 0, 0), "Sol Serit"))
        if right_mask: selected_masks.append((right_mask, (0, 0, 255), "Sag Serit"))
        
        for m, color, label in selected_masks:
            colored_mask = np.zeros_like(img)
            colored_mask[m["mask"] > 0] = color
            original_img = cv2.addWeighted(original_img, 1, colored_mask, 0.5, 0)
            cv2.circle(original_img, (m["cx"], m["cy"]), 5, color, -1)
            cv2.putText(original_img, label, (m["cx"] - 10, m["cy"] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
        cv2.putText(original_img, f"Offset: {offset} px", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 255, 100), 2)
        cv2.putText(original_img, f"Aci: {round(angle, 2)} deg", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 200, 100), 2)
        cv2.putText(original_img, f"Direksiyon: {steering_value}", (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if self.show_window:
            cv2.imshow('Original with Detection', original_img)
            cv2.waitKey(1)

# --- ROS 2 Ana Fonksiyon ---
def main(args=None):
    rclpy.init(args=args)
    lane_follower_node = LaneFollowerNode()
    
    try:
        rclpy.spin(lane_follower_node)
    except KeyboardInterrupt:
        lane_follower_node.get_logger().info('Düğüm Klavye Kesintisi ile kapatılıyor.')
    except Exception as e:
        lane_follower_node.get_logger().error(f"Beklenmeyen düğüm hatası: {e}")
    finally:
        # Temizleme
        cv2.destroyAllWindows()
        lane_follower_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
