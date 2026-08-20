from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    project_root = os.path.normpath(os.path.join(
        get_package_share_directory('fusion'), '..', '..', '..', '..'))
    config = os.path.join(project_root, 'config', 'params.yaml')
    general_config = os.path.join(
        project_root, 'config', 'radar_general_params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'radar_params', default_value=general_config,
            description='Radar/fusion parameter overlay for real Avia deployment'),
        Node(
            package='fusion',
            executable='fusion_node',
            name='fusion_manager',
            output='screen',
            parameters=[config, LaunchConfiguration('radar_params')],
        )
    ])
