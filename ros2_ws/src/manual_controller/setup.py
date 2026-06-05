import os
from glob import glob
from setuptools import setup

package_name = 'manual_controller'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Pedro',
    maintainer_email='pcondesalvarelli@gmail.com',
    description='Keyboard teleoperation node for EyeRobot',
    license='MIT',
    entry_points={
        'console_scripts': [
            'manual_controller = manual_controller.manual_controller_node:main',
            'state_estimator = manual_controller.state_estimator_node:main',
            'dual_odometry = manual_controller.dual_odometry_node:main',
        ],
    },
)
