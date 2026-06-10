#!/usr/bin/env python3
"""Gravity-aligned IMU relay: depthai_ros_driver sensor frame → body frame.

The OAK-D is mounted tilted (~60° to the horizontal, looking down at the
floor), so the raw gyro z-axis only carries cos(tilt) ≈ 0.5 of the robot's
yaw rate — the cause of the EKF integrating ~54% of every rotation (and of the
flaky yaw sign). Instead of hand-tuned axis signs or a hardcoded mount angle,
this node MEASURES the mounting at startup: while the robot sits still on flat
ground, the average accelerometer vector is gravity, i.e. the sensor-frame
direction of body-up. All data is then rotated by the minimal rotation that
aligns that direction with +z. Result: angular_velocity.z is the TRUE yaw rate
with the physically correct sign, automatically, for any mount orientation.

The x/y body axes are defined only up to a rotation about vertical (gravity
cannot observe sensor yaw), which is irrelevant for the EKF (fuses vyaw only).
For the future ramp-pitch detector, calibrate the pitch axis sign once on the
real ramp.

Correction lives HERE, in the data, not in TF: rotating the IMU frame in the
URDF did not change the yaw rate the EKF integrates (verified on hardware
2026-06-10), so the data is corrected directly and stamped with the
body-aligned imu_link.

Pipeline:
  depthai_ros_driver  →  /oak/imu/data  →  [this node]  →  /oak/imu/data_raw
  →  imu_filter_madgwick  →  /oak/imu/fused  →  EKF

Startup: keep the robot STILL on FLAT ground for ~2 s until it logs
"mount tilt = ... gyro bias = ...". Nothing is published before that.
"""
from __future__ import annotations
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Imu


def _rotation_aligning(v: tuple[float, float, float],
                       eps: float = 1e-9) -> list[list[float]]:
    """Rodrigues: minimal rotation R such that R·v̂ = (0, 0, 1)."""
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    ux, uy, uz = v[0] / n, v[1] / n, v[2] / n
    # k = û × ẑ ; c = û·ẑ ; s² = |k|²
    kx, ky, kz = uy, -ux, 0.0
    c = uz
    s2 = kx * kx + ky * ky
    if s2 < eps:
        if c > 0.0:                       # already aligned
            return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        # anti-parallel: 180° about x
        return [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]]
    f = (1.0 - c) / s2
    # R = I + K + K²·f with K = skew(k)
    return [
        [1.0 + f * (-ky * ky),      f * kx * ky,            ky],
        [f * kx * ky,               1.0 + f * (-kx * kx),  -kx],
        [-ky,                       kx,                     1.0 + f * (-kx * kx - ky * ky)],
    ]


def _apply(R: list[list[float]], x: float, y: float, z: float):
    return (R[0][0] * x + R[0][1] * y + R[0][2] * z,
            R[1][0] * x + R[1][1] * y + R[1][2] * z,
            R[2][0] * x + R[2][1] * y + R[2][2] * z)


class ImuRemapNode(Node):
    def __init__(self) -> None:
        super().__init__('imu_remap')
        self.declare_parameter('input_topic',  '/oak/imu/data')
        self.declare_parameter('output_topic', '/oak/imu/data_raw')
        self.declare_parameter('frame_id',     'imu_link')
        # Startup calibration window (robot still, flat ground): averages the
        # gyro (→ bias) and the accelerometer (→ gravity direction → mount
        # rotation). ~2 s at 200 Hz. 0 disables both (data passes raw).
        self.declare_parameter('calib_samples', 400)

        self._frame = self.get_parameter('frame_id').value

        self._calib_n   = max(0, int(self.get_parameter('calib_samples').value))
        self._gyro_sum  = [0.0, 0.0, 0.0]
        self._accel_sum = [0.0, 0.0, 0.0]
        self._count     = 0
        # Set together once calibration finishes (or immediately if disabled).
        self._gyro_bias: tuple[float, float, float] | None = None
        self._R: list[list[float]] | None = None
        if self._calib_n == 0:
            self._gyro_bias = (0.0, 0.0, 0.0)
            self._R = _rotation_aligning((0.0, 0.0, 1.0))

        # BMI270 covariances from 61-min Allan variance calibration (2026-06-08).
        # Measurement noise = ARW² × 200 Hz; diagonal 3×3 in row-major order.
        # Kept un-rotated: the per-axis values are near-isotropic.
        self._gyro_cov  = [1.65e-6, 0., 0., 0., 1.84e-6, 0., 0., 0., 1.52e-6]
        self._accel_cov = [0.01, 0., 0., 0., 0.01, 0., 0., 0., 0.01]

        sub_qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                             history=HistoryPolicy.KEEP_LAST, depth=10)
        # Publisher must be RELIABLE: imu_filter_madgwick subscribes reliable,
        # and a best-effort publisher is QoS-incompatible with that (no data).
        pub_qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE,
                             history=HistoryPolicy.KEEP_LAST, depth=10)

        in_t  = self.get_parameter('input_topic').value
        out_t = self.get_parameter('output_topic').value
        self._pub = self.create_publisher(Imu, out_t, pub_qos)
        self.create_subscription(Imu, in_t, self._cb, sub_qos)
        self.get_logger().info(
            f'{in_t} → {out_t} — calibrating mount tilt + gyro bias over '
            f'{self._calib_n} samples; keep the robot STILL on flat ground.')

    def _finish_calibration(self) -> None:
        n = self._count
        self._gyro_bias = tuple(s / n for s in self._gyro_sum)
        a = tuple(s / n for s in self._accel_sum)
        a_norm = math.sqrt(sum(c * c for c in a))
        if a_norm < 5.0:  # gravity missing/implausible — refuse to guess
            self.get_logger().error(
                f'|accel| = {a_norm:.2f} m/s² during calibration (expected '
                f'~9.81) — cannot determine mount orientation, passing data '
                f'through UNROTATED. Check the driver/units.')
            self._R = _rotation_aligning((0.0, 0.0, 1.0))
        else:
            self._R = _rotation_aligning(a)
            tilt_deg = math.degrees(math.acos(max(-1.0, min(1.0, a[2] / a_norm))))
            self.get_logger().info(
                f'mount tilt = {tilt_deg:.1f}° from vertical (expected ~60 for '
                f'the current OAK-D mount), |g| = {a_norm:.2f} m/s²')
        bx, by, bz = self._gyro_bias
        self.get_logger().info(
            f'gyro bias = ({bx:+.5f}, {by:+.5f}, {bz:+.5f}) rad/s '
            f'({n} samples) — robot must have been still')

    def _cb(self, msg: Imu) -> None:
        # Startup calibration: nothing is published until done, so downstream
        # (Madgwick/EKF) never sees uncorrected data.
        if self._R is None:
            self._gyro_sum[0]  += msg.angular_velocity.x
            self._gyro_sum[1]  += msg.angular_velocity.y
            self._gyro_sum[2]  += msg.angular_velocity.z
            self._accel_sum[0] += msg.linear_acceleration.x
            self._accel_sum[1] += msg.linear_acceleration.y
            self._accel_sum[2] += msg.linear_acceleration.z
            self._count += 1
            if self._count >= self._calib_n:
                self._finish_calibration()
            return
        bx, by, bz = self._gyro_bias

        wx, wy, wz = _apply(self._R,
                            msg.angular_velocity.x - bx,
                            msg.angular_velocity.y - by,
                            msg.angular_velocity.z - bz)
        ax, ay, az = _apply(self._R,
                            msg.linear_acceleration.x,
                            msg.linear_acceleration.y,
                            msg.linear_acceleration.z)

        out = Imu()
        out.header = msg.header
        out.header.frame_id = self._frame
        out.angular_velocity.x = wx
        out.angular_velocity.y = wy
        out.angular_velocity.z = wz
        out.linear_acceleration.x = ax
        out.linear_acceleration.y = ay
        out.linear_acceleration.z = az
        # -1 in [0] = "orientation not estimated by this node"; imu_filter_madgwick
        # reads this sentinel and fills orientation in its output message.
        out.orientation_covariance = [-1.0, 0., 0., 0., 0., 0., 0., 0., 0.]
        out.angular_velocity_covariance    = self._gyro_cov
        out.linear_acceleration_covariance = self._accel_cov
        self._pub.publish(out)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ImuRemapNode()
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
