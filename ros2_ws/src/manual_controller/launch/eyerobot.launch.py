"""Top-level EyeRobot launch: odometry stack + OAK-D IMU.

Composes manual_controller.launch.py (state_estimator, dual_odometry, URDF/TF,
optional EKF) with oak_imu.launch.py (BMI270 gyro → /oak/imu/data_raw).

Run in its own terminal (or tmux window) — no teleop, no RViz.
Those need a real TTY / separate session:
  ros2 run manual_controller manual_controller   # wasd
  rviz2 -d <path>/eyerobot.rviz                  # on PC

Optional flags:
  lidar:=true   Start the RPLidar A1M8 (ttyUSB1). Off by default.
  slam:=true    Start SLAM Toolbox (requires lidar:=true). Publishes map→odom TF.
                Combine with ekf:=true for IMU-fused odometry under the map.

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
    oak_share = get_package_share_directory('oak_imu')
    lidar_share = get_package_share_directory('rplidar_ros')

    return LaunchDescription([
        DeclareLaunchArgument('tracker', default_value='false',
                              description='Start block tracker FSM (requires camera.py running separately)'),
        DeclareLaunchArgument('lidar', default_value='false',
                              description='Start RPLidar A1M8 on ttyUSB0'),
        DeclareLaunchArgument('slam', default_value='false',
                              description='Run SLAM Toolbox (requires lidar:=true). '
                                          'Publishes map→odom TF for full localization.'),
        DeclareLaunchArgument('ekf', default_value='false',
                              description='Run the robot_localization EKF fusing wheel odom + IMU'),
        DeclareLaunchArgument('cmd_vel_bridge', default_value='false',
                              description='Bridge /cmd_vel (Nav2) to motor wheel commands'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(mc_share, 'launch', 'manual_controller.launch.py')),
            launch_arguments={
                'ekf':            LaunchConfiguration('ekf'),
                'cmd_vel_bridge': LaunchConfiguration('cmd_vel_bridge'),
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(oak_share, 'launch', 'oak_imu.launch.py')),
            launch_arguments={'orientation': 'gyro'}.items(),
        ),

        # RPLidar A1M8 — publishes /scan on frame "laser" (matches URDF lidar_mount).
        # ttyUSB0: lidar. ttyUSB1: micro-ROS ESP32.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(lidar_share, 'launch', 'rplidar_a1_launch.py')),
            launch_arguments={
                'serial_port': '/dev/ttyUSB0',
                'frame_id': 'laser',
            }.items(),
            condition=IfCondition(LaunchConfiguration('lidar')),
        ),

        # Block tracker FSM — subscribes to /eyerobot/vision/lego_target + /scan,
        # publishes /motor_*wheel_cmd + /block_tracker/* debug topics.
        # Run camera.py separately to provide the vision detections.
        Node(
            package='manual_controller',
            executable='block_tracker',
            name='block_tracker',
            output='screen',
            condition=IfCondition(LaunchConfiguration('tracker')),
        ),

        # SLAM Toolbox (online async) — subscribes to /scan and odom→base_link TF,
        # builds a map, and publishes map→odom TF.
        # Requires: lidar:=true (for /scan) + odom→base_link (ekf:=true or default
        # state_estimator TF). TF chain: map → odom → base_link → laser.
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
