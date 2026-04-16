cmake_minimum_required(VERSION 3.8)
project(camera_vision)

set(CMAKE_CXX_STANDARD 17)
add_compile_options(-Wall -Wextra -O2)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED)
find_package(interface REQUIRED)

include_directories(include ${OpenCV_INCLUDE_DIRS})

add_executable(camera_node
  src/camera_node.cpp
  src/yolo_detector.cpp
)

ament_target_dependencies(camera_node
  rclcpp sensor_msgs cv_bridge interface
)
target_link_libraries(camera_node ${OpenCV_LIBS})

install(TARGETS camera_node DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ DESTINATION include)
install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}/launch)

ament_package()
