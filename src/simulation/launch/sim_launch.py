"""
simulation/launch/sim_launch.py

仿真一键启动：
  1. Gazebo（加载 drone_sim.world，含红色无人机模型）
  2. sim_bridge（3s 后，等 Gazebo 就绪）
  3. fusion_manager（3s 后，使用 sim_params.yaml）
  4. web_dashboard（4s 后）

启动命令：
  ros2 launch simulation sim_launch.py
"""

import os
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    sim_share   = get_package_share_directory('simulation')
    fusion_share= get_package_share_directory('fusion')
    gazebo_share= get_package_share_directory('gazebo_ros')

    # 项目根目录（config/ 在此下面）
    ws_root = os.path.join(sim_share, '..', '..', '..', '..')
    ws_root = os.path.normpath(ws_root)

    world_file   = os.path.join(sim_share, 'worlds', 'drone_sim.world')
    models_dir   = os.path.join(sim_share, 'models')
    sim_params   = os.path.join(ws_root, 'config', 'sim_params.yaml')
    fusion_params= os.path.join(ws_root, 'config', 'params.yaml')   # 备用

    return LaunchDescription([

        # ── 0. 设置 Gazebo 模型路径，让其能找到 drone 模型 ─────────────────────
        SetEnvironmentVariable(
            name='GAZEBO_MODEL_PATH',
            value=models_dir
        ),

        # ── 1. 启动 Gazebo（gzserver + gzclient）────────────────────────────
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_share, 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={
                'world': world_file,
                'verbose': 'false',
            }.items()
        ),

        # ── 2. sim_bridge（3s 后，等 Gazebo 服务就绪）───────────────────────
        TimerAction(period=3.0, actions=[
            Node(
                package='simulation',
                executable='sim_bridge',
                name='sim_bridge',
                output='screen',
                parameters=[{
                    'radius': 20.0,
                    'height': 20.0,
                    'period': 40.0,
                    'drone_model_name': 'drone',
                }]
            )
        ]),

        # ── 3. fusion_manager（3s 后，使用仿真参数文件）─────────────────────
        TimerAction(period=3.0, actions=[
            Node(
                package='fusion',
                executable='fusion_node',
                name='fusion_manager',
                output='screen',
                parameters=[sim_params]
            )
        ]),

        # ── 4. web_dashboard（4s 后）────────────────────────────────────────
        TimerAction(period=4.0, actions=[
            Node(
                package='web_dashboard',
                executable='web_dashboard_node',
                name='web_dashboard_node',
                output='screen',
            )
        ]),
    ])
