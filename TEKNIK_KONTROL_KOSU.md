# TEKNİK KONTROL — araç koşu komutları

İmaj: `robotaksi_humble:latest`, ID `10ea17e7fd02` (2026-08-22 14:37)
SHA-256 `45470c170a726b7125d4d5546588f6c855243a0ba781253266306ac26ea815c0`

Konum kaynağı: **yalnız GNSS** (`gnss_pose`). AMCL bu koşuda ÇALIŞTIRILMIYOR.
Aktüasyon: **Yol B** — aracın kendi PID'i kullanılmıyor, `steering_ctrl` +
`throttle_ctrl` doğrudan CAN'e yazıyor. `speed_fb_relay` / `throttle_relay`
**çalıştırılmaz**.

---

## 0) İmajı araca yükle (bir kez)

Laptopta:

    scp ~/robotaksi_deploy/robotaksi_humble.tar smart@<arac_ip>:/home/smart/Permanent/

Araçta:

    docker load -i /home/smart/Permanent/robotaksi_humble.tar
    docker rm -f robotaksi_container
    docker run -d --name robotaksi_container \
      --gpus all --network host --ipc=host --privileged \
      -v /dev:/dev \
      -v /home/smart/Permanent/maps:/root/maps \
      -v /home/smart/Permanent/neuravix_kayit:/root/neuravix_kayit \
      -e ROS_DOMAIN_ID=0 \
      robotaksi_humble:latest tail -f /dev/null

⚠️ `docker load` çalışan konteyneri GÜNCELLEMEZ — `rm -f` + `run` şart.
⚠️ Konteyner `-d ... tail -f /dev/null` ile başlatılıyor ki `exit` yazınca
   durmasın. Her düğüm için `docker exec -it robotaksi_container bash` aç,
   içeride `tmux` kullan (imajda var). Wifi düşünce foreground süreçler ölür.

Her kabukta ilk satır:

    source /ros2_ws/install/setup.bash

---

## 1) ÖN KONTROLLER (sürmeden önce, sırayla)

    ros2 topic hz /velodyne_points        # ~10 Hz
    ros2 topic hz /zed/zed_node/rgb/image_rect_color   # ~25 Hz
    ros2 topic hz /gnss                   # ~4 Hz   <- YALNIZ GNSS için ŞART
    ros2 topic hz /filter/quaternion      # yön kaynağı
    ros2 topic hz /imu/data
    ros2 topic echo /beemobs/FB_OMUX_to_AUTONOMOUS --once   # fb_emergency 0 mı?
    ros2 topic info /odometry/can_wheel -v                  # yayıncı VAR mı?

⚠️ `fb_emergency` 255 ise araç acil durumda — hiçbir şey hareket etmez.
   (20.08'de iki bag bu yüzden yanlış yorumlanmıştı.)
⚠️ Host tarafında da kontrol et; konteynerde yoksa önce host'ta bak.

---

## 2) DÜĞÜMLER (sıra önemli, throttle EN SON)

### 2.1 Odometri — SADECE `/odometry/can_wheel`'de yayıncı YOKSA

    ros2 run bee1_description can_odom

Aracın kendi odometrisi varsa onu kullan (%6-9 eksik; `can_odom` %25).
İkisi birden koşarsa tek topic'te iki yayıncı olur.

    ros2 topic hz /odometry/can_wheel     # ZORUNLU: akmıyorsa slalom bozulur

### 2.2 Konum (yalnız GNSS)

    ros2 run bee1_description gnss_pose

    ros2 topic hz /gnss_pose              # ~4 Hz olmalı

⚠️ Araç dururken ve Xsens filtresi gelmiyorsa düğüm bilerek poz YAYINLAMAZ
   ("Yon (yaw) henuz yok" WARN'ı basar). Birkaç metre hareketle düzelir.

### 2.3 Algı

    ros2 run neuravix_ros2 lane_follower --ros-args -p show_window:=false

    ros2 run neuravix_ros2 obstacle_lidar --ros-args \
      -p side_offset:=3.0 -p side_corridor:=1.26

`camera_topic` ve `lidar_height` zaten doğru varsayılan.

    ros2 topic hz /master                 # ID-2 + ID-4 akmalı

### 2.4 Karar/kontrol

    ros2 run neuravix_ros2 neuravix_control_real

Açılış log'unun ilk satırını OKU: `odom_topic=/odometry/can_wheel`,
`speed_scale=0.25`, `steer gain=-1.20 delta=[-36,36]`, `serit araligi ...`.

### 2.5 Direksiyon

    ros2 run bee1_description steering_ctrl --ros-args -p tolerance:=2.0

⚠️ `max_delta` bayrağı VERME. 90/110 denemek ölçülmüş çıkmaz sokak
   (joystick sapma 73 ile aynı hız); koşuyu da kıyaslanamaz kılar.

### 2.6 Rota (teknik kontrol)

    ros2 run neuravix_ros2 route_planner --ros-args \
      -p pose_topic:=/gnss_pose -p trigger_dist:=6.0

`geojson` parametresi ZATEN `teknik_kontrol.geojson`'a varsayılan.
Log'da şunları GÖRMELİSİN:

    Mission dizisi: ['start', 'hedef']
    ROTA (4 node): [1, 0, 4, 50]
      OLAY 0: turn @node 4 (62.4,12.7) 70° SOL
      OLAY 1: goal @node 50 (64.0,22.1) hedef

Görmezsen dur, sürme.

### 2.7 GAZ — EN SON, alan boş, sürücü frende

    ros2 run bee1_description throttle_ctrl

⚠️ Bu adım gazı devreye alır. Çalıştırır çalıştırmaz araç hareket edebilir.
   Ctrl+C = `RC_THRT_DATA` yayıncısı düşer = gaz kesilir.

---

## 3) KAYIT (sürmeye başlamadan önce başlat)

`docker exec -d` ya da tmux içinde, `-o` yolu `/root/maps` ile başlamalı:

    ros2 bag record -o /root/maps/tk_$(date +%m%d_%H%M) \
      --compression-mode file --compression-format zstd -b 2000000000 \
      /master /neuravix/current_state /neuravix/decision_dump /rosout \
      /neuravix/lane_debug/compressed /neuravix/bev_debug/compressed \
      /velodyne_points /imu/data /tf_static \
      /gnss /gnss_pose /filter/positionlla /filter/quaternion \
      /odometry/can_wheel /safety/emergency_stop \
      /beemobs/FB_VehicleSpeed /beemobs/FeedbackSteeringAngle \
      /beemobs/FB_MotorDriver /beemobs/FB_OMUX_to_AUTONOMOUS \
      /beemobs/rc_unittoOmux /beemobs/AUTONOMOUS_BrakePedalControl \
      /beemobs/steering_target_value /beemobs/speed_target_value \
      /beemobs/AUTONOMOUS_SteeringMot_Control /beemobs/RC_THRT_DATA

Başlattıktan ~15 s sonra `ls -l` ile klasörün büyüdüğünü doğrula
(0 baytlık bag sessizce oluşur).

---

## 4) KOŞU SIRASINDA NE BEKLENİYOR

| aşama | log'da görülecek |
|---|---|
| düz sürüş | `state=LANE_FOLLOW` |
| engel(ler) | `SLALOM ... ` → weave → `serit` |
| virajda dönüş | `/master 5,1,70.0` → `state=PLANNER_TURN` |
| dönüş engelde kesilirse | `DONUS KESILDI ... kalan donus N s saklandi` sonra `YOL ACILDI -> kesilen PLANNER donusu TAMAMLANIYOR` |
| hedefe 6 m kala | `/master 5,4,1` → `HEDEF yaklasmasi: slalom yasak` |
| hedefe 2 m kala | `/master 5,4,0` → `state=MISSION_END`, sürünme |
| duruş | `HEDEF: engel front=N m -> DUR` (lidar) ya da `4.0 m surundu -> DUR` |

`MISSION_END` terminaldir — araç bir daha kalkmaz, düğümü yeniden başlatmak
gerekir.

---

## 5) LOKALİZASYON ÇALIŞMAZSA — el ile tetikleme

Planner komut üretmiyorsa (poz yok / rota kurulmadı), operatör aynı işi
elle yapabilir. Engellere yaklaşırken:

    ros2 topic pub --once /master std_msgs/String "data: '5,4,1'"   # slalom yasak + yavasla
    ros2 topic pub --once /master std_msgs/String "data: '5,4,0'"   # hedef: surunerek yaklas, engelde dur

Dönüş de elle verilebilir (kavşağa ~6 m kala):

    ros2 topic pub --once /master std_msgs/String "data: '5,1,70'"  # 70 derece SOL

---

## 6) ACİL

- Fiziksel acil buton / kumanda (en hızlı yol).
- `throttle_ctrl`'ü Ctrl+C → gaz kesilir.
- `ros2 topic pub --once /safety/emergency_stop std_msgs/Bool "data: true"`
