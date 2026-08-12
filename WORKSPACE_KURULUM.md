# carla-ros2-ws — Kurulum Notları (slalom-ws dalı)

Bu dal, 2026-08-11 tarihli **slalom** çalışmasındaki tam ROS2 workspace'inin
kaynak kodunu içerir. Repo boyutunu makul tutmak için derleme çıktıları ve
büyük binary dosyalar **dışarıda bırakılmıştır**.

## Repoda OLMAYAN dosyalar

Bunlar `.gitignore` ile hariç tutuldu; klonladıktan sonra ayrıca edinmeniz gerekir.

| Ne | Nerede olması gerek | Boyut | Nasıl elde edilir |
|---|---|---|---|
| YOLO ağırlıkları (13 dosya) | `src/neuravix_ros2/models/` | ~187 MB | Ekip içi paylaşım (Drive / USB) |
| Pist SLAM haritası | `bee1_map.pcd` (workspace kökü) | ~134 MB | Ekip içi paylaşım, ya da FAST_LIO ile yeniden çıkarılır |
| FAST_LIO demo görselleri | `src/FAST_LIO/doc/` | ~128 MB | Gerekmiyor; isteyen upstream'den alır |
| `build/`, `install/`, `log/` | workspace kökü | ~165 MB | `colcon build` ile üretilir |

> **Dikkat:** `models/tabela_tespit_node.py` adında 19 MB'lık bir dosya vardı —
> uzantısı `.py` ama içeriği bir YOLO ağırlığı (`.pt`). Ağırlıkları paylaşırken
> bu dosyayı da unutmayın; adı yanıltıcı.

## Kurulum

```bash
git clone -b slalom-ws https://github.com/teamneuravix/neuravix2026.git carla-ros2-ws
cd carla-ros2-ws

# 1) Ağırlıkları ve haritayı yerine koyun
#    - *.pt dosyaları  -> src/neuravix_ros2/models/
#    - bee1_map.pcd    -> ./ (workspace kökü)

# 2) Bağımlılıklar
pip install -r src/requirements.txt
rosdep install --from-paths src --ignore-src -r -y

# 3) Derleme
colcon build --symlink-install
source install/setup.bash
```

## Vendor paketleri

`src/` altındaki şu paketler upstream projelerin kopyalarıdır; kendi `.git`
dizinleri temizlenmiştir (aksi halde bozuk submodule olarak görünürlerdi):

- `FAST_LIO` — hku-mars/FAST_LIO
- `ros-bridge` — carla-simulator/ros-bridge
- `carla-msgs` — carla-simulator/ros-carla-msgs
- `livox_ros_driver2` — Livox-SDK/livox_ros_driver2
- `navigation_msgs` (workspace kökünde)

Yerel değişiklik içerebilirler; upstream'den yeniden klonlamayın.

## main dalıyla ilişkisi

`main` dalının kökündeki şu dosyalar bu dalda **silindi** — aynı kodun daha
güncel sürümleri workspace içindeki doğru paket yollarında duruyor:

| main'deki dosya | Bu daldaki yeri |
|---|---|
| `astar_planner.py`, `astar_planner_node.py`, `pointcloud_filter.py` | `src/bee1_description/scripts/` |
| `lane_follower_node.py`, `neuravix_control_node.py`, `obstacle_lidar_node.py`, `tabela_tespit_node.py` | `src/neuravix_ros2/neuravix_ros2/` |

`build_pist_map.py` yalnızca `main`'de bulunuyordu, korundu.
