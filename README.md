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
安装、1--50m范围内的小/中型无人机。它不使用 TIERS rosbag 的专用参数。

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

以下命令用于**实物相机和雷达已经连接**的情况；回放已经录制的 rosbag 请使用
后面的「rosbag 录制与回放」命令，不要启动 `full_system_launch.py`，否则硬件驱动
会与 bag 中的 `/livox/lidar`、`/hik_camera/image_raw` 重复发布。

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

当前 `my_test_3drones` 同时录有原始数据和旧的处理结果。若直接回放全部 topic，bag
会发布旧的 `/radar/detect`、`/radar/dynamic_cloud`、`/fusion/markers`，新启动的节点
也会发布同名 topic，造成重复发布。要用当前代码重新处理并画雷达框，推荐只回放
`/livox/lidar` 和 `/hik_camera/image_raw`：

```bash
# 终端 1：启动处理管线和 RViz，不启动硬件驱动、不自动播放 bag
cd /home/guichen/Documents/drone-radar-fusion
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch launch/playback_launch.py

# 终端 2：只回放原始输入，并发布仿真时钟
source /opt/ros/humble/setup.bash
source /home/guichen/Documents/drone-radar-fusion/install/setup.bash
ros2 bag play /home/guichen/bags/my_test_3drones \
  --topics /livox/lidar /hik_camera/image_raw \
  --rate 0.5 --clock 100 --loop
```

先用 `--rate 0.5` 检查画框是否正常。视觉切片推理速度足够后，可以改回
`--rate 1.0`。请先启动终端 1，看到 radar、YOLO、fusion 和 RViz 均已启动后，再
执行终端 2。不要使用 `scripts/play_bag.sh` 做重新计算：该脚本会回放所有已录话题，
并且当前没有传入 `--clock`。

如果只是想快速查看 bag 当时已经录好的处理结果、不需要用当前代码重新计算，可以使用
自动播放方式：

```bash
cd /home/guichen/Documents/drone-radar-fusion
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch launch/playback_launch.py \
  bag_path:=/home/guichen/bags/my_test_3drones \
  rate:=0.5
```

> 自动方式会回放 bag 内已有处理结果，同时也启动处理节点，因此只适合快速查看，
> 不适合判断修改后的雷达算法是否生效。重新计算请始终使用上面的“双终端、只回放
> 原始输入”方式，并且不要省略 `--clock 100`。播放终端中可用 SPACE 暂停/继续。

回放时浏览器 `http://localhost:5000` 和 RViz 同样可用，**看到的可视化效果与实物
运行时完全一致**。

#### TIERS TelloOut02 公开数据集

TIERS 数据是 ROS1 bag，不能直接执行 `ros2 bag play`。仓库提供了
`scripts/convert_tiers_ros1_bag.py`，它不依赖 ROS1/Noetic，会流式完成以下转换：

| ROS1 原话题 | ROS2 输出话题 |
|---|---|
| `/avia/livox/lidar`（Livox `CustomMsg`） | `/livox/lidar`（`PointCloud2`） |
| `/camera/color/image_raw` | `/hik_camera/image_raw` |
| `/camera/color/camera_info` | `/hik_camera/camera_info` |
| `/vrpn_client_node/tello/pose` | `/tiers/tello/pose` |

原始 `.bag` 不会被修改，且转换工具不会覆盖已经存在的输出目录。完整转换约产生 5 GB
数据，建议仍写到移动硬盘：

```bash
cd /home/guichen/Documents/drone-radar-fusion
source /opt/ros/humble/setup.bash

python3 scripts/convert_tiers_ros1_bag.py \
  /media/guichen/T7/ros_bag/TelloOut02.bag \
  /media/guichen/T7/ros_bag/TelloOut02_ros2

ros2 bag info /media/guichen/T7/ros_bag/TelloOut02_ros2

# 从重复观测到的静态体素生成背景地图（原bag不会被修改）
python3 scripts/build_background_pcd.py \
  /media/guichen/T7/ros_bag/TelloOut02_ros2 \
  /media/guichen/T7/ros_bag/TelloOut02_background_balanced.pcd \
  --voxel-size 0.10 --min-frames 10
```

转换完成后重新编译并启动。TIERS 使用它自己的相机内参与 Camera–Avia 外参，不能沿用
实物设备的 `config/out_matrix.yaml`：

```bash
cd /home/guichen/Documents/drone-radar-fusion
source /opt/ros/humble/setup.bash
bash scripts/build.sh
source install/setup.bash

ros2 launch launch/playback_launch.py \
  bag_path:=/media/guichen/T7/ros_bag/TelloOut02_ros2 \
  rate:=0.2 \
  calib_yaml:=/home/guichen/Documents/drone-radar-fusion/config/tiers_tello_out_calib.yaml \
  radar_params:=/home/guichen/Documents/drone-radar-fusion/config/tiers_radar_params.yaml \
  radar_only_mode:=true
```

若要用**实物通用平衡参数**回放同一个 bag 做对比，使用下面命令。这里只将
`map_pcd_path` 替换为该录制场地的背景图，聚类、ROI和跟踪都来自
`radar_general_params.yaml`：

```bash
cd /home/guichen/Documents/drone-radar-fusion
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch launch/playback_launch.py \
  bag_path:=/media/guichen/T7/ros_bag/TelloOut02_ros2 \
  rate:=0.2 \
  calib_yaml:=/home/guichen/Documents/drone-radar-fusion/config/tiers_tello_out_calib.yaml \
  radar_params:=/home/guichen/Documents/drone-radar-fusion/config/radar_general_params.yaml \
  map_pcd_path:=/media/guichen/T7/ros_bag/TelloOut02_background_balanced.pcd \
  radar_only_mode:=true
```

正常启动时应看到“使用启动参数覆盖背景地图”和“背景地图加载成功”两行日志；
如果出现 `config/site_background.pcd` 加载失败，说明仍在运行修改前的旧进程，先
`Ctrl+C` 结束它，重新 `source install/setup.bash` 后再启动。

`radar_only_mode:=true` 会跳过 YOLO 切片推理，让这次回放只测试 Avia 雷达链路。
TIERS 转换后的点云约100Hz，实物驱动为10Hz，因此该回放适合看漏检/误报趋势，
不能完全替代实地结果。

雷达独立模式可从 `rate:=0.5` 或 `1.0` 开始；若将 `radar_only_mode`
改为 `false` 启用1920×1080图像切片推理，建议先使用 `rate:=0.2`。
`Calibration.bag` 只有各传感器点云，没有 RGB 图像，不用于检测回放。

TIERS 是以多激光雷达跟踪为主的数据集。它提供原始 RGB 图，但没有二维检测框标注，
也不保证无人机始终处于 RealSense D435 的 69°×42°视场内。对 TelloOut02 抽帧实测时，
当前 YOLO 模型即使把阈值降到 `0.001`，最高响应也只有约 `0.023`，且主要落在建筑、
自行车和支架等静态物体上。因此该 bag 适合验证 Avia 点云和 ROS2 接入，不适合单独
判断当前 YOLO 的识别精度。先保持 `radar_only_mode:=true`；只有确认
`/camera/detect_result` 已经产生正确视觉框后，才改为 `false` 测试视觉—雷达融合。

`/tiers/tello/pose` 是 MOCAP 的 `world` 坐标。bag 中没有提供固定的
`world→livox_frame` 变换，不能直接把位姿向量的模当作目标到传感器的距离。官方论文
只说明室外轨迹整体可延伸到约 30 m，并未给出 TelloOut02 每帧相对传感器的距离。

数据集没有直接提供该室外场景的空背景 PCD。本项目通过整段bag的“不同帧重复观测
次数”生成静态体素地图，再执行最近邻背景差分。对TelloOut02实测，修正
以 Avia 安装中心为原点的 z 范围后，原始雷达候选从 bag 第4.015秒开始，融合确认框
从第4.837秒持续到第22.5秒。完整轨迹 x 约11.86--22.24m、z 约-0.37--1.26m；
约46--48m处的远墙和 z≈-1m的地面杂点仍被 TIERS 专用 ROI 排除。

> 这里的 `z` 是雷达坐标系中相对 Avia 安装中心的高度，不能直接当作相对
> 地面的无人机高度。例如 `z=-0.3m` 只表示目标低于雷达安装中心0.3m。

无人机真值保存在 `/tiers/tello/pose`，但后续定量误差评估前仍需补齐
`world→livox_frame` 坐标变换。

#### 回放时检查雷达画框链路

另开一个已经 source 环境的终端，按顺序检查：

```bash
# 1. bag 是否在发布时钟和原始雷达点云
ros2 topic hz /clock
ros2 topic hz /livox/lidar

# 2. radar_node 是否在持续发布处理后点云和雷达框消息
ros2 topic hz /radar/dynamic_cloud
ros2 topic hz /radar/cluster_markers

# 3. 当前帧是否真的产生了无人机候选
ros2 topic echo /radar/detect --once
```

- `/clock` 没有频率：播放命令漏了 `--clock 100`；停止播放并按推荐命令重启。
- `/livox/lidar` 没有频率：bag 没有开始播放、路径错误或 `--topics` 写错。
- `/livox/lidar` 有频率而 `/radar/cluster_markers` 没有：确认 `radar_processor` 节点
  正在运行，并查看启动终端是否报错。若看到 `exit code 127` 或
  `undefined symbol: libusb_set_option`，说明运行的是修复前的回放 launch；结束全部
  回放进程后，重新 source 并启动当前 `launch/playback_launch.py`。
- `/radar/cluster_markers` 有频率但 `/radar/detect` 的 `drones: []`：可视化没有故障，
  而是当前参数筛选后的候选数为 0。观察 radar 日志中的
  `输入/ROI/outlier/聚类/候选` 数量，再调整 `config/params.yaml`。
- `/radar/detect` 中有目标但 RViz 没框：把 Fixed Frame 设为 `livox_frame`，确认添加的
  是 `/radar/cluster_markers`，并将 Reliability 设为 `Reliable`。

#### 录制了哪些 topic（由 `scripts/record_bag.sh` 决定）

| 类别 | Topic |
|------|-------|
| 原始数据 | `/livox/lidar` `/hik_camera/image_raw` |
| 雷达输出 | `/radar/detect` `/radar/dynamic_cloud`（bag 内有旧结果；推荐回放命令会排除并重新计算） |
| 相机输出 | `/camera/detect_result` `/camera/debug_image` |
| 融合输出 | `/fusion/final_result` `/fusion/warn` `/fusion/markers` |

使用上面的“只回放原始输入”命令时，下游节点会**重新计算**，不会播放 bag 里的旧
处理结果，所以可以修改 `config/params.yaml` 后回放比较效果。

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
