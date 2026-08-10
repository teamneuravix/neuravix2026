// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smart_can_msgs:msg/Fbomuxtoautonomous.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__TRAITS_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smart_can_msgs/msg/detail/fbomuxtoautonomous__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smart_can_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Fbomuxtoautonomous & msg,
  std::ostream & out)
{
  out << "{";
  // member: fb_emergency
  {
    out << "fb_emergency: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_emergency, out);
    out << ", ";
  }

  // member: fb_reverselight
  {
    out << "fb_reverselight: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_reverselight, out);
    out << ", ";
  }

  // member: fb_rightsignal
  {
    out << "fb_rightsignal: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_rightsignal, out);
    out << ", ";
  }

  // member: fb_windowresistance
  {
    out << "fb_windowresistance: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_windowresistance, out);
    out << ", ";
  }

  // member: fb_leftsignal
  {
    out << "fb_leftsignal: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_leftsignal, out);
    out << ", ";
  }

  // member: fb_interiorlight
  {
    out << "fb_interiorlight: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_interiorlight, out);
    out << ", ";
  }

  // member: fb_drl
  {
    out << "fb_drl: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_drl, out);
    out << ", ";
  }

  // member: fb_doorkeystatus
  {
    out << "fb_doorkeystatus: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_doorkeystatus, out);
    out << ", ";
  }

  // member: fb_brakelight
  {
    out << "fb_brakelight: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_brakelight, out);
    out << ", ";
  }

  // member: fb_batteryvoltage
  {
    out << "fb_batteryvoltage: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_batteryvoltage, out);
    out << ", ";
  }

  // member: fb_chargeinput
  {
    out << "fb_chargeinput: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_chargeinput, out);
    out << ", ";
  }

  // member: fb_highbeam
  {
    out << "fb_highbeam: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_highbeam, out);
    out << ", ";
  }

  // member: fb_lowbeam
  {
    out << "fb_lowbeam: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_lowbeam, out);
    out << ", ";
  }

  // member: fb_ignition
  {
    out << "fb_ignition: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_ignition, out);
    out << ", ";
  }

  // member: fb_hazardouslight
  {
    out << "fb_hazardouslight: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_hazardouslight, out);
    out << ", ";
  }

  // member: fb_vehiclestatus
  {
    out << "fb_vehiclestatus: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_vehiclestatus, out);
    out << ", ";
  }

  // member: fb_leftdoorstatus
  {
    out << "fb_leftdoorstatus: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_leftdoorstatus, out);
    out << ", ";
  }

  // member: fb_rightdoorstatus
  {
    out << "fb_rightdoorstatus: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_rightdoorstatus, out);
    out << ", ";
  }

  // member: fb_batterysoc
  {
    out << "fb_batterysoc: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_batterysoc, out);
    out << ", ";
  }

  // member: fb_errorpowertrain
  {
    out << "fb_errorpowertrain: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_errorpowertrain, out);
    out << ", ";
  }

  // member: fb_errorbattery
  {
    out << "fb_errorbattery: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_errorbattery, out);
    out << ", ";
  }

  // member: fb_brakepedal_voltage_en
  {
    out << "fb_brakepedal_voltage_en: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_brakepedal_voltage_en, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Fbomuxtoautonomous & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: fb_emergency
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_emergency: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_emergency, out);
    out << "\n";
  }

  // member: fb_reverselight
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_reverselight: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_reverselight, out);
    out << "\n";
  }

  // member: fb_rightsignal
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_rightsignal: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_rightsignal, out);
    out << "\n";
  }

  // member: fb_windowresistance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_windowresistance: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_windowresistance, out);
    out << "\n";
  }

  // member: fb_leftsignal
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_leftsignal: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_leftsignal, out);
    out << "\n";
  }

  // member: fb_interiorlight
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_interiorlight: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_interiorlight, out);
    out << "\n";
  }

  // member: fb_drl
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_drl: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_drl, out);
    out << "\n";
  }

  // member: fb_doorkeystatus
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_doorkeystatus: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_doorkeystatus, out);
    out << "\n";
  }

  // member: fb_brakelight
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_brakelight: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_brakelight, out);
    out << "\n";
  }

  // member: fb_batteryvoltage
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_batteryvoltage: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_batteryvoltage, out);
    out << "\n";
  }

  // member: fb_chargeinput
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_chargeinput: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_chargeinput, out);
    out << "\n";
  }

  // member: fb_highbeam
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_highbeam: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_highbeam, out);
    out << "\n";
  }

  // member: fb_lowbeam
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_lowbeam: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_lowbeam, out);
    out << "\n";
  }

  // member: fb_ignition
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_ignition: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_ignition, out);
    out << "\n";
  }

  // member: fb_hazardouslight
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_hazardouslight: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_hazardouslight, out);
    out << "\n";
  }

  // member: fb_vehiclestatus
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_vehiclestatus: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_vehiclestatus, out);
    out << "\n";
  }

  // member: fb_leftdoorstatus
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_leftdoorstatus: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_leftdoorstatus, out);
    out << "\n";
  }

  // member: fb_rightdoorstatus
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_rightdoorstatus: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_rightdoorstatus, out);
    out << "\n";
  }

  // member: fb_batterysoc
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_batterysoc: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_batterysoc, out);
    out << "\n";
  }

  // member: fb_errorpowertrain
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_errorpowertrain: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_errorpowertrain, out);
    out << "\n";
  }

  // member: fb_errorbattery
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_errorbattery: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_errorbattery, out);
    out << "\n";
  }

  // member: fb_brakepedal_voltage_en
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "fb_brakepedal_voltage_en: ";
    rosidl_generator_traits::value_to_yaml(msg.fb_brakepedal_voltage_en, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Fbomuxtoautonomous & msg, bool use_flow_style = false)
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
  const smart_can_msgs::msg::Fbomuxtoautonomous & msg,
  std::ostream & out, size_t indentation = 0)
{
  smart_can_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smart_can_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smart_can_msgs::msg::Fbomuxtoautonomous & msg)
{
  return smart_can_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smart_can_msgs::msg::Fbomuxtoautonomous>()
{
  return "smart_can_msgs::msg::Fbomuxtoautonomous";
}

template<>
inline const char * name<smart_can_msgs::msg::Fbomuxtoautonomous>()
{
  return "smart_can_msgs/msg/Fbomuxtoautonomous";
}

template<>
struct has_fixed_size<smart_can_msgs::msg::Fbomuxtoautonomous>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smart_can_msgs::msg::Fbomuxtoautonomous>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smart_can_msgs::msg::Fbomuxtoautonomous>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__TRAITS_HPP_
