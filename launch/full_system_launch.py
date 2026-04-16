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

        # ── 1. Livox Avia 驱动（立即启动）──────────────────────────────────
        # ★ 取消注释并确认包名（安装好 livox_ros_driver2 后使用）
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(
        #         os.path.join(get_package_share_directory('livox_ros_driver2'),
        #                      'launch', 'livox_lidar_launch.py')),
        # ),

        # ── 2. 雷达处理节点（延迟 2s 等驱动就绪）──────────────────────────
        TimerAction(period=2.0, actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(get_package_share_directory('radar'),
                                 'launch', 'radar_launch.py')))
        ]),

        # ── 3. 相机 + YOLO（延迟 2s）────────────────────────────────────
        TimerAction(period=2.0, actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(get_package_share_directory('camera_vision'),
                                 'launch', 'camera_launch.py')))
        ]),

        # ── 4. 融合节点（延迟 4s 等上游就绪）──────────────────────────────
        TimerAction(period=4.0, actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(get_package_share_directory('fusion'),
                                 'launch', 'fusion_launch.py')))
        ]),

        # ── 5. Web Dashboard（延迟 5s）──────────────────────────────────
        TimerAction(period=5.0, actions=[
            Node(
                package='web_dashboard',
                executable='web_dashboard_node',
                name='web_dashboard_node',
                output='screen',
            )
        ]),

        # ── 6. 看门狗（最后启动，延迟 8s）──────────────────────────────
        TimerAction(period=8.0, actions=[
            Node(
                package='web_dashboard',        # watchdog 暂放 web_dashboard 包
                executable='watchdog_node',
                name='watchdog_node',
                output='screen',
            )
        ]),
    ])
