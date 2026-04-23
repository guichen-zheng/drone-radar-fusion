// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interface:msg/DroneDetect.idl
// generated code does not contain a copyright notice

#ifndef INTERFACE__MSG__DETAIL__DRONE_DETECT__BUILDER_HPP_
#define INTERFACE__MSG__DETAIL__DRONE_DETECT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "interface/msg/detail/drone_detect__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace interface
{

namespace msg
{

namespace builder
{

class Init_DroneDetect_lng
{
public:
  explicit Init_DroneDetect_lng(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  ::interface::msg::DroneDetect lng(::interface::msg::DroneDetect::_lng_type arg)
  {
    msg_.lng = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_lat
{
public:
  explicit Init_DroneDetect_lat(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_lng lat(::interface::msg::DroneDetect::_lat_type arg)
  {
    msg_.lat = std::move(arg);
    return Init_DroneDetect_lng(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_is_tracked
{
public:
  explicit Init_DroneDetect_is_tracked(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_lat is_tracked(::interface::msg::DroneDetect::_is_tracked_type arg)
  {
    msg_.is_tracked = std::move(arg);
    return Init_DroneDetect_lat(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_label
{
public:
  explicit Init_DroneDetect_label(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_is_tracked label(::interface::msg::DroneDetect::_label_type arg)
  {
    msg_.label = std::move(arg);
    return Init_DroneDetect_is_tracked(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_bbox_h
{
public:
  explicit Init_DroneDetect_bbox_h(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_label bbox_h(::interface::msg::DroneDetect::_bbox_h_type arg)
  {
    msg_.bbox_h = std::move(arg);
    return Init_DroneDetect_label(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_bbox_w
{
public:
  explicit Init_DroneDetect_bbox_w(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_bbox_h bbox_w(::interface::msg::DroneDetect::_bbox_w_type arg)
  {
    msg_.bbox_w = std::move(arg);
    return Init_DroneDetect_bbox_h(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_bbox_y
{
public:
  explicit Init_DroneDetect_bbox_y(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_bbox_w bbox_y(::interface::msg::DroneDetect::_bbox_y_type arg)
  {
    msg_.bbox_y = std::move(arg);
    return Init_DroneDetect_bbox_w(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_bbox_x
{
public:
  explicit Init_DroneDetect_bbox_x(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_bbox_y bbox_x(::interface::msg::DroneDetect::_bbox_x_type arg)
  {
    msg_.bbox_x = std::move(arg);
    return Init_DroneDetect_bbox_y(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_confidence
{
public:
  explicit Init_DroneDetect_confidence(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_bbox_x confidence(::interface::msg::DroneDetect::_confidence_type arg)
  {
    msg_.confidence = std::move(arg);
    return Init_DroneDetect_bbox_x(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_vz
{
public:
  explicit Init_DroneDetect_vz(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_confidence vz(::interface::msg::DroneDetect::_vz_type arg)
  {
    msg_.vz = std::move(arg);
    return Init_DroneDetect_confidence(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_vy
{
public:
  explicit Init_DroneDetect_vy(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_vz vy(::interface::msg::DroneDetect::_vy_type arg)
  {
    msg_.vy = std::move(arg);
    return Init_DroneDetect_vz(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_vx
{
public:
  explicit Init_DroneDetect_vx(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_vy vx(::interface::msg::DroneDetect::_vx_type arg)
  {
    msg_.vx = std::move(arg);
    return Init_DroneDetect_vy(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_z
{
public:
  explicit Init_DroneDetect_z(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_vx z(::interface::msg::DroneDetect::_z_type arg)
  {
    msg_.z = std::move(arg);
    return Init_DroneDetect_vx(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_y
{
public:
  explicit Init_DroneDetect_y(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_z y(::interface::msg::DroneDetect::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_DroneDetect_z(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_x
{
public:
  explicit Init_DroneDetect_x(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_y x(::interface::msg::DroneDetect::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_DroneDetect_y(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_drone_id
{
public:
  explicit Init_DroneDetect_drone_id(::interface::msg::DroneDetect & msg)
  : msg_(msg)
  {}
  Init_DroneDetect_x drone_id(::interface::msg::DroneDetect::_drone_id_type arg)
  {
    msg_.drone_id = std::move(arg);
    return Init_DroneDetect_x(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

class Init_DroneDetect_header
{
public:
  Init_DroneDetect_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DroneDetect_drone_id header(::interface::msg::DroneDetect::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_DroneDetect_drone_id(msg_);
  }

private:
  ::interface::msg::DroneDetect msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interface::msg::DroneDetect>()
{
  return interface::msg::builder::Init_DroneDetect_header();
}

}  // namespace interface

#endif  // INTERFACE__MSG__DETAIL__DRONE_DETECT__BUILDER_HPP_
