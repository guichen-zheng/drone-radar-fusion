from setuptools import setup
import os
from glob import glob

package_name = 'web_dashboard'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name, package_name + '.web_dashboard'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'templates'), glob('templates/*.html')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools', 'flask', 'flask-socketio', 'opencv-python', 'numpy'],
    entry_points={
        'console_scripts': [
            'web_dashboard_node = web_dashboard.app:main',
        ],
    },
)
