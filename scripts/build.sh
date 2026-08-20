#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# scripts/build.sh  ─  一键编译脚本
# 用法：bash scripts/build.sh [--clean]
# ═══════════════════════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# ── 检查驱动依赖是否已拉取 ────────────────────────────────────
MISSING=false
for dep in src/hik_camera src/livox_driver; do
    if [ ! -d "$dep/.git" ]; then
        echo "[build.sh] ⚠  缺少驱动：$dep（请先运行 bash scripts/deps.sh）"
        MISSING=true
    fi
done
$MISSING && { echo "[build.sh] 请先执行：bash scripts/deps.sh"; exit 1; }

# 可选：--clean 删除旧的 build/install/log
if [[ "$1" == "--clean" ]]; then
    echo "[build.sh] 清理旧编译产物..."
    rm -rf build install log
fi

# Source ROS2 环境（Humble 默认路径，按实际修改）
source /opt/ros/humble/setup.bash 2>/dev/null || \
source /opt/ros/iron/setup.bash   2>/dev/null || \
{ echo "[ERROR] 未找到 ROS2 环境，请先 source /opt/ros/<distro>/setup.bash"; exit 1; }

echo "[build.sh] 开始编译（按依赖顺序）..."

# 1. 先编译消息与 Livox SDK 依赖（其他包依赖它们）
colcon build \
    --packages-select interface livox_interfaces livox_sdk_vendor \
    --symlink-install \
    --cmake-args -DCMAKE_BUILD_TYPE=Release

source install/setup.bash

# 2. 编译处理节点和实物驱动
colcon build \
    --packages-select \
        radar camera_vision fusion \
        livox_ros2_avia hik_camera_ros2_driver \
    --symlink-install \
    --cmake-args -DCMAKE_BUILD_TYPE=Release \
    --parallel-workers 4

source install/setup.bash

# 3. 编译 Python 包（YOLO ROS 桥接 + Web 仪表盘）
colcon build \
    --packages-select camera_yolo web_dashboard \
    --symlink-install

source install/setup.bash
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  编译完成！运行方式：                            ║"
echo "║  source install/setup.bash                       ║"
echo "║  ros2 launch launch/full_system_launch.py        ║"
echo "╚══════════════════════════════════════════════════╝"
