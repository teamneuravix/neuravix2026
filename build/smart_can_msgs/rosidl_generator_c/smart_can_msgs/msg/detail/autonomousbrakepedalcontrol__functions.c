// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from smart_can_msgs:msg/Autonomousbrakepedalcontrol.idl
// generated code does not contain a copyright notice
#include "smart_can_msgs/msg/detail/autonomousbrakepedalcontrol__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
smart_can_msgs__msg__Autonomousbrakepedalcontrol__init(smart_can_msgs__msg__Autonomousbrakepedalcontrol * msg)
{
  if (!msg) {
    return false;
  }
  // autonomous_brakemotor_voltage
  // autonomous_brakepedalmotor_per
  // autonomous_brakepedalmotor_acc
  // autonomous_brakepedalmotor_en
  return true;
}

void
smart_can_msgs__msg__Autonomousbrakepedalcontrol__fini(smart_can_msgs__msg__Autonomousbrakepedalcontrol * msg)
{
  if (!msg) {
    return;
  }
  // autonomous_brakemotor_voltage
  // autonomous_brakepedalmotor_per
  // autonomous_brakepedalmotor_acc
  // autonomous_brakepedalmotor_en
}

bool
smart_can_msgs__msg__Autonomousbrakepedalcontrol__are_equal(const smart_can_msgs__msg__Autonomousbrakepedalcontrol * lhs, const smart_can_msgs__msg__Autonomousbrakepedalcontrol * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // autonomous_brakemotor_voltage
  if (lhs->autonomous_brakemotor_voltage != rhs->autonomous_brakemotor_voltage) {
    return false;
  }
  // autonomous_brakepedalmotor_per
  if (lhs->autonomous_brakepedalmotor_per != rhs->autonomous_brakepedalmotor_per) {
    return false;
  }
  // autonomous_brakepedalmotor_acc
  if (lhs->autonomous_brakepedalmotor_acc != rhs->autonomous_brakepedalmotor_acc) {
    return false;
  }
  // autonomous_brakepedalmotor_en
  if (lhs->autonomous_brakepedalmotor_en != rhs->autonomous_brakepedalmotor_en) {
    return false;
  }
  return true;
}

bool
smart_can_msgs__msg__Autonomousbrakepedalcontrol__copy(
  const smart_can_msgs__msg__Autonomousbrakepedalcontrol * input,
  smart_can_msgs__msg__Autonomousbrakepedalcontrol * output)
{
  if (!input || !output) {
    return false;
  }
  // autonomous_brakemotor_voltage
  output->autonomous_brakemotor_voltage = input->autonomous_brakemotor_voltage;
  // autonomous_brakepedalmotor_per
  output->autonomous_brakepedalmotor_per = input->autonomous_brakepedalmotor_per;
  // autonomous_brakepedalmotor_acc
  output->autonomous_brakepedalmotor_acc = input->autonomous_brakepedalmotor_acc;
  // autonomous_brakepedalmotor_en
  output->autonomous_brakepedalmotor_en = input->autonomous_brakepedalmotor_en;
  return true;
}

smart_can_msgs__msg__Autonomousbrakepedalcontrol *
smart_can_msgs__msg__Autonomousbrakepedalcontrol__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Autonomousbrakepedalcontrol * msg = (smart_can_msgs__msg__Autonomousbrakepedalcontrol *)allocator.allocate(sizeof(smart_can_msgs__msg__Autonomousbrakepedalcontrol), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(smart_can_msgs__msg__Autonomousbrakepedalcontrol));
  bool success = smart_can_msgs__msg__Autonomousbrakepedalcontrol__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
smart_can_msgs__msg__Autonomousbrakepedalcontrol__destroy(smart_can_msgs__msg__Autonomousbrakepedalcontrol * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    smart_can_msgs__msg__Autonomousbrakepedalcontrol__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__init(smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Autonomousbrakepedalcontrol * data = NULL;

  if (size) {
    data = (smart_can_msgs__msg__Autonomousbrakepedalcontrol *)allocator.zero_allocate(size, sizeof(smart_can_msgs__msg__Autonomousbrakepedalcontrol), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = smart_can_msgs__msg__Autonomousbrakepedalcontrol__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        smart_can_msgs__msg__Autonomousbrakepedalcontrol__fini(&data[i - 1]);
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
smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__fini(smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence * array)
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
      smart_can_msgs__msg__Autonomousbrakepedalcontrol__fini(&array->data[i]);
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

smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence *
smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence * array = (smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence *)allocator.allocate(sizeof(smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__destroy(smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__are_equal(const smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence * lhs, const smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!smart_can_msgs__msg__Autonomousbrakepedalcontrol__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence__copy(
  const smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence * input,
  smart_can_msgs__msg__Autonomousbrakepedalcontrol__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(smart_can_msgs__msg__Autonomousbrakepedalcontrol);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    smart_can_msgs__msg__Autonomousbrakepedalcontrol * data =
      (smart_can_msgs__msg__Autonomousbrakepedalcontrol *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!smart_can_msgs__msg__Autonomousbrakepedalcontrol__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          smart_can_msgs__msg__Autonomousbrakepedalcontrol__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!smart_can_msgs__msg__Autonomousbrakepedalcontrol__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
