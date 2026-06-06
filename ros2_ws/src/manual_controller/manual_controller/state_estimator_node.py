#!/usr/bin/env python3
"""Wheel-encoder odometry for EyeRobot.

Subscribes to the per-wheel accumulated encoder counts published by the
firmware (std_msgs/Int32 on the *_fb topics), integrates them into a 2D pose
with the differential-drive model, and publishes:

  * nav_msgs/Odometry on ~odom_topic   (pose + twist, with covariance)
  * tf2 odom -> base_link              (optional, see publish_tf)
  * nav_msgs/Path on ~path_topic       (trajectory for RViz)

The message types/frames follow the Nav2 / robot_localization conventions, so
this node can later be fed straight into an EKF (ros2 robot_localization) and
fused with other sensors. When an EKF owns the odom->base_link transform, set
publish_tf:=false here so the two don't fight over the TF tree.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import rclpy
from geometry_msgs.msg import PoseStamped, TransformStamped
from nav_msgs.msg import Odometry, Path
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Int32
from std_srvs.srv import Empty
from tf2_ros import TransformBroadcaster


@dataclass
class Pose2D:
    x: float = 0.0
    y: float = 0.0
    yaw: float = 0.0


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


class StateEstimatorNode(Node):
    def __init__(self) -> None:
        super().__init__('state_estimator')

        # Encoder geometry. counts_per_output_rev are the 4x-quadrature counts
        # for one full revolution of the wheel (output) shaft.
        self.declare_parameter('counts_per_output_rev', 5756.0)
        self.declare_parameter('wheel_radius_m', 0.06)
        self.declare_parameter('wheel_separation_m', 0.33)  # CAD track width
        self.declare_parameter('odom_rate_hz', 30.0)
        self.declare_parameter('max_odom_step_s', 0.1)
        # Counts arrive slower than this node ticks; if no count has advanced for
        # this long, report zero velocity (the robot is considered stopped).
        self.declare_parameter('zero_velocity_timeout_s', 0.2)
        self.declare_parameter('path_max_len', 2000)
        # Reject implausible count jumps (e.g. a firmware reboot resetting the
        # counter): if a wheel moves more than this many revolutions in one
        # step, re-baseline instead of integrating the jump.
        self.declare_parameter('max_revs_per_step', 5.0)
        # Per-wheel feedback polarity in the ROBOT frame. The right encoder reads
        # + on forward, but the left encoder DECREMENTS on robot-forward (the MCU
        # inverts the left motor but not its encoder), so it is negated here.
        # Don't flip the MCU invert_encoder to "fix" it: that also drives the
        # closed-loop speed control and would destabilise it — correct it host-side.
        self.declare_parameter('right_feedback_sign', 1.0)
        self.declare_parameter('left_feedback_sign', -1.0)
        self.declare_parameter('publish_tf', True)
        # When true, log raw encoder counts and per-wheel/centre deltas each step
        # so a forward-vs-backward odometry asymmetry can be diagnosed live.
        self.declare_parameter('debug_encoders', False)
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('right_fb_topic', 'motor_rwheel_fb')
        self.declare_parameter('left_fb_topic', 'motor_lwheel_fb')
        self.declare_parameter('odom_topic', 'odom')
        self.declare_parameter('path_topic', 'path')
        # Diagonal measurement covariances reported on the Odometry message.
        self.declare_parameter('pose_xy_cov', 0.002)
        self.declare_parameter('pose_yaw_cov', 0.005)
        self.declare_parameter('twist_x_cov', 0.002)
        self.declare_parameter('twist_yaw_cov', 0.005)

        self._counts_per_rev = positive_float(
            self.get_parameter('counts_per_output_rev').value, 5756.0
        )
        self._wheel_radius = positive_float(
            self.get_parameter('wheel_radius_m').value, 0.06
        )
        self._wheel_separation = positive_float(
            self.get_parameter('wheel_separation_m').value, 0.150
        )
        self._odom_rate = positive_float(
            self.get_parameter('odom_rate_hz').value, 30.0
        )
        self._max_odom_step = positive_float(
            self.get_parameter('max_odom_step_s').value, 0.1
        )
        self._zero_velocity_timeout = positive_float(
            self.get_parameter('zero_velocity_timeout_s').value, 0.2
        )
        self._path_max_len = max(1, int(self.get_parameter('path_max_len').value))
        self._max_revs_per_step = positive_float(
            self.get_parameter('max_revs_per_step').value, 5.0
        )
        self._right_feedback_sign = finite_float(
            self.get_parameter('right_feedback_sign').value, 1.0
        )
        self._left_feedback_sign = finite_float(
            self.get_parameter('left_feedback_sign').value, 1.0
        )
        self._publish_tf = bool(self.get_parameter('publish_tf').value)
        self._debug_encoders = bool(self.get_parameter('debug_encoders').value)
        self._odom_frame = str(self.get_parameter('odom_frame').value)
        self._base_frame = str(self.get_parameter('base_frame').value)
        right_fb_topic = str(self.get_parameter('right_fb_topic').value)
        left_fb_topic = str(self.get_parameter('left_fb_topic').value)
        odom_topic = str(self.get_parameter('odom_topic').value)
        path_topic = str(self.get_parameter('path_topic').value)
        self._pose_xy_cov = finite_float(self.get_parameter('pose_xy_cov').value, 0.002)
        self._pose_yaw_cov = finite_float(self.get_parameter('pose_yaw_cov').value, 0.005)
        self._twist_x_cov = finite_float(self.get_parameter('twist_x_cov').value, 0.002)
        self._twist_yaw_cov = finite_float(self.get_parameter('twist_yaw_cov').value, 0.005)

        # Metres travelled by a wheel per encoder count.
        self._m_per_count = (2.0 * math.pi * self._wheel_radius) / self._counts_per_rev
        self._max_counts_per_step = self._max_revs_per_step * self._counts_per_rev

        # Best-effort to match the firmware telemetry publisher.
        fb_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self._pose = Pose2D()
        self._right_count: int | None = None
        self._left_count: int | None = None
        self._prev_right: int | None = None
        self._prev_left: int | None = None
        self._last_time = self.get_clock().now()
        # Twist is averaged over the interval between actual count updates (see
        # _update); these accumulate distance/yaw/time until counts advance.
        self._acc_dist = 0.0
        self._acc_yaw = 0.0
        self._acc_time = 0.0
        self._linear = 0.0
        self._angular = 0.0

        self._odom_pub = self.create_publisher(Odometry, odom_topic, 10)
        self._path_pub = self.create_publisher(Path, path_topic, 10)
        self._tf_broadcaster = TransformBroadcaster(self)

        self.create_subscription(Int32, right_fb_topic, self._right_cb, fb_qos)
        self.create_subscription(Int32, left_fb_topic, self._left_cb, fb_qos)

        self._path = Path()
        self._path.header.frame_id = self._odom_frame

        self._reset_srv = self.create_service(
            Empty, 'reset_odometry', self._reset_cb
        )

        self.create_timer(1.0 / self._odom_rate, self._update)

        self.get_logger().info(
            f'State estimator ready: {self._counts_per_rev:.0f} counts/rev, '
            f'r={self._wheel_radius:.3f} m, base={self._wheel_separation:.3f} m, '
            f'publish_tf={self._publish_tf}.'
        )

    # ── Encoder inputs ────────────────────────────────────────────────────────
    def _right_cb(self, msg: Int32) -> None:
        self._right_count = int(msg.data)

    def _left_cb(self, msg: Int32) -> None:
        self._left_count = int(msg.data)

    def _reset_cb(self, request, response):
        self._pose = Pose2D()
        self._prev_right = self._right_count
        self._prev_left = self._left_count
        self._path = Path()
        self._path.header.frame_id = self._odom_frame
        self._last_time = self.get_clock().now()
        self.get_logger().info('Odometry reset.')
        return response

    # ── Integration ───────────────────────────────────────────────────────────
    def _wheel_delta_m(self, current: int, previous: int, sign: float) -> float | None:
        delta_counts = sign * float(current - previous)
        if abs(delta_counts) > self._max_counts_per_step:
            # Implausible jump (likely a firmware counter reset): skip this step.
            return None
        return delta_counts * self._m_per_count

    def _update(self) -> None:
        now = self.get_clock().now()
        dt = (now - self._last_time).nanoseconds * 1e-9
        self._last_time = now

        if self._right_count is None or self._left_count is None:
            # No encoder data yet.
            return

        # First valid pair establishes the baseline without integrating it.
        if self._prev_right is None or self._prev_left is None:
            self._prev_right = self._right_count
            self._prev_left = self._left_count
            return

        # Raw (pre-clamp, pre-sign) count deltas, kept for diagnostics.
        raw_dr = self._right_count - self._prev_right
        raw_dl = self._left_count - self._prev_left

        d_right = self._wheel_delta_m(
            self._right_count, self._prev_right, self._right_feedback_sign
        )
        d_left = self._wheel_delta_m(
            self._left_count, self._prev_left, self._left_feedback_sign
        )
        self._prev_right = self._right_count
        self._prev_left = self._left_count

        if d_right is None or d_left is None:
            if self._debug_encoders:
                self.get_logger().warn(
                    f'[enc] step rejected by plausibility clamp: raw dR={raw_dr:+d} '
                    f'dL={raw_dl:+d} (limit {self._max_counts_per_step:.0f} counts) '
                    f'— re-baselined, no pose update',
                    throttle_duration_sec=0.5,
                )
            return  # re-baselined above; resume next cycle

        d_center = 0.5 * (d_right + d_left)
        d_yaw = (d_right - d_left) / self._wheel_separation

        # Exact midpoint integration of the unicycle model. Pose comes straight
        # from the count deltas, so it is independent of this loop's rate.
        mid_yaw = self._pose.yaw + 0.5 * d_yaw
        self._pose.x += d_center * math.cos(mid_yaw)
        self._pose.y += d_center * math.sin(mid_yaw)
        self._pose.yaw = normalize_angle(self._pose.yaw + d_yaw)

        # Diagnostic trace: raw counts, signed wheel deltas, and the resulting
        # centre/yaw deltas + pose. If forward motion leaves pose.x/y unchanged,
        # this shows whether the two wheel deltas are cancelling (d_center≈0,
        # i.e. forward is being integrated as a pure rotation) or whether a wheel
        # delta is being dropped.
        if self._debug_encoders and (raw_dr != 0 or raw_dl != 0):
            self.get_logger().info(
                f'[enc] R={self._right_count} L={self._left_count} '
                f'rawdR={raw_dr:+d} rawdL={raw_dl:+d} '
                f'dR={d_right:+.4f}m dL={d_left:+.4f}m '
                f'dC={d_center:+.4f}m dYaw={math.degrees(d_yaw):+.2f}deg '
                f'pose=({self._pose.x:+.3f},{self._pose.y:+.3f},'
                f'{math.degrees(self._pose.yaw):+.1f}deg)',
                throttle_duration_sec=0.3,
            )

        # Twist for downstream fusion (robot_localization fuses Vx/Vyaw, not the
        # pose): average distance/yaw over the time between *actual* count
        # updates. The firmware publishes counts slower than this loop ticks, so
        # dividing a fresh delta by the loop period would over-report speed on
        # update ticks and read zero in between. Accumulate until counts advance,
        # then emit the windowed average.
        self._acc_dist += d_center
        self._acc_yaw += d_yaw
        self._acc_time += min(dt, self._max_odom_step) if dt > 0.0 else 0.0
        if (d_right != 0.0 or d_left != 0.0) and self._acc_time > 0.0:
            self._linear = self._acc_dist / self._acc_time
            self._angular = self._acc_yaw / self._acc_time
            self._acc_dist = self._acc_yaw = self._acc_time = 0.0
        elif self._acc_time >= self._zero_velocity_timeout:
            self._linear = self._angular = 0.0
            self._acc_dist = self._acc_yaw = self._acc_time = 0.0

        self._publish(now, self._linear, self._angular)

    # ── Outputs ───────────────────────────────────────────────────────────────
    def _publish(self, now, linear: float, angular: float) -> None:
        qx, qy, qz, qw = yaw_to_quaternion(self._pose.yaw)
        stamp = now.to_msg()

        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = self._odom_frame
        odom.child_frame_id = self._base_frame
        odom.pose.pose.position.x = self._pose.x
        odom.pose.pose.position.y = self._pose.y
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = linear
        odom.twist.twist.angular.z = angular

        # Row-major 6x6 (x, y, z, roll, pitch, yaw). Only the planar DOFs are
        # observed; the rest are left large so a downstream EKF ignores them.
        odom.pose.covariance[0] = self._pose_xy_cov     # x
        odom.pose.covariance[7] = self._pose_xy_cov     # y
        odom.pose.covariance[35] = self._pose_yaw_cov   # yaw
        odom.twist.covariance[0] = self._twist_x_cov    # vx
        odom.twist.covariance[35] = self._twist_yaw_cov  # wz
        self._odom_pub.publish(odom)

        if self._publish_tf:
            tf = TransformStamped()
            tf.header.stamp = stamp
            tf.header.frame_id = self._odom_frame
            tf.child_frame_id = self._base_frame
            tf.transform.translation.x = self._pose.x
            tf.transform.translation.y = self._pose.y
            tf.transform.rotation.x = qx
            tf.transform.rotation.y = qy
            tf.transform.rotation.z = qz
            tf.transform.rotation.w = qw
            self._tf_broadcaster.sendTransform(tf)

        path_pose = PoseStamped()
        path_pose.header = odom.header
        path_pose.pose = odom.pose.pose
        self._path.header.stamp = stamp
        self._path.poses.append(path_pose)
        if len(self._path.poses) > self._path_max_len:
            self._path.poses = self._path.poses[-self._path_max_len:]
        self._path_pub.publish(self._path)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = StateEstimatorNode()
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
