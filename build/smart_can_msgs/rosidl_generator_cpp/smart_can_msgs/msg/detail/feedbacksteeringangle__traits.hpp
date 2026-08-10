// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smart_can_msgs:msg/Feedbacksteeringangle.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__TRAITS_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smart_can_msgs/msg/detail/feedbacksteeringangle__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smart_can_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Feedbacksteeringangle & msg,
  std::ostream & out)
{
  out << "{";
  // member: feedbacksteeringangle
  {
    out << "feedbacksteeringangle: ";
    rosidl_generator_traits::value_to_yaml(msg.feedbacksteeringangle, out);
    out << ", ";
  }

  // member: feedbackbrakepedalangle
  {
    out << "feedbackbrakepedalangle: ";
    rosidl_generator_traits::value_to_yaml(msg.feedbackbrakepedalangle, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Feedbacksteeringangle & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: feedbacksteeringangle
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "feedbacksteeringangle: ";
    rosidl_generator_traits::value_to_yaml(msg.feedbacksteeringangle, out);
    out << "\n";
  }

  // member: feedbackbrakepedalangle
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "feedbackbrakepedalangle: ";
    rosidl_generator_traits::value_to_yaml(msg.feedbackbrakepedalangle, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Feedbacksteeringangle & msg, bool use_flow_style = false)
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
  const smart_can_msgs::msg::Feedbacksteeringangle & msg,
  std::ostream & out, size_t indentation = 0)
{
  smart_can_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smart_can_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smart_can_msgs::msg::Feedbacksteeringangle & msg)
{
  return smart_can_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smart_can_msgs::msg::Feedbacksteeringangle>()
{
  return "smart_can_msgs::msg::Feedbacksteeringangle";
}

template<>
inline const char * name<smart_can_msgs::msg::Feedbacksteeringangle>()
{
  return "smart_can_msgs/msg/Feedbacksteeringangle";
}

template<>
struct has_fixed_size<smart_can_msgs::msg::Feedbacksteeringangle>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smart_can_msgs::msg::Feedbacksteeringangle>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smart_can_msgs::msg::Feedbacksteeringangle>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__TRAITS_HPP_
