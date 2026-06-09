import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution, PythonExpression
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

    # Expand the xacro to a URDF string at launch time. robot_description must be
    # built/installed so $(find robot_description) and package:// mesh URIs
    # resolve (see URDF/CMakeLists.txt).
    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'), ' ',
            PathJoinSubstitution([
                FindPackageShare('robot_description'), 'urdf', 'Robot.xacro']),
        ]),
        value_type=str,
    )

    # The micro-ROS agent is intentionally NOT started here; run it separately
    # (e.g. `ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0`).
    return LaunchDescription([
        _arg('rviz', 'false', 'Start RViz with the EyeRobot odometry config (off by default; run RViz on the dev PC for Jetson Nano deployments)'),
        _arg('robot_model', 'true', 'Publish the URDF (robot_state_publisher) for the RViz RobotModel'),
        # Default OFF: the xterm-wrapped teleop detaches from the launch process
        # group and survives shutdown, orphaning nodes across runs. Prefer running
        # teleop in its own terminal (`ros2 run manual_controller manual_controller`),
        # which gets a real TTY and dies cleanly on Ctrl-C. Set teleop:=true only
        # if you want the convenience xterm and accept manual cleanup.
        _arg('teleop', 'false', 'Spawn keyboard teleop in an xterm (off by default; run it in its own terminal instead)'),

        # ── Teleop (control) node ─────────────────────────────────────────────
        _arg('command_speed_rad_s', '9.0', 'Wheel command for forward/backward keys'),
        _arg('turn_speed_rad_s', '5.0', 'Wheel command for pivot turn keys'),
        _arg('fan_command_rad_s', '8.0', 'Fan command magnitude (q/e)'),
        _arg('belt_command_rad_s', '8.0', 'Belt command magnitude (r/t)'),
        _arg('command_rate_hz', '20.0', 'Motor command publish rate'),
        _arg('release_timeout_s', '0.2', 'Stop wheels if no key repeat arrives within this time'),
        _arg('accel_rad_s2', '18.0', 'Wheel acceleration ramp rate (rad/s²); limits step per publish tick'),
        # Direction is handled on the MCU (invert_motor/invert_encoder); host sends +forward.
        _arg('right_command_sign', '1.0', 'Host command polarity; keep +1, fix direction on the MCU'),
        _arg('left_command_sign', '1.0', 'Host command polarity; keep +1, fix direction on the MCU'),

        # ── State estimator (odometry) node ───────────────────────────────────
        _arg('counts_per_output_rev', '5756.0', 'Encoder counts per wheel (output) revolution'),
        _arg('wheel_radius_m', '0.06', 'Wheel radius used for odometry integration'),
        _arg('wheel_separation_m', '0.33', 'Distance between left and right wheels (from CAD)'),
        _arg('odom_rate_hz', '30.0', 'Odometry / TF / path publish rate'),
        _arg('publish_tf', 'true', 'Publish odom->base_link TF (auto-disabled when ekf:=true so the EKF owns it)'),
        # robot_localization EKF: fuse wheel odom (vx, vyaw) + IMU (roll, pitch,
        # yaw-rate) into a full pose, owning odom->base_link. Needs the OAK IMU in
        # complementary mode and ros-humble-robot-localization installed.
        _arg('ekf', 'false', 'Run the robot_localization EKF fusing wheel odom + IMU'),
        _arg('cmd_vel_bridge', 'false', 'Bridge /cmd_vel (Nav2) to motor wheel commands (for autonomous navigation)'),
        _arg('right_feedback_sign', '1.0', 'Right encoder reads + on robot-forward; keep +1'),
        # The LEFT encoder decrements when the robot rolls forward (invert_motor is
        # set on the MCU but the encoder sign is not, so its counts oppose robot
        # forward). Negate it host-side so straight driving is integrated as
        # translation, not rotation. Do NOT "fix" this by flipping the MCU
        # invert_encoder — that also feeds the closed-loop speed control and would
        # destabilise it. See state_estimator_node.py.
        _arg('left_feedback_sign', '-1.0', 'Left encoder counts oppose robot-forward; negate host-side'),
        _arg('odom_frame', 'odom', 'Odometry fixed frame'),
        _arg('base_frame', 'base_link', 'Robot base frame'),

        # ── Dual odometry comparison (encoder-only vs encoder+IMU-yaw) ─────────
        _arg('dual_odometry', 'true', 'Run the dual-odometry comparison node (two RViz paths)'),
        _arg('imu_topic', '/oak/imu/data_raw', 'IMU topic feeding the encoder+IMU-yaw estimate'),
        _arg('imu_yaw_sign', '1.0', 'Flip to -1.0 if the IMU yaw turns opposite the robot'),

        # ros2 launch does not give a node an interactive stdin, so the raw
        # keyboard reader can't run in-process. Spawn it in its own xterm, which
        # provides a real TTY. Set teleop:=false to run it yourself instead
        # (`ros2 run manual_controller manual_controller`).
        Node(
            package='manual_controller',
            executable='manual_controller',
            name='manual_controller',
            output='screen',
            prefix='xterm -title "EyeRobot teleop" -e',
            condition=IfCondition(LaunchConfiguration('teleop')),
            parameters=[{
                'command_speed_rad_s': _f('command_speed_rad_s'),
                'turn_speed_rad_s': _f('turn_speed_rad_s'),
                'fan_command_rad_s': _f('fan_command_rad_s'),
                'belt_command_rad_s': _f('belt_command_rad_s'),
                'command_rate_hz': _f('command_rate_hz'),
                'release_timeout_s': _f('release_timeout_s'),
                'accel_rad_s2': _f('accel_rad_s2'),
                'right_command_sign': _f('right_command_sign'),
                'left_command_sign': _f('left_command_sign'),
            }],
        ),
        Node(
            package='manual_controller',
            executable='state_estimator',
            name='state_estimator',
            output='screen',
            parameters=[{
                'counts_per_output_rev': _f('counts_per_output_rev'),
                'wheel_radius_m': _f('wheel_radius_m'),
                'wheel_separation_m': _f('wheel_separation_m'),
                'odom_rate_hz': _f('odom_rate_hz'),
                # Publish odom->base_link only if requested AND the EKF is off
                # (when ekf:=true the EKF owns that transform).
                # state_estimator publishes TF only when nothing else will:
                # dual_odometry (default on) owns TF when ekf:=false.
                'publish_tf': ParameterValue(
                    PythonExpression([
                        "'", LaunchConfiguration('publish_tf'), "' == 'true' and '",
                        LaunchConfiguration('ekf'), "' == 'false' and '",
                        LaunchConfiguration('dual_odometry'), "' == 'false'"]),
                    value_type=bool),
                'right_feedback_sign': _f('right_feedback_sign'),
                'left_feedback_sign': _f('left_feedback_sign'),
                'odom_frame': LaunchConfiguration('odom_frame'),
                'base_frame': LaunchConfiguration('base_frame'),
            }],
        ),
        # Encoder-only vs encoder+IMU-yaw comparison. Same wheel geometry as the
        # state_estimator so the only difference between its two paths is the yaw
        # source. Publishes no TF, so it never fights odom->base_link.
        Node(
            package='manual_controller',
            executable='dual_odometry',
            name='dual_odometry',
            output='screen',
            condition=IfCondition(LaunchConfiguration('dual_odometry')),
            parameters=[{
                'counts_per_output_rev': _f('counts_per_output_rev'),
                'wheel_radius_m': _f('wheel_radius_m'),
                'wheel_separation_m': _f('wheel_separation_m'),
                'odom_rate_hz': _f('odom_rate_hz'),
                'right_feedback_sign': _f('right_feedback_sign'),
                'left_feedback_sign': _f('left_feedback_sign'),
                'odom_frame': LaunchConfiguration('odom_frame'),
                'base_frame': LaunchConfiguration('base_frame'),
                'imu_topic': LaunchConfiguration('imu_topic'),
                'imu_yaw_sign': _f('imu_yaw_sign'),
                # Publish odom->base_link TF from the IMU-fused pose when the EKF
                # is off, making path_imu the default odometry source.
                'publish_tf': ParameterValue(
                    PythonExpression(["'", LaunchConfiguration('ekf'), "' == 'false'"]),
                    value_type=bool),
                'publish_filtered_odom': ParameterValue(
                    PythonExpression(["'", LaunchConfiguration('ekf'), "' == 'false'"]),
                    value_type=bool),
            }],
        ),
        # Publishes the URDF on /robot_description and the link TFs (base_link ->
        # wheels) via TF2. The state_estimator supplies odom -> base_link, so the
        # model rides on the wheel odometry.
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}],
            condition=IfCondition(LaunchConfiguration('robot_model')),
        ),
        # The two wheel joints are 'continuous'; publish zeroed joint states so
        # robot_state_publisher emits their transforms (the wheels just don't
        # spin in the model).
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            condition=IfCondition(LaunchConfiguration('robot_model')),
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('rviz')),
            output='screen',
        ),
        # robot_localization EKF: fuses /odom (wheel vx, vyaw) + /oak/imu/data_raw
        # (absolute roll/pitch, body rates) into a full 6-DOF pose and owns
        # odom->base_link. Off by default; state_estimator drops its TF when on.
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[PathJoinSubstitution([
                FindPackageShare('manual_controller'), 'config', 'ekf.yaml'])],
            condition=IfCondition(LaunchConfiguration('ekf')),
        ),
        # Bridge /cmd_vel (Twist from Nav2) to per-wheel Float32 speed commands.
        # Off by default — enable when running nav2.launch.py full_nav:=true.
        Node(
            package='manual_controller',
            executable='cmd_vel_bridge',
            name='cmd_vel_bridge',
            output='screen',
            parameters=[{
                'wheel_radius_m':     _f('wheel_radius_m'),
                'wheel_separation_m': _f('wheel_separation_m'),
                'right_command_sign': _f('right_command_sign'),
                'left_command_sign':  _f('left_command_sign'),
            }],
            condition=IfCondition(LaunchConfiguration('cmd_vel_bridge')),
        ),
        # Relay /robot_description from TRANSIENT_LOCAL → VOLATILE so
        # foxglove_bridge can receive it. robot_state_publisher publishes latched
        # (TRANSIENT_LOCAL) which foxglove_bridge misses over WebSocket.
        Node(
            package='manual_controller',
            executable='urdf_relay',
            name='urdf_relay',
            output='screen',
            condition=IfCondition(LaunchConfiguration('robot_model')),
        ),
        # Relay the EKF Odometry to a Path so RViz draws it as a line (magenta)
        # next to the encoder/IMU comparison paths. Visualization only.
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
