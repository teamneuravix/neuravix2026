#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to smart_can_msgs__msg__Dis

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Dis {

    // This member is not documented.
    #[allow(missing_docs)]
    pub angle: f32,

}



impl Default for Dis {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Dis::default())
  }
}

impl rosidl_runtime_rs::Message for Dis {
  type RmwMsg = super::msg::rmw::Dis;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        angle: msg.angle,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      angle: msg.angle,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      angle: msg.angle,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Kinematicmessages

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Kinematicmessages::default())
  }
}

impl rosidl_runtime_rs::Message for Kinematicmessages {
  type RmwMsg = super::msg::rmw::Kinematicmessages;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        joint_type: msg.joint_type,
        angle: msg.angle,
        angle_y: msg.angle_y,
        angular_velocity: msg.angular_velocity,
        link_length: msg.link_length,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      joint_type: msg.joint_type,
      angle: msg.angle,
      angle_y: msg.angle_y,
      angular_velocity: msg.angular_velocity,
      link_length: msg.link_length,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      joint_type: msg.joint_type,
      angle: msg.angle,
      angle_y: msg.angle_y,
      angular_velocity: msg.angular_velocity,
      link_length: msg.link_length,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Rcunittoomux

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Rcunittoomux::default())
  }
}

impl rosidl_runtime_rs::Message for Rcunittoomux {
  type RmwMsg = super::msg::rmw::Rcunittoomux;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        autonomous_emergency: msg.autonomous_emergency,
        rc_windowresintance: msg.rc_windowresintance,
        rc_interiorlight: msg.rc_interiorlight,
        rc_reverselight: msg.rc_reverselight,
        rc_drl: msg.rc_drl,
        rc_brakelight: msg.rc_brakelight,
        autonomous_door_open: msg.autonomous_door_open,
        autonomous_door_close: msg.autonomous_door_close,
        rc_signalstatus: msg.rc_signalstatus,
        rc_lowbeam: msg.rc_lowbeam,
        rc_highbeam: msg.rc_highbeam,
        rc_selectiongear: msg.rc_selectiongear,
        rc_ignition: msg.rc_ignition,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      autonomous_emergency: msg.autonomous_emergency,
      rc_windowresintance: msg.rc_windowresintance,
      rc_interiorlight: msg.rc_interiorlight,
      rc_reverselight: msg.rc_reverselight,
      rc_drl: msg.rc_drl,
      rc_brakelight: msg.rc_brakelight,
      autonomous_door_open: msg.autonomous_door_open,
      autonomous_door_close: msg.autonomous_door_close,
      rc_signalstatus: msg.rc_signalstatus,
      rc_lowbeam: msg.rc_lowbeam,
      rc_highbeam: msg.rc_highbeam,
      rc_selectiongear: msg.rc_selectiongear,
      rc_ignition: msg.rc_ignition,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      autonomous_emergency: msg.autonomous_emergency,
      rc_windowresintance: msg.rc_windowresintance,
      rc_interiorlight: msg.rc_interiorlight,
      rc_reverselight: msg.rc_reverselight,
      rc_drl: msg.rc_drl,
      rc_brakelight: msg.rc_brakelight,
      autonomous_door_open: msg.autonomous_door_open,
      autonomous_door_close: msg.autonomous_door_close,
      rc_signalstatus: msg.rc_signalstatus,
      rc_lowbeam: msg.rc_lowbeam,
      rc_highbeam: msg.rc_highbeam,
      rc_selectiongear: msg.rc_selectiongear,
      rc_ignition: msg.rc_ignition,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Rcthrtdata

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Rcthrtdata::default())
  }
}

impl rosidl_runtime_rs::Message for Rcthrtdata {
  type RmwMsg = super::msg::rmw::Rcthrtdata;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        rc_thrt_pedal_position: msg.rc_thrt_pedal_position,
        rc_thrt_pedal_press: msg.rc_thrt_pedal_press,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      rc_thrt_pedal_position: msg.rc_thrt_pedal_position,
      rc_thrt_pedal_press: msg.rc_thrt_pedal_press,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      rc_thrt_pedal_position: msg.rc_thrt_pedal_position,
      rc_thrt_pedal_press: msg.rc_thrt_pedal_press,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Autonomousbrakepedalcontrol

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Autonomousbrakepedalcontrol::default())
  }
}

impl rosidl_runtime_rs::Message for Autonomousbrakepedalcontrol {
  type RmwMsg = super::msg::rmw::Autonomousbrakepedalcontrol;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        autonomous_brakemotor_voltage: msg.autonomous_brakemotor_voltage,
        autonomous_brakepedalmotor_per: msg.autonomous_brakepedalmotor_per,
        autonomous_brakepedalmotor_acc: msg.autonomous_brakepedalmotor_acc,
        autonomous_brakepedalmotor_en: msg.autonomous_brakepedalmotor_en,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      autonomous_brakemotor_voltage: msg.autonomous_brakemotor_voltage,
      autonomous_brakepedalmotor_per: msg.autonomous_brakepedalmotor_per,
      autonomous_brakepedalmotor_acc: msg.autonomous_brakepedalmotor_acc,
      autonomous_brakepedalmotor_en: msg.autonomous_brakepedalmotor_en,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      autonomous_brakemotor_voltage: msg.autonomous_brakemotor_voltage,
      autonomous_brakepedalmotor_per: msg.autonomous_brakepedalmotor_per,
      autonomous_brakepedalmotor_acc: msg.autonomous_brakepedalmotor_acc,
      autonomous_brakepedalmotor_en: msg.autonomous_brakepedalmotor_en,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Autonomoussteeringmotcontrol

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Autonomoussteeringmotcontrol::default())
  }
}

impl rosidl_runtime_rs::Message for Autonomoussteeringmotcontrol {
  type RmwMsg = super::msg::rmw::Autonomoussteeringmotcontrol;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        autonomous_steeringmot_en: msg.autonomous_steeringmot_en,
        autonomous_steeringmot_pwm: msg.autonomous_steeringmot_pwm,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      autonomous_steeringmot_en: msg.autonomous_steeringmot_en,
      autonomous_steeringmot_pwm: msg.autonomous_steeringmot_pwm,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      autonomous_steeringmot_en: msg.autonomous_steeringmot_en,
      autonomous_steeringmot_pwm: msg.autonomous_steeringmot_pwm,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Autonomoushbmotorcontrol

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Autonomoushbmotorcontrol::default())
  }
}

impl rosidl_runtime_rs::Message for Autonomoushbmotorcontrol {
  type RmwMsg = super::msg::rmw::Autonomoushbmotorcontrol;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        autonomous_hb_motor_pwm: msg.autonomous_hb_motor_pwm,
        autonomous_hb_motstate: msg.autonomous_hb_motstate,
        autonomous_hb_moten: msg.autonomous_hb_moten,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      autonomous_hb_motor_pwm: msg.autonomous_hb_motor_pwm,
      autonomous_hb_motstate: msg.autonomous_hb_motstate,
      autonomous_hb_moten: msg.autonomous_hb_moten,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      autonomous_hb_motor_pwm: msg.autonomous_hb_motor_pwm,
      autonomous_hb_motstate: msg.autonomous_hb_motstate,
      autonomous_hb_moten: msg.autonomous_hb_moten,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Fbmotordriver

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Fbmotordriver::default())
  }
}

impl rosidl_runtime_rs::Message for Fbmotordriver {
  type RmwMsg = super::msg::rmw::Fbmotordriver;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        gear_status_from_motor: msg.gear_status_from_motor,
        plustripdistance: msg.plustripdistance,
        vehiclerpm: msg.vehiclerpm,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      gear_status_from_motor: msg.gear_status_from_motor,
      plustripdistance: msg.plustripdistance,
      vehiclerpm: msg.vehiclerpm,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      gear_status_from_motor: msg.gear_status_from_motor,
      plustripdistance: msg.plustripdistance,
      vehiclerpm: msg.vehiclerpm,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Fbvehiclespeed

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Fbvehiclespeed::default())
  }
}

impl rosidl_runtime_rs::Message for Fbvehiclespeed {
  type RmwMsg = super::msg::rmw::Fbvehiclespeed;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        fb_vehiclespeed_kmh: msg.fb_vehiclespeed_kmh,
        fb_reelvehiclespeed_kmh: msg.fb_reelvehiclespeed_kmh,
        fb_reelvehiclespeed_ms: msg.fb_reelvehiclespeed_ms,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      fb_vehiclespeed_kmh: msg.fb_vehiclespeed_kmh,
      fb_reelvehiclespeed_kmh: msg.fb_reelvehiclespeed_kmh,
      fb_reelvehiclespeed_ms: msg.fb_reelvehiclespeed_ms,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      fb_vehiclespeed_kmh: msg.fb_vehiclespeed_kmh,
      fb_reelvehiclespeed_kmh: msg.fb_reelvehiclespeed_kmh,
      fb_reelvehiclespeed_ms: msg.fb_reelvehiclespeed_ms,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Fbomuxtoautonomous

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Fbomuxtoautonomous::default())
  }
}

impl rosidl_runtime_rs::Message for Fbomuxtoautonomous {
  type RmwMsg = super::msg::rmw::Fbomuxtoautonomous;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        fb_emergency: msg.fb_emergency,
        fb_reverselight: msg.fb_reverselight,
        fb_rightsignal: msg.fb_rightsignal,
        fb_windowresistance: msg.fb_windowresistance,
        fb_leftsignal: msg.fb_leftsignal,
        fb_interiorlight: msg.fb_interiorlight,
        fb_drl: msg.fb_drl,
        fb_doorkeystatus: msg.fb_doorkeystatus,
        fb_brakelight: msg.fb_brakelight,
        fb_batteryvoltage: msg.fb_batteryvoltage,
        fb_chargeinput: msg.fb_chargeinput,
        fb_highbeam: msg.fb_highbeam,
        fb_lowbeam: msg.fb_lowbeam,
        fb_ignition: msg.fb_ignition,
        fb_hazardouslight: msg.fb_hazardouslight,
        fb_vehiclestatus: msg.fb_vehiclestatus,
        fb_leftdoorstatus: msg.fb_leftdoorstatus,
        fb_rightdoorstatus: msg.fb_rightdoorstatus,
        fb_batterysoc: msg.fb_batterysoc,
        fb_errorpowertrain: msg.fb_errorpowertrain,
        fb_errorbattery: msg.fb_errorbattery,
        fb_brakepedal_voltage_en: msg.fb_brakepedal_voltage_en,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      fb_emergency: msg.fb_emergency,
      fb_reverselight: msg.fb_reverselight,
      fb_rightsignal: msg.fb_rightsignal,
      fb_windowresistance: msg.fb_windowresistance,
      fb_leftsignal: msg.fb_leftsignal,
      fb_interiorlight: msg.fb_interiorlight,
      fb_drl: msg.fb_drl,
      fb_doorkeystatus: msg.fb_doorkeystatus,
      fb_brakelight: msg.fb_brakelight,
      fb_batteryvoltage: msg.fb_batteryvoltage,
      fb_chargeinput: msg.fb_chargeinput,
      fb_highbeam: msg.fb_highbeam,
      fb_lowbeam: msg.fb_lowbeam,
      fb_ignition: msg.fb_ignition,
      fb_hazardouslight: msg.fb_hazardouslight,
      fb_vehiclestatus: msg.fb_vehiclestatus,
      fb_leftdoorstatus: msg.fb_leftdoorstatus,
      fb_rightdoorstatus: msg.fb_rightdoorstatus,
      fb_batterysoc: msg.fb_batterysoc,
      fb_errorpowertrain: msg.fb_errorpowertrain,
      fb_errorbattery: msg.fb_errorbattery,
      fb_brakepedal_voltage_en: msg.fb_brakepedal_voltage_en,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      fb_emergency: msg.fb_emergency,
      fb_reverselight: msg.fb_reverselight,
      fb_rightsignal: msg.fb_rightsignal,
      fb_windowresistance: msg.fb_windowresistance,
      fb_leftsignal: msg.fb_leftsignal,
      fb_interiorlight: msg.fb_interiorlight,
      fb_drl: msg.fb_drl,
      fb_doorkeystatus: msg.fb_doorkeystatus,
      fb_brakelight: msg.fb_brakelight,
      fb_batteryvoltage: msg.fb_batteryvoltage,
      fb_chargeinput: msg.fb_chargeinput,
      fb_highbeam: msg.fb_highbeam,
      fb_lowbeam: msg.fb_lowbeam,
      fb_ignition: msg.fb_ignition,
      fb_hazardouslight: msg.fb_hazardouslight,
      fb_vehiclestatus: msg.fb_vehiclestatus,
      fb_leftdoorstatus: msg.fb_leftdoorstatus,
      fb_rightdoorstatus: msg.fb_rightdoorstatus,
      fb_batterysoc: msg.fb_batterysoc,
      fb_errorpowertrain: msg.fb_errorpowertrain,
      fb_errorbattery: msg.fb_errorbattery,
      fb_brakepedal_voltage_en: msg.fb_brakepedal_voltage_en,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Sndrcunitsteeringdata

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Sndrcunitsteeringdata::default())
  }
}

impl rosidl_runtime_rs::Message for Sndrcunitsteeringdata {
  type RmwMsg = super::msg::rmw::Sndrcunitsteeringdata;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        rc_steering_rightlimit: msg.rc_steering_rightlimit,
        rc_steering_leftlimit: msg.rc_steering_leftlimit,
        rc_steeringpwm: msg.rc_steeringpwm,
        rc_steeringdirection: msg.rc_steeringdirection,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      rc_steering_rightlimit: msg.rc_steering_rightlimit,
      rc_steering_leftlimit: msg.rc_steering_leftlimit,
      rc_steeringpwm: msg.rc_steeringpwm,
      rc_steeringdirection: msg.rc_steeringdirection,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      rc_steering_rightlimit: msg.rc_steering_rightlimit,
      rc_steering_leftlimit: msg.rc_steering_leftlimit,
      rc_steeringpwm: msg.rc_steeringpwm,
      rc_steeringdirection: msg.rc_steeringdirection,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Sndrcunitbrakedata

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Sndrcunitbrakedata::default())
  }
}

impl rosidl_runtime_rs::Message for Sndrcunitbrakedata {
  type RmwMsg = super::msg::rmw::Sndrcunitbrakedata;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        rc_brakepedal_speed: msg.rc_brakepedal_speed,
        rc_brakepedal_acc: msg.rc_brakepedal_acc,
        rc_brakepedal_pos: msg.rc_brakepedal_pos,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      rc_brakepedal_speed: msg.rc_brakepedal_speed,
      rc_brakepedal_acc: msg.rc_brakepedal_acc,
      rc_brakepedal_pos: msg.rc_brakepedal_pos,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      rc_brakepedal_speed: msg.rc_brakepedal_speed,
      rc_brakepedal_acc: msg.rc_brakepedal_acc,
      rc_brakepedal_pos: msg.rc_brakepedal_pos,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Sndrcunithandbrakedata

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Sndrcunithandbrakedata::default())
  }
}

impl rosidl_runtime_rs::Message for Sndrcunithandbrakedata {
  type RmwMsg = super::msg::rmw::Sndrcunithandbrakedata;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        rc_hb_pwmvalue: msg.rc_hb_pwmvalue,
        rc_handbrake_press: msg.rc_handbrake_press,
        rc_handbrake_free: msg.rc_handbrake_free,
        rc_handbrakedata: msg.rc_handbrakedata,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      rc_hb_pwmvalue: msg.rc_hb_pwmvalue,
      rc_handbrake_press: msg.rc_handbrake_press,
      rc_handbrake_free: msg.rc_handbrake_free,
      rc_handbrakedata: msg.rc_handbrakedata,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      rc_hb_pwmvalue: msg.rc_hb_pwmvalue,
      rc_handbrake_press: msg.rc_handbrake_press,
      rc_handbrake_free: msg.rc_handbrake_free,
      rc_handbrakedata: msg.rc_handbrakedata,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Autonomousheardbit

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Autonomousheardbit {

    // This member is not documented.
    #[allow(missing_docs)]
    pub autonomousmanuelselect: u8,

}



impl Default for Autonomousheardbit {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Autonomousheardbit::default())
  }
}

impl rosidl_runtime_rs::Message for Autonomousheardbit {
  type RmwMsg = super::msg::rmw::Autonomousheardbit;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        autonomousmanuelselect: msg.autonomousmanuelselect,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      autonomousmanuelselect: msg.autonomousmanuelselect,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      autonomousmanuelselect: msg.autonomousmanuelselect,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Feedbacksteeringangle

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Feedbacksteeringangle::default())
  }
}

impl rosidl_runtime_rs::Message for Feedbacksteeringangle {
  type RmwMsg = super::msg::rmw::Feedbacksteeringangle;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        feedbacksteeringangle: msg.feedbacksteeringangle,
        feedbackbrakepedalangle: msg.feedbackbrakepedalangle,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      feedbacksteeringangle: msg.feedbacksteeringangle,
      feedbackbrakepedalangle: msg.feedbackbrakepedalangle,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      feedbacksteeringangle: msg.feedbacksteeringangle,
      feedbackbrakepedalangle: msg.feedbackbrakepedalangle,
    }
  }
}


// Corresponds to smart_can_msgs__msg__Feedbacksensor

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Feedbacksensor::default())
  }
}

impl rosidl_runtime_rs::Message for Feedbacksensor {
  type RmwMsg = super::msg::rmw::Feedbacksensor;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        steeringanglesensorhamdata: msg.steeringanglesensorhamdata,
        brakepedalsensorhamdata: msg.brakepedalsensorhamdata,
        handbrakesensor: msg.handbrakesensor,
        handbrakesensor_hamdata: msg.handbrakesensor_hamdata,
        indir: msg.indir,
        kaldir: msg.kaldir,
        butonindir: msg.butonindir,
        butonkaldir: msg.butonkaldir,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      steeringanglesensorhamdata: msg.steeringanglesensorhamdata,
      brakepedalsensorhamdata: msg.brakepedalsensorhamdata,
      handbrakesensor: msg.handbrakesensor,
      handbrakesensor_hamdata: msg.handbrakesensor_hamdata,
      indir: msg.indir,
      kaldir: msg.kaldir,
      butonindir: msg.butonindir,
      butonkaldir: msg.butonkaldir,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      steeringanglesensorhamdata: msg.steeringanglesensorhamdata,
      brakepedalsensorhamdata: msg.brakepedalsensorhamdata,
      handbrakesensor: msg.handbrakesensor,
      handbrakesensor_hamdata: msg.handbrakesensor_hamdata,
      indir: msg.indir,
      kaldir: msg.kaldir,
      butonindir: msg.butonindir,
      butonkaldir: msg.butonkaldir,
    }
  }
}


