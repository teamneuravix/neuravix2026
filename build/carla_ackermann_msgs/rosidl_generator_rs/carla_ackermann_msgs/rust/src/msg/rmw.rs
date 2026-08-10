#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "carla_ackermann_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_ackermann_msgs__msg__EgoVehicleControlInfo() -> *const std::ffi::c_void;
}

#[link(name = "carla_ackermann_msgs__rosidl_generator_c")]
extern "C" {
    fn carla_ackermann_msgs__msg__EgoVehicleControlInfo__init(msg: *mut EgoVehicleControlInfo) -> bool;
    fn carla_ackermann_msgs__msg__EgoVehicleControlInfo__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlInfo>, size: usize) -> bool;
    fn carla_ackermann_msgs__msg__EgoVehicleControlInfo__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlInfo>);
    fn carla_ackermann_msgs__msg__EgoVehicleControlInfo__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<EgoVehicleControlInfo>, out_seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlInfo>) -> bool;
}

// Corresponds to carla_ackermann_msgs__msg__EgoVehicleControlInfo
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Copyright (c) 2018-2019 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.
///
/// This represents an info message of the ego vehicle

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EgoVehicleControlInfo {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// the restrictions
    pub restrictions: super::super::msg::rmw::EgoVehicleControlMaxima,

    /// the target values
    pub target: super::super::msg::rmw::EgoVehicleControlTarget,

    /// the currently measured values
    pub current: super::super::msg::rmw::EgoVehicleControlCurrent,

    /// the current control status
    pub status: super::super::msg::rmw::EgoVehicleControlStatus,

    /// the current control output to CARLA
    pub output: carla_msgs::msg::rmw::CarlaEgoVehicleControl,

}



impl Default for EgoVehicleControlInfo {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_ackermann_msgs__msg__EgoVehicleControlInfo__init(&mut msg as *mut _) {
        panic!("Call to carla_ackermann_msgs__msg__EgoVehicleControlInfo__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for EgoVehicleControlInfo {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlInfo__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlInfo__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlInfo__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for EgoVehicleControlInfo {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for EgoVehicleControlInfo where Self: Sized {
  const TYPE_NAME: &'static str = "carla_ackermann_msgs/msg/EgoVehicleControlInfo";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_ackermann_msgs__msg__EgoVehicleControlInfo() }
  }
}


#[link(name = "carla_ackermann_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_ackermann_msgs__msg__EgoVehicleControlCurrent() -> *const std::ffi::c_void;
}

#[link(name = "carla_ackermann_msgs__rosidl_generator_c")]
extern "C" {
    fn carla_ackermann_msgs__msg__EgoVehicleControlCurrent__init(msg: *mut EgoVehicleControlCurrent) -> bool;
    fn carla_ackermann_msgs__msg__EgoVehicleControlCurrent__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlCurrent>, size: usize) -> bool;
    fn carla_ackermann_msgs__msg__EgoVehicleControlCurrent__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlCurrent>);
    fn carla_ackermann_msgs__msg__EgoVehicleControlCurrent__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<EgoVehicleControlCurrent>, out_seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlCurrent>) -> bool;
}

// Corresponds to carla_ackermann_msgs__msg__EgoVehicleControlCurrent
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Copyright (c) 2018-2019 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.
///
/// This represents the current time/speed/accel values of the vehicle used by the controller

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EgoVehicleControlCurrent {

    // This member is not documented.
    #[allow(missing_docs)]
    pub time_sec: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub speed: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub speed_abs: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub accel: f32,

}



impl Default for EgoVehicleControlCurrent {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_ackermann_msgs__msg__EgoVehicleControlCurrent__init(&mut msg as *mut _) {
        panic!("Call to carla_ackermann_msgs__msg__EgoVehicleControlCurrent__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for EgoVehicleControlCurrent {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlCurrent__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlCurrent__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlCurrent__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for EgoVehicleControlCurrent {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for EgoVehicleControlCurrent where Self: Sized {
  const TYPE_NAME: &'static str = "carla_ackermann_msgs/msg/EgoVehicleControlCurrent";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_ackermann_msgs__msg__EgoVehicleControlCurrent() }
  }
}


#[link(name = "carla_ackermann_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_ackermann_msgs__msg__EgoVehicleControlMaxima() -> *const std::ffi::c_void;
}

#[link(name = "carla_ackermann_msgs__rosidl_generator_c")]
extern "C" {
    fn carla_ackermann_msgs__msg__EgoVehicleControlMaxima__init(msg: *mut EgoVehicleControlMaxima) -> bool;
    fn carla_ackermann_msgs__msg__EgoVehicleControlMaxima__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlMaxima>, size: usize) -> bool;
    fn carla_ackermann_msgs__msg__EgoVehicleControlMaxima__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlMaxima>);
    fn carla_ackermann_msgs__msg__EgoVehicleControlMaxima__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<EgoVehicleControlMaxima>, out_seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlMaxima>) -> bool;
}

// Corresponds to carla_ackermann_msgs__msg__EgoVehicleControlMaxima
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Copyright (c) 2018-2019 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.
///
/// This represents some ego vehicle control maximal values

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EgoVehicleControlMaxima {
    /// vehicle maximum values
    pub max_steering_angle: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub max_speed: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub max_accel: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub max_decel: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub min_accel: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub max_pedal: f32,

}



impl Default for EgoVehicleControlMaxima {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_ackermann_msgs__msg__EgoVehicleControlMaxima__init(&mut msg as *mut _) {
        panic!("Call to carla_ackermann_msgs__msg__EgoVehicleControlMaxima__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for EgoVehicleControlMaxima {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlMaxima__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlMaxima__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlMaxima__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for EgoVehicleControlMaxima {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for EgoVehicleControlMaxima where Self: Sized {
  const TYPE_NAME: &'static str = "carla_ackermann_msgs/msg/EgoVehicleControlMaxima";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_ackermann_msgs__msg__EgoVehicleControlMaxima() }
  }
}


#[link(name = "carla_ackermann_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_ackermann_msgs__msg__EgoVehicleControlStatus() -> *const std::ffi::c_void;
}

#[link(name = "carla_ackermann_msgs__rosidl_generator_c")]
extern "C" {
    fn carla_ackermann_msgs__msg__EgoVehicleControlStatus__init(msg: *mut EgoVehicleControlStatus) -> bool;
    fn carla_ackermann_msgs__msg__EgoVehicleControlStatus__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlStatus>, size: usize) -> bool;
    fn carla_ackermann_msgs__msg__EgoVehicleControlStatus__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlStatus>);
    fn carla_ackermann_msgs__msg__EgoVehicleControlStatus__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<EgoVehicleControlStatus>, out_seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlStatus>) -> bool;
}

// Corresponds to carla_ackermann_msgs__msg__EgoVehicleControlStatus
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Copyright (c) 2018-2019 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.
///
/// This represents the control status variables of the ego vehicle control

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EgoVehicleControlStatus {
    /// the current control status
    pub status: rosidl_runtime_rs::String,

    /// speed controller
    pub speed_control_activation_count: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub speed_control_accel_delta: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub speed_control_accel_target: f32,

    /// acceleration controller
    pub accel_control_pedal_delta: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub accel_control_pedal_target: f32,

    /// borders for lay off pedal
    pub brake_upper_border: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub throttle_lower_border: f32,

}



impl Default for EgoVehicleControlStatus {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_ackermann_msgs__msg__EgoVehicleControlStatus__init(&mut msg as *mut _) {
        panic!("Call to carla_ackermann_msgs__msg__EgoVehicleControlStatus__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for EgoVehicleControlStatus {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlStatus__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlStatus__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlStatus__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for EgoVehicleControlStatus {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for EgoVehicleControlStatus where Self: Sized {
  const TYPE_NAME: &'static str = "carla_ackermann_msgs/msg/EgoVehicleControlStatus";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_ackermann_msgs__msg__EgoVehicleControlStatus() }
  }
}


#[link(name = "carla_ackermann_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_ackermann_msgs__msg__EgoVehicleControlTarget() -> *const std::ffi::c_void;
}

#[link(name = "carla_ackermann_msgs__rosidl_generator_c")]
extern "C" {
    fn carla_ackermann_msgs__msg__EgoVehicleControlTarget__init(msg: *mut EgoVehicleControlTarget) -> bool;
    fn carla_ackermann_msgs__msg__EgoVehicleControlTarget__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlTarget>, size: usize) -> bool;
    fn carla_ackermann_msgs__msg__EgoVehicleControlTarget__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlTarget>);
    fn carla_ackermann_msgs__msg__EgoVehicleControlTarget__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<EgoVehicleControlTarget>, out_seq: *mut rosidl_runtime_rs::Sequence<EgoVehicleControlTarget>) -> bool;
}

// Corresponds to carla_ackermann_msgs__msg__EgoVehicleControlTarget
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Copyright (c) 2018-2019 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.
///
/// This represents the target speed/accel values of the ego vehicle

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EgoVehicleControlTarget {

    // This member is not documented.
    #[allow(missing_docs)]
    pub steering_angle: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub speed: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub speed_abs: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub accel: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub jerk: f32,

}



impl Default for EgoVehicleControlTarget {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_ackermann_msgs__msg__EgoVehicleControlTarget__init(&mut msg as *mut _) {
        panic!("Call to carla_ackermann_msgs__msg__EgoVehicleControlTarget__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for EgoVehicleControlTarget {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlTarget__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlTarget__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ackermann_msgs__msg__EgoVehicleControlTarget__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for EgoVehicleControlTarget {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for EgoVehicleControlTarget where Self: Sized {
  const TYPE_NAME: &'static str = "carla_ackermann_msgs/msg/EgoVehicleControlTarget";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_ackermann_msgs__msg__EgoVehicleControlTarget() }
  }
}


