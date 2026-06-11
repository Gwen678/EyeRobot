"""Standalone block-detection test: OAK-D camera + ONE detector, nothing else.

No ros2_control, no IMU pipeline, no EKF/SLAM/Nav2 — for testing the vision
pipeline on its own (bench or robot, motors off):

  ros2 launch manual_controller lego_test.launch.py                  # HSV (default)
  ros2 launch manual_controller lego_test.launch.py detector:=yolo   # onboard YOLOv8

Detectors (both publish the SAME topics, so downstream is detector-agnostic):
  hsv   lego_vision_node — host-side HSV colour segmentation + depth lookup
        on /oak/rgb + /oak/stereo.
  yolo  the trained YOLOv8n block model running ON THE OAK's Myriad X VPU
        (depthai YoloSpatialDetectionNetwork): detection + depth association
        on-device, yolo_vision_node only bridges
        /oak/nn/spatial_detections to the eyerobot topics. Blob:
        share/perception/models/best.blob; conf 0.7 (DEPLOY_OAK.md).
        ⚠ DEPLOY_OAK.md warns the bundled blob was compiled from the raw
        ultralytics ONNX head. If YOLO mode gives zero/garbage detections,
        regenerate blob+JSON at https://tools.luxonis.com from best.pt
        (input 416, OAK-D Lite 6 SHAVEs) and replace
        ros2_ws/src/perception/best.blob, then rebuild perception.

What works without the rest of the stack:
  /eyerobot/camera/annotated_image   detections on the RGB feed (Foxglove,
                                     ws://<jetson-ip>:8765 — bridge starts here)
  /eyerobot/vision/lego_target       closest block, CAMERA OPTICAL frame
                                     (x right, y down, z forward, meters):
                                     ros2 topic echo /eyerobot/vision/lego_target
What does NOT work standalone (and is expected to):
  /eyerobot/vision/lego_markers_map  needs the map TF (SLAM + mount
                                     calibration) — both nodes log a throttled
                                     "map TF unavailable" warning and drop
                                     map-frame output only.

Flags:
  detector:=hsv|yolo   which detector (default hsv)
  foxglove:=false      skip the Foxglove bridge (e.g. already running)
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


def _write_nn_config(context):
    """Generate the NN config JSON + camera yaml for detector:=yolo.
    Confidence/input size are constants in nn_config.py, not flags."""
    if context.launch_configurations.get('detector') != 'yolo':
        return []
    write_yolo_configs()
    return []


def generate_launch_description():
    detector = LaunchConfiguration('detector')
    is_hsv = IfCondition(PythonExpression(["'", detector, "' == 'hsv'"]))
    is_yolo = IfCondition(PythonExpression(["'", detector, "' == 'yolo'"]))

    return LaunchDescription([
        DeclareLaunchArgument('detector', default_value='yolo',
                              description='Block detector: yolo (onboard OAK NN) or hsv (host). '
                                          'Confidence/input size: constants in nn_config.py.'),
        DeclareLaunchArgument('foxglove', default_value='true',
                              description='Start foxglove_bridge on ws://<jetson-ip>:8765'),

        OpaqueFunction(function=_write_nn_config),

        # OAK-D driver. Same base yaml as the full stack (RGBD @ 5 fps);
        # the yolo variant adds the onboard spatial NN on top. parent_frame
        # is left at the driver default: without imu_remap there is no
        # oak_mount frame, and a TF island is fine for camera-frame testing.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('depthai_ros_driver'), 'launch', 'camera.launch.py'])),
            launch_arguments={
                # yolo: the /tmp yaml written by _write_nn_config (preview
                # size matched to the blob); hsv: the packaged production yaml.
                'params_file': PythonExpression([
                    "'", CAMERA_YAML_PATH, "' if '", detector, "' == 'yolo' else '",
                    os.path.join(get_package_share_directory('manual_controller'),
                                 'config', 'depthai_camera.yaml'), "'"]),
                'camera_model': 'OAK-D-LITE',
                'name': 'oak',
                'rectify_rgb': 'false',
            }.items(),
        ),

        Node(
            package='manual_controller',
            executable='lego_vision_node',
            name='lego_detector_node',
            output='screen',
            condition=is_hsv,
        ),

        Node(
            package='manual_controller',
            executable='yolo_vision_node',
            name='lego_detector_node',
            output='screen',
            condition=is_yolo,
        ),

        Node(
            package='foxglove_bridge',
            executable='foxglove_bridge',
            name='foxglove_bridge',
            output='screen',
            parameters=[{'port': 8765, 'capabilities': ['clientPublish', 'services', 'connectionGraph', 'assets']}],
            condition=IfCondition(LaunchConfiguration('foxglove')),
        ),
    ])
