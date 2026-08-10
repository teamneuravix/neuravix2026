// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from smart_can_msgs:msg/Fbomuxtoautonomous.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/fbomuxtoautonomous__rosidl_typesupport_fastrtps_cpp.hpp"
#include "smart_can_msgs/msg/detail/fbomuxtoautonomous__struct.hpp"

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
  const smart_can_msgs::msg::Fbomuxtoautonomous & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: fb_emergency
  cdr << ros_message.fb_emergency;
  // Member: fb_reverselight
  cdr << ros_message.fb_reverselight;
  // Member: fb_rightsignal
  cdr << ros_message.fb_rightsignal;
  // Member: fb_windowresistance
  cdr << ros_message.fb_windowresistance;
  // Member: fb_leftsignal
  cdr << ros_message.fb_leftsignal;
  // Member: fb_interiorlight
  cdr << ros_message.fb_interiorlight;
  // Member: fb_drl
  cdr << ros_message.fb_drl;
  // Member: fb_doorkeystatus
  cdr << ros_message.fb_doorkeystatus;
  // Member: fb_brakelight
  cdr << ros_message.fb_brakelight;
  // Member: fb_batteryvoltage
  cdr << ros_message.fb_batteryvoltage;
  // Member: fb_chargeinput
  cdr << ros_message.fb_chargeinput;
  // Member: fb_highbeam
  cdr << ros_message.fb_highbeam;
  // Member: fb_lowbeam
  cdr << ros_message.fb_lowbeam;
  // Member: fb_ignition
  cdr << ros_message.fb_ignition;
  // Member: fb_hazardouslight
  cdr << ros_message.fb_hazardouslight;
  // Member: fb_vehiclestatus
  cdr << ros_message.fb_vehiclestatus;
  // Member: fb_leftdoorstatus
  cdr << ros_message.fb_leftdoorstatus;
  // Member: fb_rightdoorstatus
  cdr << ros_message.fb_rightdoorstatus;
  // Member: fb_batterysoc
  cdr << ros_message.fb_batterysoc;
  // Member: fb_errorpowertrain
  cdr << ros_message.fb_errorpowertrain;
  // Member: fb_errorbattery
  cdr << ros_message.fb_errorbattery;
  // Member: fb_brakepedal_voltage_en
  cdr << ros_message.fb_brakepedal_voltage_en;
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  smart_can_msgs::msg::Fbomuxtoautonomous & ros_message)
{
  // Member: fb_emergency
  cdr >> ros_message.fb_emergency;

  // Member: fb_reverselight
  cdr >> ros_message.fb_reverselight;

  // Member: fb_rightsignal
  cdr >> ros_message.fb_rightsignal;

  // Member: fb_windowresistance
  cdr >> ros_message.fb_windowresistance;

  // Member: fb_leftsignal
  cdr >> ros_message.fb_leftsignal;

  // Member: fb_interiorlight
  cdr >> ros_message.fb_interiorlight;

  // Member: fb_drl
  cdr >> ros_message.fb_drl;

  // Member: fb_doorkeystatus
  cdr >> ros_message.fb_doorkeystatus;

  // Member: fb_brakelight
  cdr >> ros_message.fb_brakelight;

  // Member: fb_batteryvoltage
  cdr >> ros_message.fb_batteryvoltage;

  // Member: fb_chargeinput
  cdr >> ros_message.fb_chargeinput;

  // Member: fb_highbeam
  cdr >> ros_message.fb_highbeam;

  // Member: fb_lowbeam
  cdr >> ros_message.fb_lowbeam;

  // Member: fb_ignition
  cdr >> ros_message.fb_ignition;

  // Member: fb_hazardouslight
  cdr >> ros_message.fb_hazardouslight;

  // Member: fb_vehiclestatus
  cdr >> ros_message.fb_vehiclestatus;

  // Member: fb_leftdoorstatus
  cdr >> ros_message.fb_leftdoorstatus;

  // Member: fb_rightdoorstatus
  cdr >> ros_message.fb_rightdoorstatus;

  // Member: fb_batterysoc
  cdr >> ros_message.fb_batterysoc;

  // Member: fb_errorpowertrain
  cdr >> ros_message.fb_errorpowertrain;

  // Member: fb_errorbattery
  cdr >> ros_message.fb_errorbattery;

  // Member: fb_brakepedal_voltage_en
  cdr >> ros_message.fb_brakepedal_voltage_en;

  return true;
}  // NOLINT(readability/fn_size)

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
get_serialized_size(
  const smart_can_msgs::msg::Fbomuxtoautonomous & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: fb_emergency
  {
    size_t item_size = sizeof(ros_message.fb_emergency);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_reverselight
  {
    size_t item_size = sizeof(ros_message.fb_reverselight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_rightsignal
  {
    size_t item_size = sizeof(ros_message.fb_rightsignal);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_windowresistance
  {
    size_t item_size = sizeof(ros_message.fb_windowresistance);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_leftsignal
  {
    size_t item_size = sizeof(ros_message.fb_leftsignal);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_interiorlight
  {
    size_t item_size = sizeof(ros_message.fb_interiorlight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_drl
  {
    size_t item_size = sizeof(ros_message.fb_drl);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_doorkeystatus
  {
    size_t item_size = sizeof(ros_message.fb_doorkeystatus);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_brakelight
  {
    size_t item_size = sizeof(ros_message.fb_brakelight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_batteryvoltage
  {
    size_t item_size = sizeof(ros_message.fb_batteryvoltage);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_chargeinput
  {
    size_t item_size = sizeof(ros_message.fb_chargeinput);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_highbeam
  {
    size_t item_size = sizeof(ros_message.fb_highbeam);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_lowbeam
  {
    size_t item_size = sizeof(ros_message.fb_lowbeam);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_ignition
  {
    size_t item_size = sizeof(ros_message.fb_ignition);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_hazardouslight
  {
    size_t item_size = sizeof(ros_message.fb_hazardouslight);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_vehiclestatus
  {
    size_t item_size = sizeof(ros_message.fb_vehiclestatus);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_leftdoorstatus
  {
    size_t item_size = sizeof(ros_message.fb_leftdoorstatus);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_rightdoorstatus
  {
    size_t item_size = sizeof(ros_message.fb_rightdoorstatus);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_batterysoc
  {
    size_t item_size = sizeof(ros_message.fb_batterysoc);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_errorpowertrain
  {
    size_t item_size = sizeof(ros_message.fb_errorpowertrain);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_errorbattery
  {
    size_t item_size = sizeof(ros_message.fb_errorbattery);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // Member: fb_brakepedal_voltage_en
  {
    size_t item_size = sizeof(ros_message.fb_brakepedal_voltage_en);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_smart_can_msgs
max_serialized_size_Fbomuxtoautonomous(
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


  // Member: fb_emergency
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_reverselight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_rightsignal
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_windowresistance
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_leftsignal
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_interiorlight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_drl
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_doorkeystatus
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_brakelight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_batteryvoltage
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_chargeinput
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_highbeam
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_lowbeam
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_ignition
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_hazardouslight
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_vehiclestatus
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_leftdoorstatus
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_rightdoorstatus
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_batterysoc
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_errorpowertrain
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_errorbattery
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: fb_brakepedal_voltage_en
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
    using DataType = smart_can_msgs::msg::Fbomuxtoautonomous;
    is_plain =
      (
      offsetof(DataType, fb_brakepedal_voltage_en) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static bool _Fbomuxtoautonomous__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const smart_can_msgs::msg::Fbomuxtoautonomous *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _Fbomuxtoautonomous__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<smart_can_msgs::msg::Fbomuxtoautonomous *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _Fbomuxtoautonomous__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const smart_can_msgs::msg::Fbomuxtoautonomous *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _Fbomuxtoautonomous__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_Fbomuxtoautonomous(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _Fbomuxtoautonomous__callbacks = {
  "smart_can_msgs::msg",
  "Fbomuxtoautonomous",
  _Fbomuxtoautonomous__cdr_serialize,
  _Fbomuxtoautonomous__cdr_deserialize,
  _Fbomuxtoautonomous__get_serialized_size,
  _Fbomuxtoautonomous__max_serialized_size
};

static rosidl_message_type_support_t _Fbomuxtoautonomous__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_Fbomuxtoautonomous__callbacks,
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
get_message_type_support_handle<smart_can_msgs::msg::Fbomuxtoautonomous>()
{
  return &smart_can_msgs::msg::typesupport_fastrtps_cpp::_Fbomuxtoautonomous__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, smart_can_msgs, msg, Fbomuxtoautonomous)() {
  return &smart_can_msgs::msg::typesupport_fastrtps_cpp::_Fbomuxtoautonomous__handle;
}

#ifdef __cplusplus
}
#endif
