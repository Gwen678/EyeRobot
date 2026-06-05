import os
from glob import glob
from setuptools import setup

package_name = 'oak_imu'

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
    description='OAK-D Lite IMU publisher + RViz cube (raw gyro orientation)',
    license='MIT',
    entry_points={
        'console_scripts': [
            'oak_imu_cube = oak_imu.oak_imu_cube:main',
        ],
    },
)
