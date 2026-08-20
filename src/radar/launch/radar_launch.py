from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    project_root = os.path.normpath(os.path.join(
        get_package_share_directory('radar'), '..', '..', '..', '..'))
    config = os.path.join(project_root, 'config', 'params.yaml')
    general_config = os.path.join(
        project_root, 'config', 'radar_general_params.yaml')
    default_map = os.path.join(project_root, 'config', 'site_background.pcd')

    return LaunchDescription([
        DeclareLaunchArgument(
            'radar_params', default_value=general_config,
            description='Radar/fusion parameter overlay for real Avia deployment'),
        DeclareLaunchArgument(
            'map_pcd_path', default_value=default_map,
            description='Absolute PCD path recorded in the current empty scene'),
        Node(
            package='radar',
            executable='radar_node',
            name='radar_processor',
            output='screen',
            # Later entries override the legacy values in params.yaml.
            parameters=[
                config,
                LaunchConfiguration('radar_params'),
                # 独立参数保证命令行路径优先于节点专用 YAML。
                {'map_pcd_path_override': ParameterValue(
                    LaunchConfiguration('map_pcd_path'), value_type=str)},
            ],
            remappings=[
                ('/livox/lidar', '/livox/lidar'),       # Livox Avia 默认 topic，可修改
            ]
        )
    ])
