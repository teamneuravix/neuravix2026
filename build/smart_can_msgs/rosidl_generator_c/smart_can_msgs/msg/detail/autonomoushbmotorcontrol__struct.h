// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Autonomoushbmotorcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Autonomoushbmotorcontrol in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Autonomoushbmotorcontrol
{
  uint8_t autonomous_hb_motor_pwm;
  uint8_t autonomous_hb_motstate;
  uint8_t autonomous_hb_moten;
} smart_can_msgs__msg__Autonomoushbmotorcontrol;

// Struct for a sequence of smart_can_msgs__msg__Autonomoushbmotorcontrol.
typedef struct smart_can_msgs__msg__Autonomoushbmotorcontrol__Sequence
{
  smart_can_msgs__msg__Autonomoushbmotorcontrol * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Autonomoushbmotorcontrol__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__STRUCT_H_
