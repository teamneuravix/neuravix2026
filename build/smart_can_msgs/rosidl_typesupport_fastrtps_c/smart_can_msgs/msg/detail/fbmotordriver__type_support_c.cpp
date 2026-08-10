// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from smart_can_msgs:msg/Fbmotordriver.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/fbmotordriver__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "smart_can_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "smart_can_msgs/msg/detail/fbmotordriver__struct.h"
#include "smart_can_msgs/msg/detail/fbmotordriver__functions.h"
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


using _Fbmotordriver__ros_msg_type = smart_can_msgs__msg__Fbmotordriver;

static bool _Fbmotordriver__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Fbmotordriver__ros_msg_type * ros_message = static_cast<const _Fbmotordriver__ros_msg_type *>(untyped_ros_message);
  // Field name: gear_status_from_motor
  {
    cdr << ros_message->gear_status_from_motor;
  }

  // Field name: plustripdistance
  {
    cdr << ros_message->plustripdistance;
  }

  // Field name: vehiclerpm
  {
    cdr << ros_message->vehiclerpm;
  }

  return true;
}

static bool _Fbmotordriver__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Fbmotordriver__ros_msg_type * ros_message = static_cast<_Fbmotordriver__ros_msg_type *>(untyped_ros_message);
  // Field name: gear_status_from_motor
  {
    cdr >> ros_message->gear_status_from_motor;
  }

  // Field name: plustripdistance
  {
    cdr >> ros_message->plustripdistance;
  }

  // Field name: vehiclerpm
  {
    cdr >> ros_message->vehiclerpm;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t get_serialized_size_smart_can_msgs__msg__Fbmotordriver(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Fbmotordriver__ros_msg_type * ros_message = static_cast<const _Fbmotordriver__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name gear_status_from_motor
  {
    size_t item_size = sizeof(ros_message->gear_status_from_motor);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name plustripdistance
  {
    size_t item_size = sizeof(ros_message->plustripdistance);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name vehiclerpm
  {
    size_t item_size = sizeof(ros_message->vehiclerpm);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _Fbmotordriver__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_smart_can_msgs__msg__Fbmotordriver(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t max_serialized_size_smart_can_msgs__msg__Fbmotordriver(
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

  // member: gear_status_from_motor
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: plustripdistance
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: vehiclerpm
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = smart_can_msgs__msg__Fbmotordriver;
    is_plain =
      (
      offsetof(DataType, vehiclerpm) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Fbmotordriver__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_smart_can_msgs__msg__Fbmotordriver(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Fbmotordriver = {
  "smart_can_msgs::msg",
  "Fbmotordriver",
  _Fbmotordriver__cdr_serialize,
  _Fbmotordriver__cdr_deserialize,
  _Fbmotordriver__get_serialized_size,
  _Fbmotordriver__max_serialized_size
};

static rosidl_message_type_support_t _Fbmotordriver__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Fbmotordriver,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smart_can_msgs, msg, Fbmotordriver)() {
  return &_Fbmotordriver__type_support;
}

#if defined(__cplusplus)
}
#endif
