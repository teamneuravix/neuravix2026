// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from smart_can_msgs:msg/Feedbacksensor.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__TRAITS_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "smart_can_msgs/msg/detail/feedbacksensor__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace smart_can_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const Feedbacksensor & msg,
  std::ostream & out)
{
  out << "{";
  // member: steeringanglesensorhamdata
  {
    out << "steeringanglesensorhamdata: ";
    rosidl_generator_traits::value_to_yaml(msg.steeringanglesensorhamdata, out);
    out << ", ";
  }

  // member: brakepedalsensorhamdata
  {
    out << "brakepedalsensorhamdata: ";
    rosidl_generator_traits::value_to_yaml(msg.brakepedalsensorhamdata, out);
    out << ", ";
  }

  // member: handbrakesensor
  {
    out << "handbrakesensor: ";
    rosidl_generator_traits::value_to_yaml(msg.handbrakesensor, out);
    out << ", ";
  }

  // member: handbrakesensor_hamdata
  {
    out << "handbrakesensor_hamdata: ";
    rosidl_generator_traits::value_to_yaml(msg.handbrakesensor_hamdata, out);
    out << ", ";
  }

  // member: indir
  {
    out << "indir: ";
    rosidl_generator_traits::value_to_yaml(msg.indir, out);
    out << ", ";
  }

  // member: kaldir
  {
    out << "kaldir: ";
    rosidl_generator_traits::value_to_yaml(msg.kaldir, out);
    out << ", ";
  }

  // member: butonindir
  {
    out << "butonindir: ";
    rosidl_generator_traits::value_to_yaml(msg.butonindir, out);
    out << ", ";
  }

  // member: butonkaldir
  {
    out << "butonkaldir: ";
    rosidl_generator_traits::value_to_yaml(msg.butonkaldir, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Feedbacksensor & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: steeringanglesensorhamdata
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "steeringanglesensorhamdata: ";
    rosidl_generator_traits::value_to_yaml(msg.steeringanglesensorhamdata, out);
    out << "\n";
  }

  // member: brakepedalsensorhamdata
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "brakepedalsensorhamdata: ";
    rosidl_generator_traits::value_to_yaml(msg.brakepedalsensorhamdata, out);
    out << "\n";
  }

  // member: handbrakesensor
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "handbrakesensor: ";
    rosidl_generator_traits::value_to_yaml(msg.handbrakesensor, out);
    out << "\n";
  }

  // member: handbrakesensor_hamdata
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "handbrakesensor_hamdata: ";
    rosidl_generator_traits::value_to_yaml(msg.handbrakesensor_hamdata, out);
    out << "\n";
  }

  // member: indir
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "indir: ";
    rosidl_generator_traits::value_to_yaml(msg.indir, out);
    out << "\n";
  }

  // member: kaldir
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "kaldir: ";
    rosidl_generator_traits::value_to_yaml(msg.kaldir, out);
    out << "\n";
  }

  // member: butonindir
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "butonindir: ";
    rosidl_generator_traits::value_to_yaml(msg.butonindir, out);
    out << "\n";
  }

  // member: butonkaldir
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "butonkaldir: ";
    rosidl_generator_traits::value_to_yaml(msg.butonkaldir, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Feedbacksensor & msg, bool use_flow_style = false)
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
  const smart_can_msgs::msg::Feedbacksensor & msg,
  std::ostream & out, size_t indentation = 0)
{
  smart_can_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use smart_can_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const smart_can_msgs::msg::Feedbacksensor & msg)
{
  return smart_can_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<smart_can_msgs::msg::Feedbacksensor>()
{
  return "smart_can_msgs::msg::Feedbacksensor";
}

template<>
inline const char * name<smart_can_msgs::msg::Feedbacksensor>()
{
  return "smart_can_msgs/msg/Feedbacksensor";
}

template<>
struct has_fixed_size<smart_can_msgs::msg::Feedbacksensor>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<smart_can_msgs::msg::Feedbacksensor>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<smart_can_msgs::msg::Feedbacksensor>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__TRAITS_HPP_
