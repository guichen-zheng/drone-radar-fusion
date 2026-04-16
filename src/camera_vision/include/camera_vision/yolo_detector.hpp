#pragma once

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include "interface/msg/drone_detect_array.hpp"

namespace camera_vision
{

struct YoloDetection {
    int class_id;
    float confidence;
    cv::Rect bbox;
    std::string label;
};

class YoloDetector : public rclcpp::Node
{
public:
    explicit YoloDetector(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());

private:
    // ── 回调 ──────────────────────────────────────────────
    void imageCallback(const sensor_msgs::msg::Image::SharedPtr msg);

    // ── 检测流水线 ─────────────────────────────────────────
    // 1. 图像预处理（Letterbox resize + 归一化）
    cv::Mat preprocess(const cv::Mat & image, float & scale, cv::Point & offset);

    // 2. YOLO 推理（OpenCV DNN 或 TensorRT）
    std::vector<YoloDetection> runInference(const cv::Mat & blob,
                                            float scale,
                                            const cv::Point & offset,
                                            const cv::Size & orig_size);

    // 3. NMS 后处理
    std::vector<YoloDetection> applyNMS(std::vector<YoloDetection> & detections);

    // 4. 发布结果（含标注图像）
    void publishResults(const std::vector<YoloDetection> & dets,
                        const cv::Mat & image,
                        const std_msgs::msg::Header & header);

    // ── 模型加载 ───────────────────────────────────────────
    bool loadModel(const std::string & onnx_path);

    // ── ROS2 发布/订阅 ─────────────────────────────────────
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_image_;
    rclcpp::Publisher<interface::msg::DroneDetectArray>::SharedPtr pub_detect_;
    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr pub_debug_image_;

    // ── 模型 ──────────────────────────────────────────────
    cv::dnn::Net net_;
    bool model_loaded_ = false;
    std::vector<std::string> class_names_;

    // ── 参数 ──────────────────────────────────────────────
    int input_width_    = 640;
    int input_height_   = 640;
    float conf_thresh_  = 0.5f;
    float nms_thresh_   = 0.45f;
    bool use_gpu_       = true;
};

}  // namespace camera_vision
