// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from smart_can_msgs:msg/Fbomuxtoautonomous.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/fbomuxtoautonomous__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "smart_can_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "smart_can_msgs/msg/detail/fbomuxtoautonomous__struct.h"
#include "smart_can_msgs/msg/detail/fbomuxtoautonomous__functions.h"
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


using _Fbomuxtoautonomous__ros_msg_type = smart_can_msgs__msg__Fbomuxtoautonomous;

static bool _Fbomuxtoautonomous__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Fbomuxtoautonomous__ros_msg_type * ros_message = static_cast<const _Fbomuxtoautonomous__ros_msg_type *>(untyped_ros_message);
  // Field name: fb_emergency
  {
    cdr << ros_message->fb_emergency;
  }

  // Field name: fb_reverselight
  {
    cdr << ros_message->fb_reverselight;
  }

  // Field name: fb_rightsignal
  {
    cdr << ros_message->fb_rightsignal;
  }

  // Field name: fb_windowresistance
  {
    cdr << ros_message->fb_windowresistance;
  }

  // Field name: fb_leftsignal
  {
    cdr << ros_message->fb_leftsignal;
  }

  // Field name: fb_interiorlight
  {
    cdr << ros_message->fb_interiorlight;
  }

  // Field name: fb_drl
  {
    cdr << ros_message->fb_drl;
  }

  // Field name: fb_doorkeystatus
  {
    cdr << ros_message->fb_doorkeystatus;
  }

  // Field name: fb_brakelight
  {
    cdr << ros_message->fb_brakelight;
  }

  // Field name: fb_batteryvoltage
  {
    cdr << ros_message->fb_batteryvoltage;
  }

  // Field name: fb_chargeinput
  {
    cdr << ros_message->fb_chargeinput;
  }

  // Field name: fb_highbeam
  {
    cdr << ros_message->fb_highbeam;
  }

  // Field name: fb_lowbeam
  {
    cdr << ros_message->fb_lowbeam;
  }

  // Field name: fb_ignition
  {
    cdr << ros_message->fb_ignition;
  }

  // Field name: fb_hazardouslight
  {
    cdr << ros_message->fb_hazardouslight;
  }

  // Field name: fb_vehiclestatus
  {
    cdr << ros_message->fb_vehiclestatus;
  }

  // Field name: fb_leftdoorstatus
  {
    cdr << ros_message->fb_leftdoorstatus;
  }

  // Field name: fb_rightdoorstatus
  {
    cdr << ros_message->fb_rightdoorstatus;
  }

  // Field name: fb_batterysoc
  {
    cdr << ros_message->fb_batterysoc;
  }

  // Field name: fb_errorpowertrain
  {
    cdr << ros_message->fb_errorpowertrain;
  }

  // Field name: fb_errorbattery
  {
    cdr << ros_message->fb_errorbattery;
  }

  // Field name: fb_brakepedal_voltage_en
  {
    cdr << ros_message->fb_brakepedal_voltage_en;
  }

  return true;
}

static bool _Fbomuxtoautonomous__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Fbomuxtoautonomous__ros_msg_type * ros_message = static_cast<_Fbomuxtoautonomous__ros_msg_type *>(untyped_ros_message);
  // Field name: fb_emergency
  {
    cdr >> ros_message->fb_emergency;
  }

  // Field name: fb_reverselight
  {
    cdr >> ros_message->fb_reverselight;
  }

  // Field name: fb_rightsignal
  {
    cdr >> ros_message->fb_rightsignal;
  }

  // Field name: fb_windowresistance
  {
    cdr >> ros_message->fb_windowresistance;
  }

  // Field name: fb_leftsignal
  {
    cdr >> ros_message->fb_leftsignal;
  }

  // Field name: fb_interiorlight
  {
    cdr >> ros_message->fb_interiorlight;
  }

  // Field name: fb_drl
  {
    cdr >> ros_message->fb_drl;
  }

  // Field name: fb_doorkeystatus
  {
    cdr >> ros_message->fb_doorkeystatus;
  }

  // Field name: fb_brakelight
  {
    cdr >> ros_message->fb_brakelight;
  }

  // Field name: fb_batteryvoltage
  {
    cdr >> ros_message->fb_batteryvoltage;
  }

  // Field name: fb_chargeinput
  {
    cdr >> ros_message->fb_chargeinput;
  }

  // Field name: fb_highbeam
  {
    cdr >> ros_message->fb_highbeam;
  }

  // Field name: fb_lowbeam
  {
    cdr >> ros_message->fb_lowbeam;
  }

  // Field name: fb_ignition
  {
    cdr >> ros_message->fb_ignition;
  }

  // Field name: fb_hazardouslight
  {
    cdr >> ros_message->fb_hazardouslight;
  }

  // Field name: fb_vehiclestatus
  {
    cdr >> ros_message->fb_vehiclestatus;
  }

  // Field name: fb_leftdoorstatus
  {
    cdr >> ros_message->fb_leftdoorstatus;
  }

  // Field name: fb_rightdoorstatus
  {
    cdr >> ros_message->fb_rightdoorstatus;
  }

  // Field name: fb_batterysoc
  {
    cdr >> ros_message->fb_batterysoc;
  }

  // Field name: fb_errorpowertrain
  {
    cdr >> ros_message->fb_errorpowertrain;
  }

  // Field name: fb_errorbattery
  {
    cdr >> ros_message->fb_errorbattery;
  }

  // Field name: fb_brakepedal_voltage_en
  {
    cdr >> ros_message->fb_brakepedal_voltage_en;
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t get_serialized_size_smart_can_msgs__msg__Fbomuxtoautonomous(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Fbomuxtoautonomous__ros_msg_type * ros_message = static_cast<const _Fbomuxtoautonomous__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name fb_emergency
  {
    size_t item_size = sizeof(ros_message->fb_emergency);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_reverselight
  {
    size_t item_size = sizeof(ros_message->fb_reverselight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_rightsignal
  {
    size_t item_size = sizeof(ros_message->fb_rightsignal);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_windowresistance
  {
    size_t item_size = sizeof(ros_message->fb_windowresistance);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_leftsignal
  {
    size_t item_size = sizeof(ros_message->fb_leftsignal);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_interiorlight
  {
    size_t item_size = sizeof(ros_message->fb_interiorlight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_drl
  {
    size_t item_size = sizeof(ros_message->fb_drl);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_doorkeystatus
  {
    size_t item_size = sizeof(ros_message->fb_doorkeystatus);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_brakelight
  {
    size_t item_size = sizeof(ros_message->fb_brakelight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_batteryvoltage
  {
    size_t item_size = sizeof(ros_message->fb_batteryvoltage);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_chargeinput
  {
    size_t item_size = sizeof(ros_message->fb_chargeinput);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_highbeam
  {
    size_t item_size = sizeof(ros_message->fb_highbeam);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_lowbeam
  {
    size_t item_size = sizeof(ros_message->fb_lowbeam);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_ignition
  {
    size_t item_size = sizeof(ros_message->fb_ignition);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_hazardouslight
  {
    size_t item_size = sizeof(ros_message->fb_hazardouslight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_vehiclestatus
  {
    size_t item_size = sizeof(ros_message->fb_vehiclestatus);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_leftdoorstatus
  {
    size_t item_size = sizeof(ros_message->fb_leftdoorstatus);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_rightdoorstatus
  {
    size_t item_size = sizeof(ros_message->fb_rightdoorstatus);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_batterysoc
  {
    size_t item_size = sizeof(ros_message->fb_batterysoc);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_errorpowertrain
  {
    size_t item_size = sizeof(ros_message->fb_errorpowertrain);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_errorbattery
  {
    size_t item_size = sizeof(ros_message->fb_errorbattery);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name fb_brakepedal_voltage_en
  {
    size_t item_size = sizeof(ros_message->fb_brakepedal_voltage_en);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

static uint32_t _Fbomuxtoautonomous__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_smart_can_msgs__msg__Fbomuxtoautonomous(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_smart_can_msgs
size_t max_serialized_size_smart_can_msgs__msg__Fbomuxtoautonomous(
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

  // member: fb_emergency
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_reverselight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_rightsignal
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_windowresistance
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_leftsignal
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_interiorlight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_drl
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_doorkeystatus
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_brakelight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_batteryvoltage
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_chargeinput
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_highbeam
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_lowbeam
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_ignition
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_hazardouslight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_vehiclestatus
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_leftdoorstatus
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_rightdoorstatus
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_batterysoc
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_errorpowertrain
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_errorbattery
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: fb_brakepedal_voltage_en
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
    using DataType = smart_can_msgs__msg__Fbomuxtoautonomous;
    is_plain =
      (
      offsetof(DataType, fb_brakepedal_voltage_en) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Fbomuxtoautonomous__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_smart_can_msgs__msg__Fbomuxtoautonomous(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Fbomuxtoautonomous = {
  "smart_can_msgs::msg",
  "Fbomuxtoautonomous",
  _Fbomuxtoautonomous__cdr_serialize,
  _Fbomuxtoautonomous__cdr_deserialize,
  _Fbomuxtoautonomous__get_serialized_size,
  _Fbomuxtoautonomous__max_serialized_size
};

static rosidl_message_type_support_t _Fbomuxtoautonomous__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Fbomuxtoautonomous,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, smart_can_msgs, msg, Fbomuxtoautonomous)() {
  return &_Fbomuxtoautonomous__type_support;
}

#if defined(__cplusplus)
}
#endif
