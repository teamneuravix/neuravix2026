// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Autonomoussteeringmotcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Autonomoussteeringmotcontrol in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Autonomoussteeringmotcontrol
{
  uint8_t autonomous_steeringmot_en;
  uint8_t autonomous_steeringmot_pwm;
} smart_can_msgs__msg__Autonomoussteeringmotcontrol;

// Struct for a sequence of smart_can_msgs__msg__Autonomoussteeringmotcontrol.
typedef struct smart_can_msgs__msg__Autonomoussteeringmotcontrol__Sequence
{
  smart_can_msgs__msg__Autonomoussteeringmotcontrol * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Autonomoussteeringmotcontrol__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__STRUCT_H_
