// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smart_can_msgs:msg/Fbomuxtoautonomous.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/fbomuxtoautonomous__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
smart_can_msgs__msg__Fbomuxtoautonomous__init(smart_can_msgs__msg__Fbomuxtoautonomous * msg)
{
  if (!msg) {
    return false;
  }
  // fb_emergency
  // fb_reverselight
  // fb_rightsignal
  // fb_windowresistance
  // fb_leftsignal
  // fb_interiorlight
  // fb_drl
  // fb_doorkeystatus
  // fb_brakelight
  // fb_batteryvoltage
  // fb_chargeinput
  // fb_highbeam
  // fb_lowbeam
  // fb_ignition
  // fb_hazardouslight
  // fb_vehiclestatus
  // fb_leftdoorstatus
  // fb_rightdoorstatus
  // fb_batterysoc
  // fb_errorpowertrain
  // fb_errorbattery
  // fb_brakepedal_voltage_en
  return true;
}

void
smart_can_msgs__msg__Fbomuxtoautonomous__fini(smart_can_msgs__msg__Fbomuxtoautonomous * msg)
{
  if (!msg) {
    return;
  }
  // fb_emergency
  // fb_reverselight
  // fb_rightsignal
  // fb_windowresistance
  // fb_leftsignal
  // fb_interiorlight
  // fb_drl
  // fb_doorkeystatus
  // fb_brakelight
  // fb_batteryvoltage
  // fb_chargeinput
  // fb_highbeam
  // fb_lowbeam
  // fb_ignition
  // fb_hazardouslight
  // fb_vehiclestatus
  // fb_leftdoorstatus
  // fb_rightdoorstatus
  // fb_batterysoc
  // fb_errorpowertrain
  // fb_errorbattery
  // fb_brakepedal_voltage_en
}

bool
smart_can_msgs__msg__Fbomuxtoautonomous__are_equal(const smart_can_msgs__msg__Fbomuxtoautonomous * lhs, const smart_can_msgs__msg__Fbomuxtoautonomous * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // fb_emergency
  if (lhs->fb_emergency != rhs->fb_emergency) {
    return false;
  }
  // fb_reverselight
  if (lhs->fb_reverselight != rhs->fb_reverselight) {
    return false;
  }
  // fb_rightsignal
  if (lhs->fb_rightsignal != rhs->fb_rightsignal) {
    return false;
  }
  // fb_windowresistance
  if (lhs->fb_windowresistance != rhs->fb_windowresistance) {
    return false;
  }
  // fb_leftsignal
  if (lhs->fb_leftsignal != rhs->fb_leftsignal) {
    return false;
  }
  // fb_interiorlight
  if (lhs->fb_interiorlight != rhs->fb_interiorlight) {
    return false;
  }
  // fb_drl
  if (lhs->fb_drl != rhs->fb_drl) {
    return false;
  }
  // fb_doorkeystatus
  if (lhs->fb_doorkeystatus != rhs->fb_doorkeystatus) {
    return false;
  }
  // fb_brakelight
  if (lhs->fb_brakelight != rhs->fb_brakelight) {
    return false;
  }
  // fb_batteryvoltage
  if (lhs->fb_batteryvoltage != rhs->fb_batteryvoltage) {
    return false;
  }
  // fb_chargeinput
  if (lhs->fb_chargeinput != rhs->fb_chargeinput) {
    return false;
  }
  // fb_highbeam
  if (lhs->fb_highbeam != rhs->fb_highbeam) {
    return false;
  }
  // fb_lowbeam
  if (lhs->fb_lowbeam != rhs->fb_lowbeam) {
    return false;
  }
  // fb_ignition
  if (lhs->fb_ignition != rhs->fb_ignition) {
    return false;
  }
  // fb_hazardouslight
  if (lhs->fb_hazardouslight != rhs->fb_hazardouslight) {
    return false;
  }
  // fb_vehiclestatus
  if (lhs->fb_vehiclestatus != rhs->fb_vehiclestatus) {
    return false;
  }
  // fb_leftdoorstatus
  if (lhs->fb_leftdoorstatus != rhs->fb_leftdoorstatus) {
    return false;
  }
  // fb_rightdoorstatus
  if (lhs->fb_rightdoorstatus != rhs->fb_rightdoorstatus) {
    return false;
  }
  // fb_batterysoc
  if (lhs->fb_batterysoc != rhs->fb_batterysoc) {
    return false;
  }
  // fb_errorpowertrain
  if (lhs->fb_errorpowertrain != rhs->fb_errorpowertrain) {
    return false;
  }
  // fb_errorbattery
  if (lhs->fb_errorbattery != rhs->fb_errorbattery) {
    return false;
  }
  // fb_brakepedal_voltage_en
  if (lhs->fb_brakepedal_voltage_en != rhs->fb_brakepedal_voltage_en) {
    return false;
  }
  return true;
}

bool
smart_can_msgs__msg__Fbomuxtoautonomous__copy(
  const smart_can_msgs__msg__Fbomuxtoautonomous * input,
  smart_can_msgs__msg__Fbomuxtoautonomous * output)
{
  if (!input || !output) {
    return false;
  }
  // fb_emergency
  output->fb_emergency = input->fb_emergency;
  // fb_reverselight
  output->fb_reverselight = input->fb_reverselight;
  // fb_rightsignal
  output->fb_rightsignal = input->fb_rightsignal;
  // fb_windowresistance
  output->fb_windowresistance = input->fb_windowresistance;
  // fb_leftsignal
  output->fb_leftsignal = input->fb_leftsignal;
  // fb_interiorlight
  output->fb_interiorlight = input->fb_interiorlight;
  // fb_drl
  output->fb_drl = input->fb_drl;
  // fb_doorkeystatus
  output->fb_doorkeystatus = input->fb_doorkeystatus;
  // fb_brakelight
  output->fb_brakelight = input->fb_brakelight;
  // fb_batteryvoltage
  output->fb_batteryvoltage = input->fb_batteryvoltage;
  // fb_chargeinput
  output->fb_chargeinput = input->fb_chargeinput;
  // fb_highbeam
  output->fb_highbeam = input->fb_highbeam;
  // fb_lowbeam
  output->fb_lowbeam = input->fb_lowbeam;
  // fb_ignition
  output->fb_ignition = input->fb_ignition;
  // fb_hazardouslight
  output->fb_hazardouslight = input->fb_hazardouslight;
  // fb_vehiclestatus
  output->fb_vehiclestatus = input->fb_vehiclestatus;
  // fb_leftdoorstatus
  output->fb_leftdoorstatus = input->fb_leftdoorstatus;
  // fb_rightdoorstatus
  output->fb_rightdoorstatus = input->fb_rightdoorstatus;
  // fb_batterysoc
  output->fb_batterysoc = input->fb_batterysoc;
  // fb_errorpowertrain
  output->fb_errorpowertrain = input->fb_errorpowertrain;
  // fb_errorbattery
  output->fb_errorbattery = input->fb_errorbattery;
  // fb_brakepedal_voltage_en
  output->fb_brakepedal_voltage_en = input->fb_brakepedal_voltage_en;
  return true;
}

smart_can_msgs__msg__Fbomuxtoautonomous *
smart_can_msgs__msg__Fbomuxtoautonomous__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Fbomuxtoautonomous * msg = (smart_can_msgs__msg__Fbomuxtoautonomous *)allocator.allocate(sizeof(smart_can_msgs__msg__Fbomuxtoautonomous), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smart_can_msgs__msg__Fbomuxtoautonomous));
  bool success = smart_can_msgs__msg__Fbomuxtoautonomous__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smart_can_msgs__msg__Fbomuxtoautonomous__destroy(smart_can_msgs__msg__Fbomuxtoautonomous * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smart_can_msgs__msg__Fbomuxtoautonomous__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__init(smart_can_msgs__msg__Fbomuxtoautonomous__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Fbomuxtoautonomous * data = NULL;

  if (size) {
    data = (smart_can_msgs__msg__Fbomuxtoautonomous *)allocator.zero_allocate(size, sizeof(smart_can_msgs__msg__Fbomuxtoautonomous), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smart_can_msgs__msg__Fbomuxtoautonomous__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smart_can_msgs__msg__Fbomuxtoautonomous__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__fini(smart_can_msgs__msg__Fbomuxtoautonomous__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      smart_can_msgs__msg__Fbomuxtoautonomous__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

smart_can_msgs__msg__Fbomuxtoautonomous__Sequence *
smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Fbomuxtoautonomous__Sequence * array = (smart_can_msgs__msg__Fbomuxtoautonomous__Sequence *)allocator.allocate(sizeof(smart_can_msgs__msg__Fbomuxtoautonomous__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__destroy(smart_can_msgs__msg__Fbomuxtoautonomous__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__are_equal(const smart_can_msgs__msg__Fbomuxtoautonomous__Sequence * lhs, const smart_can_msgs__msg__Fbomuxtoautonomous__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smart_can_msgs__msg__Fbomuxtoautonomous__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smart_can_msgs__msg__Fbomuxtoautonomous__Sequence__copy(
  const smart_can_msgs__msg__Fbomuxtoautonomous__Sequence * input,
  smart_can_msgs__msg__Fbomuxtoautonomous__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smart_can_msgs__msg__Fbomuxtoautonomous);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smart_can_msgs__msg__Fbomuxtoautonomous * data =
      (smart_can_msgs__msg__Fbomuxtoautonomous *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smart_can_msgs__msg__Fbomuxtoautonomous__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smart_can_msgs__msg__Fbomuxtoautonomous__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smart_can_msgs__msg__Fbomuxtoautonomous__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
