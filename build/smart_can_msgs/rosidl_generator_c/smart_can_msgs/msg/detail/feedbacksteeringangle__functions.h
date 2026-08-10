// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from smart_can_msgs:msg/Feedbacksteeringangle.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__FUNCTIONS_H_
#define SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "smart_can_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "smart_can_msgs/msg/detail/feedbacksteeringangle__struct.h"

/// Initialize msg/Feedbacksteeringangle message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * smart_can_msgs__msg__Feedbacksteeringangle
 * )) before or use
 * smart_can_msgs__msg__Feedbacksteeringangle__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
bool
smart_can_msgs__msg__Feedbacksteeringangle__init(smart_can_msgs__msg__Feedbacksteeringangle * msg);

/// Finalize msg/Feedbacksteeringangle message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
void
smart_can_msgs__msg__Feedbacksteeringangle__fini(smart_can_msgs__msg__Feedbacksteeringangle * msg);

/// Create msg/Feedbacksteeringangle message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * smart_can_msgs__msg__Feedbacksteeringangle__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
smart_can_msgs__msg__Feedbacksteeringangle *
smart_can_msgs__msg__Feedbacksteeringangle__create();

/// Destroy msg/Feedbacksteeringangle message.
/**
 * It calls
 * smart_can_msgs__msg__Feedbacksteeringangle__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
void
smart_can_msgs__msg__Feedbacksteeringangle__destroy(smart_can_msgs__msg__Feedbacksteeringangle * msg);

/// Check for msg/Feedbacksteeringangle message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
bool
smart_can_msgs__msg__Feedbacksteeringangle__are_equal(const smart_can_msgs__msg__Feedbacksteeringangle * lhs, const smart_can_msgs__msg__Feedbacksteeringangle * rhs);

/// Copy a msg/Feedbacksteeringangle message.
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
smart_can_msgs__msg__Feedbacksteeringangle__copy(
  const smart_can_msgs__msg__Feedbacksteeringangle * input,
  smart_can_msgs__msg__Feedbacksteeringangle * output);

/// Initialize array of msg/Feedbacksteeringangle messages.
/**
 * It allocates the memory for the number of elements and calls
 * smart_can_msgs__msg__Feedbacksteeringangle__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
bool
smart_can_msgs__msg__Feedbacksteeringangle__Sequence__init(smart_can_msgs__msg__Feedbacksteeringangle__Sequence * array, size_t size);

/// Finalize array of msg/Feedbacksteeringangle messages.
/**
 * It calls
 * smart_can_msgs__msg__Feedbacksteeringangle__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
void
smart_can_msgs__msg__Feedbacksteeringangle__Sequence__fini(smart_can_msgs__msg__Feedbacksteeringangle__Sequence * array);

/// Create array of msg/Feedbacksteeringangle messages.
/**
 * It allocates the memory for the array and calls
 * smart_can_msgs__msg__Feedbacksteeringangle__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
smart_can_msgs__msg__Feedbacksteeringangle__Sequence *
smart_can_msgs__msg__Feedbacksteeringangle__Sequence__create(size_t size);

/// Destroy array of msg/Feedbacksteeringangle messages.
/**
 * It calls
 * smart_can_msgs__msg__Feedbacksteeringangle__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
void
smart_can_msgs__msg__Feedbacksteeringangle__Sequence__destroy(smart_can_msgs__msg__Feedbacksteeringangle__Sequence * array);

/// Check for msg/Feedbacksteeringangle message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_smart_can_msgs
bool
smart_can_msgs__msg__Feedbacksteeringangle__Sequence__are_equal(const smart_can_msgs__msg__Feedbacksteeringangle__Sequence * lhs, const smart_can_msgs__msg__Feedbacksteeringangle__Sequence * rhs);

/// Copy an array of msg/Feedbacksteeringangle messages.
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
smart_can_msgs__msg__Feedbacksteeringangle__Sequence__copy(
  const smart_can_msgs__msg__Feedbacksteeringangle__Sequence * input,
  smart_can_msgs__msg__Feedbacksteeringangle__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__FUNCTIONS_H_
