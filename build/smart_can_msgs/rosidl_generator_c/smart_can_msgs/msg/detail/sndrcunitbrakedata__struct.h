// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Sndrcunitbrakedata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITBRAKEDATA__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITBRAKEDATA__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Sndrcunitbrakedata in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Sndrcunitbrakedata
{
  uint16_t rc_brakepedal_speed;
  uint16_t rc_brakepedal_acc;
  uint8_t rc_brakepedal_pos;
} smart_can_msgs__msg__Sndrcunitbrakedata;

// Struct for a sequence of smart_can_msgs__msg__Sndrcunitbrakedata.
typedef struct smart_can_msgs__msg__Sndrcunitbrakedata__Sequence
{
  smart_can_msgs__msg__Sndrcunitbrakedata * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Sndrcunitbrakedata__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITBRAKEDATA__STRUCT_H_
