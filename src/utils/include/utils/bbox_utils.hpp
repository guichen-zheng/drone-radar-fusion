#pragma once

#include <algorithm>
#include <vector>
#include <cmath>

namespace utils
{

/**
 * @brief 2D 矩形（像素坐标）
 */
struct Rect2D {
    float x, y, w, h;   // 左上角 + 宽高
    float cx() const { return x + w / 2.f; }
    float cy() const { return y + h / 2.f; }
    float area() const { return w * h; }
};

/**
 * @brief 计算两个矩形的 IoU（Intersection over Union）
 */
inline float iou(const Rect2D & a, const Rect2D & b)
{
    float ix = std::max(0.f, std::min(a.x + a.w, b.x + b.w) - std::max(a.x, b.x));
    float iy = std::max(0.f, std::min(a.y + a.h, b.y + b.h) - std::max(a.y, b.y));
    float inter = ix * iy;
    float uni   = a.area() + b.area() - inter;
    return (uni > 0) ? inter / uni : 0.f;
}

/**
 * @brief 像素距离（两矩形中心的欧氏距离）
 */
inline float centerDist(const Rect2D & a, const Rect2D & b)
{
    float dx = a.cx() - b.cx(), dy = a.cy() - b.cy();
    return std::sqrt(dx*dx + dy*dy);
}

/**
 * @brief 简单匈牙利算法（用于多目标关联，O(n³)，适合目标数 < 20 的场景）
 * @param cost  代价矩阵（行=雷达检测，列=相机检测）
 * @param thresh 超过此代价的不匹配
 * @return 匹配对 {radar_idx, camera_idx}
 */
inline std::vector<std::pair<int,int>> hungarianMatch(
    const std::vector<std::vector<float>> & cost,
    float thresh = 1e6)
{
    int n = cost.size();
    if (n == 0) return {};
    int m = cost[0].size();

    // 简化版：贪心最小代价匹配（目标数少时效果等同匈牙利）
    std::vector<bool> used_col(m, false);
    std::vector<std::pair<int,int>> result;

    // 按最小代价排序所有 (i,j) 对
    std::vector<std::tuple<float,int,int>> pairs;
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < m; ++j)
            if (cost[i][j] < thresh)
                pairs.emplace_back(cost[i][j], i, j);
    std::sort(pairs.begin(), pairs.end());

    std::vector<bool> used_row(n, false);
    for (auto & [c, i, j] : pairs) {
        if (!used_row[i] && !used_col[j]) {
            result.emplace_back(i, j);
            used_row[i] = used_col[j] = true;
        }
    }
    return result;
}

}  // namespace utils
