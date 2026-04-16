#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# scripts/build.sh  ─  一键编译脚本
# 用法：bash scripts/build.sh [--clean]
# ═══════════════════════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

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

# 1. 先编译 interface（其他包依赖它）
colcon build \
    --packages-select interface \
    --symlink-install \
    --cmake-args -DCMAKE_BUILD_TYPE=Release

# 2. 编译 utils（纯头文件，编译快）
colcon build \
    --packages-select utils \
    --symlink-install

# 3. 编译其余 C++ 包
colcon build \
    --packages-select radar camera_vision fusion \
    --symlink-install \
    --cmake-args -DCMAKE_BUILD_TYPE=Release \
    --parallel-workers 4

# 4. 编译 Python 包
colcon build \
    --packages-select web_dashboard \
    --symlink-install

source install/setup.bash
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  编译完成！运行方式：                            ║"
echo "║  source install/setup.bash                       ║"
echo "║  ros2 launch launch/full_system_launch.py        ║"
echo "╚══════════════════════════════════════════════════╝"
