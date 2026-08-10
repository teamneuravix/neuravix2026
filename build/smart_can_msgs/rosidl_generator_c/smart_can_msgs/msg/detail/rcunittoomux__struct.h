// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Rcunittoomux.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Rcunittoomux in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Rcunittoomux
{
  int8_t autonomous_emergency;
  uint8_t rc_windowresintance;
  uint8_t rc_interiorlight;
  uint8_t rc_reverselight;
  uint8_t rc_drl;
  uint8_t rc_brakelight;
  int8_t autonomous_door_open;
  int8_t autonomous_door_close;
  uint8_t rc_signalstatus;
  uint8_t rc_lowbeam;
  uint8_t rc_highbeam;
  uint8_t rc_selectiongear;
  uint8_t rc_ignition;
} smart_can_msgs__msg__Rcunittoomux;

// Struct for a sequence of smart_can_msgs__msg__Rcunittoomux.
typedef struct smart_can_msgs__msg__Rcunittoomux__Sequence
{
  smart_can_msgs__msg__Rcunittoomux * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Rcunittoomux__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__STRUCT_H_
