// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Kinematicmessages.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__KINEMATICMESSAGES__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__KINEMATICMESSAGES__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/kinematicmessages__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Kinematicmessages_link_length
{
public:
  explicit Init_Kinematicmessages_link_length(::smart_can_msgs::msg::Kinematicmessages & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Kinematicmessages link_length(::smart_can_msgs::msg::Kinematicmessages::_link_length_type arg)
  {
    msg_.link_length = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Kinematicmessages msg_;
};

class Init_Kinematicmessages_angular_velocity
{
public:
  explicit Init_Kinematicmessages_angular_velocity(::smart_can_msgs::msg::Kinematicmessages & msg)
  : msg_(msg)
  {}
  Init_Kinematicmessages_link_length angular_velocity(::smart_can_msgs::msg::Kinematicmessages::_angular_velocity_type arg)
  {
    msg_.angular_velocity = std::move(arg);
    return Init_Kinematicmessages_link_length(msg_);
  }

private:
  ::smart_can_msgs::msg::Kinematicmessages msg_;
};

class Init_Kinematicmessages_angle_y
{
public:
  explicit Init_Kinematicmessages_angle_y(::smart_can_msgs::msg::Kinematicmessages & msg)
  : msg_(msg)
  {}
  Init_Kinematicmessages_angular_velocity angle_y(::smart_can_msgs::msg::Kinematicmessages::_angle_y_type arg)
  {
    msg_.angle_y = std::move(arg);
    return Init_Kinematicmessages_angular_velocity(msg_);
  }

private:
  ::smart_can_msgs::msg::Kinematicmessages msg_;
};

class Init_Kinematicmessages_angle
{
public:
  explicit Init_Kinematicmessages_angle(::smart_can_msgs::msg::Kinematicmessages & msg)
  : msg_(msg)
  {}
  Init_Kinematicmessages_angle_y angle(::smart_can_msgs::msg::Kinematicmessages::_angle_type arg)
  {
    msg_.angle = std::move(arg);
    return Init_Kinematicmessages_angle_y(msg_);
  }

private:
  ::smart_can_msgs::msg::Kinematicmessages msg_;
};

class Init_Kinematicmessages_joint_type
{
public:
  Init_Kinematicmessages_joint_type()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Kinematicmessages_angle joint_type(::smart_can_msgs::msg::Kinematicmessages::_joint_type_type arg)
  {
    msg_.joint_type = std::move(arg);
    return Init_Kinematicmessages_angle(msg_);
  }

private:
  ::smart_can_msgs::msg::Kinematicmessages msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Kinematicmessages>()
{
  return smart_can_msgs::msg::builder::Init_Kinematicmessages_joint_type();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__KINEMATICMESSAGES__BUILDER_HPP_
