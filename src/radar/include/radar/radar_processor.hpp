#pragma once

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/filters/statistical_outlier_removal.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <pcl/segmentation/extract_clusters.h>
#include <pcl/registration/gicp.h>
#include <pcl_conversions/pcl_conversions.h>
#include <visualization_msgs/msg/marker_array.hpp>
#include "interface/msg/drone_detect_array.hpp"

namespace radar
{

struct ClusterResult {
    pcl::PointXYZI centroid;    // 聚类中心
    float width;                 // 包围盒宽度
    float height;                // 包围盒高度（z 方向，即高度信息）
    float depth;                 // 包围盒深度
    int point_count;             // 聚类点数
    bool is_dynamic;             // 是否为动态目标
    pcl::PointIndices indices;  // 该聚类对应的点索引（指向 clean_cloud）
};

class RadarProcessor : public rclcpp::Node
{
public:
    explicit RadarProcessor(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());

private:
    // ── 回调 ──────────────────────────────────────────────
    void pointCloudCallback(const sensor_msgs::msg::PointCloud2::SharedPtr msg);

    // ── 处理流水线 ─────────────────────────────────────────
    // 1. 体素滤波（降采样）
    pcl::PointCloud<pcl::PointXYZI>::Ptr voxelFilter(
        const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud);

    // 2. ROI 裁剪（仅保留监控区域内点云）
    pcl::PointCloud<pcl::PointXYZI>::Ptr roiFilter(
        const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud);

    // 3. GICP 地图配准（去除静态背景，提取动态点云）
    pcl::PointCloud<pcl::PointXYZI>::Ptr gicpMapRegistration(
        const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud);

    // 4. 统计离群点去除
    pcl::PointCloud<pcl::PointXYZI>::Ptr outlierRemoval(
        const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud);

    // 5. 欧几里得聚类
    std::vector<ClusterResult> euclideanClustering(
        const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud);

    // 6. 无人机候选筛选（大小、高度范围过滤）
    std::vector<ClusterResult> filterDroneCandidates(
        const std::vector<ClusterResult> & clusters);

    // 7. 发布结果
    void publishResults(const std::vector<ClusterResult> & candidates,
                        const std_msgs::msg::Header & header);

    // 8. 发布无人机候选包围盒（RViz 可视化）
    void publishClusterMarkers(const std::vector<ClusterResult> & candidates,
                               const std_msgs::msg::Header & header);

    // ── 地图加载 ───────────────────────────────────────────
    bool loadMapPCD(const std::string & pcd_path);

    // ── ROS2 发布/订阅 ─────────────────────────────────────
    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr sub_cloud_;
    rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pub_dynamic_cloud_;
    rclcpp::Publisher<interface::msg::DroneDetectArray>::SharedPtr pub_radar_detect_;
    rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr pub_markers_;

    // ── 地图点云 ───────────────────────────────────────────
    pcl::PointCloud<pcl::PointXYZI>::Ptr map_cloud_;
    pcl::KdTreeFLANN<pcl::PointXYZI>::Ptr map_kdtree_;
    bool map_loaded_ = false;

    // ── 参数 ──────────────────────────────────────────────
    // ROI 范围（米）
    double roi_x_min_, roi_x_max_;
    double roi_y_min_, roi_y_max_;
    double roi_z_min_, roi_z_max_;
    // 体素滤波分辨率
    double voxel_size_;
    // 聚类参数
    double cluster_tolerance_;
    int cluster_min_size_;
    int cluster_max_size_;
    // 无人机尺寸过滤（米）
    double drone_min_height_;    // 无人机最低飞行高度
    double drone_max_height_;    // 无人机最高飞行高度
    double drone_max_size_;      // 聚类包围盒最大尺寸
    // GICP 迭代参数
    int gicp_max_iter_;
    double gicp_fitness_eps_;
    double gicp_max_corr_dist_;
    bool background_align_gicp_;
    double background_distance_thresh_;
    // 离群点滤除参数
    int outlier_mean_k_;
    double outlier_stddev_mul_;
};

}  // namespace radar
