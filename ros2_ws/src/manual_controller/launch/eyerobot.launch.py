"""Top-level EyeRobot launch: odometry stack + OAK-D IMU + camera streams.

Flags: lidar, slam, ekf, lego (detector:=yolo|hsv), bt, foxglove, tracker.
IMU chain: /oak/imu/data to imu_remap to /oak/imu/data_raw to Madgwick to /oak/imu/fused.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from manual_controller.nn_config import write_yolo_configs, CAMERA_YAML_PATH


def _yolo_active(context):
    """The NN camera pipeline runs only when vision is on AND flavour is yolo."""
    return (context.launch_configurations.get('lego', 'false').lower() == 'true'
            and context.launch_configurations.get('detector') == 'yolo')


def _maybe_write_yolo_configs(context):
    """lego:=true detector:=yolo -> generate the NN json + camera yaml.
    Confidence/input size are constants in nn_config.py, not flags."""
    if not _yolo_active(context):
        return []
    write_yolo_configs()
    return []


def generate_launch_description():
    mc_share = get_package_share_directory('manual_controller')
    lidar_share = get_package_share_directory('rplidar_ros')

    return LaunchDescription([
        DeclareLaunchArgument('tracker', default_value='false',
                              description='Start block tracker FSM'),
        DeclareLaunchArgument('lidar', default_value='false',
                              description='Start the RPLidar A1M8'),
        # /dev/rplidar is the udev symlink that tracks the lidar regardless of ttyUSB order.
        # Use lidar_port:=/dev/ttyUSBn if the udev rules are not installed.
        DeclareLaunchArgument('lidar_port', default_value='/dev/rplidar',
                              description='RPLidar serial device'),
        DeclareLaunchArgument('slam', default_value='false',
                              description='Run SLAM Toolbox (requires lidar:=true)'),
        DeclareLaunchArgument('ekf', default_value='false',
                              description='Run robot_localization EKF fusing wheel odom + IMU'),
        DeclareLaunchArgument('foxglove', default_value='true',
                              description='Start foxglove_bridge on ws://<jetson-ip>:8765'),
        DeclareLaunchArgument('lego', default_value='false',
                              description='Start the block vision detector node'),
        DeclareLaunchArgument('detector', default_value='yolo',
                              description='Block detector flavour (with lego:=true): '
                                          'yolo = onboard OAK NN (yolo_vision_node), '
                                          'hsv = host-side colour segmentation (lego_vision_node). '
                                          'detector:=yolo also switches the camera to the NN pipeline. '
                                          'Confidence/input size: constants in nn_config.py.'),

        # lego:=true detector:=yolo: write /tmp NN json + camera yaml
        # before the camera include resolves its params_file.
        OpaqueFunction(function=_maybe_write_yolo_configs),
        DeclareLaunchArgument('bt', default_value='false',
                              description='Start the mission behavior tree (needs Nav2 running)'),

        # Core odometry + ros2_control stack
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(mc_share, 'launch', 'manual_controller.launch.py')),
            launch_arguments={
                'ekf': LaunchConfiguration('ekf'),
            }.items(),
        ),

        # OAK-D driver: IMU + RGB + aligned depth (single device owner)
        # Publishes /oak/imu/data, /oak/rgb/image_raw, /oak/stereo/image_raw.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('depthai_ros_driver'), 'launch', 'camera.launch.py'])),
            launch_arguments={
                # lego:=true detector:=yolo: use the generated /tmp yaml (NN pipeline);
                # otherwise use the production camera yaml.
                'params_file': PythonExpression([
                    "'", CAMERA_YAML_PATH, "' if ('",
                    LaunchConfiguration('lego'), "'.lower() == 'true' and '",
                    LaunchConfiguration('detector'), "' == 'yolo') else '",
                    os.path.join(get_package_share_directory('manual_controller'),
                                 'config', 'depthai_camera.yaml'), "'"]),
                'camera_model': 'OAK-D-LITE',
                'name': 'oak',
                # Camera TF hangs under 'oak_mount' with zero offsets.
                # imu_remap sets the measured mount orientation at startup (~8 s calibration).
                'parent_frame': 'oak_mount',
                'cam_pos_x': '0.0',
                'cam_pos_z': '0.0',
                'rectify_rgb': 'false',
            }.items(),
        ),

        # IMU pipeline: /oak/imu/data to remap to Madgwick to /oak/imu/fused
        # imu_remap corrects the ~58 deg tilted OAK mount and subtracts gyro bias at startup.
        Node(
            package='manual_controller',
            executable='imu_remap',
            name='imu_remap',
            output='screen',
            parameters=[{
                'input_topic':  '/oak/imu/data',     # raw from depthai driver
                'output_topic': '/oak/imu/data_raw', # REP-103 bias-corrected
                'frame_id':     'imu_link',
                # imu_remap publishes base_link to oak_mount with the measured rotation.
                # Translation set here (axle midpoint to camera, meters).
                'publish_camera_tf': True,
                # With name 'oak' the body frame is 'oak' (child of oak_mount).
                # Not 'oak-d-base-frame' and not 'oak-d_frame'.
                'camera_base_frame': 'oak',
                'mount_x': 0.42,
                'mount_y': 0.0,
                'mount_z': 0.135,
            }],
        ),

        # imu_filter_madgwick: fuses accel+gyro into orientation.
        # Input: /oak/imu/data_raw; output remapped to /oak/imu/fused (avoids collision with driver).
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

        # RPLidar A1M8
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(lidar_share, 'launch', 'rplidar_a1_launch.py')),
            launch_arguments={
                'serial_port': LaunchConfiguration('lidar_port'),
                'frame_id': 'laser',
            }.items(),
            condition=IfCondition(LaunchConfiguration('lidar')),
        ),

        # Block tracker FSM
        Node(
            package='manual_controller',
            executable='block_tracker',
            name='block_tracker',
            output='screen',
            condition=IfCondition(LaunchConfiguration('tracker')),
        ),

        # Lego vision detector (HSV)
        # Publishes /eyerobot/vision/lego_target, lego_markers_map, and annotated_image.
        Node(
            package='manual_controller',
            executable='lego_vision_node',
            name='lego_detector_node',
            output='screen',
            condition=IfCondition(PythonExpression([
                "'", LaunchConfiguration('lego'), "'.lower() == 'true' and '",
                LaunchConfiguration('detector'), "' == 'hsv'"])),
        ),

        # Onboard YOLO bridge: converts /oak/nn/spatial_detections to /eyerobot/vision/* topics
        # so BlockMemory/BT are detector-agnostic.
        Node(
            package='manual_controller',
            executable='yolo_vision_node',
            name='lego_detector_node',
            output='screen',
            condition=IfCondition(PythonExpression([
                "'", LaunchConfiguration('lego'), "'.lower() == 'true' and '",
                LaunchConfiguration('detector'), "' == 'yolo'"])),
        ),

        # Mission behavior tree
        # Waits for Nav2 and AMCL before sending goals; AMCL self-initializes at the base pose.
        Node(
            package='autonomous_controller',
            executable='behavior_tree',
            name='behavior_tree',
            output='screen',
            arguments=[],
            condition=IfCondition(LaunchConfiguration('bt')),
        ),

        # Foxglove bridge
        # WebSocket server for Foxglove Studio (ws://<jetson-ip>:8765).
        Node(
            package='foxglove_bridge',
            executable='foxglove_bridge',
            name='foxglove_bridge',
            output='screen',
            parameters=[{'port': 8765, 'capabilities': ['clientPublish', 'services', 'connectionGraph', 'assets']}],
            condition=IfCondition(LaunchConfiguration('foxglove')),
        ),

        # SLAM Toolbox
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
