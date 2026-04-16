cmake_minimum_required(VERSION 3.8)
project(fusion)

set(CMAKE_CXX_STANDARD 17)
add_compile_options(-Wall -Wextra -O2)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(message_filters REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(OpenCV REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(interface REQUIRED)
find_package(utils REQUIRED)

# nlohmann/json（头文件库，直接包含）
include(FetchContent)
FetchContent_Declare(json
    URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz)
FetchContent_MakeAvailable(json)

include_directories(
    include
    ${EIGEN3_INCLUDE_DIRS}
    ${OpenCV_INCLUDE_DIRS}
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/../utils/include>
)

add_executable(fusion_node
    src/fusion_node.cpp
    src/fusion_manager.cpp
    src/kalman_filter.cpp
)

ament_target_dependencies(fusion_node
    rclcpp message_filters visualization_msgs std_msgs interface
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
