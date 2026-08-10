// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Fbvehiclespeed.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Fbvehiclespeed in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Fbvehiclespeed
{
  uint8_t fb_vehiclespeed_kmh;
  uint8_t fb_reelvehiclespeed_kmh;
  uint8_t fb_reelvehiclespeed_ms;
} smart_can_msgs__msg__Fbvehiclespeed;

// Struct for a sequence of smart_can_msgs__msg__Fbvehiclespeed.
typedef struct smart_can_msgs__msg__Fbvehiclespeed__Sequence
{
  smart_can_msgs__msg__Fbvehiclespeed * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Fbvehiclespeed__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__STRUCT_H_
