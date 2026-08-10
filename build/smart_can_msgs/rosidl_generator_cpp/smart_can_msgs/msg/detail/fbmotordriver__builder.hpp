// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Fbmotordriver.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/fbmotordriver__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Fbmotordriver_vehiclerpm
{
public:
  explicit Init_Fbmotordriver_vehiclerpm(::smart_can_msgs::msg::Fbmotordriver & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Fbmotordriver vehiclerpm(::smart_can_msgs::msg::Fbmotordriver::_vehiclerpm_type arg)
  {
    msg_.vehiclerpm = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbmotordriver msg_;
};

class Init_Fbmotordriver_plustripdistance
{
public:
  explicit Init_Fbmotordriver_plustripdistance(::smart_can_msgs::msg::Fbmotordriver & msg)
  : msg_(msg)
  {}
  Init_Fbmotordriver_vehiclerpm plustripdistance(::smart_can_msgs::msg::Fbmotordriver::_plustripdistance_type arg)
  {
    msg_.plustripdistance = std::move(arg);
    return Init_Fbmotordriver_vehiclerpm(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbmotordriver msg_;
};

class Init_Fbmotordriver_gear_status_from_motor
{
public:
  Init_Fbmotordriver_gear_status_from_motor()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Fbmotordriver_plustripdistance gear_status_from_motor(::smart_can_msgs::msg::Fbmotordriver::_gear_status_from_motor_type arg)
  {
    msg_.gear_status_from_motor = std::move(arg);
    return Init_Fbmotordriver_plustripdistance(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbmotordriver msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Fbmotordriver>()
{
  return smart_can_msgs::msg::builder::Init_Fbmotordriver_gear_status_from_motor();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__BUILDER_HPP_
