"""launch/playback_launch.py — rosbag 回放专用 launch

只启动**下游处理节点**（radar / camera_yolo / fusion / web_dashboard / rviz），
不启动 livox / hik_camera 驱动 —— 这两个 topic 由 bag 提供，重复发会冲突。

所有节点强制 `use_sim_time=true`，让时间戳走 bag 的 /clock 而不是系统时间，
保证 fusion 的 message_filters 时间同步能正常凑对。

用法：
  # 方式 A：launch 自动 ros2 bag play
  ros2 launch launch/playback_launch.py bag_path:=$HOME/bags/test_xxx rate:=1.0

  # 方式 B：只起处理管线，bag 自己手动播（暂停/单步更灵活）
  ros2 launch launch/playback_launch.py
  # 另开终端：
  bash scripts/play_bag.sh ~/bags/test_xxx
"""
import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, ExecuteProcess, TimerAction,
)
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node, SetParameter


def generate_launch_description():
    project_root = os.path.normpath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    )
    params   = os.path.join(project_root, 'config', 'params.yaml')
    rviz_cfg = os.path.join(project_root, 'config', 'live_rviz.rviz')

    bag_path = LaunchConfiguration('bag_path')
    rate     = LaunchConfiguration('rate')

    # bag_path 是否非空（决定要不要自动播）
    bag_set_condition = IfCondition(
        PythonExpression(['"', bag_path, '" != ""'])
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'bag_path', default_value='',
            description='bag 目录路径；非空时 launch 自动 ros2 bag play'),
        DeclareLaunchArgument(
            'rate', default_value='1.0',
            description='bag 播放速率（0.5=半速，2.0=双速）'),

        # 给所有 Node 默认 use_sim_time=True，省得每个 Node 单独写
        SetParameter(name='use_sim_time', value=True),

        # ── 下游处理节点 ───────────────────────────────────────────────────────
        Node(
            package='radar', executable='radar_node',
            name='radar_processor', output='screen',
            parameters=[params],
        ),
        Node(
            package='camera_yolo', executable='yolo_node',
            name='yolo_detector', output='screen',
            parameters=[params],
        ),
        Node(
            package='fusion', executable='fusion_node',
            name='fusion_manager', output='screen',
            parameters=[params],
        ),

        # ── Web 仪表盘（2s 后，让上游先建好 topic）─────────────────────────────
        TimerAction(period=2.0, actions=[
            Node(
                package='web_dashboard', executable='web_dashboard_node',
                name='web_dashboard_node', output='screen',
            ),
        ]),

        # ── 静态 TF（livox_frame ↔ map）────────────────────────────────────────
        Node(
            package='tf2_ros', executable='static_transform_publisher',
            name='lidar_map_tf',
            arguments=['0', '0', '0', '0', '0', '0', 'map', 'livox_frame'],
            output='screen',
        ),

        # ── RViz（4s 后）───────────────────────────────────────────────────────
        TimerAction(period=4.0, actions=[
            Node(
                package='rviz2', executable='rviz2', name='rviz2',
                arguments=['-d', rviz_cfg],
                output='screen',
            ),
        ]),

        # ── 可选：自动 ros2 bag play（5s 后，等节点都订阅好）──────────────────
        # --clock 100：以 100Hz 发布 /clock，给 use_sim_time 的节点用
        # --loop：循环播放（要单次播完即停，用方式 B 手动播）
        TimerAction(period=5.0, actions=[
            ExecuteProcess(
                cmd=['ros2', 'bag', 'play',
                     bag_path,
                     '--rate', rate,
                     '--clock', '100',
                     '--loop'],
                output='screen',
                condition=bag_set_condition,
            ),
        ]),
    ])
