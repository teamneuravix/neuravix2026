// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Autonomoushbmotorcontrol.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Autonomoushbmotorcontrol __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Autonomoushbmotorcontrol __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Autonomoushbmotorcontrol_
{
  using Type = Autonomoushbmotorcontrol_<ContainerAllocator>;

  explicit Autonomoushbmotorcontrol_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->autonomous_hb_motor_pwm = 0;
      this->autonomous_hb_motstate = 0;
      this->autonomous_hb_moten = 0;
    }
  }

  explicit Autonomoushbmotorcontrol_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->autonomous_hb_motor_pwm = 0;
      this->autonomous_hb_motstate = 0;
      this->autonomous_hb_moten = 0;
    }
  }

  // field types and members
  using _autonomous_hb_motor_pwm_type =
    uint8_t;
  _autonomous_hb_motor_pwm_type autonomous_hb_motor_pwm;
  using _autonomous_hb_motstate_type =
    uint8_t;
  _autonomous_hb_motstate_type autonomous_hb_motstate;
  using _autonomous_hb_moten_type =
    uint8_t;
  _autonomous_hb_moten_type autonomous_hb_moten;

  // setters for named parameter idiom
  Type & set__autonomous_hb_motor_pwm(
    const uint8_t & _arg)
  {
    this->autonomous_hb_motor_pwm = _arg;
    return *this;
  }
  Type & set__autonomous_hb_motstate(
    const uint8_t & _arg)
  {
    this->autonomous_hb_motstate = _arg;
    return *this;
  }
  Type & set__autonomous_hb_moten(
    const uint8_t & _arg)
  {
    this->autonomous_hb_moten = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Autonomoushbmotorcontrol
    std::shared_ptr<smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Autonomoushbmotorcontrol
    std::shared_ptr<smart_can_msgs::msg::Autonomoushbmotorcontrol_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Autonomoushbmotorcontrol_ & other) const
  {
    if (this->autonomous_hb_motor_pwm != other.autonomous_hb_motor_pwm) {
      return false;
    }
    if (this->autonomous_hb_motstate != other.autonomous_hb_motstate) {
      return false;
    }
    if (this->autonomous_hb_moten != other.autonomous_hb_moten) {
      return false;
    }
    return true;
  }
  bool operator!=(const Autonomoushbmotorcontrol_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Autonomoushbmotorcontrol_

// alias to use template instance with default allocator
using Autonomoushbmotorcontrol =
  smart_can_msgs::msg::Autonomoushbmotorcontrol_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__AUTONOMOUSHBMOTORCONTROL__STRUCT_HPP_
