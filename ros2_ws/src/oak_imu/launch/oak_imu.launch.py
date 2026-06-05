#!/usr/bin/env python3
"""Launch the OAK-D Lite IMU publisher, optionally with the standalone cube view.

Publishes sensor_msgs/Imu on /oak/imu/data_raw (consumed by the dual_odometry
comparison in manual_controller). Set rviz:=true for the standalone rotating-cube
RViz view; leave it false when running inside the main EyeRobot RViz.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    rviz_config = os.path.join(
        get_package_share_directory('oak_imu'), 'rviz', 'imu_cube.rviz')
    orientation = LaunchConfiguration('orientation')

    return LaunchDescription([
        DeclareLaunchArgument('orientation', default_value='gyro',
                              description='gyro | accel | complementary'),
        DeclareLaunchArgument('rviz', default_value='false',
                              description='Start the standalone IMU cube RViz view'),
        Node(
            package='oak_imu',
            executable='oak_imu_cube',
            name='oak_imu_cube',
            output='screen',
            arguments=['--orientation', orientation],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2_oak_imu',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('rviz')),
            output='screen',
        ),
    ])
