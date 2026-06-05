#!/usr/bin/env python3
"""Dual dead-reckoning odometry for EyeRobot — encoder-only vs encoder+IMU-yaw.

Publishes TWO trajectories that share the *same* encoder-derived travelled
distance and differ in ONLY one thing: where the heading (yaw) comes from. This
makes the benefit of the IMU directly visible as two overlaid lines in RViz.

  * encoder-only   : yaw integrated from the wheel difference (drifts with slip)
  * encoder+IMU yaw: same per-step distance, but heading taken from the IMU
                     (sensor_msgs/Imu, gyro-integrated orientation)

Both consume the firmware encoder ticks (std_msgs/Int32 on the *_fb topics) using
the identical differential-drive integration as state_estimator_node, so any
divergence between the lines is purely the yaw source — not different distance
models.

Outputs (in the odom frame):
  * nav_msgs/Path on ~enc_path_topic      (encoder-only)        default /path_encoder
  * nav_msgs/Path on ~imu_path_topic      (encoder + IMU yaw)   default /path_imu
  * nav_msgs/Odometry on ~enc_odom_topic  default /odom_encoder
  * nav_msgs/Odometry on ~imu_odom_topic  default /odom_imu

This is intentionally NOT a Kalman filter: it is the simple, transparent
comparison the user asked for, and a stepping stone toward a robot_localization
EKF later. No TF is published here so it never fights state_estimator's
odom->base_link.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry, Path
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Imu
from std_msgs.msg import Int32
from std_srvs.srv import Empty


@dataclass
class Pose2D:
    x: float = 0.0
    y: float = 0.0
    yaw: float = 0.0


def yaw_to_quaternion(yaw: float) -> tuple[float, float, float, float]:
    half = 0.5 * yaw
    return 0.0, 0.0, math.sin(half), math.cos(half)


def quaternion_to_yaw(x: float, y: float, z: float, w: float) -> float:
    """Planar yaw (rotation about world Z) from a quaternion."""
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


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


class DualOdometryNode(Node):
    def __init__(self) -> None:
        super().__init__('dual_odometry')

        # Geometry — defaults match state_estimator_node so the encoder line here
        # reproduces the canonical odometry exactly.
        self.declare_parameter('counts_per_output_rev', 5756.0)
        self.declare_parameter('wheel_radius_m', 0.06)
        self.declare_parameter('wheel_separation_m', 0.150)
        self.declare_parameter('odom_rate_hz', 30.0)
        self.declare_parameter('max_odom_step_s', 0.1)
        self.declare_parameter('max_revs_per_step', 5.0)
        self.declare_parameter('right_feedback_sign', 1.0)
        self.declare_parameter('left_feedback_sign', 1.0)
        self.declare_parameter('path_max_len', 2000)
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('right_fb_topic', 'motor_rwheel_fb')
        self.declare_parameter('left_fb_topic', 'motor_lwheel_fb')
        self.declare_parameter('imu_topic', '/oak/imu/data_raw')
        # Flip if the IMU is mounted so its +yaw opposes the robot's +yaw.
        self.declare_parameter('imu_yaw_sign', 1.0)
        self.declare_parameter('enc_path_topic', 'path_encoder')
        self.declare_parameter('imu_path_topic', 'path_imu')
        self.declare_parameter('enc_odom_topic', 'odom_encoder')
        self.declare_parameter('imu_odom_topic', 'odom_imu')

        self._counts_per_rev = positive_float(
            self.get_parameter('counts_per_output_rev').value, 5756.0)
        self._wheel_radius = positive_float(
            self.get_parameter('wheel_radius_m').value, 0.06)
        self._wheel_separation = positive_float(
            self.get_parameter('wheel_separation_m').value, 0.150)
        self._odom_rate = positive_float(
            self.get_parameter('odom_rate_hz').value, 30.0)
        self._max_odom_step = positive_float(
            self.get_parameter('max_odom_step_s').value, 0.1)
        self._max_revs_per_step = positive_float(
            self.get_parameter('max_revs_per_step').value, 5.0)
        self._right_feedback_sign = finite_float(
            self.get_parameter('right_feedback_sign').value, 1.0)
        self._left_feedback_sign = finite_float(
            self.get_parameter('left_feedback_sign').value, 1.0)
        self._path_max_len = max(1, int(self.get_parameter('path_max_len').value))
        self._odom_frame = str(self.get_parameter('odom_frame').value)
        self._base_frame = str(self.get_parameter('base_frame').value)
        right_fb_topic = str(self.get_parameter('right_fb_topic').value)
        left_fb_topic = str(self.get_parameter('left_fb_topic').value)
        imu_topic = str(self.get_parameter('imu_topic').value)
        self._imu_yaw_sign = finite_float(
            self.get_parameter('imu_yaw_sign').value, 1.0)
        enc_path_topic = str(self.get_parameter('enc_path_topic').value)
        imu_path_topic = str(self.get_parameter('imu_path_topic').value)
        enc_odom_topic = str(self.get_parameter('enc_odom_topic').value)
        imu_odom_topic = str(self.get_parameter('imu_odom_topic').value)

        self._m_per_count = (2.0 * math.pi * self._wheel_radius) / self._counts_per_rev
        self._max_counts_per_step = self._max_revs_per_step * self._counts_per_rev

        # Two independent poses, same starting point.
        self._enc = Pose2D()
        self._imu = Pose2D()

        self._right_count: int | None = None
        self._left_count: int | None = None
        self._prev_right: int | None = None
        self._prev_left: int | None = None

        # IMU yaw is referenced to its value at the first integration step, so
        # both trajectories start aligned at yaw = 0 regardless of how the camera
        # happens to be oriented at boot.
        self._imu_yaw_raw: float | None = None
        self._imu_yaw0: float | None = None
        self._imu_yaw_rel = 0.0
        self._prev_imu_yaw_rel = 0.0

        # Best-effort to match the firmware telemetry / IMU publishers.
        fb_qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                            history=HistoryPolicy.KEEP_LAST, depth=1)
        imu_qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                             history=HistoryPolicy.KEEP_LAST, depth=10)

        self._enc_path_pub = self.create_publisher(Path, enc_path_topic, 10)
        self._imu_path_pub = self.create_publisher(Path, imu_path_topic, 10)
        self._enc_odom_pub = self.create_publisher(Odometry, enc_odom_topic, 10)
        self._imu_odom_pub = self.create_publisher(Odometry, imu_odom_topic, 10)

        self.create_subscription(Int32, right_fb_topic, self._right_cb, fb_qos)
        self.create_subscription(Int32, left_fb_topic, self._left_cb, fb_qos)
        self.create_subscription(Imu, imu_topic, self._imu_cb, imu_qos)

        self._enc_path = Path()
        self._enc_path.header.frame_id = self._odom_frame
        self._imu_path = Path()
        self._imu_path.header.frame_id = self._odom_frame

        self._reset_srv = self.create_service(
            Empty, 'reset_dual_odometry', self._reset_cb)

        self.create_timer(1.0 / self._odom_rate, self._update)

        self._imu_seen = False
        self.get_logger().info(
            f'Dual odometry ready: encoder-only -> {enc_path_topic}, '
            f'encoder+IMU-yaw -> {imu_path_topic} (IMU on {imu_topic}). '
            f'{self._counts_per_rev:.0f} counts/rev, r={self._wheel_radius:.3f} m, '
            f'base={self._wheel_separation:.3f} m.')

    # ── Inputs ────────────────────────────────────────────────────────────────
    def _right_cb(self, msg: Int32) -> None:
        self._right_count = int(msg.data)

    def _left_cb(self, msg: Int32) -> None:
        self._left_count = int(msg.data)

    def _imu_cb(self, msg: Imu) -> None:
        o = msg.orientation
        self._imu_yaw_raw = quaternion_to_yaw(o.x, o.y, o.z, o.w)
        if not self._imu_seen:
            self._imu_seen = True
            self.get_logger().info('First IMU orientation received.')

    def _reset_cb(self, request, response):
        self._enc = Pose2D()
        self._imu = Pose2D()
        self._prev_right = self._right_count
        self._prev_left = self._left_count
        self._imu_yaw0 = self._imu_yaw_raw
        self._imu_yaw_rel = 0.0
        self._prev_imu_yaw_rel = 0.0
        self._enc_path = Path()
        self._enc_path.header.frame_id = self._odom_frame
        self._imu_path = Path()
        self._imu_path.header.frame_id = self._odom_frame
        self.get_logger().info('Dual odometry reset.')
        return response

    # ── Integration ───────────────────────────────────────────────────────────
    def _wheel_delta_m(self, current: int, previous: int, sign: float):
        delta_counts = sign * float(current - previous)
        if abs(delta_counts) > self._max_counts_per_step:
            return None  # implausible jump (firmware reset): skip this step
        return delta_counts * self._m_per_count

    def _update(self) -> None:
        if self._right_count is None or self._left_count is None:
            return
        if self._prev_right is None or self._prev_left is None:
            self._prev_right = self._right_count
            self._prev_left = self._left_count
            return

        d_right = self._wheel_delta_m(
            self._right_count, self._prev_right, self._right_feedback_sign)
        d_left = self._wheel_delta_m(
            self._left_count, self._prev_left, self._left_feedback_sign)
        self._prev_right = self._right_count
        self._prev_left = self._left_count
        if d_right is None or d_left is None:
            return

        d_center = 0.5 * (d_right + d_left)
        d_yaw_enc = (d_right - d_left) / self._wheel_separation

        # ── Estimate 1: encoder-only (yaw from wheels) ──────────────────────
        mid_yaw = self._enc.yaw + 0.5 * d_yaw_enc
        self._enc.x += d_center * math.cos(mid_yaw)
        self._enc.y += d_center * math.sin(mid_yaw)
        self._enc.yaw = normalize_angle(self._enc.yaw + d_yaw_enc)

        # ── Estimate 2: encoder distance + IMU yaw ──────────────────────────
        # Same d_center, but heading comes from the IMU. Reference the IMU yaw to
        # its first value so both lines start at yaw = 0.
        if self._imu_yaw_raw is not None:
            if self._imu_yaw0 is None:
                self._imu_yaw0 = self._imu_yaw_raw
            self._imu_yaw_rel = normalize_angle(
                self._imu_yaw_sign * (self._imu_yaw_raw - self._imu_yaw0))
        # Midpoint of the IMU heading over this step for symmetric integration.
        mid_yaw_imu = self._prev_imu_yaw_rel + 0.5 * normalize_angle(
            self._imu_yaw_rel - self._prev_imu_yaw_rel)
        self._imu.x += d_center * math.cos(mid_yaw_imu)
        self._imu.y += d_center * math.sin(mid_yaw_imu)
        self._imu.yaw = self._imu_yaw_rel
        self._prev_imu_yaw_rel = self._imu_yaw_rel

        now = self.get_clock().now().to_msg()
        self._publish(now, self._enc, self._enc_path,
                      self._enc_path_pub, self._enc_odom_pub)
        self._publish(now, self._imu, self._imu_path,
                      self._imu_path_pub, self._imu_odom_pub)

    # ── Outputs ─────────────────────────────────────────────────────────────
    def _publish(self, stamp, pose: Pose2D, path: Path, path_pub, odom_pub) -> None:
        qx, qy, qz, qw = yaw_to_quaternion(pose.yaw)

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
        odom_pub.publish(odom)

        ps = PoseStamped()
        ps.header = odom.header
        ps.pose = odom.pose.pose
        path.header.stamp = stamp
        path.poses.append(ps)
        if len(path.poses) > self._path_max_len:
            path.poses = path.poses[-self._path_max_len:]
        path_pub.publish(path)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DualOdometryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
