#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Dis() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Dis__init(msg: *mut Dis) -> bool;
    fn smart_can_msgs__msg__Dis__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Dis>, size: usize) -> bool;
    fn smart_can_msgs__msg__Dis__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Dis>);
    fn smart_can_msgs__msg__Dis__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Dis>, out_seq: *mut rosidl_runtime_rs::Sequence<Dis>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Dis
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Dis {

    // This member is not documented.
    #[allow(missing_docs)]
    pub angle: f32,

}



impl Default for Dis {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Dis__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Dis__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Dis {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Dis__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Dis__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Dis__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Dis {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Dis where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Dis";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Dis() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Kinematicmessages() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Kinematicmessages__init(msg: *mut Kinematicmessages) -> bool;
    fn smart_can_msgs__msg__Kinematicmessages__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Kinematicmessages>, size: usize) -> bool;
    fn smart_can_msgs__msg__Kinematicmessages__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Kinematicmessages>);
    fn smart_can_msgs__msg__Kinematicmessages__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Kinematicmessages>, out_seq: *mut rosidl_runtime_rs::Sequence<Kinematicmessages>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Kinematicmessages
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Kinematicmessages {

    // This member is not documented.
    #[allow(missing_docs)]
    pub joint_type: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub angle: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub angle_y: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub angular_velocity: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub link_length: f32,

}



impl Default for Kinematicmessages {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Kinematicmessages__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Kinematicmessages__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Kinematicmessages {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Kinematicmessages__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Kinematicmessages__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Kinematicmessages__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Kinematicmessages {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Kinematicmessages where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Kinematicmessages";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Kinematicmessages() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Rcunittoomux() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Rcunittoomux__init(msg: *mut Rcunittoomux) -> bool;
    fn smart_can_msgs__msg__Rcunittoomux__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Rcunittoomux>, size: usize) -> bool;
    fn smart_can_msgs__msg__Rcunittoomux__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Rcunittoomux>);
    fn smart_can_msgs__msg__Rcunittoomux__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Rcunittoomux>, out_seq: *mut rosidl_runtime_rs::Sequence<Rcunittoomux>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Rcunittoomux
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Rcunittoomux {

    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_emergency: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_windowresintance: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_interiorlight: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_reverselight: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_drl: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_brakelight: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_door_open: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_door_close: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_signalstatus: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_lowbeam: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_highbeam: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_selectiongear: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_ignition: u8,

}



impl Default for Rcunittoomux {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Rcunittoomux__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Rcunittoomux__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Rcunittoomux {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Rcunittoomux__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Rcunittoomux__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Rcunittoomux__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Rcunittoomux {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Rcunittoomux where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Rcunittoomux";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Rcunittoomux() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Rcthrtdata() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Rcthrtdata__init(msg: *mut Rcthrtdata) -> bool;
    fn smart_can_msgs__msg__Rcthrtdata__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Rcthrtdata>, size: usize) -> bool;
    fn smart_can_msgs__msg__Rcthrtdata__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Rcthrtdata>);
    fn smart_can_msgs__msg__Rcthrtdata__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Rcthrtdata>, out_seq: *mut rosidl_runtime_rs::Sequence<Rcthrtdata>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Rcthrtdata
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Rcthrtdata {

    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_thrt_pedal_position: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_thrt_pedal_press: u8,

}



impl Default for Rcthrtdata {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Rcthrtdata__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Rcthrtdata__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Rcthrtdata {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Rcthrtdata__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Rcthrtdata__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Rcthrtdata__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Rcthrtdata {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Rcthrtdata where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Rcthrtdata";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Rcthrtdata() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Autonomousbrakepedalcontrol() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Autonomousbrakepedalcontrol__init(msg: *mut Autonomousbrakepedalcontrol) -> bool;
    fn smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Autonomousbrakepedalcontrol>, size: usize) -> bool;
    fn smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Autonomousbrakepedalcontrol>);
    fn smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Autonomousbrakepedalcontrol>, out_seq: *mut rosidl_runtime_rs::Sequence<Autonomousbrakepedalcontrol>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Autonomousbrakepedalcontrol
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Autonomousbrakepedalcontrol {

    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_brakemotor_voltage: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_brakepedalmotor_per: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_brakepedalmotor_acc: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_brakepedalmotor_en: u8,

}



impl Default for Autonomousbrakepedalcontrol {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Autonomousbrakepedalcontrol__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Autonomousbrakepedalcontrol__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Autonomousbrakepedalcontrol {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Autonomousbrakepedalcontrol {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Autonomousbrakepedalcontrol where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Autonomousbrakepedalcontrol";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Autonomousbrakepedalcontrol() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Autonomoussteeringmotcontrol() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Autonomoussteeringmotcontrol__init(msg: *mut Autonomoussteeringmotcontrol) -> bool;
    fn smart_can_msgs__msg__Autonomoussteeringmotcontrol__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Autonomoussteeringmotcontrol>, size: usize) -> bool;
    fn smart_can_msgs__msg__Autonomoussteeringmotcontrol__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Autonomoussteeringmotcontrol>);
    fn smart_can_msgs__msg__Autonomoussteeringmotcontrol__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Autonomoussteeringmotcontrol>, out_seq: *mut rosidl_runtime_rs::Sequence<Autonomoussteeringmotcontrol>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Autonomoussteeringmotcontrol
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Autonomoussteeringmotcontrol {

    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_steeringmot_en: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_steeringmot_pwm: u8,

}



impl Default for Autonomoussteeringmotcontrol {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Autonomoussteeringmotcontrol__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Autonomoussteeringmotcontrol__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Autonomoussteeringmotcontrol {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomoussteeringmotcontrol__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomoussteeringmotcontrol__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomoussteeringmotcontrol__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Autonomoussteeringmotcontrol {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Autonomoussteeringmotcontrol where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Autonomoussteeringmotcontrol";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Autonomoussteeringmotcontrol() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Autonomoushbmotorcontrol() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Autonomoushbmotorcontrol__init(msg: *mut Autonomoushbmotorcontrol) -> bool;
    fn smart_can_msgs__msg__Autonomoushbmotorcontrol__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Autonomoushbmotorcontrol>, size: usize) -> bool;
    fn smart_can_msgs__msg__Autonomoushbmotorcontrol__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Autonomoushbmotorcontrol>);
    fn smart_can_msgs__msg__Autonomoushbmotorcontrol__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Autonomoushbmotorcontrol>, out_seq: *mut rosidl_runtime_rs::Sequence<Autonomoushbmotorcontrol>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Autonomoushbmotorcontrol
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Autonomoushbmotorcontrol {

    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_hb_motor_pwm: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_hb_motstate: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomous_hb_moten: u8,

}



impl Default for Autonomoushbmotorcontrol {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Autonomoushbmotorcontrol__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Autonomoushbmotorcontrol__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Autonomoushbmotorcontrol {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomoushbmotorcontrol__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomoushbmotorcontrol__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomoushbmotorcontrol__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Autonomoushbmotorcontrol {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Autonomoushbmotorcontrol where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Autonomoushbmotorcontrol";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Autonomoushbmotorcontrol() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Fbmotordriver() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Fbmotordriver__init(msg: *mut Fbmotordriver) -> bool;
    fn smart_can_msgs__msg__Fbmotordriver__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Fbmotordriver>, size: usize) -> bool;
    fn smart_can_msgs__msg__Fbmotordriver__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Fbmotordriver>);
    fn smart_can_msgs__msg__Fbmotordriver__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Fbmotordriver>, out_seq: *mut rosidl_runtime_rs::Sequence<Fbmotordriver>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Fbmotordriver
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Fbmotordriver {

    // This member is not documented.
    #[allow(missing_docs)]
    pub gear_status_from_motor: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub plustripdistance: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub vehiclerpm: u16,

}



impl Default for Fbmotordriver {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Fbmotordriver__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Fbmotordriver__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Fbmotordriver {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Fbmotordriver__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Fbmotordriver__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Fbmotordriver__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Fbmotordriver {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Fbmotordriver where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Fbmotordriver";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Fbmotordriver() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Fbvehiclespeed() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Fbvehiclespeed__init(msg: *mut Fbvehiclespeed) -> bool;
    fn smart_can_msgs__msg__Fbvehiclespeed__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Fbvehiclespeed>, size: usize) -> bool;
    fn smart_can_msgs__msg__Fbvehiclespeed__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Fbvehiclespeed>);
    fn smart_can_msgs__msg__Fbvehiclespeed__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Fbvehiclespeed>, out_seq: *mut rosidl_runtime_rs::Sequence<Fbvehiclespeed>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Fbvehiclespeed
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Fbvehiclespeed {

    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_vehiclespeed_kmh: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_reelvehiclespeed_kmh: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_reelvehiclespeed_ms: u8,

}



impl Default for Fbvehiclespeed {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Fbvehiclespeed__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Fbvehiclespeed__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Fbvehiclespeed {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Fbvehiclespeed__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Fbvehiclespeed__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Fbvehiclespeed__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Fbvehiclespeed {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Fbvehiclespeed where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Fbvehiclespeed";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Fbvehiclespeed() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Fbomuxtoautonomous() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Fbomuxtoautonomous__init(msg: *mut Fbomuxtoautonomous) -> bool;
    fn smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Fbomuxtoautonomous>, size: usize) -> bool;
    fn smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Fbomuxtoautonomous>);
    fn smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Fbomuxtoautonomous>, out_seq: *mut rosidl_runtime_rs::Sequence<Fbomuxtoautonomous>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Fbomuxtoautonomous
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Fbomuxtoautonomous {

    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_emergency: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_reverselight: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_rightsignal: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_windowresistance: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_leftsignal: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_interiorlight: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_drl: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_doorkeystatus: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_brakelight: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_batteryvoltage: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_chargeinput: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_highbeam: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_lowbeam: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_ignition: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_hazardouslight: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_vehiclestatus: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_leftdoorstatus: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_rightdoorstatus: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_batterysoc: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_errorpowertrain: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_errorbattery: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fb_brakepedal_voltage_en: u8,

}



impl Default for Fbomuxtoautonomous {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Fbomuxtoautonomous__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Fbomuxtoautonomous__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Fbomuxtoautonomous {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Fbomuxtoautonomous {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Fbomuxtoautonomous where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Fbomuxtoautonomous";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Fbomuxtoautonomous() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Sndrcunitsteeringdata() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Sndrcunitsteeringdata__init(msg: *mut Sndrcunitsteeringdata) -> bool;
    fn smart_can_msgs__msg__Sndrcunitsteeringdata__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Sndrcunitsteeringdata>, size: usize) -> bool;
    fn smart_can_msgs__msg__Sndrcunitsteeringdata__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Sndrcunitsteeringdata>);
    fn smart_can_msgs__msg__Sndrcunitsteeringdata__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Sndrcunitsteeringdata>, out_seq: *mut rosidl_runtime_rs::Sequence<Sndrcunitsteeringdata>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Sndrcunitsteeringdata
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Sndrcunitsteeringdata {

    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_steering_rightlimit: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_steering_leftlimit: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_steeringpwm: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_steeringdirection: u8,

}



impl Default for Sndrcunitsteeringdata {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Sndrcunitsteeringdata__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Sndrcunitsteeringdata__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Sndrcunitsteeringdata {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Sndrcunitsteeringdata__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Sndrcunitsteeringdata__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Sndrcunitsteeringdata__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Sndrcunitsteeringdata {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Sndrcunitsteeringdata where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Sndrcunitsteeringdata";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Sndrcunitsteeringdata() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Sndrcunitbrakedata() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Sndrcunitbrakedata__init(msg: *mut Sndrcunitbrakedata) -> bool;
    fn smart_can_msgs__msg__Sndrcunitbrakedata__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Sndrcunitbrakedata>, size: usize) -> bool;
    fn smart_can_msgs__msg__Sndrcunitbrakedata__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Sndrcunitbrakedata>);
    fn smart_can_msgs__msg__Sndrcunitbrakedata__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Sndrcunitbrakedata>, out_seq: *mut rosidl_runtime_rs::Sequence<Sndrcunitbrakedata>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Sndrcunitbrakedata
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Sndrcunitbrakedata {

    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_brakepedal_speed: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_brakepedal_acc: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_brakepedal_pos: u8,

}



impl Default for Sndrcunitbrakedata {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Sndrcunitbrakedata__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Sndrcunitbrakedata__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Sndrcunitbrakedata {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Sndrcunitbrakedata__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Sndrcunitbrakedata__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Sndrcunitbrakedata__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Sndrcunitbrakedata {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Sndrcunitbrakedata where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Sndrcunitbrakedata";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Sndrcunitbrakedata() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Sndrcunithandbrakedata() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Sndrcunithandbrakedata__init(msg: *mut Sndrcunithandbrakedata) -> bool;
    fn smart_can_msgs__msg__Sndrcunithandbrakedata__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Sndrcunithandbrakedata>, size: usize) -> bool;
    fn smart_can_msgs__msg__Sndrcunithandbrakedata__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Sndrcunithandbrakedata>);
    fn smart_can_msgs__msg__Sndrcunithandbrakedata__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Sndrcunithandbrakedata>, out_seq: *mut rosidl_runtime_rs::Sequence<Sndrcunithandbrakedata>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Sndrcunithandbrakedata
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Sndrcunithandbrakedata {

    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_hb_pwmvalue: u16,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_handbrake_press: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_handbrake_free: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rc_handbrakedata: u8,

}



impl Default for Sndrcunithandbrakedata {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Sndrcunithandbrakedata__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Sndrcunithandbrakedata__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Sndrcunithandbrakedata {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Sndrcunithandbrakedata__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Sndrcunithandbrakedata__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Sndrcunithandbrakedata__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Sndrcunithandbrakedata {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Sndrcunithandbrakedata where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Sndrcunithandbrakedata";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Sndrcunithandbrakedata() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Autonomousheardbit() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Autonomousheardbit__init(msg: *mut Autonomousheardbit) -> bool;
    fn smart_can_msgs__msg__Autonomousheardbit__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Autonomousheardbit>, size: usize) -> bool;
    fn smart_can_msgs__msg__Autonomousheardbit__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Autonomousheardbit>);
    fn smart_can_msgs__msg__Autonomousheardbit__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Autonomousheardbit>, out_seq: *mut rosidl_runtime_rs::Sequence<Autonomousheardbit>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Autonomousheardbit
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Autonomousheardbit {

    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomousmanuelselect: u8,

}



impl Default for Autonomousheardbit {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Autonomousheardbit__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Autonomousheardbit__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Autonomousheardbit {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomousheardbit__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomousheardbit__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Autonomousheardbit__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Autonomousheardbit {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Autonomousheardbit where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Autonomousheardbit";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Autonomousheardbit() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Feedbacksteeringangle() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Feedbacksteeringangle__init(msg: *mut Feedbacksteeringangle) -> bool;
    fn smart_can_msgs__msg__Feedbacksteeringangle__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Feedbacksteeringangle>, size: usize) -> bool;
    fn smart_can_msgs__msg__Feedbacksteeringangle__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Feedbacksteeringangle>);
    fn smart_can_msgs__msg__Feedbacksteeringangle__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Feedbacksteeringangle>, out_seq: *mut rosidl_runtime_rs::Sequence<Feedbacksteeringangle>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Feedbacksteeringangle
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Feedbacksteeringangle {

    // This member is not documented.
    #[allow(missing_docs)]
    pub feedbacksteeringangle: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedbackbrakepedalangle: i8,

}



impl Default for Feedbacksteeringangle {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Feedbacksteeringangle__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Feedbacksteeringangle__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Feedbacksteeringangle {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Feedbacksteeringangle__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Feedbacksteeringangle__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Feedbacksteeringangle__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Feedbacksteeringangle {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Feedbacksteeringangle where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Feedbacksteeringangle";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Feedbacksteeringangle() }
  }
}


#[link(name = "smart_can_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Feedbacksensor() -> *const std::ffi::c_void;
}

#[link(name = "smart_can_msgs__rosidl_generator_c")]
extern "C" {
    fn smart_can_msgs__msg__Feedbacksensor__init(msg: *mut Feedbacksensor) -> bool;
    fn smart_can_msgs__msg__Feedbacksensor__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Feedbacksensor>, size: usize) -> bool;
    fn smart_can_msgs__msg__Feedbacksensor__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Feedbacksensor>);
    fn smart_can_msgs__msg__Feedbacksensor__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Feedbacksensor>, out_seq: *mut rosidl_runtime_rs::Sequence<Feedbacksensor>) -> bool;
}

// Corresponds to smart_can_msgs__msg__Feedbacksensor
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Feedbacksensor {

    // This member is not documented.
    #[allow(missing_docs)]
    pub steeringanglesensorhamdata: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub brakepedalsensorhamdata: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub handbrakesensor: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub handbrakesensor_hamdata: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub indir: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub kaldir: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub butonindir: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub butonkaldir: u8,

}



impl Default for Feedbacksensor {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !smart_can_msgs__msg__Feedbacksensor__init(&mut msg as *mut _) {
        panic!("Call to smart_can_msgs__msg__Feedbacksensor__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Feedbacksensor {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Feedbacksensor__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Feedbacksensor__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { smart_can_msgs__msg__Feedbacksensor__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Feedbacksensor {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Feedbacksensor where Self: Sized {
  const TYPE_NAME: &'static str = "smart_can_msgs/msg/Feedbacksensor";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__smart_can_msgs__msg__Feedbacksensor() }
  }
}


