from setuptools import setup
from glob import glob

package_name = 'camera_yolo'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='guichen',
    maintainer_email='2830532983@qq.com',
    description='YOLO 推理节点（conda subprocess 桥接，绕过 cv::dnn 兼容问题）',
    license='MIT',
    entry_points={
        'console_scripts': [
            # 注意：yolo_worker.py 不进入 entry_points —— 它要在 conda 环境里跑，
            # 不能用系统 Python 启动。yolo_node 通过 share/ 路径找到它。
            'yolo_node = camera_yolo.yolo_node:main',
        ],
    },
)
