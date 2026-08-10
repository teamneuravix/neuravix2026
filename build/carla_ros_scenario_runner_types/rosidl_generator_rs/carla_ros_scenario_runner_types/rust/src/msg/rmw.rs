#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "carla_ros_scenario_runner_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_ros_scenario_runner_types__msg__CarlaScenario() -> *const std::ffi::c_void;
}

#[link(name = "carla_ros_scenario_runner_types__rosidl_generator_c")]
extern "C" {
    fn carla_ros_scenario_runner_types__msg__CarlaScenario__init(msg: *mut CarlaScenario) -> bool;
    fn carla_ros_scenario_runner_types__msg__CarlaScenario__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CarlaScenario>, size: usize) -> bool;
    fn carla_ros_scenario_runner_types__msg__CarlaScenario__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CarlaScenario>);
    fn carla_ros_scenario_runner_types__msg__CarlaScenario__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CarlaScenario>, out_seq: *mut rosidl_runtime_rs::Sequence<CarlaScenario>) -> bool;
}

// Corresponds to carla_ros_scenario_runner_types__msg__CarlaScenario
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Copyright (c) 2020 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CarlaScenario {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub scenario_file: rosidl_runtime_rs::String,

}



impl Default for CarlaScenario {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_ros_scenario_runner_types__msg__CarlaScenario__init(&mut msg as *mut _) {
        panic!("Call to carla_ros_scenario_runner_types__msg__CarlaScenario__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CarlaScenario {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__msg__CarlaScenario__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__msg__CarlaScenario__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__msg__CarlaScenario__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CarlaScenario {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CarlaScenario where Self: Sized {
  const TYPE_NAME: &'static str = "carla_ros_scenario_runner_types/msg/CarlaScenario";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_ros_scenario_runner_types__msg__CarlaScenario() }
  }
}


#[link(name = "carla_ros_scenario_runner_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_ros_scenario_runner_types__msg__CarlaScenarioList() -> *const std::ffi::c_void;
}

#[link(name = "carla_ros_scenario_runner_types__rosidl_generator_c")]
extern "C" {
    fn carla_ros_scenario_runner_types__msg__CarlaScenarioList__init(msg: *mut CarlaScenarioList) -> bool;
    fn carla_ros_scenario_runner_types__msg__CarlaScenarioList__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CarlaScenarioList>, size: usize) -> bool;
    fn carla_ros_scenario_runner_types__msg__CarlaScenarioList__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CarlaScenarioList>);
    fn carla_ros_scenario_runner_types__msg__CarlaScenarioList__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CarlaScenarioList>, out_seq: *mut rosidl_runtime_rs::Sequence<CarlaScenarioList>) -> bool;
}

// Corresponds to carla_ros_scenario_runner_types__msg__CarlaScenarioList
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Copyright (c) 2020 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CarlaScenarioList {

    // This member is not documented.
    #[allow(missing_docs)]
    pub scenarios: rosidl_runtime_rs::Sequence<super::super::msg::rmw::CarlaScenario>,

}



impl Default for CarlaScenarioList {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_ros_scenario_runner_types__msg__CarlaScenarioList__init(&mut msg as *mut _) {
        panic!("Call to carla_ros_scenario_runner_types__msg__CarlaScenarioList__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CarlaScenarioList {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__msg__CarlaScenarioList__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__msg__CarlaScenarioList__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__msg__CarlaScenarioList__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CarlaScenarioList {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CarlaScenarioList where Self: Sized {
  const TYPE_NAME: &'static str = "carla_ros_scenario_runner_types/msg/CarlaScenarioList";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_ros_scenario_runner_types__msg__CarlaScenarioList() }
  }
}


#[link(name = "carla_ros_scenario_runner_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus() -> *const std::ffi::c_void;
}

#[link(name = "carla_ros_scenario_runner_types__rosidl_generator_c")]
extern "C" {
    fn carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus__init(msg: *mut CarlaScenarioRunnerStatus) -> bool;
    fn carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CarlaScenarioRunnerStatus>, size: usize) -> bool;
    fn carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CarlaScenarioRunnerStatus>);
    fn carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CarlaScenarioRunnerStatus>, out_seq: *mut rosidl_runtime_rs::Sequence<CarlaScenarioRunnerStatus>) -> bool;
}

// Corresponds to carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Copyright (c) 2020 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CarlaScenarioRunnerStatus {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: u8,

}

impl CarlaScenarioRunnerStatus {

    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STOPPED: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STARTING: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const RUNNING: u8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const SHUTTINGDOWN: u8 = 3;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const ERROR: u8 = 4;

}


impl Default for CarlaScenarioRunnerStatus {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus__init(&mut msg as *mut _) {
        panic!("Call to carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CarlaScenarioRunnerStatus {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CarlaScenarioRunnerStatus {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CarlaScenarioRunnerStatus where Self: Sized {
  const TYPE_NAME: &'static str = "carla_ros_scenario_runner_types/msg/CarlaScenarioRunnerStatus";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus() }
  }
}


