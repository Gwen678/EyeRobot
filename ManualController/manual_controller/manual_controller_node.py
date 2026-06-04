#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
import math
import select
import sys
import termios
import threading
import time
import tty

import rclpy
from geometry_msgs.msg import PoseStamped, TransformStamped
from nav_msgs.msg import Odometry, Path
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Float32, Int32
from tf2_ros import TransformBroadcaster


@dataclass(frozen=True)
class KeyBinding:
    right: float
    left: float
    rfan: float
    lfan: float
    belt: float
    label: str


@dataclass
class WheelFeedback:
    rad_s: float = 0.0
    stamp_s: float = 0.0


@dataclass
class Pose2D:
    x: float = 0.0
    y: float = 0.0
    yaw: float = 0.0


_HEADER = (
    '\n'
    'EyeRobot manual controller\n'
    '  hold w/s: forward/backward\n'
    '  hold a/d: pivot left/right\n'
    '  hold q/e: fans (coupled, opposite directions)\n'
    '  hold r/t: belt forward/reverse\n'
    '  space or x: stop\n'
    '  o: reset RViz odometry\n'
    '  ctrl-c: quit\n'
    '\n'
    'RViz topics: /odom, /path, TF odom -> base_link\n'
)


def yaw_to_quaternion(yaw: float) -> tuple[float, float, float, float]:
    half = 0.5 * yaw
    return 0.0, 0.0, math.sin(half), math.cos(half)


def normalize_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def finite_float(value: object, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if math.isfinite(number) else fallback


def positive_float(value: object, fallback: float) -> float:
    number = finite_float(value, fallback)
    return number if number > 0.0 else fallback


class ManualControllerNode(Node):
    def __init__(self) -> None:
        super().__init__('manual_controller')

        self.declare_parameter('command_speed_rad_s', 8.0)
        self.declare_parameter('turn_speed_rad_s', 5.0)
        self.declare_parameter('fan_command_rad_s', 8.0)
        self.declare_parameter('belt_command_rad_s', 8.0)
        self.declare_parameter('wheel_radius_m', 0.035)
        self.declare_parameter('wheel_separation_m', 0.150)
        self.declare_parameter('command_rate_hz', 20.0)
        self.declare_parameter('odom_rate_hz', 30.0)
        self.declare_parameter('keyboard_timeout_s', 0.4)
        self.declare_parameter('feedback_timeout_s', 0.5)
        self.declare_parameter('max_odom_step_s', 0.1)
        self.declare_parameter('path_max_len', 2000)
        self.declare_parameter('right_command_sign', -1.0)
        self.declare_parameter('left_command_sign', 1.0)
        self.declare_parameter('rfan_command_sign', 1.0)
        self.declare_parameter('lfan_command_sign', 1.0)
        self.declare_parameter('belt_command_sign', 1.0)
        self.declare_parameter('right_feedback_sign', 1.0)
        self.declare_parameter('left_feedback_sign', 1.0)
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('right_cmd_topic', 'motor_rwheel_cmd')
        self.declare_parameter('left_cmd_topic', 'motor_lwheel_cmd')
        self.declare_parameter('rfan_cmd_topic', 'motor_rfan_cmd')
        self.declare_parameter('lfan_cmd_topic', 'motor_lfan_cmd')
        self.declare_parameter('belt_cmd_topic', 'motor_belt_cmd')
        self.declare_parameter('right_fb_topic', 'motor_rwheel_fb')
        self.declare_parameter('left_fb_topic', 'motor_lwheel_fb')
        self.declare_parameter('odom_topic', 'odom')
        self.declare_parameter('path_topic', 'path')

        self._command_speed = positive_float(
            self.get_parameter('command_speed_rad_s').value, 8.0
        )
        self._turn_speed = positive_float(
            self.get_parameter('turn_speed_rad_s').value, 5.0
        )
        self._fan_speed = positive_float(
            self.get_parameter('fan_command_rad_s').value, 8.0
        )
        self._belt_speed = positive_float(
            self.get_parameter('belt_command_rad_s').value, 8.0
        )
        self._wheel_radius = positive_float(
            self.get_parameter('wheel_radius_m').value, 0.035
        )
        self._wheel_separation = positive_float(
            self.get_parameter('wheel_separation_m').value, 0.150
        )
        self._command_rate = positive_float(
            self.get_parameter('command_rate_hz').value, 20.0
        )
        self._odom_rate = positive_float(
            self.get_parameter('odom_rate_hz').value, 30.0
        )
        self._keyboard_timeout = positive_float(
            self.get_parameter('keyboard_timeout_s').value, 0.7
        )
        self._feedback_timeout = positive_float(
            self.get_parameter('feedback_timeout_s').value, 0.5
        )
        self._max_odom_step = positive_float(
            self.get_parameter('max_odom_step_s').value, 0.1
        )
        self._path_max_len = max(1, int(self.get_parameter('path_max_len').value))
        self._right_command_sign = finite_float(
            self.get_parameter('right_command_sign').value, 1.0
        )
        self._left_command_sign = finite_float(
            self.get_parameter('left_command_sign').value, 1.0
        )
        self._rfan_command_sign = finite_float(
            self.get_parameter('rfan_command_sign').value, 1.0
        )
        self._lfan_command_sign = finite_float(
            self.get_parameter('lfan_command_sign').value, 1.0
        )
        self._belt_command_sign = finite_float(
            self.get_parameter('belt_command_sign').value, 1.0
        )
        self._right_feedback_sign = finite_float(
            self.get_parameter('right_feedback_sign').value, 1.0
        )
        self._left_feedback_sign = finite_float(
            self.get_parameter('left_feedback_sign').value, 1.0
        )

        self._odom_frame = str(self.get_parameter('odom_frame').value)
        self._base_frame = str(self.get_parameter('base_frame').value)
        right_cmd_topic = str(self.get_parameter('right_cmd_topic').value)
        left_cmd_topic = str(self.get_parameter('left_cmd_topic').value)
        rfan_cmd_topic = str(self.get_parameter('rfan_cmd_topic').value)
        lfan_cmd_topic = str(self.get_parameter('lfan_cmd_topic').value)
        belt_cmd_topic = str(self.get_parameter('belt_cmd_topic').value)
        right_fb_topic = str(self.get_parameter('right_fb_topic').value)
        left_fb_topic = str(self.get_parameter('left_fb_topic').value)
        odom_topic = str(self.get_parameter('odom_topic').value)
        path_topic = str(self.get_parameter('path_topic').value)

        # Best-effort: commands are re-published continuously at command_rate,
        # so dropping a sample is harmless and avoids the reliable-QoS ACK
        # traffic / head-of-line stalls that starve the shared micro-ROS UART
        # (symptom: a single motor randomly stalls while others keep running).
        cmd_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        fb_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self._pub_r = self.create_publisher(Float32, right_cmd_topic, cmd_qos)
        self._pub_l = self.create_publisher(Float32, left_cmd_topic, cmd_qos)
        self._pub_rfan = self.create_publisher(Float32, rfan_cmd_topic, cmd_qos)
        self._pub_lfan = self.create_publisher(Float32, lfan_cmd_topic, cmd_qos)
        self._pub_belt = self.create_publisher(Float32, belt_cmd_topic, cmd_qos)
        self._odom_pub = self.create_publisher(Odometry, odom_topic, 10)
        self._path_pub = self.create_publisher(Path, path_topic, 10)
        self._tf_broadcaster = TransformBroadcaster(self)

        self.create_subscription(Int32, right_fb_topic, self._right_feedback_cb, fb_qos)
        self.create_subscription(Int32, left_fb_topic, self._left_feedback_cb, fb_qos)

        # Keys map to an absolute command for every motor. Each press sets the
        # full vector (groups not involved go to zero), so only one group runs
        # at a time and releasing any key lets everything time out to a stop.
        cs, ts = self._command_speed, self._turn_speed
        fs, bs = self._fan_speed, self._belt_speed
        self._bindings: dict[str, KeyBinding] = {
            'w': KeyBinding(cs, cs, 0.0, 0.0, 0.0, 'FORWARD'),
            's': KeyBinding(-cs, -cs, 0.0, 0.0, 0.0, 'BACKWARD'),
            'a': KeyBinding(-ts, ts, 0.0, 0.0, 0.0, 'TURN LEFT'),
            'd': KeyBinding(ts, -ts, 0.0, 0.0, 0.0, 'TURN RIGHT'),
            ' ': KeyBinding(0.0, 0.0, 0.0, 0.0, 0.0, 'STOP'),
            'x': KeyBinding(0.0, 0.0, 0.0, 0.0, 0.0, 'STOP'),
            # Fans are mechanically coupled to spin opposite each other.
            'q': KeyBinding(0.0, 0.0, fs, -fs, 0.0, 'FANS >'),
            'e': KeyBinding(0.0, 0.0, -fs, fs, 0.0, 'FANS <'),
            'r': KeyBinding(0.0, 0.0, 0.0, 0.0, bs, 'BELT +'),
            't': KeyBinding(0.0, 0.0, 0.0, 0.0, -bs, 'BELT -'),
        }

        now_s = time.monotonic()
        self._lock = threading.Lock()
        self._cmd_right = 0.0
        self._cmd_left = 0.0
        self._cmd_rfan = 0.0
        self._cmd_lfan = 0.0
        self._cmd_belt = 0.0
        self._last_key_s = now_s
        self._right_feedback = WheelFeedback(stamp_s=now_s)
        self._left_feedback = WheelFeedback(stamp_s=now_s)
        self._pose = Pose2D()
        self._last_odom_time = self.get_clock().now()
        self._path = Path()
        self._path.header.frame_id = self._odom_frame

        self.create_timer(1.0 / self._command_rate, self._publish_command)
        self.create_timer(1.0 / self._odom_rate, self._publish_odometry)

        self.get_logger().info(
            'Manual controller ready. Hold WASD in this terminal; release stops after '
            f'{self._keyboard_timeout:.2f}s.'
        )

    def apply_key(self, key: str) -> str | None:
        key = key.lower()
        if key == 'o':
            self.reset_odometry()
            return 'RESET ODOM'

        binding = self._bindings.get(key)
        if binding is None:
            return None

        with self._lock:
            self._cmd_right = binding.right
            self._cmd_left = binding.left
            self._cmd_rfan = binding.rfan
            self._cmd_lfan = binding.lfan
            self._cmd_belt = binding.belt
            self._last_key_s = time.monotonic()
        # Do NOT publish here. Key auto-repeat fires this dozens of times per
        # second; publishing per-keypress makes the wire rate track how the key
        # is held and floods the shared micro-ROS UART. The fixed-rate timer
        # (_publish_command at command_rate) is the single publishing path.
        return binding.label

    def stop(self) -> None:
        with self._lock:
            self._cmd_right = 0.0
            self._cmd_left = 0.0
            self._cmd_rfan = 0.0
            self._cmd_lfan = 0.0
            self._cmd_belt = 0.0
            self._last_key_s = time.monotonic()

        for _ in range(3):
            self._publish_command()
            time.sleep(0.02)

    def reset_odometry(self) -> None:
        with self._lock:
            self._pose = Pose2D()
            self._path = Path()
            self._path.header.frame_id = self._odom_frame
            self._last_odom_time = self.get_clock().now()

    def command_snapshot(self) -> tuple[float, float, float, float, float]:
        with self._lock:
            return (
                self._cmd_right,
                self._cmd_left,
                self._cmd_rfan,
                self._cmd_lfan,
                self._cmd_belt,
            )

    def _publish_command(self) -> None:
        with self._lock:
            if (time.monotonic() - self._last_key_s) > self._keyboard_timeout:
                self._cmd_right = 0.0
                self._cmd_left = 0.0
                self._cmd_rfan = 0.0
                self._cmd_lfan = 0.0
                self._cmd_belt = 0.0

            right = self._cmd_right * self._right_command_sign
            left = self._cmd_left * self._left_command_sign
            rfan = self._cmd_rfan * self._rfan_command_sign
            lfan = self._cmd_lfan * self._lfan_command_sign
            belt = self._cmd_belt * self._belt_command_sign

        self._pub_r.publish(Float32(data=right))
        self._pub_l.publish(Float32(data=left))
        self._pub_rfan.publish(Float32(data=rfan))
        self._pub_lfan.publish(Float32(data=lfan))
        self._pub_belt.publish(Float32(data=belt))

    def _right_feedback_cb(self, msg: Int32) -> None:
        with self._lock:
            self._right_feedback.rad_s = self._right_feedback_sign * float(msg.data) / 1000.0
            self._right_feedback.stamp_s = time.monotonic()

    def _left_feedback_cb(self, msg: Int32) -> None:
        with self._lock:
            self._left_feedback.rad_s = self._left_feedback_sign * float(msg.data) / 1000.0
            self._left_feedback.stamp_s = time.monotonic()

    def _wheel_speeds(self) -> tuple[float, float]:
        now_s = time.monotonic()
        with self._lock:
            right = self._right_feedback.rad_s
            left = self._left_feedback.rad_s
            if (now_s - self._right_feedback.stamp_s) > self._feedback_timeout:
                right = 0.0
            if (now_s - self._left_feedback.stamp_s) > self._feedback_timeout:
                left = 0.0
        return right, left

    def _publish_odometry(self) -> None:
        now = self.get_clock().now()
        dt = (now - self._last_odom_time).nanoseconds * 1e-9
        self._last_odom_time = now
        if dt <= 0.0:
            return
        dt = min(dt, self._max_odom_step)

        right_rad_s, left_rad_s = self._wheel_speeds()
        v_right = right_rad_s * self._wheel_radius
        v_left = left_rad_s * self._wheel_radius
        linear = 0.5 * (v_right + v_left)
        angular = (v_right - v_left) / self._wheel_separation

        with self._lock:
            mid_yaw = self._pose.yaw + 0.5 * angular * dt
            self._pose.x += linear * math.cos(mid_yaw) * dt
            self._pose.y += linear * math.sin(mid_yaw) * dt
            self._pose.yaw = normalize_angle(self._pose.yaw + angular * dt)
            pose = Pose2D(self._pose.x, self._pose.y, self._pose.yaw)

        qx, qy, qz, qw = yaw_to_quaternion(pose.yaw)
        stamp = now.to_msg()

        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = self._odom_frame
        odom.child_frame_id = self._base_frame
        odom.pose.pose.position.x = pose.x
        odom.pose.pose.position.y = pose.y
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = linear
        odom.twist.twist.angular.z = angular
        self._odom_pub.publish(odom)

        tf = TransformStamped()
        tf.header.stamp = stamp
        tf.header.frame_id = self._odom_frame
        tf.child_frame_id = self._base_frame
        tf.transform.translation.x = pose.x
        tf.transform.translation.y = pose.y
        tf.transform.rotation.x = qx
        tf.transform.rotation.y = qy
        tf.transform.rotation.z = qz
        tf.transform.rotation.w = qw
        self._tf_broadcaster.sendTransform(tf)

        path_pose = PoseStamped()
        path_pose.header = odom.header
        path_pose.pose = odom.pose.pose

        with self._lock:
            self._path.header.stamp = stamp
            self._path.poses.append(path_pose)
            if len(self._path.poses) > self._path_max_len:
                self._path.poses = self._path.poses[-self._path_max_len:]
            path = self._path

        self._path_pub.publish(path)


class RawKeyboard:
    def __enter__(self) -> RawKeyboard:
        self._fd = sys.stdin.fileno()
        self._saved_attrs = termios.tcgetattr(self._fd)
        tty.setraw(self._fd)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved_attrs)

    def read_key(self, timeout_s: float) -> str | None:
        readable, _, _ = select.select([sys.stdin], [], [], timeout_s)
        if not readable:
            return None
        return sys.stdin.read(1)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ManualControllerNode()

    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    if not sys.stdin.isatty():
        node.get_logger().error('Keyboard control requires an interactive terminal.')
        node.stop()
        node.destroy_node()
        rclpy.shutdown()
        return

    print(_HEADER, flush=True)

    try:
        with RawKeyboard() as keyboard:
            sys.stdout.write('\rWaiting for key...\r')
            sys.stdout.flush()

            while rclpy.ok():
                key = keyboard.read_key(0.05)
                if key is None:
                    continue

                if key == '\x03':
                    break

                label = node.apply_key(key)
                if label is None:
                    continue

                right, left, rfan, lfan, belt = node.command_snapshot()
                sys.stdout.write(
                    f'\r  {label:<12}  '
                    f'R={right:+.1f} L={left:+.1f}  '
                    f'fan={rfan:+.1f}/{lfan:+.1f}  '
                    f'belt={belt:+.1f}    \r'
                )
                sys.stdout.flush()

    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()
        print('\nMotors stopped.')


if __name__ == '__main__':
    main()
