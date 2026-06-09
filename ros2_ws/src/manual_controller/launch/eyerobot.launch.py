"""Top-level EyeRobot launch: odometry stack + OAK-D IMU.

IMU pipeline (replaces custom oak_imu package):
  depthai_ros_driver → /oak/imu (raw, sensor frame)
  imu_remap          → /oak/imu/data_raw (axis-corrected, REP-103 frame)
  imu_filter_madgwick→ /oak/imu/data (orientation from Madgwick filter)

Note: depthai_ros_driver opens the OAK-D device exclusively.  Direct depthai SDK
access (detect_lego.py, oak_view.py) cannot run simultaneously — same as the old
oak_imu_cube.py which also held the device open.

Run in its own terminal (or tmux window) — no teleop, no RViz.
Those need a real TTY / separate session:
  ros2 run teleop_twist_keyboard teleop_twist_keyboard   # driving
  ros2 run manual_controller manual_controller           # fans/belt
  rviz2 -d <path>/eyerobot.rviz                          # on PC

Optional flags:
  lidar:=true   Start the RPLidar A1M8. Off by default.
  slam:=true    Start SLAM Toolbox (requires lidar:=true). Publishes map→odom TF.
  ekf:=true     Run robot_localization EKF fusing wheel odom + IMU.
                Also set enable_odom_tf: false in diff_drive_controller.yaml
                so the EKF — not diff_drive_controller — owns odom→base_link TF.

Full mapping session:
  ros2 launch manual_controller eyerobot.launch.py lidar:=true slam:=true ekf:=true

Save map after driving:
  ros2 run nav2_map_server map_saver_cli -f ~/map
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    mc_share = get_package_share_directory('manual_controller')
    lidar_share = get_package_share_directory('rplidar_ros')

    return LaunchDescription([
        DeclareLaunchArgument('tracker', default_value='false',
                              description='Start block tracker FSM'),
        DeclareLaunchArgument('lidar', default_value='false',
                              description='Start RPLidar A1M8 on ttyUSB0'),
        DeclareLaunchArgument('slam', default_value='false',
                              description='Run SLAM Toolbox (requires lidar:=true)'),
        DeclareLaunchArgument('ekf', default_value='false',
                              description='Run robot_localization EKF fusing wheel odom + IMU'),

        # ── Core odometry + ros2_control stack ───────────────────────────────
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(mc_share, 'launch', 'manual_controller.launch.py')),
            launch_arguments={
                'ekf': LaunchConfiguration('ekf'),
            }.items(),
        ),

        # ── IMU pipeline: depthai_ros_driver → remap → Madgwick ──────────────
        # depthai_ros_driver: opens the OAK-D Lite and publishes raw IMU on /oak/imu.
        # Camera streams are disabled in depthai_camera.yaml (IMU only).
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('depthai_ros_driver'), 'launch', 'camera.launch.py'])),
            launch_arguments={
                'params_file': PathJoinSubstitution([
                    FindPackageShare('manual_controller'), 'config', 'depthai_camera.yaml']),
                'camera_model': 'OAK-D-LITE',
                'name': 'oak',
            }.items(),
        ),

        # imu_remap: applies accel/gyro sign correction (180° about X) so values
        # are in REP-103 frame.  input_topic must match what depthai_ros_driver
        # actually publishes — check with `ros2 topic list | grep oak` after launch.
        # Some depthai-ros versions publish to /oak/imu, others to /oak/imu/data.
        Node(
            package='manual_controller',
            executable='imu_remap',
            name='imu_remap',
            output='screen',
            respawn=True,
            respawn_delay=3.0,
            parameters=[{
                'accel_signs':  [1.0, -1.0, -1.0],
                'gyro_signs':   [1.0, -1.0, -1.0],
                'input_topic':  '/oak/imu',        # adjust if depthai-ros uses /oak/imu/data
                'output_topic': '/oak/imu/data_raw',
                'frame_id':     'imu_link',
            }],
        ),

        # imu_filter_madgwick: fuses corrected accel + gyro into an orientation
        # estimate.  Runs in /oak namespace so imu/data_raw → /oak/imu/data_raw
        # and imu/data → /oak/imu/data automatically.
        Node(
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            name='imu_filter_madgwick_node',
            namespace='oak',
            output='screen',
            parameters=[PathJoinSubstitution([
                FindPackageShare('manual_controller'), 'config', 'imu_filter.yaml'])],
        ),

        # ── RPLidar A1M8 ─────────────────────────────────────────────────────
        # ttyUSB0: lidar.  ttyUSB1: micro-ROS ESP32.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(lidar_share, 'launch', 'rplidar_a1_launch.py')),
            launch_arguments={
                'serial_port': '/dev/ttyUSB0',
                'frame_id': 'laser',
            }.items(),
            condition=IfCondition(LaunchConfiguration('lidar')),
        ),

        # ── Block tracker FSM ─────────────────────────────────────────────────
        Node(
            package='manual_controller',
            executable='block_tracker',
            name='block_tracker',
            output='screen',
            condition=IfCondition(LaunchConfiguration('tracker')),
        ),

        # ── SLAM Toolbox ──────────────────────────────────────────────────────
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[PathJoinSubstitution([
                FindPackageShare('manual_controller'), 'config', 'slam_toolbox_params.yaml'])],
            condition=IfCondition(LaunchConfiguration('slam')),
        ),
    ])
