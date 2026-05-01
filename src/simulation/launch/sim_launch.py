"""
simulation/launch/sim_launch.py

仿真一键启动：
  1. Gazebo gzserver（无 GUI，避免黑色窗口遮挡桌面）
  2. sim_bridge（3s 后，等 Gazebo 服务就绪）
  3. fusion_manager（3s 后，使用 sim_params.yaml）
  4. web_dashboard（4s 后）

启动命令：
  ros2 launch simulation sim_launch.py          # 默认无 GUI
  ros2 launch simulation sim_launch.py gui:=true # 需要看 Gazebo 3D 世界时开启
"""

import os
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
)
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    sim_share   = get_package_share_directory('simulation')
    gazebo_share= get_package_share_directory('gazebo_ros')

    # 项目根目录（config/ 在此下面）
    ws_root = os.path.normpath(os.path.join(sim_share, '..', '..', '..', '..'))

    world_file   = os.path.join(sim_share, 'worlds', 'drone_sim.world')
    models_dir   = os.path.join(sim_share, 'models')
    sim_params   = os.path.join(ws_root, 'config', 'sim_params.yaml')
    rviz_config  = os.path.join(ws_root, 'config', 'sim_rviz.rviz')

    return LaunchDescription([

        # ── GUI 开关（默认关闭，避免黑色窗口遮挡桌面）──────────────────────────
        DeclareLaunchArgument(
            'gui', default_value='false',
            description='启动 Gazebo GUI（true=开启 3D 界面，false=仅后台服务）'
        ),

        # ── 0. 设置 Gazebo 模型路径 ────────────────────────────────────────────
        SetEnvironmentVariable(
            name='GAZEBO_MODEL_PATH',
            value=models_dir
        ),

        # ── 1. 启动 Gazebo（gui:=false 时只跑 gzserver，无黑色窗口）────────────
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_share, 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={
                'world':   world_file,
                'verbose': 'false',
                'gui':     LaunchConfiguration('gui'),
            }.items()
        ),

        # ── 2. sim_bridge（5s 后，给 Gazebo 足够时间加载 world）────────────
        TimerAction(period=5.0, actions=[
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

        # ── 3. fusion_manager（5s 后，使用仿真参数文件）─────────────────────
        TimerAction(period=5.0, actions=[
            Node(
                package='fusion',
                executable='fusion_node',
                name='fusion_manager',
                output='screen',
                parameters=[sim_params]
            )
        ]),

        # ── 4. web_dashboard（6s 后）────────────────────────────────────────
        TimerAction(period=6.0, actions=[
            Node(
                package='web_dashboard',
                executable='web_dashboard_node',
                name='web_dashboard_node',
                output='screen',
            )
        ]),

        # ── 5. RViz2（7s 后，显示 /fusion/markers 3D 目标标记）──────────────
        TimerAction(period=7.0, actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=['-d', rviz_config],
                output='screen',
            )
        ]),
    ])
