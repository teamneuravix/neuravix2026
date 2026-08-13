#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Engel Tespit Node - Lidar -> /master (ID 4)
================================================================
Lidar point cloud'undan onundeki/yanindaki engel mesafelerini hesaplar ve
karar beynine (/master) yayinlar.

/master formati (decision_brain bunu bekler):
    "4,<front>,<left>,<right>"   (metre; 99 = temiz, 0 = kapali/veri yok)

Sektorler (lidar sensor frame, ROS REP-103: x ileri, +y SOL, z yukari).
UCUNUN DE OLCUSU AYNI: "o koridorda ilerlersem tamponum carpana kadar kac
metrem var" (BOYLAMSAL mesafe, sensorden degil ON TAMPONDAN itibaren):
  - front : |y| < corridor                     -> ego koridoru
  - left  : |y - side_offset| < corridor       -> sola kacarsam girecegim koridor
  - right : |y + side_offset| < corridor       -> saga kacarsam girecegim koridor

  ⚠ ANLAM DEGISIKLIGI (2026-07-21): left/right eskiden "en yakin noktanin YANAL
    uzakligi" idi. O tanim matematiksel olarak `corridor`'dan kucuk deger
    uretemiyordu; koridor kenarinin hemen disindaki tek bir nokta degeri
    corridor'a civiliyor, decision_brain'in safe_side_distance=2.0 esigi de
    o tarafi kalici "kapali" sayiyordu (07-20 log'undaki "left dakikalarca tam
    1.20 m" ve "_pick_avoid_direction asla sol secmiyor" bulgusu).
    Yeni tanimda left/right, front ile ayni birimde ve dogrudan
    "o tarafa kacabilir miyim" sorusunun cevabi -> beynin esikleri anlamli.

Gurultu dayanikliligi (07-20 log'undaki "front 1 saniyede 99 <-> 1.1 zipliyor"):
  - Uzaysal: tek nokta engel sayilmaz; bir engelin raporlanmasi icin sektorde
    en az `min_points` nokta gerekir ve mesafe olarak en yakin noktanin degil
    `min_points`. noktanin mesafesi kullanilir.
  - Zamansal: son `filter_window` karenin en kucuk `confirm_frames`. degeri
    raporlanir. Ayni islem olmasina ragmen SONUC ASIMETRIKTIR: istatistigi
    asagi cekmek `confirm_frames` kadar yakin kare ister, yukari itmek ise
    `filter_window - confirm_frames + 1` kadar temiz kare. Varsayilanlarda
    (5 kare pencere, k=2) -> engel 2 karede (~0.2 s) raporlanir, ancak
    4 kare (~0.4 s) temiz gorulmeden birakilmaz. Yavas birakma = guvenli taraf.

Fail-safe: lidar susarsa/bos bulut gonderirse `lidar_timeout` sonrasi "0,0,0"
yayinlanir (= dur), bayat 99'lar DEGIL. Bu araçta surucunun sessizce olmesi
defalarca yasandi (Velodyne poll() timeout, reboot sonrasi askida kalan
suruculer, /dev/shm sahiplik cakismasi) — "veri yok" asla "yol acik" demek
degildir.
  decision_brain'de dogrulandi (2026-07-21): "4,0,0,0" -> _pick_avoid_direction
  None doner (slalom YOK), OBSTACLE_STOP + brake=1 + target_speed=0, ve
  left/right<=1.0 oldugu icin A* costmap'ine hayali engel de islenmez.
  Veri donunce _update_state_machine front>slow_distance gorup LANE_FOLLOW'a
  kendiliginden geri doner. Kilitlenme yok.

Calistirma:
    # GERCEK ARAC — tum varsayilanlar Bee1'e gore, ekstra parametre gerekmez
    ros2 run neuravix_ros2 obstacle_lidar

    # CARLA SIM — IKI parametre de sart (lidar 1.6 m'de ve topic farkli)
    ros2 run neuravix_ros2 obstacle_lidar --ros-args \
        -p lidar_topic:=/carla/ego_vehicle/lidar -p lidar_height:=1.6
    # lidar_height'i unutursan pencere kayar ve TUM engeller filtrelenir
    # (sessiz fail-open). Node zemin donuslerinden montaj yuksekligini tahmin
    # edip uyusmazlikta ERROR basar — o log'u gormezden gelme.

    # y ekseni ters cikarsa (sol/sag yer degistirirse):
    ros2 run neuravix_ros2 obstacle_lidar --ros-args -p flip_y:=true

Ayar parametreleri CALISIRKEN degistirilebilir (`ros2 param set`); sadece
lidar_topic/master_topic/rate_hz baslangicta okunur.
"""
import sys
from collections import deque

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rcl_interfaces.msg import SetParametersResult
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import String

try:
    from sensor_msgs_py import point_cloud2 as pc2
except ImportError:
    sys.exit("sensor_msgs_py yok (ROS2 humble ile gelir)")

CLEAR = 99.0    # "engel yok" sentinel — decision_brain bu degeri bekler
BLOCKED = 0.0   # "hic klerans yok" / "veri yok" -> beyin durur


class ObstacleLidarNode(Node):

    # Calisirken degistirilebilen ayarlar (tip gruplarina gore)
    _FLOAT_TUNABLE = ("corridor", "side_offset", "side_corridor",
                      "side_x_min", "x_min",
                      "max_range", "z_min", "z_max", "bumper_offset",
                      "lateral_offset", "lidar_timeout", "log_period",
                      "mount_check_tol")
    _INT_TUNABLE = ("min_points", "filter_window", "confirm_frames")
    _BOOL_TUNABLE = ("flip_y", "near_field_guard")

    def __init__(self):
        super().__init__("obstacle_lidar_node")

        # --- sadece baslangicta okunanlar -------------------------------
        # Varsayilan GERCEK ARAC (digerleriyle tutarli). CARLA icin acikca
        # -p lidar_topic:=/carla/ego_vehicle/lidar verilmeli; verilmezse node
        # hicbir buluta abone olamaz ve fail-safe'e duser (gurultulu sekilde
        # durur), sessizce yanlis veri uretmez.
        self.declare_parameter("lidar_topic", "/velodyne_points")
        self.declare_parameter("master_topic", "/master")
        self.declare_parameter("rate_hz", 10.0)
        self.lidar_topic = self.get_parameter("lidar_topic").value
        self.master_topic = self.get_parameter("master_topic").value

        # --- yukseklik penceresi ----------------------------------------
        # Pencere YERE gore tanimlanir, sensor frame'ine cevrilir. Boylece
        # montaj yuksekligi degisince (CARLA 1.6 m <-> gercek 1.35 m) elle
        # z_min hesaplamak gerekmez. Eski hali sabit z_min=-1.3 idi ve gercek
        # araca gecerken elle daraltilmazsa zemini kalici engel sayiyordu.
        # Degerler pointcloud_to_laserscan_real.yaml ile ayni (yerden 0.22 /
        # 2.12 m): tunel tavani ve ust gecitler disarida kalir.
        #
        # 1.35: UC gercek pist bag'inin zemin donuslerinden olculdu
        # (2026-07-21): pist_17tem_2 -> 1.29, pist_18tem -> 1.31,
        # pist_19_3tem -> 1.41 (5-20 m halkasindaki noktalarin z modu).
        # URDF lidar_z de ayni gun 0.620 -> 1.350 duzeltildi (eski deger bu
        # verilerle celisiyordu); MEZURAYLA TEYIT EDILMELI. Yanlis yukseklikle
        # 0.62 ornegi: pencere yerden [0.22,2.12] SANILIR ama gercekte
        # [0.95,2.85] olur -> 1 m altindaki her sey (koni, alcak bariyer,
        # arac alt govdesi) sessizce filtrelenir.
        self.declare_parameter("lidar_height", 1.35)
        self.declare_parameter("ground_clearance", 0.22)     # yerden alt sinir
        self.declare_parameter("max_obstacle_height", 2.12)  # yerden ust sinir
        h = float(self.get_parameter("lidar_height").value)
        gc = float(self.get_parameter("ground_clearance").value)
        mh = float(self.get_parameter("max_obstacle_height").value)
        self.declare_parameter("z_min", gc - h)   # varsayilani yukaridan turer
        self.declare_parameter("z_max", mh - h)
        self.lidar_height = h
        # Yanlis lidar_height sessiz FAIL-OPEN uretir (or. CARLA'nin 1.6 m'lik
        # lidar'ini 1.35 varsayilaniyla calistirinca pencere yerden [0.47,2.37]
        # olur; zemine yakin engeller disarida kalir -> 99 = temiz gorunur).
        # Bu kontrol 2026-07-21'de tam da boyle bir hatayi yakaladi.
        # Zemin donuslerinden gercek montaj yuksekligini tahmin edip uyariyoruz.
        self.declare_parameter("mount_check_tol", 0.35)
        self._mount_checks_left = 20

        # --- koridor geometrisi (URDF bee1_robotaxi.urdf.xacro) ---------
        # body_width=1.06 -> yari genislik 0.53; corridor = 0.53 + ~0.17 pay.
        # (Eski 1.2 -> 2.4 m'lik koridor, aracin iki katindan genisti ve
        #  bariyerli pistte virajlarda hayalet engel uretiyordu.)
        self.declare_parameter("corridor", 0.70)
        # Kacis koridoru = KOMSU/KARSI SERIT (2026-08-03 pist olcusu: serit
        # genisligi 3.0 m). side_offset komsu serit MERKEZI, side_corridor o
        # seridin yari genisligi -> sol koridor y in [1.5, 4.5], sag y in
        # [-4.5,-1.5]. Boylece left/right klerans "o seride kacabilir miyim"
        # sorusunun boylamsal cevabidir (slalom_sim.py ile AYNI geometri;
        # ikisi degisince birlikte degismeli).
        # ESKI tasarim (side_offset=1.40 = 2*corridor, side_corridor=corridor)
        # bitisik seridi olcuyordu; pistin 3.0 m serit genisligine gecildi.
        # NOT: front |y|<=0.70 ile side |y-3.0|<1.5 arasinda y in (0.70,1.50)
        # olu bolgesi olusur; 1.4 m'lik pist engeli iki sektore de girdigi
        # icin sorun degil, ama serit cizgisi ustundeki INCE cisim kacabilir.
        self.declare_parameter("side_offset", 3.0)
        # 1.5 -> 1.0 (2026-08-10 CARLA): side_corridor=1.5 iken sol koridor
        # y in [1.5,4.5] KOMSU SERIDIN SINIRINDA (y=1.5) basliyor; sag seridi
        # dolduran genis bir engel/bariyer o siniri yaliyor ve sol koridoru
        # "dolu" gosteriyordu (left ~ front). 1.0 -> koridor y in [2.0,4.0],
        # yani TEMIZ sol serit; engel kenari olu bolgeye dusup left=99 (acik)
        # okunur. Olu bolge y in (0.70,2.0)'ye genisler (kabul edilebilir).
        self.declare_parameter("side_corridor", 1.0)
        # Yan koridorda geriye bakis siniri = arka tampon hizasi:
        #   -(wheelbase 1.86 + rear_overhang 0.47) - lidar_x 0.177 = -2.51
        # Aracin YANINDA duran bir cisim hala kacisi engeller; ondan daha
        # geride kalan (coktan gecilmis) seyler engellememeli.
        self.declare_parameter("side_x_min", -2.51)
        # Mesafeler tampondan olculur: front_overhang 0.410 - lidar_x 0.177
        self.declare_parameter("bumper_offset", 0.233)
        self.declare_parameter("lateral_offset", 0.0)   # URDF lidar_y
        self.declare_parameter("x_min", 0.5)            # kendi govdesi/yakin alan reddi
        self.declare_parameter("max_range", 30.0)       # ileri bakis siniri
        self.declare_parameter("flip_y", False)
        self.declare_parameter("near_field_guard", True)

        # --- filtreler ---------------------------------------------------
        self.declare_parameter("min_points", 4)      # engel = en az N nokta
        self.declare_parameter("filter_window", 5)   # zamansal pencere (kare)
        self.declare_parameter("confirm_frames", 2)  # k-of-n onayi
        self.declare_parameter("lidar_timeout", 0.5)  # bu surede bulut yoksa fail-safe
        self.declare_parameter("log_period", 2.0)

        # filter_window ONCE okunur: deque'ler daha ilk kareden itibaren dogru
        # maxlen ile kurulsun (asagidaki dongunun sirasina bagli kalmasin).
        self.filter_window = max(1, int(self.get_parameter("filter_window").value))
        self._hist = {k: deque(maxlen=self.filter_window)
                      for k in ("front", "left", "right")}
        for name in (self._FLOAT_TUNABLE + self._INT_TUNABLE + self._BOOL_TUNABLE):
            self._apply_param(name, self.get_parameter(name).value)
        self.add_on_set_parameters_callback(self._on_params)

        self._last_cloud_t = None

        self.pub = self.create_publisher(String, self.master_topic, 10)
        # sensor_data QoS (best-effort): gercek lidar suruculeri (Velodyne)
        # best-effort yayinlar; reliable abonelik onlarla hic eslesmez.
        # Best-effort abonelik CARLA'nin reliable yayiniyla da eslesir.
        self.sub = self.create_subscription(
            PointCloud2, self.lidar_topic, self.cloud_cb,
            qos_profile_sensor_data)

        rate = float(self.get_parameter("rate_hz").value)
        self.timer = self.create_timer(1.0 / max(0.1, rate), self.publish_master)

        self.get_logger().info(
            f"Engel lidar: {self.lidar_topic} -> {self.master_topic} (ID 4)\n"
            f"  koridor=+-{self.corridor:.2f} m, yan koridor merkezi="
            f"+-{self.side_offset:.2f} m (yari gen. {self.side_corridor:.2f}), "
            f"ileri menzil={self.max_range:.1f} m\n"
            f"  z penceresi=[{self.z_min:.2f}, {self.z_max:.2f}] "
            f"(lidar_height={h:.2f} -> yerden [{self.z_min + h:.2f}, "
            f"{self.z_max + h:.2f}] m)\n"
            f"  min_points={self.min_points}, pencere={self.filter_window} kare, "
            f"onay={self.confirm_frames} kare, timeout={self.lidar_timeout:.1f} s\n"
            f"  mesafeler on tampondan ({self.bumper_offset:.3f} m) olculur")

    # ------------------------------------------------------------------
    # Parametreler
    # ------------------------------------------------------------------
    def _apply_param(self, name, value):
        if name in self._FLOAT_TUNABLE:
            setattr(self, name, float(value))
        elif name in self._BOOL_TUNABLE:
            setattr(self, name, bool(value))
        elif name == "min_points":
            self.min_points = max(1, int(value))
        elif name == "confirm_frames":
            self.confirm_frames = max(1, int(value))
        elif name == "filter_window":
            win = max(1, int(value))
            if win != self.filter_window:
                self.filter_window = win
                self._hist = {k: deque(v, maxlen=win)
                              for k, v in self._hist.items()}

    def _on_params(self, params):
        """Calisma anindaki `ros2 param set` cagrilari. Eskiden parametreler
        sadece __init__'te okunuyordu ve `param set` sessizce hicbir sey
        yapmiyordu (lane_follower'in err_offset tuzaginin aynisi).
        Tanimadigimiz parametreler (use_sim_time gibi altyapi parametreleri
        dahil) dokunulmadan gecirilir — reddedilirse rclpy'nin kendi
        cagrilari da basarisiz olur."""
        known = self._FLOAT_TUNABLE + self._INT_TUNABLE + self._BOOL_TUNABLE
        for p in params:
            if p.name not in known:
                continue
            if p.name in ("corridor", "max_range") and float(p.value) <= 0.0:
                return SetParametersResult(
                    successful=False, reason=f"'{p.name}' pozitif olmali")
            if p.name in self._INT_TUNABLE and int(p.value) < 1:
                return SetParametersResult(
                    successful=False, reason=f"'{p.name}' >= 1 olmali")
        for p in params:
            if p.name in known:
                self._apply_param(p.name, p.value)
        return SetParametersResult(successful=True)

    # ------------------------------------------------------------------
    # Bulut isleme
    # ------------------------------------------------------------------
    def _xyz(self, cloud: PointCloud2):
        # read_points_numpy KULLANMA: field_names verilse bile buluttaki TUM
        # field'lar ayni datatype degilse assert ile patliyor. Velodyne
        # bulutlari karisik tipli (x/y/z float32 + ring uint16) — CARLA'nin
        # hepsi-float32 bulutlarinda gorunmeyen bu cokme gercek aracta ilk
        # mesajda node'u oldurdu (2026-07-12). read_points structured array
        # dondurur ve tip karisikligindan etkilenmez.
        pts = pc2.read_points(cloud, field_names=("x", "y", "z"), skip_nans=True)
        empty = np.empty(0, dtype=np.float32)
        if isinstance(pts, np.ndarray):  # Humble: structured ndarray
            if pts.size == 0:
                return empty, empty.copy(), empty.copy()
            return (np.asarray(pts["x"], dtype=np.float32),
                    np.asarray(pts["y"], dtype=np.float32),
                    np.asarray(pts["z"], dtype=np.float32))
        arr = np.array([[p[0], p[1], p[2]] for p in pts],  # eski API (Foxy)
                       dtype=np.float32)
        if arr.size == 0:
            return empty, empty.copy(), empty.copy()
        return arr[:, 0], arr[:, 1], arr[:, 2]

    def cloud_cb(self, cloud: PointCloud2):
        # BOS bulut "engel yok" DEGILDIR, "surucu veri uretmiyor"dur.
        # Zaman damgasini guncellemiyoruz -> timeout devreye girer -> fail-safe.
        if cloud.width * cloud.height == 0:
            self.get_logger().warn(
                "Bos PointCloud2 geldi (surucu?) - veri yok sayiliyor",
                throttle_duration_sec=5.0)
            return

        try:
            x, y, z = self._xyz(cloud)
        except Exception as exc:
            # bozuk/beklenmedik bulut node'u oldurmesin — uyar ve mesaji atla.
            # Damga guncellenmedigi icin hata surerse fail-safe'e duseriz.
            self.get_logger().warn(
                f"PointCloud2 okunamadi, mesaj atlandi: {exc}",
                throttle_duration_sec=5.0)
            return

        if x.size == 0:  # ham nokta var ama hepsi NaN -> yine surucu sorunu
            self.get_logger().warn(
                "Bulutta gecerli (NaN olmayan) nokta yok - veri yok sayiliyor",
                throttle_duration_sec=5.0)
            return

        self._check_mount_height(z)

        if self.flip_y:
            y = -y
        y = y - self.lateral_offset   # koridorlari arac ekseninde merkezle

        # zemin + yuksek (tunel tavani, ust gecit) filtresi
        m = (z > self.z_min) & (z < self.z_max)
        x, y = x[m], y[m]
        # Buradan sonra x bos olabilir: bu MESRU "acik yol" durumudur
        # (ham bulut dolu, sadece yukseklik penceresinde nokta yok) ve
        # yardimcilar dogal olarak CLEAR dondurur.

        self._hist["front"].append(self._front_clearance(x, y))
        self._hist["left"].append(self._side_clearance(x, y, +self.side_offset))
        self._hist["right"].append(self._side_clearance(x, y, -self.side_offset))
        self._last_cloud_t = self.get_clock().now()

    def _check_mount_height(self, z):
        """Ilk karelerde zemin donuslerinden montaj yuksekligini tahmin et ve
        `lidar_height` ile karsilastir. Yanlis yukseklik yukseklik penceresini
        kaydirir ve sessizce TUM engelleri filtreler (fail-open) — bu, sim/arac
        arasi gecerken en kolay yapilan hata."""
        if self._mount_checks_left <= 0 or z.size < 200:
            return
        self._mount_checks_left -= 1
        est = -float(np.percentile(z, 10))   # zemin ~ en dusuk %10'luk dilim
        if abs(est - self.lidar_height) > self.mount_check_tol:
            self.get_logger().error(
                f"MONTAJ YUKSEKLIGI UYUSMUYOR: lidar_height={self.lidar_height:.2f} m "
                f"ama zemin donusleri ~{est:.2f} m diyor. Yukseklik penceresi "
                f"kaymis olabilir -> engeller filtrelenip 'temiz' gorunebilir. "
                f"CARLA icin -p lidar_height:=1.6 verdin mi?",
                throttle_duration_sec=5.0)

    def _robust_distance(self, xs):
        """Sektordeki `min_points`. en yakin noktanin tampondan boylamsal
        mesafesi. Mutlak min yerine k'inci min: tek noktalik gurultunun
        (toz, yagmur, sicrama, tumsekte tek zemin donusu) engel sayilmasini
        onler. Negatif sonuc = cisim tamponun hizasinda -> 0 (kapali)."""
        if xs.size < self.min_points:
            return CLEAR
        k = self.min_points - 1
        return max(0.0, float(np.partition(xs, k)[k]) - self.bumper_offset)

    def _front_clearance(self, x, y):
        # Ego koridoru: kendi seridimiz, |y| <= corridor (0.70). Yan koridorlar
        # artik komsu seritte (side_offset=3.0 +- side_corridor=1.5) oldugu icin
        # ego ile ortusmez; kendi seridimizdeki engel kacis yolunu kapali
        # gostermez (slalom tetiklenebilir).
        band = np.abs(y) <= self.corridor
        if self.near_field_guard:
            # x_min kendi govdesini reddetmek icin var, ama eskiden x_min'in
            # icine giren engel TAMAMEN kayboluyor ve front 99'a (=temiz)
            # zipliyordu: tam en tehlikeli anda fail-open. Simdi tampon ile
            # x_min arasinda yeterli nokta varsa "cok yakin" = 0 raporlanir.
            near = int(np.count_nonzero(
                band & (x > self.bumper_offset) & (x <= self.x_min)))
            if near >= self.min_points:
                self.get_logger().warn(
                    f"Yakin alanda ({self.bumper_offset:.2f}-{self.x_min:.2f} m) "
                    f"{near} nokta -> front=0. Surekli goruyorsan aracin kendi "
                    "govdesi olabilir: x_min'i buyut ya da near_field_guard=false",
                    throttle_duration_sec=2.0)
                return BLOCKED
        return self._robust_distance(
            x[band & (x > self.x_min) & (x < self.max_range)])

    def _side_clearance(self, x, y, y_center):
        """Kacis koridorunda boylamsal klerans — front ile AYNI birim.
        Yan koridor yari genisligi = side_corridor (komsu seridin tamami),
        front'un corridor'undan (0.70) BAGIMSIZ. Eski "min(|y|)" tanimi
        corridor'dan kucuk deger uretemiyordu."""
        m = ((np.abs(y - y_center) < self.side_corridor)
             & (x > self.side_x_min) & (x < self.max_range))
        return self._robust_distance(x[m])

    def _filtered(self, key):
        """Son `filter_window` karenin en kucuk `confirm_frames`. degeri.
        Asimetrik: 1 karelik yakin gurultu elenir (k=2 -> 2 kare onay ~0.2 s),
        ama engelin kaybolmasi pencerenin cogunlugunu gerektirir."""
        h = self._hist[key]
        if not h:
            return None
        k = min(self.confirm_frames, len(h)) - 1
        return float(np.partition(np.asarray(h, dtype=np.float64), k)[k])

    # ------------------------------------------------------------------
    # Yayin
    # ------------------------------------------------------------------
    def _is_stale(self):
        if self._last_cloud_t is None:
            return True
        dt = (self.get_clock().now() - self._last_cloud_t).nanoseconds * 1e-9
        return dt > self.lidar_timeout

    def publish_master(self):
        if self._is_stale():
            # FAIL-SAFE: veri yokken bayat degerleri (cogunlukla 99,99,99)
            # yaymak beyne "yol temiz" der ve arac lidarsiz devam eder.
            first = self._last_cloud_t is None
            for h in self._hist.values():
                h.clear()
            front = left = right = BLOCKED
            if first:
                self.get_logger().warn(
                    f"{self.lidar_topic} uzerinden HIC bulut gelmedi -> "
                    "fail-safe (0,0,0)", throttle_duration_sec=5.0)
            else:
                self.get_logger().error(
                    f"LIDAR SUSTU (> {self.lidar_timeout:.1f} s) -> "
                    "fail-safe (0,0,0)", throttle_duration_sec=2.0)
        else:
            front = self._filtered("front")
            left = self._filtered("left")
            right = self._filtered("right")
            if front is None or left is None or right is None:
                front = left = right = BLOCKED

        msg = String()
        msg.data = f"4,{front:.2f},{left:.2f},{right:.2f}"
        self.pub.publish(msg)
        # Aracta tek gorunurluk `ros2 topic echo /master` idi ve orasi
        # lane/tabela trafigiyle karisik akiyor.
        self.get_logger().info(
            f"ID4 front={front:.2f} left={left:.2f} right={right:.2f}",
            throttle_duration_sec=self.log_period)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleLidarNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():  # Ctrl+C zaten kapatmis olabilir
            rclpy.shutdown()


if __name__ == "__main__":
    main()
