// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interface:msg/RadarWarn.idl
// generated code does not contain a copyright notice

#ifndef INTERFACE__MSG__DETAIL__RADAR_WARN__BUILDER_HPP_
#define INTERFACE__MSG__DETAIL__RADAR_WARN__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interface/msg/detail/radar_warn__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interface
{

namespace msg
{

namespace builder
{

class Init_RadarWarn_detected_at
{
public:
  explicit Init_RadarWarn_detected_at(::interface::msg::RadarWarn & msg)
  : msg_(msg)
  {}
  ::interface::msg::RadarWarn detected_at(::interface::msg::RadarWarn::_detected_at_type arg)
  {
    msg_.detected_at = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interface::msg::RadarWarn msg_;
};

class Init_RadarWarn_description
{
public:
  explicit Init_RadarWarn_description(::interface::msg::RadarWarn & msg)
  : msg_(msg)
  {}
  Init_RadarWarn_detected_at description(::interface::msg::RadarWarn::_description_type arg)
  {
    msg_.description = std::move(arg);
    return Init_RadarWarn_detected_at(msg_);
  }

private:
  ::interface::msg::RadarWarn msg_;
};

class Init_RadarWarn_warn_level
{
public:
  explicit Init_RadarWarn_warn_level(::interface::msg::RadarWarn & msg)
  : msg_(msg)
  {}
  Init_RadarWarn_description warn_level(::interface::msg::RadarWarn::_warn_level_type arg)
  {
    msg_.warn_level = std::move(arg);
    return Init_RadarWarn_description(msg_);
  }

private:
  ::interface::msg::RadarWarn msg_;
};

class Init_RadarWarn_confidence
{
public:
  explicit Init_RadarWarn_confidence(::interface::msg::RadarWarn & msg)
  : msg_(msg)
  {}
  Init_RadarWarn_warn_level confidence(::interface::msg::RadarWarn::_confidence_type arg)
  {
    msg_.confidence = std::move(arg);
    return Init_RadarWarn_warn_level(msg_);
  }

private:
  ::interface::msg::RadarWarn msg_;
};

class Init_RadarWarn_z
{
public:
  explicit Init_RadarWarn_z(::interface::msg::RadarWarn & msg)
  : msg_(msg)
  {}
  Init_RadarWarn_confidence z(::interface::msg::RadarWarn::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_RadarWarn_confidence(msg_);
  }

private:
  ::interface::msg::RadarWarn msg_;
};

class Init_RadarWarn_y
{
public:
  explicit Init_RadarWarn_y(::interface::msg::RadarWarn & msg)
  : msg_(msg)
  {}
  Init_RadarWarn_z y(::interface::msg::RadarWarn::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_RadarWarn_z(msg_);
  }

private:
  ::interface::msg::RadarWarn msg_;
};

class Init_RadarWarn_x
{
public:
  explicit Init_RadarWarn_x(::interface::msg::RadarWarn & msg)
  : msg_(msg)
  {}
  Init_RadarWarn_y x(::interface::msg::RadarWarn::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_RadarWarn_y(msg_);
  }

private:
  ::interface::msg::RadarWarn msg_;
};

class Init_RadarWarn_drone_id
{
public:
  explicit Init_RadarWarn_drone_id(::interface::msg::RadarWarn & msg)
  : msg_(msg)
  {}
  Init_RadarWarn_x drone_id(::interface::msg::RadarWarn::_drone_id_type arg)
  {
    msg_.drone_id = std::move(arg);
    return Init_RadarWarn_x(msg_);
  }

private:
  ::interface::msg::RadarWarn msg_;
};

class Init_RadarWarn_header
{
public:
  Init_RadarWarn_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RadarWarn_drone_id header(::interface::msg::RadarWarn::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_RadarWarn_drone_id(msg_);
  }

private:
  ::interface::msg::RadarWarn msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interface::msg::RadarWarn>()
{
  return interface::msg::builder::Init_RadarWarn_header();
}

}  // namespace interface

#endif  // INTERFACE__MSG__DETAIL__RADAR_WARN__BUILDER_HPP_
