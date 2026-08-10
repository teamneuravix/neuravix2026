// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Fbvehiclespeed.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/fbvehiclespeed__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Fbvehiclespeed_fb_reelvehiclespeed_ms
{
public:
  explicit Init_Fbvehiclespeed_fb_reelvehiclespeed_ms(::smart_can_msgs::msg::Fbvehiclespeed & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Fbvehiclespeed fb_reelvehiclespeed_ms(::smart_can_msgs::msg::Fbvehiclespeed::_fb_reelvehiclespeed_ms_type arg)
  {
    msg_.fb_reelvehiclespeed_ms = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbvehiclespeed msg_;
};

class Init_Fbvehiclespeed_fb_reelvehiclespeed_kmh
{
public:
  explicit Init_Fbvehiclespeed_fb_reelvehiclespeed_kmh(::smart_can_msgs::msg::Fbvehiclespeed & msg)
  : msg_(msg)
  {}
  Init_Fbvehiclespeed_fb_reelvehiclespeed_ms fb_reelvehiclespeed_kmh(::smart_can_msgs::msg::Fbvehiclespeed::_fb_reelvehiclespeed_kmh_type arg)
  {
    msg_.fb_reelvehiclespeed_kmh = std::move(arg);
    return Init_Fbvehiclespeed_fb_reelvehiclespeed_ms(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbvehiclespeed msg_;
};

class Init_Fbvehiclespeed_fb_vehiclespeed_kmh
{
public:
  Init_Fbvehiclespeed_fb_vehiclespeed_kmh()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Fbvehiclespeed_fb_reelvehiclespeed_kmh fb_vehiclespeed_kmh(::smart_can_msgs::msg::Fbvehiclespeed::_fb_vehiclespeed_kmh_type arg)
  {
    msg_.fb_vehiclespeed_kmh = std::move(arg);
    return Init_Fbvehiclespeed_fb_reelvehiclespeed_kmh(msg_);
  }

private:
  ::smart_can_msgs::msg::Fbvehiclespeed msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Fbvehiclespeed>()
{
  return smart_can_msgs::msg::builder::Init_Fbvehiclespeed_fb_vehiclespeed_kmh();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__BUILDER_HPP_
