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
| `config/site_background.pcd` | Avia 固定后录制当前场地的空场点云，按下文命令生成 |
| `config/out_matrix.yaml` | 用 Kalibr 或五点标定工具完成相机-雷达外参标定 |

### 4. 实物 Avia 通用基线与现场背景

`config/radar_general_params.yaml` 是实物 Avia 的平衡起点，默认面向水平固定
安装、1--50m范围内的小/中型无人机。`main` 不加载任何 rosbag 专用参数。

实测现场没有 PCD 时，**不能使用 Tello rosbag 的背景 PCD 代替**，因为背景地图只
对应生成它时的雷达位置、朝向和静态场景。每次更换场地，或者移动/旋转 Avia 后，
都要在没有无人机、人员尽量离开监控区的情况下重新录制 20--30 秒：

这里的 rosbag 只用于正式测试前的一次短时背景采集。生成 PCD 后就停止录制，正式
检测过程中直接读取该 PCD，**不需要持续录制 rosbag**。如果场地、雷达位置、安装
高度和朝向均未改变，之后的多次实测可以重复使用同一个 PCD。

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

# 录制结束后生成背景 PCD（工具不会覆盖已存在文件）
cd /home/guichen/Documents/drone-radar-fusion
source /opt/ros/humble/setup.bash
python3 scripts/build_background_pcd.py \
  /home/guichen/bags/avia_empty_scene \
  /home/guichen/Documents/drone-radar-fusion/config/site_background.pcd \
  --voxel-size 0.10 --min-frames 10
```

生成完成后使用现场 PCD 启动实测：

```bash
cd /home/guichen/Documents/drone-radar-fusion
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch launch/full_system_launch.py \
  map_pcd_path:=/home/guichen/Documents/drone-radar-fusion/config/site_background.pcd
```

注意：

- 生成背景后不能再移动或旋转雷达，否则必须重新生成。
- 更换场地、改变安装高度，或场景中的大型静态物体明显变化时，也应重新生成。
- 录制背景时不能有无人机，人员也应尽量离开监控区域。
- 通用配置要求背景地图成功加载；地图缺失时 `radar_node` 会主动停止，避免把墙、
  树木和地面识别为无人机。
- 不建议通过关闭 `background_required` 强行无背景运行，这会产生大量静态物体误报，
  不适合作为实测结果。

通用参数中 `z` 是相对 Avia 安装中心的坐标，不是无人机离地高度。
`roi_z_min` 应按现场安装尺寸计算：

```text
roi_z_min = 允许的最低无人机离地高度 - Avia离地安装高度
```

例如 Avia 离地1.5m，希望检测离地至少1.0m的无人机，则
`roi_z_min` 和 `drone_min_height` 都设为 `-0.5`。该参数在
`config/radar_general_params.yaml` 中修改。

实物默认使用平衡档：`cluster_min_size=3`、约0.5秒确认。若远距离无人机
经常只有2个点，可将 `cluster_min_size` 改为 `2`，同时将
`confirm_thresh` 提高到 `8`，以免单点杂波被误确认。

#### 其他项目参数

编辑 `config/params.yaml`：

```yaml
origin_lat: 22.123456      # 监控区域地理纬度（地图光标基准）
origin_lng: 114.123456     # 监控区域地理经度
warn_confidence: 0.6       # 报警置信度阈值
radar_only_mode: false     # 相机与外参可用时启用视觉—雷达融合
```

视觉节点默认使用重叠切片推理，以保留远距离小目标细节：

```yaml
yolo_detector:
  ros__parameters:
    input_size:       1280  # ONNX 的固定输入尺寸，不要改成切片尺寸
    slice_enabled:    true
    slice_size:       960   # 2448x2048 原图约生成 3x3=9 个切片
    slice_overlap:    0.20
    slice_nms_iou:    0.45  # 整图坐标下合并跨切片重复框
    hybrid_full_frame: true # 整图负责近距离大目标，切片负责远距离小目标
```

默认每帧执行 1 次整图推理和约 9 次切片推理。整图分支避免近距离大目标被切片边界
截断，切片分支保留远距离小目标细节；所有检测框还原到原图坐标后统一执行全局 NMS。
若设备性能不足，可将 `slice_enabled` 设为 `false` 临时恢复仅整图推理；切片尺寸越小，
远距离细节越多，但每帧推理次数也越多。

### 5. 编译

```bash
cd drone-radar-fusion
bash scripts/build.sh
```

编译顺序：`interface` + `livox_interfaces` + `livox_sdk_vendor` →
`radar` + `camera_vision` + `fusion` + `livox_ros2_avia` + `hik_camera_ros2_driver`（并行）→
`camera_yolo` + `web_dashboard`。

> **使用 `--clean` 选项完整重编译：**
> ```bash
> bash scripts/build.sh --clean
> ```
> 注意：`--clean` 会删除 `build/` 和 `install/` 目录，重编译后需重新 source：
> ```bash
> source install/setup.bash
> ```

### 6. 启动

`main` 是实测分支，以下命令会启动 Livox Avia 与海康相机硬件驱动。rosbag 回放与
TIERS 数据转换只在 `bag-workflow` 分支维护，不应在本分支使用回放输入代替实物驱动。

```bash
cd /home/guichen/Documents/drone-radar-fusion
source /opt/ros/humble/setup.bash
source install/setup.bash

# 一键启动全系统（默认加载 radar_general_params.yaml）
ros2 launch launch/full_system_launch.py \
  map_pcd_path:=/home/guichen/Documents/drone-radar-fusion/config/site_background.pcd

# 使用其他场地的背景图时，只需替换绝对路径
# ros2 launch launch/full_system_launch.py map_pcd_path:=/absolute/path/site_b.pcd
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
- **RViz2 雷达原始候选框**：添加 `MarkerArray`，Topic 设为 `/radar/cluster_markers`
- **RViz2 融合结果框**：添加另一个 `MarkerArray`，Topic 设为 `/fusion/markers`
- **RViz2 雷达点云**：添加 `PointCloud2`，Topic 设为 `/radar/dynamic_cloud`

雷达框和融合框不是同一个话题：`/radar/cluster_markers` 会显示雷达聚类后立即得到的
候选框；`/fusion/markers` 只有目标通过融合、连续命中和追踪后才会出现。检查雷达算法时
应先看 `/radar/cluster_markers`。RViz 的 `Fixed Frame` 应设为 `livox_frame`，MarkerArray
的 Reliability 应设为 `Reliable`。仓库自带的 `config/live_rviz.rviz` 已经包含这些设置。

相机窗口也有两个：`Image (raw)` 是原始图像，永远不会带框；要查看 YOLO 框，必须在
Displays 中勾选 `Image (YOLO debug)`（Topic 为 `/camera/debug_image`）。为了避免看错，
可以取消勾选 `Image (raw)`，只保留 `Image (YOLO debug)`。

> 无人机硬件未连接时：hik_camera 和 radar 会报 `No camera found` / `Invalid bd:` 错误并持续重试，属正常现象。Web 地图页面仍可正常加载，但不显示目标数据。

### 8. 实测数据录制（可选）

实物跑通后，可以把关键 topic 录成 rosbag 作为现场测试记录。本节只负责录制；离线
回放和公开数据集转换请切换到 `bag-workflow` 分支。

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

#### 录制的话题（由 `scripts/record_bag.sh` 决定）

| 类别 | Topic |
|------|-------|
| 原始数据 | `/livox/lidar` `/hik_camera/image_raw` |
| 雷达输出 | `/radar/detect` `/radar/dynamic_cloud` |
| 相机输出 | `/camera/detect_result` `/camera/debug_image` |
| 融合输出 | `/fusion/final_result` `/fusion/warn` `/fusion/markers` |

---

## Topic 一览

| Topic | 类型 | 发布节点 | 说明 |
|-------|------|----------|------|
| `/livox/lidar` | PointCloud2 | livox_ros2_avia | 原始点云 |
| `/hik_camera/image_raw` | Image | hik_camera_ros2_driver | 原始图像 |
| `/radar/detect` | DroneDetectArray | radar | 雷达候选目标（含高度） |
| `/camera/detect_result` | DroneDetectArray | camera_vision | YOLO 检测结果（BBox） |
| `/camera/debug_image` | Image | camera_vision | YOLO 标注调试图像 |
| `/radar/cluster_markers` | MarkerArray | radar | 雷达聚类候选框（RViz 首选检查项） |
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
