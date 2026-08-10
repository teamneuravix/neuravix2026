// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Autonomoushbmotorcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/autonomoushbmotorcontrol__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Autonomoushbmotorcontrol_autonomous_hb_moten
{
public:
  explicit Init_Autonomoushbmotorcontrol_autonomous_hb_moten(::smart_can_msgs::msg::Autonomoushbmotorcontrol & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Autonomoushbmotorcontrol autonomous_hb_moten(::smart_can_msgs::msg::Autonomoushbmotorcontrol::_autonomous_hb_moten_type arg)
  {
    msg_.autonomous_hb_moten = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Autonomoushbmotorcontrol msg_;
};

class Init_Autonomoushbmotorcontrol_autonomous_hb_motstate
{
public:
  explicit Init_Autonomoushbmotorcontrol_autonomous_hb_motstate(::smart_can_msgs::msg::Autonomoushbmotorcontrol & msg)
  : msg_(msg)
  {}
  Init_Autonomoushbmotorcontrol_autonomous_hb_moten autonomous_hb_motstate(::smart_can_msgs::msg::Autonomoushbmotorcontrol::_autonomous_hb_motstate_type arg)
  {
    msg_.autonomous_hb_motstate = std::move(arg);
    return Init_Autonomoushbmotorcontrol_autonomous_hb_moten(msg_);
  }

private:
  ::smart_can_msgs::msg::Autonomoushbmotorcontrol msg_;
};

class Init_Autonomoushbmotorcontrol_autonomous_hb_motor_pwm
{
public:
  Init_Autonomoushbmotorcontrol_autonomous_hb_motor_pwm()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Autonomoushbmotorcontrol_autonomous_hb_motstate autonomous_hb_motor_pwm(::smart_can_msgs::msg::Autonomoushbmotorcontrol::_autonomous_hb_motor_pwm_type arg)
  {
    msg_.autonomous_hb_motor_pwm = std::move(arg);
    return Init_Autonomoushbmotorcontrol_autonomous_hb_motstate(msg_);
  }

private:
  ::smart_can_msgs::msg::Autonomoushbmotorcontrol msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Autonomoushbmotorcontrol>()
{
  return smart_can_msgs::msg::builder::Init_Autonomoushbmotorcontrol_autonomous_hb_motor_pwm();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__BUILDER_HPP_
