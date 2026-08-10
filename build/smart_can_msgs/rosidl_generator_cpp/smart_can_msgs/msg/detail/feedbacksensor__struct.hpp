// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Feedbacksensor.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Feedbacksensor __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Feedbacksensor __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Feedbacksensor_
{
  using Type = Feedbacksensor_<ContainerAllocator>;

  explicit Feedbacksensor_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->steeringanglesensorhamdata = 0;
      this->brakepedalsensorhamdata = 0;
      this->handbrakesensor = 0;
      this->handbrakesensor_hamdata = 0;
      this->indir = 0;
      this->kaldir = 0;
      this->butonindir = 0;
      this->butonkaldir = 0;
    }
  }

  explicit Feedbacksensor_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->steeringanglesensorhamdata = 0;
      this->brakepedalsensorhamdata = 0;
      this->handbrakesensor = 0;
      this->handbrakesensor_hamdata = 0;
      this->indir = 0;
      this->kaldir = 0;
      this->butonindir = 0;
      this->butonkaldir = 0;
    }
  }

  // field types and members
  using _steeringanglesensorhamdata_type =
    uint8_t;
  _steeringanglesensorhamdata_type steeringanglesensorhamdata;
  using _brakepedalsensorhamdata_type =
    uint8_t;
  _brakepedalsensorhamdata_type brakepedalsensorhamdata;
  using _handbrakesensor_type =
    uint8_t;
  _handbrakesensor_type handbrakesensor;
  using _handbrakesensor_hamdata_type =
    uint8_t;
  _handbrakesensor_hamdata_type handbrakesensor_hamdata;
  using _indir_type =
    uint8_t;
  _indir_type indir;
  using _kaldir_type =
    uint8_t;
  _kaldir_type kaldir;
  using _butonindir_type =
    uint8_t;
  _butonindir_type butonindir;
  using _butonkaldir_type =
    uint8_t;
  _butonkaldir_type butonkaldir;

  // setters for named parameter idiom
  Type & set__steeringanglesensorhamdata(
    const uint8_t & _arg)
  {
    this->steeringanglesensorhamdata = _arg;
    return *this;
  }
  Type & set__brakepedalsensorhamdata(
    const uint8_t & _arg)
  {
    this->brakepedalsensorhamdata = _arg;
    return *this;
  }
  Type & set__handbrakesensor(
    const uint8_t & _arg)
  {
    this->handbrakesensor = _arg;
    return *this;
  }
  Type & set__handbrakesensor_hamdata(
    const uint8_t & _arg)
  {
    this->handbrakesensor_hamdata = _arg;
    return *this;
  }
  Type & set__indir(
    const uint8_t & _arg)
  {
    this->indir = _arg;
    return *this;
  }
  Type & set__kaldir(
    const uint8_t & _arg)
  {
    this->kaldir = _arg;
    return *this;
  }
  Type & set__butonindir(
    const uint8_t & _arg)
  {
    this->butonindir = _arg;
    return *this;
  }
  Type & set__butonkaldir(
    const uint8_t & _arg)
  {
    this->butonkaldir = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Feedbacksensor
    std::shared_ptr<smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Feedbacksensor
    std::shared_ptr<smart_can_msgs::msg::Feedbacksensor_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Feedbacksensor_ & other) const
  {
    if (this->steeringanglesensorhamdata != other.steeringanglesensorhamdata) {
      return false;
    }
    if (this->brakepedalsensorhamdata != other.brakepedalsensorhamdata) {
      return false;
    }
    if (this->handbrakesensor != other.handbrakesensor) {
      return false;
    }
    if (this->handbrakesensor_hamdata != other.handbrakesensor_hamdata) {
      return false;
    }
    if (this->indir != other.indir) {
      return false;
    }
    if (this->kaldir != other.kaldir) {
      return false;
    }
    if (this->butonindir != other.butonindir) {
      return false;
    }
    if (this->butonkaldir != other.butonkaldir) {
      return false;
    }
    return true;
  }
  bool operator!=(const Feedbacksensor_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Feedbacksensor_

// alias to use template instance with default allocator
using Feedbacksensor =
  smart_can_msgs::msg::Feedbacksensor_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__STRUCT_HPP_
