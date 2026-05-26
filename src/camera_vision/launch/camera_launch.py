from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # 项目 config（给 yolo_detector 用 —— 模型路径、阈值等）
    project_config = os.path.join(
        get_package_share_directory('camera_vision'),
        '..', '..', '..', '..', 'config', 'params.yaml'
    )
    # 海康驱动自己的 config（给驱动用 —— pixel_format / exposure / gain / topic 名）
    hik_config = os.path.join(
        get_package_share_directory('hik_camera_ros2_driver'),
        'config', 'camera_params.yaml'
    )

    return LaunchDescription([
        # ── 海康相机驱动 ────────────────────────────────────────────────────────
        # 包名：hik_camera_ros2_driver
        # node 名必须与 hik_config YAML 的顶层 key (/hik_camera_ros2_driver) 一致，
        # 否则参数加载不进去，会用驱动默认值，topic 会变成 /camera/image。
        Node(
            package='hik_camera_ros2_driver',
            executable='hik_camera_ros2_driver_node',
            name='hik_camera_ros2_driver',
            output='screen',
            parameters=[hik_config],
            # 配置后发布到 /hik_camera/image_raw，与 yolo_detector 订阅一致
        ),
        # ── YOLO 检测节点（Python 版，conda subprocess 桥接 ultralytics）──────
        # 原 C++ camera_node 因系统 OpenCV 4.5.4 解析 YOLOv8 ONNX 触发 cv::dnn
        # shape_utils total() 断言崩溃（opencv/opencv#22251），已弃用。
        # 现走 camera_yolo 包：rclpy 节点 + conda 子进程跑 ultralytics 推理，
        # 走 stdin/stdout JSON 协议。需提前装好 conda env：
        #   conda create -n yolov8 python=3.10
        #   conda activate yolov8 && pip install ultralytics opencv-python
        # conda_python 路径如非默认，可在 params.yaml yolo_detector 段覆盖。
        Node(
            package='camera_yolo',
            executable='yolo_node',
            name='yolo_detector',
            output='screen',
            parameters=[project_config],
        ),
    ])
