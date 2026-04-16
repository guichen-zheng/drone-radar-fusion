#include "camera_vision/yolo_detector.hpp"
#include <filesystem>

namespace camera_vision
{

YoloDetector::YoloDetector(const rclcpp::NodeOptions & options)
: Node("yolo_detector", options)
{
    // ── 参数声明 ───────────────────────────────────────────
    this->declare_parameter("model_path", "model/ONNX/yolo_drone.onnx");
    this->declare_parameter("class_names_path", "model/ONNX/classes.txt");
    this->declare_parameter("input_width", 640);
    this->declare_parameter("input_height", 640);
    this->declare_parameter("conf_thresh", 0.5);
    this->declare_parameter("nms_thresh", 0.45);
    this->declare_parameter("use_gpu", true);

    input_width_  = this->get_parameter("input_width").as_int();
    input_height_ = this->get_parameter("input_height").as_int();
    conf_thresh_  = static_cast<float>(this->get_parameter("conf_thresh").as_double());
    nms_thresh_   = static_cast<float>(this->get_parameter("nms_thresh").as_double());
    use_gpu_      = this->get_parameter("use_gpu").as_bool();

    // 加载类别名称
    std::string classes_path = this->get_parameter("class_names_path").as_string();
    std::ifstream f(classes_path);
    if (f.is_open()) {
        std::string line;
        while (std::getline(f, line)) class_names_.push_back(line);
    } else {
        class_names_ = {"drone"};  // 默认只有无人机一类
        RCLCPP_WARN(this->get_logger(), "[Camera] 类别文件未找到，使用默认 [drone]");
    }

    // 加载模型
    std::string model_path = this->get_parameter("model_path").as_string();
    if (!loadModel(model_path)) {
        RCLCPP_ERROR(this->get_logger(),
            "[Camera] ONNX 模型加载失败：%s", model_path.c_str());
        RCLCPP_ERROR(this->get_logger(),
            "[Camera] 请将训练好的 ONNX 模型放到 model/ONNX/ 目录");
    }

    // ── 订阅与发布 ─────────────────────────────────────────
    // 海康相机驱动发布图像 topic（由 hik_camera 包提供）
    sub_image_ = this->create_subscription<sensor_msgs::msg::Image>(
        "/hik_camera/image_raw", 10,
        std::bind(&YoloDetector::imageCallback, this, std::placeholders::_1));

    pub_detect_ = this->create_publisher<interface::msg::DroneDetectArray>(
        "/camera/detect_result", 10);

    pub_debug_image_ = this->create_publisher<sensor_msgs::msg::Image>(
        "/camera/debug_image", 10);

    RCLCPP_INFO(this->get_logger(), "[Camera] YOLO 检测节点已启动");
}

bool YoloDetector::loadModel(const std::string & path)
{
    if (!std::filesystem::exists(path)) {
        RCLCPP_WARN(this->get_logger(),
            "[Camera] 模型文件不存在：%s", path.c_str());
        return false;
    }
    net_ = cv::dnn::readNetFromONNX(path);
    if (use_gpu_) {
        net_.setPreferableBackend(cv::dnn::DNN_BACKEND_CUDA);
        net_.setPreferableTarget(cv::dnn::DNN_TARGET_CUDA);
        RCLCPP_INFO(this->get_logger(), "[Camera] 使用 CUDA GPU 加速推理");
    } else {
        net_.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);
        net_.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);
    }
    model_loaded_ = true;
    return true;
}

void YoloDetector::imageCallback(const sensor_msgs::msg::Image::SharedPtr msg)
{
    if (!model_loaded_) return;

    cv_bridge::CvImagePtr cv_ptr;
    try {
        cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
    } catch (cv_bridge::Exception & e) {
        RCLCPP_ERROR(this->get_logger(), "[Camera] cv_bridge 错误：%s", e.what());
        return;
    }

    float scale;
    cv::Point offset;
    cv::Mat blob = preprocess(cv_ptr->image, scale, offset);

    net_.setInput(blob);
    cv::Mat output = net_.forward();  // YOLOv8 输出格式：[1, 84, 8400]

    auto dets = runInference(blob, scale, offset, cv_ptr->image.size());
    auto final_dets = applyNMS(dets);

    publishResults(final_dets, cv_ptr->image, msg->header);
}

cv::Mat YoloDetector::preprocess(const cv::Mat & image, float & scale, cv::Point & offset)
{
    // Letterbox resize（保持宽高比，填充灰色边框）
    int iw = image.cols, ih = image.rows;
    scale = std::min((float)input_width_ / iw, (float)input_height_ / ih);
    int nw = static_cast<int>(iw * scale);
    int nh = static_cast<int>(ih * scale);
    offset.x = (input_width_ - nw) / 2;
    offset.y = (input_height_ - nh) / 2;

    cv::Mat resized;
    cv::resize(image, resized, cv::Size(nw, nh));
    cv::Mat padded(input_height_, input_width_, CV_8UC3, cv::Scalar(114, 114, 114));
    resized.copyTo(padded(cv::Rect(offset.x, offset.y, nw, nh)));

    cv::Mat blob = cv::dnn::blobFromImage(padded, 1.0 / 255.0,
        cv::Size(input_width_, input_height_), cv::Scalar(), true, false);
    return blob;
}

std::vector<YoloDetection> YoloDetector::runInference(
    const cv::Mat & /*blob*/,
    float scale,
    const cv::Point & offset,
    const cv::Size & orig_size)
{
    // 获取网络输出并解析 YOLOv8 格式
    std::vector<cv::Mat> outputs;
    net_.forward(outputs, net_.getUnconnectedOutLayersNames());

    std::vector<YoloDetection> results;
    // outputs[0] shape: [1, num_classes+4, num_anchors]
    cv::Mat data = outputs[0];
    data = data.reshape(1, data.size[1]);   // [85, 8400]
    cv::transpose(data, data);              // [8400, 85]

    for (int i = 0; i < data.rows; ++i) {
        float * row = data.ptr<float>(i);
        // row[0..3] = cx, cy, w, h（相对 input_size）
        // row[4..N] = 各类置信度
        float max_conf = 0;
        int class_id = 0;
        for (int c = 4; c < data.cols; ++c) {
            if (row[c] > max_conf) { max_conf = row[c]; class_id = c - 4; }
        }
        if (max_conf < conf_thresh_) continue;

        // 还原到原图坐标
        float cx = (row[0] - offset.x) / scale;
        float cy = (row[1] - offset.y) / scale;
        float w  = row[2] / scale;
        float h  = row[3] / scale;

        YoloDetection det;
        det.class_id   = class_id;
        det.confidence = max_conf;
        det.label      = (class_id < (int)class_names_.size()) ?
                          class_names_[class_id] : "unknown";
        det.bbox = cv::Rect(
            std::max(0, (int)(cx - w / 2)),
            std::max(0, (int)(cy - h / 2)),
            std::min((int)w, orig_size.width),
            std::min((int)h, orig_size.height)
        );
        results.push_back(det);
    }
    return results;
}

std::vector<YoloDetection> YoloDetector::applyNMS(std::vector<YoloDetection> & dets)
{
    std::vector<cv::Rect> boxes;
    std::vector<float> scores;
    for (auto & d : dets) { boxes.push_back(d.bbox); scores.push_back(d.confidence); }

    std::vector<int> indices;
    cv::dnn::NMSBoxes(boxes, scores, conf_thresh_, nms_thresh_, indices);

    std::vector<YoloDetection> result;
    for (int idx : indices) result.push_back(dets[idx]);
    return result;
}

void YoloDetector::publishResults(
    const std::vector<YoloDetection> & dets,
    const cv::Mat & image,
    const std_msgs::msg::Header & header)
{
    interface::msg::DroneDetectArray arr;
    arr.header = header;

    cv::Mat debug = image.clone();

    for (size_t i = 0; i < dets.size(); ++i) {
        const auto & d = dets[i];
        interface::msg::DroneDetect det;
        det.drone_id   = static_cast<uint32_t>(i);
        det.bbox_x     = d.bbox.x;
        det.bbox_y     = d.bbox.y;
        det.bbox_w     = d.bbox.width;
        det.bbox_h     = d.bbox.height;
        det.confidence = d.confidence;
        det.label      = d.label;
        // 注意：相机无深度，x/y/z 由 fusion 包填充
        arr.drones.push_back(det);

        // 调试图像绘制
        cv::rectangle(debug, d.bbox, cv::Scalar(0, 255, 0), 2);
        std::string txt = d.label + " " + std::to_string((int)(d.confidence * 100)) + "%";
        cv::putText(debug, txt, cv::Point(d.bbox.x, d.bbox.y - 5),
                    cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 255, 0), 2);
    }

    pub_detect_->publish(arr);

    // 发布调试图像（可在 Foxglove Studio 中查看）
    auto debug_msg = cv_bridge::CvImage(header, "bgr8", debug).toImageMsg();
    pub_debug_image_->publish(*debug_msg);
}

}  // namespace camera_vision
