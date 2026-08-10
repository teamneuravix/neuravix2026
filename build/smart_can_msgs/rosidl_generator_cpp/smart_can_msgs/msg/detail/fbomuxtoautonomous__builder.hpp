// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Fbomuxtoautonomous.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/fbomuxtoautonomous__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Fbomuxtoautonomous_fb_brakepedal_voltage_en
{
public:
  explicit Init_Fbomuxtoautonomous_fb_brakepedal_voltage_en(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Fbomuxtoautonomous fb_brakepedal_voltage_en(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_brakepedal_voltage_en_type arg)
  {
    msg_.fb_brakepedal_voltage_en = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_errorbattery
{
public:
  explicit Init_Fbomuxtoautonomous_fb_errorbattery(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_brakepedal_voltage_en fb_errorbattery(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_errorbattery_type arg)
  {
    msg_.fb_errorbattery = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_brakepedal_voltage_en(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_errorpowertrain
{
public:
  explicit Init_Fbomuxtoautonomous_fb_errorpowertrain(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_errorbattery fb_errorpowertrain(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_errorpowertrain_type arg)
  {
    msg_.fb_errorpowertrain = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_errorbattery(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_batterysoc
{
public:
  explicit Init_Fbomuxtoautonomous_fb_batterysoc(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_errorpowertrain fb_batterysoc(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_batterysoc_type arg)
  {
    msg_.fb_batterysoc = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_errorpowertrain(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_rightdoorstatus
{
public:
  explicit Init_Fbomuxtoautonomous_fb_rightdoorstatus(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_batterysoc fb_rightdoorstatus(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_rightdoorstatus_type arg)
  {
    msg_.fb_rightdoorstatus = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_batterysoc(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_leftdoorstatus
{
public:
  explicit Init_Fbomuxtoautonomous_fb_leftdoorstatus(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_rightdoorstatus fb_leftdoorstatus(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_leftdoorstatus_type arg)
  {
    msg_.fb_leftdoorstatus = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_rightdoorstatus(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_vehiclestatus
{
public:
  explicit Init_Fbomuxtoautonomous_fb_vehiclestatus(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_leftdoorstatus fb_vehiclestatus(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_vehiclestatus_type arg)
  {
    msg_.fb_vehiclestatus = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_leftdoorstatus(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_hazardouslight
{
public:
  explicit Init_Fbomuxtoautonomous_fb_hazardouslight(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_vehiclestatus fb_hazardouslight(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_hazardouslight_type arg)
  {
    msg_.fb_hazardouslight = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_vehiclestatus(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_ignition
{
public:
  explicit Init_Fbomuxtoautonomous_fb_ignition(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_hazardouslight fb_ignition(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_ignition_type arg)
  {
    msg_.fb_ignition = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_hazardouslight(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_lowbeam
{
public:
  explicit Init_Fbomuxtoautonomous_fb_lowbeam(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_ignition fb_lowbeam(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_lowbeam_type arg)
  {
    msg_.fb_lowbeam = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_ignition(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_highbeam
{
public:
  explicit Init_Fbomuxtoautonomous_fb_highbeam(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_lowbeam fb_highbeam(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_highbeam_type arg)
  {
    msg_.fb_highbeam = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_lowbeam(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_chargeinput
{
public:
  explicit Init_Fbomuxtoautonomous_fb_chargeinput(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_highbeam fb_chargeinput(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_chargeinput_type arg)
  {
    msg_.fb_chargeinput = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_highbeam(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_batteryvoltage
{
public:
  explicit Init_Fbomuxtoautonomous_fb_batteryvoltage(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_chargeinput fb_batteryvoltage(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_batteryvoltage_type arg)
  {
    msg_.fb_batteryvoltage = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_chargeinput(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_brakelight
{
public:
  explicit Init_Fbomuxtoautonomous_fb_brakelight(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_batteryvoltage fb_brakelight(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_brakelight_type arg)
  {
    msg_.fb_brakelight = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_batteryvoltage(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_doorkeystatus
{
public:
  explicit Init_Fbomuxtoautonomous_fb_doorkeystatus(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_brakelight fb_doorkeystatus(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_doorkeystatus_type arg)
  {
    msg_.fb_doorkeystatus = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_brakelight(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_drl
{
public:
  explicit Init_Fbomuxtoautonomous_fb_drl(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_doorkeystatus fb_drl(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_drl_type arg)
  {
    msg_.fb_drl = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_doorkeystatus(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_interiorlight
{
public:
  explicit Init_Fbomuxtoautonomous_fb_interiorlight(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_drl fb_interiorlight(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_interiorlight_type arg)
  {
    msg_.fb_interiorlight = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_drl(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_leftsignal
{
public:
  explicit Init_Fbomuxtoautonomous_fb_leftsignal(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_interiorlight fb_leftsignal(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_leftsignal_type arg)
  {
    msg_.fb_leftsignal = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_interiorlight(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_windowresistance
{
public:
  explicit Init_Fbomuxtoautonomous_fb_windowresistance(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_leftsignal fb_windowresistance(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_windowresistance_type arg)
  {
    msg_.fb_windowresistance = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_leftsignal(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_rightsignal
{
public:
  explicit Init_Fbomuxtoautonomous_fb_rightsignal(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_windowresistance fb_rightsignal(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_rightsignal_type arg)
  {
    msg_.fb_rightsignal = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_windowresistance(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_reverselight
{
public:
  explicit Init_Fbomuxtoautonomous_fb_reverselight(::smart_can_msgs::msg::Fbomuxtoautonomous & msg)
  : msg_(msg)
  {}
  Init_Fbomuxtoautonomous_fb_rightsignal fb_reverselight(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_reverselight_type arg)
  {
    msg_.fb_reverselight = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_rightsignal(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

class Init_Fbomuxtoautonomous_fb_emergency
{
public:
  Init_Fbomuxtoautonomous_fb_emergency()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Fbomuxtoautonomous_fb_reverselight fb_emergency(::smart_can_msgs::msg::Fbomuxtoautonomous::_fb_emergency_type arg)
  {
    msg_.fb_emergency = std::move(arg);
    return Init_Fbomuxtoautonomous_fb_reverselight(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbomuxtoautonomous msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Fbomuxtoautonomous>()
{
  return smart_can_msgs::msg::builder::Init_Fbomuxtoautonomous_fb_emergency();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__BUILDER_HPP_
