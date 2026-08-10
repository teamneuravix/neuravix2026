// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Sndrcunithandbrakedata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITHANDBRAKEDATA__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITHANDBRAKEDATA__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/sndrcunithandbrakedata__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Sndrcunithandbrakedata_rc_handbrakedata
{
public:
  explicit Init_Sndrcunithandbrakedata_rc_handbrakedata(::smart_can_msgs::msg::Sndrcunithandbrakedata & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Sndrcunithandbrakedata rc_handbrakedata(::smart_can_msgs::msg::Sndrcunithandbrakedata::_rc_handbrakedata_type arg)
  {
    msg_.rc_handbrakedata = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunithandbrakedata msg_;
};

class Init_Sndrcunithandbrakedata_rc_handbrake_free
{
public:
  explicit Init_Sndrcunithandbrakedata_rc_handbrake_free(::smart_can_msgs::msg::Sndrcunithandbrakedata & msg)
  : msg_(msg)
  {}
  Init_Sndrcunithandbrakedata_rc_handbrakedata rc_handbrake_free(::smart_can_msgs::msg::Sndrcunithandbrakedata::_rc_handbrake_free_type arg)
  {
    msg_.rc_handbrake_free = std::move(arg);
    return Init_Sndrcunithandbrakedata_rc_handbrakedata(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunithandbrakedata msg_;
};

class Init_Sndrcunithandbrakedata_rc_handbrake_press
{
public:
  explicit Init_Sndrcunithandbrakedata_rc_handbrake_press(::smart_can_msgs::msg::Sndrcunithandbrakedata & msg)
  : msg_(msg)
  {}
  Init_Sndrcunithandbrakedata_rc_handbrake_free rc_handbrake_press(::smart_can_msgs::msg::Sndrcunithandbrakedata::_rc_handbrake_press_type arg)
  {
    msg_.rc_handbrake_press = std::move(arg);
    return Init_Sndrcunithandbrakedata_rc_handbrake_free(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunithandbrakedata msg_;
};

class Init_Sndrcunithandbrakedata_rc_hb_pwmvalue
{
public:
  Init_Sndrcunithandbrakedata_rc_hb_pwmvalue()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Sndrcunithandbrakedata_rc_handbrake_press rc_hb_pwmvalue(::smart_can_msgs::msg::Sndrcunithandbrakedata::_rc_hb_pwmvalue_type arg)
  {
    msg_.rc_hb_pwmvalue = std::move(arg);
    return Init_Sndrcunithandbrakedata_rc_handbrake_press(msg_);
  }

private:
  ::smart_can_msgs::msg::Sndrcunithandbrakedata msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Sndrcunithandbrakedata>()
{
  return smart_can_msgs::msg::builder::Init_Sndrcunithandbrakedata_rc_hb_pwmvalue();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITHANDBRAKEDATA__BUILDER_HPP_
