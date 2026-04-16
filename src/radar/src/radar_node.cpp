#include "radar/radar_processor.hpp"

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<radar::RadarProcessor>());
    rclcpp::shutdown();
    return 0;
}
