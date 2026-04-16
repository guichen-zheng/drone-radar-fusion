#include "camera_vision/yolo_detector.hpp"

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<camera_vision::YoloDetector>());
    rclcpp::shutdown();
    return 0;
}
