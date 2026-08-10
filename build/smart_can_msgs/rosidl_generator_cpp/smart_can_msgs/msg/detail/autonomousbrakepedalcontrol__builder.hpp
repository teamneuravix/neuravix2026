// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Autonomousbrakepedalcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSBRAKEPEDALCONTROL__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSBRAKEPEDALCONTROL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/autonomousbrakepedalcontrol__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_en
{
public:
  explicit Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_en(::smart_can_msgs::msg::Autonomousbrakepedalcontrol & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Autonomousbrakepedalcontrol autonomous_brakepedalmotor_en(::smart_can_msgs::msg::Autonomousbrakepedalcontrol::_autonomous_brakepedalmotor_en_type arg)
  {
    msg_.autonomous_brakepedalmotor_en = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Autonomousbrakepedalcontrol msg_;
};

class Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_acc
{
public:
  explicit Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_acc(::smart_can_msgs::msg::Autonomousbrakepedalcontrol & msg)
  : msg_(msg)
  {}
  Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_en autonomous_brakepedalmotor_acc(::smart_can_msgs::msg::Autonomousbrakepedalcontrol::_autonomous_brakepedalmotor_acc_type arg)
  {
    msg_.autonomous_brakepedalmotor_acc = std::move(arg);
    return Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_en(msg_);
  }

private:
  ::smart_can_msgs::msg::Autonomousbrakepedalcontrol msg_;
};

class Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_per
{
public:
  explicit Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_per(::smart_can_msgs::msg::Autonomousbrakepedalcontrol & msg)
  : msg_(msg)
  {}
  Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_acc autonomous_brakepedalmotor_per(::smart_can_msgs::msg::Autonomousbrakepedalcontrol::_autonomous_brakepedalmotor_per_type arg)
  {
    msg_.autonomous_brakepedalmotor_per = std::move(arg);
    return Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_acc(msg_);
  }

private:
  ::smart_can_msgs::msg::Autonomousbrakepedalcontrol msg_;
};

class Init_Autonomousbrakepedalcontrol_autonomous_brakemotor_voltage
{
public:
  Init_Autonomousbrakepedalcontrol_autonomous_brakemotor_voltage()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_per autonomous_brakemotor_voltage(::smart_can_msgs::msg::Autonomousbrakepedalcontrol::_autonomous_brakemotor_voltage_type arg)
  {
    msg_.autonomous_brakemotor_voltage = std::move(arg);
    return Init_Autonomousbrakepedalcontrol_autonomous_brakepedalmotor_per(msg_);
  }

private:
  ::smart_can_msgs::msg::Autonomousbrakepedalcontrol msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Autonomousbrakepedalcontrol>()
{
  return smart_can_msgs::msg::builder::Init_Autonomousbrakepedalcontrol_autonomous_brakemotor_voltage();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSBRAKEPEDALCONTROL__BUILDER_HPP_
