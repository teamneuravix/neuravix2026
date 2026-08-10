// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Sndrcunithandbrakedata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITHANDBRAKEDATA__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITHANDBRAKEDATA__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Sndrcunithandbrakedata __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Sndrcunithandbrakedata __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Sndrcunithandbrakedata_
{
  using Type = Sndrcunithandbrakedata_<ContainerAllocator>;

  explicit Sndrcunithandbrakedata_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rc_hb_pwmvalue = 0;
      this->rc_handbrake_press = 0;
      this->rc_handbrake_free = 0;
      this->rc_handbrakedata = 0;
    }
  }

  explicit Sndrcunithandbrakedata_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rc_hb_pwmvalue = 0;
      this->rc_handbrake_press = 0;
      this->rc_handbrake_free = 0;
      this->rc_handbrakedata = 0;
    }
  }

  // field types and members
  using _rc_hb_pwmvalue_type =
    uint16_t;
  _rc_hb_pwmvalue_type rc_hb_pwmvalue;
  using _rc_handbrake_press_type =
    uint8_t;
  _rc_handbrake_press_type rc_handbrake_press;
  using _rc_handbrake_free_type =
    uint8_t;
  _rc_handbrake_free_type rc_handbrake_free;
  using _rc_handbrakedata_type =
    uint8_t;
  _rc_handbrakedata_type rc_handbrakedata;

  // setters for named parameter idiom
  Type & set__rc_hb_pwmvalue(
    const uint16_t & _arg)
  {
    this->rc_hb_pwmvalue = _arg;
    return *this;
  }
  Type & set__rc_handbrake_press(
    const uint8_t & _arg)
  {
    this->rc_handbrake_press = _arg;
    return *this;
  }
  Type & set__rc_handbrake_free(
    const uint8_t & _arg)
  {
    this->rc_handbrake_free = _arg;
    return *this;
  }
  Type & set__rc_handbrakedata(
    const uint8_t & _arg)
  {
    this->rc_handbrakedata = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Sndrcunithandbrakedata
    std::shared_ptr<smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Sndrcunithandbrakedata
    std::shared_ptr<smart_can_msgs::msg::Sndrcunithandbrakedata_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Sndrcunithandbrakedata_ & other) const
  {
    if (this->rc_hb_pwmvalue != other.rc_hb_pwmvalue) {
      return false;
    }
    if (this->rc_handbrake_press != other.rc_handbrake_press) {
      return false;
    }
    if (this->rc_handbrake_free != other.rc_handbrake_free) {
      return false;
    }
    if (this->rc_handbrakedata != other.rc_handbrakedata) {
      return false;
    }
    return true;
  }
  bool operator!=(const Sndrcunithandbrakedata_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Sndrcunithandbrakedata_

// alias to use template instance with default allocator
using Sndrcunithandbrakedata =
  smart_can_msgs::msg::Sndrcunithandbrakedata_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITHANDBRAKEDATA__STRUCT_HPP_
