"""Nav2 localization + navigation for EyeRobot.

Run AFTER the main stack (eyerobot.launch.py) is up:
  ros2 launch manual_controller nav2.launch.py
  ros2 launch manual_controller nav2.launch.py map:=/eyerobot/ros2_ws/maps/map_fermee_sans_tapis.yaml

Brings up:
  - map_server        (serves the saved .pgm map)
  - amcl              (localises on map -> publishes map->odom TF)
  - planner_server    (global path planning)
  - controller_server (local DWB controller -> /cmd_vel)
  - recoveries_server (spin / backup / wait behaviours)
  - bt_navigator      (behaviour tree action server)
  - lifecycle managers (autostart all of the above)

Prerequisites:
  - eyerobot.launch.py running (EKF, lidar, URDF)
  - /scan publishing (RPLidar on ttyUSB1)
  - /odometry/filtered publishing (EKF with ekf:=true)
  - odom->base_link TF from EKF
  - base_link->laser TF from URDF
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    mc_share = get_package_share_directory('manual_controller')
    params_file = os.path.join(mc_share, 'config', 'nav2_params.yaml')
    default_map = os.path.join('/eyerobot/ros2_ws/maps', 'map.yaml')

    map_arg = DeclareLaunchArgument(
        'map', default_value=default_map,
        description='Full path to the map yaml file')
    map_path = LaunchConfiguration('map')

    return LaunchDescription([
        map_arg,

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[params_file, {'yaml_filename': map_path}],
        ),
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[params_file],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[params_file],
        ),
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[params_file],
        ),
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[params_file],
            remappings=[('cmd_vel', '/cmd_vel')],
        ),
        Node(
            package='nav2_recoveries',
            executable='recoveries_server',
            name='recoveries_server',
            output='screen',
            parameters=[params_file],
        ),
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[params_file],
        ),
        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[params_file],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[params_file],
        ),
    ])
