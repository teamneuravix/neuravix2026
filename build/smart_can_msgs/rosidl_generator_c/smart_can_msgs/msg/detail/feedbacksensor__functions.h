// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from smart_can_msgs:msg/Feedbacksensor.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__FUNCTIONS_H_
#define SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "smart_can_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "smart_can_msgs/msg/detail/feedbacksensor__struct.h"

/// Initialize msg/Feedbacksensor message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smart_can_msgs__msg__Feedbacksensor
 * )) before or use
 * smart_can_msgs__msg__Feedbacksensor__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
bool
smart_can_msgs__msg__Feedbacksensor__init(smart_can_msgs__msg__Feedbacksensor * msg);

/// Finalize msg/Feedbacksensor message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
void
smart_can_msgs__msg__Feedbacksensor__fini(smart_can_msgs__msg__Feedbacksensor * msg);

/// Create msg/Feedbacksensor message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smart_can_msgs__msg__Feedbacksensor__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
smart_can_msgs__msg__Feedbacksensor *
smart_can_msgs__msg__Feedbacksensor__create();

/// Destroy msg/Feedbacksensor message.
/**
 * It calls
 * smart_can_msgs__msg__Feedbacksensor__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
void
smart_can_msgs__msg__Feedbacksensor__destroy(smart_can_msgs__msg__Feedbacksensor * msg);

/// Check for msg/Feedbacksensor message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
bool
smart_can_msgs__msg__Feedbacksensor__are_equal(const smart_can_msgs__msg__Feedbacksensor * lhs, const smart_can_msgs__msg__Feedbacksensor * rhs);

/// Copy a msg/Feedbacksensor message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
bool
smart_can_msgs__msg__Feedbacksensor__copy(
  const smart_can_msgs__msg__Feedbacksensor * input,
  smart_can_msgs__msg__Feedbacksensor * output);

/// Initialize array of msg/Feedbacksensor messages.
/**
 * It allocates the memory for the number of elements and calls
 * smart_can_msgs__msg__Feedbacksensor__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
bool
smart_can_msgs__msg__Feedbacksensor__Sequence__init(smart_can_msgs__msg__Feedbacksensor__Sequence * array, size_t size);

/// Finalize array of msg/Feedbacksensor messages.
/**
 * It calls
 * smart_can_msgs__msg__Feedbacksensor__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
void
smart_can_msgs__msg__Feedbacksensor__Sequence__fini(smart_can_msgs__msg__Feedbacksensor__Sequence * array);

/// Create array of msg/Feedbacksensor messages.
/**
 * It allocates the memory for the array and calls
 * smart_can_msgs__msg__Feedbacksensor__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
smart_can_msgs__msg__Feedbacksensor__Sequence *
smart_can_msgs__msg__Feedbacksensor__Sequence__create(size_t size);

/// Destroy array of msg/Feedbacksensor messages.
/**
 * It calls
 * smart_can_msgs__msg__Feedbacksensor__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
void
smart_can_msgs__msg__Feedbacksensor__Sequence__destroy(smart_can_msgs__msg__Feedbacksensor__Sequence * array);

/// Check for msg/Feedbacksensor message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
bool
smart_can_msgs__msg__Feedbacksensor__Sequence__are_equal(const smart_can_msgs__msg__Feedbacksensor__Sequence * lhs, const smart_can_msgs__msg__Feedbacksensor__Sequence * rhs);

/// Copy an array of msg/Feedbacksensor messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
bool
smart_can_msgs__msg__Feedbacksensor__Sequence__copy(
  const smart_can_msgs__msg__Feedbacksensor__Sequence * input,
  smart_can_msgs__msg__Feedbacksensor__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__FUNCTIONS_H_
