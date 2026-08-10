#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to carla_ackermann_msgs__msg__EgoVehicleControlInfo
/// Copyright (c) 2018-2019 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.
///
/// This represents an info message of the ego vehicle

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EgoVehicleControlInfo {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

    /// the restrictions
    pub restrictions: super::msg::EgoVehicleControlMaxima,

    /// the target values
    pub target: super::msg::EgoVehicleControlTarget,

    /// the currently measured values
    pub current: super::msg::EgoVehicleControlCurrent,

    /// the current control status
    pub status: super::msg::EgoVehicleControlStatus,

    /// the current control output to CARLA
    pub output: carla_msgs::msg::CarlaEgoVehicleControl,

}



impl Default for EgoVehicleControlInfo {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::EgoVehicleControlInfo::default())
  }
}

impl rosidl_runtime_rs::Message for EgoVehicleControlInfo {
  type RmwMsg = super::msg::rmw::EgoVehicleControlInfo;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        restrictions: super::msg::EgoVehicleControlMaxima::into_rmw_message(std::borrow::Cow::Owned(msg.restrictions)).into_owned(),
        target: super::msg::EgoVehicleControlTarget::into_rmw_message(std::borrow::Cow::Owned(msg.target)).into_owned(),
        current: super::msg::EgoVehicleControlCurrent::into_rmw_message(std::borrow::Cow::Owned(msg.current)).into_owned(),
        status: super::msg::EgoVehicleControlStatus::into_rmw_message(std::borrow::Cow::Owned(msg.status)).into_owned(),
        output: carla_msgs::msg::CarlaEgoVehicleControl::into_rmw_message(std::borrow::Cow::Owned(msg.output)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        restrictions: super::msg::EgoVehicleControlMaxima::into_rmw_message(std::borrow::Cow::Borrowed(&msg.restrictions)).into_owned(),
        target: super::msg::EgoVehicleControlTarget::into_rmw_message(std::borrow::Cow::Borrowed(&msg.target)).into_owned(),
        current: super::msg::EgoVehicleControlCurrent::into_rmw_message(std::borrow::Cow::Borrowed(&msg.current)).into_owned(),
        status: super::msg::EgoVehicleControlStatus::into_rmw_message(std::borrow::Cow::Borrowed(&msg.status)).into_owned(),
        output: carla_msgs::msg::CarlaEgoVehicleControl::into_rmw_message(std::borrow::Cow::Borrowed(&msg.output)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      restrictions: super::msg::EgoVehicleControlMaxima::from_rmw_message(msg.restrictions),
      target: super::msg::EgoVehicleControlTarget::from_rmw_message(msg.target),
      current: super::msg::EgoVehicleControlCurrent::from_rmw_message(msg.current),
      status: super::msg::EgoVehicleControlStatus::from_rmw_message(msg.status),
      output: carla_msgs::msg::CarlaEgoVehicleControl::from_rmw_message(msg.output),
    }
  }
}


// Corresponds to carla_ackermann_msgs__msg__EgoVehicleControlCurrent
/// Copyright (c) 2018-2019 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.
///
/// This represents the current time/speed/accel values of the vehicle used by the controller

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::EgoVehicleControlCurrent::default())
  }
}

impl rosidl_runtime_rs::Message for EgoVehicleControlCurrent {
  type RmwMsg = super::msg::rmw::EgoVehicleControlCurrent;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        time_sec: msg.time_sec,
        speed: msg.speed,
        speed_abs: msg.speed_abs,
        accel: msg.accel,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      time_sec: msg.time_sec,
      speed: msg.speed,
      speed_abs: msg.speed_abs,
      accel: msg.accel,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      time_sec: msg.time_sec,
      speed: msg.speed,
      speed_abs: msg.speed_abs,
      accel: msg.accel,
    }
  }
}


// Corresponds to carla_ackermann_msgs__msg__EgoVehicleControlMaxima
/// Copyright (c) 2018-2019 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.
///
/// This represents some ego vehicle control maximal values

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::EgoVehicleControlMaxima::default())
  }
}

impl rosidl_runtime_rs::Message for EgoVehicleControlMaxima {
  type RmwMsg = super::msg::rmw::EgoVehicleControlMaxima;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        max_steering_angle: msg.max_steering_angle,
        max_speed: msg.max_speed,
        max_accel: msg.max_accel,
        max_decel: msg.max_decel,
        min_accel: msg.min_accel,
        max_pedal: msg.max_pedal,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      max_steering_angle: msg.max_steering_angle,
      max_speed: msg.max_speed,
      max_accel: msg.max_accel,
      max_decel: msg.max_decel,
      min_accel: msg.min_accel,
      max_pedal: msg.max_pedal,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      max_steering_angle: msg.max_steering_angle,
      max_speed: msg.max_speed,
      max_accel: msg.max_accel,
      max_decel: msg.max_decel,
      min_accel: msg.min_accel,
      max_pedal: msg.max_pedal,
    }
  }
}


// Corresponds to carla_ackermann_msgs__msg__EgoVehicleControlStatus
/// Copyright (c) 2018-2019 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.
///
/// This represents the control status variables of the ego vehicle control

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct EgoVehicleControlStatus {
    /// the current control status
    pub status: std::string::String,

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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::EgoVehicleControlStatus::default())
  }
}

impl rosidl_runtime_rs::Message for EgoVehicleControlStatus {
  type RmwMsg = super::msg::rmw::EgoVehicleControlStatus;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        status: msg.status.as_str().into(),
        speed_control_activation_count: msg.speed_control_activation_count,
        speed_control_accel_delta: msg.speed_control_accel_delta,
        speed_control_accel_target: msg.speed_control_accel_target,
        accel_control_pedal_delta: msg.accel_control_pedal_delta,
        accel_control_pedal_target: msg.accel_control_pedal_target,
        brake_upper_border: msg.brake_upper_border,
        throttle_lower_border: msg.throttle_lower_border,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        status: msg.status.as_str().into(),
      speed_control_activation_count: msg.speed_control_activation_count,
      speed_control_accel_delta: msg.speed_control_accel_delta,
      speed_control_accel_target: msg.speed_control_accel_target,
      accel_control_pedal_delta: msg.accel_control_pedal_delta,
      accel_control_pedal_target: msg.accel_control_pedal_target,
      brake_upper_border: msg.brake_upper_border,
      throttle_lower_border: msg.throttle_lower_border,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      status: msg.status.to_string(),
      speed_control_activation_count: msg.speed_control_activation_count,
      speed_control_accel_delta: msg.speed_control_accel_delta,
      speed_control_accel_target: msg.speed_control_accel_target,
      accel_control_pedal_delta: msg.accel_control_pedal_delta,
      accel_control_pedal_target: msg.accel_control_pedal_target,
      brake_upper_border: msg.brake_upper_border,
      throttle_lower_border: msg.throttle_lower_border,
    }
  }
}


// Corresponds to carla_ackermann_msgs__msg__EgoVehicleControlTarget
/// Copyright (c) 2018-2019 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.
///
/// This represents the target speed/accel values of the ego vehicle

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::EgoVehicleControlTarget::default())
  }
}

impl rosidl_runtime_rs::Message for EgoVehicleControlTarget {
  type RmwMsg = super::msg::rmw::EgoVehicleControlTarget;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        steering_angle: msg.steering_angle,
        speed: msg.speed,
        speed_abs: msg.speed_abs,
        accel: msg.accel,
        jerk: msg.jerk,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      steering_angle: msg.steering_angle,
      speed: msg.speed,
      speed_abs: msg.speed_abs,
      accel: msg.accel,
      jerk: msg.jerk,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      steering_angle: msg.steering_angle,
      speed: msg.speed,
      speed_abs: msg.speed_abs,
      accel: msg.accel,
      jerk: msg.jerk,
    }
  }
}


