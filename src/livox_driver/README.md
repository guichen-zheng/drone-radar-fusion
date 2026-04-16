# src/livox_driver/ — Livox Avia 驱动（★ 待填入）

## 说明
此目录为 Livox Avia 激光雷达驱动占位。请从官方仓库获取：

## 官方 ROS2 驱动
```bash
# Livox ROS2 驱动（官方）
git clone https://github.com/Livox-SDK/livox_ros_driver2.git src/livox_driver
colcon build --packages-select livox_ros_driver2
```

## 发布 Topic
驱动默认发布：
```
/livox/lidar   (sensor_msgs/msg/PointCloud2)
/livox/imu     (sensor_msgs/msg/Imu)
```
与本项目 radar 包的订阅 Topic 完全一致，无需额外修改。

## 配置文件
Livox 驱动需要配置 `MID360_config.json`（或 Avia 对应配置）
指定雷达 IP 地址，详见驱动 README。
