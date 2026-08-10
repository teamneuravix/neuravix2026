// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smart_can_msgs:msg/Rcunittoomux.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__TRAITS_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smart_can_msgs/msg/detail/rcunittoomux__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smart_can_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Rcunittoomux & msg,
  std::ostream & out)
{
  out << "{";
  // member: autonomous_emergency
  {
    out << "autonomous_emergency: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_emergency, out);
    out << ", ";
  }

  // member: rc_windowresintance
  {
    out << "rc_windowresintance: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_windowresintance, out);
    out << ", ";
  }

  // member: rc_interiorlight
  {
    out << "rc_interiorlight: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_interiorlight, out);
    out << ", ";
  }

  // member: rc_reverselight
  {
    out << "rc_reverselight: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_reverselight, out);
    out << ", ";
  }

  // member: rc_drl
  {
    out << "rc_drl: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_drl, out);
    out << ", ";
  }

  // member: rc_brakelight
  {
    out << "rc_brakelight: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_brakelight, out);
    out << ", ";
  }

  // member: autonomous_door_open
  {
    out << "autonomous_door_open: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_door_open, out);
    out << ", ";
  }

  // member: autonomous_door_close
  {
    out << "autonomous_door_close: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_door_close, out);
    out << ", ";
  }

  // member: rc_signalstatus
  {
    out << "rc_signalstatus: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_signalstatus, out);
    out << ", ";
  }

  // member: rc_lowbeam
  {
    out << "rc_lowbeam: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_lowbeam, out);
    out << ", ";
  }

  // member: rc_highbeam
  {
    out << "rc_highbeam: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_highbeam, out);
    out << ", ";
  }

  // member: rc_selectiongear
  {
    out << "rc_selectiongear: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_selectiongear, out);
    out << ", ";
  }

  // member: rc_ignition
  {
    out << "rc_ignition: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_ignition, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Rcunittoomux & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: autonomous_emergency
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "autonomous_emergency: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_emergency, out);
    out << "\n";
  }

  // member: rc_windowresintance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rc_windowresintance: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_windowresintance, out);
    out << "\n";
  }

  // member: rc_interiorlight
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rc_interiorlight: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_interiorlight, out);
    out << "\n";
  }

  // member: rc_reverselight
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rc_reverselight: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_reverselight, out);
    out << "\n";
  }

  // member: rc_drl
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rc_drl: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_drl, out);
    out << "\n";
  }

  // member: rc_brakelight
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rc_brakelight: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_brakelight, out);
    out << "\n";
  }

  // member: autonomous_door_open
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "autonomous_door_open: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_door_open, out);
    out << "\n";
  }

  // member: autonomous_door_close
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "autonomous_door_close: ";
    rosidl_generator_traits::value_to_yaml(msg.autonomous_door_close, out);
    out << "\n";
  }

  // member: rc_signalstatus
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rc_signalstatus: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_signalstatus, out);
    out << "\n";
  }

  // member: rc_lowbeam
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rc_lowbeam: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_lowbeam, out);
    out << "\n";
  }

  // member: rc_highbeam
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rc_highbeam: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_highbeam, out);
    out << "\n";
  }

  // member: rc_selectiongear
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rc_selectiongear: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_selectiongear, out);
    out << "\n";
  }

  // member: rc_ignition
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rc_ignition: ";
    rosidl_generator_traits::value_to_yaml(msg.rc_ignition, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Rcunittoomux & msg, bool use_flow_style = false)
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
  const smart_can_msgs::msg::Rcunittoomux & msg,
  std::ostream & out, size_t indentation = 0)
{
  smart_can_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smart_can_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smart_can_msgs::msg::Rcunittoomux & msg)
{
  return smart_can_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smart_can_msgs::msg::Rcunittoomux>()
{
  return "smart_can_msgs::msg::Rcunittoomux";
}

template<>
inline const char * name<smart_can_msgs::msg::Rcunittoomux>()
{
  return "smart_can_msgs/msg/Rcunittoomux";
}

template<>
struct has_fixed_size<smart_can_msgs::msg::Rcunittoomux>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smart_can_msgs::msg::Rcunittoomux>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smart_can_msgs::msg::Rcunittoomux>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__TRAITS_HPP_
