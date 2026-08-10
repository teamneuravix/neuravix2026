// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from smart_can_msgs:msg/Autonomousbrakepedalcontrol.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/autonomousbrakepedalcontrol__rosidl_typesupport_fastrtps_cpp.hpp"
#include "smart_can_msgs/msg/detail/autonomousbrakepedalcontrol__struct.hpp"

#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions

namespace smart_can_msgs
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
cdr_serialize(
  const smart_can_msgs::msg::Autonomousbrakepedalcontrol & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: autonomous_brakemotor_voltage
  cdr << ros_message.autonomous_brakemotor_voltage;
  // Member: autonomous_brakepedalmotor_per
  cdr << ros_message.autonomous_brakepedalmotor_per;
  // Member: autonomous_brakepedalmotor_acc
  cdr << ros_message.autonomous_brakepedalmotor_acc;
  // Member: autonomous_brakepedalmotor_en
  cdr << ros_message.autonomous_brakepedalmotor_en;
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  smart_can_msgs::msg::Autonomousbrakepedalcontrol & ros_message)
{
  // Member: autonomous_brakemotor_voltage
  cdr >> ros_message.autonomous_brakemotor_voltage;

  // Member: autonomous_brakepedalmotor_per
  cdr >> ros_message.autonomous_brakepedalmotor_per;

  // Member: autonomous_brakepedalmotor_acc
  cdr >> ros_message.autonomous_brakepedalmotor_acc;

  // Member: autonomous_brakepedalmotor_en
  cdr >> ros_message.autonomous_brakepedalmotor_en;

  return true;
}  // NOLINT(readability/fn_size)

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
get_serialized_size(
  const smart_can_msgs::msg::Autonomousbrakepedalcontrol & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: autonomous_brakemotor_voltage
  {
    size_t item_size = sizeof(ros_message.autonomous_brakemotor_voltage);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: autonomous_brakepedalmotor_per
  {
    size_t item_size = sizeof(ros_message.autonomous_brakepedalmotor_per);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: autonomous_brakepedalmotor_acc
  {
    size_t item_size = sizeof(ros_message.autonomous_brakepedalmotor_acc);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: autonomous_brakepedalmotor_en
  {
    size_t item_size = sizeof(ros_message.autonomous_brakepedalmotor_en);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
max_serialized_size_Autonomousbrakepedalcontrol(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;


  // Member: autonomous_brakemotor_voltage
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: autonomous_brakepedalmotor_per
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: autonomous_brakepedalmotor_acc
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }

  // Member: autonomous_brakepedalmotor_en
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = smart_can_msgs::msg::Autonomousbrakepedalcontrol;
    is_plain =
      (
      offsetof(DataType, autonomous_brakepedalmotor_en) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static bool _Autonomousbrakepedalcontrol__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const smart_can_msgs::msg::Autonomousbrakepedalcontrol *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _Autonomousbrakepedalcontrol__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<smart_can_msgs::msg::Autonomousbrakepedalcontrol *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _Autonomousbrakepedalcontrol__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const smart_can_msgs::msg::Autonomousbrakepedalcontrol *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _Autonomousbrakepedalcontrol__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_Autonomousbrakepedalcontrol(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _Autonomousbrakepedalcontrol__callbacks = {
  "smart_can_msgs::msg",
  "Autonomousbrakepedalcontrol",
  _Autonomousbrakepedalcontrol__cdr_serialize,
  _Autonomousbrakepedalcontrol__cdr_deserialize,
  _Autonomousbrakepedalcontrol__get_serialized_size,
  _Autonomousbrakepedalcontrol__max_serialized_size
};

static rosidl_message_type_support_t _Autonomousbrakepedalcontrol__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_Autonomousbrakepedalcontrol__callbacks,
  get_message_typesupport_handle_function,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace smart_can_msgs

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_smart_can_msgs
const rosidl_message_type_support_t *
get_message_type_support_handle<smart_can_msgs::msg::Autonomousbrakepedalcontrol>()
{
  return &smart_can_msgs::msg::typesupport_fastrtps_cpp::_Autonomousbrakepedalcontrol__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smart_can_msgs, msg, Autonomousbrakepedalcontrol)() {
  return &smart_can_msgs::msg::typesupport_fastrtps_cpp::_Autonomousbrakepedalcontrol__handle;
}

#ifdef __cplusplus
}
#endif
