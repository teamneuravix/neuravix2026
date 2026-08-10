// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Autonomousheardbit.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHEARDBIT__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHEARDBIT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/autonomousheardbit__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Autonomousheardbit_autonomousmanuelselect
{
public:
  Init_Autonomousheardbit_autonomousmanuelselect()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smart_can_msgs::msg::Autonomousheardbit autonomousmanuelselect(::smart_can_msgs::msg::Autonomousheardbit::_autonomousmanuelselect_type arg)
  {
    msg_.autonomousmanuelselect = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Autonomousheardbit msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Autonomousheardbit>()
{
  return smart_can_msgs::msg::builder::Init_Autonomousheardbit_autonomousmanuelselect();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHEARDBIT__BUILDER_HPP_
