#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# scripts/play_bag.sh  ─  回放 rosbag（用于离线调试）
# 用法：bash scripts/play_bag.sh <bag_path> [--rate 0.5]
# ═══════════════════════════════════════════════════════════════════════════════

BAG_PATH="$1"
RATE="${2:---rate}" 
RATE_VAL="${3:-1.0}"

if [[ -z "$BAG_PATH" ]]; then
    echo "用法：bash play_bag.sh <bag_dir> [--rate 0.5]"
    exit 1
fi

source /opt/ros/humble/setup.bash
source "$(dirname "$0")/../install/setup.bash" 2>/dev/null || true

echo "[play_bag] 回放：$BAG_PATH  速率：$RATE_VAL"
ros2 bag play "$BAG_PATH" --rate "$RATE_VAL" --loop
