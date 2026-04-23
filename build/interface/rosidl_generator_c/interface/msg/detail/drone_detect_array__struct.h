// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interface:msg/DroneDetectArray.idl
// generated code does not contain a copyright notice

#ifndef INTERFACE__MSG__DETAIL__DRONE_DETECT_ARRAY__STRUCT_H_
#define INTERFACE__MSG__DETAIL__DRONE_DETECT_ARRAY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'drones'
#include "interface/msg/detail/drone_detect__struct.h"

/// Struct defined in msg/DroneDetectArray in the package interface.
typedef struct interface__msg__DroneDetectArray
{
  std_msgs__msg__Header header;
  /// 当前帧所有检测到的无人机列表
  interface__msg__DroneDetect__Sequence drones;
} interface__msg__DroneDetectArray;

// Struct for a sequence of interface__msg__DroneDetectArray.
typedef struct interface__msg__DroneDetectArray__Sequence
{
  interface__msg__DroneDetectArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interface__msg__DroneDetectArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACE__MSG__DETAIL__DRONE_DETECT_ARRAY__STRUCT_H_
