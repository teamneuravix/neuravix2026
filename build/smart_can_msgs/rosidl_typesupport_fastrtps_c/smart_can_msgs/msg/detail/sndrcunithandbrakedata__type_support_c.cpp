// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from smart_can_msgs:msg/Sndrcunithandbrakedata.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/sndrcunithandbrakedata__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "smart_can_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "smart_can_msgs/msg/detail/sndrcunithandbrakedata__struct.h"
#include "smart_can_msgs/msg/detail/sndrcunithandbrakedata__functions.h"
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


using _Sndrcunithandbrakedata__ros_msg_type = smart_can_msgs__msg__Sndrcunithandbrakedata;

static bool _Sndrcunithandbrakedata__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Sndrcunithandbrakedata__ros_msg_type * ros_message = static_cast<const _Sndrcunithandbrakedata__ros_msg_type *>(untyped_ros_message);
  // Field name: rc_hb_pwmvalue
  {
    cdr << ros_message->rc_hb_pwmvalue;
  }

  // Field name: rc_handbrake_press
  {
    cdr << ros_message->rc_handbrake_press;
  }

  // Field name: rc_handbrake_free
  {
    cdr << ros_message->rc_handbrake_free;
  }

  // Field name: rc_handbrakedata
  {
    cdr << ros_message->rc_handbrakedata;
  }

  return true;
}

static bool _Sndrcunithandbrakedata__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Sndrcunithandbrakedata__ros_msg_type * ros_message = static_cast<_Sndrcunithandbrakedata__ros_msg_type *>(untyped_ros_message);
  // Field name: rc_hb_pwmvalue
  {
    cdr >> ros_message->rc_hb_pwmvalue;
  }

  // Field name: rc_handbrake_press
  {
    cdr >> ros_message->rc_handbrake_press;
  }

  // Field name: rc_handbrake_free
  {
    cdr >> ros_message->rc_handbrake_free;
  }

  // Field name: rc_handbrakedata
  {
    cdr >> ros_message->rc_handbrakedata;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t get_serialized_size_smart_can_msgs__msg__Sndrcunithandbrakedata(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Sndrcunithandbrakedata__ros_msg_type * ros_message = static_cast<const _Sndrcunithandbrakedata__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name rc_hb_pwmvalue
  {
    size_t item_size = sizeof(ros_message->rc_hb_pwmvalue);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_handbrake_press
  {
    size_t item_size = sizeof(ros_message->rc_handbrake_press);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_handbrake_free
  {
    size_t item_size = sizeof(ros_message->rc_handbrake_free);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_handbrakedata
  {
    size_t item_size = sizeof(ros_message->rc_handbrakedata);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _Sndrcunithandbrakedata__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_smart_can_msgs__msg__Sndrcunithandbrakedata(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t max_serialized_size_smart_can_msgs__msg__Sndrcunithandbrakedata(
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

  // member: rc_hb_pwmvalue
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint16_t);
    current_alignment += array_size * sizeof(uint16_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint16_t));
  }
  // member: rc_handbrake_press
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_handbrake_free
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_handbrakedata
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
    using DataType = smart_can_msgs__msg__Sndrcunithandbrakedata;
    is_plain =
      (
      offsetof(DataType, rc_handbrakedata) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Sndrcunithandbrakedata__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_smart_can_msgs__msg__Sndrcunithandbrakedata(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Sndrcunithandbrakedata = {
  "smart_can_msgs::msg",
  "Sndrcunithandbrakedata",
  _Sndrcunithandbrakedata__cdr_serialize,
  _Sndrcunithandbrakedata__cdr_deserialize,
  _Sndrcunithandbrakedata__get_serialized_size,
  _Sndrcunithandbrakedata__max_serialized_size
};

static rosidl_message_type_support_t _Sndrcunithandbrakedata__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Sndrcunithandbrakedata,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smart_can_msgs, msg, Sndrcunithandbrakedata)() {
  return &_Sndrcunithandbrakedata__type_support;
}

#if defined(__cplusplus)
}
#endif
