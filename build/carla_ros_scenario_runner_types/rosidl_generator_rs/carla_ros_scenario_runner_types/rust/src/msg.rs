#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to carla_ros_scenario_runner_types__msg__CarlaScenario
/// Copyright (c) 2020 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CarlaScenario {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub scenario_file: std::string::String,

}



impl Default for CarlaScenario {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CarlaScenario::default())
  }
}

impl rosidl_runtime_rs::Message for CarlaScenario {
  type RmwMsg = super::msg::rmw::CarlaScenario;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        name: msg.name.as_str().into(),
        scenario_file: msg.scenario_file.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        name: msg.name.as_str().into(),
        scenario_file: msg.scenario_file.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      name: msg.name.to_string(),
      scenario_file: msg.scenario_file.to_string(),
    }
  }
}


// Corresponds to carla_ros_scenario_runner_types__msg__CarlaScenarioList
/// Copyright (c) 2020 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CarlaScenarioList {

    // This member is not documented.
    #[allow(missing_docs)]
    pub scenarios: Vec<super::msg::CarlaScenario>,

}



impl Default for CarlaScenarioList {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CarlaScenarioList::default())
  }
}

impl rosidl_runtime_rs::Message for CarlaScenarioList {
  type RmwMsg = super::msg::rmw::CarlaScenarioList;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        scenarios: msg.scenarios
          .into_iter()
          .map(|elem| super::msg::CarlaScenario::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        scenarios: msg.scenarios
          .iter()
          .map(|elem| super::msg::CarlaScenario::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      scenarios: msg.scenarios
          .into_iter()
          .map(super::msg::CarlaScenario::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to carla_ros_scenario_runner_types__msg__CarlaScenarioRunnerStatus
/// Copyright (c) 2020 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CarlaScenarioRunnerStatus::default())
  }
}

impl rosidl_runtime_rs::Message for CarlaScenarioRunnerStatus {
  type RmwMsg = super::msg::rmw::CarlaScenarioRunnerStatus;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        status: msg.status,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      status: msg.status,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      status: msg.status,
    }
  }
}


