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

        # ── 启动参数 ────────────────────────────────────────────────────────────
        DeclareLaunchArgument(
            'gui', default_value='false',
            description='启动 Gazebo GUI（true=开启 3D 界面，false=仅后台服务）'
        ),
        DeclareLaunchArgument(
            'map_radius', default_value='22.0',
            description='中间机的轨迹半径（米）。三机编队：内机 R-7 / 中机 R / 外机 R+6'
        ),

        # ── 0. 环境变量 ────────────────────────────────────────────────────────
        SetEnvironmentVariable(name='GAZEBO_MODEL_PATH', value=models_dir),
        # 修复 OGRE 渲染黑屏（ros2 launch 子进程不继承 shell 渲染环境）
        SetEnvironmentVariable(name='OGRE_RTT_MODE', value='Copy'),
        # 海康 MVS SDK 在 LD_LIBRARY_PATH 里塞了 /opt/MVS/lib/64，里面带过期的
        # libusb-1.0.so.0（缺 libusb_set_option 符号）会让 PCL/libpcl_io 加载
        # 失败 → radar_node 崩溃。这里只过滤掉 /opt/MVS 路径，保留 ROS/系统库。
        SetEnvironmentVariable(
            name='LD_LIBRARY_PATH',
            value=':'.join(
                p for p in os.environ.get('LD_LIBRARY_PATH', '').split(':')
                if p and '/opt/MVS' not in p
            )
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

        # ── 2. sim_bridge（8s 后，给 gzserver 充足时间完成初始化）──────────
        TimerAction(period=8.0, actions=[
            Node(
                package='simulation',
                executable='sim_bridge',
                name='sim_bridge',
                output='screen',
                parameters=[{
                    # 中间机的半径（近/远机自动 ±7m / +6m）
                    'radius': LaunchConfiguration('map_radius'),
                    'period': 40.0,
                }]
            )
        ]),

        # ── 3. 感知层（5s 后）：YOLO (走 conda subprocess) + radar (点云聚类) ──
        # 注：原 C++ camera_node 因系统 OpenCV 4.5.4 解析 YOLOv8 ONNX 失败，
        # 改用 simulation 包里的 Python yolo_node 桥接 conda 环境的 ultralytics
        TimerAction(period=5.0, actions=[
            Node(
                package='simulation',
                executable='yolo_node',
                name='yolo_detector',
                output='screen',
                parameters=[sim_params],
            ),
            Node(
                package='radar',
                executable='radar_node',
                name='radar_processor',
                output='screen',
                parameters=[sim_params],
                # 云台模式：radar 输出原始（lidar 局部坐标）到 _lidar 后缀的 topic，
                # 由 radar_world_repub 转世界坐标后再发回 /radar/detect 给 fusion
                remappings=[('/radar/detect', '/radar/detect_lidar')],
            ),
            # 雷达检测坐标变换：lidar frame → map frame
            Node(
                package='simulation',
                executable='radar_world_repub',
                name='radar_world_repub',
                output='screen',
                parameters=[{
                    'input_topic':  '/radar/detect_lidar',
                    'output_topic': '/radar/detect',
                    'world_frame':  'map',
                }],
            ),
        ]),

        # ── 4. fusion_manager（5s 后，与感知节点同时启动）───────────────────
        TimerAction(period=5.0, actions=[
            Node(
                package='fusion',
                executable='fusion_node',
                name='fusion_manager',
                output='screen',
                parameters=[sim_params]
            )
        ]),

        # ── 4.5 gimbal_controller（6s 后，等 radar_processor 起来再开始追）────
        # 走 set_entity_state 简化版：订阅 /radar/detect → 选目标 → 旋转
        # sensor_camera 模型 → 发布动态 TF lidar → camera_optical（fusion 用）
        TimerAction(period=6.0, actions=[
            Node(
                package='simulation',
                executable='gimbal_controller',
                name='gimbal_controller',
                output='screen',
                parameters=[sim_params],
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

        # ── 5. （已移除静态 lidar_map_tf）─────────────────────────────────────
        # 雷达现在装在 sensor_head 上跟着云台转，gimbal_controller 会动态发布
        # map→lidar 这个 TF（带 pan/tilt 旋转）。如果再起一个 static identity
        # 会和动态 TF 打架。

        # ── 6. RViz2（7s 后）──────────────────────────────────────────────────
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
