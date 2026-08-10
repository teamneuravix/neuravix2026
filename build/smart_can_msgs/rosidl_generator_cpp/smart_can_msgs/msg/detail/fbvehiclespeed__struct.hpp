// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Fbvehiclespeed.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Fbvehiclespeed __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Fbvehiclespeed __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Fbvehiclespeed_
{
  using Type = Fbvehiclespeed_<ContainerAllocator>;

  explicit Fbvehiclespeed_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->fb_vehiclespeed_kmh = 0;
      this->fb_reelvehiclespeed_kmh = 0;
      this->fb_reelvehiclespeed_ms = 0;
    }
  }

  explicit Fbvehiclespeed_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->fb_vehiclespeed_kmh = 0;
      this->fb_reelvehiclespeed_kmh = 0;
      this->fb_reelvehiclespeed_ms = 0;
    }
  }

  // field types and members
  using _fb_vehiclespeed_kmh_type =
    uint8_t;
  _fb_vehiclespeed_kmh_type fb_vehiclespeed_kmh;
  using _fb_reelvehiclespeed_kmh_type =
    uint8_t;
  _fb_reelvehiclespeed_kmh_type fb_reelvehiclespeed_kmh;
  using _fb_reelvehiclespeed_ms_type =
    uint8_t;
  _fb_reelvehiclespeed_ms_type fb_reelvehiclespeed_ms;

  // setters for named parameter idiom
  Type & set__fb_vehiclespeed_kmh(
    const uint8_t & _arg)
  {
    this->fb_vehiclespeed_kmh = _arg;
    return *this;
  }
  Type & set__fb_reelvehiclespeed_kmh(
    const uint8_t & _arg)
  {
    this->fb_reelvehiclespeed_kmh = _arg;
    return *this;
  }
  Type & set__fb_reelvehiclespeed_ms(
    const uint8_t & _arg)
  {
    this->fb_reelvehiclespeed_ms = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Fbvehiclespeed
    std::shared_ptr<smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Fbvehiclespeed
    std::shared_ptr<smart_can_msgs::msg::Fbvehiclespeed_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Fbvehiclespeed_ & other) const
  {
    if (this->fb_vehiclespeed_kmh != other.fb_vehiclespeed_kmh) {
      return false;
    }
    if (this->fb_reelvehiclespeed_kmh != other.fb_reelvehiclespeed_kmh) {
      return false;
    }
    if (this->fb_reelvehiclespeed_ms != other.fb_reelvehiclespeed_ms) {
      return false;
    }
    return true;
  }
  bool operator!=(const Fbvehiclespeed_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Fbvehiclespeed_

// alias to use template instance with default allocator
using Fbvehiclespeed =
  smart_can_msgs::msg::Fbvehiclespeed_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBVEHICLESPEED__STRUCT_HPP_
