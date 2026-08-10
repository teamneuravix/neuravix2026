// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Fbmotordriver.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Fbmotordriver __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Fbmotordriver __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Fbmotordriver_
{
  using Type = Fbmotordriver_<ContainerAllocator>;

  explicit Fbmotordriver_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->gear_status_from_motor = 0;
      this->plustripdistance = 0;
      this->vehiclerpm = 0;
    }
  }

  explicit Fbmotordriver_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->gear_status_from_motor = 0;
      this->plustripdistance = 0;
      this->vehiclerpm = 0;
    }
  }

  // field types and members
  using _gear_status_from_motor_type =
    uint8_t;
  _gear_status_from_motor_type gear_status_from_motor;
  using _plustripdistance_type =
    uint16_t;
  _plustripdistance_type plustripdistance;
  using _vehiclerpm_type =
    uint16_t;
  _vehiclerpm_type vehiclerpm;

  // setters for named parameter idiom
  Type & set__gear_status_from_motor(
    const uint8_t & _arg)
  {
    this->gear_status_from_motor = _arg;
    return *this;
  }
  Type & set__plustripdistance(
    const uint16_t & _arg)
  {
    this->plustripdistance = _arg;
    return *this;
  }
  Type & set__vehiclerpm(
    const uint16_t & _arg)
  {
    this->vehiclerpm = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Fbmotordriver
    std::shared_ptr<smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Fbmotordriver
    std::shared_ptr<smart_can_msgs::msg::Fbmotordriver_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Fbmotordriver_ & other) const
  {
    if (this->gear_status_from_motor != other.gear_status_from_motor) {
      return false;
    }
    if (this->plustripdistance != other.plustripdistance) {
      return false;
    }
    if (this->vehiclerpm != other.vehiclerpm) {
      return false;
    }
    return true;
  }
  bool operator!=(const Fbmotordriver_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Fbmotordriver_

// alias to use template instance with default allocator
using Fbmotordriver =
  smart_can_msgs::msg::Fbmotordriver_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBMOTORDRIVER__STRUCT_HPP_
