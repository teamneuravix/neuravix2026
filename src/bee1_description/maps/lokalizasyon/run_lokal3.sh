#!/usr/bin/env bash
#   ./run_lokal3.sh TAG BAG ESIK BAG_ODOM(0/1)
#   ornek: WS=~/Desktop/carla-ros2-ws BAG_DIR=~/maps_son \
#          ./run_lokal3.sh TEST lokal_0820_0722 3.0 0
set -eo pipefail
TAG="$1"; BAGN="$2"; ESIK="${3:-4.5}"; BODOM="${4:-0}"
WS="${WS:-$HOME/Desktop/carla-ros2-ws}"
MAP="${MAP:-$(cd "$(dirname "$0")/.." && pwd)/pist_final.yaml}"
BAG="${BAG_DIR:-$HOME/Downloads/harita_bags}/$BAGN"
OUT="${OUT:-/tmp/loc}"
source /opt/ros/humble/setup.bash; source "$WS/install/setup.bash"
export ROS_DOMAIN_ID=11; mkdir -p "$OUT"
# Onceki kosudan artan surec varsa dur -- iki AMCL ayni anda kosarsa sonuc coper
LEFT=$(pgrep -af "can_odom|nav2_amcl|ros2 bag play|pose_logger" 2>/dev/null \
        | awk '{print $1}' | tr '\n' ' ' || true)
# NOT (bizde duzeltildi): asagidaki satir yazarin surumunde
#   [ -n "$LEFT" ] && { ...; exit 1; }
# seklindeydi; `set -e` altinda LEFT BOSKEN de (yani hicbir artik surec yokken)
# test 1 dondurup script'i sessizce oldurüyordu -- hic log uretmeden.
if [ -n "$LEFT" ]; then echo "!! calisan kosu var, once onlari kapat: $LEFT"; exit 1; fi
if [ "$BODOM" = "1" ]; then WHEEL=true; TOPICS_EK="/odometry/can_wheel"; else WHEEL=false; TOPICS_EK=""; fi
echo "== $TAG | $BAGN | esik $ESIK | use_wheel_odom=$WHEEL"
PIDS=(); cleanup(){ for p in "${PIDS[@]}"; do kill -TERM -"$p" 2>/dev/null; done; sleep 2
                    for p in "${PIDS[@]}"; do kill -9 -"$p" 2>/dev/null; done; }
trap cleanup EXIT INT TERM
setsid ros2 launch bee1_description bee1_bringup.launch.py use_sim_time:=true \
  > "$OUT/${TAG}_bringup.log" 2>&1 &
PIDS+=($!); sleep 6
setsid ros2 launch bee1_description pist_localization_amcl.launch.py \
  use_sim_time:=true map_yaml:="$MAP" use_ekf:=false use_wheel_odom:=$WHEEL \
  use_imu_yaw:=true imu_topic:=/imu/data lidar_topic:=/velodyne_points \
  use_gnss:=true gnss_topic:=/gnss gnss_enabled:=true gnss_threshold:=$ESIK \
  initial_pose_x:=${IPX:-20.51} initial_pose_y:=${IPY:-3.89} initial_pose_yaw:=${IPYAW:-0.1749} \
  datum_lat:=40.79041010 datum_lon:=29.50912636 datum_yaw_deg:=-149.20 \
  use_yer_tanima:=false > "$OUT/${TAG}_loc.log" 2>&1 &
PIDS+=($!); sleep 18
grep -q "Managed nodes are active" "$OUT/${TAG}_loc.log" && echo "-- amcl AKTIF --" \
  || { echo "!! aktiflesmedi"; exit 1; }
setsid python3 "$(dirname "$0")/pose_logger.py" "$OUT/${TAG}_poz.csv" \
  --ros-args -p use_sim_time:=true > "$OUT/${TAG}_poz.log" 2>&1 &
PIDS+=($!); sleep 2
( sleep 20; ros2 lifecycle set /map_server deactivate >/dev/null 2>&1; sleep 1
  ros2 lifecycle set /map_server activate >/dev/null 2>&1 ) &
ros2 bag play "$BAG" --clock 100 --rate 1.0 --disable-keyboard-controls \
  --topics /velodyne_points /imu/data /gnss $TOPICS_EK \
           /beemobs/FB_VehicleSpeed /beemobs/FeedbackSteeringAngle /beemobs/FB_MotorDriver \
  > "$OUT/${TAG}_bag.log" 2>&1
sleep 3; echo -n "  tohumlama: "; grep -c "YENIDEN TOHUMLAMA" "$OUT/${TAG}_loc.log" || true
exit 0
