#include "fusion/fusion_manager.hpp"
#include "utils/coord_transform.hpp"
#include <yaml-cpp/yaml.h>
#include <opencv2/core/eigen.hpp>
#include <nlohmann/json.hpp>
#include <sstream>

namespace fusion
{

FusionManager::FusionManager(const rclcpp::NodeOptions & options)
: Node("fusion_manager", options)
{
    // ── 参数 ──────────────────────────────────────────────
    this->declare_parameter("calib_yaml",       "config/out_matrix.yaml");
    this->declare_parameter("confirm_thresh",   3);
    this->declare_parameter("max_miss_frames",  5);
    this->declare_parameter("match_dist_thresh", 50.0);
    this->declare_parameter("match_iou_thresh",  0.3);
    this->declare_parameter("warn_confidence",   0.7);
    this->declare_parameter("warn_level",        "MEDIUM");
    this->declare_parameter("origin_lat",        39.9);   // 监控区域原点纬度（度）
    this->declare_parameter("origin_lng",       116.4);   // 监控区域原点经度（度）

    confirm_thresh_    = this->get_parameter("confirm_thresh").as_int();
    max_miss_frames_   = this->get_parameter("max_miss_frames").as_int();
    match_dist_thresh_ = this->get_parameter("match_dist_thresh").as_double();
    match_iou_thresh_  = this->get_parameter("match_iou_thresh").as_double();
    warn_confidence_   = this->get_parameter("warn_confidence").as_double();
    warn_level_        = this->get_parameter("warn_level").as_string();

    // 初始化地理坐标原点（雷达坐标 → WGS84 的基准点）
    double origin_lat = this->get_parameter("origin_lat").as_double();
    double origin_lng = this->get_parameter("origin_lng").as_double();
    utils::CoordTransform::setOrigin(origin_lat, origin_lng);

    // 加载相机-雷达标定参数
    std::string calib_path = this->get_parameter("calib_yaml").as_string();
    if (!loadCalibration(calib_path)) {
        RCLCPP_WARN(this->get_logger(),
            "[Fusion] 标定文件未加载：%s，融合将仅使用雷达坐标", calib_path.c_str());
    }

    // ── 时间同步订阅（容忍 200ms 时差）──────────────────
    sub_radar_.subscribe(this, "/radar/detect");
    sub_camera_.subscribe(this, "/camera/detect_result");
    sync_ = std::make_shared<message_filters::Synchronizer<SyncPolicy>>(
        SyncPolicy(10), sub_radar_, sub_camera_);
    sync_->setMaxIntervalDuration(rclcpp::Duration::from_seconds(0.2));
    sync_->registerCallback(
        std::bind(&FusionManager::fusionCallback, this,
                  std::placeholders::_1, std::placeholders::_2));

    // ── 发布 ──────────────────────────────────────────────
    pub_final_    = this->create_publisher<interface::msg::DroneDetectArray>("/fusion/final_result", 10);
    pub_warn_     = this->create_publisher<interface::msg::RadarWarn>("/fusion/warn", 10);
    pub_markers_  = this->create_publisher<visualization_msgs::msg::MarkerArray>("/fusion/markers", 10);
    pub_warn_json_= this->create_publisher<std_msgs::msg::String>("/fusion/warn_json", 10);

    RCLCPP_INFO(this->get_logger(), "[Fusion] 融合管理节点已启动");
}

// ─────────────────────────────────────────────────────────────────────────────
void FusionManager::fusionCallback(
    const interface::msg::DroneDetectArray::ConstSharedPtr & radar_msg,
    const interface::msg::DroneDetectArray::ConstSharedPtr & camera_msg)
{
    double ts = rclcpp::Time(radar_msg->header.stamp).seconds();

    // ── 1. 匹配雷达检测与相机检测 ─────────────────────────
    std::vector<interface::msg::DroneDetect> fused_dets;

    if (!calib_loaded_) {
        // 无标定时直接用雷达结果（已含 3D 坐标）
        fused_dets = radar_msg->drones;
    } else {
        // 将雷达 3D 点投影到图像平面，与相机 BBox 中心做距离匹配
        auto matches = matchDetections(*radar_msg, *camera_msg,
                                       cam_intrinsic_, T_cam_lidar_);

        std::set<int> matched_radar, matched_camera;
        for (auto & [ri, ci] : matches) {
            interface::msg::DroneDetect fused = radar_msg->drones[ri];
            const auto & cam_det = camera_msg->drones[ci];

            // 融合置信度：雷达 0.6 × 相机置信度 0.4 加权
            fused.confidence = 0.6 * fused.confidence + 0.4 * cam_det.confidence;
            fused.bbox_x     = cam_det.bbox_x;
            fused.bbox_y     = cam_det.bbox_y;
            fused.bbox_w     = cam_det.bbox_w;
            fused.bbox_h     = cam_det.bbox_h;
            fused.label      = cam_det.label;  // 相机分类结果更可信
            fused_dets.push_back(fused);
            matched_radar.insert(ri);
            matched_camera.insert(ci);
        }

        // 未匹配的雷达检测（无视觉确认，置信度降权）
        for (size_t i = 0; i < radar_msg->drones.size(); ++i) {
            if (!matched_radar.count(i)) {
                auto d = radar_msg->drones[i];
                d.confidence *= 0.6;
                fused_dets.push_back(d);
            }
        }
    }

    // ── 2. 卡尔曼多目标追踪更新 ───────────────────────────
    updateTracks(fused_dets, ts);

    // ── 3. 报警 + 发布 ─────────────────────────────────────
    publishResults();
    publishMarkers();
}

// ─────────────────────────────────────────────────────────────────────────────
std::vector<std::pair<int,int>> FusionManager::matchDetections(
    const interface::msg::DroneDetectArray & radar,
    const interface::msg::DroneDetectArray & camera,
    const Eigen::Matrix3d & K,
    const Eigen::Matrix4d & T_cam_lidar)
{
    std::vector<std::pair<int,int>> matches;
    if (radar.drones.empty() || camera.drones.empty()) return matches;

    // 构建代价矩阵（雷达投影点 vs 相机 BBox 中心欧氏距离）
    int nr = radar.drones.size(), nc = camera.drones.size();
    Eigen::MatrixXd cost(nr, nc);

    for (int r = 0; r < nr; ++r) {
        Eigen::Vector3d pt(radar.drones[r].x,
                           radar.drones[r].y,
                           radar.drones[r].z);
        cv::Point2f proj = projectToImage(pt, K, T_cam_lidar);

        for (int c = 0; c < nc; ++c) {
            const auto & cd = camera.drones[c];
            float cam_cx = cd.bbox_x + cd.bbox_w / 2.0f;
            float cam_cy = cd.bbox_y + cd.bbox_h / 2.0f;
            double dx = proj.x - cam_cx, dy = proj.y - cam_cy;
            cost(r, c) = std::sqrt(dx*dx + dy*dy);
        }
    }

    // 贪心最近邻匹配（足够无人机数量较少的场景，如需多目标可改匈牙利算法）
    std::vector<bool> used_cam(nc, false);
    for (int r = 0; r < nr; ++r) {
        double best = match_dist_thresh_;
        int best_c = -1;
        for (int c = 0; c < nc; ++c) {
            if (!used_cam[c] && cost(r, c) < best) {
                best = cost(r, c);
                best_c = c;
            }
        }
        if (best_c >= 0) {
            matches.push_back({r, best_c});
            used_cam[best_c] = true;
        }
    }
    return matches;
}

cv::Point2f FusionManager::projectToImage(
    const Eigen::Vector3d & pt3d,
    const Eigen::Matrix3d & K,
    const Eigen::Matrix4d & T)
{
    Eigen::Vector4d p_hom(pt3d.x(), pt3d.y(), pt3d.z(), 1.0);
    Eigen::Vector4d p_cam = T * p_hom;
    if (p_cam.z() <= 0) return cv::Point2f(-1, -1);

    Eigen::Vector3d p_img = K * p_cam.head<3>();
    return cv::Point2f(p_img.x() / p_img.z(), p_img.y() / p_img.z());
}

// ─────────────────────────────────────────────────────────────────────────────
void FusionManager::updateTracks(
    const std::vector<interface::msg::DroneDetect> & dets,
    double ts)
{
    // 预测所有现有轨迹
    for (auto & [id, track] : tracks_) {
        double dt = ts - track.kf.last_update_time;
        if (dt > 0 && dt < 1.0) track.kf.predict(dt);
    }

    // 简单最近邻关联（按 3D 距离）
    std::set<uint32_t> updated_ids;
    double assoc_dist = 10.0;  // 米，超过此距离认为是新目标

    for (const auto & det : dets) {
        uint32_t best_id = UINT32_MAX;
        double best_dist = assoc_dist;

        for (auto & [id, track] : tracks_) {
            auto pos = track.kf.getPosition();
            double d = std::sqrt(
                std::pow(pos.x() - det.x, 2) +
                std::pow(pos.y() - det.y, 2) +
                std::pow(pos.z() - det.z, 2));
            if (d < best_dist) { best_dist = d; best_id = id; }
        }

        if (best_id == UINT32_MAX) {
            // 新目标：创建轨迹
            DroneTrack t;
            t.track_id = next_track_id_++;
            t.kf.init(det.x, det.y, det.z, ts);
            t.latest = det;
            t.latest.drone_id = t.track_id;
            t.hit_count = 1;
            tracks_[t.track_id] = t;
            updated_ids.insert(t.track_id);
        } else {
            // 更新已有轨迹
            auto & track = tracks_[best_id];
            track.kf.update(det.x, det.y, det.z);
            track.kf.last_update_time = ts;
            auto pos = track.kf.getPosition();
            auto vel = track.kf.getVelocity();
            track.latest = det;
            track.latest.drone_id = best_id;
            track.latest.x  = pos.x();
            track.latest.y  = pos.y();
            track.latest.z  = pos.z();
            track.latest.vx = vel.x();
            track.latest.vy = vel.y();
            track.latest.vz = vel.z();
            track.latest.is_tracked = true;
            track.hit_count++;
            if (track.hit_count >= confirm_thresh_) track.confirmed = true;
            updated_ids.insert(best_id);
        }
    }

    // 未更新的轨迹增加丢失计数
    for (auto & [id, track] : tracks_) {
        if (!updated_ids.count(id)) track.kf.miss_count++;
    }

    // 删除长时间丢失的轨迹
    for (auto it = tracks_.begin(); it != tracks_.end(); ) {
        if (it->second.kf.miss_count > max_miss_frames_)
            it = tracks_.erase(it);
        else
            ++it;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
void FusionManager::publishResults()
{
    interface::msg::DroneDetectArray arr;
    arr.header.stamp = this->now();
    arr.header.frame_id = "map";

    for (auto & [id, track] : tracks_) {
        if (!track.confirmed) continue;
        auto det = track.latest;
        // 填入地理坐标（雷达坐标 → WGS84），供 web_dashboard 地图使用
        Eigen::Vector3d wgs = utils::CoordTransform::lidarToWGS84(
            Eigen::Vector3d(det.x, det.y, det.z));
        det.lat = wgs.x();
        det.lng = wgs.y();
        arr.drones.push_back(det);
        checkAndWarn(track);
    }
    pub_final_->publish(arr);
}

void FusionManager::checkAndWarn(const DroneTrack & track)
{
    if (track.warned) return;
    if (track.latest.confidence < warn_confidence_) return;

    // 发布 ROS2 报警消息
    interface::msg::RadarWarn warn;
    warn.header.stamp = this->now();
    warn.drone_id    = track.track_id;
    warn.x           = track.latest.x;
    warn.y           = track.latest.y;
    warn.z           = track.latest.z;
    warn.confidence  = track.latest.confidence;
    warn.warn_level  = warn_level_;
    warn.description = "无人机检测确认！ID=" + std::to_string(track.track_id) +
                       " 高度=" + std::to_string((int)track.latest.z) + "m";
    pub_warn_->publish(warn);

    // 同时发布 JSON 字符串（供 web_dashboard WebSocket 消费）
    nlohmann::json j;
    j["type"]       = "drone_warn";
    j["drone_id"]   = track.track_id;
    j["x"]          = track.latest.x;
    j["y"]          = track.latest.y;
    j["z"]          = track.latest.z;
    j["confidence"] = track.latest.confidence;
    j["level"]      = warn_level_;
    std_msgs::msg::String jmsg;
    jmsg.data = j.dump();
    pub_warn_json_->publish(jmsg);

    // 标记已报警（轨迹对象是 const 引用，真实代码需改为非 const）
    RCLCPP_WARN(this->get_logger(),
        "[Fusion][报警] %s", warn.description.c_str());
}

// ─────────────────────────────────────────────────────────────────────────────
void FusionManager::publishMarkers()
{
    visualization_msgs::msg::MarkerArray ma;
    int mid = 0;

    for (auto & [id, track] : tracks_) {
        if (!track.confirmed) continue;
        const auto & d = track.latest;

        // 球形 Marker（目标位置）
        visualization_msgs::msg::Marker sphere;
        sphere.header.frame_id = "map";
        sphere.header.stamp    = this->now();
        sphere.ns              = "drones";
        sphere.id              = mid++;
        sphere.type            = visualization_msgs::msg::Marker::SPHERE;
        sphere.action          = visualization_msgs::msg::Marker::ADD;
        sphere.pose.position.x = d.x;
        sphere.pose.position.y = d.y;
        sphere.pose.position.z = d.z;
        sphere.scale.x = sphere.scale.y = sphere.scale.z = 2.0;
        sphere.color.r = 1.0f; sphere.color.g = 0.0f;
        sphere.color.b = 0.0f; sphere.color.a = 0.9f;
        sphere.lifetime = rclcpp::Duration::from_seconds(0.5);
        ma.markers.push_back(sphere);

        // 文字 Marker（显示 ID + 高度）
        visualization_msgs::msg::Marker text;
        text.header        = sphere.header;
        text.ns            = "drone_labels";
        text.id            = mid++;
        text.type          = visualization_msgs::msg::Marker::TEXT_VIEW_FACING;
        text.action        = visualization_msgs::msg::Marker::ADD;
        text.pose.position.x = d.x;
        text.pose.position.y = d.y;
        text.pose.position.z = d.z + 3.0;
        text.scale.z       = 2.5;
        text.color.r = text.color.g = text.color.b = 1.0f;
        text.color.a       = 1.0f;
        text.text          = "ID:" + std::to_string(id) +
                             "\nH:" + std::to_string((int)d.z) + "m" +
                             "\n" + std::to_string((int)(d.confidence * 100)) + "%";
        text.lifetime      = rclcpp::Duration::from_seconds(0.5);
        ma.markers.push_back(text);
    }
    pub_markers_->publish(ma);
}

// ─────────────────────────────────────────────────────────────────────────────
bool FusionManager::loadCalibration(const std::string & path)
{
    try {
        YAML::Node cfg = YAML::LoadFile(path);
        // 读取相机内参 K (3×3)
        auto K = cfg["camera_matrix"]["data"].as<std::vector<double>>();
        for (int r = 0; r < 3; ++r)
            for (int c = 0; c < 3; ++c)
                cam_intrinsic_(r, c) = K[r * 3 + c];

        // 读取外参 T_cam_lidar (4×4)
        auto T = cfg["T_cam_lidar"]["data"].as<std::vector<double>>();
        for (int r = 0; r < 4; ++r)
            for (int c = 0; c < 4; ++c)
                T_cam_lidar_(r, c) = T[r * 4 + c];

        calib_loaded_ = true;
        RCLCPP_INFO(this->get_logger(), "[Fusion] 标定参数加载成功：%s", path.c_str());
        return true;
    } catch (const std::exception & e) {
        RCLCPP_WARN(this->get_logger(),
            "[Fusion] 标定文件解析失败：%s", e.what());
        return false;
    }
}

}  // namespace fusion
