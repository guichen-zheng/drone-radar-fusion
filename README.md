# drone-radar-fusion

> 海康相机（YOLO）+ Livox Avia 激光雷达 双模态无人机检测与定位系统
> 基于 ROS2 Humble，后融合架构

---

## 系统架构

```
Livox Avia ──► livox_ros2_avia ──► /livox/lidar ──► radar
                                                       │ /radar/detect
海康相机 ──► hik_camera_ros2_driver ──► /hik_camera/image_raw ──► camera_vision
                                                       │ /camera/detect_result
                                                       ▼
                                                    fusion ──► /fusion/final_result
                                                       │           ├─ web_dashboard（地图+报警）
                                                       │           └─ /fusion/markers（RViz/Foxglove）
                                                       └─► /fusion/warn_json ──► 报警推送
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
│       ├── yolo_drone.onnx          # VisDrone + YOLOv8 训练导出
│       └── classes.txt              # ★待填入（如 drone）
│
├── launch/
│   └── full_system_launch.py        # 一键顺序启动全系统
│
├── scripts/
│   ├── deps.sh                      # 拉取外部驱动（hik_camera / livox_driver）
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
│   ├── radar/                       # ② Livox 点云处理（C++）
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
│   ├── camera_vision/               # ③ YOLO 推理（C++，OpenCV DNN/CUDA）
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
│   ├── fusion/                      # ④ 核心融合包（C++）
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
│   ├── web_dashboard/               # ⑤ Web 可视化（Python）
│   │   ├── setup.py
│   │   ├── package.xml
│   │   ├── templates/
│   │   │   └── index.html           # Leaflet地图+光标+高度+报警弹窗
│   │   ├── resource/
│   │   │   └── web_dashboard        # ament 资源标记
│   │   └── web_dashboard/           # Python 包（ament_python 规范）
│   │       ├── __init__.py
│   │       ├── app.py               # Flask+SocketIO 后端，ROS2 订阅→推送
│   │       └── watchdog_node.py     # 进程看门狗，每5秒检测+自动重启
│   │
│   ├── hik_camera/                  # 海康相机驱动（由 deps.sh 拉取）
│   │   └── ...                      # hik_camera_ros2_driver
│   │
│   └── livox_driver/                # Livox Avia 驱动（由 deps.sh 拉取）
│       └── ...                      # livox_ros2_avia（含 livox_interfaces、livox_sdk_vendor）
```

## 快速上手

### 1. 系统依赖

```bash
# ROS2 Humble 基础依赖
sudo apt install \
    ros-humble-pcl-conversions ros-humble-cv-bridge \
    ros-humble-message-filters ros-humble-visualization-msgs \
    ros-humble-camera-info-manager \
    libpcl-dev libeigen3-dev libopencv-dev libyaml-cpp-dev

# Web Dashboard Python 依赖（推荐用 apt，避免与系统 ROS2 冲突）
sudo apt install python3-flask python3-flask-socketio python3-cv2

# WebSocket 性能优化（可选，消除 "WebSocket transport not available" 警告）
sudo apt install python3-eventlet
```

### 2. 拉取外部驱动

项目依赖两个外部驱动，通过 `deps.sh` 一键克隆：

```bash
cd drone-radar-fusion
bash scripts/deps.sh
```

| 驱动目录 | 仓库 | 说明 |
|----------|------|------|
| `src/hik_camera/` | [hik_camera_ros2_driver](https://github.com/SMBU-PolarBear-Robotics-Team/hik_camera_ros2_driver) | 海康相机 ROS2 驱动 |
| `src/livox_driver/` | [livox_ros2_avia](https://github.com/ASIG-X/livox_ros2_avia) | Livox Avia 雷达驱动 |

> 如需手动克隆，直接替换脚本中对应 URL 即可。

### 3. 填入缺失文件（★ 标注的部分）

| 文件 | 来源 |
|------|------|
| `model/ONNX/yolo_drone.onnx` | 用 VisDrone 数据集训练 YOLOv8，`yolo export format=onnx` 导出 |
| `config/drone_map.pcd` | 用 Livox Avia 扫描监控区域，`ros2 bag record /livox/lidar` 后用 pcl 工具导出 |
| `config/out_matrix.yaml` | 用 Kalibr 或五点标定工具完成相机-雷达外参标定 |

### 4. 修改参数

编辑 `config/params.yaml`：

```yaml
origin_lat: 22.123456      # 监控区域地理纬度（地图光标基准）
origin_lng: 114.123456     # 监控区域地理经度
drone_min_height: 2.0      # 最小检测高度（米），低于此值忽略
drone_max_height: 120.0    # 最大检测高度（米）
warn_confidence: 0.6       # 报警置信度阈值
```

### 5. 编译

```bash
cd drone-radar-fusion
bash scripts/build.sh
```

编译顺序：`interface` → `radar` + `camera_vision` + `fusion`（并行）→ `web_dashboard` → `livox_interfaces` → `livox_sdk_vendor` → `livox_ros2_avia` → `hik_camera_ros2_driver`

> **使用 `--clean` 选项完整重编译：**
> ```bash
> bash scripts/build.sh --clean
> ```
> 注意：`--clean` 会删除 `build/` 和 `install/` 目录，重编译后需重新 source：
> ```bash
> source install/setup.bash
> ```

### 6. 启动

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash

# 一键启动全系统（推荐）
ros2 launch launch/full_system_launch.py
```

各组件启动顺序（由 launch 文件控制延迟）：

| 延迟 | 组件 | 说明 |
|------|------|------|
| 0s | livox_ros2_avia | Livox 雷达驱动 |
| 3s | radar | 点云处理节点 |
| 3s | camera_vision | 相机 + YOLO 推理 |
| 5s | fusion | 雷达-相机融合 |
| 6s | web_dashboard_node | Flask Web 服务 |
| 9s | watchdog_node | 进程看门狗 |

**分步启动（调试用）：**

```bash
ros2 launch livox_ros2_avia livox_lidar_launch.py         # 终端 1
ros2 launch radar radar_launch.py                          # 终端 2
ros2 launch camera_vision camera_launch.py                 # 终端 3
ros2 launch fusion fusion_launch.py                        # 终端 4
ros2 run web_dashboard web_dashboard_node                  # 终端 5
ros2 run web_dashboard watchdog_node                       # 终端 6（可选）
```

> **重启全系统时**，需先彻底停止旧进程，否则 web_dashboard 会因端口 5000 占用而报错：
> ```bash
> pkill -f "ros2 launch" && pkill -f "web_dashboard_node" && \
> pkill -f "radar" && pkill -f "yolo_detector" && pkill -f "fusion_manager"
> sleep 2
> ros2 launch launch/full_system_launch.py
> ```

### 7. 可视化

- **Web 地图**：浏览器打开 `http://localhost:5000`（无人机光标 + 高度 + 报警弹窗）
- **Foxglove Studio**：连接 `ws://localhost:8765`，订阅 `/fusion/markers` 和 `/camera/debug_image`
- **RViz2**：添加 MarkerArray（`/fusion/markers`）和 PointCloud2（`/radar/dynamic_cloud`）

> 无人机硬件未连接时：hik_camera 和 radar 会报 `No camera found` / `Invalid bd:` 错误并持续重试，属正常现象。Web 地图页面仍可正常加载，但不显示目标数据。

### 8. rosbag 录制与回放（数据驱动调试）

实物跑通后，把关键 topic 录成 rosbag，可以在没有硬件的环境里反复回放，用于
调试融合参数、卡尔曼追踪、报警规则等下游算法。

#### 录制

```bash
# 终端 A：照常启动实物系统
ros2 launch launch/full_system_launch.py

# 终端 B：开始录制
bash scripts/record_bag.sh                       # 自动命名 drone_fusion_YYYYMMDD_HHMMSS
bash scripts/record_bag.sh my_test_3drones      # 自定义名字
```

默认录到 `~/bags/<名字>/`，zstd 压缩；Ctrl+C 停。**注意**：raw 点云 + 图像约
3–5 GB/min，录前 `df -h ~` 确认空间。

**录到移动硬盘 / 其他位置**：用 `BAG_ROOT` 环境变量覆盖根目录，脚本会自动 mkdir。

```bash
# 先确认硬盘挂载点
df -h | grep media

# 录制时指定 BAG_ROOT（例：挂在 /media/guichen/MyDisk/）
BAG_ROOT=/media/guichen/MyDisk/bags  bash scripts/record_bag.sh my_test

# 想长期固定到硬盘，加进 ~/.bashrc：
# export BAG_ROOT=/media/guichen/MyDisk/bags
```

⚠️ 移动硬盘必须是 **ext4/xfs/NTFS**（FAT32/exFAT 不支持大文件，超过 4GB 会截断）；
USB3.0 / SSD 才够写入速度，USB2.0 慢盘可能丢消息。

#### 回放

`launch/playback_launch.py` **只启动下游节点**（不启动 livox / hik 驱动），
所有节点自动设 `use_sim_time:=true` 让时间戳走 bag /clock。

```bash
# 方式 A：launch 自动启动 ros2 bag play（默认循环）
ros2 launch launch/playback_launch.py bag_path:=$HOME/bags/my_test_3drones rate:=1.0

# 方式 B：只起处理管线，bag 手动播（支持暂停 SPACE / 单步 S）
ros2 launch launch/playback_launch.py
# 另开终端：
bash scripts/play_bag.sh ~/bags/my_test_3drones
```

回放时浏览器 `http://localhost:5000` 和 RViz 同样可用，**看到的可视化效果与实物
运行时完全一致**。

#### 录制了哪些 topic（由 `scripts/record_bag.sh` 决定）

| 类别 | Topic |
|------|-------|
| 原始数据 | `/livox/lidar` `/hik_camera/image_raw` |
| 雷达输出 | `/radar/detect` `/radar/dynamic_cloud` |
| 相机输出 | `/camera/detect_result` `/camera/debug_image` |
| 融合输出 | `/fusion/final_result` `/fusion/warn` `/fusion/markers` |

回放时下游节点会**重新计算**（忽略 bag 里录的处理结果 topic），所以可以改
`config/params.yaml` 后回放看效果。

---

## Topic 一览

| Topic | 类型 | 发布节点 | 说明 |
|-------|------|----------|------|
| `/livox/lidar` | PointCloud2 | livox_ros2_avia | 原始点云 |
| `/hik_camera/image_raw` | Image | hik_camera_ros2_driver | 原始图像 |
| `/radar/detect` | DroneDetectArray | radar | 雷达候选目标（含高度） |
| `/camera/detect_result` | DroneDetectArray | camera_vision | YOLO 检测结果（BBox） |
| `/camera/debug_image` | Image | camera_vision | YOLO 标注调试图像 |
| `/fusion/final_result` | DroneDetectArray | fusion | 融合最终结果（含坐标+高度） |
| `/fusion/markers` | MarkerArray | fusion | RViz/Foxglove 可视化 Marker |
| `/fusion/warn` | RadarWarn | fusion | 结构化报警消息 |
| `/fusion/warn_json` | String (JSON) | fusion | JSON 报警（供 Web Dashboard） |
| `/watchdog/system_status` | String (JSON) | watchdog_node | 各节点存活状态 |

---

## 常见问题

**Q: `web_dashboard` 启动时报 `PackageNotFoundError: package 'web_dashboard' not found`**

编译后需要重新 source 环境：
```bash
source install/setup.bash
```

**Q: 浏览器访问 `localhost:5000` 显示 500 Internal Server Error**

通常是旧进程仍在占用端口。先杀掉旧进程再重启：
```bash
pkill -9 -f web_dashboard_node
ros2 run web_dashboard web_dashboard_node
```

**Q: `OSError: [Errno 98] Address already in use`**

端口 5000 被占用，参考上方「重启全系统」步骤。

**Q: `WebSocket transport not available` 警告**

安装 eventlet 可消除此警告并提升 WebSocket 性能：
```bash
sudo apt install python3-eventlet
```

**Q: hik_camera 报 `No camera found`，radar 报 `Invalid bd:`**

硬件未连接，节点会持续重试。连接实际硬件后自动恢复，不影响其他节点运行。
