// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interface:msg/DroneDetect.idl
// generated code does not contain a copyright notice

#ifndef INTERFACE__MSG__DETAIL__DRONE_DETECT__TRAITS_HPP_
#define INTERFACE__MSG__DETAIL__DRONE_DETECT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "interface/msg/detail/drone_detect__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace interface
{

namespace msg
{

inline void to_flow_style_yaml(
  const DroneDetect & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: drone_id
  {
    out << "drone_id: ";
    rosidl_generator_traits::value_to_yaml(msg.drone_id, out);
    out << ", ";
  }

  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << ", ";
  }

  // member: z
  {
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << ", ";
  }

  // member: vx
  {
    out << "vx: ";
    rosidl_generator_traits::value_to_yaml(msg.vx, out);
    out << ", ";
  }

  // member: vy
  {
    out << "vy: ";
    rosidl_generator_traits::value_to_yaml(msg.vy, out);
    out << ", ";
  }

  // member: vz
  {
    out << "vz: ";
    rosidl_generator_traits::value_to_yaml(msg.vz, out);
    out << ", ";
  }

  // member: confidence
  {
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
    out << ", ";
  }

  // member: bbox_x
  {
    out << "bbox_x: ";
    rosidl_generator_traits::value_to_yaml(msg.bbox_x, out);
    out << ", ";
  }

  // member: bbox_y
  {
    out << "bbox_y: ";
    rosidl_generator_traits::value_to_yaml(msg.bbox_y, out);
    out << ", ";
  }

  // member: bbox_w
  {
    out << "bbox_w: ";
    rosidl_generator_traits::value_to_yaml(msg.bbox_w, out);
    out << ", ";
  }

  // member: bbox_h
  {
    out << "bbox_h: ";
    rosidl_generator_traits::value_to_yaml(msg.bbox_h, out);
    out << ", ";
  }

  // member: label
  {
    out << "label: ";
    rosidl_generator_traits::value_to_yaml(msg.label, out);
    out << ", ";
  }

  // member: is_tracked
  {
    out << "is_tracked: ";
    rosidl_generator_traits::value_to_yaml(msg.is_tracked, out);
    out << ", ";
  }

  // member: lat
  {
    out << "lat: ";
    rosidl_generator_traits::value_to_yaml(msg.lat, out);
    out << ", ";
  }

  // member: lng
  {
    out << "lng: ";
    rosidl_generator_traits::value_to_yaml(msg.lng, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DroneDetect & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: drone_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "drone_id: ";
    rosidl_generator_traits::value_to_yaml(msg.drone_id, out);
    out << "\n";
  }

  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }

  // member: z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "z: ";
    rosidl_generator_traits::value_to_yaml(msg.z, out);
    out << "\n";
  }

  // member: vx
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "vx: ";
    rosidl_generator_traits::value_to_yaml(msg.vx, out);
    out << "\n";
  }

  // member: vy
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "vy: ";
    rosidl_generator_traits::value_to_yaml(msg.vy, out);
    out << "\n";
  }

  // member: vz
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "vz: ";
    rosidl_generator_traits::value_to_yaml(msg.vz, out);
    out << "\n";
  }

  // member: confidence
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "confidence: ";
    rosidl_generator_traits::value_to_yaml(msg.confidence, out);
    out << "\n";
  }

  // member: bbox_x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "bbox_x: ";
    rosidl_generator_traits::value_to_yaml(msg.bbox_x, out);
    out << "\n";
  }

  // member: bbox_y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "bbox_y: ";
    rosidl_generator_traits::value_to_yaml(msg.bbox_y, out);
    out << "\n";
  }

  // member: bbox_w
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "bbox_w: ";
    rosidl_generator_traits::value_to_yaml(msg.bbox_w, out);
    out << "\n";
  }

  // member: bbox_h
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "bbox_h: ";
    rosidl_generator_traits::value_to_yaml(msg.bbox_h, out);
    out << "\n";
  }

  // member: label
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "label: ";
    rosidl_generator_traits::value_to_yaml(msg.label, out);
    out << "\n";
  }

  // member: is_tracked
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "is_tracked: ";
    rosidl_generator_traits::value_to_yaml(msg.is_tracked, out);
    out << "\n";
  }

  // member: lat
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "lat: ";
    rosidl_generator_traits::value_to_yaml(msg.lat, out);
    out << "\n";
  }

  // member: lng
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "lng: ";
    rosidl_generator_traits::value_to_yaml(msg.lng, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DroneDetect & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace interface

namespace rosidl_generator_traits
{

[[deprecated("use interface::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const interface::msg::DroneDetect & msg,
  std::ostream & out, size_t indentation = 0)
{
  interface::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use interface::msg::to_yaml() instead")]]
inline std::string to_yaml(const interface::msg::DroneDetect & msg)
{
  return interface::msg::to_yaml(msg);
}

template<>
inline const char * data_type<interface::msg::DroneDetect>()
{
  return "interface::msg::DroneDetect";
}

template<>
inline const char * name<interface::msg::DroneDetect>()
{
  return "interface/msg/DroneDetect";
}

template<>
struct has_fixed_size<interface::msg::DroneDetect>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<interface::msg::DroneDetect>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<interface::msg::DroneDetect>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACE__MSG__DETAIL__DRONE_DETECT__TRAITS_HPP_
