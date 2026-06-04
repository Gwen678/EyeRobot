#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class KeyBinding:
    # Which motor group the key drives and the values it applies. 'wheels' are
    # momentary (held to run); 'fans'/'belt' toggle-latch (tap on, tap off);
    # 'stop' clears everything.
    group: str
    values: tuple[float, ...]
    label: str


_HEADER = (
    '\n'
    'EyeRobot manual controller\n'
    '  hold w/s: forward/backward      (momentary)\n'
    '  hold a/d: pivot left/right      (momentary)\n'
    '  tap  q/e: fans  on/reverse      (latched, tap again to stop)\n'
    '  tap  r/t: belt  fwd/reverse     (latched, tap again to stop)\n'
    '  space or x: stop all\n'
    '  ctrl-c: quit\n'
    '\n'
    'Wheels stop ~release_timeout after you let go; fans/belt keep running\n'
    'until you tap their key again or hit stop.\n'
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

        self.declare_parameter('command_speed_rad_s', 8.0)
        self.declare_parameter('turn_speed_rad_s', 5.0)
        self.declare_parameter('fan_command_rad_s', 8.0)
        self.declare_parameter('belt_command_rad_s', 8.0)
        self.declare_parameter('command_rate_hz', 20.0)
        self.declare_parameter('release_timeout_s', 0.2)
        self.declare_parameter('right_command_sign', -1.0)
        self.declare_parameter('left_command_sign', 1.0)
        self.declare_parameter('rfan_command_sign', 1.0)
        self.declare_parameter('lfan_command_sign', 1.0)
        self.declare_parameter('belt_command_sign', 1.0)
        self.declare_parameter('right_cmd_topic', 'motor_rwheel_cmd')
        self.declare_parameter('left_cmd_topic', 'motor_lwheel_cmd')
        self.declare_parameter('rfan_cmd_topic', 'motor_rfan_cmd')
        self.declare_parameter('lfan_cmd_topic', 'motor_lfan_cmd')
        self.declare_parameter('belt_cmd_topic', 'motor_belt_cmd')

        self._command_speed = positive_float(
            self.get_parameter('command_speed_rad_s').value, 8.0
        )
        self._turn_speed = positive_float(
            self.get_parameter('turn_speed_rad_s').value, 5.0
        )
        self._fan_speed = positive_float(
            self.get_parameter('fan_command_rad_s').value, 8.0
        )
        self._belt_speed = positive_float(
            self.get_parameter('belt_command_rad_s').value, 8.0
        )
        self._command_rate = positive_float(
            self.get_parameter('command_rate_hz').value, 20.0
        )
        self._release_timeout = positive_float(
            self.get_parameter('release_timeout_s').value, 0.2
        )
        self._right_command_sign = finite_float(
            self.get_parameter('right_command_sign').value, 1.0
        )
        self._left_command_sign = finite_float(
            self.get_parameter('left_command_sign').value, 1.0
        )
        self._rfan_command_sign = finite_float(
            self.get_parameter('rfan_command_sign').value, 1.0
        )
        self._lfan_command_sign = finite_float(
            self.get_parameter('lfan_command_sign').value, 1.0
        )
        self._belt_command_sign = finite_float(
            self.get_parameter('belt_command_sign').value, 1.0
        )

        right_cmd_topic = str(self.get_parameter('right_cmd_topic').value)
        left_cmd_topic = str(self.get_parameter('left_cmd_topic').value)
        rfan_cmd_topic = str(self.get_parameter('rfan_cmd_topic').value)
        lfan_cmd_topic = str(self.get_parameter('lfan_cmd_topic').value)
        belt_cmd_topic = str(self.get_parameter('belt_cmd_topic').value)

        # Best-effort: commands are re-published continuously at command_rate,
        # so dropping a sample is harmless and avoids the reliable-QoS ACK
        # traffic / head-of-line stalls that starve the shared micro-ROS UART
        # (symptom: a single motor randomly stalls while others keep running).
        cmd_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self._pub_r = self.create_publisher(Float32, right_cmd_topic, cmd_qos)
        self._pub_l = self.create_publisher(Float32, left_cmd_topic, cmd_qos)
        self._pub_rfan = self.create_publisher(Float32, rfan_cmd_topic, cmd_qos)
        self._pub_lfan = self.create_publisher(Float32, lfan_cmd_topic, cmd_qos)
        self._pub_belt = self.create_publisher(Float32, belt_cmd_topic, cmd_qos)

        # Stored commands are the unsigned logical values; the per-motor sign is
        # applied only at publish time, so toggle comparisons stay exact.
        cs, ts = self._command_speed, self._turn_speed
        fs, bs = self._fan_speed, self._belt_speed
        self._bindings: dict[str, KeyBinding] = {
            'w': KeyBinding('wheels', (cs, cs), 'FORWARD'),
            's': KeyBinding('wheels', (-cs, -cs), 'BACKWARD'),
            'a': KeyBinding('wheels', (-ts, ts), 'TURN LEFT'),
            'd': KeyBinding('wheels', (ts, -ts), 'TURN RIGHT'),
            ' ': KeyBinding('stop', (), 'STOP'),
            'x': KeyBinding('stop', (), 'STOP'),
            # Fans are mechanically coupled to spin opposite each other.
            'q': KeyBinding('fans', (fs, -fs), 'FANS >'),
            'e': KeyBinding('fans', (-fs, fs), 'FANS <'),
            'r': KeyBinding('belt', (bs,), 'BELT +'),
            't': KeyBinding('belt', (-bs,), 'BELT -'),
        }

        now_s = time.monotonic()
        self._lock = threading.Lock()
        self._cmd_right = 0.0
        self._cmd_left = 0.0
        self._cmd_rfan = 0.0
        self._cmd_lfan = 0.0
        self._cmd_belt = 0.0
        # Wheels are momentary: key auto-repeat refreshes this timestamp while a
        # wheel key is held; once it stops repeating, _publish_command zeroes the
        # wheels after release_timeout. Fans/belt are latched and ignore it.
        self._last_wheel_press_s = now_s

        self.create_timer(1.0 / self._command_rate, self._publish_command)

        self.get_logger().info(
            'Manual controller ready. Hold w/a/s/d to drive; tap q/e and r/t to '
            'toggle fans and belt. space/x stops all.'
        )

    def apply_key(self, key: str) -> str | None:
        key = key.lower()
        binding = self._bindings.get(key)
        if binding is None:
            return None

        now_s = time.monotonic()
        with self._lock:
            if binding.group == 'wheels':
                self._cmd_right, self._cmd_left = binding.values
                self._last_wheel_press_s = now_s
            elif binding.group == 'fans':
                # Toggle: tapping the active direction stops the fans, any other
                # tap (re)sets the requested direction.
                if (self._cmd_rfan, self._cmd_lfan) == binding.values:
                    self._cmd_rfan, self._cmd_lfan = 0.0, 0.0
                else:
                    self._cmd_rfan, self._cmd_lfan = binding.values
            elif binding.group == 'belt':
                (target,) = binding.values
                self._cmd_belt = 0.0 if self._cmd_belt == target else target
            elif binding.group == 'stop':
                self._cmd_right = 0.0
                self._cmd_left = 0.0
                self._cmd_rfan = 0.0
                self._cmd_lfan = 0.0
                self._cmd_belt = 0.0
        # Do NOT publish here. Key auto-repeat fires this dozens of times per
        # second; publishing per-keypress makes the wire rate track how the key
        # is held and floods the shared micro-ROS UART. The fixed-rate timer
        # (_publish_command at command_rate) is the single publishing path.
        return binding.label

    def stop(self) -> None:
        with self._lock:
            self._cmd_right = 0.0
            self._cmd_left = 0.0
            self._cmd_rfan = 0.0
            self._cmd_lfan = 0.0
            self._cmd_belt = 0.0

        for _ in range(3):
            self._publish_command()
            time.sleep(0.02)

    def command_snapshot(self) -> tuple[float, float, float, float, float]:
        with self._lock:
            return (
                self._cmd_right,
                self._cmd_left,
                self._cmd_rfan,
                self._cmd_lfan,
                self._cmd_belt,
            )

    def _publish_command(self) -> None:
        # Wheels are momentary: zero them once their key stops auto-repeating.
        # Fans/belt are latched and keep their value until toggled or stopped.
        now_s = time.monotonic()
        with self._lock:
            if (now_s - self._last_wheel_press_s) > self._release_timeout:
                self._cmd_right = 0.0
                self._cmd_left = 0.0

            right = self._cmd_right * self._right_command_sign
            left = self._cmd_left * self._left_command_sign
            rfan = self._cmd_rfan * self._rfan_command_sign
            lfan = self._cmd_lfan * self._lfan_command_sign
            belt = self._cmd_belt * self._belt_command_sign

        self._pub_r.publish(Float32(data=right))
        self._pub_l.publish(Float32(data=left))
        self._pub_rfan.publish(Float32(data=rfan))
        self._pub_lfan.publish(Float32(data=lfan))
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

                right, left, rfan, lfan, belt = node.command_snapshot()
                sys.stdout.write(
                    f'\r  {label:<12}  '
                    f'R={right:+.1f} L={left:+.1f}  '
                    f'fan={rfan:+.1f}/{lfan:+.1f}  '
                    f'belt={belt:+.1f}    \r'
                )
                sys.stdout.flush()

    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()
        print('\nMotors stopped.')


if __name__ == '__main__':
    main()
