#include "radar/radar_processor.hpp"
#include <pcl/io/pcd_io.h>
#include <pcl/filters/crop_box.h>

namespace radar
{

RadarProcessor::RadarProcessor(const rclcpp::NodeOptions & options)
: Node("radar_processor", options)
{
    // ── 声明并读取参数 ─────────────────────────────────────
    this->declare_parameter("map_pcd_path", "config/drone_map.pcd");
    this->declare_parameter("voxel_size", 0.1);
    this->declare_parameter("roi_x_min", -100.0);
    this->declare_parameter("roi_x_max",  100.0);
    this->declare_parameter("roi_y_min", -100.0);
    this->declare_parameter("roi_y_max",  100.0);
    this->declare_parameter("roi_z_min",   0.5);    // 地面以上 0.5m 开始
    this->declare_parameter("roi_z_max", 200.0);    // 最高 200m
    this->declare_parameter("cluster_tolerance", 2.0);
    this->declare_parameter("cluster_min_size", 5);
    this->declare_parameter("cluster_max_size", 500);
    this->declare_parameter("drone_min_height", 5.0);
    this->declare_parameter("drone_max_height", 200.0);
    this->declare_parameter("drone_max_size", 10.0);
    this->declare_parameter("gicp_max_iter", 50);
    this->declare_parameter("gicp_fitness_eps", 0.01);
    // 离群点滤除参数（仿真稀疏点云需把 mean_k 调小，否则会把无人机点全部误删）
    this->declare_parameter("outlier_mean_k", 30);
    this->declare_parameter("outlier_stddev_mul", 1.0);

    roi_x_min_        = this->get_parameter("roi_x_min").as_double();
    roi_x_max_        = this->get_parameter("roi_x_max").as_double();
    roi_y_min_        = this->get_parameter("roi_y_min").as_double();
    roi_y_max_        = this->get_parameter("roi_y_max").as_double();
    roi_z_min_        = this->get_parameter("roi_z_min").as_double();
    roi_z_max_        = this->get_parameter("roi_z_max").as_double();
    voxel_size_       = this->get_parameter("voxel_size").as_double();
    cluster_tolerance_ = this->get_parameter("cluster_tolerance").as_double();
    cluster_min_size_ = this->get_parameter("cluster_min_size").as_int();
    cluster_max_size_ = this->get_parameter("cluster_max_size").as_int();
    drone_min_height_ = this->get_parameter("drone_min_height").as_double();
    drone_max_height_ = this->get_parameter("drone_max_height").as_double();
    drone_max_size_   = this->get_parameter("drone_max_size").as_double();
    gicp_max_iter_    = this->get_parameter("gicp_max_iter").as_int();
    gicp_fitness_eps_ = this->get_parameter("gicp_fitness_eps").as_double();
    outlier_mean_k_     = this->get_parameter("outlier_mean_k").as_int();
    outlier_stddev_mul_ = this->get_parameter("outlier_stddev_mul").as_double();

    // ── 加载地图 ───────────────────────────────────────────
    std::string map_path = this->get_parameter("map_pcd_path").as_string();
    if (!loadMapPCD(map_path)) {
        RCLCPP_WARN(this->get_logger(),
            "[Radar] 地图文件未加载：%s，将跳过 GICP 背景去除", map_path.c_str());
    }

    // ── 订阅与发布 ─────────────────────────────────────────
    sub_cloud_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
        "/livox/lidar", 10,
        std::bind(&RadarProcessor::pointCloudCallback, this, std::placeholders::_1));

    pub_dynamic_cloud_ = this->create_publisher<sensor_msgs::msg::PointCloud2>(
        "/radar/dynamic_cloud", 10);

    pub_radar_detect_ = this->create_publisher<interface::msg::DroneDetectArray>(
        "/radar/detect", 10);

    pub_markers_ = this->create_publisher<visualization_msgs::msg::MarkerArray>(
        "/radar/cluster_markers", 10);

    RCLCPP_INFO(this->get_logger(), "[Radar] 雷达处理节点已启动");
}

void RadarProcessor::pointCloudCallback(
    const sensor_msgs::msg::PointCloud2::SharedPtr msg)
{
    // PCL 格式转换
    pcl::PointCloud<pcl::PointXYZI>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZI>);
    pcl::fromROSMsg(*msg, *cloud);

    if (cloud->empty()) return;

    // 处理流水线
    auto filtered     = voxelFilter(cloud);
    auto roi_cloud    = roiFilter(filtered);
    auto dynamic_cloud = map_loaded_ ? gicpMapRegistration(roi_cloud) : roi_cloud;
    auto clean_cloud  = outlierRemoval(dynamic_cloud);
    auto clusters     = euclideanClustering(clean_cloud);
    auto candidates   = filterDroneCandidates(clusters);

    // 每秒打印一次各阶段点数（仿真调试用）
    static int frame_cnt = 0;
    if (++frame_cnt % 10 == 0) {
        RCLCPP_INFO(this->get_logger(),
            "[Radar] 点数: 输入=%zu voxel=%zu ROI=%zu outlier=%zu 聚类=%zu 候选=%zu",
            cloud->size(), filtered->size(), roi_cloud->size(),
            clean_cloud->size(), clusters.size(), candidates.size());
    }

    publishResults(candidates, msg->header);
}

pcl::PointCloud<pcl::PointXYZI>::Ptr RadarProcessor::voxelFilter(
    const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud)
{
    pcl::VoxelGrid<pcl::PointXYZI> vg;
    pcl::PointCloud<pcl::PointXYZI>::Ptr output(new pcl::PointCloud<pcl::PointXYZI>);
    vg.setInputCloud(cloud);
    vg.setLeafSize(voxel_size_, voxel_size_, voxel_size_);
    vg.filter(*output);
    return output;
}

pcl::PointCloud<pcl::PointXYZI>::Ptr RadarProcessor::roiFilter(
    const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud)
{
    pcl::CropBox<pcl::PointXYZI> crop;
    pcl::PointCloud<pcl::PointXYZI>::Ptr output(new pcl::PointCloud<pcl::PointXYZI>);
    crop.setInputCloud(cloud);
    crop.setMin(Eigen::Vector4f(roi_x_min_, roi_y_min_, roi_z_min_, 1.0));
    crop.setMax(Eigen::Vector4f(roi_x_max_, roi_y_max_, roi_z_max_, 1.0));
    crop.filter(*output);
    return output;
}

pcl::PointCloud<pcl::PointXYZI>::Ptr RadarProcessor::gicpMapRegistration(
    const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud)
{
    // GICP 将当前帧与预建地图对齐，通过差值提取动态点（背景去除）
    pcl::GeneralizedIterativeClosestPoint<pcl::PointXYZI, pcl::PointXYZI> gicp;
    gicp.setMaximumIterations(gicp_max_iter_);
    gicp.setTransformationEpsilon(gicp_fitness_eps_);
    gicp.setInputSource(cloud);
    gicp.setInputTarget(map_cloud_);

    pcl::PointCloud<pcl::PointXYZI> aligned;
    gicp.align(aligned);

    // TODO: 在对齐后的点云与地图之间做差集，提取动态点
    // 当前直接返回原始点云（完整实现参考原库 lidar/ 中的差分逻辑）
    return cloud;
}

pcl::PointCloud<pcl::PointXYZI>::Ptr RadarProcessor::outlierRemoval(
    const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud)
{
    // outlier_mean_k <= 0 时直接跳过滤除（仿真稀疏点云用）
    if (outlier_mean_k_ <= 0) return cloud;
    // 输入点数过少（< mean_k+2）时也跳过，否则 SOR 会触发 KDTree empty 错误
    if (static_cast<int>(cloud->size()) < outlier_mean_k_ + 2) return cloud;
    pcl::StatisticalOutlierRemoval<pcl::PointXYZI> sor;
    pcl::PointCloud<pcl::PointXYZI>::Ptr output(new pcl::PointCloud<pcl::PointXYZI>);
    sor.setInputCloud(cloud);
    sor.setMeanK(outlier_mean_k_);
    sor.setStddevMulThresh(outlier_stddev_mul_);
    sor.filter(*output);
    return output;
}

std::vector<ClusterResult> RadarProcessor::euclideanClustering(
    const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud)
{
    std::vector<ClusterResult> results;
    if (cloud->empty()) return results;

    pcl::search::KdTree<pcl::PointXYZI>::Ptr tree(
        new pcl::search::KdTree<pcl::PointXYZI>);
    tree->setInputCloud(cloud);

    std::vector<pcl::PointIndices> cluster_indices;
    pcl::EuclideanClusterExtraction<pcl::PointXYZI> ec;
    ec.setClusterTolerance(cluster_tolerance_);
    ec.setMinClusterSize(cluster_min_size_);
    ec.setMaxClusterSize(cluster_max_size_);
    ec.setSearchMethod(tree);
    ec.setInputCloud(cloud);
    ec.extract(cluster_indices);

    for (const auto & indices : cluster_indices) {
        ClusterResult res;
        float min_x = 1e6, min_y = 1e6, min_z = 1e6;
        float max_x = -1e6, max_y = -1e6, max_z = -1e6;
        float sum_x = 0, sum_y = 0, sum_z = 0;
        res.point_count = indices.indices.size();

        for (int idx : indices.indices) {
            const auto & pt = cloud->points[idx];
            sum_x += pt.x; sum_y += pt.y; sum_z += pt.z;
            min_x = std::min(min_x, pt.x); max_x = std::max(max_x, pt.x);
            min_y = std::min(min_y, pt.y); max_y = std::max(max_y, pt.y);
            min_z = std::min(min_z, pt.z); max_z = std::max(max_z, pt.z);
        }
        res.centroid.x = sum_x / res.point_count;
        res.centroid.y = sum_y / res.point_count;
        res.centroid.z = sum_z / res.point_count;   // ← 高度来自此处
        res.width  = max_x - min_x;
        res.height = max_z - min_z;
        res.depth  = max_y - min_y;
        results.push_back(res);
    }
    return results;
}

std::vector<ClusterResult> RadarProcessor::filterDroneCandidates(
    const std::vector<ClusterResult> & clusters)
{
    std::vector<ClusterResult> candidates;
    for (const auto & c : clusters) {
        // 高度范围过滤
        if (c.centroid.z < drone_min_height_ || c.centroid.z > drone_max_height_)
            continue;
        // 尺寸过滤（无人机体积较小）
        if (c.width > drone_max_size_ || c.depth > drone_max_size_)
            continue;
        candidates.push_back(c);
    }
    return candidates;
}

void RadarProcessor::publishResults(
    const std::vector<ClusterResult> & candidates,
    const std_msgs::msg::Header & header)
{
    interface::msg::DroneDetectArray arr;
    arr.header = header;

    for (size_t i = 0; i < candidates.size(); ++i) {
        const auto & c = candidates[i];
        interface::msg::DroneDetect det;
        det.drone_id   = static_cast<uint32_t>(i);
        det.x          = c.centroid.x;
        det.y          = c.centroid.y;
        det.z          = c.centroid.z;    // 高度
        det.confidence = 0.6;             // 雷达初始置信度，融合后会更新
        det.is_tracked = false;
        arr.drones.push_back(det);
    }
    pub_radar_detect_->publish(arr);
}

bool RadarProcessor::loadMapPCD(const std::string & path)
{
    map_cloud_.reset(new pcl::PointCloud<pcl::PointXYZI>);
    if (pcl::io::loadPCDFile<pcl::PointXYZI>(path, *map_cloud_) == -1) {
        return false;
    }
    map_loaded_ = true;
    RCLCPP_INFO(this->get_logger(),
        "[Radar] 地图加载成功：%s（%zu 点）", path.c_str(), map_cloud_->size());
    return true;
}

}  // namespace radar
