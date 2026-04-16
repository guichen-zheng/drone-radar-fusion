cmake_minimum_required(VERSION 3.8)
project(radar)

set(CMAKE_CXX_STANDARD 17)
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -O2)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(PCL REQUIRED COMPONENTS common io filters kdtree segmentation registration)
find_package(interface REQUIRED)

include_directories(
  include
  ${PCL_INCLUDE_DIRS}
)
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

add_executable(radar_node
  src/radar_node.cpp
  src/radar_processor.cpp
)

ament_target_dependencies(radar_node
  rclcpp
  sensor_msgs
  visualization_msgs
  pcl_conversions
  interface
)

target_link_libraries(radar_node ${PCL_LIBRARIES})

install(TARGETS radar_node
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY include/ DESTINATION include)
install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}/launch)

ament_package()
