# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target smart_can_msgs::smart_can_msgs
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${smart_can_msgs_TARGETS}.
if(smart_can_msgs_TARGETS AND NOT TARGET smart_can_msgs::smart_can_msgs)
  add_library(smart_can_msgs::smart_can_msgs INTERFACE IMPORTED)
  set_target_properties(smart_can_msgs::smart_can_msgs PROPERTIES
    INTERFACE_LINK_LIBRARIES "${smart_can_msgs_TARGETS}")
endif()
