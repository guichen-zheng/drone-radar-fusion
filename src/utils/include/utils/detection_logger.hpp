#pragma once

#include <rclcpp/rclcpp.hpp>
#include <chrono>
#include <string>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <filesystem>

namespace utils
{

/**
 * @brief 带时间戳的文件日志工具
 * 同时输出到 ROS2 日志 + 本地 CSV 文件（方便离线分析）
 * CSV 格式：timestamp_s, drone_id, x, y, z, vx, vy, vz, confidence, source
 */
class DetectionLogger
{
public:
    /**
     * @param log_dir   日志保存目录（自动创建）
     * @param node_name 用于 ROS2 日志前缀
     */
    explicit DetectionLogger(const std::string & log_dir = "/tmp/drone_fusion_logs")
    {
        std::filesystem::create_directories(log_dir);
        // 文件名带时间戳，避免覆盖
        auto now = std::chrono::system_clock::now();
        auto t   = std::chrono::system_clock::to_time_t(now);
        std::ostringstream ss;
        ss << log_dir << "/detection_"
           << std::put_time(std::localtime(&t), "%Y%m%d_%H%M%S")
           << ".csv";
        file_.open(ss.str(), std::ios::out);
        if (file_.is_open()) {
            file_ << "timestamp_s,drone_id,x,y,z,vx,vy,vz,confidence,source\n";
            file_.flush();
            log_path_ = ss.str();
        }
    }

    ~DetectionLogger() { if (file_.is_open()) file_.close(); }

    /**
     * @brief 写入一条检测记录
     * @param source  "radar" / "camera" / "fusion"
     */
    void log(double timestamp_s, uint32_t drone_id,
             double x, double y, double z,
             double vx, double vy, double vz,
             double confidence, const std::string & source)
    {
        if (!file_.is_open()) return;
        file_ << std::fixed << std::setprecision(4)
              << timestamp_s << ","
              << drone_id << ","
              << x << "," << y << "," << z << ","
              << vx << "," << vy << "," << vz << ","
              << confidence << ","
              << source << "\n";
        file_.flush();
    }

    const std::string & logPath() const { return log_path_; }

private:
    std::ofstream file_;
    std::string   log_path_;
};


/**
 * @brief 帧率计算器（用于监控各节点处理频率）
 */
class FpsCounter
{
public:
    explicit FpsCounter(int window = 30) : window_(window) {}

    void tick()
    {
        auto now = std::chrono::steady_clock::now();
        timestamps_.push_back(now);
        if ((int)timestamps_.size() > window_)
            timestamps_.erase(timestamps_.begin());
    }

    double fps() const
    {
        if (timestamps_.size() < 2) return 0.0;
        auto dt = std::chrono::duration<double>(
            timestamps_.back() - timestamps_.front()).count();
        return (timestamps_.size() - 1) / dt;
    }

private:
    int window_;
    std::vector<std::chrono::steady_clock::time_point> timestamps_;
};

}  // namespace utils
