// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Rcunittoomux.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Rcunittoomux __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Rcunittoomux __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Rcunittoomux_
{
  using Type = Rcunittoomux_<ContainerAllocator>;

  explicit Rcunittoomux_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->autonomous_emergency = 0;
      this->rc_windowresintance = 0;
      this->rc_interiorlight = 0;
      this->rc_reverselight = 0;
      this->rc_drl = 0;
      this->rc_brakelight = 0;
      this->autonomous_door_open = 0;
      this->autonomous_door_close = 0;
      this->rc_signalstatus = 0;
      this->rc_lowbeam = 0;
      this->rc_highbeam = 0;
      this->rc_selectiongear = 0;
      this->rc_ignition = 0;
    }
  }

  explicit Rcunittoomux_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->autonomous_emergency = 0;
      this->rc_windowresintance = 0;
      this->rc_interiorlight = 0;
      this->rc_reverselight = 0;
      this->rc_drl = 0;
      this->rc_brakelight = 0;
      this->autonomous_door_open = 0;
      this->autonomous_door_close = 0;
      this->rc_signalstatus = 0;
      this->rc_lowbeam = 0;
      this->rc_highbeam = 0;
      this->rc_selectiongear = 0;
      this->rc_ignition = 0;
    }
  }

  // field types and members
  using _autonomous_emergency_type =
    int8_t;
  _autonomous_emergency_type autonomous_emergency;
  using _rc_windowresintance_type =
    uint8_t;
  _rc_windowresintance_type rc_windowresintance;
  using _rc_interiorlight_type =
    uint8_t;
  _rc_interiorlight_type rc_interiorlight;
  using _rc_reverselight_type =
    uint8_t;
  _rc_reverselight_type rc_reverselight;
  using _rc_drl_type =
    uint8_t;
  _rc_drl_type rc_drl;
  using _rc_brakelight_type =
    uint8_t;
  _rc_brakelight_type rc_brakelight;
  using _autonomous_door_open_type =
    int8_t;
  _autonomous_door_open_type autonomous_door_open;
  using _autonomous_door_close_type =
    int8_t;
  _autonomous_door_close_type autonomous_door_close;
  using _rc_signalstatus_type =
    uint8_t;
  _rc_signalstatus_type rc_signalstatus;
  using _rc_lowbeam_type =
    uint8_t;
  _rc_lowbeam_type rc_lowbeam;
  using _rc_highbeam_type =
    uint8_t;
  _rc_highbeam_type rc_highbeam;
  using _rc_selectiongear_type =
    uint8_t;
  _rc_selectiongear_type rc_selectiongear;
  using _rc_ignition_type =
    uint8_t;
  _rc_ignition_type rc_ignition;

  // setters for named parameter idiom
  Type & set__autonomous_emergency(
    const int8_t & _arg)
  {
    this->autonomous_emergency = _arg;
    return *this;
  }
  Type & set__rc_windowresintance(
    const uint8_t & _arg)
  {
    this->rc_windowresintance = _arg;
    return *this;
  }
  Type & set__rc_interiorlight(
    const uint8_t & _arg)
  {
    this->rc_interiorlight = _arg;
    return *this;
  }
  Type & set__rc_reverselight(
    const uint8_t & _arg)
  {
    this->rc_reverselight = _arg;
    return *this;
  }
  Type & set__rc_drl(
    const uint8_t & _arg)
  {
    this->rc_drl = _arg;
    return *this;
  }
  Type & set__rc_brakelight(
    const uint8_t & _arg)
  {
    this->rc_brakelight = _arg;
    return *this;
  }
  Type & set__autonomous_door_open(
    const int8_t & _arg)
  {
    this->autonomous_door_open = _arg;
    return *this;
  }
  Type & set__autonomous_door_close(
    const int8_t & _arg)
  {
    this->autonomous_door_close = _arg;
    return *this;
  }
  Type & set__rc_signalstatus(
    const uint8_t & _arg)
  {
    this->rc_signalstatus = _arg;
    return *this;
  }
  Type & set__rc_lowbeam(
    const uint8_t & _arg)
  {
    this->rc_lowbeam = _arg;
    return *this;
  }
  Type & set__rc_highbeam(
    const uint8_t & _arg)
  {
    this->rc_highbeam = _arg;
    return *this;
  }
  Type & set__rc_selectiongear(
    const uint8_t & _arg)
  {
    this->rc_selectiongear = _arg;
    return *this;
  }
  Type & set__rc_ignition(
    const uint8_t & _arg)
  {
    this->rc_ignition = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Rcunittoomux
    std::shared_ptr<smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Rcunittoomux
    std::shared_ptr<smart_can_msgs::msg::Rcunittoomux_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Rcunittoomux_ & other) const
  {
    if (this->autonomous_emergency != other.autonomous_emergency) {
      return false;
    }
    if (this->rc_windowresintance != other.rc_windowresintance) {
      return false;
    }
    if (this->rc_interiorlight != other.rc_interiorlight) {
      return false;
    }
    if (this->rc_reverselight != other.rc_reverselight) {
      return false;
    }
    if (this->rc_drl != other.rc_drl) {
      return false;
    }
    if (this->rc_brakelight != other.rc_brakelight) {
      return false;
    }
    if (this->autonomous_door_open != other.autonomous_door_open) {
      return false;
    }
    if (this->autonomous_door_close != other.autonomous_door_close) {
      return false;
    }
    if (this->rc_signalstatus != other.rc_signalstatus) {
      return false;
    }
    if (this->rc_lowbeam != other.rc_lowbeam) {
      return false;
    }
    if (this->rc_highbeam != other.rc_highbeam) {
      return false;
    }
    if (this->rc_selectiongear != other.rc_selectiongear) {
      return false;
    }
    if (this->rc_ignition != other.rc_ignition) {
      return false;
    }
    return true;
  }
  bool operator!=(const Rcunittoomux_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Rcunittoomux_

// alias to use template instance with default allocator
using Rcunittoomux =
  smart_can_msgs::msg::Rcunittoomux_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__RCUNITTOOMUX__STRUCT_HPP_
