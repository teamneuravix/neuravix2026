// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Autonomoussteeringmotcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Autonomoussteeringmotcontrol __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Autonomoussteeringmotcontrol __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Autonomoussteeringmotcontrol_
{
  using Type = Autonomoussteeringmotcontrol_<ContainerAllocator>;

  explicit Autonomoussteeringmotcontrol_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->autonomous_steeringmot_en = 0;
      this->autonomous_steeringmot_pwm = 0;
    }
  }

  explicit Autonomoussteeringmotcontrol_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->autonomous_steeringmot_en = 0;
      this->autonomous_steeringmot_pwm = 0;
    }
  }

  // field types and members
  using _autonomous_steeringmot_en_type =
    uint8_t;
  _autonomous_steeringmot_en_type autonomous_steeringmot_en;
  using _autonomous_steeringmot_pwm_type =
    uint8_t;
  _autonomous_steeringmot_pwm_type autonomous_steeringmot_pwm;

  // setters for named parameter idiom
  Type & set__autonomous_steeringmot_en(
    const uint8_t & _arg)
  {
    this->autonomous_steeringmot_en = _arg;
    return *this;
  }
  Type & set__autonomous_steeringmot_pwm(
    const uint8_t & _arg)
  {
    this->autonomous_steeringmot_pwm = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Autonomoussteeringmotcontrol
    std::shared_ptr<smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Autonomoussteeringmotcontrol
    std::shared_ptr<smart_can_msgs::msg::Autonomoussteeringmotcontrol_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Autonomoussteeringmotcontrol_ & other) const
  {
    if (this->autonomous_steeringmot_en != other.autonomous_steeringmot_en) {
      return false;
    }
    if (this->autonomous_steeringmot_pwm != other.autonomous_steeringmot_pwm) {
      return false;
    }
    return true;
  }
  bool operator!=(const Autonomoussteeringmotcontrol_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Autonomoussteeringmotcontrol_

// alias to use template instance with default allocator
using Autonomoussteeringmotcontrol =
  smart_can_msgs::msg::Autonomoussteeringmotcontrol_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSSTEERINGMOTCONTROL__STRUCT_HPP_
