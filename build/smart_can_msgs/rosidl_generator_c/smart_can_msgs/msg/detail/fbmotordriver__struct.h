// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Fbmotordriver.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Fbmotordriver in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Fbmotordriver
{
  uint8_t gear_status_from_motor;
  uint16_t plustripdistance;
  uint16_t vehiclerpm;
} smart_can_msgs__msg__Fbmotordriver;

// Struct for a sequence of smart_can_msgs__msg__Fbmotordriver.
typedef struct smart_can_msgs__msg__Fbmotordriver__Sequence
{
  smart_can_msgs__msg__Fbmotordriver * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Fbmotordriver__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__STRUCT_H_
