cmake_minimum_required(VERSION 3.8)
project(fusion)

set(CMAKE_CXX_STANDARD 17)
add_compile_options(-Wall -Wextra -O2)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(message_filters REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(OpenCV REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(interface REQUIRED)

# nlohmann/json（头文件库，直接包含）
include(FetchContent)
FetchContent_Declare(json
    URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz)
FetchContent_MakeAvailable(json)

include_directories(
    include
    ${EIGEN3_INCLUDE_DIRS}
    ${OpenCV_INCLUDE_DIRS}
    # utils 是 header-only 库，直接引用源码目录中的 include 路径
    ${CMAKE_CURRENT_SOURCE_DIR}/../utils/include
)

add_executable(fusion_node
    src/fusion_node.cpp
    src/fusion_manager.cpp
    src/kalman_filter.cpp
)

ament_target_dependencies(fusion_node
    rclcpp message_filters visualization_msgs std_msgs geometry_msgs
    tf2 tf2_ros interface
)
target_link_libraries(fusion_node
    Eigen3::Eigen
    ${OpenCV_LIBS}
    yaml-cpp
    nlohmann_json::nlohmann_json
)

install(TARGETS fusion_node DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ DESTINATION include)
install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}/launch)

ament_package()