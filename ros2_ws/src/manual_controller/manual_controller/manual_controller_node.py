#!/usr/bin/env python3
"""Fans and belt keyboard controller.

Driving is handled by teleop_twist_keyboard (→ /cmd_vel → cmd_vel_bridge).
This node only controls the fans and belt, which Twist cannot carry.

  tap q/e : fans forward / reverse  (latched, tap again to stop)
  tap r/t : belt forward / reverse  (latched, tap again to stop)
  space/x : stop fans and belt
  ctrl-c  : quit
"""
from __future__ import annotations

import math
import select
import sys
import termios
import threading
import time
import tty

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Float32


_HEADER = (
    '\n'
    'EyeRobot fans/belt controller\n'
    '  tap q/e: fans forward/reverse   (latched)\n'
    '  tap r/t: belt forward/reverse   (latched)\n'
    '  space or x: stop fans and belt\n'
    '  ctrl-c: quit\n'
    '\n'
    'Drive with teleop_twist_keyboard in another terminal.\n'
)


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

        self.declare_parameter('fan_command_rad_s',  8.0)
        self.declare_parameter('belt_command_rad_s', 8.0)
        self.declare_parameter('command_rate_hz',   20.0)
        self.declare_parameter('cmd_fans_topic', '/cmd_fans')
        self.declare_parameter('cmd_belt_topic', '/cmd_belt')

        self._fan_speed    = positive_float(self.get_parameter('fan_command_rad_s').value,  8.0)
        self._belt_speed   = positive_float(self.get_parameter('belt_command_rad_s').value, 8.0)
        self._command_rate = positive_float(self.get_parameter('command_rate_hz').value,   20.0)

        qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE,
                         history=HistoryPolicy.KEEP_LAST, depth=1)
        self._pub_fans = self.create_publisher(Float32, self.get_parameter('cmd_fans_topic').value, qos)
        self._pub_belt = self.create_publisher(Float32, self.get_parameter('cmd_belt_topic').value, qos)

        self._lock     = threading.Lock()
        self._cmd_fans = 0.0
        self._cmd_belt = 0.0

        self.create_timer(1.0 / self._command_rate, self._publish_command)
        self.get_logger().info('Fans/belt controller ready.')

    def apply_key(self, key: str) -> str | None:
        key = key.lower()
        fs, bs = self._fan_speed, self._belt_speed
        bindings = {
            'q': ('fans', fs,   'FANS >'),
            'e': ('fans', -fs,  'FANS <'),
            'r': ('belt', bs,   'BELT +'),
            't': ('belt', -bs,  'BELT -'),
            ' ': ('stop', 0.0,  'STOP'),
            'x': ('stop', 0.0,  'STOP'),
        }
        entry = bindings.get(key)
        if entry is None:
            return None
        group, value, label = entry

        with self._lock:
            if group == 'fans':
                self._cmd_fans = 0.0 if self._cmd_fans == value else value
            elif group == 'belt':
                self._cmd_belt = 0.0 if self._cmd_belt == value else value
            elif group == 'stop':
                self._cmd_fans = 0.0
                self._cmd_belt = 0.0
        return label

    def stop(self) -> None:
        with self._lock:
            self._cmd_fans = 0.0
            self._cmd_belt = 0.0
        for _ in range(3):
            self._publish_command()
            time.sleep(0.02)

    def _publish_command(self) -> None:
        with self._lock:
            fans = self._cmd_fans
            belt = self._cmd_belt
        self._pub_fans.publish(Float32(data=fans))
        self._pub_belt.publish(Float32(data=belt))


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

                with node._lock:
                    fans, belt = node._cmd_fans, node._cmd_belt
                sys.stdout.write(
                    f'\r  {label:<10}  fans={fans:+.1f}  belt={belt:+.1f}    \r'
                )
                sys.stdout.flush()

    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()
        print('\nFans and belt stopped.')


if __name__ == '__main__':
    main()
