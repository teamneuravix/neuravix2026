// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Sndrcunitbrakedata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITBRAKEDATA__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITBRAKEDATA__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Sndrcunitbrakedata __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Sndrcunitbrakedata __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Sndrcunitbrakedata_
{
  using Type = Sndrcunitbrakedata_<ContainerAllocator>;

  explicit Sndrcunitbrakedata_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rc_brakepedal_speed = 0;
      this->rc_brakepedal_acc = 0;
      this->rc_brakepedal_pos = 0;
    }
  }

  explicit Sndrcunitbrakedata_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rc_brakepedal_speed = 0;
      this->rc_brakepedal_acc = 0;
      this->rc_brakepedal_pos = 0;
    }
  }

  // field types and members
  using _rc_brakepedal_speed_type =
    uint16_t;
  _rc_brakepedal_speed_type rc_brakepedal_speed;
  using _rc_brakepedal_acc_type =
    uint16_t;
  _rc_brakepedal_acc_type rc_brakepedal_acc;
  using _rc_brakepedal_pos_type =
    uint8_t;
  _rc_brakepedal_pos_type rc_brakepedal_pos;

  // setters for named parameter idiom
  Type & set__rc_brakepedal_speed(
    const uint16_t & _arg)
  {
    this->rc_brakepedal_speed = _arg;
    return *this;
  }
  Type & set__rc_brakepedal_acc(
    const uint16_t & _arg)
  {
    this->rc_brakepedal_acc = _arg;
    return *this;
  }
  Type & set__rc_brakepedal_pos(
    const uint8_t & _arg)
  {
    this->rc_brakepedal_pos = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Sndrcunitbrakedata
    std::shared_ptr<smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Sndrcunitbrakedata
    std::shared_ptr<smart_can_msgs::msg::Sndrcunitbrakedata_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Sndrcunitbrakedata_ & other) const
  {
    if (this->rc_brakepedal_speed != other.rc_brakepedal_speed) {
      return false;
    }
    if (this->rc_brakepedal_acc != other.rc_brakepedal_acc) {
      return false;
    }
    if (this->rc_brakepedal_pos != other.rc_brakepedal_pos) {
      return false;
    }
    return true;
  }
  bool operator!=(const Sndrcunitbrakedata_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Sndrcunitbrakedata_

// alias to use template instance with default allocator
using Sndrcunitbrakedata =
  smart_can_msgs::msg::Sndrcunitbrakedata_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__SNDRCUNITBRAKEDATA__STRUCT_HPP_
