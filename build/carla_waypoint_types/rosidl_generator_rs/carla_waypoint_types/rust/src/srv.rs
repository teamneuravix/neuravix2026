#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to carla_waypoint_types__srv__GetWaypoint_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetWaypoint_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub location: geometry_msgs::msg::Point,

}



impl Default for GetWaypoint_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetWaypoint_Request::default())
  }
}

impl rosidl_runtime_rs::Message for GetWaypoint_Request {
  type RmwMsg = super::srv::rmw::GetWaypoint_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        location: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.location)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        location: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.location)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      location: geometry_msgs::msg::Point::from_rmw_message(msg.location),
    }
  }
}


// Corresponds to carla_waypoint_types__srv__GetWaypoint_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetWaypoint_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub waypoint: super::msg::CarlaWaypoint,

}



impl Default for GetWaypoint_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetWaypoint_Response::default())
  }
}

impl rosidl_runtime_rs::Message for GetWaypoint_Response {
  type RmwMsg = super::srv::rmw::GetWaypoint_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        waypoint: super::msg::CarlaWaypoint::into_rmw_message(std::borrow::Cow::Owned(msg.waypoint)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        waypoint: super::msg::CarlaWaypoint::into_rmw_message(std::borrow::Cow::Borrowed(&msg.waypoint)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      waypoint: super::msg::CarlaWaypoint::from_rmw_message(msg.waypoint),
    }
  }
}


// Corresponds to carla_waypoint_types__srv__GetActorWaypoint_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetActorWaypoint_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub id: u32,

}



impl Default for GetActorWaypoint_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetActorWaypoint_Request::default())
  }
}

impl rosidl_runtime_rs::Message for GetActorWaypoint_Request {
  type RmwMsg = super::srv::rmw::GetActorWaypoint_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        id: msg.id,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      id: msg.id,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      id: msg.id,
    }
  }
}


// Corresponds to carla_waypoint_types__srv__GetActorWaypoint_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetActorWaypoint_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub waypoint: super::msg::CarlaWaypoint,

}



impl Default for GetActorWaypoint_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetActorWaypoint_Response::default())
  }
}

impl rosidl_runtime_rs::Message for GetActorWaypoint_Response {
  type RmwMsg = super::srv::rmw::GetActorWaypoint_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        waypoint: super::msg::CarlaWaypoint::into_rmw_message(std::borrow::Cow::Owned(msg.waypoint)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        waypoint: super::msg::CarlaWaypoint::into_rmw_message(std::borrow::Cow::Borrowed(&msg.waypoint)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      waypoint: super::msg::CarlaWaypoint::from_rmw_message(msg.waypoint),
    }
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


