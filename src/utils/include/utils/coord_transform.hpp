#pragma once

#include <Eigen/Dense>
#include <cmath>

namespace utils
{

/**
 * @brief 坐标系转换工具
 *
 * 本项目使用三套坐标系：
 *   1. 雷达坐标系（Livox Avia 本体）：x 前、y 左、z 上，单位：米
 *   2. 世界坐标系（ENU）：以监控区域某点为原点，x 东、y 北、z 上，单位：米
 *   3. 地理坐标系（WGS84）：纬度 lat、经度 lng，用于 Web 地图显示
 *
 * 流程：雷达坐标 → [外参 T_world_lidar] → 世界坐标 → [原点偏移] → 地理坐标
 */
class CoordTransform
{
public:
    /**
     * @brief 设置雷达→世界坐标系变换矩阵
     * @param T  4×4 齐次变换矩阵（由 GICP 或手动标定给出）
     */
    static void setLidarToWorld(const Eigen::Matrix4d & T) { T_world_lidar_ = T; }

    /**
     * @brief 设置地图原点（世界坐标系原点对应的 WGS84 经纬度）
     * @param lat  纬度（度）
     * @param lng  经度（度）
     * @param alt  海拔（米，默认 0）
     */
    static void setOrigin(double lat, double lng, double alt = 0.0)
    {
        origin_lat_ = lat * M_PI / 180.0;   // 转弧度
        origin_lng_ = lng * M_PI / 180.0;
        origin_alt_ = alt;
    }

    /**
     * @brief 雷达坐标系 → 世界坐标系（ENU，米）
     */
    static Eigen::Vector3d lidarToWorld(const Eigen::Vector3d & pt_lidar)
    {
        Eigen::Vector4d p_h(pt_lidar.x(), pt_lidar.y(), pt_lidar.z(), 1.0);
        Eigen::Vector4d p_w = T_world_lidar_ * p_h;
        return p_w.head<3>();
    }

    /**
     * @brief 世界坐标系（ENU，米）→ WGS84 经纬高（度, 度, 米）
     *
     * 使用小角度近似（适用于监控区域 < 10km）：
     *   Δlat = y / R_earth
     *   Δlng = x / (R_earth * cos(lat0))
     *
     * @param enu   ENU 坐标（米）
     * @return      [latitude_deg, longitude_deg, altitude_m]
     */
    static Eigen::Vector3d enuToWGS84(const Eigen::Vector3d & enu)
    {
        constexpr double R = 6378137.0;  // WGS84 地球半径（米）
        double d_lat = enu.y() / R;
        double d_lng = enu.x() / (R * std::cos(origin_lat_));
        return Eigen::Vector3d(
            (origin_lat_ + d_lat) * 180.0 / M_PI,
            (origin_lng_ + d_lng) * 180.0 / M_PI,
            origin_alt_ + enu.z()
        );
    }

    /**
     * @brief 雷达坐标系 → WGS84（一步完成，融合包直接调用）
     * @return [lat_deg, lng_deg, alt_m]
     */
    static Eigen::Vector3d lidarToWGS84(const Eigen::Vector3d & pt_lidar)
    {
        return enuToWGS84(lidarToWorld(pt_lidar));
    }

    /**
     * @brief 将相机像素坐标 + 雷达深度反投影为世界坐标
     * @param u, v      图像像素坐标
     * @param depth_z   雷达提供的深度（米）
     * @param K         相机内参（3×3）
     * @param T_cam_lid 雷达→相机外参（4×4）
     */
    static Eigen::Vector3d pixelDepthToWorld(
        double u, double v, double depth_z,
        const Eigen::Matrix3d & K,
        const Eigen::Matrix4d & T_cam_lid)
    {
        // 像素 → 相机归一化坐标
        Eigen::Vector3d p_cam(
            (u - K(0,2)) / K(0,0) * depth_z,
            (v - K(1,2)) / K(1,1) * depth_z,
            depth_z
        );
        // 相机 → 雷达
        Eigen::Matrix4d T_lid_cam = T_cam_lid.inverse();
        Eigen::Vector4d p_h(p_cam.x(), p_cam.y(), p_cam.z(), 1.0);
        Eigen::Vector4d p_lid = T_lid_cam * p_h;
        // 雷达 → 世界
        return lidarToWorld(p_lid.head<3>());
    }

private:
    inline static Eigen::Matrix4d T_world_lidar_ = Eigen::Matrix4d::Identity();
    inline static double origin_lat_ = 0.0;   // 弧度
    inline static double origin_lng_ = 0.0;   // 弧度
    inline static double origin_alt_ = 0.0;
};

}  // namespace utils
