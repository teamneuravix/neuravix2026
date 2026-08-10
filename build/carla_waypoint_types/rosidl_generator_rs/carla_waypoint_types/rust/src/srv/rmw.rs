#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



#[link(name = "carla_waypoint_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_waypoint_types__srv__GetWaypoint_Request() -> *const std::ffi::c_void;
}

#[link(name = "carla_waypoint_types__rosidl_generator_c")]
extern "C" {
    fn carla_waypoint_types__srv__GetWaypoint_Request__init(msg: *mut GetWaypoint_Request) -> bool;
    fn carla_waypoint_types__srv__GetWaypoint_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetWaypoint_Request>, size: usize) -> bool;
    fn carla_waypoint_types__srv__GetWaypoint_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetWaypoint_Request>);
    fn carla_waypoint_types__srv__GetWaypoint_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetWaypoint_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<GetWaypoint_Request>) -> bool;
}

// Corresponds to carla_waypoint_types__srv__GetWaypoint_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetWaypoint_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub location: geometry_msgs::msg::rmw::Point,

}



impl Default for GetWaypoint_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_waypoint_types__srv__GetWaypoint_Request__init(&mut msg as *mut _) {
        panic!("Call to carla_waypoint_types__srv__GetWaypoint_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetWaypoint_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetWaypoint_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetWaypoint_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetWaypoint_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetWaypoint_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetWaypoint_Request where Self: Sized {
  const TYPE_NAME: &'static str = "carla_waypoint_types/srv/GetWaypoint_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_waypoint_types__srv__GetWaypoint_Request() }
  }
}


#[link(name = "carla_waypoint_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_waypoint_types__srv__GetWaypoint_Response() -> *const std::ffi::c_void;
}

#[link(name = "carla_waypoint_types__rosidl_generator_c")]
extern "C" {
    fn carla_waypoint_types__srv__GetWaypoint_Response__init(msg: *mut GetWaypoint_Response) -> bool;
    fn carla_waypoint_types__srv__GetWaypoint_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetWaypoint_Response>, size: usize) -> bool;
    fn carla_waypoint_types__srv__GetWaypoint_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetWaypoint_Response>);
    fn carla_waypoint_types__srv__GetWaypoint_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetWaypoint_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<GetWaypoint_Response>) -> bool;
}

// Corresponds to carla_waypoint_types__srv__GetWaypoint_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetWaypoint_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub waypoint: super::super::msg::rmw::CarlaWaypoint,

}



impl Default for GetWaypoint_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_waypoint_types__srv__GetWaypoint_Response__init(&mut msg as *mut _) {
        panic!("Call to carla_waypoint_types__srv__GetWaypoint_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetWaypoint_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetWaypoint_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetWaypoint_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetWaypoint_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetWaypoint_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetWaypoint_Response where Self: Sized {
  const TYPE_NAME: &'static str = "carla_waypoint_types/srv/GetWaypoint_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_waypoint_types__srv__GetWaypoint_Response() }
  }
}


#[link(name = "carla_waypoint_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_waypoint_types__srv__GetActorWaypoint_Request() -> *const std::ffi::c_void;
}

#[link(name = "carla_waypoint_types__rosidl_generator_c")]
extern "C" {
    fn carla_waypoint_types__srv__GetActorWaypoint_Request__init(msg: *mut GetActorWaypoint_Request) -> bool;
    fn carla_waypoint_types__srv__GetActorWaypoint_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetActorWaypoint_Request>, size: usize) -> bool;
    fn carla_waypoint_types__srv__GetActorWaypoint_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetActorWaypoint_Request>);
    fn carla_waypoint_types__srv__GetActorWaypoint_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetActorWaypoint_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<GetActorWaypoint_Request>) -> bool;
}

// Corresponds to carla_waypoint_types__srv__GetActorWaypoint_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetActorWaypoint_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub id: u32,

}



impl Default for GetActorWaypoint_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_waypoint_types__srv__GetActorWaypoint_Request__init(&mut msg as *mut _) {
        panic!("Call to carla_waypoint_types__srv__GetActorWaypoint_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetActorWaypoint_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetActorWaypoint_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetActorWaypoint_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetActorWaypoint_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetActorWaypoint_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetActorWaypoint_Request where Self: Sized {
  const TYPE_NAME: &'static str = "carla_waypoint_types/srv/GetActorWaypoint_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_waypoint_types__srv__GetActorWaypoint_Request() }
  }
}


#[link(name = "carla_waypoint_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__carla_waypoint_types__srv__GetActorWaypoint_Response() -> *const std::ffi::c_void;
}

#[link(name = "carla_waypoint_types__rosidl_generator_c")]
extern "C" {
    fn carla_waypoint_types__srv__GetActorWaypoint_Response__init(msg: *mut GetActorWaypoint_Response) -> bool;
    fn carla_waypoint_types__srv__GetActorWaypoint_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetActorWaypoint_Response>, size: usize) -> bool;
    fn carla_waypoint_types__srv__GetActorWaypoint_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetActorWaypoint_Response>);
    fn carla_waypoint_types__srv__GetActorWaypoint_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetActorWaypoint_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<GetActorWaypoint_Response>) -> bool;
}

// Corresponds to carla_waypoint_types__srv__GetActorWaypoint_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetActorWaypoint_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub waypoint: super::super::msg::rmw::CarlaWaypoint,

}



impl Default for GetActorWaypoint_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !carla_waypoint_types__srv__GetActorWaypoint_Response__init(&mut msg as *mut _) {
        panic!("Call to carla_waypoint_types__srv__GetActorWaypoint_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetActorWaypoint_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetActorWaypoint_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetActorWaypoint_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { carla_waypoint_types__srv__GetActorWaypoint_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetActorWaypoint_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetActorWaypoint_Response where Self: Sized {
  const TYPE_NAME: &'static str = "carla_waypoint_types/srv/GetActorWaypoint_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__carla_waypoint_types__srv__GetActorWaypoint_Response() }
  }
}






#[link(name = "carla_waypoint_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__carla_waypoint_types__srv__GetWaypoint() -> *const std::ffi::c_void;
}

// Corresponds to carla_waypoint_types__srv__GetWaypoint
#[allow(missing_docs, non_camel_case_types)]
pub struct GetWaypoint;

impl rosidl_runtime_rs::Service for GetWaypoint {
    type Request = GetWaypoint_Request;
    type Response = GetWaypoint_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__carla_waypoint_types__srv__GetWaypoint() }
    }
}




#[link(name = "carla_waypoint_types__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__carla_waypoint_types__srv__GetActorWaypoint() -> *const std::ffi::c_void;
}

// Corresponds to carla_waypoint_types__srv__GetActorWaypoint
#[allow(missing_docs, non_camel_case_types)]
pub struct GetActorWaypoint;

impl rosidl_runtime_rs::Service for GetActorWaypoint {
    type Request = GetActorWaypoint_Request;
    type Response = GetActorWaypoint_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__carla_waypoint_types__srv__GetActorWaypoint() }
    }
}


