#include "radar/radar_processor.hpp"
#include <pcl/io/pcd_io.h>
#include <pcl/filters/crop_box.h>
#include <stdexcept>

namespace radar
{

RadarProcessor::RadarProcessor(const rclcpp::NodeOptions & options)
: Node("radar_processor", options)
{
    // ── 声明并读取参数 ─────────────────────────────────────
    this->declare_parameter("map_pcd_path", "config/drone_map.pcd");
    // 当前多参数文件合并时，节点专用 YAML 中的 map_pcd_path 可能遮蔽
    // launch 生成的 /** 同名参数。用独立参数承接显式覆盖；空字符串表示
    // 仍使用 map_pcd_path，以兼容旧参数文件和直接 ros2 run 的用法。
    this->declare_parameter("map_pcd_path_override", "");
    this->declare_parameter("background_required", false);
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
    this->declare_parameter("gicp_max_corr_dist", 1.0);
    // 固定安装的 Livox 与背景地图本来就在同一坐标系，默认不做逐帧 GICP。
    // 雷达或支架可能轻微移动时才开启，以免动态目标影响配准结果。
    this->declare_parameter("background_align_gicp", false);
    // 当前点到静态地图最近点距离超过该阈值时，才视为前景/动态点。
    this->declare_parameter("background_distance_thresh", 0.25);
    // 离群点滤除参数（mean_k<=0 时跳过；点云稀疏时也跳过，避免 KDTree empty）
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
    gicp_max_corr_dist_ = this->get_parameter("gicp_max_corr_dist").as_double();
    background_align_gicp_ = this->get_parameter("background_align_gicp").as_bool();
    background_distance_thresh_ =
        this->get_parameter("background_distance_thresh").as_double();
    outlier_mean_k_     = this->get_parameter("outlier_mean_k").as_int();
    outlier_stddev_mul_ = this->get_parameter("outlier_stddev_mul").as_double();

    // ── 加载地图 ───────────────────────────────────────────
    std::string map_path = this->get_parameter("map_pcd_path").as_string();
    const std::string map_path_override =
        this->get_parameter("map_pcd_path_override").as_string();
    if (!map_path_override.empty()) {
        map_path = map_path_override;
        RCLCPP_INFO(this->get_logger(),
            "[Radar] 使用启动参数覆盖背景地图：%s", map_path.c_str());
    }
    if (!loadMapPCD(map_path)) {
        if (this->get_parameter("background_required").as_bool()) {
            RCLCPP_FATAL(this->get_logger(),
                "[Radar] 实物模式要求背景地图，但加载失败：%s",
                map_path.c_str());
            throw std::runtime_error(
                "required radar background PCD could not be loaded: " + map_path);
        }
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

    // 每 10 帧打印一次各阶段点数（实物调试用）
    static int frame_cnt = 0;
    if (++frame_cnt % 10 == 0) {
        RCLCPP_INFO(this->get_logger(),
            "[Radar] 点数: 输入=%zu voxel=%zu ROI=%zu 前景=%zu outlier=%zu 聚类=%zu 候选=%zu",
            cloud->size(), filtered->size(), roi_cloud->size(),
            dynamic_cloud->size(), clean_cloud->size(),
            clusters.size(), candidates.size());
    }

    // 把候选无人机的点云强度抬高到 250，便于在 RViz 用 intensity 着色时高亮
    pcl::PointCloud<pcl::PointXYZI>::Ptr highlight_cloud(new pcl::PointCloud<pcl::PointXYZI>(*clean_cloud));
    for (const auto & c : candidates) {
        for (int idx : c.indices.indices) {
            if (idx >= 0 && idx < static_cast<int>(highlight_cloud->size())) {
                highlight_cloud->points[idx].intensity = 250.0f;
            }
        }
    }

    // 发布动态点云（候选目标点已被高亮）
    sensor_msgs::msg::PointCloud2 cloud_msg;
    pcl::toROSMsg(*highlight_cloud, cloud_msg);
    cloud_msg.header = msg->header;
    pub_dynamic_cloud_->publish(cloud_msg);

    // 发布无人机包围盒标记
    publishClusterMarkers(candidates, msg->header);

    publishResults(candidates, msg->header);
}

void RadarProcessor::publishClusterMarkers(
    const std::vector<ClusterResult> & candidates,
    const std_msgs::msg::Header & header)
{
    visualization_msgs::msg::MarkerArray ma;

    // 先发 DELETEALL 清掉上一帧的旧 marker
    visualization_msgs::msg::Marker clr;
    clr.header = header;
    clr.ns = "drone_candidates";
    clr.action = visualization_msgs::msg::Marker::DELETEALL;
    ma.markers.push_back(clr);

    for (size_t i = 0; i < candidates.size(); ++i) {
        const auto & c = candidates[i];

        // 半透明青色包围盒：尺寸 = cluster bbox（宽×深×高），叠在聚类点上
        visualization_msgs::msg::Marker box;
        box.header = header;
        box.ns = "drone_candidates";
        box.id = static_cast<int>(i);
        box.type = visualization_msgs::msg::Marker::CUBE;
        box.action = visualization_msgs::msg::Marker::ADD;
        box.pose.position.x = c.centroid.x;
        box.pose.position.y = c.centroid.y;
        box.pose.position.z = c.centroid.z;
        box.pose.orientation.w = 1.0;
        box.scale.x = std::max(c.width,  0.3f);
        box.scale.y = std::max(c.depth,  0.3f);
        box.scale.z = std::max(c.height, 0.3f);
        box.color.r = 0.4f; box.color.g = 0.9f; box.color.b = 1.0f;
        box.color.a = 0.45f;
        box.lifetime = rclcpp::Duration::from_seconds(0.5);
        ma.markers.push_back(box);
    }

    pub_markers_->publish(ma);
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
    if (!map_loaded_ || !map_kdtree_ || cloud->empty()) return cloud;

    // 数据集和固定监控设备中，点云与地图共享 livox_frame，直接差分最稳定。
    // 只有明确知道雷达发生了轻微位移时才启用 GICP 对齐。
    pcl::PointCloud<pcl::PointXYZI>::Ptr aligned_cloud = cloud;
    pcl::PointCloud<pcl::PointXYZI>::Ptr aligned_storage;
    if (background_align_gicp_ && cloud->size() >= 20 && map_cloud_->size() >= 20) {
        pcl::GeneralizedIterativeClosestPoint<pcl::PointXYZI, pcl::PointXYZI> gicp;
        gicp.setMaximumIterations(gicp_max_iter_);
        gicp.setTransformationEpsilon(gicp_fitness_eps_);
        gicp.setMaxCorrespondenceDistance(gicp_max_corr_dist_);
        gicp.setInputSource(cloud);
        gicp.setInputTarget(map_cloud_);

        aligned_storage.reset(new pcl::PointCloud<pcl::PointXYZI>);
        gicp.align(*aligned_storage);
        if (gicp.hasConverged()) {
            aligned_cloud = aligned_storage;
        } else {
            RCLCPP_WARN_THROTTLE(
                this->get_logger(), *this->get_clock(), 5000,
                "[Radar] GICP 未收敛，本帧按原坐标进行背景差分");
        }
    }

    pcl::PointCloud<pcl::PointXYZI>::Ptr foreground(
        new pcl::PointCloud<pcl::PointXYZI>);
    foreground->reserve(aligned_cloud->size());
    const float threshold_sq = static_cast<float>(
        background_distance_thresh_ * background_distance_thresh_);
    std::vector<int> nearest_index(1);
    std::vector<float> nearest_distance_sq(1);

    for (const auto & point : aligned_cloud->points) {
        if (!pcl::isFinite(point)) continue;
        const int found = map_kdtree_->nearestKSearch(
            point, 1, nearest_index, nearest_distance_sq);
        // 地图覆盖不到，或与最近背景点足够远：保留为前景。
        if (found == 0 || nearest_distance_sq[0] > threshold_sq) {
            foreground->push_back(point);
        }
    }
    foreground->width = static_cast<uint32_t>(foreground->size());
    foreground->height = 1;
    foreground->is_dense = true;
    return foreground;
}

pcl::PointCloud<pcl::PointXYZI>::Ptr RadarProcessor::outlierRemoval(
    const pcl::PointCloud<pcl::PointXYZI>::Ptr & cloud)
{
    // outlier_mean_k <= 0 时直接跳过滤除（点云稀疏时用）
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
        res.indices = indices;

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
        if (c.width > drone_max_size_ ||
            c.depth > drone_max_size_ ||
            c.height > drone_max_size_)
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
    if (map_cloud_->empty()) {
        RCLCPP_WARN(this->get_logger(), "[Radar] 背景地图为空：%s", path.c_str());
        return false;
    }
    map_kdtree_.reset(new pcl::KdTreeFLANN<pcl::PointXYZI>);
    map_kdtree_->setInputCloud(map_cloud_);
    map_loaded_ = true;
    RCLCPP_INFO(this->get_logger(),
        "[Radar] 背景地图加载成功：%s（%zu 点），差分阈值=%.3fm，GICP=%s",
        path.c_str(), map_cloud_->size(), background_distance_thresh_,
        background_align_gicp_ ? "on" : "off");
    return true;
}

}  // namespace radar
