"""Nav2 localization and optional full navigation for EyeRobot.

Wraps nav2_bringup launch files (localization_launch.py and navigation_launch.py).
Run AFTER: ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true
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
    nav2_share = get_package_share_directory('nav2_bringup')

    params_file = os.path.join(mc_share, 'config', 'nav2_params.yaml')
    default_map  = '/eyerobot/ros2_ws/maps/clean_room_8x8.yaml'

    localization_launch = os.path.join(nav2_share, 'launch', 'localization_launch.py')
    navigation_launch   = os.path.join(nav2_share, 'launch', 'navigation_launch.py')

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Full path to the .yaml map file'),
        DeclareLaunchArgument('full_nav', default_value='false',
                              description='Add global planner + local controller '
                                          '(requires /cmd_vel relay to diff_drive_controller)'),

        # AMCL + map_server
        # nav2_bringup/localization_launch.py manages map_server and amcl via the Nav2 lifecycle manager.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(localization_launch),
            launch_arguments={
                'map':           LaunchConfiguration('map'),
                'params_file':   params_file,
                'use_sim_time':  'false',
                'autostart':     'true',
            }.items(),
        ),

        # Full navigation stack
        # nav2_bringup/navigation_launch.py adds controller_server, planner_server, bt_navigator, and others.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(navigation_launch),
            launch_arguments={
                'params_file':  params_file,
                'use_sim_time': 'false',
                'autostart':    'true',
            }.items(),
            condition=IfCondition(LaunchConfiguration('full_nav')),
        ),
    ])
