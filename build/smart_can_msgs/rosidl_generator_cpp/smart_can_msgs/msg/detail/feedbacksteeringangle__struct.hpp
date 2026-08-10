// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Feedbacksteeringangle.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Feedbacksteeringangle __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Feedbacksteeringangle __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Feedbacksteeringangle_
{
  using Type = Feedbacksteeringangle_<ContainerAllocator>;

  explicit Feedbacksteeringangle_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->feedbacksteeringangle = 0;
      this->feedbackbrakepedalangle = 0;
    }
  }

  explicit Feedbacksteeringangle_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->feedbacksteeringangle = 0;
      this->feedbackbrakepedalangle = 0;
    }
  }

  // field types and members
  using _feedbacksteeringangle_type =
    int8_t;
  _feedbacksteeringangle_type feedbacksteeringangle;
  using _feedbackbrakepedalangle_type =
    int8_t;
  _feedbackbrakepedalangle_type feedbackbrakepedalangle;

  // setters for named parameter idiom
  Type & set__feedbacksteeringangle(
    const int8_t & _arg)
  {
    this->feedbacksteeringangle = _arg;
    return *this;
  }
  Type & set__feedbackbrakepedalangle(
    const int8_t & _arg)
  {
    this->feedbackbrakepedalangle = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Feedbacksteeringangle
    std::shared_ptr<smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Feedbacksteeringangle
    std::shared_ptr<smart_can_msgs::msg::Feedbacksteeringangle_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Feedbacksteeringangle_ & other) const
  {
    if (this->feedbacksteeringangle != other.feedbacksteeringangle) {
      return false;
    }
    if (this->feedbackbrakepedalangle != other.feedbackbrakepedalangle) {
      return false;
    }
    return true;
  }
  bool operator!=(const Feedbacksteeringangle_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Feedbacksteeringangle_

// alias to use template instance with default allocator
using Feedbacksteeringangle =
  smart_can_msgs::msg::Feedbacksteeringangle_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSTEERINGANGLE__STRUCT_HPP_
