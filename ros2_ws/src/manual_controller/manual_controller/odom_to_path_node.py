#!/usr/bin/env python3
"""Relay nav_msgs/Odometry to nav_msgs/Path for RViz.

Accumulates EKF poses into a Path so the fused trajectory shows as a continuous line.
"""
from __future__ import annotations

import math
import rclpy
from geometry_msgs.msg import PoseStamped, Vector3
from nav_msgs.msg import Odometry, Path
from rclpy.node import Node


class OdomToPathNode(Node):
    def __init__(self) -> None:
        super().__init__('odom_to_path')
        self.declare_parameter('odom_topic', '/odometry/filtered')
        self.declare_parameter('path_topic', '/ekf_path')
        self.declare_parameter('pose2d_topic', 'pose2d_ekf')
        self.declare_parameter('path_max_len', 2000)
        odom_topic = str(self.get_parameter('odom_topic').value)
        path_topic = str(self.get_parameter('path_topic').value)
        pose2d_topic = str(self.get_parameter('pose2d_topic').value)
        self._max_len = max(1, int(self.get_parameter('path_max_len').value))

        self._path = Path()
        self._pub = self.create_publisher(Path, path_topic, 10)
        # Human-readable pose: x (m), y (m), z = yaw (deg).
        # Echo /pose2d_ekf or /pose2d_wheel to read it.
        self._pose2d_pub = self.create_publisher(Vector3, pose2d_topic, 10)
        self.create_subscription(Odometry, odom_topic, self._cb, 10)
        self.get_logger().info(
            f'Relaying {odom_topic} to {path_topic} as nav_msgs/Path.')

    def _cb(self, msg: Odometry) -> None:
        # Path uses the odometry frame; each pose is one EKF sample.
        self._path.header = msg.header
        ps = PoseStamped()
        ps.header = msg.header
        ps.pose = msg.pose.pose
        self._path.poses.append(ps)
        if len(self._path.poses) > self._max_len:
            self._path.poses = self._path.poses[-self._max_len:]
        self._pub.publish(self._path)

        q = msg.pose.pose.orientation
        yaw_deg = math.degrees(math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                                          1.0 - 2.0 * (q.y * q.y + q.z * q.z)))
        self._pose2d_pub.publish(Vector3(
            x=msg.pose.pose.position.x,
            y=msg.pose.pose.position.y,
            z=yaw_deg,
        ))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = OdomToPathNode()
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
