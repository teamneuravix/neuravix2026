// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Feedbacksteeringangle.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Feedbacksteeringangle in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Feedbacksteeringangle
{
  int8_t feedbacksteeringangle;
  int8_t feedbackbrakepedalangle;
} smart_can_msgs__msg__Feedbacksteeringangle;

// Struct for a sequence of smart_can_msgs__msg__Feedbacksteeringangle.
typedef struct smart_can_msgs__msg__Feedbacksteeringangle__Sequence
{
  smart_can_msgs__msg__Feedbacksteeringangle * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Feedbacksteeringangle__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__STRUCT_H_
