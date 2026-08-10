// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from smart_can_msgs:msg/Sndrcunitsteeringdata.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "smart_can_msgs/msg/detail/sndrcunitsteeringdata__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace smart_can_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void Sndrcunitsteeringdata_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) smart_can_msgs::msg::Sndrcunitsteeringdata(_init);
}

void Sndrcunitsteeringdata_fini_function(void * message_memory)
{
  auto typed_message = static_cast<smart_can_msgs::msg::Sndrcunitsteeringdata *>(message_memory);
  typed_message->~Sndrcunitsteeringdata();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember Sndrcunitsteeringdata_message_member_array[4] = {
  {
    "rc_steering_rightlimit",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smart_can_msgs::msg::Sndrcunitsteeringdata, rc_steering_rightlimit),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "rc_steering_leftlimit",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smart_can_msgs::msg::Sndrcunitsteeringdata, rc_steering_leftlimit),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "rc_steeringpwm",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT16,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smart_can_msgs::msg::Sndrcunitsteeringdata, rc_steeringpwm),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "rc_steeringdirection",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(smart_can_msgs::msg::Sndrcunitsteeringdata, rc_steeringdirection),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers Sndrcunitsteeringdata_message_members = {
  "smart_can_msgs::msg",  // message namespace
  "Sndrcunitsteeringdata",  // message name
  4,  // number of fields
  sizeof(smart_can_msgs::msg::Sndrcunitsteeringdata),
  Sndrcunitsteeringdata_message_member_array,  // message members
  Sndrcunitsteeringdata_init_function,  // function to initialize message memory (memory has to be allocated)
  Sndrcunitsteeringdata_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t Sndrcunitsteeringdata_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &Sndrcunitsteeringdata_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace smart_can_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<smart_can_msgs::msg::Sndrcunitsteeringdata>()
{
  return &::smart_can_msgs::msg::rosidl_typesupport_introspection_cpp::Sndrcunitsteeringdata_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, smart_can_msgs, msg, Sndrcunitsteeringdata)() {
  return &::smart_can_msgs::msg::rosidl_typesupport_introspection_cpp::Sndrcunitsteeringdata_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
