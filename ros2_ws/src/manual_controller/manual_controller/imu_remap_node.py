#!/usr/bin/env python3
"""Axis sign correction relay: depthai_ros_driver frame → REP-103 frame.

The OAK-D Lite BMI270 is mounted at 180° about X relative to the robot body
(REP-103: X forward, Y left, Z up).  That rotation negates the Y and Z axes of
both the accelerometer and gyroscope.  Signs are read from ROS parameters so
they can be tuned in YAML without touching code.

Pipeline:
  depthai_ros_driver  →  /oak/imu  →  [this node]  →  /oak/imu/data_raw
  →  imu_filter_madgwick  →  /oak/imu/data
"""
from __future__ import annotations
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Imu


class ImuRemapNode(Node):
    def __init__(self) -> None:
        super().__init__('imu_remap')
        self.declare_parameter('accel_signs',  [1.0, -1.0, -1.0])
        self.declare_parameter('gyro_signs',   [1.0, -1.0, -1.0])
        self.declare_parameter('input_topic',  '/oak/imu')
        self.declare_parameter('output_topic', '/oak/imu/data_raw')
        self.declare_parameter('frame_id',     'imu_link')

        a = self.get_parameter('accel_signs').value
        g = self.get_parameter('gyro_signs').value
        self._ax, self._ay, self._az = float(a[0]), float(a[1]), float(a[2])
        self._gx, self._gy, self._gz = float(g[0]), float(g[1]), float(g[2])
        self._frame = self.get_parameter('frame_id').value

        # BMI270 covariances from 61-min Allan variance calibration (2026-06-08).
        # Measurement noise = ARW² × 200 Hz; diagonal 3×3 in row-major order.
        self._gyro_cov  = [1.65e-6, 0., 0., 0., 1.84e-6, 0., 0., 0., 1.52e-6]
        self._accel_cov = [0.01, 0., 0., 0., 0.01, 0., 0., 0., 0.01]

        qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                         history=HistoryPolicy.KEEP_LAST, depth=10)

        in_t  = self.get_parameter('input_topic').value
        out_t = self.get_parameter('output_topic').value
        self._pub = self.create_publisher(Imu, out_t, qos)
        self.create_subscription(Imu, in_t, self._cb, qos)
        self.get_logger().info(
            f'{in_t} → {out_t}  accel=({self._ax},{self._ay},{self._az})'
            f'  gyro=({self._gx},{self._gy},{self._gz})')

    def _cb(self, msg: Imu) -> None:
        out = Imu()
        out.header = msg.header
        out.header.frame_id = self._frame
        out.linear_acceleration.x = self._ax * msg.linear_acceleration.x
        out.linear_acceleration.y = self._ay * msg.linear_acceleration.y
        out.linear_acceleration.z = self._az * msg.linear_acceleration.z
        out.angular_velocity.x = self._gx * msg.angular_velocity.x
        out.angular_velocity.y = self._gy * msg.angular_velocity.y
        out.angular_velocity.z = self._gz * msg.angular_velocity.z
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
