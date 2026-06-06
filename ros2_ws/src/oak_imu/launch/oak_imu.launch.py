#!/usr/bin/env python3
"""Launch the OAK-D Lite IMU publisher, optionally with the standalone cube view.

Publishes sensor_msgs/Imu on /oak/imu/data_raw (consumed by dual_odometry and the
EKF in manual_controller). Set rviz:=true for the standalone rotating-cube view.

broadcast_tf (default false): off for robot use — base_link->imu_link is a static
URDF mount and the orientation is consumed from the message, so the node must NOT
also publish world->imu_link (that would give imu_link two parents and break the
EKF's frame lookup). Set broadcast_tf:=true only for the standalone cube demo.
For the EKF use orientation:=complementary (gravity-referenced roll/pitch = ramps).
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    rviz_config = os.path.join(
        get_package_share_directory('oak_imu'), 'rviz', 'imu_cube.rviz')
    orientation = LaunchConfiguration('orientation')
    broadcast_tf = LaunchConfiguration('broadcast_tf')

    return LaunchDescription([
        DeclareLaunchArgument('orientation', default_value='gyro',
                              description='gyro | accel | complementary'),
        DeclareLaunchArgument('rviz', default_value='false',
                              description='Start the standalone IMU cube RViz view'),
        DeclareLaunchArgument('broadcast_tf', default_value='false',
                              description='Publish world->imu_link TF (standalone '
                                          'cube only; keep false on the robot)'),
        # Robot use: suppress the dynamic world->imu_link TF.
        Node(
            package='oak_imu',
            executable='oak_imu_cube',
            name='oak_imu_cube',
            output='screen',
            arguments=['--orientation', orientation, '--no-tf'],
            condition=UnlessCondition(broadcast_tf),
        ),
        # Standalone cube demo: broadcast the TF so the cube rotates.
        Node(
            package='oak_imu',
            executable='oak_imu_cube',
            name='oak_imu_cube',
            output='screen',
            arguments=['--orientation', orientation],
            condition=IfCondition(broadcast_tf),
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
