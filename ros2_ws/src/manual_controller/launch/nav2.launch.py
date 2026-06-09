"""Nav2 localization + (optional) navigation for EyeRobot.

Wraps the official nav2_bringup launch files instead of instantiating nodes
manually — more robust lifecycle management, battle-tested parameter loading.

Run AFTER: ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true

Localization only (AMCL → map->odom TF, you drive manually):
  ros2 launch manual_controller nav2.launch.py

Full navigation stack (adds global planner + local DWB controller):
  ros2 launch manual_controller nav2.launch.py full_nav:=true

Choose a map:
  ros2 launch manual_controller nav2.launch.py \\
    map:=/eyerobot/ros2_ws/maps/map_fermee_sans_tapis.yaml

Available maps (inside the container):
  /eyerobot/ros2_ws/maps/map.yaml
  /eyerobot/ros2_ws/maps/map_fermee_sans_tapis.yaml
  /eyerobot/ros2_ws/maps/map_ouverte_sans_tapis.yaml

On startup AMCL initialises at (0,0,0). If the robot is elsewhere, publish an
initial pose via Foxglove (/initialpose) or the 2D Pose Estimate tool.

NOTE: full_nav:=true publishes /cmd_vel (Twist), but diff_drive_controller
subscribes to /diff_drive_controller/cmd_vel_unstamped. Bridge it before
autonomous navigation actually moves the robot, e.g.:
  ros2 run topic_tools relay /cmd_vel /diff_drive_controller/cmd_vel_unstamped
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
    default_map  = '/eyerobot/ros2_ws/maps/map.yaml'

    localization_launch = os.path.join(nav2_share, 'launch', 'localization_launch.py')
    navigation_launch   = os.path.join(nav2_share, 'launch', 'navigation_launch.py')

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Full path to the .yaml map file'),
        DeclareLaunchArgument('full_nav', default_value='false',
                              description='Add global planner + local controller '
                                          '(requires /cmd_vel relay to diff_drive_controller)'),

        # ── AMCL + map_server ─────────────────────────────────────────────────
        # nav2_bringup/localization_launch.py manages map_server + amcl via the
        # Nav2 lifecycle manager. Publishes map->odom TF from /scan + /map.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(localization_launch),
            launch_arguments={
                'map':           LaunchConfiguration('map'),
                'params_file':   params_file,
                'use_sim_time':  'false',
                'autostart':     'true',
            }.items(),
        ),

        # ── Full navigation stack ─────────────────────────────────────────────
        # nav2_bringup/navigation_launch.py adds controller_server,
        # planner_server, behavior_server, bt_navigator, waypoint_follower.
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
