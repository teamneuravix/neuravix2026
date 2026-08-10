// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Sndrcunitsteeringdata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITSTEERINGDATA__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITSTEERINGDATA__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/sndrcunitsteeringdata__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Sndrcunitsteeringdata_rc_steeringdirection
{
public:
  explicit Init_Sndrcunitsteeringdata_rc_steeringdirection(::smart_can_msgs::msg::Sndrcunitsteeringdata & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Sndrcunitsteeringdata rc_steeringdirection(::smart_can_msgs::msg::Sndrcunitsteeringdata::_rc_steeringdirection_type arg)
  {
    msg_.rc_steeringdirection = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunitsteeringdata msg_;
};

class Init_Sndrcunitsteeringdata_rc_steeringpwm
{
public:
  explicit Init_Sndrcunitsteeringdata_rc_steeringpwm(::smart_can_msgs::msg::Sndrcunitsteeringdata & msg)
  : msg_(msg)
  {}
  Init_Sndrcunitsteeringdata_rc_steeringdirection rc_steeringpwm(::smart_can_msgs::msg::Sndrcunitsteeringdata::_rc_steeringpwm_type arg)
  {
    msg_.rc_steeringpwm = std::move(arg);
    return Init_Sndrcunitsteeringdata_rc_steeringdirection(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunitsteeringdata msg_;
};

class Init_Sndrcunitsteeringdata_rc_steering_leftlimit
{
public:
  explicit Init_Sndrcunitsteeringdata_rc_steering_leftlimit(::smart_can_msgs::msg::Sndrcunitsteeringdata & msg)
  : msg_(msg)
  {}
  Init_Sndrcunitsteeringdata_rc_steeringpwm rc_steering_leftlimit(::smart_can_msgs::msg::Sndrcunitsteeringdata::_rc_steering_leftlimit_type arg)
  {
    msg_.rc_steering_leftlimit = std::move(arg);
    return Init_Sndrcunitsteeringdata_rc_steeringpwm(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunitsteeringdata msg_;
};

class Init_Sndrcunitsteeringdata_rc_steering_rightlimit
{
public:
  Init_Sndrcunitsteeringdata_rc_steering_rightlimit()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Sndrcunitsteeringdata_rc_steering_leftlimit rc_steering_rightlimit(::smart_can_msgs::msg::Sndrcunitsteeringdata::_rc_steering_rightlimit_type arg)
  {
    msg_.rc_steering_rightlimit = std::move(arg);
    return Init_Sndrcunitsteeringdata_rc_steering_leftlimit(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunitsteeringdata msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Sndrcunitsteeringdata>()
{
  return smart_can_msgs::msg::builder::Init_Sndrcunitsteeringdata_rc_steering_rightlimit();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITSTEERINGDATA__BUILDER_HPP_
