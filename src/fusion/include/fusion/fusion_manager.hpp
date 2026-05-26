#pragma once

#include <rclcpp/rclcpp.hpp>
#include <message_filters/subscriber.h>
#include <message_filters/synchronizer.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <visualization_msgs/msg/marker_array.hpp>
#include <std_msgs/msg/string.hpp>
#include <Eigen/Dense>
#include <opencv2/core.hpp>
#include <map>
#include <mutex>

#include "interface/msg/drone_detect_array.hpp"
#include "interface/msg/radar_warn.hpp"
#include "fusion/kalman_filter.hpp"

namespace fusion
{

// 一条完整的追踪轨迹（含卡尔曼滤波器 + 最新融合结果）
struct DroneTrack {
    uint32_t track_id;
    KalmanFilter kf;
    interface::msg::DroneDetect latest;   // 最新融合输出
    int hit_count   = 0;                  // 连续命中帧数（用于确认目标）
    bool confirmed  = false;              // 是否已确认（hit_count >= confirm_thresh）
    bool warned     = false;              // 是否已报警（避免重复报警）
};

class FusionManager : public rclcpp::Node
{
public:
    explicit FusionManager(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());

private:
    // ── 时间同步回调 ───────────────────────────────────────
    // 同时接收雷达检测 + 相机检测，做融合
    void fusionCallback(
        const interface::msg::DroneDetectArray::ConstSharedPtr & radar_msg,
        const interface::msg::DroneDetectArray::ConstSharedPtr & camera_msg);

    // ── 融合核心 ───────────────────────────────────────────
    // 1. 相机-雷达匹配（IOU + 距离代价矩阵，匈牙利算法）
    std::vector<std::pair<int,int>> matchDetections(
        const interface::msg::DroneDetectArray & radar,
        const interface::msg::DroneDetectArray & camera,
        const Eigen::Matrix3d & cam_intrinsic,
        const Eigen::Matrix4d & extrinsic);

    // 2. 将雷达 3D 点投影到相机图像平面（用于与相机 BBox 匹配）
    cv::Point2f projectToImage(
        const Eigen::Vector3d & point_3d,
        const Eigen::Matrix3d & K,
        const Eigen::Matrix4d & T_cam_lidar);

    // 3. 卡尔曼更新（多目标追踪）
    void updateTracks(const std::vector<interface::msg::DroneDetect> & fused_dets,
                      double timestamp);

    // 4. 发布融合结果
    void publishResults();

    // 5. 报警逻辑
    void checkAndWarn(const DroneTrack & track);

    // 6. 发布 RViz / Foxglove 可视化 Marker
    void publishMarkers();

    // ── 外参/内参加载 ──────────────────────────────────────
    bool loadCalibration(const std::string & yaml_path);

    // ── 传感器位姿动态更新（由 Web Dashboard 发来）──────────
    void onSensorPose(const std_msgs::msg::String::SharedPtr msg);

    // ── 报警发布（MQTT / HTTP 由外部桥接节点监听 /warn topic）──
    rclcpp::Publisher<interface::msg::RadarWarn>::SharedPtr pub_warn_;
    rclcpp::Publisher<interface::msg::DroneDetectArray>::SharedPtr pub_final_;
    rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr pub_markers_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_warn_json_;  // 给 web_dashboard

    // ── 时间同步订阅器 ─────────────────────────────────────
    using SyncPolicy = message_filters::sync_policies::ApproximateTime<
        interface::msg::DroneDetectArray,
        interface::msg::DroneDetectArray>;
    message_filters::Subscriber<interface::msg::DroneDetectArray> sub_radar_;
    message_filters::Subscriber<interface::msg::DroneDetectArray> sub_camera_;
    std::shared_ptr<message_filters::Synchronizer<SyncPolicy>> sync_;

    // ── 传感器位姿订阅器 ──────────────────────────────────
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_sensor_pose_;

    // ── 追踪轨迹表（track_id → DroneTrack）────────────────
    std::map<uint32_t, DroneTrack> tracks_;
    uint32_t next_track_id_ = 0;

    // ── 标定参数 ───────────────────────────────────────────
    Eigen::Matrix3d cam_intrinsic_;    // 相机内参 K（3×3）
    Eigen::Matrix4d T_cam_lidar_;      // 雷达→相机外参（4×4 齐次变换）
    bool calib_loaded_ = false;

    // ── 坐标转换互斥锁（保护 CoordTransform 静态状态）──────
    std::mutex pose_mutex_;

    // ── 参数 ──────────────────────────────────────────────
    int confirm_thresh_    = 3;    // 连续命中多少帧才确认目标
    int max_miss_frames_   = 5;    // 连续丢失多少帧删除轨迹
    double match_iou_thresh_ = 0.3;
    double match_dist_thresh_ = 50.0;  // 像素距离阈值
    double track_assoc_dist_  = 5.0;   // 米：track 关联阈值（>此距离视为新目标）
    double warn_confidence_   = 0.7;   // 触发报警的最低置信度
    std::string warn_level_   = "MEDIUM";
};

}  // namespace fusion
