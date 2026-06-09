#!/usr/bin/env python3
"""Single motor interface: converts /cmd_vel, /cmd_fans, /cmd_belt to per-motor Float32 commands.

/cmd_vel  (Twist)   — wheels via differential-drive kinematics + acceleration ramp
/cmd_fans (Float32) — fan speed; +value = forward, bridge applies mechanical coupling (lfan = -rfan)
/cmd_belt (Float32) — belt speed; sign encodes direction

Motor topics published:
  motor_rwheel_cmd, motor_lwheel_cmd
  motor_rfan_cmd,   motor_lfan_cmd
  motor_belt_cmd
"""
from __future__ import annotations
import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Float32

_PUBLISH_RATE_HZ = 20.0


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

        self.declare_parameter('wheel_radius_m',     0.06)
        self.declare_parameter('wheel_separation_m', 0.33)
        self.declare_parameter('max_wheel_rad_s',    9.0)
        self.declare_parameter('accel_rad_s2',       18.0)
        self.declare_parameter('right_command_sign', 1.0)
        self.declare_parameter('left_command_sign',  1.0)
        self.declare_parameter('rfan_command_sign',  1.0)
        self.declare_parameter('lfan_command_sign',  1.0)
        self.declare_parameter('belt_command_sign',  1.0)
        self.declare_parameter('cmd_vel_topic',   '/cmd_vel')
        self.declare_parameter('cmd_fans_topic',  '/cmd_fans')
        self.declare_parameter('cmd_belt_topic',  '/cmd_belt')
        self.declare_parameter('right_cmd_topic', 'motor_rwheel_cmd')
        self.declare_parameter('left_cmd_topic',  'motor_lwheel_cmd')
        self.declare_parameter('rfan_cmd_topic',  'motor_rfan_cmd')
        self.declare_parameter('lfan_cmd_topic',  'motor_lfan_cmd')
        self.declare_parameter('belt_cmd_topic',  'motor_belt_cmd')
        self.declare_parameter('timeout_s', 0.5)

        self._radius     = positive_float(self.get_parameter('wheel_radius_m').value,     0.06)
        self._separation = positive_float(self.get_parameter('wheel_separation_m').value, 0.33)
        self._max_speed  = positive_float(self.get_parameter('max_wheel_rad_s').value,    9.0)
        self._accel      = positive_float(self.get_parameter('accel_rad_s2').value,       18.0)
        self._r_sign     = finite_float(self.get_parameter('right_command_sign').value,   1.0)
        self._l_sign     = finite_float(self.get_parameter('left_command_sign').value,    1.0)
        self._rfan_sign  = finite_float(self.get_parameter('rfan_command_sign').value,    1.0)
        self._lfan_sign  = finite_float(self.get_parameter('lfan_command_sign').value,    1.0)
        self._belt_sign  = finite_float(self.get_parameter('belt_command_sign').value,    1.0)
        self._timeout    = positive_float(self.get_parameter('timeout_s').value,           0.5)

        motor_qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                               history=HistoryPolicy.KEEP_LAST, depth=1)
        sub_qos   = QoSProfile(reliability=ReliabilityPolicy.RELIABLE,
                               history=HistoryPolicy.KEEP_LAST, depth=1)

        self._r_pub    = self.create_publisher(Float32, self.get_parameter('right_cmd_topic').value, motor_qos)
        self._l_pub    = self.create_publisher(Float32, self.get_parameter('left_cmd_topic').value,  motor_qos)
        self._rfan_pub = self.create_publisher(Float32, self.get_parameter('rfan_cmd_topic').value,  motor_qos)
        self._lfan_pub = self.create_publisher(Float32, self.get_parameter('lfan_cmd_topic').value,  motor_qos)
        self._belt_pub = self.create_publisher(Float32, self.get_parameter('belt_cmd_topic').value,  motor_qos)

        self.create_subscription(Twist,   self.get_parameter('cmd_vel_topic').value,  self._cb_vel,  sub_qos)
        self.create_subscription(Float32, self.get_parameter('cmd_fans_topic').value, self._cb_fans, sub_qos)
        self.create_subscription(Float32, self.get_parameter('cmd_belt_topic').value, self._cb_belt, sub_qos)

        self._target_right = 0.0
        self._target_left  = 0.0
        self._actual_right = 0.0
        self._actual_left  = 0.0
        self._fans_cmd     = 0.0   # latched — not zeroed by watchdog
        self._belt_cmd     = 0.0   # latched — not zeroed by watchdog
        self._last_vel_time = self.get_clock().now()

        self.create_timer(1.0 / _PUBLISH_RATE_HZ, self._publish)

        self.get_logger().info(
            f'cmd_vel bridge ready: r={self._radius:.3f} m  base={self._separation:.3f} m  '
            f'max={self._max_speed:.1f} rad/s  accel={self._accel:.1f} rad/s²')

    def _cb_vel(self, msg: Twist) -> None:
        self._last_vel_time = self.get_clock().now()
        vx = float(msg.linear.x)
        wz = float(msg.angular.z)
        v_right = (vx + wz * self._separation / 2.0) / self._radius
        v_left  = (vx - wz * self._separation / 2.0) / self._radius
        self._target_right = max(-self._max_speed, min(self._max_speed, v_right))
        self._target_left  = max(-self._max_speed, min(self._max_speed, v_left))

    def _cb_fans(self, msg: Float32) -> None:
        # Fans are mechanically coupled: lfan always spins opposite rfan.
        self._fans_cmd = float(msg.data)

    def _cb_belt(self, msg: Float32) -> None:
        self._belt_cmd = float(msg.data)

    @staticmethod
    def _ramp(actual: float, target: float, max_step: float) -> float:
        diff = target - actual
        if abs(diff) <= max_step:
            return target
        return actual + math.copysign(max_step, diff)

    def _publish(self) -> None:
        age = (self.get_clock().now() - self._last_vel_time).nanoseconds * 1e-9
        if age > self._timeout:
            self._target_right = 0.0
            self._target_left  = 0.0

        max_step = self._accel / _PUBLISH_RATE_HZ
        self._actual_right = self._ramp(self._actual_right, self._target_right, max_step)
        self._actual_left  = self._ramp(self._actual_left,  self._target_left,  max_step)

        self._r_pub.publish(Float32(data=float(self._r_sign * self._actual_right)))
        self._l_pub.publish(Float32(data=float(self._l_sign * self._actual_left)))
        self._rfan_pub.publish(Float32(data=float(self._rfan_sign * self._fans_cmd)))
        self._lfan_pub.publish(Float32(data=float(self._lfan_sign * -self._fans_cmd)))
        self._belt_pub.publish(Float32(data=float(self._belt_sign * self._belt_cmd)))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CmdVelBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        for pub in (node._r_pub, node._l_pub, node._rfan_pub, node._lfan_pub, node._belt_pub):
            pub.publish(Float32(data=0.0))
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
