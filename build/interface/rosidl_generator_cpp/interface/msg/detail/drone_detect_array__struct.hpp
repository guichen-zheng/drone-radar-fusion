// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interface:msg/DroneDetectArray.idl
// generated code does not contain a copyright notice

#ifndef INTERFACE__MSG__DETAIL__DRONE_DETECT_ARRAY__STRUCT_HPP_
#define INTERFACE__MSG__DETAIL__DRONE_DETECT_ARRAY__STRUCT_HPP_

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
// Member 'drones'
#include "interface/msg/detail/drone_detect__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__interface__msg__DroneDetectArray __attribute__((deprecated))
#else
# define DEPRECATED__interface__msg__DroneDetectArray __declspec(deprecated)
#endif

namespace interface
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct DroneDetectArray_
{
  using Type = DroneDetectArray_<ContainerAllocator>;

  explicit DroneDetectArray_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    (void)_init;
  }

  explicit DroneDetectArray_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _drones_type =
    std::vector<interface::msg::DroneDetect_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<interface::msg::DroneDetect_<ContainerAllocator>>>;
  _drones_type drones;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__drones(
    const std::vector<interface::msg::DroneDetect_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<interface::msg::DroneDetect_<ContainerAllocator>>> & _arg)
  {
    this->drones = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interface::msg::DroneDetectArray_<ContainerAllocator> *;
  using ConstRawPtr =
    const interface::msg::DroneDetectArray_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interface::msg::DroneDetectArray_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interface::msg::DroneDetectArray_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interface::msg::DroneDetectArray_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interface::msg::DroneDetectArray_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interface::msg::DroneDetectArray_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interface::msg::DroneDetectArray_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interface::msg::DroneDetectArray_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interface::msg::DroneDetectArray_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interface__msg__DroneDetectArray
    std::shared_ptr<interface::msg::DroneDetectArray_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interface__msg__DroneDetectArray
    std::shared_ptr<interface::msg::DroneDetectArray_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DroneDetectArray_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->drones != other.drones) {
      return false;
    }
    return true;
  }
  bool operator!=(const DroneDetectArray_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DroneDetectArray_

// alias to use template instance with default allocator
using DroneDetectArray =
  interface::msg::DroneDetectArray_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interface

#endif  // INTERFACE__MSG__DETAIL__DRONE_DETECT_ARRAY__STRUCT_HPP_
