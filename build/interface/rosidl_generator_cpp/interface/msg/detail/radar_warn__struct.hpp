// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interface:msg/RadarWarn.idl
// generated code does not contain a copyright notice

#ifndef INTERFACE__MSG__DETAIL__RADAR_WARN__STRUCT_HPP_
#define INTERFACE__MSG__DETAIL__RADAR_WARN__STRUCT_HPP_

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
// Member 'detected_at'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__interface__msg__RadarWarn __attribute__((deprecated))
#else
# define DEPRECATED__interface__msg__RadarWarn __declspec(deprecated)
#endif

namespace interface
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct RadarWarn_
{
  using Type = RadarWarn_<ContainerAllocator>;

  explicit RadarWarn_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    detected_at(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->drone_id = 0ul;
      this->x = 0.0;
      this->y = 0.0;
      this->z = 0.0;
      this->confidence = 0.0;
      this->warn_level = "";
      this->description = "";
    }
  }

  explicit RadarWarn_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    warn_level(_alloc),
    description(_alloc),
    detected_at(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->drone_id = 0ul;
      this->x = 0.0;
      this->y = 0.0;
      this->z = 0.0;
      this->confidence = 0.0;
      this->warn_level = "";
      this->description = "";
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
  using _confidence_type =
    double;
  _confidence_type confidence;
  using _warn_level_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _warn_level_type warn_level;
  using _description_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _description_type description;
  using _detected_at_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _detected_at_type detected_at;

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
  Type & set__confidence(
    const double & _arg)
  {
    this->confidence = _arg;
    return *this;
  }
  Type & set__warn_level(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->warn_level = _arg;
    return *this;
  }
  Type & set__description(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->description = _arg;
    return *this;
  }
  Type & set__detected_at(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->detected_at = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interface::msg::RadarWarn_<ContainerAllocator> *;
  using ConstRawPtr =
    const interface::msg::RadarWarn_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interface::msg::RadarWarn_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interface::msg::RadarWarn_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interface::msg::RadarWarn_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interface::msg::RadarWarn_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interface::msg::RadarWarn_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interface::msg::RadarWarn_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interface::msg::RadarWarn_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interface::msg::RadarWarn_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interface__msg__RadarWarn
    std::shared_ptr<interface::msg::RadarWarn_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interface__msg__RadarWarn
    std::shared_ptr<interface::msg::RadarWarn_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RadarWarn_ & other) const
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
    if (this->confidence != other.confidence) {
      return false;
    }
    if (this->warn_level != other.warn_level) {
      return false;
    }
    if (this->description != other.description) {
      return false;
    }
    if (this->detected_at != other.detected_at) {
      return false;
    }
    return true;
  }
  bool operator!=(const RadarWarn_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RadarWarn_

// alias to use template instance with default allocator
using RadarWarn =
  interface::msg::RadarWarn_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interface

#endif  // INTERFACE__MSG__DETAIL__RADAR_WARN__STRUCT_HPP_
