// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Sndrcunitbrakedata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITBRAKEDATA__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITBRAKEDATA__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/sndrcunitbrakedata__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Sndrcunitbrakedata_rc_brakepedal_pos
{
public:
  explicit Init_Sndrcunitbrakedata_rc_brakepedal_pos(::smart_can_msgs::msg::Sndrcunitbrakedata & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Sndrcunitbrakedata rc_brakepedal_pos(::smart_can_msgs::msg::Sndrcunitbrakedata::_rc_brakepedal_pos_type arg)
  {
    msg_.rc_brakepedal_pos = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunitbrakedata msg_;
};

class Init_Sndrcunitbrakedata_rc_brakepedal_acc
{
public:
  explicit Init_Sndrcunitbrakedata_rc_brakepedal_acc(::smart_can_msgs::msg::Sndrcunitbrakedata & msg)
  : msg_(msg)
  {}
  Init_Sndrcunitbrakedata_rc_brakepedal_pos rc_brakepedal_acc(::smart_can_msgs::msg::Sndrcunitbrakedata::_rc_brakepedal_acc_type arg)
  {
    msg_.rc_brakepedal_acc = std::move(arg);
    return Init_Sndrcunitbrakedata_rc_brakepedal_pos(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunitbrakedata msg_;
};

class Init_Sndrcunitbrakedata_rc_brakepedal_speed
{
public:
  Init_Sndrcunitbrakedata_rc_brakepedal_speed()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Sndrcunitbrakedata_rc_brakepedal_acc rc_brakepedal_speed(::smart_can_msgs::msg::Sndrcunitbrakedata::_rc_brakepedal_speed_type arg)
  {
    msg_.rc_brakepedal_speed = std::move(arg);
    return Init_Sndrcunitbrakedata_rc_brakepedal_acc(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunitbrakedata msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Sndrcunitbrakedata>()
{
  return smart_can_msgs::msg::builder::Init_Sndrcunitbrakedata_rc_brakepedal_speed();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITBRAKEDATA__BUILDER_HPP_
