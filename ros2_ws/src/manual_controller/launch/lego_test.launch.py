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
import json
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

# depthai_camera_yolo.yaml points nn.i_nn_config_path here; written at launch
# so the blob path always tracks the perception package's install space.
NN_CONFIG_PATH = "/tmp/eyerobot_yolo_nn.json"


def _write_nn_config(context):
    """Generate the YoloDetectionNetwork config JSON for detector:=yolo."""
    if context.launch_configurations.get('detector') != 'yolo':
        return []
    blob = os.path.join(get_package_share_directory('perception'), 'models', 'best.blob')
    if not os.path.isfile(blob):
        raise RuntimeError(
            f"YOLO blob not found at {blob} — build the perception package "
            "(colcon build --packages-select perception)")
    config = {
        "model": {"zoo": "path", "model_name": blob},
        "nn_config": {
            "output_format": "detection",
            "NN_family": "YOLO",
            "input_size": "416x416",
            "confidence_threshold": 0.7,     # DEPLOY_OAK.md eval sweep
            "NN_specific_metadata": {
                "classes": 1,
                "coordinates": 4,
                "anchors": [],               # YOLOv8 is anchor-free
                "anchor_masks": {},
                "iou_threshold": 0.5,
                "confidence_threshold": 0.7,
            },
        },
        "mappings": {"labels": ["block"]},
    }
    with open(NN_CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    return []


def generate_launch_description():
    detector = LaunchConfiguration('detector')
    is_hsv = IfCondition(PythonExpression(["'", detector, "' == 'hsv'"]))
    is_yolo = IfCondition(PythonExpression(["'", detector, "' == 'yolo'"]))

    return LaunchDescription([
        DeclareLaunchArgument('detector', default_value='hsv',
                              description='Block detector: hsv (host) or yolo (onboard OAK NN)'),
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
                'params_file': PathJoinSubstitution([
                    FindPackageShare('manual_controller'), 'config',
                    PythonExpression(["'depthai_camera_yolo.yaml' if '", detector,
                                      "' == 'yolo' else 'depthai_camera.yaml'"])]),
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
