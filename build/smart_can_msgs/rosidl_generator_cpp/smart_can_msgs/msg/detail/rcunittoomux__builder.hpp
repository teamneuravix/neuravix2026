// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Rcunittoomux.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/rcunittoomux__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Rcunittoomux_rc_ignition
{
public:
  explicit Init_Rcunittoomux_rc_ignition(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Rcunittoomux rc_ignition(::smart_can_msgs::msg::Rcunittoomux::_rc_ignition_type arg)
  {
    msg_.rc_ignition = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_rc_selectiongear
{
public:
  explicit Init_Rcunittoomux_rc_selectiongear(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_rc_ignition rc_selectiongear(::smart_can_msgs::msg::Rcunittoomux::_rc_selectiongear_type arg)
  {
    msg_.rc_selectiongear = std::move(arg);
    return Init_Rcunittoomux_rc_ignition(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_rc_highbeam
{
public:
  explicit Init_Rcunittoomux_rc_highbeam(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_rc_selectiongear rc_highbeam(::smart_can_msgs::msg::Rcunittoomux::_rc_highbeam_type arg)
  {
    msg_.rc_highbeam = std::move(arg);
    return Init_Rcunittoomux_rc_selectiongear(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_rc_lowbeam
{
public:
  explicit Init_Rcunittoomux_rc_lowbeam(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_rc_highbeam rc_lowbeam(::smart_can_msgs::msg::Rcunittoomux::_rc_lowbeam_type arg)
  {
    msg_.rc_lowbeam = std::move(arg);
    return Init_Rcunittoomux_rc_highbeam(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_rc_signalstatus
{
public:
  explicit Init_Rcunittoomux_rc_signalstatus(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_rc_lowbeam rc_signalstatus(::smart_can_msgs::msg::Rcunittoomux::_rc_signalstatus_type arg)
  {
    msg_.rc_signalstatus = std::move(arg);
    return Init_Rcunittoomux_rc_lowbeam(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_autonomous_door_close
{
public:
  explicit Init_Rcunittoomux_autonomous_door_close(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_rc_signalstatus autonomous_door_close(::smart_can_msgs::msg::Rcunittoomux::_autonomous_door_close_type arg)
  {
    msg_.autonomous_door_close = std::move(arg);
    return Init_Rcunittoomux_rc_signalstatus(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_autonomous_door_open
{
public:
  explicit Init_Rcunittoomux_autonomous_door_open(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_autonomous_door_close autonomous_door_open(::smart_can_msgs::msg::Rcunittoomux::_autonomous_door_open_type arg)
  {
    msg_.autonomous_door_open = std::move(arg);
    return Init_Rcunittoomux_autonomous_door_close(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_rc_brakelight
{
public:
  explicit Init_Rcunittoomux_rc_brakelight(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_autonomous_door_open rc_brakelight(::smart_can_msgs::msg::Rcunittoomux::_rc_brakelight_type arg)
  {
    msg_.rc_brakelight = std::move(arg);
    return Init_Rcunittoomux_autonomous_door_open(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_rc_drl
{
public:
  explicit Init_Rcunittoomux_rc_drl(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_rc_brakelight rc_drl(::smart_can_msgs::msg::Rcunittoomux::_rc_drl_type arg)
  {
    msg_.rc_drl = std::move(arg);
    return Init_Rcunittoomux_rc_brakelight(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_rc_reverselight
{
public:
  explicit Init_Rcunittoomux_rc_reverselight(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_rc_drl rc_reverselight(::smart_can_msgs::msg::Rcunittoomux::_rc_reverselight_type arg)
  {
    msg_.rc_reverselight = std::move(arg);
    return Init_Rcunittoomux_rc_drl(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_rc_interiorlight
{
public:
  explicit Init_Rcunittoomux_rc_interiorlight(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_rc_reverselight rc_interiorlight(::smart_can_msgs::msg::Rcunittoomux::_rc_interiorlight_type arg)
  {
    msg_.rc_interiorlight = std::move(arg);
    return Init_Rcunittoomux_rc_reverselight(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_rc_windowresintance
{
public:
  explicit Init_Rcunittoomux_rc_windowresintance(::smart_can_msgs::msg::Rcunittoomux & msg)
  : msg_(msg)
  {}
  Init_Rcunittoomux_rc_interiorlight rc_windowresintance(::smart_can_msgs::msg::Rcunittoomux::_rc_windowresintance_type arg)
  {
    msg_.rc_windowresintance = std::move(arg);
    return Init_Rcunittoomux_rc_interiorlight(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

class Init_Rcunittoomux_autonomous_emergency
{
public:
  Init_Rcunittoomux_autonomous_emergency()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Rcunittoomux_rc_windowresintance autonomous_emergency(::smart_can_msgs::msg::Rcunittoomux::_autonomous_emergency_type arg)
  {
    msg_.autonomous_emergency = std::move(arg);
    return Init_Rcunittoomux_rc_windowresintance(msg_);
  }

private:
  ::smart_can_msgs::msg::Rcunittoomux msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Rcunittoomux>()
{
  return smart_can_msgs::msg::builder::Init_Rcunittoomux_autonomous_emergency();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__BUILDER_HPP_
