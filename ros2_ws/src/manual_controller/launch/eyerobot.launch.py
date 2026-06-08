"""Top-level EyeRobot launch: odometry stack + OAK-D IMU.

Composes manual_controller.launch.py (state_estimator, dual_odometry, URDF/TF,
optional EKF) with oak_imu.launch.py (BMI270 gyro → /oak/imu/data_raw).

Run in its own terminal (or tmux window) — no teleop, no RViz.
Those need a real TTY / separate session:
  ros2 run manual_controller manual_controller   # wasd
  rviz2 -d <path>/eyerobot.rviz                  # on PC

Optional flags:
  lidar:=true   Start the RPLidar A1M8 (ttyUSB1). Off by default.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    mc_share = get_package_share_directory('manual_controller')
    oak_share = get_package_share_directory('oak_imu')
    lidar_share = get_package_share_directory('sllidar_ros2')

    return LaunchDescription([
        DeclareLaunchArgument('lidar', default_value='false',
                              description='Start RPLidar A1M8 on ttyUSB1'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(mc_share, 'launch', 'manual_controller.launch.py')),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(oak_share, 'launch', 'oak_imu.launch.py')),
            launch_arguments={'orientation': 'gyro'}.items(),
        ),
        # RPLidar A1M8 — publishes /scan on frame "laser" (matches URDF lidar_mount).
        # ttyUSB1: lidar. ttyUSB0: micro-ROS ESP32.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(lidar_share, 'launch', 'sllidar_a1_launch.py')),
            launch_arguments={
                'serial_port': '/dev/ttyUSB1',
                'frame_id': 'laser',
            }.items(),
            condition=IfCondition(LaunchConfiguration('lidar')),
        ),
    ])
