#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "carla_waypoint_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_waypoint_types__msg__CarlaWaypoint() -> *const std::ffi::c_void;
}

#[link(name = "carla_waypoint_types__rosidl_generator_c")]
extern "C" {
    fn carla_waypoint_types__msg__CarlaWaypoint__init(msg: *mut CarlaWaypoint) -> bool;
    fn carla_waypoint_types__msg__CarlaWaypoint__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CarlaWaypoint>, size: usize) -> bool;
    fn carla_waypoint_types__msg__CarlaWaypoint__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CarlaWaypoint>);
    fn carla_waypoint_types__msg__CarlaWaypoint__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CarlaWaypoint>, out_seq: *mut rosidl_runtime_rs::Sequence<CarlaWaypoint>) -> bool;
}

// Corresponds to carla_waypoint_types__msg__CarlaWaypoint
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Copyright (c) 2020 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CarlaWaypoint {

    // This member is not documented.
    #[allow(missing_docs)]
    pub road_id: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub section_id: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lane_id: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub is_junction: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pose: geometry_msgs::msg::rmw::Pose,

}



impl Default for CarlaWaypoint {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_waypoint_types__msg__CarlaWaypoint__init(&mut msg as *mut _) {
        panic!("Call to carla_waypoint_types__msg__CarlaWaypoint__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CarlaWaypoint {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__msg__CarlaWaypoint__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__msg__CarlaWaypoint__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__msg__CarlaWaypoint__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CarlaWaypoint {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CarlaWaypoint where Self: Sized {
  const TYPE_NAME: &'static str = "carla_waypoint_types/msg/CarlaWaypoint";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_waypoint_types__msg__CarlaWaypoint() }
  }
}


