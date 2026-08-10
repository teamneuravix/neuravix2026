// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smart_can_msgs:msg/Autonomousheardbit.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/autonomousheardbit__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
smart_can_msgs__msg__Autonomousheardbit__init(smart_can_msgs__msg__Autonomousheardbit * msg)
{
  if (!msg) {
    return false;
  }
  // autonomousmanuelselect
  return true;
}

void
smart_can_msgs__msg__Autonomousheardbit__fini(smart_can_msgs__msg__Autonomousheardbit * msg)
{
  if (!msg) {
    return;
  }
  // autonomousmanuelselect
}

bool
smart_can_msgs__msg__Autonomousheardbit__are_equal(const smart_can_msgs__msg__Autonomousheardbit * lhs, const smart_can_msgs__msg__Autonomousheardbit * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // autonomousmanuelselect
  if (lhs->autonomousmanuelselect != rhs->autonomousmanuelselect) {
    return false;
  }
  return true;
}

bool
smart_can_msgs__msg__Autonomousheardbit__copy(
  const smart_can_msgs__msg__Autonomousheardbit * input,
  smart_can_msgs__msg__Autonomousheardbit * output)
{
  if (!input || !output) {
    return false;
  }
  // autonomousmanuelselect
  output->autonomousmanuelselect = input->autonomousmanuelselect;
  return true;
}

smart_can_msgs__msg__Autonomousheardbit *
smart_can_msgs__msg__Autonomousheardbit__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Autonomousheardbit * msg = (smart_can_msgs__msg__Autonomousheardbit *)allocator.allocate(sizeof(smart_can_msgs__msg__Autonomousheardbit), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smart_can_msgs__msg__Autonomousheardbit));
  bool success = smart_can_msgs__msg__Autonomousheardbit__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smart_can_msgs__msg__Autonomousheardbit__destroy(smart_can_msgs__msg__Autonomousheardbit * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smart_can_msgs__msg__Autonomousheardbit__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smart_can_msgs__msg__Autonomousheardbit__Sequence__init(smart_can_msgs__msg__Autonomousheardbit__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Autonomousheardbit * data = NULL;

  if (size) {
    data = (smart_can_msgs__msg__Autonomousheardbit *)allocator.zero_allocate(size, sizeof(smart_can_msgs__msg__Autonomousheardbit), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smart_can_msgs__msg__Autonomousheardbit__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smart_can_msgs__msg__Autonomousheardbit__fini(&data[i - 1]);
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
smart_can_msgs__msg__Autonomousheardbit__Sequence__fini(smart_can_msgs__msg__Autonomousheardbit__Sequence * array)
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
      smart_can_msgs__msg__Autonomousheardbit__fini(&array->data[i]);
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

smart_can_msgs__msg__Autonomousheardbit__Sequence *
smart_can_msgs__msg__Autonomousheardbit__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Autonomousheardbit__Sequence * array = (smart_can_msgs__msg__Autonomousheardbit__Sequence *)allocator.allocate(sizeof(smart_can_msgs__msg__Autonomousheardbit__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smart_can_msgs__msg__Autonomousheardbit__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smart_can_msgs__msg__Autonomousheardbit__Sequence__destroy(smart_can_msgs__msg__Autonomousheardbit__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smart_can_msgs__msg__Autonomousheardbit__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smart_can_msgs__msg__Autonomousheardbit__Sequence__are_equal(const smart_can_msgs__msg__Autonomousheardbit__Sequence * lhs, const smart_can_msgs__msg__Autonomousheardbit__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smart_can_msgs__msg__Autonomousheardbit__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smart_can_msgs__msg__Autonomousheardbit__Sequence__copy(
  const smart_can_msgs__msg__Autonomousheardbit__Sequence * input,
  smart_can_msgs__msg__Autonomousheardbit__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smart_can_msgs__msg__Autonomousheardbit);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smart_can_msgs__msg__Autonomousheardbit * data =
      (smart_can_msgs__msg__Autonomousheardbit *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smart_can_msgs__msg__Autonomousheardbit__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smart_can_msgs__msg__Autonomousheardbit__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smart_can_msgs__msg__Autonomousheardbit__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
