// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interface:msg/RadarWarn.idl
// generated code does not contain a copyright notice

#ifndef INTERFACE__MSG__DETAIL__RADAR_WARN__STRUCT_H_
#define INTERFACE__MSG__DETAIL__RADAR_WARN__STRUCT_H_

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
// Member 'warn_level'
// Member 'description'
#include "rosidl_runtime_c/string.h"
// Member 'detected_at'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in msg/RadarWarn in the package interface.
typedef struct interface__msg__RadarWarn
{
  std_msgs__msg__Header header;
  /// 对应无人机 ID
  uint32_t drone_id;
  /// 世界坐标 X
  double x;
  /// 世界坐标 Y
  double y;
  /// 高度（米）
  double z;
  /// 置信度
  double confidence;
  /// 警告等级："LOW" / "MEDIUM" / "HIGH"
  rosidl_runtime_c__String warn_level;
  /// 报警描述（如 "Drone detected at zone A, height 50m"）
  rosidl_runtime_c__String description;
  /// 检测时间戳
  builtin_interfaces__msg__Time detected_at;
} interface__msg__RadarWarn;

// Struct for a sequence of interface__msg__RadarWarn.
typedef struct interface__msg__RadarWarn__Sequence
{
  interface__msg__RadarWarn * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interface__msg__RadarWarn__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACE__MSG__DETAIL__RADAR_WARN__STRUCT_H_
