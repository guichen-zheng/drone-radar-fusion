// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interface:msg/DroneDetectArray.idl
// generated code does not contain a copyright notice

#ifndef INTERFACE__MSG__DETAIL__DRONE_DETECT_ARRAY__BUILDER_HPP_
#define INTERFACE__MSG__DETAIL__DRONE_DETECT_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interface/msg/detail/drone_detect_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interface
{

namespace msg
{

namespace builder
{

class Init_DroneDetectArray_drones
{
public:
  explicit Init_DroneDetectArray_drones(::interface::msg::DroneDetectArray & msg)
  : msg_(msg)
  {}
  ::interface::msg::DroneDetectArray drones(::interface::msg::DroneDetectArray::_drones_type arg)
  {
    msg_.drones = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interface::msg::DroneDetectArray msg_;
};

class Init_DroneDetectArray_header
{
public:
  Init_DroneDetectArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DroneDetectArray_drones header(::interface::msg::DroneDetectArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_DroneDetectArray_drones(msg_);
  }

private:
  ::interface::msg::DroneDetectArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interface::msg::DroneDetectArray>()
{
  return interface::msg::builder::Init_DroneDetectArray_header();
}

}  // namespace interface

#endif  // INTERFACE__MSG__DETAIL__DRONE_DETECT_ARRAY__BUILDER_HPP_
