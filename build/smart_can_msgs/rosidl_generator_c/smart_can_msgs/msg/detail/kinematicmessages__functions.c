// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smart_can_msgs:msg/Kinematicmessages.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/kinematicmessages__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
smart_can_msgs__msg__Kinematicmessages__init(smart_can_msgs__msg__Kinematicmessages * msg)
{
  if (!msg) {
    return false;
  }
  // joint_type
  // angle
  // angle_y
  // angular_velocity
  // link_length
  return true;
}

void
smart_can_msgs__msg__Kinematicmessages__fini(smart_can_msgs__msg__Kinematicmessages * msg)
{
  if (!msg) {
    return;
  }
  // joint_type
  // angle
  // angle_y
  // angular_velocity
  // link_length
}

bool
smart_can_msgs__msg__Kinematicmessages__are_equal(const smart_can_msgs__msg__Kinematicmessages * lhs, const smart_can_msgs__msg__Kinematicmessages * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // joint_type
  if (lhs->joint_type != rhs->joint_type) {
    return false;
  }
  // angle
  if (lhs->angle != rhs->angle) {
    return false;
  }
  // angle_y
  if (lhs->angle_y != rhs->angle_y) {
    return false;
  }
  // angular_velocity
  if (lhs->angular_velocity != rhs->angular_velocity) {
    return false;
  }
  // link_length
  if (lhs->link_length != rhs->link_length) {
    return false;
  }
  return true;
}

bool
smart_can_msgs__msg__Kinematicmessages__copy(
  const smart_can_msgs__msg__Kinematicmessages * input,
  smart_can_msgs__msg__Kinematicmessages * output)
{
  if (!input || !output) {
    return false;
  }
  // joint_type
  output->joint_type = input->joint_type;
  // angle
  output->angle = input->angle;
  // angle_y
  output->angle_y = input->angle_y;
  // angular_velocity
  output->angular_velocity = input->angular_velocity;
  // link_length
  output->link_length = input->link_length;
  return true;
}

smart_can_msgs__msg__Kinematicmessages *
smart_can_msgs__msg__Kinematicmessages__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Kinematicmessages * msg = (smart_can_msgs__msg__Kinematicmessages *)allocator.allocate(sizeof(smart_can_msgs__msg__Kinematicmessages), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smart_can_msgs__msg__Kinematicmessages));
  bool success = smart_can_msgs__msg__Kinematicmessages__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smart_can_msgs__msg__Kinematicmessages__destroy(smart_can_msgs__msg__Kinematicmessages * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smart_can_msgs__msg__Kinematicmessages__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smart_can_msgs__msg__Kinematicmessages__Sequence__init(smart_can_msgs__msg__Kinematicmessages__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Kinematicmessages * data = NULL;

  if (size) {
    data = (smart_can_msgs__msg__Kinematicmessages *)allocator.zero_allocate(size, sizeof(smart_can_msgs__msg__Kinematicmessages), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smart_can_msgs__msg__Kinematicmessages__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smart_can_msgs__msg__Kinematicmessages__fini(&data[i - 1]);
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
smart_can_msgs__msg__Kinematicmessages__Sequence__fini(smart_can_msgs__msg__Kinematicmessages__Sequence * array)
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
      smart_can_msgs__msg__Kinematicmessages__fini(&array->data[i]);
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

smart_can_msgs__msg__Kinematicmessages__Sequence *
smart_can_msgs__msg__Kinematicmessages__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Kinematicmessages__Sequence * array = (smart_can_msgs__msg__Kinematicmessages__Sequence *)allocator.allocate(sizeof(smart_can_msgs__msg__Kinematicmessages__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smart_can_msgs__msg__Kinematicmessages__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smart_can_msgs__msg__Kinematicmessages__Sequence__destroy(smart_can_msgs__msg__Kinematicmessages__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smart_can_msgs__msg__Kinematicmessages__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smart_can_msgs__msg__Kinematicmessages__Sequence__are_equal(const smart_can_msgs__msg__Kinematicmessages__Sequence * lhs, const smart_can_msgs__msg__Kinematicmessages__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smart_can_msgs__msg__Kinematicmessages__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smart_can_msgs__msg__Kinematicmessages__Sequence__copy(
  const smart_can_msgs__msg__Kinematicmessages__Sequence * input,
  smart_can_msgs__msg__Kinematicmessages__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smart_can_msgs__msg__Kinematicmessages);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smart_can_msgs__msg__Kinematicmessages * data =
      (smart_can_msgs__msg__Kinematicmessages *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smart_can_msgs__msg__Kinematicmessages__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smart_can_msgs__msg__Kinematicmessages__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smart_can_msgs__msg__Kinematicmessages__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
