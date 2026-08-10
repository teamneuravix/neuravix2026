// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Sndrcunitsteeringdata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITSTEERINGDATA__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITSTEERINGDATA__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Sndrcunitsteeringdata in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Sndrcunitsteeringdata
{
  uint8_t rc_steering_rightlimit;
  uint8_t rc_steering_leftlimit;
  uint16_t rc_steeringpwm;
  uint8_t rc_steeringdirection;
} smart_can_msgs__msg__Sndrcunitsteeringdata;

// Struct for a sequence of smart_can_msgs__msg__Sndrcunitsteeringdata.
typedef struct smart_can_msgs__msg__Sndrcunitsteeringdata__Sequence
{
  smart_can_msgs__msg__Sndrcunitsteeringdata * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Sndrcunitsteeringdata__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITSTEERINGDATA__STRUCT_H_
