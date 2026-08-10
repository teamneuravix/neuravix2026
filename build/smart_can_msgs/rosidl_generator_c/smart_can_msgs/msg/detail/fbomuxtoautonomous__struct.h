// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smart_can_msgs:msg/Fbomuxtoautonomous.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__STRUCT_H_
#define SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Fbomuxtoautonomous in the package smart_can_msgs.
typedef struct smart_can_msgs__msg__Fbomuxtoautonomous
{
  uint8_t fb_emergency;
  uint8_t fb_reverselight;
  uint8_t fb_rightsignal;
  uint8_t fb_windowresistance;
  uint8_t fb_leftsignal;
  uint8_t fb_interiorlight;
  uint8_t fb_drl;
  uint8_t fb_doorkeystatus;
  uint8_t fb_brakelight;
  uint8_t fb_batteryvoltage;
  uint8_t fb_chargeinput;
  uint8_t fb_highbeam;
  uint8_t fb_lowbeam;
  uint8_t fb_ignition;
  uint8_t fb_hazardouslight;
  uint8_t fb_vehiclestatus;
  uint8_t fb_leftdoorstatus;
  uint8_t fb_rightdoorstatus;
  uint8_t fb_batterysoc;
  uint8_t fb_errorpowertrain;
  uint8_t fb_errorbattery;
  uint8_t fb_brakepedal_voltage_en;
} smart_can_msgs__msg__Fbomuxtoautonomous;

// Struct for a sequence of smart_can_msgs__msg__Fbomuxtoautonomous.
typedef struct smart_can_msgs__msg__Fbomuxtoautonomous__Sequence
{
  smart_can_msgs__msg__Fbomuxtoautonomous * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smart_can_msgs__msg__Fbomuxtoautonomous__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__STRUCT_H_
