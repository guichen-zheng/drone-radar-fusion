// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interface:msg/DroneDetect.idl
// generated code does not contain a copyright notice

#ifndef INTERFACE__MSG__DETAIL__DRONE_DETECT__STRUCT_HPP_
#define INTERFACE__MSG__DETAIL__DRONE_DETECT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__interface__msg__DroneDetect __attribute__((deprecated))
#else
# define DEPRECATED__interface__msg__DroneDetect __declspec(deprecated)
#endif

namespace interface
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct DroneDetect_
{
  using Type = DroneDetect_<ContainerAllocator>;

  explicit DroneDetect_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->drone_id = 0ul;
      this->x = 0.0;
      this->y = 0.0;
      this->z = 0.0;
      this->vx = 0.0;
      this->vy = 0.0;
      this->vz = 0.0;
      this->confidence = 0.0;
      this->bbox_x = 0l;
      this->bbox_y = 0l;
      this->bbox_w = 0l;
      this->bbox_h = 0l;
      this->label = "";
      this->is_tracked = false;
      this->lat = 0.0;
      this->lng = 0.0;
    }
  }

  explicit DroneDetect_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    label(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->drone_id = 0ul;
      this->x = 0.0;
      this->y = 0.0;
      this->z = 0.0;
      this->vx = 0.0;
      this->vy = 0.0;
      this->vz = 0.0;
      this->confidence = 0.0;
      this->bbox_x = 0l;
      this->bbox_y = 0l;
      this->bbox_w = 0l;
      this->bbox_h = 0l;
      this->label = "";
      this->is_tracked = false;
      this->lat = 0.0;
      this->lng = 0.0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _drone_id_type =
    uint32_t;
  _drone_id_type drone_id;
  using _x_type =
    double;
  _x_type x;
  using _y_type =
    double;
  _y_type y;
  using _z_type =
    double;
  _z_type z;
  using _vx_type =
    double;
  _vx_type vx;
  using _vy_type =
    double;
  _vy_type vy;
  using _vz_type =
    double;
  _vz_type vz;
  using _confidence_type =
    double;
  _confidence_type confidence;
  using _bbox_x_type =
    int32_t;
  _bbox_x_type bbox_x;
  using _bbox_y_type =
    int32_t;
  _bbox_y_type bbox_y;
  using _bbox_w_type =
    int32_t;
  _bbox_w_type bbox_w;
  using _bbox_h_type =
    int32_t;
  _bbox_h_type bbox_h;
  using _label_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _label_type label;
  using _is_tracked_type =
    bool;
  _is_tracked_type is_tracked;
  using _lat_type =
    double;
  _lat_type lat;
  using _lng_type =
    double;
  _lng_type lng;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__drone_id(
    const uint32_t & _arg)
  {
    this->drone_id = _arg;
    return *this;
  }
  Type & set__x(
    const double & _arg)
  {
    this->x = _arg;
    return *this;
  }
  Type & set__y(
    const double & _arg)
  {
    this->y = _arg;
    return *this;
  }
  Type & set__z(
    const double & _arg)
  {
    this->z = _arg;
    return *this;
  }
  Type & set__vx(
    const double & _arg)
  {
    this->vx = _arg;
    return *this;
  }
  Type & set__vy(
    const double & _arg)
  {
    this->vy = _arg;
    return *this;
  }
  Type & set__vz(
    const double & _arg)
  {
    this->vz = _arg;
    return *this;
  }
  Type & set__confidence(
    const double & _arg)
  {
    this->confidence = _arg;
    return *this;
  }
  Type & set__bbox_x(
    const int32_t & _arg)
  {
    this->bbox_x = _arg;
    return *this;
  }
  Type & set__bbox_y(
    const int32_t & _arg)
  {
    this->bbox_y = _arg;
    return *this;
  }
  Type & set__bbox_w(
    const int32_t & _arg)
  {
    this->bbox_w = _arg;
    return *this;
  }
  Type & set__bbox_h(
    const int32_t & _arg)
  {
    this->bbox_h = _arg;
    return *this;
  }
  Type & set__label(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->label = _arg;
    return *this;
  }
  Type & set__is_tracked(
    const bool & _arg)
  {
    this->is_tracked = _arg;
    return *this;
  }
  Type & set__lat(
    const double & _arg)
  {
    this->lat = _arg;
    return *this;
  }
  Type & set__lng(
    const double & _arg)
  {
    this->lng = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interface::msg::DroneDetect_<ContainerAllocator> *;
  using ConstRawPtr =
    const interface::msg::DroneDetect_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interface::msg::DroneDetect_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interface::msg::DroneDetect_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interface::msg::DroneDetect_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interface::msg::DroneDetect_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interface::msg::DroneDetect_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interface::msg::DroneDetect_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interface::msg::DroneDetect_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interface::msg::DroneDetect_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interface__msg__DroneDetect
    std::shared_ptr<interface::msg::DroneDetect_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interface__msg__DroneDetect
    std::shared_ptr<interface::msg::DroneDetect_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DroneDetect_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->drone_id != other.drone_id) {
      return false;
    }
    if (this->x != other.x) {
      return false;
    }
    if (this->y != other.y) {
      return false;
    }
    if (this->z != other.z) {
      return false;
    }
    if (this->vx != other.vx) {
      return false;
    }
    if (this->vy != other.vy) {
      return false;
    }
    if (this->vz != other.vz) {
      return false;
    }
    if (this->confidence != other.confidence) {
      return false;
    }
    if (this->bbox_x != other.bbox_x) {
      return false;
    }
    if (this->bbox_y != other.bbox_y) {
      return false;
    }
    if (this->bbox_w != other.bbox_w) {
      return false;
    }
    if (this->bbox_h != other.bbox_h) {
      return false;
    }
    if (this->label != other.label) {
      return false;
    }
    if (this->is_tracked != other.is_tracked) {
      return false;
    }
    if (this->lat != other.lat) {
      return false;
    }
    if (this->lng != other.lng) {
      return false;
    }
    return true;
  }
  bool operator!=(const DroneDetect_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DroneDetect_

// alias to use template instance with default allocator
using DroneDetect =
  interface::msg::DroneDetect_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interface

#endif  // INTERFACE__MSG__DETAIL__DRONE_DETECT__STRUCT_HPP_
