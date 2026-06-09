import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessStart
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def _arg(name: str, default: str, description: str) -> DeclareLaunchArgument:
    return DeclareLaunchArgument(name, default_value=default, description=description)


def _f(name: str):
    return ParameterValue(LaunchConfiguration(name), value_type=float)


def generate_launch_description():
    pkg_share = get_package_share_directory('manual_controller')
    rviz_config = os.path.join(pkg_share, 'rviz', 'eyerobot.rviz')

    # Expand the xacro to a URDF string at launch time.  robot_description must be
    # built/installed so $(find robot_description) and package:// mesh URIs resolve.
    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'), ' ',
            PathJoinSubstitution([
                FindPackageShare('robot_description'), 'urdf', 'Robot.xacro']),
        ]),
        value_type=str,
    )

    # controller_manager loads the hardware plugin (eyerobot_hardware) described in
    # Robot.xacro and the controller YAML.  It must start before the spawners.
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description},
            PathJoinSubstitution([
                FindPackageShare('manual_controller'), 'config', 'diff_drive_controller.yaml']),
        ],
        output='screen',
    )

    # Spawners start after controller_manager is alive (RegisterEventHandler below).
    # joint_state_broadcaster publishes /joint_states so robot_state_publisher can
    # animate wheels; diff_drive_controller owns kinematics and odom->base_link TF.
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'],
    )

    # The micro-ROS agent is intentionally NOT started here; run it separately:
    #   ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0
    return LaunchDescription([
        _arg('rviz',       'false', 'Start RViz with the EyeRobot config (off by default; run on dev PC)'),
        _arg('robot_model','true',  'Publish the URDF (robot_state_publisher) for RViz RobotModel'),
        # Teleop: run in its own terminal for a real TTY.
        #   ros2 run manual_controller manual_controller
        # Drives wheels (wasd → /diff_drive_controller/cmd_vel_unstamped),
        # fans (q/e) and belt (r/t); space stops everything.
        _arg('teleop',     'false', 'Spawn the teleop controller in an xterm'),

        # ── Fans/belt controller ──────────────────────────────────────────────
        _arg('fan_command_rad_s',  '8.0', 'Fan command magnitude (q/e)'),
        _arg('belt_command_rad_s', '8.0', 'Belt command magnitude (r/t)'),
        _arg('command_rate_hz',   '20.0', 'Fans/belt publish rate (Hz)'),

        # ── Optional EKF (robot_localization) ────────────────────────────────
        # When enabled, set enable_odom_tf: false in diff_drive_controller.yaml
        # so the EKF — not diff_drive_controller — owns the odom->base_link TF.
        _arg('ekf', 'false', 'Run robot_localization EKF fusing wheel odom + IMU'),

        # ── Fans/belt controller node (optional xterm) ────────────────────────
        Node(
            package='manual_controller',
            executable='manual_controller',
            name='manual_controller',
            output='screen',
            prefix='xterm -title "EyeRobot fans/belt" -e',
            condition=IfCondition(LaunchConfiguration('teleop')),
            parameters=[{
                'fan_command_rad_s':  _f('fan_command_rad_s'),
                'belt_command_rad_s': _f('belt_command_rad_s'),
                'command_rate_hz':    _f('command_rate_hz'),
            }],
        ),

        # ── ros2_control: controller manager + controllers ────────────────────
        controller_manager,

        RegisterEventHandler(
            event_handler=OnProcessStart(
                target_action=controller_manager,
                on_start=[joint_state_broadcaster_spawner, diff_drive_spawner],
            )
        ),

        # ── Robot description / TF ────────────────────────────────────────────
        # robot_state_publisher converts joint states (from joint_state_broadcaster)
        # into link TFs; it does NOT conflict with odom->base_link (owned by
        # diff_drive_controller or the EKF).
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}],
            condition=IfCondition(LaunchConfiguration('robot_model')),
        ),

        # ── Visualization ─────────────────────────────────────────────────────
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('rviz')),
            output='screen',
        ),

        # ── Optional EKF ─────────────────────────────────────────────────────
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[PathJoinSubstitution([
                FindPackageShare('manual_controller'), 'config', 'ekf.yaml'])],
            condition=IfCondition(LaunchConfiguration('ekf')),
        ),

        # ── Fans/belt bridge (wheels handled by diff_drive_controller) ────────
        Node(
            package='manual_controller',
            executable='cmd_vel_bridge',
            name='cmd_vel_bridge',
            output='screen',
        ),

        # ── Foxglove: relay /robot_description TRANSIENT_LOCAL → VOLATILE ─────
        Node(
            package='manual_controller',
            executable='urdf_relay',
            name='urdf_relay',
            output='screen',
            condition=IfCondition(LaunchConfiguration('robot_model')),
        ),

        # ── EKF path for RViz (visualization only) ────────────────────────────
        Node(
            package='manual_controller',
            executable='odom_to_path',
            name='odom_to_path',
            output='screen',
            parameters=[{
                'odom_topic': '/odometry/filtered',
                'path_topic': '/ekf_path',
            }],
            condition=IfCondition(LaunchConfiguration('ekf')),
        ),
    ])
