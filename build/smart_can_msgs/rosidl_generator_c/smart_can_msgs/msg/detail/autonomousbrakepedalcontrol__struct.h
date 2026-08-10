// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Autonomousbrakepedalcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSBRAKEPEDALCONTROL__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSBRAKEPEDALCONTROL__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Autonomousbrakepedalcontrol in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Autonomousbrakepedalcontrol
{
  uint8_t autonomous_brakemotor_voltage;
  uint8_t autonomous_brakepedalmotor_per;
  uint16_t autonomous_brakepedalmotor_acc;
  uint8_t autonomous_brakepedalmotor_en;
} smart_can_msgs__msg__Autonomousbrakepedalcontrol;

// Struct for a sequence of smart_can_msgs__msg__Autonomousbrakepedalcontrol.
typedef struct smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence
{
  smart_can_msgs__msg__Autonomousbrakepedalcontrol * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSBRAKEPEDALCONTROL__STRUCT_H_
