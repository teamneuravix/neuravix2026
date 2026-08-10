// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Dis.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__DIS__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__DIS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Dis in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Dis
{
  float angle;
} smart_can_msgs__msg__Dis;

// Struct for a sequence of smart_can_msgs__msg__Dis.
typedef struct smart_can_msgs__msg__Dis__Sequence
{
  smart_can_msgs__msg__Dis * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Dis__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__DIS__STRUCT_H_
