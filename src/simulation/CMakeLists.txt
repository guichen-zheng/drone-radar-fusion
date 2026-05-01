cmake_minimum_required(VERSION 3.8)
project(simulation)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# 安装 Python 包和 setup.py
ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  simulation/sim_bridge.py
  DESTINATION lib/${PROJECT_NAME}
)

# 安装 launch / worlds / models
install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}/launch)
install(DIRECTORY worlds/ DESTINATION share/${PROJECT_NAME}/worlds)
install(DIRECTORY models/ DESTINATION share/${PROJECT_NAME}/models)

ament_package()
