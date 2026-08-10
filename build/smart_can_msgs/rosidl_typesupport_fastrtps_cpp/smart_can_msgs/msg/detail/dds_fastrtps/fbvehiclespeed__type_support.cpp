// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from smart_can_msgs:msg/Fbvehiclespeed.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/fbvehiclespeed__rosidl_typesupport_fastrtps_cpp.hpp"
#include "smart_can_msgs/msg/detail/fbvehiclespeed__struct.hpp"

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
  const smart_can_msgs::msg::Fbvehiclespeed & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: fb_vehiclespeed_kmh
  cdr << ros_message.fb_vehiclespeed_kmh;
  // Member: fb_reelvehiclespeed_kmh
  cdr << ros_message.fb_reelvehiclespeed_kmh;
  // Member: fb_reelvehiclespeed_ms
  cdr << ros_message.fb_reelvehiclespeed_ms;
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  smart_can_msgs::msg::Fbvehiclespeed & ros_message)
{
  // Member: fb_vehiclespeed_kmh
  cdr >> ros_message.fb_vehiclespeed_kmh;

  // Member: fb_reelvehiclespeed_kmh
  cdr >> ros_message.fb_reelvehiclespeed_kmh;

  // Member: fb_reelvehiclespeed_ms
  cdr >> ros_message.fb_reelvehiclespeed_ms;

  return true;
}  // NOLINT(readability/fn_size)

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
get_serialized_size(
  const smart_can_msgs::msg::Fbvehiclespeed & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: fb_vehiclespeed_kmh
  {
    size_t item_size = sizeof(ros_message.fb_vehiclespeed_kmh);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_reelvehiclespeed_kmh
  {
    size_t item_size = sizeof(ros_message.fb_reelvehiclespeed_kmh);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_reelvehiclespeed_ms
  {
    size_t item_size = sizeof(ros_message.fb_reelvehiclespeed_ms);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
max_serialized_size_Fbvehiclespeed(
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


  // Member: fb_vehiclespeed_kmh
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_reelvehiclespeed_kmh
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_reelvehiclespeed_ms
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
    using DataType = smart_can_msgs::msg::Fbvehiclespeed;
    is_plain =
      (
      offsetof(DataType, fb_reelvehiclespeed_ms) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static bool _Fbvehiclespeed__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const smart_can_msgs::msg::Fbvehiclespeed *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _Fbvehiclespeed__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<smart_can_msgs::msg::Fbvehiclespeed *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _Fbvehiclespeed__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const smart_can_msgs::msg::Fbvehiclespeed *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _Fbvehiclespeed__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_Fbvehiclespeed(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _Fbvehiclespeed__callbacks = {
  "smart_can_msgs::msg",
  "Fbvehiclespeed",
  _Fbvehiclespeed__cdr_serialize,
  _Fbvehiclespeed__cdr_deserialize,
  _Fbvehiclespeed__get_serialized_size,
  _Fbvehiclespeed__max_serialized_size
};

static rosidl_message_type_support_t _Fbvehiclespeed__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_Fbvehiclespeed__callbacks,
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
get_message_type_support_handle<smart_can_msgs::msg::Fbvehiclespeed>()
{
  return &smart_can_msgs::msg::typesupport_fastrtps_cpp::_Fbvehiclespeed__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smart_can_msgs, msg, Fbvehiclespeed)() {
  return &smart_can_msgs::msg::typesupport_fastrtps_cpp::_Fbvehiclespeed__handle;
}

#ifdef __cplusplus
}
#endif
