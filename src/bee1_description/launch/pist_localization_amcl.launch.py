#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pist Localization launch - AMCL sürümü (GERÇEK ARAÇ)
====================================================
pist_localization_real.launch.py'nin ALTERNATİFİ. O dosya OLDUĞU GİBİ DURUYOR
ve hâlâ çalışıyor; bu ayrı bir seçenek, ikisi yan yana yaşar.

TEK FARK 3. NODE:
    localization_slam_toolbox_node   -->   map_server + amcl
can_odom / EKF, pointcloud_to_laserscan ve tüm frame'ler AYNI.
Çıktı yine `map -> odom` TF olduğu için decision_brain, planner ve kontrol
katmanı hiçbir farkı görmez.

NEDEN (2026-08-12 ölçümü):
  slam_toolbox localization kilitliyken 5-7 cm hassasiyette, ama araç hareket
  edince kilidi kaybedip GERİ DÖNEMİYOR -- koşunun %15'i kilitli, medyan
  tarama-harita mesafesi 3.01 m. Dört ayar varyantı denendi, hiçbiri fark
  yaratmadı. Haritada global arama her an 0.03-0.27 m'lik uyum buluyor, yani
  bilgi orada; eksik olan geri dönüş mekanizması. AMCL'de o var
  (recovery_alpha_slow/fast -- config'te AÇILDI, varsayılanı 0.0 = kapalı).

HARİTA FORMATI FARKI:
  slam_toolbox  -> .posegraph + .data
  AMCL          -> .pgm + .yaml (occupancy grid)
  İkincisini zaten üretiyoruz: ~/neuravix_exp/save_map_image.sh <harita_adi>

KULLANIM (offline, masada bag ile):
  ros2 launch bee1_description pist_localization_amcl.launch.py \
      use_sim_time:=true \
      map_yaml:=/home/balman/neuravix_new/maps/pist_C_19_3tem_img.yaml
  # sonra: ros2 bag play <bag> --clock 100 --rate 1.0 --topics ...

KULLANIM (gerçek araçta):
  ros2 launch bee1_description pist_localization_amcl.launch.py \
      map_yaml:=/root/maps/pist_haritasi_img.yaml
  # config'te set_initial_pose:=false yapıp RViz "2D Pose Estimate" ile ver,
  # ya da amcl_pist_real.yaml'daki initial_pose'u start çizgisine göre güncelle.

⚠️ map_yaml MUTLAK YOL alır ve sorunsuz çalışır. (slam_toolbox'ın map_file_name
   parametresi mutlak yolu KABUL ETMEZ -- okurken cwd'yi başa ekler; nav2
   map_server'da o sorun yok.)
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('bee1_description')
    p2l_config = os.path.join(pkg_share, 'config', 'pointcloud_to_laserscan_real.yaml')
    ekf_config = os.path.join(pkg_share, 'config', 'ekf_odom_real.yaml')
    amcl_config = os.path.join(pkg_share, 'config', 'amcl_pist_real.yaml')

    lidar_topic = LaunchConfiguration('lidar_topic')
    map_yaml = LaunchConfiguration('map_yaml')
    use_imu_yaw = LaunchConfiguration('use_imu_yaw')
    use_imu_orientation = LaunchConfiguration('use_imu_orientation')
    imu_topic = LaunchConfiguration('imu_topic')
    steer_gain = LaunchConfiguration('steer_feedback_gain')
    steer_offset = LaunchConfiguration('steer_feedback_offset')
    speed_scale = LaunchConfiguration('speed_scale')
    speed_topic = LaunchConfiguration('speed_topic')
    use_ekf = LaunchConfiguration('use_ekf')
    sim_time = ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)
    use_gnss = LaunchConfiguration('use_gnss')
    gnss_topic = LaunchConfiguration('gnss_topic')
    gnss_threshold = ParameterValue(LaunchConfiguration('gnss_threshold'), value_type=float)
    gnss_enabled = ParameterValue(LaunchConfiguration('gnss_enabled'), value_type=bool)
    # deney: gozetmeni bir zaman penceresinde sustur (tunel benzetimi)
    kor_bas = ParameterValue(LaunchConfiguration('kor_baslangic_s'), value_type=float)
    kor_sure = ParameterValue(LaunchConfiguration('kor_sure_s'), value_type=float)
    datum_lat = ParameterValue(LaunchConfiguration('datum_lat'), value_type=float)
    datum_lon = ParameterValue(LaunchConfiguration('datum_lon'), value_type=float)
    datum_yaw = ParameterValue(LaunchConfiguration('datum_yaw_deg'), value_type=float)
    use_can_odom = LaunchConfiguration('use_can_odom')
    use_wheel_odom = LaunchConfiguration('use_wheel_odom')
    wheel_odom_topic = LaunchConfiguration('wheel_odom_topic')
    gnss_sustain = ParameterValue(LaunchConfiguration('gnss_sustain_s'), value_type=float)
    gnss_min_int = ParameterValue(LaunchConfiguration('gnss_min_interval_s'), value_type=float)
    set_init_pose = ParameterValue(LaunchConfiguration('set_initial_pose'), value_type=bool)
    init_x = ParameterValue(LaunchConfiguration('initial_pose_x'), value_type=float)
    init_y = ParameterValue(LaunchConfiguration('initial_pose_y'), value_type=float)
    init_yaw = ParameterValue(LaunchConfiguration('initial_pose_yaw'), value_type=float)
    use_yer_tanima = LaunchConfiguration('use_yer_tanima')
    yt_db = LaunchConfiguration('yer_tanima_db')
    yt_oran = ParameterValue(LaunchConfiguration('yer_tanima_oran'), value_type=float)
    yt_esik = ParameterValue(LaunchConfiguration('yer_tanima_esik'), value_type=float)
    yt_enabled = ParameterValue(LaunchConfiguration('yer_tanima_enabled'), value_type=bool)

    args = [
        DeclareLaunchArgument('use_sim_time', default_value='false',
                              description='Offline bag replay icin true (+ bag play --clock)'),
        # VARSAYILAN PAKETIN ICINDEKI HARITA (21.08.2026 entegrasyonu).
        # Eskiden /root/maps/pist_haritasi_img.yaml idi; o dosya (a) bu
        # workspace'te yok, (b) 12.08'de terk edilen slam_toolbox yiginina ait
        # ve (c) 20.08'de lidar montaj yuksekligi 0.62 -> 1.35 duzeltilince
        # gecersizlesti. pist_final artik bee1_description/maps altinda kurulu
        # ve imajla birlikte geliyor -- volume'a bagimli degil.
        # Daha yeni bir harita varsa: map_yaml:=/root/maps/<yeni>.yaml
        DeclareLaunchArgument(
            'map_yaml',
            default_value=os.path.join(
                get_package_share_directory('bee1_description'),
                'maps', 'pist_final.yaml'),
            description='Occupancy grid YAML (.pgm yaninda olmali)'),
        # can_odom argumanlari pist_localization_real ile BIREBIR AYNI
        DeclareLaunchArgument('use_ekf', default_value='false',
                              description='true: odom->base_link EKF surer (can_odom TF kapanir)'),
        DeclareLaunchArgument('lidar_topic', default_value='/velodyne_points'),
        DeclareLaunchArgument('use_imu_yaw', default_value='true'),
        DeclareLaunchArgument('use_imu_orientation', default_value='false'),
        DeclareLaunchArgument('imu_topic', default_value='/imu/data'),
        DeclareLaunchArgument('steer_feedback_gain', default_value='-0.02322'),
        DeclareLaunchArgument('steer_feedback_offset', default_value='2.0'),
        DeclareLaunchArgument('speed_scale', default_value='0.31627'),
        DeclareLaunchArgument('speed_topic', default_value='/beemobs/FB_VehicleSpeed'),
        # --- GNSS gozetmeni (varsayilan KAPALI -- mevcut davranis degismez) ---
        DeclareLaunchArgument('use_gnss', default_value='false',
                              description='true: GNSS gozetmeni AMCL aliasing ini duzeltir'),
        DeclareLaunchArgument('gnss_topic', default_value='/gnss'),
        # ⚠️ 5.0 -> 18.0 (2026-08-13). Ilk deger YANLISTI: haritanin KENDISI
        # gercege gore burulmus. Elle dogrulanmis 7 cipa noktasinda GNSS ile
        # harita arasindaki artik 6-17 m (RMS 11.1) -- yani DOGRU yerdeki bir
        # arac bile sirf harita burulmasi yuzunden GNSS'ten ~12 m ayri gorunur.
        # 5 m esigiyle gozetmen surekli ve HAKSIZ yere tetikleniyordu.
        # Ayirmak istedigimiz sey aliasing: 30-130 m. Arada genis bir bosluk var.
        # 18.0 -> 3.0 (2026-08-22, yazarin teyidi). 18.0 13 Agustos'tan kalmaydi:
        # o gun haritanin KENDISI gercege gore ~11 m burulmustu. 19 Agustos'ta
        # datum yer tanimanin 594 eslesmesinden yeniden cozuldu, burulma medyani
        # 1.54 m'ye indi ve 3.0 uc bagimsiz bag'de dogrulandi (LOK19 3.81 -> 0.98 m,
        # pist_17tem_2 1.57 -> 1.19 m, tohum sayisi 7 -> 9, patlamadi).
        DeclareLaunchArgument('gnss_threshold', default_value='3.0',
                              description='Bu kadar m ayrisma surerse yeniden tohumlar'),
        # YARIS HIZI AYARLARI -- gozetmenin tepki gecikmesi sustain_s'tir
        # (25 s yalnizca LOG araligi, karar her GNSS fix'inde 4 Hz veriliyor).
        # 0.66 m/s'de sustain 2.0 s = 1.3 m yol; 15 km/h'de ayni 2 s = 8.4 m.
        # Yazarin yaris onerisi: sustain 1.0 / min_interval 3.0 -- SAHADA A/B EDIN,
        # olcut tur boyunca tohum sayisi + ortalama ayrisma (tohum 15-20'yi
        # geciyorsa sustain'i geri acin).
        DeclareLaunchArgument('gnss_sustain_s', default_value='2.0',
                              description='Ayrisma bu kadar surerse tohumlar (yaris: 1.0)'),
        DeclareLaunchArgument('gnss_min_interval_s', default_value='5.0',
                              description='Iki tohumlama arasi en az sure (yaris: 3.0)'),
        # false: yalnizca olcer ve raporlar, MUDAHALE ETMEZ (esikleri gormek icin)
        DeclareLaunchArgument('gnss_enabled', default_value='true'),
        DeclareLaunchArgument('kor_baslangic_s', default_value='0.0',
                              description='GNSS gozetmenini sustur: baslangic (bag basindan saniye)'),
        DeclareLaunchArgument('kor_sure_s', default_value='0.0',
                              description='GNSS gozetmenini sustur: sure (0 = kor pencere yok)'),
        # DATUM -- pist_C_19_3tem haritasina OZEL. BASKA HARITA -> YENIDEN OLC.
        # 2026-08-13, ikinci hesap: M1 kosusunda insanin ELLE dogruladigi 7 poz
        # cipa alindi (pistin farkli yerlerinde, 65x67 m yayilim).
        # Ilk hesap (RANSAC, 1365 pozun %8'i ic nokta) YANLISTI -- zayif uzlasma
        # yuzunden araci haritanin DISINA koyuyordu. Dogrulama olarak artik
        # "GNSS izinin tamami harita sinirlari icinde mi" kontrol ediliyor: %100.
        # ⚠️ DOGRULANMIS CIFT (2026-08-20). Bu ucu birlikte degistir, tek basina
        # degil: lat/lon harita (0,0)'in karsiligidir, yarismanin datum satiri
        # DEGIL (bkz. KURULUM.md). Eski varsayilanlar (-121.22) 28 derece
        # yanlisti ve argumansiz calistirildiginda sessizce bozuk poz veriyordu.
        DeclareLaunchArgument('datum_lat', default_value='40.79041010'),
        DeclareLaunchArgument('datum_lon', default_value='29.50912636'),
        DeclareLaunchArgument('datum_yaw_deg', default_value='-149.20'),
        # --- YER TANIMA gozetmeni (varsayilan KAPALI -- mevcut davranis degismez) ---
        # GNSS gozetmeninin ALTERNATIFI; ikisini ayni anda ACMAYIN, ayni
        # /initialpose'u surerler.
        # Odometri kaynagini KAPATMAK icin (varsayilan acik -- mevcut davranis
        # degismez). Hiz/direksiyon verisi OLMAYAN bag'lerde can_odom sifir
        # hizla gyro yaw'i entegre edip odom->base_link'i surer; harici bir
        # odometri (or. LiDAR odometrisi) ayni TF kenarini surerse IKI YAYINCI
        # carpisir ve AMCL kacar (2026-08-18: medyan hata 52 m, maks 874 m).
        DeclareLaunchArgument('use_can_odom', default_value='true',
                              description='false: can_odom/EKF hic baslatilmaz '
                                          '(odom->base_link disaridan gelir)'),
        # Odometriyi araca hazir gelen /odometry/can_wheel'den al (can_odom
        # yerine). 2026-08-20'de olculdu: can_odom kat edilen yolu %25 eksik
        # veriyor, bu topic %6-9. Hareket halindeki medyan hata 3.67 -> 1.45 m.
        # ⚠️ Varsayilan FALSE: yalnizca iki kisa bag'de (lokal_0820_*) dogrulandi
        # ve temmuz bag'lerinde bu topic YOK. Sahada bir kez teyit edilmeden
        # yarista acilmasin -- topic akmazsa odom->base_link TF hic uretilmez.
        DeclareLaunchArgument('use_wheel_odom', default_value='false',
                              description='true: /odometry/can_wheel -> odom->base_link TF '
                                          '(can_odom baslatilmaz)'),
        DeclareLaunchArgument('wheel_odom_topic', default_value='/odometry/can_wheel'),
        # BASLANGIC POZU -- eskiden amcl_pist_real.yaml'a GOMULUYDU ve oradaki
        # (2.05, 0.76) degeri BASKA harita+bag icindi (pist_C_19_3tem +
        # pist_17tem_2). Her yarisma gununun geojson'unun kendi 'start'i var,
        # yani gomulu kalmasi tanimi geregi yanlis. Gunun degerini
        # maps/yarisma_donusum.py uretir:
        #   teknik kontrol start (95.15, 48.88) -> harita (20.51, 3.89) yaw 10.03deg
        # Gozetmen 2-3 saniyede zaten duzeltiyor, ama yaris gunu hazirlik suresi
        # 3 dakika -- RViz'de tiklamaya vakit harcamayin, argumanla verin.
        DeclareLaunchArgument('set_initial_pose', default_value='true',
                              description='false: poz RViz 2D Pose Estimate ile elle verilir'),
        DeclareLaunchArgument('initial_pose_x', default_value='20.51'),
        DeclareLaunchArgument('initial_pose_y', default_value='3.89'),
        DeclareLaunchArgument('initial_pose_yaw', default_value='0.1749',
                              description='RADYAN (10.03 derece = teknik kontrol start)'),
        DeclareLaunchArgument('use_yer_tanima', default_value='false',
                              description='true: LiDAR yer tanima gozetmeni AMCL aliasing ini duzeltir'),
        DeclareLaunchArgument('yer_tanima_db',
                              default_value='/root/maps/yer_tanima_db.npz',
                              description='yer_tanima_db.py ile uretilen veritabani (.npz). '
                                          'HARITAYI ureten kosunun pozlarindan kurulmus olmali.'),
        # Oran testi esigi. Olculdu (capraz oturum, GNSS referansi):
        #   0.85 -> kapsama %25, kesinlik %100
        #   0.90 -> kapsama %53, kesinlik %100   <- secilen
        #   0.95 -> kapsama %66, kesinlik %92.5
        # Gozetmen icin kesinlik kapsamadan onemli: yanlis tohumlama AMCL'i
        # duzeltmek yerine bozar, dogru tohumlama ise saniyede bir gelse yeter.
        DeclareLaunchArgument('yer_tanima_oran', default_value='0.90'),
        # Yer tanimanin kendi hatasi 1.6 m, AMCL'in mesru hatasi ~0.5 m.
        # 4 m ikisiyle de aciklanamaz -> aliasing.
        DeclareLaunchArgument('yer_tanima_esik', default_value='4.0'),
        # false: yalnizca olcer ve raporlar, MUDAHALE ETMEZ.
        DeclareLaunchArgument('yer_tanima_enabled', default_value='true'),
    ]

    # 1) CAN odometri -- pist_localization_real ile AYNI
    _can_odom_params = {
        'use_sim_time': sim_time,
        'use_imu_yaw': use_imu_yaw,
        'use_imu_orientation': use_imu_orientation,
        'imu_topic': imu_topic,
        'steer_feedback_gain': steer_gain,
        'steer_feedback_offset': steer_offset,
        'speed_scale': speed_scale,
        'speed_topic': speed_topic,
    }
    can_odom_tf = Node(
        package='bee1_description', executable='can_odom', name='can_odom_node',
        output='screen',
        parameters=[dict(_can_odom_params, publish_tf=True)],
        condition=IfCondition(PythonExpression(["'", use_can_odom, "'=='true' and '", use_ekf,
                                            "'!='true' and '", use_wheel_odom, "'!='true'"])),
    )
    can_odom_notf = Node(
        package='bee1_description', executable='can_odom', name='can_odom_node',
        output='screen',
        parameters=[dict(_can_odom_params, publish_tf=False)],
        condition=IfCondition(PythonExpression(["'", use_can_odom, "'=='true' and '", use_ekf,
                                            "'=='true' and '", use_wheel_odom, "'!='true'"])),
    )
    ekf_odom = Node(
        package='robot_localization', executable='ekf_node', name='ekf_odom',
        output='screen',
        parameters=[ekf_config, {'use_sim_time': sim_time}],
        condition=IfCondition(PythonExpression(["'", use_can_odom, "'=='true' and '", use_ekf,
                                            "'=='true' and '", use_wheel_odom, "'!='true'"])),
    )

    # 1b) Tekerlek odometrisi TF koprusu -- can_odom'un ALTERNATIFI (ikisi ayni
    # anda odom->base_link surerse AMCL kacar, bkz. tekerlek_odom_tf.py)
    tekerlek_odom = Node(
        package='bee1_description', executable='tekerlek_odom_tf',
        name='tekerlek_odom_tf', output='screen',
        parameters=[{'use_sim_time': sim_time, 'odom_topic': wheel_odom_topic}],
        condition=IfCondition(use_wheel_odom),
    )

    # 2) 3D bulut -> 2D scan -- pist_localization_real ile AYNI
    p2l = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[p2l_config, {'use_sim_time': sim_time}],
        remappings=[('cloud_in', lidar_topic), ('scan', '/scan_bee1')],
    )

    # 3a) Haritayi yayinla (occupancy grid)
    map_server = Node(
        package='nav2_map_server', executable='map_server', name='map_server',
        output='screen',
        parameters=[{'use_sim_time': sim_time, 'yaml_filename': map_yaml}],
    )

    # 3b) AMCL -- map->odom TF'i bu surer (slam_toolbox'in yerine)
    amcl = Node(
        package='nav2_amcl', executable='amcl', name='amcl',
        output='screen',
        # Baslangic pozu yaml'daki degeri EZER (yaml'daki (2.05,0.76) baska
        # harita+bag icindi). nav2_amcl bu dort ismi ic ice parametre olarak
        # tanimlar; nokta gosterimi dogru kullanimdir.
        parameters=[amcl_config, {
            'use_sim_time': sim_time,
            'set_initial_pose': set_init_pose,
            'initial_pose.x': init_x,
            'initial_pose.y': init_y,
            'initial_pose.z': 0.0,
            'initial_pose.yaw': init_yaw,
        }],
    )

    # 3c) nav2 node'lari LIFECYCLE node -- configure+activate edilmeleri sart,
    #     yoksa sessizce hicbir sey yayinlamazlar. Bu yuzden lifecycle_manager
    #     slam_toolbox yolunda olmayan EK bir node.
    #
    # ⚠️ use_sim_time BILEREK False (sim_time DEGIL). 2026-08-12'de ilk denemede
    #    true verilmisti ve node'lar HIC aktiflesmedi: "Waiting on external
    #    lifecycle transitions to activate" deyip asili kaldi. Sebep, ROS
    #    zamaninin /clock gelene kadar sifirda donuk olmasi -- manager'in
    #    baslatma zamanlayicisi hic atesenmiyor, bag ise 15 s sonra basliyor.
    #    Manager yalnizca lifecycle servis cagrilarini siraya koyar, sensor
    #    verisiyle isi yoktur; duvar saatiyle calismasi dogru olan.
    #    (map_server ve amcl sim_time kullanmaya DEVAM ediyor, onlar TF/tarama
    #     zamanlamasi icin gercekten gerekli.)
    lifecycle = Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_localization', output='screen',
        parameters=[{
            'use_sim_time': False,
            'autostart': True,
            'node_names': ['map_server', 'amcl'],
            'bond_timeout': 0.0,     # bag replay'de saat siciradiginda bond kopmasin
        }],
    )

    # 3d) GNSS gozetmeni (SADECE use_gnss:=true). AMCL'e KARISMAZ, yalnizca
    #     izler: GNSS ile AMCL uzun sure ayrisirsa /initialpose ile geri cagirir.
    #     Olculen kusura nisan aliyor -- "kilitli" pozlarin %92'si aliasing
    #     yuzunden yanlis yerdeydi (2026-08-13, RANSAC ile olculdu).
    #     Datum bu haritaya OZEL; harita degisirse yeniden olculmeli.
    gnss_sup = Node(
        package='bee1_description', executable='gnss_supervisor',
        name='gnss_supervisor', output='screen',
        parameters=[{
            'use_sim_time': sim_time,
            'datum_lat': datum_lat,
            'datum_lon': datum_lon,
            'datum_yaw_deg': datum_yaw,
            'gnss_topic': gnss_topic,
            'threshold_m': gnss_threshold,
            'sustain_s': gnss_sustain,
            'min_interval_s': gnss_min_int,
            'enabled': gnss_enabled,
            'kor_baslangic_s': kor_bas,
            'kor_sure_s': kor_sure,
        }],
        condition=IfCondition(use_gnss),
    )

    # 3e) YER TANIMA gozetmeni (SADECE use_yer_tanima:=true). GNSS gozetmeninin
    #     yerini alir; ikisini AYNI ANDA acmayin -- ayni /initialpose'u surerler.
    #     GNSS gozetmeni neden basarisiz oldu, bu neden olmuyor: GNSS gercek
    #     dunyada, harita ise kendi burulmus cercevesinde (~12 m). Duzeltilecek
    #     hata 20-26 m; iki dagilim ust uste binince esik bulunamadi. Yer tanima
    #     tamamen harita cercevesinde calisir (veritabani pozlari haritayi ureten
    #     kosudan gelir), burulma sadelesir. Ayrica GNSS'in veremedigi YON'u de
    #     verir (2026-08-17: medyan yaw hatasi 7 derece).
    #     Olculen (capraz oturum, farkli gunlerin bag'leri, GNSS referansi):
    #       mevcut 2B /scan ile : top-1 %27 dogru, hata 13.6 m
    #       Scan Context + oran testi 0.90 : kapsama %53, KESINLIK %100, hata 1.6 m
    yer_tanima = Node(
        package='bee1_description', executable='yer_tanima',
        name='yer_tanima', output='screen',
        parameters=[{
            'use_sim_time': sim_time,
            'db_path': yt_db,
            'lidar_topic': lidar_topic,
            'oran_esigi': yt_oran,
            'esik_m': yt_esik,
            'enabled': yt_enabled,
        }],
        condition=IfCondition(use_yer_tanima),
    )

    return LaunchDescription(
        args + [can_odom_tf, can_odom_notf, ekf_odom, tekerlek_odom, p2l,
                map_server, amcl, lifecycle, gnss_sup, yer_tanima])
