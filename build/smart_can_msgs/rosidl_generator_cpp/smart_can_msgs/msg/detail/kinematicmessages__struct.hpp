// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Kinematicmessages.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__KINEMATICMESSAGES__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__KINEMATICMESSAGES__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Kinematicmessages __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Kinematicmessages __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Kinematicmessages_
{
  using Type = Kinematicmessages_<ContainerAllocator>;

  explicit Kinematicmessages_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->joint_type = 0;
      this->angle = 0.0f;
      this->angle_y = 0.0f;
      this->angular_velocity = 0.0f;
      this->link_length = 0.0f;
    }
  }

  explicit Kinematicmessages_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->joint_type = 0;
      this->angle = 0.0f;
      this->angle_y = 0.0f;
      this->angular_velocity = 0.0f;
      this->link_length = 0.0f;
    }
  }

  // field types and members
  using _joint_type_type =
    uint8_t;
  _joint_type_type joint_type;
  using _angle_type =
    float;
  _angle_type angle;
  using _angle_y_type =
    float;
  _angle_y_type angle_y;
  using _angular_velocity_type =
    float;
  _angular_velocity_type angular_velocity;
  using _link_length_type =
    float;
  _link_length_type link_length;

  // setters for named parameter idiom
  Type & set__joint_type(
    const uint8_t & _arg)
  {
    this->joint_type = _arg;
    return *this;
  }
  Type & set__angle(
    const float & _arg)
  {
    this->angle = _arg;
    return *this;
  }
  Type & set__angle_y(
    const float & _arg)
  {
    this->angle_y = _arg;
    return *this;
  }
  Type & set__angular_velocity(
    const float & _arg)
  {
    this->angular_velocity = _arg;
    return *this;
  }
  Type & set__link_length(
    const float & _arg)
  {
    this->link_length = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Kinematicmessages
    std::shared_ptr<smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Kinematicmessages
    std::shared_ptr<smart_can_msgs::msg::Kinematicmessages_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Kinematicmessages_ & other) const
  {
    if (this->joint_type != other.joint_type) {
      return false;
    }
    if (this->angle != other.angle) {
      return false;
    }
    if (this->angle_y != other.angle_y) {
      return false;
    }
    if (this->angular_velocity != other.angular_velocity) {
      return false;
    }
    if (this->link_length != other.link_length) {
      return false;
    }
    return true;
  }
  bool operator!=(const Kinematicmessages_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Kinematicmessages_

// alias to use template instance with default allocator
using Kinematicmessages =
  smart_can_msgs::msg::Kinematicmessages_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__KINEMATICMESSAGES__STRUCT_HPP_
