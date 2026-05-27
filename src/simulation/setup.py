from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'simulation'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.world')),
        (os.path.join('share', package_name, 'models/drone'),
            [f for f in glob('models/drone/*') if os.path.isfile(f)]),
        (os.path.join('share', package_name, 'models/drone/meshes'),
            glob('models/drone/meshes/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'sim_bridge         = simulation.sim_bridge:main',
            'yolo_node          = simulation.yolo_node:main',
            'gimbal_controller  = simulation.gimbal_controller:main',
            'radar_world_repub  = simulation.radar_world_repub:main',
        ],
    },
)
