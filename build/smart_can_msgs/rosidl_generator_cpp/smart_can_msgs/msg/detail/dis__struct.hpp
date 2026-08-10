// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Dis.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__DIS__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__DIS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Dis __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Dis __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Dis_
{
  using Type = Dis_<ContainerAllocator>;

  explicit Dis_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->angle = 0.0f;
    }
  }

  explicit Dis_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->angle = 0.0f;
    }
  }

  // field types and members
  using _angle_type =
    float;
  _angle_type angle;

  // setters for named parameter idiom
  Type & set__angle(
    const float & _arg)
  {
    this->angle = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Dis_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Dis_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Dis_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Dis_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Dis_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Dis_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Dis_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Dis_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Dis_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Dis_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Dis
    std::shared_ptr<smart_can_msgs::msg::Dis_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Dis
    std::shared_ptr<smart_can_msgs::msg::Dis_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Dis_ & other) const
  {
    if (this->angle != other.angle) {
      return false;
    }
    return true;
  }
  bool operator!=(const Dis_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Dis_

// alias to use template instance with default allocator
using Dis =
  smart_can_msgs::msg::Dis_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__DIS__STRUCT_HPP_
