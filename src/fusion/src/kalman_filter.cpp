#include "fusion/kalman_filter.hpp"

namespace fusion
{

KalmanFilter::KalmanFilter()
{
    // 状态向量初始化（6 维）
    x_ = Eigen::VectorXd::Zero(6);

    // 状态协方差（初始不确定性较大）
    P_ = Eigen::MatrixXd::Identity(6, 6) * 100.0;

    // 观测矩阵 H：只观测位置（x, y, z）
    H_ = Eigen::MatrixXd::Zero(3, 6);
    H_(0, 0) = 1.0;
    H_(1, 1) = 1.0;
    H_(2, 2) = 1.0;

    // 观测噪声（雷达测量精度约 0.5m）
    R_ = Eigen::MatrixXd::Identity(3, 3) * 0.25;

    // 过程噪声（无人机机动性适中）
    Q_ = Eigen::MatrixXd::Zero(6, 6);
    Q_(0, 0) = Q_(1, 1) = Q_(2, 2) = 0.1;    // 位置过程噪声
    Q_(3, 3) = Q_(4, 4) = Q_(5, 5) = 1.0;    // 速度过程噪声

    // 状态转移矩阵（初始化为单位矩阵，在 predict 中动态填入 dt）
    F_ = Eigen::MatrixXd::Identity(6, 6);
}

void KalmanFilter::init(double x, double y, double z, double timestamp)
{
    x_(0) = x; x_(1) = y; x_(2) = z;
    x_(3) = 0; x_(4) = 0; x_(5) = 0;
    P_ = Eigen::MatrixXd::Identity(6, 6) * 100.0;
    last_update_time = timestamp;
    is_initialized = true;
    miss_count = 0;
}

void KalmanFilter::predict(double dt)
{
    if (!is_initialized) return;

    // 更新状态转移矩阵（匀速运动模型）
    F_(0, 3) = dt;
    F_(1, 4) = dt;
    F_(2, 5) = dt;

    // 动态过程噪声（与 dt 相关）
    Eigen::MatrixXd Q = Q_;
    Q(0, 0) = Q(1, 1) = Q(2, 2) = 0.5 * dt * dt;
    Q(3, 3) = Q(4, 4) = Q(5, 5) = dt;

    x_ = F_ * x_;
    P_ = F_ * P_ * F_.transpose() + Q;
}

void KalmanFilter::update(double x, double y, double z)
{
    if (!is_initialized) return;

    Eigen::Vector3d z_obs(x, y, z);
    Eigen::Vector3d y_diff = z_obs - H_ * x_;
    Eigen::MatrixXd S = H_ * P_ * H_.transpose() + R_;
    Eigen::MatrixXd K = P_ * H_.transpose() * S.inverse();

    x_ = x_ + K * y_diff;
    P_ = (Eigen::MatrixXd::Identity(6, 6) - K * H_) * P_;
    miss_count = 0;
}

Eigen::Vector3d KalmanFilter::getPosition() const
{
    return Eigen::Vector3d(x_(0), x_(1), x_(2));
}

Eigen::Vector3d KalmanFilter::getVelocity() const
{
    return Eigen::Vector3d(x_(3), x_(4), x_(5));
}

Eigen::Vector3d KalmanFilter::getPredictedPosition() const
{
    return getPosition();
}

}  // namespace fusion
