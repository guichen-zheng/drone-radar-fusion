#include "fusion/fusion_manager.hpp"

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<fusion::FusionManager>());
    rclcpp::shutdown();
    return 0;
}
