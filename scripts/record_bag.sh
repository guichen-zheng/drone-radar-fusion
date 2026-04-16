#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# scripts/record_bag.sh  ─  录制关键 Topic 到 rosbag（用于离线调试/回放）
# 用法：bash scripts/record_bag.sh [bag_name]
# ═══════════════════════════════════════════════════════════════════════════════

BAG_NAME="${1:-drone_fusion_$(date +%Y%m%d_%H%M%S)}"
BAG_DIR="$HOME/bags/$BAG_NAME"

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
