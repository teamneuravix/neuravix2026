// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smart_can_msgs:msg/Rcunittoomux.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/rcunittoomux__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
smart_can_msgs__msg__Rcunittoomux__init(smart_can_msgs__msg__Rcunittoomux * msg)
{
  if (!msg) {
    return false;
  }
  // autonomous_emergency
  // rc_windowresintance
  // rc_interiorlight
  // rc_reverselight
  // rc_drl
  // rc_brakelight
  // autonomous_door_open
  // autonomous_door_close
  // rc_signalstatus
  // rc_lowbeam
  // rc_highbeam
  // rc_selectiongear
  // rc_ignition
  return true;
}

void
smart_can_msgs__msg__Rcunittoomux__fini(smart_can_msgs__msg__Rcunittoomux * msg)
{
  if (!msg) {
    return;
  }
  // autonomous_emergency
  // rc_windowresintance
  // rc_interiorlight
  // rc_reverselight
  // rc_drl
  // rc_brakelight
  // autonomous_door_open
  // autonomous_door_close
  // rc_signalstatus
  // rc_lowbeam
  // rc_highbeam
  // rc_selectiongear
  // rc_ignition
}

bool
smart_can_msgs__msg__Rcunittoomux__are_equal(const smart_can_msgs__msg__Rcunittoomux * lhs, const smart_can_msgs__msg__Rcunittoomux * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // autonomous_emergency
  if (lhs->autonomous_emergency != rhs->autonomous_emergency) {
    return false;
  }
  // rc_windowresintance
  if (lhs->rc_windowresintance != rhs->rc_windowresintance) {
    return false;
  }
  // rc_interiorlight
  if (lhs->rc_interiorlight != rhs->rc_interiorlight) {
    return false;
  }
  // rc_reverselight
  if (lhs->rc_reverselight != rhs->rc_reverselight) {
    return false;
  }
  // rc_drl
  if (lhs->rc_drl != rhs->rc_drl) {
    return false;
  }
  // rc_brakelight
  if (lhs->rc_brakelight != rhs->rc_brakelight) {
    return false;
  }
  // autonomous_door_open
  if (lhs->autonomous_door_open != rhs->autonomous_door_open) {
    return false;
  }
  // autonomous_door_close
  if (lhs->autonomous_door_close != rhs->autonomous_door_close) {
    return false;
  }
  // rc_signalstatus
  if (lhs->rc_signalstatus != rhs->rc_signalstatus) {
    return false;
  }
  // rc_lowbeam
  if (lhs->rc_lowbeam != rhs->rc_lowbeam) {
    return false;
  }
  // rc_highbeam
  if (lhs->rc_highbeam != rhs->rc_highbeam) {
    return false;
  }
  // rc_selectiongear
  if (lhs->rc_selectiongear != rhs->rc_selectiongear) {
    return false;
  }
  // rc_ignition
  if (lhs->rc_ignition != rhs->rc_ignition) {
    return false;
  }
  return true;
}

bool
smart_can_msgs__msg__Rcunittoomux__copy(
  const smart_can_msgs__msg__Rcunittoomux * input,
  smart_can_msgs__msg__Rcunittoomux * output)
{
  if (!input || !output) {
    return false;
  }
  // autonomous_emergency
  output->autonomous_emergency = input->autonomous_emergency;
  // rc_windowresintance
  output->rc_windowresintance = input->rc_windowresintance;
  // rc_interiorlight
  output->rc_interiorlight = input->rc_interiorlight;
  // rc_reverselight
  output->rc_reverselight = input->rc_reverselight;
  // rc_drl
  output->rc_drl = input->rc_drl;
  // rc_brakelight
  output->rc_brakelight = input->rc_brakelight;
  // autonomous_door_open
  output->autonomous_door_open = input->autonomous_door_open;
  // autonomous_door_close
  output->autonomous_door_close = input->autonomous_door_close;
  // rc_signalstatus
  output->rc_signalstatus = input->rc_signalstatus;
  // rc_lowbeam
  output->rc_lowbeam = input->rc_lowbeam;
  // rc_highbeam
  output->rc_highbeam = input->rc_highbeam;
  // rc_selectiongear
  output->rc_selectiongear = input->rc_selectiongear;
  // rc_ignition
  output->rc_ignition = input->rc_ignition;
  return true;
}

smart_can_msgs__msg__Rcunittoomux *
smart_can_msgs__msg__Rcunittoomux__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Rcunittoomux * msg = (smart_can_msgs__msg__Rcunittoomux *)allocator.allocate(sizeof(smart_can_msgs__msg__Rcunittoomux), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smart_can_msgs__msg__Rcunittoomux));
  bool success = smart_can_msgs__msg__Rcunittoomux__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smart_can_msgs__msg__Rcunittoomux__destroy(smart_can_msgs__msg__Rcunittoomux * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smart_can_msgs__msg__Rcunittoomux__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smart_can_msgs__msg__Rcunittoomux__Sequence__init(smart_can_msgs__msg__Rcunittoomux__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Rcunittoomux * data = NULL;

  if (size) {
    data = (smart_can_msgs__msg__Rcunittoomux *)allocator.zero_allocate(size, sizeof(smart_can_msgs__msg__Rcunittoomux), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smart_can_msgs__msg__Rcunittoomux__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smart_can_msgs__msg__Rcunittoomux__fini(&data[i - 1]);
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
smart_can_msgs__msg__Rcunittoomux__Sequence__fini(smart_can_msgs__msg__Rcunittoomux__Sequence * array)
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
      smart_can_msgs__msg__Rcunittoomux__fini(&array->data[i]);
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

smart_can_msgs__msg__Rcunittoomux__Sequence *
smart_can_msgs__msg__Rcunittoomux__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Rcunittoomux__Sequence * array = (smart_can_msgs__msg__Rcunittoomux__Sequence *)allocator.allocate(sizeof(smart_can_msgs__msg__Rcunittoomux__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smart_can_msgs__msg__Rcunittoomux__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smart_can_msgs__msg__Rcunittoomux__Sequence__destroy(smart_can_msgs__msg__Rcunittoomux__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smart_can_msgs__msg__Rcunittoomux__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smart_can_msgs__msg__Rcunittoomux__Sequence__are_equal(const smart_can_msgs__msg__Rcunittoomux__Sequence * lhs, const smart_can_msgs__msg__Rcunittoomux__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smart_can_msgs__msg__Rcunittoomux__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smart_can_msgs__msg__Rcunittoomux__Sequence__copy(
  const smart_can_msgs__msg__Rcunittoomux__Sequence * input,
  smart_can_msgs__msg__Rcunittoomux__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smart_can_msgs__msg__Rcunittoomux);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smart_can_msgs__msg__Rcunittoomux * data =
      (smart_can_msgs__msg__Rcunittoomux *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smart_can_msgs__msg__Rcunittoomux__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smart_can_msgs__msg__Rcunittoomux__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smart_can_msgs__msg__Rcunittoomux__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
