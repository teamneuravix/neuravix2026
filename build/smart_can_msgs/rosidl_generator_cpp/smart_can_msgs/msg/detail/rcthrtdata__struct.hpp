// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from smart_can_msgs:msg/Rcthrtdata.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__RCTHRTDATA__STRUCT_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__RCTHRTDATA__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__smart_can_msgs__msg__Rcthrtdata __attribute__((deprecated))
#else
# define DEPRECATED__smart_can_msgs__msg__Rcthrtdata __declspec(deprecated)
#endif

namespace smart_can_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Rcthrtdata_
{
  using Type = Rcthrtdata_<ContainerAllocator>;

  explicit Rcthrtdata_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rc_thrt_pedal_position = 0;
      this->rc_thrt_pedal_press = 0;
    }
  }

  explicit Rcthrtdata_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rc_thrt_pedal_position = 0;
      this->rc_thrt_pedal_press = 0;
    }
  }

  // field types and members
  using _rc_thrt_pedal_position_type =
    uint8_t;
  _rc_thrt_pedal_position_type rc_thrt_pedal_position;
  using _rc_thrt_pedal_press_type =
    uint8_t;
  _rc_thrt_pedal_press_type rc_thrt_pedal_press;

  // setters for named parameter idiom
  Type & set__rc_thrt_pedal_position(
    const uint8_t & _arg)
  {
    this->rc_thrt_pedal_position = _arg;
    return *this;
  }
  Type & set__rc_thrt_pedal_press(
    const uint8_t & _arg)
  {
    this->rc_thrt_pedal_press = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator> *;
  using ConstRawPtr =
    const smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__smart_can_msgs__msg__Rcthrtdata
    std::shared_ptr<smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__smart_can_msgs__msg__Rcthrtdata
    std::shared_ptr<smart_can_msgs::msg::Rcthrtdata_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Rcthrtdata_ & other) const
  {
    if (this->rc_thrt_pedal_position != other.rc_thrt_pedal_position) {
      return false;
    }
    if (this->rc_thrt_pedal_press != other.rc_thrt_pedal_press) {
      return false;
    }
    return true;
  }
  bool operator!=(const Rcthrtdata_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Rcthrtdata_

// alias to use template instance with default allocator
using Rcthrtdata =
  smart_can_msgs::msg::Rcthrtdata_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__RCTHRTDATA__STRUCT_HPP_
