// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smart_can_msgs:msg/Autonomoushbmotorcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__TRAITS_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smart_can_msgs/msg/detail/autonomoushbmotorcontrol__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smart_can_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Autonomoushbmotorcontrol & msg,
  std::ostream & out)
{
  out << "{";
  // member: autonomous_hb_motor_pwm
  {
    out << "autonomous_hb_motor_pwm: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_hb_motor_pwm, out);
    out << ", ";
  }

  // member: autonomous_hb_motstate
  {
    out << "autonomous_hb_motstate: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_hb_motstate, out);
    out << ", ";
  }

  // member: autonomous_hb_moten
  {
    out << "autonomous_hb_moten: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_hb_moten, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Autonomoushbmotorcontrol & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: autonomous_hb_motor_pwm
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "autonomous_hb_motor_pwm: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_hb_motor_pwm, out);
    out << "\n";
  }

  // member: autonomous_hb_motstate
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "autonomous_hb_motstate: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_hb_motstate, out);
    out << "\n";
  }

  // member: autonomous_hb_moten
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "autonomous_hb_moten: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_hb_moten, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Autonomoushbmotorcontrol & msg, bool use_flow_style = false)
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
  const smart_can_msgs::msg::Autonomoushbmotorcontrol & msg,
  std::ostream & out, size_t indentation = 0)
{
  smart_can_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smart_can_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smart_can_msgs::msg::Autonomoushbmotorcontrol & msg)
{
  return smart_can_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smart_can_msgs::msg::Autonomoushbmotorcontrol>()
{
  return "smart_can_msgs::msg::Autonomoushbmotorcontrol";
}

template<>
inline const char * name<smart_can_msgs::msg::Autonomoushbmotorcontrol>()
{
  return "smart_can_msgs/msg/Autonomoushbmotorcontrol";
}

template<>
struct has_fixed_size<smart_can_msgs::msg::Autonomoushbmotorcontrol>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smart_can_msgs::msg::Autonomoushbmotorcontrol>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smart_can_msgs::msg::Autonomoushbmotorcontrol>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__TRAITS_HPP_
