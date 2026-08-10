// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Fbomuxtoautonomous.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Fbomuxtoautonomous __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Fbomuxtoautonomous __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Fbomuxtoautonomous_
{
  using Type = Fbomuxtoautonomous_<ContainerAllocator>;

  explicit Fbomuxtoautonomous_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->fb_emergency = 0;
      this->fb_reverselight = 0;
      this->fb_rightsignal = 0;
      this->fb_windowresistance = 0;
      this->fb_leftsignal = 0;
      this->fb_interiorlight = 0;
      this->fb_drl = 0;
      this->fb_doorkeystatus = 0;
      this->fb_brakelight = 0;
      this->fb_batteryvoltage = 0;
      this->fb_chargeinput = 0;
      this->fb_highbeam = 0;
      this->fb_lowbeam = 0;
      this->fb_ignition = 0;
      this->fb_hazardouslight = 0;
      this->fb_vehiclestatus = 0;
      this->fb_leftdoorstatus = 0;
      this->fb_rightdoorstatus = 0;
      this->fb_batterysoc = 0;
      this->fb_errorpowertrain = 0;
      this->fb_errorbattery = 0;
      this->fb_brakepedal_voltage_en = 0;
    }
  }

  explicit Fbomuxtoautonomous_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->fb_emergency = 0;
      this->fb_reverselight = 0;
      this->fb_rightsignal = 0;
      this->fb_windowresistance = 0;
      this->fb_leftsignal = 0;
      this->fb_interiorlight = 0;
      this->fb_drl = 0;
      this->fb_doorkeystatus = 0;
      this->fb_brakelight = 0;
      this->fb_batteryvoltage = 0;
      this->fb_chargeinput = 0;
      this->fb_highbeam = 0;
      this->fb_lowbeam = 0;
      this->fb_ignition = 0;
      this->fb_hazardouslight = 0;
      this->fb_vehiclestatus = 0;
      this->fb_leftdoorstatus = 0;
      this->fb_rightdoorstatus = 0;
      this->fb_batterysoc = 0;
      this->fb_errorpowertrain = 0;
      this->fb_errorbattery = 0;
      this->fb_brakepedal_voltage_en = 0;
    }
  }

  // field types and members
  using _fb_emergency_type =
    uint8_t;
  _fb_emergency_type fb_emergency;
  using _fb_reverselight_type =
    uint8_t;
  _fb_reverselight_type fb_reverselight;
  using _fb_rightsignal_type =
    uint8_t;
  _fb_rightsignal_type fb_rightsignal;
  using _fb_windowresistance_type =
    uint8_t;
  _fb_windowresistance_type fb_windowresistance;
  using _fb_leftsignal_type =
    uint8_t;
  _fb_leftsignal_type fb_leftsignal;
  using _fb_interiorlight_type =
    uint8_t;
  _fb_interiorlight_type fb_interiorlight;
  using _fb_drl_type =
    uint8_t;
  _fb_drl_type fb_drl;
  using _fb_doorkeystatus_type =
    uint8_t;
  _fb_doorkeystatus_type fb_doorkeystatus;
  using _fb_brakelight_type =
    uint8_t;
  _fb_brakelight_type fb_brakelight;
  using _fb_batteryvoltage_type =
    uint8_t;
  _fb_batteryvoltage_type fb_batteryvoltage;
  using _fb_chargeinput_type =
    uint8_t;
  _fb_chargeinput_type fb_chargeinput;
  using _fb_highbeam_type =
    uint8_t;
  _fb_highbeam_type fb_highbeam;
  using _fb_lowbeam_type =
    uint8_t;
  _fb_lowbeam_type fb_lowbeam;
  using _fb_ignition_type =
    uint8_t;
  _fb_ignition_type fb_ignition;
  using _fb_hazardouslight_type =
    uint8_t;
  _fb_hazardouslight_type fb_hazardouslight;
  using _fb_vehiclestatus_type =
    uint8_t;
  _fb_vehiclestatus_type fb_vehiclestatus;
  using _fb_leftdoorstatus_type =
    uint8_t;
  _fb_leftdoorstatus_type fb_leftdoorstatus;
  using _fb_rightdoorstatus_type =
    uint8_t;
  _fb_rightdoorstatus_type fb_rightdoorstatus;
  using _fb_batterysoc_type =
    uint8_t;
  _fb_batterysoc_type fb_batterysoc;
  using _fb_errorpowertrain_type =
    uint8_t;
  _fb_errorpowertrain_type fb_errorpowertrain;
  using _fb_errorbattery_type =
    uint8_t;
  _fb_errorbattery_type fb_errorbattery;
  using _fb_brakepedal_voltage_en_type =
    uint8_t;
  _fb_brakepedal_voltage_en_type fb_brakepedal_voltage_en;

  // setters for named parameter idiom
  Type & set__fb_emergency(
    const uint8_t & _arg)
  {
    this->fb_emergency = _arg;
    return *this;
  }
  Type & set__fb_reverselight(
    const uint8_t & _arg)
  {
    this->fb_reverselight = _arg;
    return *this;
  }
  Type & set__fb_rightsignal(
    const uint8_t & _arg)
  {
    this->fb_rightsignal = _arg;
    return *this;
  }
  Type & set__fb_windowresistance(
    const uint8_t & _arg)
  {
    this->fb_windowresistance = _arg;
    return *this;
  }
  Type & set__fb_leftsignal(
    const uint8_t & _arg)
  {
    this->fb_leftsignal = _arg;
    return *this;
  }
  Type & set__fb_interiorlight(
    const uint8_t & _arg)
  {
    this->fb_interiorlight = _arg;
    return *this;
  }
  Type & set__fb_drl(
    const uint8_t & _arg)
  {
    this->fb_drl = _arg;
    return *this;
  }
  Type & set__fb_doorkeystatus(
    const uint8_t & _arg)
  {
    this->fb_doorkeystatus = _arg;
    return *this;
  }
  Type & set__fb_brakelight(
    const uint8_t & _arg)
  {
    this->fb_brakelight = _arg;
    return *this;
  }
  Type & set__fb_batteryvoltage(
    const uint8_t & _arg)
  {
    this->fb_batteryvoltage = _arg;
    return *this;
  }
  Type & set__fb_chargeinput(
    const uint8_t & _arg)
  {
    this->fb_chargeinput = _arg;
    return *this;
  }
  Type & set__fb_highbeam(
    const uint8_t & _arg)
  {
    this->fb_highbeam = _arg;
    return *this;
  }
  Type & set__fb_lowbeam(
    const uint8_t & _arg)
  {
    this->fb_lowbeam = _arg;
    return *this;
  }
  Type & set__fb_ignition(
    const uint8_t & _arg)
  {
    this->fb_ignition = _arg;
    return *this;
  }
  Type & set__fb_hazardouslight(
    const uint8_t & _arg)
  {
    this->fb_hazardouslight = _arg;
    return *this;
  }
  Type & set__fb_vehiclestatus(
    const uint8_t & _arg)
  {
    this->fb_vehiclestatus = _arg;
    return *this;
  }
  Type & set__fb_leftdoorstatus(
    const uint8_t & _arg)
  {
    this->fb_leftdoorstatus = _arg;
    return *this;
  }
  Type & set__fb_rightdoorstatus(
    const uint8_t & _arg)
  {
    this->fb_rightdoorstatus = _arg;
    return *this;
  }
  Type & set__fb_batterysoc(
    const uint8_t & _arg)
  {
    this->fb_batterysoc = _arg;
    return *this;
  }
  Type & set__fb_errorpowertrain(
    const uint8_t & _arg)
  {
    this->fb_errorpowertrain = _arg;
    return *this;
  }
  Type & set__fb_errorbattery(
    const uint8_t & _arg)
  {
    this->fb_errorbattery = _arg;
    return *this;
  }
  Type & set__fb_brakepedal_voltage_en(
    const uint8_t & _arg)
  {
    this->fb_brakepedal_voltage_en = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Fbomuxtoautonomous
    std::shared_ptr<smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Fbomuxtoautonomous
    std::shared_ptr<smart_can_msgs::msg::Fbomuxtoautonomous_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Fbomuxtoautonomous_ & other) const
  {
    if (this->fb_emergency != other.fb_emergency) {
      return false;
    }
    if (this->fb_reverselight != other.fb_reverselight) {
      return false;
    }
    if (this->fb_rightsignal != other.fb_rightsignal) {
      return false;
    }
    if (this->fb_windowresistance != other.fb_windowresistance) {
      return false;
    }
    if (this->fb_leftsignal != other.fb_leftsignal) {
      return false;
    }
    if (this->fb_interiorlight != other.fb_interiorlight) {
      return false;
    }
    if (this->fb_drl != other.fb_drl) {
      return false;
    }
    if (this->fb_doorkeystatus != other.fb_doorkeystatus) {
      return false;
    }
    if (this->fb_brakelight != other.fb_brakelight) {
      return false;
    }
    if (this->fb_batteryvoltage != other.fb_batteryvoltage) {
      return false;
    }
    if (this->fb_chargeinput != other.fb_chargeinput) {
      return false;
    }
    if (this->fb_highbeam != other.fb_highbeam) {
      return false;
    }
    if (this->fb_lowbeam != other.fb_lowbeam) {
      return false;
    }
    if (this->fb_ignition != other.fb_ignition) {
      return false;
    }
    if (this->fb_hazardouslight != other.fb_hazardouslight) {
      return false;
    }
    if (this->fb_vehiclestatus != other.fb_vehiclestatus) {
      return false;
    }
    if (this->fb_leftdoorstatus != other.fb_leftdoorstatus) {
      return false;
    }
    if (this->fb_rightdoorstatus != other.fb_rightdoorstatus) {
      return false;
    }
    if (this->fb_batterysoc != other.fb_batterysoc) {
      return false;
    }
    if (this->fb_errorpowertrain != other.fb_errorpowertrain) {
      return false;
    }
    if (this->fb_errorbattery != other.fb_errorbattery) {
      return false;
    }
    if (this->fb_brakepedal_voltage_en != other.fb_brakepedal_voltage_en) {
      return false;
    }
    return true;
  }
  bool operator!=(const Fbomuxtoautonomous_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Fbomuxtoautonomous_

// alias to use template instance with default allocator
using Fbomuxtoautonomous =
  smart_can_msgs::msg::Fbomuxtoautonomous_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FBOMUXTOAUTONOMOUS__STRUCT_HPP_
