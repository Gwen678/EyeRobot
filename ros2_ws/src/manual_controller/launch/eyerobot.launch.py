"""Top-level EyeRobot launch: odometry stack + OAK-D IMU.

IMU pipeline (replaces custom oak_imu package):
  depthai_ros_driver  → /oak/imu/data  (raw accel+gyro, factory-calibrated frame)
  imu_filter_madgwick → /oak/imu/fused (orientation from Madgwick filter)

Note: depthai_ros_driver opens the OAK-D device exclusively.  Direct depthai SDK
access (detect_lego.py, oak_view.py) cannot run simultaneously — same as the old
oak_imu_cube.py which also held the device open.

Run in its own terminal (or tmux window) — no teleop, no RViz.
Those need a real TTY / separate session:
  ros2 run manual_controller manual_controller   # driving (wasd) + fans (q/e) + belt (r/t)
  rviz2 -d <path>/eyerobot.rviz                  # on PC

(teleop_twist_keyboard also works, but needs a remap — diff_drive_controller
listens on /diff_drive_controller/cmd_vel_unstamped, not /cmd_vel:
  ros2 run teleop_twist_keyboard teleop_twist_keyboard \\
    --ros-args -r cmd_vel:=/diff_drive_controller/cmd_vel_unstamped)

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
        DeclareLaunchArgument('foxglove', default_value='true',
                              description='Start foxglove_bridge on ws://<jetson-ip>:8765'),

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
                # Attach the camera's TF tree (oak-d-base-frame → oak → ...) to
                # the robot: oak_state_publisher then publishes
                # base_link → oak-d-base-frame at the mount pose (same offsets
                # as imu_link in Robot.xacro). Without this the oak frames are
                # an island with no path to odom.
                'parent_frame': 'base_link',
                'cam_pos_x': '0.42',
                'cam_pos_z': '0.135',
                # No image_proc rectify component: RGB streams are disabled
                # (IMU only), the rectify node would just advertise dead
                # /oak/rgb/image_rect* topics.
                'rectify_rgb': 'false',
            }.items(),
        ),

        # imu_filter_madgwick: fuses depthai_ros_driver accel+gyro into orientation.
        # depthai_ros_driver already applies the device factory calibration (IMU→camera
        # extrinsics), so no manual axis remap is needed.  Verify on first boot:
        #   ros2 topic echo /oak/imu --once
        # while the robot is flat: accel_z should be ~+9.81 m/s² and angular_velocity.z
        # should increase counter-clockwise (yaw left = positive).  If wrong, the
        # imu_remap_node in manual_controller/imu_remap_node.py can be re-added.
        #
        # imu_remap: sign correction (gyro/accel y,z negated — the BMI270 is
        # mounted 180° about X) + startup gyro-bias subtraction. Keep the robot
        # STILL for ~2 s after launch until it logs "gyro bias = ...".
        # Sign handling lives here, in the data: rolling oak_imu_frame by pi in
        # the URDF did not flip the yaw rate the EKF integrates (verified on
        # hardware), so TF-level correction was abandoned.
        Node(
            package='manual_controller',
            executable='imu_remap',
            name='imu_remap',
            output='screen',
            parameters=[{
                'input_topic':  '/oak/imu/data',     # raw from depthai driver
                'output_topic': '/oak/imu/data_raw', # REP-103, bias-corrected
                'frame_id':     'imu_link',
            }],
        ),

        # Topic wiring (driver publishes ~/imu/data → /oak/imu/data, verified in
        # depthai-ros 2.7.5 imu.cpp — NOT /oak/imu):
        #   input : imu/data_raw = /oak/imu/data_raw (from imu_remap above)
        #   output: imu/data     → /oak/imu/fused (remapped! the default
        #           /oak/imu/data would collide with the driver's raw topic)
        # ekf.yaml imu0 must point at /oak/imu/fused.
        Node(
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            name='imu_filter_madgwick_node',
            namespace='oak',
            output='screen',
            parameters=[PathJoinSubstitution([
                FindPackageShare('manual_controller'), 'config', 'imu_filter.yaml'])],
            remappings=[('imu/data', 'imu/fused')],
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

        # ── Foxglove bridge ───────────────────────────────────────────────────
        # WebSocket server for Foxglove Studio on the PC (ws://<jetson-ip>:8765).
        # urdf_relay (manual_controller.launch.py) republishes /robot_description
        # as VOLATILE on /robot_description_volatile for the Foxglove URDF panel.
        Node(
            package='foxglove_bridge',
            executable='foxglove_bridge',
            name='foxglove_bridge',
            output='screen',
            parameters=[{'port': 8765}],
            condition=IfCondition(LaunchConfiguration('foxglove')),
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
