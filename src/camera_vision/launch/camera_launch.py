from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('camera_vision'),
        '..', '..', '..', '..', 'config', 'params.yaml'
    )
    return LaunchDescription([
        # ── 海康相机驱动（包名：hik_camera_ros2_driver）────────────────────────
        # 克隆自：https://github.com/SMBU-PolarBear-Robotics-Team/hik_camera_ros2_driver
        Node(
            package='hik_camera_ros2_driver',
            executable='hik_camera_ros2_driver_node',
            name='hik_camera',
            output='screen',
            parameters=[config],
            # 该驱动默认发布 /hik_camera/image_raw，与 yolo_detector 订阅一致
        ),
        # ── YOLO 检测节点 ──────────────────────────────────────────────────────
        Node(
            package='camera_vision',
            executable='camera_node',
            name='yolo_detector',
            output='screen',
            parameters=[config],
        ),
    ])
