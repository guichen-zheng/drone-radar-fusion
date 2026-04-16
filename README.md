# drone-radar-fusion

> 海康相机（YOLO）+ Livox Avia 激光雷达 双模态无人机检测与定位系统
> 基于 ROS2，参考 [guichen-zheng/lidar](https://github.com/guichen-zheng/lidar) 后融合架构

---

## 系统架构

```
Livox Avia ──► livox_driver ──► /livox/lidar ──► radar
                                                    │ /radar/detect
海康相机 ──► hik_camera ──► /hik_camera/image_raw ──► camera_vision
                                                    │ /camera/detect_result
                                                    ▼
                                                 fusion  ──► /fusion/final_result
                                                    │           ├─ web_dashboard（地图+报警）
                                                    │           └─ /fusion/markers（RViz/Foxglove）
                                                    └─► /fusion/warn ──► 报警推送
```

## 目录结构

```
drone-radar-fusion/
├── README.md
├── .gitignore
│
├── config/                          # 配置 · 标定 · 地图
│   ├── params.yaml                  # 所有节点统一参数（origin_lat/lng 在此改）
│   ├── out_matrix.yaml              # 相机内参 + 相机-雷达外参  ★待填入
│   ├── foxglove_layout.json         # Foxglove Studio 预配置布局
│   └── calib_tool/
│       └── calib_interactive.py     # 键盘交互式外参标定工具
│                                    # （drone_map.pcd 也放此目录  ★待填入）
│
├── model/
│   └── ONNX/
│       ├── README.md                # 训练/导出说明
│       ├── yolo_drone.onnx          # ★待填入（VisDrone + YOLOv8 训练导出）
│       └── classes.txt              # ★待填入（如 drone）
│
├── launch/
│   └── full_system_launch.py        # 一键顺序启动全系统
│
├── scripts/
│   ├── build.sh                     # 按依赖顺序编译
│   ├── record_bag.sh                # 录制 rosbag
│   └── play_bag.sh                  # 回放 rosbag
│
├── src/
│   ├── interface/                   # ① 自定义消息（最先编译）
│   │   ├── CMakeLists.txt
│   │   ├── package.xml
│   │   └── msg/
│   │       ├── DroneDetect.msg      # 单目标：坐标/高度/速度/BBox/lat/lng
│   │       ├── DroneDetectArray.msg # 目标列表
│   │       └── RadarWarn.msg        # 报警消息
│   │
│   ├── utils/                       # ② 纯头文件工具库（header-only）
│   │   ├── CMakeLists.txt
│   │   ├── package.xml
│   │   └── include/utils/
│   │       ├── coord_transform.hpp  # 雷达坐标→ENU→WGS84
│   │       ├── detection_logger.hpp # CSV日志 + FPS计数器
│   │       └── bbox_utils.hpp       # IOU / 匈牙利匹配
│   │
│   ├── radar/                       # ③ Livox 点云处理（C++）
│   │   ├── CMakeLists.txt
│   │   ├── package.xml
│   │   ├── include/radar/
│   │   │   └── radar_processor.hpp
│   │   ├── src/
│   │   │   ├── radar_processor.cpp  # 滤波→ROI→GICP→聚类→高度筛选
│   │   │   └── radar_node.cpp
│   │   └── launch/
│   │       └── radar_launch.py
│   │
│   ├── camera_vision/               # ④ YOLO 推理（C++，OpenCV DNN/CUDA）
│   │   ├── CMakeLists.txt
│   │   ├── package.xml
│   │   ├── include/camera_vision/
│   │   │   └── yolo_detector.hpp
│   │   ├── src/
│   │   │   ├── yolo_detector.cpp    # Letterbox→推理→NMS→BBox发布
│   │   │   └── camera_node.cpp
│   │   └── launch/
│   │       └── camera_launch.py
│   │
│   ├── fusion/                      # ⑤ 核心融合包（C++）
│   │   ├── CMakeLists.txt
│   │   ├── package.xml
│   │   ├── include/fusion/
│   │   │   ├── fusion_manager.hpp   # 时间同步/匹配/追踪/报警
│   │   │   └── kalman_filter.hpp    # 6维卡尔曼（位置+速度）
│   │   ├── src/
│   │   │   ├── fusion_manager.cpp
│   │   │   ├── fusion_node.cpp
│   │   │   └── kalman_filter.cpp
│   │   └── launch/
│   │       └── fusion_launch.py
│   │
│   ├── web_dashboard/               # ⑥ Web 可视化（Python）
│   │   ├── setup.py
│   │   ├── package.xml
│   │   ├── app.py                   # Flask+SocketIO 后端
│   │   ├── templates/
│   │   │   └── index.html           # Leaflet地图+光标+高度+报警弹窗
│   │   ├── resource/
│   │   │   └── web_dashboard        # ament 资源标记
│   │   └── web_dashboard/
│   │       └── __init__.py
│   │
│   ├── hik_camera/                  # ★待填入：海康相机驱动
│   │   └── README.md                # → git clone ros_hik_camera
│   │
│   └── livox_driver/                # ★待填入：Livox Avia 驱动
│       └── README.md                # → git clone livox_ros_driver2
│
└── watchDog/
    └── watchdog_node.py             # 进程看门狗，每5秒检测+自动重启
```

## 快速上手

### 1. 依赖安装
```bash
# ROS2 Humble（推荐）
sudo apt install ros-humble-pcl-conversions ros-humble-cv-bridge \
                 ros-humble-message-filters ros-humble-visualization-msgs \
                 libpcl-dev libeigen3-dev libopencv-dev libyaml-cpp-dev

# Python 依赖（web_dashboard）
pip3 install flask flask-socketio opencv-python numpy
```

### 2. 填入缺失文件（★ 标注的部分）
| 文件 | 来源 |
|------|------|
| `src/livox_driver/` | `git clone https://github.com/Livox-SDK/livox_ros_driver2` |
| `src/hik_camera/`   | `git clone https://github.com/whlook/ros_hik_camera` |
| `model/ONNX/yolo_drone.onnx` | 用 VisDrone 数据集训练 YOLOv8，导出 ONNX |
| `config/drone_map.pcd` | 用 Livox Avia 扫描监控区域保存点云 |
| `config/out_matrix.yaml` | 用 Kalibr 或五点标定工具标定相机-雷达外参 |

### 3. 修改参数
编辑 `config/params.yaml`：
- `origin_lat` / `origin_lng`：监控区域地理坐标（地图光标基准）
- `drone_min_height` / `drone_max_height`：根据实际场景调整
- `warn_confidence`：报警阈值

### 4. 编译
```bash
cd drone-radar-fusion
colcon build --symlink-install
source install/setup.bash
```

### 5. 启动
```bash
# 一键启动全系统
ros2 launch launch/full_system_launch.py

# 或分步启动（调试用）
ros2 launch livox_ros_driver2 livox_lidar_launch.py   # 终端 1
ros2 launch radar radar_launch.py                      # 终端 2
ros2 launch camera_vision camera_launch.py             # 终端 3
ros2 launch fusion fusion_launch.py                    # 终端 4
ros2 run web_dashboard web_dashboard_node              # 终端 5
```

### 6. 可视化
- **Web 地图**：浏览器打开 `http://localhost:5000`（无人机光标 + 高度 + 报警弹窗）
- **Foxglove Studio**：连接 `ws://localhost:8765`，订阅 `/fusion/markers` 和 `/camera/debug_image`
- **RViz2**：添加 MarkerArray（`/fusion/markers`）和 PointCloud2（`/radar/dynamic_cloud`）

## Topic 一览

| Topic | 类型 | 发布节点 | 说明 |
|-------|------|----------|------|
| `/livox/lidar` | PointCloud2 | livox_driver | 原始点云 |
| `/hik_camera/image_raw` | Image | hik_camera | 原始图像 |
| `/radar/detect` | DroneDetectArray | radar | 雷达候选目标（含高度） |
| `/camera/detect_result` | DroneDetectArray | camera_vision | YOLO 检测结果（BBox） |
| `/camera/debug_image` | Image | camera_vision | YOLO 标注调试图像 |
| `/fusion/final_result` | DroneDetectArray | fusion | 融合最终结果（含坐标+高度） |
| `/fusion/markers` | MarkerArray | fusion | RViz/Foxglove 可视化 Marker |
| `/fusion/warn` | RadarWarn | fusion | 结构化报警消息 |
| `/fusion/warn_json` | String (JSON) | fusion | JSON 报警（供 Web Dashboard） |
| `/watchdog/system_status` | String (JSON) | watchdog | 各节点存活状态 |
