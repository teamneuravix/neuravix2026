#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



#[link(name = "carla_ros_scenario_runner_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_ros_scenario_runner_types__srv__ExecuteScenario_Request() -> *const std::ffi::c_void;
}

#[link(name = "carla_ros_scenario_runner_types__rosidl_generator_c")]
extern "C" {
    fn carla_ros_scenario_runner_types__srv__ExecuteScenario_Request__init(msg: *mut ExecuteScenario_Request) -> bool;
    fn carla_ros_scenario_runner_types__srv__ExecuteScenario_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ExecuteScenario_Request>, size: usize) -> bool;
    fn carla_ros_scenario_runner_types__srv__ExecuteScenario_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ExecuteScenario_Request>);
    fn carla_ros_scenario_runner_types__srv__ExecuteScenario_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ExecuteScenario_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<ExecuteScenario_Request>) -> bool;
}

// Corresponds to carla_ros_scenario_runner_types__srv__ExecuteScenario_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ExecuteScenario_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub scenario: super::super::msg::rmw::CarlaScenario,

}



impl Default for ExecuteScenario_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_ros_scenario_runner_types__srv__ExecuteScenario_Request__init(&mut msg as *mut _) {
        panic!("Call to carla_ros_scenario_runner_types__srv__ExecuteScenario_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ExecuteScenario_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__srv__ExecuteScenario_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__srv__ExecuteScenario_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__srv__ExecuteScenario_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ExecuteScenario_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ExecuteScenario_Request where Self: Sized {
  const TYPE_NAME: &'static str = "carla_ros_scenario_runner_types/srv/ExecuteScenario_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_ros_scenario_runner_types__srv__ExecuteScenario_Request() }
  }
}


#[link(name = "carla_ros_scenario_runner_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_ros_scenario_runner_types__srv__ExecuteScenario_Response() -> *const std::ffi::c_void;
}

#[link(name = "carla_ros_scenario_runner_types__rosidl_generator_c")]
extern "C" {
    fn carla_ros_scenario_runner_types__srv__ExecuteScenario_Response__init(msg: *mut ExecuteScenario_Response) -> bool;
    fn carla_ros_scenario_runner_types__srv__ExecuteScenario_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ExecuteScenario_Response>, size: usize) -> bool;
    fn carla_ros_scenario_runner_types__srv__ExecuteScenario_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ExecuteScenario_Response>);
    fn carla_ros_scenario_runner_types__srv__ExecuteScenario_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ExecuteScenario_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<ExecuteScenario_Response>) -> bool;
}

// Corresponds to carla_ros_scenario_runner_types__srv__ExecuteScenario_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ExecuteScenario_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub result: bool,

}



impl Default for ExecuteScenario_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_ros_scenario_runner_types__srv__ExecuteScenario_Response__init(&mut msg as *mut _) {
        panic!("Call to carla_ros_scenario_runner_types__srv__ExecuteScenario_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ExecuteScenario_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__srv__ExecuteScenario_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__srv__ExecuteScenario_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_ros_scenario_runner_types__srv__ExecuteScenario_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ExecuteScenario_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ExecuteScenario_Response where Self: Sized {
  const TYPE_NAME: &'static str = "carla_ros_scenario_runner_types/srv/ExecuteScenario_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_ros_scenario_runner_types__srv__ExecuteScenario_Response() }
  }
}






#[link(name = "carla_ros_scenario_runner_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__carla_ros_scenario_runner_types__srv__ExecuteScenario() -> *const std::ffi::c_void;
}

// Corresponds to carla_ros_scenario_runner_types__srv__ExecuteScenario
#[allow(missing_docs, non_camel_case_types)]
pub struct ExecuteScenario;

impl rosidl_runtime_rs::Service for ExecuteScenario {
    type Request = ExecuteScenario_Request;
    type Response = ExecuteScenario_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__carla_ros_scenario_runner_types__srv__ExecuteScenario() }
    }
}


