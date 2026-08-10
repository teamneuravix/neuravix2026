// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smart_can_msgs:msg/Fbvehiclespeed.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__TRAITS_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smart_can_msgs/msg/detail/fbvehiclespeed__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smart_can_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Fbvehiclespeed & msg,
  std::ostream & out)
{
  out << "{";
  // member: fb_vehiclespeed_kmh
  {
    out << "fb_vehiclespeed_kmh: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_vehiclespeed_kmh, out);
    out << ", ";
  }

  // member: fb_reelvehiclespeed_kmh
  {
    out << "fb_reelvehiclespeed_kmh: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_reelvehiclespeed_kmh, out);
    out << ", ";
  }

  // member: fb_reelvehiclespeed_ms
  {
    out << "fb_reelvehiclespeed_ms: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_reelvehiclespeed_ms, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Fbvehiclespeed & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: fb_vehiclespeed_kmh
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_vehiclespeed_kmh: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_vehiclespeed_kmh, out);
    out << "\n";
  }

  // member: fb_reelvehiclespeed_kmh
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_reelvehiclespeed_kmh: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_reelvehiclespeed_kmh, out);
    out << "\n";
  }

  // member: fb_reelvehiclespeed_ms
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_reelvehiclespeed_ms: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_reelvehiclespeed_ms, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Fbvehiclespeed & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace smart_can_msgs

namespace rosidl_generator_traits
{

[[deprecated("use smart_can_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const smart_can_msgs::msg::Fbvehiclespeed & msg,
  std::ostream & out, size_t indentation = 0)
{
  smart_can_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smart_can_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smart_can_msgs::msg::Fbvehiclespeed & msg)
{
  return smart_can_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smart_can_msgs::msg::Fbvehiclespeed>()
{
  return "smart_can_msgs::msg::Fbvehiclespeed";
}

template<>
inline const char * name<smart_can_msgs::msg::Fbvehiclespeed>()
{
  return "smart_can_msgs/msg/Fbvehiclespeed";
}

template<>
struct has_fixed_size<smart_can_msgs::msg::Fbvehiclespeed>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smart_can_msgs::msg::Fbvehiclespeed>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smart_can_msgs::msg::Fbvehiclespeed>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__TRAITS_HPP_
