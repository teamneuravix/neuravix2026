// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smart_can_msgs:msg/Feedbacksensor.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/feedbacksensor__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
smart_can_msgs__msg__Feedbacksensor__init(smart_can_msgs__msg__Feedbacksensor * msg)
{
  if (!msg) {
    return false;
  }
  // steeringanglesensorhamdata
  // brakepedalsensorhamdata
  // handbrakesensor
  // handbrakesensor_hamdata
  // indir
  // kaldir
  // butonindir
  // butonkaldir
  return true;
}

void
smart_can_msgs__msg__Feedbacksensor__fini(smart_can_msgs__msg__Feedbacksensor * msg)
{
  if (!msg) {
    return;
  }
  // steeringanglesensorhamdata
  // brakepedalsensorhamdata
  // handbrakesensor
  // handbrakesensor_hamdata
  // indir
  // kaldir
  // butonindir
  // butonkaldir
}

bool
smart_can_msgs__msg__Feedbacksensor__are_equal(const smart_can_msgs__msg__Feedbacksensor * lhs, const smart_can_msgs__msg__Feedbacksensor * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // steeringanglesensorhamdata
  if (lhs->steeringanglesensorhamdata != rhs->steeringanglesensorhamdata) {
    return false;
  }
  // brakepedalsensorhamdata
  if (lhs->brakepedalsensorhamdata != rhs->brakepedalsensorhamdata) {
    return false;
  }
  // handbrakesensor
  if (lhs->handbrakesensor != rhs->handbrakesensor) {
    return false;
  }
  // handbrakesensor_hamdata
  if (lhs->handbrakesensor_hamdata != rhs->handbrakesensor_hamdata) {
    return false;
  }
  // indir
  if (lhs->indir != rhs->indir) {
    return false;
  }
  // kaldir
  if (lhs->kaldir != rhs->kaldir) {
    return false;
  }
  // butonindir
  if (lhs->butonindir != rhs->butonindir) {
    return false;
  }
  // butonkaldir
  if (lhs->butonkaldir != rhs->butonkaldir) {
    return false;
  }
  return true;
}

bool
smart_can_msgs__msg__Feedbacksensor__copy(
  const smart_can_msgs__msg__Feedbacksensor * input,
  smart_can_msgs__msg__Feedbacksensor * output)
{
  if (!input || !output) {
    return false;
  }
  // steeringanglesensorhamdata
  output->steeringanglesensorhamdata = input->steeringanglesensorhamdata;
  // brakepedalsensorhamdata
  output->brakepedalsensorhamdata = input->brakepedalsensorhamdata;
  // handbrakesensor
  output->handbrakesensor = input->handbrakesensor;
  // handbrakesensor_hamdata
  output->handbrakesensor_hamdata = input->handbrakesensor_hamdata;
  // indir
  output->indir = input->indir;
  // kaldir
  output->kaldir = input->kaldir;
  // butonindir
  output->butonindir = input->butonindir;
  // butonkaldir
  output->butonkaldir = input->butonkaldir;
  return true;
}

smart_can_msgs__msg__Feedbacksensor *
smart_can_msgs__msg__Feedbacksensor__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Feedbacksensor * msg = (smart_can_msgs__msg__Feedbacksensor *)allocator.allocate(sizeof(smart_can_msgs__msg__Feedbacksensor), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smart_can_msgs__msg__Feedbacksensor));
  bool success = smart_can_msgs__msg__Feedbacksensor__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smart_can_msgs__msg__Feedbacksensor__destroy(smart_can_msgs__msg__Feedbacksensor * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smart_can_msgs__msg__Feedbacksensor__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smart_can_msgs__msg__Feedbacksensor__Sequence__init(smart_can_msgs__msg__Feedbacksensor__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Feedbacksensor * data = NULL;

  if (size) {
    data = (smart_can_msgs__msg__Feedbacksensor *)allocator.zero_allocate(size, sizeof(smart_can_msgs__msg__Feedbacksensor), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smart_can_msgs__msg__Feedbacksensor__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smart_can_msgs__msg__Feedbacksensor__fini(&data[i - 1]);
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
smart_can_msgs__msg__Feedbacksensor__Sequence__fini(smart_can_msgs__msg__Feedbacksensor__Sequence * array)
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
      smart_can_msgs__msg__Feedbacksensor__fini(&array->data[i]);
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

smart_can_msgs__msg__Feedbacksensor__Sequence *
smart_can_msgs__msg__Feedbacksensor__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Feedbacksensor__Sequence * array = (smart_can_msgs__msg__Feedbacksensor__Sequence *)allocator.allocate(sizeof(smart_can_msgs__msg__Feedbacksensor__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smart_can_msgs__msg__Feedbacksensor__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smart_can_msgs__msg__Feedbacksensor__Sequence__destroy(smart_can_msgs__msg__Feedbacksensor__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smart_can_msgs__msg__Feedbacksensor__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smart_can_msgs__msg__Feedbacksensor__Sequence__are_equal(const smart_can_msgs__msg__Feedbacksensor__Sequence * lhs, const smart_can_msgs__msg__Feedbacksensor__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smart_can_msgs__msg__Feedbacksensor__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smart_can_msgs__msg__Feedbacksensor__Sequence__copy(
  const smart_can_msgs__msg__Feedbacksensor__Sequence * input,
  smart_can_msgs__msg__Feedbacksensor__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smart_can_msgs__msg__Feedbacksensor);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smart_can_msgs__msg__Feedbacksensor * data =
      (smart_can_msgs__msg__Feedbacksensor *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smart_can_msgs__msg__Feedbacksensor__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smart_can_msgs__msg__Feedbacksensor__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smart_can_msgs__msg__Feedbacksensor__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
