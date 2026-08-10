// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smart_can_msgs:msg/Kinematicmessages.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__KINEMATICMESSAGES__TRAITS_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__KINEMATICMESSAGES__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smart_can_msgs/msg/detail/kinematicmessages__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smart_can_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Kinematicmessages & msg,
  std::ostream & out)
{
  out << "{";
  // member: joint_type
  {
    out << "joint_type: ";
    rosidl_generator_traits::value_to_yaml(msg.joint_type, out);
    out << ", ";
  }

  // member: angle
  {
    out << "angle: ";
    rosidl_generator_traits::value_to_yaml(msg.angle, out);
    out << ", ";
  }

  // member: angle_y
  {
    out << "angle_y: ";
    rosidl_generator_traits::value_to_yaml(msg.angle_y, out);
    out << ", ";
  }

  // member: angular_velocity
  {
    out << "angular_velocity: ";
    rosidl_generator_traits::value_to_yaml(msg.angular_velocity, out);
    out << ", ";
  }

  // member: link_length
  {
    out << "link_length: ";
    rosidl_generator_traits::value_to_yaml(msg.link_length, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Kinematicmessages & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: joint_type
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "joint_type: ";
    rosidl_generator_traits::value_to_yaml(msg.joint_type, out);
    out << "\n";
  }

  // member: angle
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "angle: ";
    rosidl_generator_traits::value_to_yaml(msg.angle, out);
    out << "\n";
  }

  // member: angle_y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "angle_y: ";
    rosidl_generator_traits::value_to_yaml(msg.angle_y, out);
    out << "\n";
  }

  // member: angular_velocity
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "angular_velocity: ";
    rosidl_generator_traits::value_to_yaml(msg.angular_velocity, out);
    out << "\n";
  }

  // member: link_length
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "link_length: ";
    rosidl_generator_traits::value_to_yaml(msg.link_length, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Kinematicmessages & msg, bool use_flow_style = false)
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
  const smart_can_msgs::msg::Kinematicmessages & msg,
  std::ostream & out, size_t indentation = 0)
{
  smart_can_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smart_can_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smart_can_msgs::msg::Kinematicmessages & msg)
{
  return smart_can_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smart_can_msgs::msg::Kinematicmessages>()
{
  return "smart_can_msgs::msg::Kinematicmessages";
}

template<>
inline const char * name<smart_can_msgs::msg::Kinematicmessages>()
{
  return "smart_can_msgs/msg/Kinematicmessages";
}

template<>
struct has_fixed_size<smart_can_msgs::msg::Kinematicmessages>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smart_can_msgs::msg::Kinematicmessages>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smart_can_msgs::msg::Kinematicmessages>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMART_CAN_MSGS__MSG__DETAIL__KINEMATICMESSAGES__TRAITS_HPP_
