"""Top-level EyeRobot launch: odometry stack + OAK-D IMU + camera streams.

The single depthai_ros_driver instance owns the OAK-D device and publishes
(RGBD pipeline, see config/depthai_camera.yaml):
  /oak/imu/data           raw accel+gyro (factory-calibrated frame)
  /oak/rgb/image_raw      640x480 @ 10 fps colour feed
  /oak/stereo/image_raw   depth aligned to the RGB frame

IMU chain: /oak/imu/data → imu_remap → /oak/imu/data_raw → Madgwick →
/oak/imu/fused (the topic ekf.yaml's imu0 points at).

Note: depthai_ros_driver opens the OAK-D device exclusively.  Direct depthai SDK
access (detect_lego.py, oak_view.py, perception/lego_vision_node.py) cannot run
simultaneously — vision consumers must subscribe to the /oak/* topics instead
(that is what manual_controller/lego_vision_node.py does, see lego:=true).

Run in its own terminal (or tmux window) — no teleop, no RViz.
Those need a real TTY / separate session:
  ros2 run manual_controller manual_controller   # driving (wasd) + fans (q/e) + belt (r/t)
  rviz2 -d <path>/eyerobot.rviz                  # on PC

(teleop_twist_keyboard also works out of the box — diff_drive_controller's
subscription is remapped to /cmd_vel in manual_controller.launch.py, so
anything publishing /cmd_vel, Nav2 included, drives the wheels directly.)

Optional flags:
  lidar:=true   Start the RPLidar A1M8. Off by default.
  slam:=true    Start SLAM Toolbox (requires lidar:=true). Publishes map→odom TF.
  ekf:=true     Run robot_localization EKF fusing wheel odom + IMU.
                Also set enable_odom_tf: false in diff_drive_controller.yaml
                so the EKF — not diff_drive_controller — owns odom→base_link TF.
  lego:=true    Start the ROS-native Lego vision detector node
                (manual_controller/lego_vision_node.py — subscribes to the
                /oak/rgb + /oak/stereo topics above, publishes
                /eyerobot/vision/lego_target and /eyerobot/vision/lego_markers_map).
  bt:=true      Start the mission behavior tree (autonomous_controller package,
                also runnable as: ros2 run autonomous_controller behavior_tree).
                Needs Nav2 running (nav2.launch.py full_nav:=true); it waits
                for the navigate_through_poses server and then for AMCL
                localization (set the initial pose in Foxglove) before
                starting the mission.
  bt_mission:=full|zone1|zone3|zone4   Mission variant (default full).
                Each zone flag is a partial run of the full flow:
                zone1 = zone 1 collection + unload only (no button, no ramp);
                zone3 = full minus the ramp/zone-4 leg;
                zone4 = full minus the button/door/zone-3 leg.
                Zone 1 cleanup + final unload close every mission.

Full mapping session with vision:
  ros2 launch manual_controller eyerobot.launch.py lidar:=true slam:=true ekf:=true lego:=true

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
                              description='Start the RPLidar A1M8'),
        # /dev/rplidar is the udev symlink (docker/99-eyerobot-usb.rules) that
        # tracks the lidar regardless of ttyUSB enumeration order. Fall back to
        # lidar_port:=/dev/ttyUSBn if the rules are not installed yet.
        DeclareLaunchArgument('lidar_port', default_value='/dev/rplidar',
                              description='RPLidar serial device'),
        DeclareLaunchArgument('slam', default_value='false',
                              description='Run SLAM Toolbox (requires lidar:=true)'),
        DeclareLaunchArgument('ekf', default_value='false',
                              description='Run robot_localization EKF fusing wheel odom + IMU'),
        DeclareLaunchArgument('foxglove', default_value='true',
                              description='Start foxglove_bridge on ws://<jetson-ip>:8765'),
        DeclareLaunchArgument('lego', default_value='false',
                              description='Start the Lego vision detector node'),
        DeclareLaunchArgument('bt', default_value='false',
                              description='Start the mission behavior tree (needs Nav2 running)'),
        DeclareLaunchArgument('bt_mission', default_value='full',
                              description='Mission variant: full | zone1 | zone3 | zone4'),

        # ── Core odometry + ros2_control stack ───────────────────────────────
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(mc_share, 'launch', 'manual_controller.launch.py')),
            launch_arguments={
                'ekf': LaunchConfiguration('ekf'),
            }.items(),
        ),

        # ── OAK-D driver: IMU + RGB + aligned depth (single device owner) ────
        # depthai_ros_driver opens the OAK-D Lite and publishes raw IMU on
        # /oak/imu/data plus the RGBD streams /oak/rgb/image_raw and
        # /oak/stereo/image_raw (configured in depthai_camera.yaml).
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('depthai_ros_driver'), 'launch', 'camera.launch.py'])),
            launch_arguments={
                'params_file': PathJoinSubstitution([
                    FindPackageShare('manual_controller'), 'config', 'depthai_camera.yaml']),
                'camera_model': 'OAK-D-LITE',
                'name': 'oak',
                # Camera TF tree hangs under 'oak_mount' with ZERO offsets:
                # imu_remap publishes base_link -> oak_mount with the
                # gravity-MEASURED mount orientation (+ the translation, its
                # mount_x/y/z params) once IMU calibration finishes. A static
                # cam_pitch here would go stale every time the physical mount
                # is tweaked — measured-at-launch can't. Until calibration
                # (~8 s) the oak frames are a TF island and lego_vision_node
                # drops detections, which is correct: their projection would
                # be garbage anyway.
                'parent_frame': 'oak_mount',
                'cam_pos_x': '0.0',
                'cam_pos_z': '0.0',
                'rectify_rgb': 'false',
            }.items(),
        ),

        # ── IMU pipeline: /oak/imu/data → remap → Madgwick → /oak/imu/fused ──
        # imu_remap: gravity-aligns the ~58°-tilted OAK mount at startup +
        # subtracts gyro bias. Keep the robot STILL for ~2 s after launch until
        # it logs "gyro bias = ...". Sign/tilt handling lives here, in the
        # data: rotating oak_imu_frame in the URDF did not change the yaw rate
        # the EKF integrates (verified on hardware), so TF-level correction
        # was abandoned.
        Node(
            package='manual_controller',
            executable='imu_remap',
            name='imu_remap',
            output='screen',
            parameters=[{
                'input_topic':  '/oak/imu/data',     # raw from depthai driver
                'output_topic': '/oak/imu/data_raw', # REP-103, bias-corrected
                'frame_id':     'imu_link',
                # Camera mount: imu_remap publishes base_link -> oak_mount
                # with the gravity-measured rotation; translation set here
                # (measure axle midpoint -> camera, meters).
                'publish_camera_tf': True,
                'mount_x': 0.42,
                'mount_y': 0.0,
                'mount_z': 0.135,
            }],
        ),

        # imu_filter_madgwick: fuses accel+gyro into orientation.
        # Topic wiring (driver publishes ~/imu/data → /oak/imu/data — NOT /oak/imu):
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
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(lidar_share, 'launch', 'rplidar_a1_launch.py')),
            launch_arguments={
                'serial_port': LaunchConfiguration('lidar_port'),
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

        # ── Lego vision detector ─────────────────────────────────────────────
        # HSV colour detection + centroid tracking on /oak/rgb/image_raw with
        # depth lookup in /oak/stereo/image_raw (RGB-aligned). Publishes the
        # closest target on /eyerobot/vision/lego_target, map-frame markers on
        # /eyerobot/vision/lego_markers_map and an annotated feed on
        # /eyerobot/camera/annotated_image (viewable in Foxglove).
        Node(
            package='manual_controller',
            executable='lego_vision_node',
            name='lego_detector_node',
            output='screen',
            condition=IfCondition(LaunchConfiguration('lego')),
        ),

        # ── Mission behavior tree ─────────────────────────────────────────────
        # Safe to start with the rest of the stack: setup() blocks on the
        # navigate_through_poses action server (so it waits for Nav2 to come
        # up), and the tree's first behavior waits for AMCL localization before
        # sending any goal — set the initial pose in Foxglove and the mission
        # starts on its own.
        Node(
            package='autonomous_controller',
            executable='behavior_tree',
            name='behavior_tree',
            output='screen',
            arguments=['--mission', LaunchConfiguration('bt_mission')],
            condition=IfCondition(LaunchConfiguration('bt')),
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
            parameters=[{'port': 8765, 'capabilities': ['clientPublish', 'services', 'connectionGraph', 'assets']}],
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
