// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from smart_can_msgs:msg/Rcunittoomux.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/rcunittoomux__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "smart_can_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "smart_can_msgs/msg/detail/rcunittoomux__struct.h"
#include "smart_can_msgs/msg/detail/rcunittoomux__functions.h"
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


using _Rcunittoomux__ros_msg_type = smart_can_msgs__msg__Rcunittoomux;

static bool _Rcunittoomux__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Rcunittoomux__ros_msg_type * ros_message = static_cast<const _Rcunittoomux__ros_msg_type *>(untyped_ros_message);
  // Field name: autonomous_emergency
  {
    cdr << ros_message->autonomous_emergency;
  }

  // Field name: rc_windowresintance
  {
    cdr << ros_message->rc_windowresintance;
  }

  // Field name: rc_interiorlight
  {
    cdr << ros_message->rc_interiorlight;
  }

  // Field name: rc_reverselight
  {
    cdr << ros_message->rc_reverselight;
  }

  // Field name: rc_drl
  {
    cdr << ros_message->rc_drl;
  }

  // Field name: rc_brakelight
  {
    cdr << ros_message->rc_brakelight;
  }

  // Field name: autonomous_door_open
  {
    cdr << ros_message->autonomous_door_open;
  }

  // Field name: autonomous_door_close
  {
    cdr << ros_message->autonomous_door_close;
  }

  // Field name: rc_signalstatus
  {
    cdr << ros_message->rc_signalstatus;
  }

  // Field name: rc_lowbeam
  {
    cdr << ros_message->rc_lowbeam;
  }

  // Field name: rc_highbeam
  {
    cdr << ros_message->rc_highbeam;
  }

  // Field name: rc_selectiongear
  {
    cdr << ros_message->rc_selectiongear;
  }

  // Field name: rc_ignition
  {
    cdr << ros_message->rc_ignition;
  }

  return true;
}

static bool _Rcunittoomux__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Rcunittoomux__ros_msg_type * ros_message = static_cast<_Rcunittoomux__ros_msg_type *>(untyped_ros_message);
  // Field name: autonomous_emergency
  {
    cdr >> ros_message->autonomous_emergency;
  }

  // Field name: rc_windowresintance
  {
    cdr >> ros_message->rc_windowresintance;
  }

  // Field name: rc_interiorlight
  {
    cdr >> ros_message->rc_interiorlight;
  }

  // Field name: rc_reverselight
  {
    cdr >> ros_message->rc_reverselight;
  }

  // Field name: rc_drl
  {
    cdr >> ros_message->rc_drl;
  }

  // Field name: rc_brakelight
  {
    cdr >> ros_message->rc_brakelight;
  }

  // Field name: autonomous_door_open
  {
    cdr >> ros_message->autonomous_door_open;
  }

  // Field name: autonomous_door_close
  {
    cdr >> ros_message->autonomous_door_close;
  }

  // Field name: rc_signalstatus
  {
    cdr >> ros_message->rc_signalstatus;
  }

  // Field name: rc_lowbeam
  {
    cdr >> ros_message->rc_lowbeam;
  }

  // Field name: rc_highbeam
  {
    cdr >> ros_message->rc_highbeam;
  }

  // Field name: rc_selectiongear
  {
    cdr >> ros_message->rc_selectiongear;
  }

  // Field name: rc_ignition
  {
    cdr >> ros_message->rc_ignition;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t get_serialized_size_smart_can_msgs__msg__Rcunittoomux(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Rcunittoomux__ros_msg_type * ros_message = static_cast<const _Rcunittoomux__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name autonomous_emergency
  {
    size_t item_size = sizeof(ros_message->autonomous_emergency);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_windowresintance
  {
    size_t item_size = sizeof(ros_message->rc_windowresintance);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_interiorlight
  {
    size_t item_size = sizeof(ros_message->rc_interiorlight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_reverselight
  {
    size_t item_size = sizeof(ros_message->rc_reverselight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_drl
  {
    size_t item_size = sizeof(ros_message->rc_drl);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_brakelight
  {
    size_t item_size = sizeof(ros_message->rc_brakelight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name autonomous_door_open
  {
    size_t item_size = sizeof(ros_message->autonomous_door_open);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name autonomous_door_close
  {
    size_t item_size = sizeof(ros_message->autonomous_door_close);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_signalstatus
  {
    size_t item_size = sizeof(ros_message->rc_signalstatus);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_lowbeam
  {
    size_t item_size = sizeof(ros_message->rc_lowbeam);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_highbeam
  {
    size_t item_size = sizeof(ros_message->rc_highbeam);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_selectiongear
  {
    size_t item_size = sizeof(ros_message->rc_selectiongear);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name rc_ignition
  {
    size_t item_size = sizeof(ros_message->rc_ignition);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _Rcunittoomux__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_smart_can_msgs__msg__Rcunittoomux(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t max_serialized_size_smart_can_msgs__msg__Rcunittoomux(
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

  // member: autonomous_emergency
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_windowresintance
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_interiorlight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_reverselight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_drl
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_brakelight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: autonomous_door_open
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: autonomous_door_close
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_signalstatus
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_lowbeam
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_highbeam
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_selectiongear
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: rc_ignition
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
    using DataType = smart_can_msgs__msg__Rcunittoomux;
    is_plain =
      (
      offsetof(DataType, rc_ignition) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Rcunittoomux__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_smart_can_msgs__msg__Rcunittoomux(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Rcunittoomux = {
  "smart_can_msgs::msg",
  "Rcunittoomux",
  _Rcunittoomux__cdr_serialize,
  _Rcunittoomux__cdr_deserialize,
  _Rcunittoomux__get_serialized_size,
  _Rcunittoomux__max_serialized_size
};

static rosidl_message_type_support_t _Rcunittoomux__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Rcunittoomux,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smart_can_msgs, msg, Rcunittoomux)() {
  return &_Rcunittoomux__type_support;
}

#if defined(__cplusplus)
}
#endif
