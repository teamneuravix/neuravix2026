// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from smart_can_msgs:msg/Feedbacksensor.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/feedbacksensor__rosidl_typesupport_fastrtps_cpp.hpp"
#include "smart_can_msgs/msg/detail/feedbacksensor__struct.hpp"

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
  const smart_can_msgs::msg::Feedbacksensor & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: steeringanglesensorhamdata
  cdr << ros_message.steeringanglesensorhamdata;
  // Member: brakepedalsensorhamdata
  cdr << ros_message.brakepedalsensorhamdata;
  // Member: handbrakesensor
  cdr << ros_message.handbrakesensor;
  // Member: handbrakesensor_hamdata
  cdr << ros_message.handbrakesensor_hamdata;
  // Member: indir
  cdr << ros_message.indir;
  // Member: kaldir
  cdr << ros_message.kaldir;
  // Member: butonindir
  cdr << ros_message.butonindir;
  // Member: butonkaldir
  cdr << ros_message.butonkaldir;
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  smart_can_msgs::msg::Feedbacksensor & ros_message)
{
  // Member: steeringanglesensorhamdata
  cdr >> ros_message.steeringanglesensorhamdata;

  // Member: brakepedalsensorhamdata
  cdr >> ros_message.brakepedalsensorhamdata;

  // Member: handbrakesensor
  cdr >> ros_message.handbrakesensor;

  // Member: handbrakesensor_hamdata
  cdr >> ros_message.handbrakesensor_hamdata;

  // Member: indir
  cdr >> ros_message.indir;

  // Member: kaldir
  cdr >> ros_message.kaldir;

  // Member: butonindir
  cdr >> ros_message.butonindir;

  // Member: butonkaldir
  cdr >> ros_message.butonkaldir;

  return true;
}  // NOLINT(readability/fn_size)

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
get_serialized_size(
  const smart_can_msgs::msg::Feedbacksensor & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: steeringanglesensorhamdata
  {
    size_t item_size = sizeof(ros_message.steeringanglesensorhamdata);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: brakepedalsensorhamdata
  {
    size_t item_size = sizeof(ros_message.brakepedalsensorhamdata);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: handbrakesensor
  {
    size_t item_size = sizeof(ros_message.handbrakesensor);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: handbrakesensor_hamdata
  {
    size_t item_size = sizeof(ros_message.handbrakesensor_hamdata);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: indir
  {
    size_t item_size = sizeof(ros_message.indir);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: kaldir
  {
    size_t item_size = sizeof(ros_message.kaldir);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: butonindir
  {
    size_t item_size = sizeof(ros_message.butonindir);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: butonkaldir
  {
    size_t item_size = sizeof(ros_message.butonkaldir);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
max_serialized_size_Feedbacksensor(
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


  // Member: steeringanglesensorhamdata
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: brakepedalsensorhamdata
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: handbrakesensor
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: handbrakesensor_hamdata
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: indir
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: kaldir
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: butonindir
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: butonkaldir
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
    using DataType = smart_can_msgs::msg::Feedbacksensor;
    is_plain =
      (
      offsetof(DataType, butonkaldir) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static bool _Feedbacksensor__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const smart_can_msgs::msg::Feedbacksensor *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _Feedbacksensor__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<smart_can_msgs::msg::Feedbacksensor *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _Feedbacksensor__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const smart_can_msgs::msg::Feedbacksensor *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _Feedbacksensor__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_Feedbacksensor(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _Feedbacksensor__callbacks = {
  "smart_can_msgs::msg",
  "Feedbacksensor",
  _Feedbacksensor__cdr_serialize,
  _Feedbacksensor__cdr_deserialize,
  _Feedbacksensor__get_serialized_size,
  _Feedbacksensor__max_serialized_size
};

static rosidl_message_type_support_t _Feedbacksensor__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_Feedbacksensor__callbacks,
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
get_message_type_support_handle<smart_can_msgs::msg::Feedbacksensor>()
{
  return &smart_can_msgs::msg::typesupport_fastrtps_cpp::_Feedbacksensor__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smart_can_msgs, msg, Feedbacksensor)() {
  return &smart_can_msgs::msg::typesupport_fastrtps_cpp::_Feedbacksensor__handle;
}

#ifdef __cplusplus
}
#endif
