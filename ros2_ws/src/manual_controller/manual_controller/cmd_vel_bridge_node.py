#!/usr/bin/env python3
"""Convert geometry_msgs/Twist (/cmd_vel) to per-wheel Float32 speed commands.

Nav2's controller_server publishes /cmd_vel (linear.x m/s, angular.z rad/s).
The EyeRobot firmware expects per-wheel setpoints in rad/s on:
  motor_rwheel_cmd  (std_msgs/Float32)
  motor_lwheel_cmd  (std_msgs/Float32)

Differential-drive kinematics:
  v_right = (linear.x + angular.z * wheel_separation / 2) / wheel_radius
  v_left  = (linear.x - angular.z * wheel_separation / 2) / wheel_radius

Safety: if no /cmd_vel arrives within timeout_s, publish 0 to both wheels.
"""
from __future__ import annotations
import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Float32


def finite_float(value: object, fallback: float) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return fallback
    return f if math.isfinite(f) else fallback


def positive_float(value: object, fallback: float) -> float:
    f = finite_float(value, fallback)
    return f if f > 0.0 else fallback


class CmdVelBridgeNode(Node):
    def __init__(self) -> None:
        super().__init__('cmd_vel_bridge')

        self.declare_parameter('wheel_radius_m',    0.06)
        self.declare_parameter('wheel_separation_m', 0.33)
        self.declare_parameter('max_wheel_rad_s',    9.0)   # hard clamp — protect motors
        self.declare_parameter('right_command_sign', 1.0)
        self.declare_parameter('left_command_sign',  1.0)
        self.declare_parameter('cmd_vel_topic',      '/cmd_vel')
        self.declare_parameter('right_cmd_topic',    'motor_rwheel_cmd')
        self.declare_parameter('left_cmd_topic',     'motor_lwheel_cmd')
        # Stop motors if no /cmd_vel arrives within this window (Nav2 already
        # sends zero-velocity when stopped, but this is a belt-and-suspenders).
        self.declare_parameter('timeout_s', 0.5)

        self._radius     = positive_float(self.get_parameter('wheel_radius_m').value,     0.06)
        self._separation = positive_float(self.get_parameter('wheel_separation_m').value, 0.33)
        self._max_speed  = positive_float(self.get_parameter('max_wheel_rad_s').value,    9.0)
        self._r_sign     = finite_float(self.get_parameter('right_command_sign').value,   1.0)
        self._l_sign     = finite_float(self.get_parameter('left_command_sign').value,    1.0)
        self._timeout    = positive_float(self.get_parameter('timeout_s').value,           0.5)

        cmd_vel_topic  = str(self.get_parameter('cmd_vel_topic').value)
        right_cmd      = str(self.get_parameter('right_cmd_topic').value)
        left_cmd       = str(self.get_parameter('left_cmd_topic').value)

        pub_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self._r_pub = self.create_publisher(Float32, right_cmd, pub_qos)
        self._l_pub = self.create_publisher(Float32, left_cmd,  pub_qos)

        self.create_subscription(Twist, cmd_vel_topic, self._cb,
                                 QoSProfile(reliability=ReliabilityPolicy.RELIABLE,
                                            history=HistoryPolicy.KEEP_LAST, depth=1))

        self._last_msg_time = self.get_clock().now()
        self.create_timer(self._timeout / 2.0, self._watchdog)

        self.get_logger().info(
            f'cmd_vel bridge ready: r={self._radius:.3f} m  '
            f'base={self._separation:.3f} m  '
            f'max={self._max_speed:.1f} rad/s  '
            f'timeout={self._timeout:.2f} s')

    def _cb(self, msg: Twist) -> None:
        self._last_msg_time = self.get_clock().now()
        vx  = float(msg.linear.x)
        wz  = float(msg.angular.z)

        # Differential-drive inverse kinematics
        v_right = (vx + wz * self._separation / 2.0) / self._radius
        v_left  = (vx - wz * self._separation / 2.0) / self._radius

        # Clamp to motor limits
        v_right = max(-self._max_speed, min(self._max_speed, v_right))
        v_left  = max(-self._max_speed, min(self._max_speed, v_left))

        self._r_pub.publish(Float32(data=float(self._r_sign * v_right)))
        self._l_pub.publish(Float32(data=float(self._l_sign * v_left)))

    def _watchdog(self) -> None:
        age = (self.get_clock().now() - self._last_msg_time).nanoseconds * 1e-9
        if age > self._timeout:
            self._r_pub.publish(Float32(data=0.0))
            self._l_pub.publish(Float32(data=0.0))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CmdVelBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node._r_pub.publish(Float32(data=0.0))
        node._l_pub.publish(Float32(data=0.0))
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
