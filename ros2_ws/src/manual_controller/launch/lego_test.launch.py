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

import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

# depthai_camera_yolo.yaml points nn.i_nn_config_path here; both files are
# written at launch so the blob path tracks the perception install space and
# the preview size tracks yolo_input.
NN_CONFIG_PATH = "/tmp/eyerobot_yolo_nn.json"
CAMERA_YAML_PATH = "/tmp/eyerobot_camera_yolo.yaml"


def _write_nn_config(context):
    """Generate the NN config JSON + camera yaml for detector:=yolo.

    The driver aborts unless the RGB preview size equals the blob's input
    size exactly (nn.i_disable_resize), so both files must agree — they are
    derived here from the single yolo_input argument: 640 for the bundled
    best.blob, 416 for a blob exported from the duplo_yolov8n_416 run.
    """
    if context.launch_configurations.get('detector') != 'yolo':
        return []
    blob = os.path.join(get_package_share_directory('perception'), 'models', 'best.blob')
    if not os.path.isfile(blob):
        raise RuntimeError(
            f"YOLO blob not found at {blob} — build the perception package "
            "(colcon build --packages-select perception)")
    conf = float(context.launch_configurations.get('yolo_conf', '0.7'))
    size = int(context.launch_configurations.get('yolo_input', '640'))

    config = {
        "model": {"zoo": "path", "model_name": blob},
        "nn_config": {
            "output_format": "detection",
            "NN_family": "YOLO",
            "input_size": f"{size}x{size}",
            "confidence_threshold": conf,
            "NN_specific_metadata": {
                "classes": 1,
                "coordinates": 4,
                "anchors": [],               # YOLOv8 is anchor-free
                "anchor_masks": {},
                "iou_threshold": 0.5,
                "confidence_threshold": conf,
            },
        },
        "mappings": {"labels": ["block"]},
    }
    with open(NN_CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

    # Camera yaml: the packaged depthai_camera_yolo.yaml with the preview
    # size rewritten to match the blob (single source of truth for the
    # pipeline/IMU settings stays the packaged file).
    base = os.path.join(get_package_share_directory('manual_controller'),
                        'config', 'depthai_camera_yolo.yaml')
    with open(base) as f:
        params = yaml.safe_load(f)
    rgb = params['/**']['ros__parameters']['rgb']
    rgb['i_preview_size'] = size
    rgb['i_preview_width'] = size
    rgb['i_preview_height'] = size
    with open(CAMERA_YAML_PATH, 'w') as f:
        yaml.safe_dump(params, f)
    return []


def generate_launch_description():
    detector = LaunchConfiguration('detector')
    is_hsv = IfCondition(PythonExpression(["'", detector, "' == 'hsv'"]))
    is_yolo = IfCondition(PythonExpression(["'", detector, "' == 'yolo'"]))

    return LaunchDescription([
        DeclareLaunchArgument('detector', default_value='hsv',
                              description='Block detector: hsv (host) or yolo (onboard OAK NN)'),
        DeclareLaunchArgument('yolo_conf', default_value='0.7',
                              description='YOLO confidence threshold (detector:=yolo only)'),
        DeclareLaunchArgument('yolo_input', default_value='640',
                              description='YOLO blob input size: 640 (bundled best.blob) or '
                                          '416 (re-exported duplo_yolov8n_416 model)'),
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
