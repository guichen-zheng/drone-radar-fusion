from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('radar'), '..', '..', '..', '..', 'config', 'params.yaml'
    )
    return LaunchDescription([
        Node(
            package='radar',
            executable='radar_node',
            name='radar_processor',
            output='screen',
            parameters=[config],
            remappings=[
                ('/livox/lidar', '/livox/lidar'),       # Livox Avia 默认 topic，可修改
            ]
        )
    ])
