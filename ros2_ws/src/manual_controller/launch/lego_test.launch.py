"""Standalone block-detection test: OAK-D camera + one detector, no ros2_control/EKF/Nav2.
Both detectors (hsv, yolo) publish the same topics; use detector:=hsv|yolo to select."""
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

        # OAK-D driver. Same base yaml as the full stack (RGBD at 5 fps);
        # yolo variant adds the onboard spatial NN. parent_frame left at driver default.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('depthai_ros_driver'), 'launch', 'camera.launch.py'])),
            launch_arguments={
                # yolo: /tmp yaml written by _write_nn_config; hsv: packaged yaml.
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
