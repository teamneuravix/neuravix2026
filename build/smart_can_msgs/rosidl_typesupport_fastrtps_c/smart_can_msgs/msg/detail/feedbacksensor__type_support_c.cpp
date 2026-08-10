// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from smart_can_msgs:msg/Feedbacksensor.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/feedbacksensor__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "smart_can_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "smart_can_msgs/msg/detail/feedbacksensor__struct.h"
#include "smart_can_msgs/msg/detail/feedbacksensor__functions.h"
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


using _Feedbacksensor__ros_msg_type = smart_can_msgs__msg__Feedbacksensor;

static bool _Feedbacksensor__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Feedbacksensor__ros_msg_type * ros_message = static_cast<const _Feedbacksensor__ros_msg_type *>(untyped_ros_message);
  // Field name: steeringanglesensorhamdata
  {
    cdr << ros_message->steeringanglesensorhamdata;
  }

  // Field name: brakepedalsensorhamdata
  {
    cdr << ros_message->brakepedalsensorhamdata;
  }

  // Field name: handbrakesensor
  {
    cdr << ros_message->handbrakesensor;
  }

  // Field name: handbrakesensor_hamdata
  {
    cdr << ros_message->handbrakesensor_hamdata;
  }

  // Field name: indir
  {
    cdr << ros_message->indir;
  }

  // Field name: kaldir
  {
    cdr << ros_message->kaldir;
  }

  // Field name: butonindir
  {
    cdr << ros_message->butonindir;
  }

  // Field name: butonkaldir
  {
    cdr << ros_message->butonkaldir;
  }

  return true;
}

static bool _Feedbacksensor__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Feedbacksensor__ros_msg_type * ros_message = static_cast<_Feedbacksensor__ros_msg_type *>(untyped_ros_message);
  // Field name: steeringanglesensorhamdata
  {
    cdr >> ros_message->steeringanglesensorhamdata;
  }

  // Field name: brakepedalsensorhamdata
  {
    cdr >> ros_message->brakepedalsensorhamdata;
  }

  // Field name: handbrakesensor
  {
    cdr >> ros_message->handbrakesensor;
  }

  // Field name: handbrakesensor_hamdata
  {
    cdr >> ros_message->handbrakesensor_hamdata;
  }

  // Field name: indir
  {
    cdr >> ros_message->indir;
  }

  // Field name: kaldir
  {
    cdr >> ros_message->kaldir;
  }

  // Field name: butonindir
  {
    cdr >> ros_message->butonindir;
  }

  // Field name: butonkaldir
  {
    cdr >> ros_message->butonkaldir;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t get_serialized_size_smart_can_msgs__msg__Feedbacksensor(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Feedbacksensor__ros_msg_type * ros_message = static_cast<const _Feedbacksensor__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name steeringanglesensorhamdata
  {
    size_t item_size = sizeof(ros_message->steeringanglesensorhamdata);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name brakepedalsensorhamdata
  {
    size_t item_size = sizeof(ros_message->brakepedalsensorhamdata);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name handbrakesensor
  {
    size_t item_size = sizeof(ros_message->handbrakesensor);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name handbrakesensor_hamdata
  {
    size_t item_size = sizeof(ros_message->handbrakesensor_hamdata);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name indir
  {
    size_t item_size = sizeof(ros_message->indir);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name kaldir
  {
    size_t item_size = sizeof(ros_message->kaldir);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name butonindir
  {
    size_t item_size = sizeof(ros_message->butonindir);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name butonkaldir
  {
    size_t item_size = sizeof(ros_message->butonkaldir);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _Feedbacksensor__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_smart_can_msgs__msg__Feedbacksensor(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t max_serialized_size_smart_can_msgs__msg__Feedbacksensor(
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

  // member: steeringanglesensorhamdata
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: brakepedalsensorhamdata
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: handbrakesensor
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: handbrakesensor_hamdata
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: indir
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: kaldir
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: butonindir
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: butonkaldir
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
    using DataType = smart_can_msgs__msg__Feedbacksensor;
    is_plain =
      (
      offsetof(DataType, butonkaldir) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Feedbacksensor__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_smart_can_msgs__msg__Feedbacksensor(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Feedbacksensor = {
  "smart_can_msgs::msg",
  "Feedbacksensor",
  _Feedbacksensor__cdr_serialize,
  _Feedbacksensor__cdr_deserialize,
  _Feedbacksensor__get_serialized_size,
  _Feedbacksensor__max_serialized_size
};

static rosidl_message_type_support_t _Feedbacksensor__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Feedbacksensor,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smart_can_msgs, msg, Feedbacksensor)() {
  return &_Feedbacksensor__type_support;
}

#if defined(__cplusplus)
}
#endif
