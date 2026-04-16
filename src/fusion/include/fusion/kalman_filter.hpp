#pragma once

#include <Eigen/Dense>
#include <rclcpp/rclcpp.hpp>

namespace fusion
{

/**
 * @brief 用于单目标追踪的卡尔曼滤波器
 * 状态向量：[x, y, z, vx, vy, vz]（位置 + 速度，6 维）
 * 观测向量：[x, y, z]（雷达/融合位置，3 维）
 */
class KalmanFilter
{
public:
    KalmanFilter();

    // 用初始观测初始化滤波器
    void init(double x, double y, double z, double timestamp);

    // 预测步骤（dt = 时间间隔秒）
    void predict(double dt);

    // 更新步骤（雷达观测 or 融合位置）
    void update(double x, double y, double z);

    // 获取当前估计位置
    Eigen::Vector3d getPosition() const;

    // 获取当前估计速度
    Eigen::Vector3d getVelocity() const;

    // 获取预测位置（未 update 时）
    Eigen::Vector3d getPredictedPosition() const;

    bool is_initialized = false;
    double last_update_time = 0.0;  // Unix 时间戳（秒）
    int miss_count = 0;             // 连续未匹配帧数（超过阈值则删除轨迹）

private:
    // 状态向量 [x, y, z, vx, vy, vz]
    Eigen::VectorXd x_;  // 6×1

    // 协方差矩阵
    Eigen::MatrixXd P_;  // 6×6 状态协方差
    Eigen::MatrixXd F_;  // 6×6 状态转移矩阵
    Eigen::MatrixXd H_;  // 3×6 观测矩阵
    Eigen::MatrixXd R_;  // 3×3 观测噪声
    Eigen::MatrixXd Q_;  // 6×6 过程噪声
};

}  // namespace fusion
