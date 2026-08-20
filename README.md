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

#### 实测现场没有背景 PCD 时

背景 PCD **不能跨场地通用**，也不能使用 Tello rosbag 的背景 PCD 代替。背景地图只
对应生成它时的雷达位置、朝向和静态场景。每次更换场地，或者移动/旋转 Avia 后，
都应先在没有无人机、人员尽量离开监控区的情况下录制 20--30 秒空场点云。

> 以下自动生成和启动命令依赖 `bag-workflow` 分支中的
> `scripts/build_background_pcd.py`、`config/radar_general_params.yaml` 以及
> `map_pcd_path` launch 参数；`main` 尚未合并这些实现时，请先合并对应功能代码。

```bash
# 终端 A：只启动 Avia 驱动，雷达位置和角度之后不能再动
cd /home/guichen/Documents/drone-radar-fusion
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch livox_ros2_avia livox_lidar_launch.py

# 终端 B：录制20--30秒后 Ctrl+C
source /opt/ros/humble/setup.bash
ros2 bag record /livox/lidar \
  -o /home/guichen/bags/avia_empty_scene

# 录制结束后生成现场背景 PCD
cd /home/guichen/Documents/drone-radar-fusion
source /opt/ros/humble/setup.bash
python3 scripts/build_background_pcd.py \
  /home/guichen/bags/avia_empty_scene \
  /home/guichen/Documents/drone-radar-fusion/config/site_background.pcd \
  --voxel-size 0.10 --min-frames 10

# 使用现场 PCD 启动实测
source install/setup.bash
ros2 launch launch/full_system_launch.py \
  map_pcd_path:=/home/guichen/Documents/drone-radar-fusion/config/site_background.pcd
```

注意：

- 生成背景后不能再移动或旋转雷达，否则必须重新生成。
- 录制背景时不能有无人机，人员也应尽量离开监控区域。
- 通用配置在地图缺失时会停止 `radar_node`，避免把墙、树木和地面识别成无人机。
- 不建议关闭 `background_required` 强行无背景运行，这会产生大量静态物体误报。

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

---

## 检测原理：雷达粗检 + 相机细分类

系统是**后融合**架构：雷达和相机各自独立检测，再在 `fusion_manager` 里匹配并融合。
两者的检测逻辑**完全不同**，**互相不可替代**。

> **一句话：雷达负责"哪里有东西在飞"（3D 定位），相机负责"那个东西是不是无人机"（分类）。**

### 雷达：纯几何 + 启发式阈值，**不识别形状**

`radar/radar_processor.cpp` 是六步无机器学习的几何流水线，**不存在任何"无人机
模型"或形状模板**。流程如下：

| 步骤 | 实现 | 作用 |
|------|------|------|
| ① 体素滤波 | `pcl::VoxelGrid`（leaf=0.15m） | 把原始点云降采到几千点，加速后续 |
| ② ROI 切割 | `pcl::CropBox`（**z ≥ 3m**） | **只保留 3 米以上的点** ← 地面/人/车/树全在此被排除 |
| ③ GICP 地图配准 | `pcl::GICP` 对静态地图差分 | 去除新出现的高层建筑/塔架（**当前是 TODO**，未实装） |
| ④ 离群点滤除 | `pcl::StatisticalOutlierRemoval` | 去掉远距离孤立噪声点 |
| ⑤ 欧氏聚类 | `pcl::EuclideanClusterExtraction`（tol=2m, 4~300 点） | 把连续点抠成独立物体 |
| ⑥ 三阈值过滤 | `filterDroneCandidates()` | 高度 5~200m + 包围盒 < 8m + 点数 4~300 |

**雷达眼里所谓"无人机"**：

> *在 5~200 米高空、包围盒小于 8 米、由 4~300 个点组成的、能聚成一团的反射物。*

它会**把鸟、气球、风筝、远处直升机一视同仁地报上来**；地面上的人/车被 ROI 第 ② 步
直接排除（z<3m）。雷达**没有任何能力**告诉你这是不是无人机 —— 它只能告诉你
"那里有个飞的小东西，坐标 (x,y,z)"。

### 相机：YOLOv8 神经网络分类

`camera_yolo/yolo_worker.py` 走神经网络：图像 → YOLOv8 推理 → 2D bbox + 分类标签 +
置信度。模型权重 `model/ONNX/yolo_drone.onnx` 用 VisDrone 数据集训练，**学习过
无人机的视觉特征**（旋翼、机身轮廓、纹理），能区分 drone / bird / human 等。

- ✅ 分类能力强（能区分鸟和无人机）
- ❌ 单目相机**没有任何距离/深度信息**，无法给出 3D 坐标

### 融合策略（[fusion_manager.cpp:84-112](src/fusion/src/fusion_manager.cpp#L84)）

`fusion_manager` 把雷达的 3D 点用外参 `T_cam_lidar` + 内参 `K` **投影到图像平面**，
和相机 bbox 中心做距离匹配（阈值 `match_dist_thresh` 像素，默认 60）。匹配结果按如下
策略合成：

| 雷达 | 相机 | 处理 | 出现在地图上？ |
|:---:|:---:|---|:---:|
| ✅ | ✅ | 位置取**雷达**，分类/标签取**相机**，置信度 = 0.6×雷达 + 0.4×相机 | ✅ |
| ✅ | ❌ | 位置取**雷达**，置信度 × 0.6（无视觉确认，降权） | ✅ |
| ❌ | ✅ | **直接丢弃**（没有 3D 坐标，无法画在地图上） | ❌ |

> **关键推论**：如果雷达没连上 / 没探测到，**YOLO 单独识别到的无人机不会出现在前端
> 地图上**。这是当前架构的固有限制，不是 bug。如需突破，需要给单目深度估计兜底或者
> 假设固定飞行高度反推距离。

### 为什么这样设计？

| 方案 | 问题 |
|------|------|
| 只用相机 | 单目无距离 → 无法在地图上标位置、无法估速度、无法判断"是不是在监控区内" |
| 只用雷达 | 区分不了无人机和鸟/气球 → 误报率高 |
| **雷达 + 相机融合**（本系统） | 雷达给位置，相机给类别，互补 |

### 对比：单目相机 + 毫米波雷达（汽车 ADAS 常见方案）

那种方案是"**相机给区域 → 毫米波雷达窄波束测距**"。本项目用的是 **3D 激光雷达
（Livox Avia）**，**直接出 3D 点云**，不需要相机告诉它去哪测距，反过来是它告诉相机
"这个 bbox 在 X 米外、Y 米高"。两者方向相反。

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
