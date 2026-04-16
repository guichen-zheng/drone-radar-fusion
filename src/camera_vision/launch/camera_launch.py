from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('camera_vision'), '..', '..', '..', '..', 'config', 'params.yaml'
    )
    return LaunchDescription([
        # ── 海康相机驱动（由 hik_camera 包提供，需单独安装）────────────
        Node(
            package='hik_camera',          # ← 填入你的海康 ROS2 驱动包名
            executable='hik_camera_node',
            name='hik_camera',
            output='screen',
            parameters=[config],
        ),
        # ── YOLO 检测节点 ────────────────────────────────────────────
        Node(
            package='camera_vision',
            executable='camera_node',
            name='yolo_detector',
            output='screen',
            parameters=[config],
        ),
    ])
