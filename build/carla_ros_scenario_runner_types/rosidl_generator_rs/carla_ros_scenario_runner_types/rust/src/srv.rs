#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to carla_ros_scenario_runner_types__srv__ExecuteScenario_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ExecuteScenario_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub scenario: super::msg::CarlaScenario,

}



impl Default for ExecuteScenario_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ExecuteScenario_Request::default())
  }
}

impl rosidl_runtime_rs::Message for ExecuteScenario_Request {
  type RmwMsg = super::srv::rmw::ExecuteScenario_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        scenario: super::msg::CarlaScenario::into_rmw_message(std::borrow::Cow::Owned(msg.scenario)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        scenario: super::msg::CarlaScenario::into_rmw_message(std::borrow::Cow::Borrowed(&msg.scenario)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      scenario: super::msg::CarlaScenario::from_rmw_message(msg.scenario),
    }
  }
}


// Corresponds to carla_ros_scenario_runner_types__srv__ExecuteScenario_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ExecuteScenario_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub result: bool,

}



impl Default for ExecuteScenario_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ExecuteScenario_Response::default())
  }
}

impl rosidl_runtime_rs::Message for ExecuteScenario_Response {
  type RmwMsg = super::srv::rmw::ExecuteScenario_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        result: msg.result,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      result: msg.result,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      result: msg.result,
    }
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


