#!/usr/bin/env python3
"""block_tracker_fsm.py — Block-tracking FSM with direct motor control.

States
------
SEARCH  no block visible → spin in place to scan the environment
TRACK   block visible    → P-steer on camera centroid, drive forward
AVOID   obstacle ahead   → P-steer toward the clearer side

Inputs
------
/eyerobot/vision/lego_target  (geometry_msgs/Point)  camera-frame centroid
    .x > 0 → block to the right,  .x < 0 → block to the left
    .z     → depth in metres
/scan                          (sensor_msgs/LaserScan)

Outputs
-------
/motor_lwheel_cmd  (std_msgs/Float32)  rad/s  left  wheel
/motor_rwheel_cmd  (std_msgs/Float32)  rad/s  right wheel

Run
---
python3 block_tracker_fsm.py          # (ROS 2 must be sourced)
"""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Float32
from geometry_msgs.msg import Point
from sensor_msgs.msg import LaserScan

# ── Tuning ─────────────────────────────────────────────────────────────────
BASE_SPEED     = 10.0   # rad/s  cruising speed (both wheels equal)
SEARCH_SPIN    =  5.0   # rad/s  differential while spinning to search
KP_VISION      = 60.0   # P gain: lego.x (m) → wheel differential (rad/s)
KP_AVOID       = 10.0   # P gain: side imbalance (m) → wheel differential
AVOID_SPEED    =  5.0   # rad/s  base speed during avoidance

OBSTACLE_DIST  =  0.50  # m   — front range that triggers AVOID
FRONT_CONE     =   20   # scan indices each side of centre for front check
SIDE_CONE      =   80   # scan indices used per side for avoidance balance
TARGET_TIMEOUT =  0.5   # s   — lose target if silent for this long
# ───────────────────────────────────────────────────────────────────────────


class BlockTrackerFSM(Node):

    def __init__(self):
        super().__init__('block_tracker_fsm')

        self._l_pub = self.create_publisher(Float32, '/motor_lwheel_cmd', 10)
        self._r_pub = self.create_publisher(Float32, '/motor_rwheel_cmd', 10)

        self.create_subscription(Point, '/eyerobot/vision/lego_target',
                                 self._vision_cb, 10)
        self.create_subscription(LaserScan, '/scan',
                                 self._scan_cb, qos_profile_sensor_data)

        self._target = None
        self._last_t = 0.0
        self._scan   = None
        self._state  = 'SEARCH'

        self.create_timer(0.05, self._loop)  # 20 Hz control loop
        self.get_logger().info('BlockTrackerFSM ready  state=SEARCH')

    # ── Callbacks ──────────────────────────────────────────────────────────

    def _vision_cb(self, msg: Point):
        self._target = msg
        self._last_t = self.get_clock().now().nanoseconds * 1e-9

    def _scan_cb(self, msg: LaserScan):
        self._scan = msg

    # ── Lidar helpers ──────────────────────────────────────────────────────

    def _valid(self, values):
        return [x for x in values if not math.isnan(x) and not math.isinf(x) and x > 0.1]

    def _front_min(self) -> float:
        if self._scan is None:
            return float('inf')
        c = len(self._scan.ranges) // 2
        cone = self._valid(self._scan.ranges[c - FRONT_CONE: c + FRONT_CONE])
        return min(cone) if cone else float('inf')

    def _avoid_correction(self) -> float:
        """Positive → steer right (more room on right); negative → steer left."""
        if self._scan is None:
            return 0.0
        r = self._scan.ranges
        c = len(r) // 2
        # Right sector: negative angles (indices below centre)
        right = self._valid(r[c - FRONT_CONE - SIDE_CONE: c - FRONT_CONE])
        # Left sector: positive angles (indices above centre)
        left  = self._valid(r[c + FRONT_CONE: c + FRONT_CONE + SIDE_CONE])
        right_min = min(right) if right else 5.0
        left_min  = min(left)  if left  else 5.0
        return KP_AVOID * (right_min - left_min)

    # ── Motor output ───────────────────────────────────────────────────────

    def _motors(self, left: float, right: float):
        self._l_pub.publish(Float32(data=float(left)))
        self._r_pub.publish(Float32(data=float(right)))

    def _stop(self):
        self._motors(0.0, 0.0)

    # ── FSM ────────────────────────────────────────────────────────────────

    def _loop(self):
        now = self.get_clock().now().nanoseconds * 1e-9
        has_target = self._target is not None and (now - self._last_t) < TARGET_TIMEOUT
        obstacle   = self._front_min() < OBSTACLE_DIST

        # Transitions
        prev = self._state
        if self._state == 'SEARCH':
            if has_target:
                self._state = 'TRACK'
        elif self._state == 'TRACK':
            if obstacle:
                self._state = 'AVOID'
            elif not has_target:
                self._state = 'SEARCH'
        elif self._state == 'AVOID':
            if not obstacle:
                self._state = 'TRACK' if has_target else 'SEARCH'

        if self._state != prev:
            self.get_logger().info(f'{prev} -> {self._state}')

        # Actions
        if self._state == 'SEARCH':
            # Spin CCW in place: left backward, right forward
            self._motors(-SEARCH_SPIN, SEARCH_SPIN)

        elif self._state == 'TRACK':
            # lego.x > 0 (right) → corr > 0 → left faster, right slower → turn right
            corr = KP_VISION * self._target.x
            self._motors(BASE_SPEED + corr, BASE_SPEED - corr)

        elif self._state == 'AVOID':
            # corr > 0 (more room on right) → left faster, right slower → turn right
            corr = self._avoid_correction()
            self._motors(AVOID_SPEED + corr, AVOID_SPEED - corr)


def main(args=None):
    rclpy.init(args=args)
    node = BlockTrackerFSM()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node._stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
