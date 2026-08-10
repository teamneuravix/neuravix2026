// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Rcthrtdata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__RCTHRTDATA__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__RCTHRTDATA__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/rcthrtdata__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Rcthrtdata_rc_thrt_pedal_press
{
public:
  explicit Init_Rcthrtdata_rc_thrt_pedal_press(::smart_can_msgs::msg::Rcthrtdata & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Rcthrtdata rc_thrt_pedal_press(::smart_can_msgs::msg::Rcthrtdata::_rc_thrt_pedal_press_type arg)
  {
    msg_.rc_thrt_pedal_press = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcthrtdata msg_;
};

class Init_Rcthrtdata_rc_thrt_pedal_position
{
public:
  Init_Rcthrtdata_rc_thrt_pedal_position()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Rcthrtdata_rc_thrt_pedal_press rc_thrt_pedal_position(::smart_can_msgs::msg::Rcthrtdata::_rc_thrt_pedal_position_type arg)
  {
    msg_.rc_thrt_pedal_position = std::move(arg);
    return Init_Rcthrtdata_rc_thrt_pedal_press(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcthrtdata msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Rcthrtdata>()
{
  return smart_can_msgs::msg::builder::Init_Rcthrtdata_rc_thrt_pedal_position();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__RCTHRTDATA__BUILDER_HPP_
