// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from smart_can_msgs:msg/Feedbacksensor.idl
// generated code does not contain a copyright notice

#ifndef SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__BUILDER_HPP_
#define SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "smart_can_msgs/msg/detail/feedbacksensor__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace smart_can_msgs
{

namespace msg
{

namespace builder
{

class Init_Feedbacksensor_butonkaldir
{
public:
  explicit Init_Feedbacksensor_butonkaldir(::smart_can_msgs::msg::Feedbacksensor & msg)
  : msg_(msg)
  {}
  ::smart_can_msgs::msg::Feedbacksensor butonkaldir(::smart_can_msgs::msg::Feedbacksensor::_butonkaldir_type arg)
  {
    msg_.butonkaldir = std::move(arg);
    return std::move(msg_);
  }

private:
  ::smart_can_msgs::msg::Feedbacksensor msg_;
};

class Init_Feedbacksensor_butonindir
{
public:
  explicit Init_Feedbacksensor_butonindir(::smart_can_msgs::msg::Feedbacksensor & msg)
  : msg_(msg)
  {}
  Init_Feedbacksensor_butonkaldir butonindir(::smart_can_msgs::msg::Feedbacksensor::_butonindir_type arg)
  {
    msg_.butonindir = std::move(arg);
    return Init_Feedbacksensor_butonkaldir(msg_);
  }

private:
  ::smart_can_msgs::msg::Feedbacksensor msg_;
};

class Init_Feedbacksensor_kaldir
{
public:
  explicit Init_Feedbacksensor_kaldir(::smart_can_msgs::msg::Feedbacksensor & msg)
  : msg_(msg)
  {}
  Init_Feedbacksensor_butonindir kaldir(::smart_can_msgs::msg::Feedbacksensor::_kaldir_type arg)
  {
    msg_.kaldir = std::move(arg);
    return Init_Feedbacksensor_butonindir(msg_);
  }

private:
  ::smart_can_msgs::msg::Feedbacksensor msg_;
};

class Init_Feedbacksensor_indir
{
public:
  explicit Init_Feedbacksensor_indir(::smart_can_msgs::msg::Feedbacksensor & msg)
  : msg_(msg)
  {}
  Init_Feedbacksensor_kaldir indir(::smart_can_msgs::msg::Feedbacksensor::_indir_type arg)
  {
    msg_.indir = std::move(arg);
    return Init_Feedbacksensor_kaldir(msg_);
  }

private:
  ::smart_can_msgs::msg::Feedbacksensor msg_;
};

class Init_Feedbacksensor_handbrakesensor_hamdata
{
public:
  explicit Init_Feedbacksensor_handbrakesensor_hamdata(::smart_can_msgs::msg::Feedbacksensor & msg)
  : msg_(msg)
  {}
  Init_Feedbacksensor_indir handbrakesensor_hamdata(::smart_can_msgs::msg::Feedbacksensor::_handbrakesensor_hamdata_type arg)
  {
    msg_.handbrakesensor_hamdata = std::move(arg);
    return Init_Feedbacksensor_indir(msg_);
  }

private:
  ::smart_can_msgs::msg::Feedbacksensor msg_;
};

class Init_Feedbacksensor_handbrakesensor
{
public:
  explicit Init_Feedbacksensor_handbrakesensor(::smart_can_msgs::msg::Feedbacksensor & msg)
  : msg_(msg)
  {}
  Init_Feedbacksensor_handbrakesensor_hamdata handbrakesensor(::smart_can_msgs::msg::Feedbacksensor::_handbrakesensor_type arg)
  {
    msg_.handbrakesensor = std::move(arg);
    return Init_Feedbacksensor_handbrakesensor_hamdata(msg_);
  }

private:
  ::smart_can_msgs::msg::Feedbacksensor msg_;
};

class Init_Feedbacksensor_brakepedalsensorhamdata
{
public:
  explicit Init_Feedbacksensor_brakepedalsensorhamdata(::smart_can_msgs::msg::Feedbacksensor & msg)
  : msg_(msg)
  {}
  Init_Feedbacksensor_handbrakesensor brakepedalsensorhamdata(::smart_can_msgs::msg::Feedbacksensor::_brakepedalsensorhamdata_type arg)
  {
    msg_.brakepedalsensorhamdata = std::move(arg);
    return Init_Feedbacksensor_handbrakesensor(msg_);
  }

private:
  ::smart_can_msgs::msg::Feedbacksensor msg_;
};

class Init_Feedbacksensor_steeringanglesensorhamdata
{
public:
  Init_Feedbacksensor_steeringanglesensorhamdata()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Feedbacksensor_brakepedalsensorhamdata steeringanglesensorhamdata(::smart_can_msgs::msg::Feedbacksensor::_steeringanglesensorhamdata_type arg)
  {
    msg_.steeringanglesensorhamdata = std::move(arg);
    return Init_Feedbacksensor_brakepedalsensorhamdata(msg_);
  }

private:
  ::smart_can_msgs::msg::Feedbacksensor msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::smart_can_msgs::msg::Feedbacksensor>()
{
  return smart_can_msgs::msg::builder::Init_Feedbacksensor_steeringanglesensorhamdata();
}

}  // namespace smart_can_msgs

#endif  // SMART_CAN_MSGS__MSG__DETAIL__FEEDBACKSENSOR__BUILDER_HPP_
