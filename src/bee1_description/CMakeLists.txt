cmake_minimum_required(VERSION 3.8)
project(bee1_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf launch config
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/pointcloud_filter.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME pointcloud_filter
)
install(
  PROGRAMS scripts/odom_relay.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME odom_relay
)
install(
  PROGRAMS scripts/gps_relay.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME gps_relay
)
install(
  PROGRAMS scripts/pist_odom_tf.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME pist_odom_tf
)

# A* cekirdek kutuphane: IMPORT edilen modul -> .py uzantisi KALMALI
install(
  PROGRAMS scripts/astar_planner.py
  DESTINATION lib/${PROJECT_NAME}
)

# A* planner node: calistirilabilir -> launch 'astar_planner_node' adiyla arar
install(
  PROGRAMS scripts/astar_planner_node.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME astar_planner_node
)

# LiDAR nokta verisini terminale basan debug dugumu
# 'ros2 run bee1_description lidar_echo' ile calisir
install(
  PROGRAMS scripts/lidar_echo_node.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME lidar_echo
)

# GERCEK ARAC (TASLAK): CAN hiz+direksiyon feedback'inden bisiklet modeliyle
# odom -> base_link uretir (pist_odom_tf.py'nin gercek-arac esdegeri).
# 'ros2 run bee1_description can_odom' ile calisir
install(
  PROGRAMS scripts/can_odom_node.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME can_odom
)

# GERCEK ARAC: /beemobs/FB_VehicleSpeed -> /beemobs/fbvehiclespeed isim koprusu.
# Arac speed_pid_node feedback'i fbvehiclespeed'den bekliyor, CAN koprusu
# FB_VehicleSpeed yayinliyor; PID feedback alsin diye (arac config'ine
# dokunmadan). 'ros2 run bee1_description speed_fb_relay' ile calisir.
install(
  PROGRAMS scripts/speed_fb_relay.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME speed_fb_relay
)

# GERCEK ARAC: /beemobs/rcthrtdata -> /beemobs/RC_THRT_DATA isim koprusu.
# speed_pid_node gazi rcthrtdata'ya basar, can_handler RC_THRT_DATA bekler
# (2026-07-18 aracta dogrulandi). speed_fb_relay'in cikis-tarafi ikizi.
# 'ros2 run bee1_description throttle_relay' ile calisir.
install(
  PROGRAMS scripts/throttle_relay.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME throttle_relay
)

# GERCEK ARAC: aracin BOZUK PID'lerinin yerine gecen kendi kontrolcularimiz.
# steering PID tek yonlu (min_output=0 -> pwm=0 -> motor kapali), speed PID
# anti-windup'siz (pedali 255'e sisiriyor). Ikisi de 2026-07-20 bag'leriyle
# kanitlandi; semantik olculdu (pwm merkez 127, pedal olu bolge 47).
install(
  PROGRAMS scripts/steering_ctrl.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME steering_ctrl
)
install(
  PROGRAMS scripts/throttle_ctrl.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME throttle_ctrl
)

ament_package()
