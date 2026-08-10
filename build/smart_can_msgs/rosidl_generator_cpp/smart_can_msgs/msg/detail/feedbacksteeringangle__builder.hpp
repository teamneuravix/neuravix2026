// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Feedbacksteeringangle.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/feedbacksteeringangle__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Feedbacksteeringangle_feedbackbrakepedalangle
{
public:
  explicit Init_Feedbacksteeringangle_feedbackbrakepedalangle(::smart_can_msgs::msg::Feedbacksteeringangle & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Feedbacksteeringangle feedbackbrakepedalangle(::smart_can_msgs::msg::Feedbacksteeringangle::_feedbackbrakepedalangle_type arg)
  {
    msg_.feedbackbrakepedalangle = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Feedbacksteeringangle msg_;
};

class Init_Feedbacksteeringangle_feedbacksteeringangle
{
public:
  Init_Feedbacksteeringangle_feedbacksteeringangle()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Feedbacksteeringangle_feedbackbrakepedalangle feedbacksteeringangle(::smart_can_msgs::msg::Feedbacksteeringangle::_feedbacksteeringangle_type arg)
  {
    msg_.feedbacksteeringangle = std::move(arg);
    return Init_Feedbacksteeringangle_feedbackbrakepedalangle(msg_);
  }

private:
  ::smart_can_msgs::msg::Feedbacksteeringangle msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Feedbacksteeringangle>()
{
  return smart_can_msgs::msg::builder::Init_Feedbacksteeringangle_feedbacksteeringangle();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__BUILDER_HPP_
