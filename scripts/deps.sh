#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# scripts/deps.sh  —  拉取外部驱动依赖
#
# 用法：
#   bash scripts/deps.sh          # 首次拉取
#   bash scripts/deps.sh --update # 已存在时强制 git pull
#
# 拉取后目录结构：
#   src/hik_camera/    ← 海康相机 ROS2 驱动
#   src/livox_driver/  ← Livox Avia ROS2 驱动
# ═══════════════════════════════════════════════════════════════════════════════
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$ROOT_DIR/src"
UPDATE=false
[[ "$1" == "--update" ]] && UPDATE=true

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[deps]${NC} $*"; }
warn()  { echo -e "${YELLOW}[deps]${NC} $*"; }
error() { echo -e "${RED}[deps]${NC} $*"; exit 1; }

command -v git &>/dev/null || error "未找到 git，请先安装：sudo apt install git"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           drone-radar-fusion  外部依赖拉取脚本               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── clone_or_update <目标目录> <仓库URL> <分支> ────────────────────────────────
clone_or_update() {
    local target="$1"
    local url="$2"
    local branch="$3"
    local name
    name="$(basename "$target")"

    echo "──────────────────────────────────────────────────────────────"
    info "处理：$name"
    info "仓库：$url"
    info "目标：$target"

    if [ -d "$target/.git" ]; then
        if $UPDATE; then
            info "已存在，执行 git pull（--update 模式）..."
            git -C "$target" pull origin "$branch" \
                || warn "git pull 失败，跳过（保留现有版本）"
        else
            warn "已存在，跳过（用 --update 可拉取最新）"
        fi
    else
        if [ -d "$target" ] && [ -n "$(ls -A "$target")" ]; then
            info "检测到占位目录，初始化 git 并拉取..."
            cd "$target"
            git init -q
            git remote add origin "$url"
            git fetch --depth=1 origin "$branch" \
                || error "fetch 失败，请检查网络和仓库地址：$url"
            git checkout -q FETCH_HEAD
            git branch -M "$branch" 2>/dev/null || true
            cd "$ROOT_DIR"
        else
            git clone --depth=1 -b "$branch" "$url" "$target" \
                || error "clone 失败，请检查网络和仓库地址：$url"
        fi
        info "✓ $name 拉取完成"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# 依赖列表（在此处增减）
# ═══════════════════════════════════════════════════════════════════════════════

clone_or_update \
    "$SRC_DIR/hik_camera" \
    "https://github.com/SMBU-PolarBear-Robotics-Team/hik_camera_ros2_driver.git" \
    "main"

clone_or_update \
    "$SRC_DIR/livox_driver" \
    "https://github.com/ASIG-X/livox_ros2_avia.git" \
    "main"

# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "══════════════════════════════════════════════════════════════"
info "所有依赖处理完毕，验证目录："
echo ""

for dep in hik_camera livox_driver; do
    target="$SRC_DIR/$dep"
    if [ -d "$target/.git" ]; then
        commit=$(git -C "$target" log --oneline -1 2>/dev/null || echo "未知")
        echo -e "  ${GREEN}✓${NC}  $dep  →  $commit"
    else
        echo -e "  ${RED}✗${NC}  $dep  →  未找到，请检查网络后重试"
    fi
done

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "下一步：运行编译脚本"
echo "  bash scripts/build.sh"
echo "══════════════════════════════════════════════════════════════"
echo ""
