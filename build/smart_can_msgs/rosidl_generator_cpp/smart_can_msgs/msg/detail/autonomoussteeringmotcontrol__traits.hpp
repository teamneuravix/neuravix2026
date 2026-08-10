// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smart_can_msgs:msg/Autonomoussteeringmotcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__TRAITS_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smart_can_msgs/msg/detail/autonomoussteeringmotcontrol__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smart_can_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Autonomoussteeringmotcontrol & msg,
  std::ostream & out)
{
  out << "{";
  // member: autonomous_steeringmot_en
  {
    out << "autonomous_steeringmot_en: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_steeringmot_en, out);
    out << ", ";
  }

  // member: autonomous_steeringmot_pwm
  {
    out << "autonomous_steeringmot_pwm: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_steeringmot_pwm, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Autonomoussteeringmotcontrol & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: autonomous_steeringmot_en
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "autonomous_steeringmot_en: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_steeringmot_en, out);
    out << "\n";
  }

  // member: autonomous_steeringmot_pwm
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "autonomous_steeringmot_pwm: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_steeringmot_pwm, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Autonomoussteeringmotcontrol & msg, bool use_flow_style = false)
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
  const smart_can_msgs::msg::Autonomoussteeringmotcontrol & msg,
  std::ostream & out, size_t indentation = 0)
{
  smart_can_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smart_can_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smart_can_msgs::msg::Autonomoussteeringmotcontrol & msg)
{
  return smart_can_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smart_can_msgs::msg::Autonomoussteeringmotcontrol>()
{
  return "smart_can_msgs::msg::Autonomoussteeringmotcontrol";
}

template<>
inline const char * name<smart_can_msgs::msg::Autonomoussteeringmotcontrol>()
{
  return "smart_can_msgs/msg/Autonomoussteeringmotcontrol";
}

template<>
struct has_fixed_size<smart_can_msgs::msg::Autonomoussteeringmotcontrol>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smart_can_msgs::msg::Autonomoussteeringmotcontrol>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smart_can_msgs::msg::Autonomoussteeringmotcontrol>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__TRAITS_HPP_
