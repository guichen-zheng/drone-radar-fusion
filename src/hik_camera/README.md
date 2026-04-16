# src/hik_camera/ — 海康相机 ROS2 驱动（★ 待填入）

## 说明
此目录为海康相机驱动占位。该驱动**不在本项目中构建**，需从以下来源获取：

## 推荐驱动方案

### 方案 A：第三方 ROS2 封装（推荐快速上手）
```bash
# 仓库：https://github.com/whlook/ros_hik_camera
git clone https://github.com/whlook/ros_hik_camera.git src/hik_camera
colcon build --packages-select hik_camera
```
发布 Topic：`/hik_camera/image_raw`（`sensor_msgs/Image`）

### 方案 B：海康官方 MVS SDK + 自封装
1. 从海康官网下载 MVS SDK（Linux 版）：
   https://www.hikrobotics.com/cn/machinevision/service/download
2. 安装 SDK 后参考 SDK 示例封装 ROS2 节点
3. 节点应发布 Topic：`/hik_camera/image_raw`

## 与本项目的接口
camera_vision 包的 `yolo_detector` 节点订阅：
```
/hik_camera/image_raw   (sensor_msgs/msg/Image)
```
只需确保驱动发布此 Topic，无需修改 camera_vision 任何代码。
