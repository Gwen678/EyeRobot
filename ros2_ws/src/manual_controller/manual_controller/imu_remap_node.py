#!/usr/bin/env python3
"""Corrected IMU relay: depthai_ros_driver sensor frame to body frame.

Measures the OAK-D mount tilt from gravity at startup (robot still, flat
ground ~2 s), rotates all IMU data to align with the body frame, and
subtracts gyro bias. Pipeline: /oak/imu/data to [this node] to
/oak/imu/data_raw to imu_filter_madgwick to /oak/imu/fused to EKF.
"""
from __future__ import annotations
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Imu
from geometry_msgs.msg import TransformStamped
from tf2_ros import Buffer, TransformListener, StaticTransformBroadcaster


def _rotation_aligning(v: tuple[float, float, float],
                       eps: float = 1e-9) -> list[list[float]]:
    """Rodrigues minimal rotation R such that R*v_hat = (0, 0, 1)."""
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    ux, uy, uz = v[0] / n, v[1] / n, v[2] / n
    # k = u_hat x z_hat ; c = u_hat dot z_hat ; s2 = |k|^2
    kx, ky, kz = uy, -ux, 0.0
    c = uz
    s2 = kx * kx + ky * ky
    if s2 < eps:
        if c > 0.0:                       # already aligned
            return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        # opposite direction: 180 deg about x
        return [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]]
    f = (1.0 - c) / s2
    # R = I + K + K^2 * f with K = skew(k)
    return [
        [1.0 + f * (-ky * ky),      f * kx * ky,            ky],
        [f * kx * ky,               1.0 + f * (-kx * kx),  -kx],
        [-ky,                       kx,                     1.0 + f * (-kx * kx - ky * ky)],
    ]


def _apply(R: list[list[float]], x: float, y: float, z: float):
    return (R[0][0] * x + R[0][1] * y + R[0][2] * z,
            R[1][0] * x + R[1][1] * y + R[1][2] * z,
            R[2][0] * x + R[2][1] * y + R[2][2] * z)


def _matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)]
            for i in range(3)]


def _matrix_from_rpy(roll, pitch, yaw):
    """Rotation matrix from extrinsic XYZ (roll, pitch, yaw) Euler angles."""
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return _matmul(
        [[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]],
        _matmul([[cp, 0.0, sp], [0.0, 1.0, 0.0], [-sp, 0.0, cp]],
                [[1.0, 0.0, 0.0], [0.0, cr, -sr], [0.0, sr, cr]]))


def _matrix_from_quat(x, y, z, w):
    """Rotation matrix from a (normalized) quaternion."""
    return [
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w),     2 * (x * z + y * w)],
        [2 * (x * y + z * w),     1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w),     2 * (y * z + x * w),     1 - 2 * (x * x + y * y)],
    ]


def _quat_from_matrix(R):
    """Quaternion (x, y, z, w) from a rotation matrix (Shepperd's method)."""
    t = R[0][0] + R[1][1] + R[2][2]
    if t > 0.0:
        s = math.sqrt(t + 1.0) * 2.0
        return ((R[2][1] - R[1][2]) / s, (R[0][2] - R[2][0]) / s,
                (R[1][0] - R[0][1]) / s, 0.25 * s)
    if R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        s = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2.0
        return (0.25 * s, (R[0][1] + R[1][0]) / s,
                (R[0][2] + R[2][0]) / s, (R[2][1] - R[1][2]) / s)
    if R[1][1] > R[2][2]:
        s = math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2]) * 2.0
        return ((R[0][1] + R[1][0]) / s, 0.25 * s,
                (R[1][2] + R[2][1]) / s, (R[0][2] - R[2][0]) / s)
    s = math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1]) * 2.0
    return ((R[0][2] + R[2][0]) / s, (R[1][2] + R[2][1]) / s,
            0.25 * s, (R[1][0] - R[0][1]) / s)


class ImuRemapNode(Node):
    def __init__(self) -> None:
        super().__init__('imu_remap')
        self.declare_parameter('input_topic',  '/oak/imu/data')
        self.declare_parameter('output_topic', '/oak/imu/data_raw')
        self.declare_parameter('frame_id',     'imu_link')
        # Startup calibration window (robot still, flat ground): averages gyro
        # for bias and accel for gravity direction. ~2 s at 200 Hz. 0 disables.
        self.declare_parameter('calib_samples', 400)

        self._frame = self.get_parameter('frame_id').value

        self._calib_n   = max(0, int(self.get_parameter('calib_samples').value))
        self._gyro_sum  = [0.0, 0.0, 0.0]
        self._accel_sum = [0.0, 0.0, 0.0]
        self._count     = 0
        # Set once calibration finishes, or immediately if disabled.
        self._gyro_bias: tuple[float, float, float] | None = None
        self._R: list[list[float]] | None = None
        if self._calib_n == 0:
            self._gyro_bias = (0.0, 0.0, 0.0)
            self._R = _rotation_aligning((0.0, 0.0, 1.0))

        # BMI270 covariances from Allan variance calibration. Diagonal 3x3 in
        # row-major order; near-isotropic so kept unrotated.
        self._gyro_cov  = [1.65e-6, 0., 0., 0., 1.84e-6, 0., 0., 0., 1.52e-6]
        self._accel_cov = [0.01, 0., 0., 0., 0.01, 0., 0., 0., 0.01]

        # Camera mount TF: the IMU is inside the OAK, so gravity calibration
        # also gives the camera mount orientation. Publishes base_link to
        # oak_mount with the measured rotation (yaw forced to 0, camera forward).
        self.declare_parameter('publish_camera_tf', True)
        self.declare_parameter('camera_mount_frame', 'oak_mount')
        # The driver URDF sets the camera body frame to the camera name ('oak').
        # 'oak-d-base-frame' only exists as the default parent and is not used.
        self.declare_parameter('camera_base_frame', 'oak')
        # IMU to camera-body extrinsic fallback (roll, pitch, yaw, radians).
        # OAK-D-LITE URDF never creates an IMU frame, so this parameter is
        # the actual mechanism; check the logged pitch matches the mount tilt.
        self.declare_parameter('imu_extrinsic_rpy', [0.0, 0.0, 0.0])
        self.declare_parameter('mount_x', 0.42)   # base_link to camera, meters
        self.declare_parameter('mount_y', 0.0)
        self.declare_parameter('mount_z', 0.135)
        self._g_sensor: tuple[float, float, float] | None = None
        self._imu_frame: str | None = None
        self._mount_tf_done = False
        if bool(self.get_parameter('publish_camera_tf').value):
            self._tf_buffer = Buffer()
            self._tf_listener = TransformListener(self._tf_buffer, self)
            self._tf_static_pub = StaticTransformBroadcaster(self)
            # Retries until the driver's static TF is available, then publishes once.
            self._mount_tf_timer = self.create_timer(1.0, self._try_publish_mount_tf)

        sub_qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                             history=HistoryPolicy.KEEP_LAST, depth=10)
        # Publisher must be RELIABLE: imu_filter_madgwick subscribes reliable;
        # a best effort publisher is QoS-incompatible (no data delivered).
        pub_qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE,
                             history=HistoryPolicy.KEEP_LAST, depth=10)

        in_t  = self.get_parameter('input_topic').value
        out_t = self.get_parameter('output_topic').value
        self._pub = self.create_publisher(Imu, out_t, pub_qos)
        self.create_subscription(Imu, in_t, self._cb, sub_qos)
        self.get_logger().info(
            f'{in_t} to {out_t}: calibrating mount tilt and gyro bias over '
            f'{self._calib_n} samples; keep the robot STILL on flat ground.')

    def _finish_calibration(self) -> None:
        n = self._count
        self._gyro_bias = tuple(s / n for s in self._gyro_sum)
        a = tuple(s / n for s in self._accel_sum)
        a_norm = math.sqrt(sum(c * c for c in a))
        if a_norm < 5.0:  # gravity missing or implausible; refuse to guess
            self.get_logger().error(
                f'|accel| = {a_norm:.2f} m/s² during calibration (expected '
                f'~9.81) — cannot determine mount orientation, passing data '
                f'through UNROTATED. Check the driver/units.')
            self._R = _rotation_aligning((0.0, 0.0, 1.0))
        else:
            self._R = _rotation_aligning(a)
            self._g_sensor = (a[0] / a_norm, a[1] / a_norm, a[2] / a_norm)
            tilt_deg = math.degrees(math.acos(max(-1.0, min(1.0, a[2] / a_norm))))
            self.get_logger().info(
                f'mount tilt = {tilt_deg:.1f}° from vertical (expected ~60 for '
                f'the current OAK-D mount), |g| = {a_norm:.2f} m/s²')
        bx, by, bz = self._gyro_bias
        self.get_logger().info(
            f'gyro bias = ({bx:+.5f}, {by:+.5f}, {bz:+.5f}) rad/s '
            f'({n} samples) — robot must have been still')

    def _try_publish_mount_tf(self) -> None:
        """Publish base_link to oak_mount using the gravity-measured camera rotation.

        Needs the calibrated up-vector and the driver's IMU to camera-body
        extrinsic. Retries each tick until both are available.
        """
        if self._mount_tf_done:
            return
        # Log the blocker so a silent retry is not confused with a healthy wait.
        if self._imu_frame is None:
            self.get_logger().warning(
                'camera mount TF pending: no IMU message received yet',
                throttle_duration_sec=10.0)
            return
        if self._g_sensor is None:
            self.get_logger().warning(
                'camera mount TF pending: gravity calibration not finished '
                '(robot must be STILL on flat ground)',
                throttle_duration_sec=10.0)
            return
        cam_frame = self.get_parameter('camera_base_frame').value
        R_ic = None
        try:
            t = self._tf_buffer.lookup_transform(
                cam_frame, self._imu_frame, rclpy.time.Time())
            q = t.transform.rotation
            R_ic = _matrix_from_quat(q.x, q.y, q.z, q.w)
        except Exception:
            # OAK-D-LITE URDF never creates an IMU frame, so the lookup cannot
            # succeed; after a short grace period use imu_extrinsic_rpy instead.
            self._tf_misses = getattr(self, '_tf_misses', 0) + 1
            if self._tf_misses < 10:
                self.get_logger().warning(
                    f'camera mount TF: extrinsic {cam_frame} <- '
                    f'{self._imu_frame} not in TF (attempt '
                    f'{self._tf_misses}/10 before parameter fallback)',
                    throttle_duration_sec=5.0)
                return
            rpy = [float(v) for v in self.get_parameter('imu_extrinsic_rpy').value]
            R_ic = _matrix_from_rpy(*rpy)
            self.get_logger().warning(
                'camera mount TF: using imu_extrinsic_rpy parameter '
                f'{rpy} (no IMU frame in the driver URDF for this camera '
                'model). VERIFY the published pitch against the physical '
                'mount tilt.')
        # Up-vector from IMU frame expressed in camera body frame via extrinsic.
        u = _apply(R_ic, *self._g_sensor)
        R = _rotation_aligning(u)             # camera-body vectors to level frame
        # Gravity cannot observe yaw: rotate so camera body x-axis aligns with base_link +x.
        yaw = math.atan2(R[1][0], R[0][0])
        cz, sz = math.cos(-yaw), math.sin(-yaw)
        R = _matmul([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]], R)
        qx, qy, qz, qw = _quat_from_matrix(R)

        tf_msg = TransformStamped()
        tf_msg.header.stamp = self.get_clock().now().to_msg()
        tf_msg.header.frame_id = 'base_link'
        tf_msg.child_frame_id = self.get_parameter('camera_mount_frame').value
        tf_msg.transform.translation.x = float(self.get_parameter('mount_x').value)
        tf_msg.transform.translation.y = float(self.get_parameter('mount_y').value)
        tf_msg.transform.translation.z = float(self.get_parameter('mount_z').value)
        tf_msg.transform.rotation.x = qx
        tf_msg.transform.rotation.y = qy
        tf_msg.transform.rotation.z = qz
        tf_msg.transform.rotation.w = qw
        self._tf_static_pub.sendTransform(tf_msg)
        self._mount_tf_done = True
        self._mount_tf_timer.cancel()
        pitch_down = math.degrees(math.asin(max(-1.0, min(1.0, -R[2][0]))))
        self.get_logger().info(
            f'camera mount TF published: base_link to '
            f'{tf_msg.child_frame_id}, camera forward pitched '
            f'{pitch_down:+.1f} deg below horizontal (gravity-measured)')

    def _cb(self, msg: Imu) -> None:
        # Nothing is published until calibration finishes so EKF never sees uncorrected data.
        if self._imu_frame is None:
            self._imu_frame = msg.header.frame_id
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
        # -1 in [0] signals orientation not estimated; imu_filter_madgwick fills it.
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
