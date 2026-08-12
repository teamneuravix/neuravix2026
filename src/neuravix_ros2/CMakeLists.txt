cmake_minimum_required(VERSION 3.8)
project(neuravix_ros2)

find_package(ament_cmake REQUIRED)

# PYTHON BAĞIMLILIKLARI ROS YOLUNA EKLENMELİDİR
#[[
find_package(Python3 REQUIRED COMPONENTS Interpreter)
Python3_find_package(numpy REQUIRED)
Python3_find_package(ultralytics REQUIRED) # Bu satır, ultralytics'i bulamazsa hata verebilir.

# 1. PYTHON DÜĞÜMÜNÜ ROS 2'DE ÇALIŞTIRILABİLİR OLARAK KURMA
# Bu yöntem, setup.py sorununu bypass eder ve çalıştırılabilir dosyanın oluşturulmasını garanti eder.
# Çalıştırılabilir dosya: lane_follower
install(PROGRAMS
  # neuravix_ros2 içindeki lane_follower_node.py dosyasını kullan
  neuravix_ros2/lane_follower_node.py
  # Çalıştırılabilir adı olarak 'lane_follower' kullan
  DESTINATION lib/${PROJECT_NAME}
)

# 2. MODEL DOSYALARINI KURMA
install(DIRECTORY models/
  DESTINATION share/${PROJECT_NAME}
)
#]]

# 3. BAĞIMLILIKLARI EXPORT ETME
ament_export_dependencies(
  rclpy
  std_msgs
  sensor_msgs
  cv_bridge
)

# 4. PAKET METADATALARINI KURMA
ament_package()
