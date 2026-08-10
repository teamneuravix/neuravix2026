#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to carla_waypoint_types__msg__CarlaWaypoint
/// Copyright (c) 2020 Intel Corporation.
///
/// This work is licensed under the terms of the MIT license.
/// For a copy, see <https://opensource.org/licenses/MIT>.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CarlaWaypoint {

    // This member is not documented.
    #[allow(missing_docs)]
    pub road_id: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub section_id: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lane_id: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub is_junction: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pose: geometry_msgs::msg::Pose,

}



impl Default for CarlaWaypoint {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CarlaWaypoint::default())
  }
}

impl rosidl_runtime_rs::Message for CarlaWaypoint {
  type RmwMsg = super::msg::rmw::CarlaWaypoint;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        road_id: msg.road_id,
        section_id: msg.section_id,
        lane_id: msg.lane_id,
        is_junction: msg.is_junction,
        pose: geometry_msgs::msg::Pose::into_rmw_message(std::borrow::Cow::Owned(msg.pose)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      road_id: msg.road_id,
      section_id: msg.section_id,
      lane_id: msg.lane_id,
      is_junction: msg.is_junction,
        pose: geometry_msgs::msg::Pose::into_rmw_message(std::borrow::Cow::Borrowed(&msg.pose)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      road_id: msg.road_id,
      section_id: msg.section_id,
      lane_id: msg.lane_id,
      is_junction: msg.is_junction,
      pose: geometry_msgs::msg::Pose::from_rmw_message(msg.pose),
    }
  }
}


