// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interface:msg/DroneDetect.idl
// generated code does not contain a copyright notice

#ifndef INTERFACE__MSG__DETAIL__DRONE_DETECT__STRUCT_H_
#define INTERFACE__MSG__DETAIL__DRONE_DETECT__STRUCT_H_

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
// Member 'label'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/DroneDetect in the package interface.
typedef struct interface__msg__DroneDetect
{
  std_msgs__msg__Header header;
  /// 无人机唯一 ID（多目标追踪）
  uint32_t drone_id;
  /// 世界坐标 X（米）
  double x;
  /// 世界坐标 Y（米）
  double y;
  /// 高度 Z（米）
  double z;
  /// X 方向速度（米/秒）
  double vx;
  /// Y 方向速度（米/秒）
  double vy;
  /// Z 方向速度（米/秒）
  double vz;
  /// 融合置信度（0.0 ~ 1.0）
  double confidence;
  /// 图像 bounding box 左上角 x（像素）
  int32_t bbox_x;
  /// 图像 bounding box 左上角 y（像素）
  int32_t bbox_y;
  /// bounding box 宽度（像素）
  int32_t bbox_w;
  /// bounding box 高度（像素）
  int32_t bbox_h;
  /// 类别标签（如 "drone"）
  rosidl_runtime_c__String label;
  /// 是否处于卡尔曼追踪状态
  bool is_tracked;
  /// 地理坐标（由 fusion 包通过 CoordTransform 填入，供 web_dashboard 使用）
  /// 纬度（度，WGS84）
  double lat;
  /// 经度（度，WGS84）
  double lng;
} interface__msg__DroneDetect;

// Struct for a sequence of interface__msg__DroneDetect.
typedef struct interface__msg__DroneDetect__Sequence
{
  interface__msg__DroneDetect * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interface__msg__DroneDetect__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACE__MSG__DETAIL__DRONE_DETECT__STRUCT_H_
