cmake_minimum_required(VERSION 3.8)
project(utils)

set(CMAKE_CXX_STANDARD 17)

find_package(ament_cmake REQUIRED)
find_package(Eigen3 REQUIRED)

# utils 是纯头文件库（header-only），其他包用 ament_target_dependencies 引入即可
ament_export_include_directories(include)
ament_export_dependencies(Eigen3)

install(DIRECTORY include/ DESTINATION include)

ament_package()
