#!/usr/bin/env python3
"""Fans and belt bridge.

Wheels are handled by diff_drive_controller (ros2_control).
This node only forwards /cmd_fans and /cmd_belt to the motor topics,
applying per-motor sign corrections and the mechanical fan coupling (lfan = -rfan).
"""
from __future__ import annotations
import math

import rclpy
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

        self.declare_parameter('rfan_command_sign', 1.0)
        self.declare_parameter('lfan_command_sign', 1.0)
        self.declare_parameter('belt_command_sign', 1.0)
        self.declare_parameter('cmd_fans_topic',  '/cmd_fans')
        self.declare_parameter('cmd_belt_topic',  '/cmd_belt')
        self.declare_parameter('rfan_cmd_topic',  'motor_rfan_cmd')
        self.declare_parameter('lfan_cmd_topic',  'motor_lfan_cmd')
        self.declare_parameter('belt_cmd_topic',  'motor_belt_cmd')

        self._rfan_sign = finite_float(self.get_parameter('rfan_command_sign').value, 1.0)
        self._lfan_sign = finite_float(self.get_parameter('lfan_command_sign').value, 1.0)
        self._belt_sign = finite_float(self.get_parameter('belt_command_sign').value, 1.0)

        motor_qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                               history=HistoryPolicy.KEEP_LAST, depth=1)
        sub_qos   = QoSProfile(reliability=ReliabilityPolicy.RELIABLE,
                               history=HistoryPolicy.KEEP_LAST, depth=1)

        self._rfan_pub = self.create_publisher(Float32, self.get_parameter('rfan_cmd_topic').value, motor_qos)
        self._lfan_pub = self.create_publisher(Float32, self.get_parameter('lfan_cmd_topic').value, motor_qos)
        self._belt_pub = self.create_publisher(Float32, self.get_parameter('belt_cmd_topic').value, motor_qos)

        self.create_subscription(Float32, self.get_parameter('cmd_fans_topic').value, self._cb_fans, sub_qos)
        self.create_subscription(Float32, self.get_parameter('cmd_belt_topic').value, self._cb_belt, sub_qos)

        self.get_logger().info('Fans/belt bridge ready (wheels handled by diff_drive_controller).')

    def _cb_fans(self, msg: Float32) -> None:
        val = float(msg.data)
        self._rfan_pub.publish(Float32(data=float(self._rfan_sign *  val)))
        self._lfan_pub.publish(Float32(data=float(self._lfan_sign * -val)))

    def _cb_belt(self, msg: Float32) -> None:
        self._belt_pub.publish(Float32(data=float(self._belt_sign * float(msg.data))))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CmdVelBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        for pub in (node._rfan_pub, node._lfan_pub, node._belt_pub):
            pub.publish(Float32(data=0.0))
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
