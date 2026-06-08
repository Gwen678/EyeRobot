"""Top-level EyeRobot launch: odometry stack + OAK-D IMU.

Composes manual_controller.launch.py (state_estimator, dual_odometry, URDF/TF,
optional EKF) with oak_imu.launch.py (BMI270 gyro → /oak/imu/data_raw).

Run in its own terminal (or tmux window) — no teleop, no RViz.
Those need a real TTY / separate session:
  ros2 run manual_controller manual_controller   # wasd
  rviz2 -d <path>/eyerobot.rviz                  # on PC
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    mc_share = get_package_share_directory('manual_controller')
    oak_share = get_package_share_directory('oak_imu')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(mc_share, 'launch', 'manual_controller.launch.py')),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(oak_share, 'launch', 'oak_imu.launch.py')),
            launch_arguments={'orientation': 'gyro'}.items(),
        ),
    ])
