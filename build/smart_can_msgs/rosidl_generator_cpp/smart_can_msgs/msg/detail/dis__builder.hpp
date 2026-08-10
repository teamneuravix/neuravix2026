// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Dis.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__DIS__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__DIS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/dis__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Dis_angle
{
public:
  Init_Dis_angle()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::smart_can_msgs::msg::Dis angle(::smart_can_msgs::msg::Dis::_angle_type arg)
  {
    msg_.angle = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Dis msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Dis>()
{
  return smart_can_msgs::msg::builder::Init_Dis_angle();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__DIS__BUILDER_HPP_
