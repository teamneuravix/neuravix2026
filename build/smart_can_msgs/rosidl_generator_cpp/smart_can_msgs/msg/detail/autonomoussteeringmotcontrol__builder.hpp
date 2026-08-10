// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Autonomoussteeringmotcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/autonomoussteeringmotcontrol__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Autonomoussteeringmotcontrol_autonomous_steeringmot_pwm
{
public:
  explicit Init_Autonomoussteeringmotcontrol_autonomous_steeringmot_pwm(::smart_can_msgs::msg::Autonomoussteeringmotcontrol & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Autonomoussteeringmotcontrol autonomous_steeringmot_pwm(::smart_can_msgs::msg::Autonomoussteeringmotcontrol::_autonomous_steeringmot_pwm_type arg)
  {
    msg_.autonomous_steeringmot_pwm = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Autonomoussteeringmotcontrol msg_;
};

class Init_Autonomoussteeringmotcontrol_autonomous_steeringmot_en
{
public:
  Init_Autonomoussteeringmotcontrol_autonomous_steeringmot_en()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Autonomoussteeringmotcontrol_autonomous_steeringmot_pwm autonomous_steeringmot_en(::smart_can_msgs::msg::Autonomoussteeringmotcontrol::_autonomous_steeringmot_en_type arg)
  {
    msg_.autonomous_steeringmot_en = std::move(arg);
    return Init_Autonomoussteeringmotcontrol_autonomous_steeringmot_pwm(msg_);
  }

private:
  ::smart_can_msgs::msg::Autonomoussteeringmotcontrol msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Autonomoussteeringmotcontrol>()
{
  return smart_can_msgs::msg::builder::Init_Autonomoussteeringmotcontrol_autonomous_steeringmot_en();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__BUILDER_HPP_
