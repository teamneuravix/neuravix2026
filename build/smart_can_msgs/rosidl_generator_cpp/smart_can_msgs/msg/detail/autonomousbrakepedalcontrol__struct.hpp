// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Autonomousbrakepedalcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSBRAKEPEDALCONTROL__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSBRAKEPEDALCONTROL__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Autonomousbrakepedalcontrol __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Autonomousbrakepedalcontrol __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Autonomousbrakepedalcontrol_
{
  using Type = Autonomousbrakepedalcontrol_<ContainerAllocator>;

  explicit Autonomousbrakepedalcontrol_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->autonomous_brakemotor_voltage = 0;
      this->autonomous_brakepedalmotor_per = 0;
      this->autonomous_brakepedalmotor_acc = 0;
      this->autonomous_brakepedalmotor_en = 0;
    }
  }

  explicit Autonomousbrakepedalcontrol_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->autonomous_brakemotor_voltage = 0;
      this->autonomous_brakepedalmotor_per = 0;
      this->autonomous_brakepedalmotor_acc = 0;
      this->autonomous_brakepedalmotor_en = 0;
    }
  }

  // field types and members
  using _autonomous_brakemotor_voltage_type =
    uint8_t;
  _autonomous_brakemotor_voltage_type autonomous_brakemotor_voltage;
  using _autonomous_brakepedalmotor_per_type =
    uint8_t;
  _autonomous_brakepedalmotor_per_type autonomous_brakepedalmotor_per;
  using _autonomous_brakepedalmotor_acc_type =
    uint16_t;
  _autonomous_brakepedalmotor_acc_type autonomous_brakepedalmotor_acc;
  using _autonomous_brakepedalmotor_en_type =
    uint8_t;
  _autonomous_brakepedalmotor_en_type autonomous_brakepedalmotor_en;

  // setters for named parameter idiom
  Type & set__autonomous_brakemotor_voltage(
    const uint8_t & _arg)
  {
    this->autonomous_brakemotor_voltage = _arg;
    return *this;
  }
  Type & set__autonomous_brakepedalmotor_per(
    const uint8_t & _arg)
  {
    this->autonomous_brakepedalmotor_per = _arg;
    return *this;
  }
  Type & set__autonomous_brakepedalmotor_acc(
    const uint16_t & _arg)
  {
    this->autonomous_brakepedalmotor_acc = _arg;
    return *this;
  }
  Type & set__autonomous_brakepedalmotor_en(
    const uint8_t & _arg)
  {
    this->autonomous_brakepedalmotor_en = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Autonomousbrakepedalcontrol
    std::shared_ptr<smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Autonomousbrakepedalcontrol
    std::shared_ptr<smart_can_msgs::msg::Autonomousbrakepedalcontrol_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Autonomousbrakepedalcontrol_ & other) const
  {
    if (this->autonomous_brakemotor_voltage != other.autonomous_brakemotor_voltage) {
      return false;
    }
    if (this->autonomous_brakepedalmotor_per != other.autonomous_brakepedalmotor_per) {
      return false;
    }
    if (this->autonomous_brakepedalmotor_acc != other.autonomous_brakepedalmotor_acc) {
      return false;
    }
    if (this->autonomous_brakepedalmotor_en != other.autonomous_brakepedalmotor_en) {
      return false;
    }
    return true;
  }
  bool operator!=(const Autonomousbrakepedalcontrol_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Autonomousbrakepedalcontrol_

// alias to use template instance with default allocator
using Autonomousbrakepedalcontrol =
  smart_can_msgs::msg::Autonomousbrakepedalcontrol_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSBRAKEPEDALCONTROL__STRUCT_HPP_
