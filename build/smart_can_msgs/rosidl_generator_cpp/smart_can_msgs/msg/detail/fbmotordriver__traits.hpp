// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smart_can_msgs:msg/Fbmotordriver.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__TRAITS_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smart_can_msgs/msg/detail/fbmotordriver__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smart_can_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Fbmotordriver & msg,
  std::ostream & out)
{
  out << "{";
  // member: gear_status_from_motor
  {
    out << "gear_status_from_motor: ";
    rosidl_generator_traits::value_to_yaml(msg.gear_status_from_motor, out);
    out << ", ";
  }

  // member: plustripdistance
  {
    out << "plustripdistance: ";
    rosidl_generator_traits::value_to_yaml(msg.plustripdistance, out);
    out << ", ";
  }

  // member: vehiclerpm
  {
    out << "vehiclerpm: ";
    rosidl_generator_traits::value_to_yaml(msg.vehiclerpm, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Fbmotordriver & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: gear_status_from_motor
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "gear_status_from_motor: ";
    rosidl_generator_traits::value_to_yaml(msg.gear_status_from_motor, out);
    out << "\n";
  }

  // member: plustripdistance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "plustripdistance: ";
    rosidl_generator_traits::value_to_yaml(msg.plustripdistance, out);
    out << "\n";
  }

  // member: vehiclerpm
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "vehiclerpm: ";
    rosidl_generator_traits::value_to_yaml(msg.vehiclerpm, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Fbmotordriver & msg, bool use_flow_style = false)
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
  const smart_can_msgs::msg::Fbmotordriver & msg,
  std::ostream & out, size_t indentation = 0)
{
  smart_can_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smart_can_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smart_can_msgs::msg::Fbmotordriver & msg)
{
  return smart_can_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smart_can_msgs::msg::Fbmotordriver>()
{
  return "smart_can_msgs::msg::Fbmotordriver";
}

template<>
inline const char * name<smart_can_msgs::msg::Fbmotordriver>()
{
  return "smart_can_msgs/msg/Fbmotordriver";
}

template<>
struct has_fixed_size<smart_can_msgs::msg::Fbmotordriver>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smart_can_msgs::msg::Fbmotordriver>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smart_can_msgs::msg::Fbmotordriver>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__TRAITS_HPP_
