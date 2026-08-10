cmake_minimum_required(VERSION 3.3)
project(pcl_recorder)

# ROS Sürümünü Belirleme Mantığı
# Ortamdan oku, tırnak içine alarak boşluk hatalarını önle.
find_package(ros_environment REQUIRED)
set(ROS_VERSION "$ENV{ROS_VERSION}")

# Eğer $ROS_VERSION boşsa (colcon build/ament ortamı), varsayılanı 2 yap.
if("${ROS_VERSION}" STREQUAL "")
    set(ROS_VERSION 2)
endif()

# ROS 1 BLOKU (catkin)
if("${ROS_VERSION}" EQUAL 1)
  find_package(catkin REQUIRED COMPONENTS
    pcl_conversions
    pcl_ros
    roscpp
    sensor_msgs
    roslaunch
  )

  catkin_package()

  if(CATKIN_ENABLE_TESTING)
    roslaunch_add_file_check(launch DEPENDENCIES ${PROJECT_NAME}_node)
  endif()

  include_directories(
    include
    ${catkin_INCLUDE_DIRS}
  )

  add_executable(${PROJECT_NAME}_node
    src/PclRecorder.cpp
    src/main.cpp
  )

  target_link_libraries(${PROJECT_NAME}_node
    ${catkin_LIBRARIES}
  )

  # C++ Derleme Özellikleri
  target_compile_features(${PROJECT_NAME}_node PRIVATE
    cxx_inheriting_constructors
    cxx_lambdas
    cxx_auto_type
    cxx_variadic_templates
    cxx_variable_templates
  )

  install(TARGETS ${PROJECT_NAME}_node
    ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
    LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
    RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
  )

  install(DIRECTORY launch/
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
  )

# ROS 2 BLOKU (ament_cmake)

elseif("${ROS_VERSION}" EQUAL 2)

  # Default to C++14
  if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 14)
  endif()

  if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
  endif()

  find_package(ament_cmake REQUIRED)
  find_package(rclcpp REQUIRED)
  find_package(rclcpp_components REQUIRED)
  find_package(sensor_msgs REQUIRED)
  find_package(tf2 REQUIRED)
  find_package(tf2_eigen REQUIRED)
  find_package(tf2_geometry_msgs REQUIRED)
  find_package(tf2_ros REQUIRED)
  find_package(pcl_conversions REQUIRED)
  find_package(Boost REQUIRED COMPONENTS system)
  find_package(PCL REQUIRED COMPONENTS common io)

  add_executable(${PROJECT_NAME}_node
    src/PclRecorderROS2.cpp
    src/mainROS2.cpp
  )

  target_include_directories(${PROJECT_NAME}_node PUBLIC
    include
    ${PCL_INCLUDE_DIRS}
  )

  ament_target_dependencies(${PROJECT_NAME}_node
    rclcpp
    sensor_msgs
    pcl_conversions
    tf2
    tf2_ros
  )

  target_link_libraries(${PROJECT_NAME}_node
    ${Boost_SYSTEM_LIBRARY}
    ${PCL_LIBRARIES}
  )

  # C++ Derleme Özellikleri
  target_compile_features(${PROJECT_NAME}_node PRIVATE
    cxx_inheriting_constructors
    cxx_lambdas
    cxx_auto_type
    cxx_variadic_templates
    cxx_variable_templates
  )

  install(TARGETS ${PROJECT_NAME}_node
    DESTINATION lib/${PROJECT_NAME}
  )

  install(DIRECTORY launch/
    DESTINATION share/${PROJECT_NAME}/
  )

  ament_package()

endif()