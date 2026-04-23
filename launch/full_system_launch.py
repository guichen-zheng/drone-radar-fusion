"""
launch/full_system_launch.py
一键启动全系统：雷达驱动 → 相机+YOLO → 融合 → Web Dashboard
"""
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    return LaunchDescription([

        # ── 1. Livox Avia 驱动（立即启动）──────────────────────────────────────
        # 包名：livox_ros2_avia
        # 克隆自：https://github.com/ASIG-X/livox_ros2_avia
        # 启动前需先在 src/livox_driver/config/livox_lidar_config.json 填写序列号
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('livox_ros2_avia'),
                    'launch', 'livox_lidar_launch.py'   # 该包的实际 launch 文件名
                )
            ),
        ),

        # ── 2. 雷达处理节点（延迟 3s 等驱动就绪）──────────────────────────────
        TimerAction(period=3.0, actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory('radar'),
                        'launch', 'radar_launch.py'
                    )
                )
            )
        ]),

        # ── 3. 相机 + YOLO（延迟 3s）────────────────────────────────────────
        TimerAction(period=3.0, actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory('camera_vision'),
                        'launch', 'camera_launch.py'
                    )
                )
            )
        ]),

        # ── 4. 融合节点（延迟 5s 等上游就绪）──────────────────────────────────
        TimerAction(period=5.0, actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory('fusion'),
                        'launch', 'fusion_launch.py'
                    )
                )
            )
        ]),

        # ── 5. Web Dashboard（延迟 6s）──────────────────────────────────────
        TimerAction(period=6.0, actions=[
            Node(
                package='web_dashboard',
                executable='web_dashboard_node',
                name='web_dashboard_node',
                output='screen',
            )
        ]),

        # ── 6. 看门狗（最后启动，延迟 9s）──────────────────────────────────
        TimerAction(period=9.0, actions=[
            Node(
                package='web_dashboard',
                executable='watchdog_node',
                name='watchdog_node',
                output='screen',
            )
        ]),
    ])
