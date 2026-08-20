#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# scripts/record_bag.sh  ─  录制关键 Topic 到 rosbag（用于离线调试/回放）
# 用法：
#   bash scripts/record_bag.sh [bag_name]
#     默认录到 ~/bags/<bag_name>/
#   BAG_ROOT=/media/guichen/MyDisk/bags bash scripts/record_bag.sh [bag_name]
#     用 BAG_ROOT 环境变量指定其他根目录（如移动硬盘）
# ═══════════════════════════════════════════════════════════════════════════════

BAG_NAME="${1:-drone_fusion_$(date +%Y%m%d_%H%M%S)}"
# 录制根目录：默认 ~/bags，可用 BAG_ROOT 环境变量覆盖（如指向移动硬盘）
BAG_ROOT="${BAG_ROOT:-$HOME/bags}"
BAG_DIR="$BAG_ROOT/$BAG_NAME"

# 自动创建根目录（移动硬盘首次使用时方便）
mkdir -p "$BAG_ROOT" 2>/dev/null || {
    echo "[record_bag] ❌ 无法创建 $BAG_ROOT，检查权限或移动硬盘是否挂载"
    exit 1
}

source /opt/ros/humble/setup.bash
source "$(dirname "$0")/../install/setup.bash" 2>/dev/null || true

echo "[record_bag] 开始录制 → $BAG_DIR"
echo "[record_bag] Ctrl+C 停止录制"

ros2 bag record \
    /livox/lidar \
    /hik_camera/image_raw \
    /radar/detect \
    /radar/dynamic_cloud \
    /camera/detect_result \
    /camera/debug_image \
    /fusion/final_result \
    /fusion/warn \
    /fusion/markers \
    --output "$BAG_DIR" \
    --compression-mode file \
    --compression-format zstd
