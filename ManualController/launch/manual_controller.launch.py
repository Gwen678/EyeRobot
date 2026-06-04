import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _arg(name: str, default: str, description: str) -> DeclareLaunchArgument:
    return DeclareLaunchArgument(name, default_value=default, description=description)


def generate_launch_description():
    pkg_share = get_package_share_directory('manual_controller')
    rviz_config = os.path.join(pkg_share, 'rviz', 'eyerobot.rviz')

    return LaunchDescription([
        _arg('micro_ros_agent', 'true', 'Start the micro-ROS serial agent'),
        _arg('serial_dev', '/dev/ttyUSB0', 'Serial device connected to the ESP32'),
        _arg('baud', '115200', 'Serial baud rate for the micro-ROS agent'),
        _arg('rviz', 'true', 'Start RViz with the EyeRobot odometry config'),
        _arg('command_speed_rad_s', '8.0', 'Wheel command for forward/backward keys'),
        _arg('turn_speed_rad_s', '5.0', 'Wheel command for pivot turn keys'),
        _arg('wheel_radius_m', '0.035', 'Wheel radius used for odometry integration'),
        _arg('wheel_separation_m', '0.150', 'Distance between left and right wheel contact lines'),
        _arg('command_rate_hz', '20.0', 'Motor command publish rate'),
        _arg('odom_rate_hz', '30.0', 'Odometry and TF publish rate'),
        _arg('keyboard_timeout_s', '0.2', 'Stop if no key repeat arrives within this time'),
        _arg('feedback_timeout_s', '0.5', 'Treat stale wheel feedback as zero speed'),
        _arg('max_odom_step_s', '0.1', 'Clamp large odometry integration steps'),
        _arg('path_max_len', '2000', 'Maximum number of poses kept in /path'),
        _arg('right_command_sign', '-1.0', 'Set to -1.0 if right motor command polarity is inverted'),
        _arg('left_command_sign', '1.0', 'Set to -1.0 if left motor command polarity is inverted'),
        _arg('right_feedback_sign', '1.0', 'Set to -1.0 if right encoder feedback polarity is inverted'),
        _arg('left_feedback_sign', '1.0', 'Set to -1.0 if left encoder feedback polarity is inverted'),
        _arg('odom_frame', 'odom', 'Odometry fixed frame'),
        _arg('base_frame', 'base_link', 'Robot base frame'),
        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            arguments=[
                'serial',
                '--dev', LaunchConfiguration('serial_dev'),
                '-b', LaunchConfiguration('baud'),
            ],
            condition=IfCondition(LaunchConfiguration('micro_ros_agent')),
            output='screen',
        ),
        Node(
            package='manual_controller',
            executable='manual_controller',
            name='manual_controller',
            output='screen',
            emulate_tty=True,   # keeps raw-terminal keyboard input working
            parameters=[{
                'command_speed_rad_s': ParameterValue(
                    LaunchConfiguration('command_speed_rad_s'), value_type=float),
                'turn_speed_rad_s': ParameterValue(
                    LaunchConfiguration('turn_speed_rad_s'), value_type=float),
                'wheel_radius_m': ParameterValue(
                    LaunchConfiguration('wheel_radius_m'), value_type=float),
                'wheel_separation_m': ParameterValue(
                    LaunchConfiguration('wheel_separation_m'), value_type=float),
                'command_rate_hz': ParameterValue(
                    LaunchConfiguration('command_rate_hz'), value_type=float),
                'odom_rate_hz': ParameterValue(
                    LaunchConfiguration('odom_rate_hz'), value_type=float),
                'keyboard_timeout_s': ParameterValue(
                    LaunchConfiguration('keyboard_timeout_s'), value_type=float),
                'feedback_timeout_s': ParameterValue(
                    LaunchConfiguration('feedback_timeout_s'), value_type=float),
                'max_odom_step_s': ParameterValue(
                    LaunchConfiguration('max_odom_step_s'), value_type=float),
                'path_max_len': ParameterValue(
                    LaunchConfiguration('path_max_len'), value_type=int),
                'right_command_sign': ParameterValue(
                    LaunchConfiguration('right_command_sign'), value_type=float),
                'left_command_sign': ParameterValue(
                    LaunchConfiguration('left_command_sign'), value_type=float),
                'right_feedback_sign': ParameterValue(
                    LaunchConfiguration('right_feedback_sign'), value_type=float),
                'left_feedback_sign': ParameterValue(
                    LaunchConfiguration('left_feedback_sign'), value_type=float),
                'odom_frame': LaunchConfiguration('odom_frame'),
                'base_frame': LaunchConfiguration('base_frame'),
            }],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('rviz')),
            output='screen',
        ),
    ])
