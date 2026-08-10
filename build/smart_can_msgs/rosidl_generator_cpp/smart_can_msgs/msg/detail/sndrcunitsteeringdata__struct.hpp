// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Sndrcunitsteeringdata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITSTEERINGDATA__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITSTEERINGDATA__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Sndrcunitsteeringdata __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Sndrcunitsteeringdata __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Sndrcunitsteeringdata_
{
  using Type = Sndrcunitsteeringdata_<ContainerAllocator>;

  explicit Sndrcunitsteeringdata_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rc_steering_rightlimit = 0;
      this->rc_steering_leftlimit = 0;
      this->rc_steeringpwm = 0;
      this->rc_steeringdirection = 0;
    }
  }

  explicit Sndrcunitsteeringdata_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rc_steering_rightlimit = 0;
      this->rc_steering_leftlimit = 0;
      this->rc_steeringpwm = 0;
      this->rc_steeringdirection = 0;
    }
  }

  // field types and members
  using _rc_steering_rightlimit_type =
    uint8_t;
  _rc_steering_rightlimit_type rc_steering_rightlimit;
  using _rc_steering_leftlimit_type =
    uint8_t;
  _rc_steering_leftlimit_type rc_steering_leftlimit;
  using _rc_steeringpwm_type =
    uint16_t;
  _rc_steeringpwm_type rc_steeringpwm;
  using _rc_steeringdirection_type =
    uint8_t;
  _rc_steeringdirection_type rc_steeringdirection;

  // setters for named parameter idiom
  Type & set__rc_steering_rightlimit(
    const uint8_t & _arg)
  {
    this->rc_steering_rightlimit = _arg;
    return *this;
  }
  Type & set__rc_steering_leftlimit(
    const uint8_t & _arg)
  {
    this->rc_steering_leftlimit = _arg;
    return *this;
  }
  Type & set__rc_steeringpwm(
    const uint16_t & _arg)
  {
    this->rc_steeringpwm = _arg;
    return *this;
  }
  Type & set__rc_steeringdirection(
    const uint8_t & _arg)
  {
    this->rc_steeringdirection = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Sndrcunitsteeringdata
    std::shared_ptr<smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Sndrcunitsteeringdata
    std::shared_ptr<smart_can_msgs::msg::Sndrcunitsteeringdata_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Sndrcunitsteeringdata_ & other) const
  {
    if (this->rc_steering_rightlimit != other.rc_steering_rightlimit) {
      return false;
    }
    if (this->rc_steering_leftlimit != other.rc_steering_leftlimit) {
      return false;
    }
    if (this->rc_steeringpwm != other.rc_steeringpwm) {
      return false;
    }
    if (this->rc_steeringdirection != other.rc_steeringdirection) {
      return false;
    }
    return true;
  }
  bool operator!=(const Sndrcunitsteeringdata_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Sndrcunitsteeringdata_

// alias to use template instance with default allocator
using Sndrcunitsteeringdata =
  smart_can_msgs::msg::Sndrcunitsteeringdata_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITSTEERINGDATA__STRUCT_HPP_
