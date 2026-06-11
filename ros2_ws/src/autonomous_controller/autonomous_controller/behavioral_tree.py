#!/usr/bin/env python3
import argparse
import math

import rclpy
from rclpy.action import ActionClient
from rclpy.time import Time
import py_trees
import py_trees_ros
from py_trees.common import Status
from tf2_ros import Buffer, TransformListener

# ROS 2 Navigation Messages
from geometry_msgs.msg import PoseStamped, PointStamped, Twist
from nav2_msgs.action import NavigateToPose, NavigateThroughPoses
from nav_msgs.msg import Path as NavPath
from visualization_msgs.msg import Marker, MarkerArray
from action_msgs.msg import GoalStatus
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
from rclpy.qos import qos_profile_sensor_data

# Intake actuation (cmd_vel_bridge forwards these to the motor topics).
# 8.0 rad/s matches the teleop defaults (fan/belt_command_rad_s).
FAN_SPEED = 8.0
BELT_SPEED = 8.0
DISCHARGE_SECONDS = 5.0
DISCHARGE_BLOCK_COUNT = 5   # go unload at base once this many blocks were collected

VERBOSE = True

# Pullback retry distances (meters). If Nav2 cannot plan through a target
# (e.g. a lego block sitting against a wall, inside the costmap inflation
# radius), we retry with that pose pulled back along its approach line. The
# robot then passes nose-first just short of the block and the front fans
# absorb it on the close pass — we never need to physically reach the
# block's center.
PULLBACK_OFFSETS = (0.0, 0.25, 0.45)

# Pause between navigation retries: an instant resend after an abort burns all
# attempts in milliseconds on transient failures (e.g. Nav2's planner/costmap
# servers still activating when the first goal lands).
RETRY_DELAY_S = 2.0

# ── Calibrated mission frame ────────────────────────────────────────────────
# clean_room_8x8.yaml is re-zeroed so the user-picked origin pixel
# (120.3, 104.3) becomes map (0,0). We keep arena_to_map() as a no-op so the
# BT call sites stay stable, but the calibrated mission poses below are now
# authored directly in this map frame, using the colored markers in ref.png.
ARENA_ORIGIN_IN_MAP = (0.0, 0.0)


def arena_to_map(x, y):
    """Identity transform retained so existing BT call sites do not change."""
    return (x + ARENA_ORIGIN_IN_MAP[0], y + ARENA_ORIGIN_IN_MAP[1])


def _yaw_to_quat(pose, yaw):
    """Write a planar yaw into a geometry_msgs Pose orientation."""
    pose.orientation.z = math.sin(yaw / 2.0)
    pose.orientation.w = math.cos(yaw / 2.0)


def _robot_xy(tf_buffer):
    """Current robot position in the map frame, or None if TF is not up yet."""
    try:
        t = tf_buffer.lookup_transform("map", "base_link", Time())
        return t.transform.translation.x, t.transform.translation.y
    except Exception:
        return None


def _shared_tf_buffer(node):
    """One TF buffer shared by all behaviors (each TransformListener subscribes
    to /tf, so we only want a single one on the node)."""
    if not hasattr(node, "bt_tf_buffer"):
        node.bt_tf_buffer = Buffer()
        node.bt_tf_listener = TransformListener(node.bt_tf_buffer, node)
    return node.bt_tf_buffer


class BlockMemory:
    """Accumulates lego detections from /eyerobot/vision/lego_markers_map.

    Detections within MERGE_RADIUS of a known block are the same block (the
    vision node re-publishes tracked blocks every frame). A block the robot
    has passed within EAT_RADIUS of is removed — with the roomba intake,
    driving over a block IS collecting it. This makes block counts real:
    "collect 5 then discharge" counts actual known blocks, not guesses.
    """
    MERGE_RADIUS = 0.30
    EAT_RADIUS = 0.35

    # Reachable-block gate, map frame: the room's free space as measured on
    # clean_room_8x8.pgm under the calibrated origin (x right from the arena
    # corner, interior at negative y). Vision occasionally projects false
    # positives outside the walls (HSV matches through openings, TF timing
    # noise) — routing to one sends Nav2 outside the map, the planner aborts,
    # and the whole route burns its retries. Anything outside this rectangle
    # is not a collectable block by definition.
    X_RANGE = (0.0, 8.8)
    Y_RANGE = (-8.0, 0.0)

    def __init__(self, node, tf_buffer):
        self.node = node
        self.tf_buffer = tf_buffer
        self.blocks = []  # [(x, y)] map frame
        self.collected_since_discharge = 0  # drives the discharge-at-5 trigger
        node.create_subscription(
            PointStamped, '/eyerobot/vision/lego_markers_map', self._on_detection, 10)
        # Foxglove visualization: known blocks as green cubes on /bt/blocks.
        self.marker_pub = node.create_publisher(MarkerArray, '/bt/blocks', 10)
        node.create_timer(0.5, self._prune_eaten)

    def _on_detection(self, msg):
        p = (msg.point.x, msg.point.y)
        if not (self.X_RANGE[0] <= p[0] <= self.X_RANGE[1]
                and self.Y_RANGE[0] <= p[1] <= self.Y_RANGE[1]):
            # Throttled: the vision node re-publishes tracked blocks at frame
            # rate, so an out-of-bounds ghost would otherwise spam the log.
            self.node.get_logger().warning(
                f"[blocks] IGNORED out-of-arena detection at map "
                f"({p[0]:.2f}, {p[1]:.2f})", throttle_duration_sec=5.0)
            return
        for b in self.blocks:
            if math.hypot(b[0] - p[0], b[1] - p[1]) < self.MERGE_RADIUS:
                return
        self.blocks.append(p)
        self.node.get_logger().info(
            f"[blocks] new block at map ({p[0]:.2f}, {p[1]:.2f}) — {len(self.blocks)} known")

    def _prune_eaten(self):
        robot = _robot_xy(self.tf_buffer)
        if robot is None:
            return
        kept = [b for b in self.blocks
                if math.hypot(b[0] - robot[0], b[1] - robot[1]) > self.EAT_RADIUS]
        eaten = len(self.blocks) - len(kept)
        if eaten:
            self.collected_since_discharge += eaten
            self.node.get_logger().info(
                f"[blocks] collected {eaten} block(s) — {len(kept)} known left, "
                f"{self.collected_since_discharge} on board since last discharge")
        self.blocks = kept
        self._publish_markers()

    def _publish_markers(self):
        """Known blocks as green cubes (DELETEALL first so eaten ones vanish)."""
        arr = MarkerArray()
        wipe = Marker()
        wipe.header.frame_id = "map"
        wipe.action = Marker.DELETEALL
        arr.markers.append(wipe)
        stamp = self.node.get_clock().now().to_msg()
        for i, (x, y) in enumerate(self.blocks):
            m = Marker()
            m.header.frame_id = "map"
            m.header.stamp = stamp
            m.ns = "blocks"
            m.id = i
            m.type = Marker.CUBE
            m.action = Marker.ADD
            m.pose.position.x = x
            m.pose.position.y = y
            m.pose.position.z = 0.02
            m.pose.orientation.w = 1.0
            m.scale.x = m.scale.y = m.scale.z = 0.08
            m.color.g = 1.0
            m.color.a = 0.9
            arr.markers.append(m)
        self.marker_pub.publish(arr)


def _route_publisher(node):
    """Shared /bt/route publisher: the goals the BT just sent to Nav2, as a
    nav_msgs/Path — drop the topic on a Foxglove 3D panel to see where the
    robot is being sent (distinct from /plan, Nav2's computed path there)."""
    if not hasattr(node, "bt_route_pub"):
        node.bt_route_pub = node.create_publisher(NavPath, '/bt/route', 10)
    return node.bt_route_pub


def _publish_route(node, poses):
    path = NavPath()
    path.header.frame_id = "map"
    path.header.stamp = node.get_clock().now().to_msg()
    path.poses = list(poses)
    _route_publisher(node).publish(path)


def _shared_block_memory(node, tf_buffer):
    if not hasattr(node, "bt_block_memory"):
        node.bt_block_memory = BlockMemory(node, tf_buffer)
    return node.bt_block_memory


def _wait_for_server_verbose(behaviour, action_name):
    """Block setup until the Nav2 action server exists, logging while waiting.

    Nav2's lifecycle bringup takes 30-60+ s on the Jetson Nano, so a bare
    wait_for_server() looks like a hang and overruns any finite tree-setup
    timeout (the mission must NOT start without Nav2 anyway — see main()).
    """
    waited = 0
    while not behaviour.action_client.wait_for_server(timeout_sec=5.0):
        waited += 5
        behaviour.logger.info(
            f"[{behaviour.name}] waiting for '{action_name}' action server "
            f"({waited} s — Nav2 still starting up?)")


class WaitForLocalization(py_trees.behaviour.Behaviour):
    """Blocks the mission until AMCL is localized (map→base_link TF resolves).

    This is the launch-file replacement for the old press-ENTER gate in
    run_autonomous.sh: nav2 AMCL publishes map→odom only after it receives an
    initial pose, so the mission waits here until you set it in Foxglove
    (Set pose tool), then starts on its own. Deliberately NOT wrapped in a
    timeout — starting unlocalized would send the robot to wrong places.
    """
    def __init__(self, name="Wait_For_Localization"):
        super().__init__(name)
        self.node = None
        self._last_log_s = 0.0

    def setup(self, **kwargs):
        self.node = kwargs.get("node")
        if self.node is None:
            self.logger.error(f"[{self.name}] ROS 2 node context not found in setup!")
            raise RuntimeError("ROS 2 node context missing.")
        self.tf_buffer = _shared_tf_buffer(self.node)

    def update(self) -> Status:
        if _robot_xy(self.tf_buffer) is not None:
            self.logger.info(f"[{self.name}] AMCL localized — starting the mission.")
            return Status.SUCCESS
        now_s = self.node.get_clock().now().nanoseconds * 1e-9
        if now_s - self._last_log_s > 5.0:
            self._last_log_s = now_s
            self.logger.info(
                f"[{self.name}] Waiting for localization — set the initial pose "
                "in Foxglove (Set pose tool).")
        return Status.RUNNING


class GoToPose(py_trees.behaviour.Behaviour):
    """A reusable Behavior Tree leaf node that sends the robot to specific coordinates via Nav2.

    target_yaw: final heading in radians (map frame). None = face along the
    approach direction (right for flow-through collection); set it explicitly
    when the arrival heading matters (facing the button, the drop-off, ...).
    """
    def __init__(self, name="Go_To_Pose", target_x=0.0, target_y=0.0, target_yaw=None):
        super().__init__(name)
        self.target_x = target_x
        self.target_y = target_y
        self.target_yaw = target_yaw

        self.node = None
        self.action_client = None
        self.goal_handle = None
        self.goal_status = None
        self.tick_count = 0
        self.attempt = 0
        self._retry_at_s = None

    def setup(self, **kwargs):
        """Extracts the ROS 2 node from the py_trees_ros environment setup."""
        self.node = kwargs.get("node")
        if self.node is None:
            self.logger.error(f"[{self.name}] ROS 2 node context not found in setup!")
            raise RuntimeError("ROS 2 node context missing.")

        self.action_client = ActionClient(self.node, NavigateToPose, 'navigate_to_pose')
        _wait_for_server_verbose(self, 'navigate_to_pose')
        self.tf_buffer = _shared_tf_buffer(self.node)

    def _now_s(self):
        return self.node.get_clock().now().nanoseconds * 1e-9

    def _send_goal(self, pullback):
        """Send the Nav2 goal, optionally pulled back toward the robot by `pullback` meters.

        The goal heading always points from the robot THROUGH the target, so the
        front intake leads and the block is swallowed as the robot arrives.
        """
        self.goal_status = None
        self.goal_handle = None

        gx, gy, yaw = self.target_x, self.target_y, None
        robot = _robot_xy(self.tf_buffer)
        if robot is not None:
            dx, dy = self.target_x - robot[0], self.target_y - robot[1]
            dist = math.hypot(dx, dy)
            if dist > 1e-3:
                yaw = math.atan2(dy, dx)
                if pullback > 0.0:
                    # Stay on the approach line, `pullback` meters short of the target
                    # (clamped so we never plant the goal behind the robot).
                    back = min(pullback, max(dist - 0.05, 0.0))
                    gx -= back * dx / dist
                    gy -= back * dy / dist
        elif pullback > 0.0:
            self.logger.warning(f"[{self.name}] No map->base_link TF; retrying exact target without pullback.")

        # Explicit arrival heading (e.g. facing the button) beats the
        # approach-direction default.
        if self.target_yaw is not None:
            yaw = self.target_yaw

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.node.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = gx
        goal_msg.pose.pose.position.y = gy
        if yaw is not None:
            _yaw_to_quat(goal_msg.pose.pose, yaw)
        else:
            goal_msg.pose.pose.orientation.w = 1.0

        self.logger.info(
            f"[{self.name}] Goal: X={gx:.2f}, Y={gy:.2f}"
            + (f" (pullback {pullback} m)" if pullback > 0.0 else "")
        )
        _publish_route(self.node, [goal_msg.pose])
        send_goal_future = self.action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self._goal_response_callback)

    def initialise(self) -> None:
        """Fires every time the behavior switches from inactive to active."""
        self.tick_count = 0
        self.attempt = 0
        self._retry_at_s = None
        self._send_goal(PULLBACK_OFFSETS[0])

    def _goal_response_callback(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.logger.error(f"[{self.name}] Goal rejected by Nav2 planner!")
            self.goal_status = GoalStatus.STATUS_ABORTED
            return

        result_future = self.goal_handle.get_result_async()
        result_future.add_done_callback(self._goal_result_callback)

    def _goal_result_callback(self, future):
        self.goal_status = future.result().status

    def update(self) -> Status:
        """Evaluates every 50ms while this behavior is actively running."""
        self.tick_count += 1

        if VERBOSE and self.tick_count % 20 == 0:
            print(f"[{self.name}] Advancing to target coordinates... (Tick: {self.tick_count})")

        if self.goal_status is None:
            return Status.RUNNING

        if self.goal_status == GoalStatus.STATUS_SUCCEEDED:
            self.logger.info(f"[{self.name}] Target pose successfully reached!")
            return Status.SUCCESS

        if self.goal_status in [GoalStatus.STATUS_ABORTED, GoalStatus.STATUS_UNKNOWN]:
            # Infeasible target (e.g. block against a wall): pull the goal back
            # toward the robot and retry before giving up on this waypoint.
            # Retries are spaced RETRY_DELAY_S apart so a transient failure
            # (Nav2 servers still activating) doesn't burn all attempts at once.
            if self.attempt + 1 < len(PULLBACK_OFFSETS):
                if self._retry_at_s is None:
                    self._retry_at_s = self._now_s() + RETRY_DELAY_S
                    self.logger.warning(
                        f"[{self.name}] Nav2 aborted/rejected; retrying in {RETRY_DELAY_S} s.")
                    return Status.RUNNING
                if self._now_s() < self._retry_at_s:
                    return Status.RUNNING
                self._retry_at_s = None
                self.attempt += 1
                offset = PULLBACK_OFFSETS[self.attempt]
                self.logger.warning(f"[{self.name}] retry {self.attempt} with {offset} m pullback.")
                self._send_goal(offset)
                return Status.RUNNING
            self.logger.error(f"[{self.name}] Nav2 failed to reach target after {self.attempt + 1} attempts.")
            return Status.FAILURE

        if self.goal_status == GoalStatus.STATUS_CANCELED:
            self.logger.error(f"[{self.name}] Navigation canceled.")
            return Status.FAILURE

        return Status.RUNNING

    def terminate(self, new_status: Status) -> None:
        """Fires automatically when the node stops running."""
        if new_status == Status.INVALID and self.goal_handle is not None:
            self.logger.warning(f"[{self.name}] Interrupted! Canceling active navigation.")
            self.goal_handle.cancel_goal_async()

        self.goal_handle = None
        self.goal_status = None


class GoThroughPoses(py_trees.behaviour.Behaviour):
    """Flow-through multi-waypoint navigation via Nav2's NavigateThroughPoses.

    The robot does NOT stop at intermediate poses — blocks are absorbed by the
    front fans as it drives over them (roomba-style collection). This behavior
    works around the Humble limitation that one infeasible segment aborts the
    WHOLE multi-pose goal: on abort we use the action feedback to find the
    suspect pose, pull it back along its approach line (PULLBACK_OFFSETS), and
    resend the remaining route; a pose that keeps failing is dropped so one
    unreachable block never kills the mission.
    """
    def __init__(self, name="Go_Through_Poses", waypoints=()):
        super().__init__(name)
        self.waypoints = [tuple(w) for w in waypoints]

        self.node = None
        self.action_client = None
        self.goal_handle = None
        self.goal_status = None
        self.tick_count = 0

        # Mission progress state (rebuilt in initialise)
        self.pending = []        # waypoints not yet reached
        self.pb_level = []       # per-pending-pose index into PULLBACK_OFFSETS
        self.sent_count = 0      # how many poses the active goal contains
        self.feedback_remaining = None
        self._retry_at_s = None

    def setup(self, **kwargs):
        """Extracts the ROS 2 node from the py_trees_ros environment setup."""
        self.node = kwargs.get("node")
        if self.node is None:
            self.logger.error(f"[{self.name}] ROS 2 node context not found in setup!")
            raise RuntimeError("ROS 2 node context missing.")

        self.action_client = ActionClient(self.node, NavigateThroughPoses, 'navigate_through_poses')
        _wait_for_server_verbose(self, 'navigate_through_poses')
        self.tf_buffer = _shared_tf_buffer(self.node)

    def _now_s(self):
        return self.node.get_clock().now().nanoseconds * 1e-9

    def _build_poses(self):
        """PoseStamped list for the pending waypoints.

        Each pose's heading points along its approach line (previous waypoint →
        this one; the robot's live position anchors the first), so the intake
        leads through every block. A pose with an active pullback level is
        shifted back along that same line.
        """
        stamp = self.node.get_clock().now().to_msg()
        poses = []
        prev = _robot_xy(self.tf_buffer)
        for (x, y), level in zip(self.pending, self.pb_level):
            gx, gy, yaw = x, y, None
            if prev is not None:
                dx, dy = x - prev[0], y - prev[1]
                dist = math.hypot(dx, dy)
                if dist > 1e-3:
                    yaw = math.atan2(dy, dx)
                    pullback = PULLBACK_OFFSETS[level]
                    if pullback > 0.0:
                        back = min(pullback, max(dist - 0.05, 0.0))
                        gx -= back * dx / dist
                        gy -= back * dy / dist
            ps = PoseStamped()
            ps.header.frame_id = "map"
            ps.header.stamp = stamp
            ps.pose.position.x = gx
            ps.pose.position.y = gy
            if yaw is not None:
                _yaw_to_quat(ps.pose, yaw)
            else:
                ps.pose.orientation.w = 1.0
            poses.append(ps)
            prev = (x, y)  # anchor the next heading on the original waypoint
        return poses

    def _send_goal(self):
        self.goal_status = None
        self.goal_handle = None
        self.feedback_remaining = None
        self.sent_count = len(self.pending)

        goal_msg = NavigateThroughPoses.Goal()
        goal_msg.poses = self._build_poses()
        _publish_route(self.node, goal_msg.poses)
        self.logger.info(f"[{self.name}] Routing through {self.sent_count} pose(s): {self.pending}")
        send_goal_future = self.action_client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_callback)
        send_goal_future.add_done_callback(self._goal_response_callback)

    def initialise(self) -> None:
        """Fires every time the behavior switches from inactive to active."""
        self.tick_count = 0
        self._retry_at_s = None
        self.pending = list(self.waypoints)
        self.pb_level = [0] * len(self.pending)
        if not self.pending:
            # Empty route (e.g. dynamic planner produced nothing): fail fast
            # instead of sending Nav2 a zero-pose goal.
            self.logger.warning(f"[{self.name}] No waypoints — nothing to do.")
            self.goal_status = GoalStatus.STATUS_ABORTED
            return
        self._send_goal()

    def _feedback_callback(self, feedback_msg):
        self.feedback_remaining = feedback_msg.feedback.number_of_poses_remaining

    def _goal_response_callback(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.logger.error(f"[{self.name}] Route rejected by Nav2 planner!")
            self.goal_status = GoalStatus.STATUS_ABORTED
            return

        result_future = self.goal_handle.get_result_async()
        result_future.add_done_callback(self._goal_result_callback)

    def _goal_result_callback(self, future):
        self.goal_status = future.result().status

    def _recover_from_abort(self):
        """Trim reached poses, pull back (or drop) the suspect, resend.

        Returns False when no poses are left to try.
        """
        # Feedback tells us how many poses were still ahead when the goal died:
        # everything before them was reached, and the first remaining pose is
        # the one Nav2 was working on (the suspect).
        rem = self.feedback_remaining
        if rem is not None and 0 < rem < self.sent_count:
            reached = self.sent_count - rem
            self.pending = self.pending[reached:]
            self.pb_level = self.pb_level[reached:]
            self.pb_level[0] = 0  # new suspect, start its pullback ladder fresh

        if not self.pending:
            return False

        if self.pb_level[0] + 1 < len(PULLBACK_OFFSETS):
            self.pb_level[0] += 1
            self.logger.warning(
                f"[{self.name}] Route aborted at {self.pending[0]}; retrying with "
                f"{PULLBACK_OFFSETS[self.pb_level[0]]} m pullback.")
        else:
            # Pullbacks exhausted: sacrifice this pose so the rest of the route
            # survives. (If the abort happened during upfront planning we get no
            # feedback and cannot tell WHICH pose was infeasible — dropping the
            # first is a heuristic; it converges after at most a few resends.)
            dropped = self.pending.pop(0)
            self.pb_level.pop(0)
            self.logger.error(f"[{self.name}] Dropping unreachable pose {dropped}.")
            if not self.pending:
                return False

        self._send_goal()
        return True

    def update(self) -> Status:
        """Evaluates every 50ms while this behavior is actively running."""
        self.tick_count += 1

        if VERBOSE and self.tick_count % 20 == 0:
            print(f"[{self.name}] Flowing through route... (Tick: {self.tick_count})")

        if self.goal_status is None:
            return Status.RUNNING

        if self.goal_status == GoalStatus.STATUS_SUCCEEDED:
            self.logger.info(f"[{self.name}] Route completed!")
            return Status.SUCCESS

        if self.goal_status in [GoalStatus.STATUS_ABORTED, GoalStatus.STATUS_UNKNOWN]:
            # Space recovery resends RETRY_DELAY_S apart (transient Nav2
            # failures — e.g. servers still activating — otherwise burn all
            # pullback levels instantly).
            if self._retry_at_s is None:
                self._retry_at_s = self._now_s() + RETRY_DELAY_S
                self.logger.warning(f"[{self.name}] Route aborted; recovering in {RETRY_DELAY_S} s.")
                return Status.RUNNING
            if self._now_s() < self._retry_at_s:
                return Status.RUNNING
            self._retry_at_s = None
            if self._recover_from_abort():
                return Status.RUNNING
            self.logger.error(f"[{self.name}] No reachable poses left in route.")
            return Status.FAILURE

        if self.goal_status == GoalStatus.STATUS_CANCELED:
            self.logger.error(f"[{self.name}] Route canceled.")
            return Status.FAILURE

        return Status.RUNNING

    def terminate(self, new_status: Status) -> None:
        """Fires automatically when the node stops running."""
        if new_status == Status.INVALID and self.goal_handle is not None:
            self.logger.warning(f"[{self.name}] Interrupted! Canceling active navigation.")
            self.goal_handle.cancel_goal_async()

        self.goal_handle = None
        self.goal_status = None


class PlanBlockRoute(py_trees.behaviour.Behaviour):
    """Snapshot up to `max_blocks` nearest vision-detected blocks into a route.

    Greedy nearest-neighbor ordering from the robot's current position; the
    result lands on the shared node as `bt_planned_route` for GoThroughPlanned.
    FAILURE when no blocks are known (lets a Selector fall back to a sweep).
    """
    def __init__(self, name, max_blocks=5):
        super().__init__(name)
        self.max_blocks = max_blocks
        self.node = None

    def setup(self, **kwargs):
        self.node = kwargs.get("node")
        if self.node is None:
            raise RuntimeError("ROS 2 node context missing.")
        self.tf_buffer = _shared_tf_buffer(self.node)
        self.memory = _shared_block_memory(self.node, self.tf_buffer)

    def update(self) -> Status:
        blocks = list(self.memory.blocks)
        if not blocks:
            self.logger.info(f"[{self.name}] no blocks known — falling back.")
            return Status.FAILURE
        pos = _robot_xy(self.tf_buffer) or blocks[0]
        route = []
        while blocks and len(route) < self.max_blocks:
            blocks.sort(key=lambda b: math.hypot(b[0] - pos[0], b[1] - pos[1]))
            nxt = blocks.pop(0)
            route.append(nxt)
            pos = nxt
        self.node.bt_planned_route = route
        self.logger.info(f"[{self.name}] route over {len(route)} block(s): "
                         + ", ".join(f"({x:.2f},{y:.2f})" for x, y in route))
        return Status.SUCCESS


class GoThroughPlanned(GoThroughPoses):
    """GoThroughPoses whose route comes from PlanBlockRoute at activation time."""
    def initialise(self) -> None:
        self.waypoints = [tuple(p) for p in getattr(self.node, 'bt_planned_route', [])]
        super().initialise()


class HoldEnoughBlocks(py_trees.behaviour.Behaviour):
    """SUCCESS once >= DISCHARGE_BLOCK_COUNT blocks were collected since the
    last discharge — gates the trip back to base so a 2-block round doesn't
    waste match time on an unload detour."""
    def __init__(self, name, threshold=DISCHARGE_BLOCK_COUNT):
        super().__init__(name)
        self.threshold = threshold

    def setup(self, **kwargs):
        self.node = kwargs.get("node")
        if self.node is None:
            raise RuntimeError("ROS 2 node context missing.")
        self.memory = _shared_block_memory(self.node, _shared_tf_buffer(self.node))

    def update(self) -> Status:
        n = self.memory.collected_since_discharge
        if n >= self.threshold:
            self.logger.info(f"[{self.name}] {n} blocks on board — going to discharge.")
            return Status.SUCCESS
        self.logger.info(f"[{self.name}] only {n}/{self.threshold} on board — keep collecting.")
        return Status.FAILURE


class ResetBlockCount(py_trees.behaviour.Behaviour):
    """Zero the on-board counter after a discharge."""
    def __init__(self, name="Reset_Block_Count"):
        super().__init__(name)

    def setup(self, **kwargs):
        self.node = kwargs.get("node")
        if self.node is None:
            raise RuntimeError("ROS 2 node context missing.")
        self.memory = _shared_block_memory(self.node, _shared_tf_buffer(self.node))

    def update(self) -> Status:
        self.memory.collected_since_discharge = 0
        return Status.SUCCESS


class SetMotor(py_trees.behaviour.Behaviour):
    """Latched motor command: set /cmd_fans or /cmd_belt to a value.

    The firmware zeroes any motor command not refreshed within 500 ms (its
    comms-loss safety net), so 'set once' must really be 'set and keep
    republishing': a single shared 5 Hz node timer re-sends the latched value
    of every commanded topic for the rest of the mission. The behavior itself
    returns SUCCESS immediately after updating the latch.
    """
    def __init__(self, name, topic, value):
        super().__init__(name)
        self.topic = topic
        self.value = float(value)
        self.node = None

    def setup(self, **kwargs):
        self.node = kwargs.get("node")
        if self.node is None:
            raise RuntimeError("ROS 2 node context missing.")
        # Shared across all SetMotor instances: one publisher per topic, one
        # latch dict, one republish timer on the node.
        if not hasattr(self.node, "bt_motor_latch"):
            self.node.bt_motor_pubs = {}
            self.node.bt_motor_latch = {}
            node = self.node

            def _republish():
                for topic, value in node.bt_motor_latch.items():
                    node.bt_motor_pubs[topic].publish(Float32(data=value))

            self.node.bt_motor_timer = self.node.create_timer(0.2, _republish)
        if self.topic not in self.node.bt_motor_pubs:
            self.node.bt_motor_pubs[self.topic] = self.node.create_publisher(
                Float32, self.topic, 10)

    def update(self) -> Status:
        self.node.bt_motor_latch[self.topic] = self.value
        self.node.bt_motor_pubs[self.topic].publish(Float32(data=self.value))
        self.logger.info(f"[{self.name}] {self.topic} = {self.value} (latched)")
        return Status.SUCCESS


class Wait(py_trees.behaviour.Behaviour):
    """RUNNING for a fixed duration, then SUCCESS (e.g. discharge dwell time)."""
    def __init__(self, name, duration_s):
        super().__init__(name)
        self.duration_s = duration_s
        self.node = None
        self._t0 = None

    def setup(self, **kwargs):
        self.node = kwargs.get("node")
        if self.node is None:
            raise RuntimeError("ROS 2 node context missing.")

    def initialise(self):
        self._t0 = self.node.get_clock().now()

    def update(self) -> Status:
        elapsed = (self.node.get_clock().now() - self._t0).nanoseconds * 1e-9
        return Status.SUCCESS if elapsed >= self.duration_s else Status.RUNNING


# =========================================================
# Placeholder downstream mechanisms
# =========================================================

class PushButton(py_trees.behaviour.Behaviour):
    def __init__(self, name="Push_Button"):
        super().__init__(name)
        self.button_pushed = False
    def update(self):
        # Automatically succeed for testing downstream executions
        return Status.SUCCESS

def _wrap_deg(d):
    """Fold an angle difference into [-180, 180)."""
    return (d + 180.0) % 360.0 - 180.0


def _wrap_half(d):
    """Fold a LINE-direction difference into (-90, 90] (lines are mod 180)."""
    return (d + 90.0) % 180.0 - 90.0


class AlignWithWall(py_trees.behaviour.Behaviour):
    """Laser double-check of heading before a precision traverse (door/ramp).

    The calibrated map waypoints + AMCL get the robot ROUGHLY onto the
    alignment line; this behavior then trues the heading against the PHYSICAL
    wall, independently of localization. It fits a line (principal axis) to
    the /scan points in a sector around `wall_bearing_deg` (robot frame:
    0 = ahead, -90 = right, +90 = left) and measures the residual yaw error:
      mode 'perpendicular' — we face the wall: its line should read 90 deg
      mode 'parallel'      — we run along it: its line should read 0 deg
    If the error exceeds TRIGGER_DEG, rotate in place (/cmd_vel) until within
    SETTLE_DEG. If no wall can be fit (sensor hiccup, wall out of range) it
    warns LOUDLY and passes — the double-check must never strand the mission;
    the Timeout decorator around it bounds the correction time.
    """

    ROTATE_MAX_RAD_S = 0.4
    ROTATE_MIN_RAD_S = 0.12    # below this the diff drive barely moves
    GAIN = 0.03                # rad/s per deg of error
    TRIGGER_DEG = 4.0          # start correcting above this
    SETTLE_DEG = 2.0           # stop correcting below this (hysteresis)
    SECTOR_HALF_DEG = 35.0
    MAX_RANGE_M = 3.0          # drop returns past this (e.g. through the door gap)
    RANGE_BAND_M = 0.4         # keep points within ±band of the sector median
    MIN_POINTS = 15

    def __init__(self, name="Align_With_Wall", wall_bearing_deg=0.0,
                 mode="perpendicular"):
        super().__init__(name)
        self.wall_bearing_deg = float(wall_bearing_deg)
        self.expected_deg = 90.0 if mode == "perpendicular" else 0.0
        self.node = None
        self._cmd_pub = None
        self._correcting = False

    def setup(self, **kwargs):
        self.node = kwargs.get("node")
        if self.node is None:
            raise RuntimeError("ROS 2 node context missing.")
        # One shared /scan cache for all AlignWithWall instances. Sensor-data
        # QoS is mandatory: rplidar publishes BEST_EFFORT and a default
        # RELIABLE subscription would silently never match.
        if not hasattr(self.node, "bt_scan_cache"):
            cache = {"msg": None}
            self.node.bt_scan_cache = cache
            self.node.create_subscription(
                LaserScan, '/scan',
                lambda m: cache.__setitem__("msg", m),
                qos_profile_sensor_data)
        self._cmd_pub = self.node.create_publisher(Twist, '/cmd_vel', 10)

    def initialise(self):
        self._correcting = False

    def _wall_error_deg(self, scan):
        """Fitted wall-line angle minus expected, in deg; None if no good fit."""
        pts = []
        a = scan.angle_min
        for r in scan.ranges:
            bearing_deg = math.degrees(a)
            a += scan.angle_increment
            if not math.isfinite(r) or r < scan.range_min or r > self.MAX_RANGE_M:
                continue
            if abs(_wrap_deg(bearing_deg - self.wall_bearing_deg)) > self.SECTOR_HALF_DEG:
                continue
            pts.append((r, math.radians(bearing_deg)))
        if len(pts) < self.MIN_POINTS:
            return None
        # Median-range band keeps only the wall surface, rejecting returns
        # through the door opening or off foreground clutter.
        ranges = sorted(p[0] for p in pts)
        median = ranges[len(ranges) // 2]
        xy = [(r * math.cos(b), r * math.sin(b)) for r, b in pts
              if abs(r - median) <= self.RANGE_BAND_M]
        if len(xy) < self.MIN_POINTS:
            return None
        # Principal-axis (total least squares) line fit — no numpy needed.
        n = len(xy)
        mx = sum(p[0] for p in xy) / n
        my = sum(p[1] for p in xy) / n
        sxx = sum((p[0] - mx) ** 2 for p in xy)
        syy = sum((p[1] - my) ** 2 for p in xy)
        sxy = sum((p[0] - mx) * (p[1] - my) for p in xy)
        line_deg = math.degrees(0.5 * math.atan2(2.0 * sxy, sxx - syy))
        return _wrap_half(line_deg - self.expected_deg)

    def _stop(self):
        if self._cmd_pub is not None:
            self._cmd_pub.publish(Twist())

    def update(self) -> Status:
        scan = self.node.bt_scan_cache["msg"]
        if scan is None:
            return Status.RUNNING   # no scan yet; Timeout wrapper bounds this
        err = self._wall_error_deg(scan)
        if err is None:
            self.logger.warning(
                f"[{self.name}] No wall fit in scan sector (bearing "
                f"{self.wall_bearing_deg:+.0f} deg) — SKIPPING the alignment "
                f"double-check. Verify the heading visually if you can!")
            self._stop()
            return Status.SUCCESS
        threshold = self.SETTLE_DEG if self._correcting else self.TRIGGER_DEG
        if abs(err) <= threshold:
            self._stop()
            self.logger.info(f"[{self.name}] Wall-aligned (residual {err:+.1f} deg"
                             + (", corrected" if self._correcting else "") + ").")
            return Status.SUCCESS
        if not self._correcting:
            self.logger.warning(
                f"[{self.name}] Heading off by {err:+.1f} deg vs the wall "
                f"(AMCL pose disagrees with the laser) — correcting in place.")
            self._correcting = True
        # err > 0 means the wall line reads CCW of expected, i.e. our yaw is
        # short — rotate CCW (+z). Plain P-control with a deadband floor.
        wz = max(self.ROTATE_MIN_RAD_S,
                 min(self.ROTATE_MAX_RAD_S, self.GAIN * abs(err)))
        cmd = Twist()
        cmd.angular.z = wz if err > 0 else -wz
        self._cmd_pub.publish(cmd)
        return Status.RUNNING

    def terminate(self, new_status):
        self._stop()


class SeekBlockForward(py_trees.behaviour.Behaviour):
    """Creep straight forward until vision registers a block.

    Fallback discovery when BlockMemory is empty: instead of driving blind
    sweep chunks, just move slowly ahead so the camera gets fresh ground in
    view. SUCCESS as soon as >=1 block is known (the next vision round routes
    over it). The laser guards the front: if a wall/obstacle is closer than
    STOP_DIST_M, stop and FAIL (the round is skipped and the mission moves
    on). Wrap with a Timeout — open floor with no blocks would otherwise
    creep until the far wall.
    """

    SPEED_M_S = 0.12
    STOP_DIST_M = 0.45         # laser front-sector minimum before giving up
    FRONT_HALF_DEG = 20.0

    def __init__(self, name="Seek_Block_Forward"):
        super().__init__(name)
        self.node = None
        self._cmd_pub = None
        self.memory = None

    def setup(self, **kwargs):
        self.node = kwargs.get("node")
        if self.node is None:
            raise RuntimeError("ROS 2 node context missing.")
        if not hasattr(self.node, "bt_scan_cache"):
            cache = {"msg": None}
            self.node.bt_scan_cache = cache
            self.node.create_subscription(
                LaserScan, '/scan',
                lambda m: cache.__setitem__("msg", m),
                qos_profile_sensor_data)
        self._cmd_pub = self.node.create_publisher(Twist, '/cmd_vel', 10)
        self.memory = _shared_block_memory(self.node, _shared_tf_buffer(self.node))

    def _front_clearance(self):
        scan = self.node.bt_scan_cache["msg"]
        if scan is None:
            return None
        best = float('inf')
        a = scan.angle_min
        for r in scan.ranges:
            bearing = math.degrees(a)
            a += scan.angle_increment
            if abs(_wrap_deg(bearing)) > self.FRONT_HALF_DEG:
                continue
            if math.isfinite(r) and r > scan.range_min:
                best = min(best, r)
        return best

    def _stop(self):
        if self._cmd_pub is not None:
            self._cmd_pub.publish(Twist())

    def update(self) -> Status:
        if self.memory.blocks:
            self._stop()
            self.logger.info(
                f"[{self.name}] Vision sees {len(self.memory.blocks)} block(s) — stopping seek.")
            return Status.SUCCESS
        clearance = self._front_clearance()
        if clearance is None:
            return Status.RUNNING   # no scan yet; Timeout wrapper bounds this
        if clearance < self.STOP_DIST_M:
            self._stop()
            self.logger.warning(
                f"[{self.name}] Obstacle {clearance:.2f} m ahead and still no "
                f"block in sight — giving up this seek.")
            return Status.FAILURE
        cmd = Twist()
        cmd.linear.x = self.SPEED_M_S
        self._cmd_pub.publish(cmd)
        return Status.RUNNING

    def terminate(self, new_status):
        self._stop()


class ClimbDoor(py_trees.behaviour.Behaviour):
    def __init__(self, name="Climb_Door"): super().__init__(name)
    def update(self): return Status.SUCCESS

class GoToStart(py_trees.behaviour.Behaviour):
    def __init__(self, name="Go_To_Start"): super().__init__(name)
    def update(self): return Status.SUCCESS

class Delivery(py_trees.behaviour.Behaviour):
    def __init__(self, name="Delivery"): super().__init__(name)
    def update(self): return Status.SUCCESS


def wrap_with_timeout(behaviour_node, duration_seconds):
    timeout_node = py_trees.decorators.Timeout(
        child=behaviour_node,
        duration=duration_seconds,
        name=f"{behaviour_node.name}_Timeout"
    )
    lenient_node = py_trees.decorators.FailureIsSuccess(
        child=timeout_node,
        name=f"{behaviour_node.name}_Skippable"
    )
    return lenient_node

# =========================================================
# TREE COMPOSITION — mission phases mirror fsm.py's state machine
# =========================================================

# Mission calibration points, MAP frame, derived from ros2_ws/maps/ref.png
# under the current clean_room_8x8.yaml origin. Third element = arrival yaw.
# The ref image encodes:
#   red    arena/map (0,0)
#   green  initial/base point
#   yellow button
#   pink   door alignment line (travel upward through the doorway)
#   blue   ramp alignment line
#   red    objectives.png long-term zone goals
POSE_BUTTON = (8.810, -4.355, 0.0)                 # yellow point; face the button wall
POSE_BASE = (1.005, -0.955, 2.381699)             # green point; face arena origin
POSE_DOOR_LINE_ENTRY = (8.210, -4.010, math.pi / 2.0)   # lower pink point; face upward
POSE_DOOR_LINE_EXIT = (8.210, -3.610, math.pi / 2.0)    # upper pink point; continue upward
POSE_ZONE3_OBJECTIVE = (8.135, -2.085, math.pi)         # top red point; turn into zone 3
POSE_RAMP_LINE_ENTRY = (4.510, -8.135, 0.174216)        # left blue point; face up-ramp toward zone 4
RAMP_UP_ROUTE_POINTS = [
    (4.885, -8.160),   # middle blue point
    (5.210, -8.160),   # right blue point
    (7.635, -7.585),   # bottom red objective in zone 4
]
POSE_ZONE4_OBJECTIVE = (7.635, -7.585, math.pi)        # bottom red point; turn into zone 4
POSE_RAMP_RETURN_ENTRY = (7.635, -8.160, math.pi)      # same horizontal as blue points, face back toward ramp
RAMP_DOWN_ROUTE_POINTS = [
    (5.210, -8.160),   # right blue point
    (4.885, -8.160),   # middle blue point
    (4.510, -8.135),   # left blue point / ramp exit
]

# Fallback sweep routes in the current calibrated map frame. The BT prefers
# vision-planned routes first; these are only the "no blocks known yet" backup
# passes for each zone.
ZONE1_SWEEP_CHUNKS = [
    [(1.10, -1.10), (3.80, -1.10), (4.20, -3.10)],
    [(4.20, -5.60), (2.30, -6.90), (1.10, -5.10)],
]
ZONE3_SWEEP_CHUNKS = [
    [(8.10, -2.10), (7.10, -2.10), (6.70, -2.90)],
    [(6.70, -1.40), (7.60, -1.10), (8.10, -1.80)],
]
ZONE4_SWEEP_CHUNKS = [
    [(7.60, -7.60), (6.80, -7.20), (6.10, -6.60)],
    [(6.10, -7.90), (6.90, -8.00), (7.50, -7.70)],
]


def _goto(name, arena_pose, timeout_s):
    """GoToPose at a calibrated mission pose, wrapped in the standard timeout/skip."""
    x, y = arena_to_map(arena_pose[0], arena_pose[1])
    return wrap_with_timeout(GoToPose(name, x, y, target_yaw=arena_pose[2]), timeout_s)


def _follow_map_route(name, points, timeout_s):
    """Navigate through an explicit map-frame polyline without per-point yaw."""
    return _with_timeout(GoThroughPoses(name, points), timeout_s)


def _discharge_at_base(tag):
    """Drive to the base and unload: belt on + fans reversed, dwell, restore."""
    seq = py_trees.composites.Sequence(name=f"Discharge_{tag}", memory=True)
    seq.add_child(_goto(f"Discharge_{tag}_Goto_Base", POSE_BASE, 90.0))
    seq.add_child(SetMotor(f"Discharge_{tag}_Fans_Reverse", '/cmd_fans', -FAN_SPEED))
    seq.add_child(SetMotor(f"Discharge_{tag}_Belt_On", '/cmd_belt', BELT_SPEED))
    seq.add_child(Wait(f"Discharge_{tag}_Dwell", DISCHARGE_SECONDS))
    seq.add_child(SetMotor(f"Discharge_{tag}_Belt_Off", '/cmd_belt', 0.0))
    seq.add_child(SetMotor(f"Discharge_{tag}_Fans_Forward", '/cmd_fans', FAN_SPEED))
    seq.add_child(ResetBlockCount(f"Discharge_{tag}_Reset_Count"))
    return seq


def _discharge_if_full(tag):
    """Discharge only when >= DISCHARGE_BLOCK_COUNT blocks are on board;
    otherwise skip (FailureIsSuccess) and keep collecting."""
    seq = py_trees.composites.Sequence(name=f"Maybe_Discharge_{tag}", memory=True)
    seq.add_child(HoldEnoughBlocks(f"{tag}_Hold_{DISCHARGE_BLOCK_COUNT}"))
    seq.add_child(_discharge_at_base(tag))
    return py_trees.decorators.FailureIsSuccess(
        child=seq, name=f"Maybe_Discharge_{tag}_Skippable")


def _with_timeout(behaviour_node, duration_seconds):
    """Timeout WITHOUT FailureIsSuccess — for children inside a Selector, where
    a failure must fall through to the next option instead of faking success."""
    return py_trees.decorators.Timeout(
        child=behaviour_node, duration=duration_seconds,
        name=f"{behaviour_node.name}_Timeout")


def _collect_zone(zone_tag, chunks, discharge_between_rounds=True):
    """Collect blocks: vision-planned routes first, sweep chunks as fallback.

    Each round: if vision (BlockMemory) knows blocks, flow through the <=5
    nearest and discharge at base — real counting, the memory drops blocks the
    robot drove over. If no blocks are known yet, drive the next predefined
    sweep chunk instead (which both collects blindly and lets the camera
    discover blocks for the next round). One extra vision-only round runs
    after the sweeps to mop up late discoveries. A round with nothing to do
    fails its Selector and skips its discharge (FailureIsSuccess keeps the
    mission going).

    discharge_between_rounds=False for zones behind a precision traverse
    (door / ramp): a mid-collection run to base would path back through the
    door or off the ramp WITHOUT the alignment phases. Those zones collect
    everything regardless of count; the unload happens after the aligned
    return, as the mission flow schedules it.
    """
    seq = py_trees.composites.Sequence(name=f"Collect_{zone_tag}", memory=True)
    rounds = len(chunks) + 1
    for i in range(1, rounds + 1):
        source = py_trees.composites.Selector(name=f"{zone_tag}_R{i}_Source", memory=True)

        vision = py_trees.composites.Sequence(name=f"{zone_tag}_R{i}_Vision", memory=True)
        vision.add_child(PlanBlockRoute(f"{zone_tag}_R{i}_Plan"))
        vision.add_child(_with_timeout(GoThroughPlanned(f"{zone_tag}_R{i}_Blocks"), 120.0))
        source.add_child(vision)

        # Discovery fallback: no blocks known -> creep straight forward until
        # the camera sees one (next round's vision plan routes over it).
        # Replaces the blind sweep chunks: with the short 1.5 m detection
        # range the camera only finds blocks near its own path anyway.
        source.add_child(_with_timeout(
            SeekBlockForward(f"{zone_tag}_R{i}_Seek"), 45.0))

        round_seq = py_trees.composites.Sequence(name=f"{zone_tag}_Round_{i}", memory=True)
        round_seq.add_child(source)
        if discharge_between_rounds:
            # Unload only when the intake actually holds DISCHARGE_BLOCK_COUNT
            # blocks (counted by BlockMemory as the robot drives over them).
            round_seq.add_child(_discharge_if_full(f"{zone_tag}_{i}"))
        seq.add_child(py_trees.decorators.FailureIsSuccess(
            child=round_seq, name=f"{zone_tag}_Round_{i}_Skippable"))
    return seq


def _button_phase(root):
    """Button + door entry, matching the yellow/pink markers in ref.png.

    Pre_Button gate: blocks swallowed incidentally on the way here count too —
    if the intake already holds >= DISCHARGE_BLOCK_COUNT, make ONE trip back
    to base, then head straight for the objective (no block routing). Inside
    the door (zone 3) the count is ignored until the aligned return.
    The laser align check trues the heading against the physical door wall
    before the traverse — AMCL alone is not trusted for precision moves.
    """
    root.add_child(_discharge_if_full("Pre_Button"))
    root.add_child(_goto("Move_To_Button", POSE_BUTTON, 60.0))
    root.add_child(wrap_with_timeout(PushButton(), 5.0))
    root.add_child(_goto("Door_Line_Entry", POSE_DOOR_LINE_ENTRY, 60.0))
    root.add_child(wrap_with_timeout(AlignWithWall(
        "Door_Align_Check", wall_bearing_deg=0.0, mode="perpendicular"), 12.0))
    root.add_child(_goto("Door_Line_Exit", POSE_DOOR_LINE_EXIT, 30.0))


def _zone3_phase(root):
    """Door transition, then drive to the top objective and collect zone 3.

    No mid-collection discharge: everything collected behind the door stays on
    board until the mission flow brings the robot back out and unloads.
    """
    _button_phase(root)
    root.add_child(_goto("Zone3_Objective", POSE_ZONE3_OBJECTIVE, 45.0))
    root.add_child(_collect_zone("Zone3", ZONE3_SWEEP_CHUNKS,
                                 discharge_between_rounds=False))


def _ramp_phase(root):
    """Line up on the blue markers, climb the ramp, and reach zone 4 objective.

    Same gate as the button leg: one optional base trip BEFORE committing to
    the ramp, then direct. The align check runs the right-hand wall parallel
    before the climb — a misaligned ramp entry is how the robot falls off.
    """
    root.add_child(_discharge_if_full("Pre_Ramp"))
    root.add_child(_goto("Ramp_Line_Entry", POSE_RAMP_LINE_ENTRY, 60.0))
    root.add_child(wrap_with_timeout(AlignWithWall(
        "Ramp_Align_Check", wall_bearing_deg=-90.0, mode="parallel"), 12.0))
    root.add_child(_follow_map_route("Pass_Ramp", RAMP_UP_ROUTE_POINTS, 120.0))
    root.add_child(_goto("Zone4_Objective", POSE_ZONE4_OBJECTIVE, 30.0))


def _ramp_return_phase(root):
    """Return from zone 4 by re-aligning on the blue line and driving down-ramp.

    Facing pi (back toward the ramp) the same wall is now on the LEFT (+90).
    """
    root.add_child(_goto("Ramp_Return_Entry", POSE_RAMP_RETURN_ENTRY, 45.0))
    root.add_child(wrap_with_timeout(AlignWithWall(
        "Ramp_Return_Align_Check", wall_bearing_deg=90.0, mode="parallel"), 12.0))
    root.add_child(_follow_map_route("Return_Down_Ramp", RAMP_DOWN_ROUTE_POINTS, 120.0))


def create_tree(mission="full"):
    """Mission selector (--mission CLI flag / bt_mission launch argument).

    Every zone flag is a PARTIAL RUN of the full flow — identical phases in
    identical order, with the skipped leg removed:

    full   button/door + zone 3 + discharge + ramp + zone 4 + aligned return
           + discharge + zone 1 cleanup + final unload
    zone1  full minus the button/door/zone-3 leg AND the ramp/zone-4 leg
    zone3  full minus the ramp/zone-4 leg (and its intermediary goals)
    zone4  full minus the button/door/zone-3 leg (and its intermediary goals)

    All modes: fans ON before the first motion; AMCL localization gates the
    start; zone 1 cleanup + unconditional base unload close every mission.
    Block-count policy: at most ONE base trip at the Pre_Button / Pre_Ramp
    gates if >= DISCHARGE_BLOCK_COUNT was swallowed en route; once inside
    zone 3 or zone 4, the count is ignored until the aligned return.
    """
    root = py_trees.composites.Sequence(name=f"Mission_{mission}", memory=True)

    # 0. Common prologue: localized first, then fans spinning BEFORE any motion
    #    (blocks must be absorbable from the very first meter).
    root.add_child(WaitForLocalization())
    root.add_child(SetMotor("Fans_On", '/cmd_fans', FAN_SPEED))

    if mission in ("full", "zone3"):
        _zone3_phase(root)
        root.add_child(_discharge_at_base("Post_Zone3"))
    if mission in ("full", "zone4"):
        _ramp_phase(root)
        root.add_child(_collect_zone("Zone4", ZONE4_SWEEP_CHUNKS,
                                     discharge_between_rounds=False))
        _ramp_return_phase(root)
        root.add_child(_discharge_at_base("Post_Zone4"))
    # Zone 1 cleanup runs in EVERY mode (it is the robot's home zone — no
    # precision traverse needed, so per-round discharges stay enabled).
    root.add_child(_collect_zone("Zone1", ZONE1_SWEEP_CHUNKS))

    # Epilogue: back to base and unload UNCONDITIONALLY (whatever partial load
    # is on board), then stop the intake.
    root.add_child(_discharge_at_base("Final"))
    root.add_child(wrap_with_timeout(Delivery(), 5.0))
    root.add_child(SetMotor("Fans_Off", '/cmd_fans', 0.0))

    return root


def main(args=None):
    # --mission selects the tree composition; ROS args pass through untouched.
    parser = argparse.ArgumentParser(description="EyeRobot mission behavior tree")
    parser.add_argument('--mission', default='full',
                        choices=['full', 'zone1', 'zone3', 'zone4'],
                        help="Mission variant (see create_tree docstring)")
    cli, ros_argv = parser.parse_known_args(args)

    rclpy.init(args=ros_argv)
    print(f"=== Mission mode: {cli.mission} ===")
    tree_root = create_tree(cli.mission)
    
    if VERBOSE:
        print("\n--- BEHAVIOR TREE STRUCTURE ---")
        print(py_trees.display.unicode_tree(tree_root))
        print("-------------------------------\n")
    
    tree = py_trees_ros.trees.BehaviourTree(
        root=tree_root,
        unicode_tree_debug=False
    )

    # Infinite setup timeout: setup blocks on the Nav2 action servers, and Nav2
    # takes 30-60+ s to activate on the Nano — a finite timeout (the old 15.0)
    # killed the tree mid-boot with "tree setup interrupted or timed out".
    # If Nav2 never comes up, the periodic "waiting for ... action server" logs
    # make the hang visible and diagnosable, which beats starting a mission
    # without navigation.
    tree.setup(node_name="autonomous_controller", timeout=py_trees.common.Duration.INFINITE)
    
    try:
        tree.tick_tock(period_ms=50)
        rclpy.spin(tree.node)
    except KeyboardInterrupt:
        tree.node.get_logger().info('Stopping due to user interruption.')
    finally:
        tree.shutdown()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
