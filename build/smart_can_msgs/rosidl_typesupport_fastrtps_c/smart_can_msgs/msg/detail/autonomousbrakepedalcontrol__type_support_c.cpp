// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from smart_can_msgs:msg/Autonomousbrakepedalcontrol.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/autonomousbrakepedalcontrol__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "smart_can_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "smart_can_msgs/msg/detail/autonomousbrakepedalcontrol__struct.h"
#include "smart_can_msgs/msg/detail/autonomousbrakepedalcontrol__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif


// forward declare type support functions


using _Autonomousbrakepedalcontrol__ros_msg_type = smart_can_msgs__msg__Autonomousbrakepedalcontrol;

static bool _Autonomousbrakepedalcontrol__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Autonomousbrakepedalcontrol__ros_msg_type * ros_message = static_cast<const _Autonomousbrakepedalcontrol__ros_msg_type *>(untyped_ros_message);
  // Field name: autonomous_brakemotor_voltage
  {
    cdr << ros_message->autonomous_brakemotor_voltage;
  }

  // Field name: autonomous_brakepedalmotor_per
  {
    cdr << ros_message->autonomous_brakepedalmotor_per;
  }

  // Field name: autonomous_brakepedalmotor_acc
  {
    cdr << ros_message->autonomous_brakepedalmotor_acc;
  }

  // Field name: autonomous_brakepedalmotor_en
  {
    cdr << ros_message->autonomous_brakepedalmotor_en;
  }

  return true;
}

static bool _Autonomousbrakepedalcontrol__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Autonomousbrakepedalcontrol__ros_msg_type * ros_message = static_cast<_Autonomousbrakepedalcontrol__ros_msg_type *>(untyped_ros_message);
  // Field name: autonomous_brakemotor_voltage
  {
    cdr >> ros_message->autonomous_brakemotor_voltage;
  }

  // Field name: autonomous_brakepedalmotor_per
  {
    cdr >> ros_message->autonomous_brakepedalmotor_per;
  }

  // Field name: autonomous_brakepedalmotor_acc
  {
    cdr >> ros_message->autonomous_brakepedalmotor_acc;
  }

  // Field name: autonomous_brakepedalmotor_en
  {
    cdr >> ros_message->autonomous_brakepedalmotor_en;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t get_serialized_size_smart_can_msgs__msg__Autonomousbrakepedalcontrol(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Autonomousbrakepedalcontrol__ros_msg_type * ros_message = static_cast<const _Autonomousbrakepedalcontrol__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name autonomous_brakemotor_voltage
  {
    size_t item_size = sizeof(ros_message->autonomous_brakemotor_voltage);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name autonomous_brakepedalmotor_per
  {
    size_t item_size = sizeof(ros_message->autonomous_brakepedalmotor_per);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name autonomous_brakepedalmotor_acc
  {
    size_t item_size = sizeof(ros_message->autonomous_brakepedalmotor_acc);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name autonomous_brakepedalmotor_en
  {
    size_t item_size = sizeof(ros_message->autonomous_brakepedalmotor_en);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _Autonomousbrakepedalcontrol__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_smart_can_msgs__msg__Autonomousbrakepedalcontrol(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t max_serialized_size_smart_can_msgs__msg__Autonomousbrakepedalcontrol(
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

  // member: autonomous_brakemotor_voltage
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: autonomous_brakepedalmotor_per
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: autonomous_brakepedalmotor_acc
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: autonomous_brakepedalmotor_en
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
    using DataType = smart_can_msgs__msg__Autonomousbrakepedalcontrol;
    is_plain =
      (
      offsetof(DataType, autonomous_brakepedalmotor_en) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Autonomousbrakepedalcontrol__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_smart_can_msgs__msg__Autonomousbrakepedalcontrol(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Autonomousbrakepedalcontrol = {
  "smart_can_msgs::msg",
  "Autonomousbrakepedalcontrol",
  _Autonomousbrakepedalcontrol__cdr_serialize,
  _Autonomousbrakepedalcontrol__cdr_deserialize,
  _Autonomousbrakepedalcontrol__get_serialized_size,
  _Autonomousbrakepedalcontrol__max_serialized_size
};

static rosidl_message_type_support_t _Autonomousbrakepedalcontrol__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Autonomousbrakepedalcontrol,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smart_can_msgs, msg, Autonomousbrakepedalcontrol)() {
  return &_Autonomousbrakepedalcontrol__type_support;
}

#if defined(__cplusplus)
}
#endif
