// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Sndrcunithandbrakedata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITHANDBRAKEDATA__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITHANDBRAKEDATA__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Sndrcunithandbrakedata in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Sndrcunithandbrakedata
{
  uint16_t rc_hb_pwmvalue;
  uint8_t rc_handbrake_press;
  uint8_t rc_handbrake_free;
  uint8_t rc_handbrakedata;
} smart_can_msgs__msg__Sndrcunithandbrakedata;

// Struct for a sequence of smart_can_msgs__msg__Sndrcunithandbrakedata.
typedef struct smart_can_msgs__msg__Sndrcunithandbrakedata__Sequence
{
  smart_can_msgs__msg__Sndrcunithandbrakedata * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Sndrcunithandbrakedata__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITHANDBRAKEDATA__STRUCT_H_
