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
    DeclareLaunchArgument, ExecuteProcess, TimerAction, SetEnvironmentVariable,
)
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node, SetParameter
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    project_root = os.path.normpath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    )
    params   = os.path.join(project_root, 'config', 'params.yaml')
    rviz_cfg = os.path.join(project_root, 'config', 'live_rviz.rviz')

    bag_path = LaunchConfiguration('bag_path')
    rate     = LaunchConfiguration('rate')
    calib_yaml = LaunchConfiguration('calib_yaml')
    radar_only_mode = LaunchConfiguration('radar_only_mode')
    radar_params = LaunchConfiguration('radar_params')
    map_pcd_path = LaunchConfiguration('map_pcd_path')

    # bag_path 是否非空（决定要不要自动播）
    bag_set_condition = IfCondition(
        PythonExpression(['"', bag_path, '" != ""'])
    )
    map_set_condition = IfCondition(
        PythonExpression(['"', map_pcd_path, '" != ""'])
    )
    map_unset_condition = IfCondition(
        PythonExpression(['"', map_pcd_path, '" == ""'])
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'bag_path', default_value='',
            description='bag 目录路径；非空时 launch 自动 ros2 bag play'),
        DeclareLaunchArgument(
            'rate', default_value='1.0',
            description='bag 播放速率（0.5=半速，2.0=双速）'),
        DeclareLaunchArgument(
            'calib_yaml',
            default_value=os.path.join(project_root, 'config', 'out_matrix.yaml'),
            description='相机-雷达标定文件；TIERS 数据使用 config/tiers_tello_out_calib.yaml'),
        DeclareLaunchArgument(
            'radar_only_mode', default_value='true',
            description='true=只用雷达；false=启用相机与雷达融合'),
        DeclareLaunchArgument(
            'radar_params', default_value=params,
            description='雷达参数文件；TIERS 使用 config/tiers_radar_params.yaml'),
        DeclareLaunchArgument(
            'map_pcd_path', default_value='',
            description='可选背景PCD覆盖；空字符串=使用radar_params中的路径'),

        # 海康 MVS SDK 在 LD_LIBRARY_PATH 中加入了自带的旧版 libusb，PCL 加载
        # libpcl_io 时会报 undefined symbol: libusb_set_option，导致 radar_node
        # 以 exit code 127 退出。回放虽然不启动相机驱动，但会继承终端环境，
        # 因此与实物 full_system_launch.py 一样过滤 /opt/MVS。
        SetEnvironmentVariable(
            name='LD_LIBRARY_PATH',
            value=':'.join(
                path for path in os.environ.get('LD_LIBRARY_PATH', '').split(':')
                if path and '/opt/MVS' not in path
            ),
        ),

        # 给所有 Node 默认 use_sim_time=True，省得每个 Node 单独写
        SetParameter(name='use_sim_time', value=True),

        # ── 下游处理节点 ───────────────────────────────────────────────────────
        Node(
            package='radar', executable='radar_node',
            name='radar_processor', output='screen',
            parameters=[params, radar_params],
            condition=map_unset_condition,
        ),
        Node(
            package='radar', executable='radar_node',
            name='radar_processor', output='screen',
            parameters=[
                params,
                radar_params,
                # 使用独立覆盖参数，避免 radar_params 中节点专用的
                # map_pcd_path 覆盖 launch 生成的 /** 参数。
                {'map_pcd_path_override': ParameterValue(
                    map_pcd_path, value_type=str)},
            ],
            condition=map_set_condition,
        ),
        Node(
            package='camera_yolo', executable='yolo_node',
            name='yolo_detector', output='screen',
            parameters=[params],
            condition=IfCondition(
                PythonExpression(['"', radar_only_mode, '" == "false"'])
            ),
        ),
        Node(
            package='fusion', executable='fusion_node',
            name='fusion_manager', output='screen',
            parameters=[
                params,
                radar_params,
                {
                    'calib_yaml': calib_yaml,
                    'radar_only_mode': ParameterValue(
                        radar_only_mode, value_type=bool),
                },
            ],
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
