#!/usr/bin/env python3
import argparse
import math

import numpy as np
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
from nav_msgs.msg import Path as NavPath, OccupancyGrid
from visualization_msgs.msg import Marker, MarkerArray
from action_msgs.msg import GoalStatus
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
from rclpy.qos import (qos_profile_sensor_data, QoSProfile,
                       ReliabilityPolicy, DurabilityPolicy)

# Intake actuation (cmd_vel_bridge forwards these to the motor topics).
# 8.0 rad/s matches the teleop defaults (fan/belt_command_rad_s).
FAN_SPEED = 8.0
BELT_SPEED = 8.0
DISCHARGE_SECONDS = 5.0
DISCHARGE_BLOCK_COUNT = 10  # go unload at base once this many blocks were collected

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

# Mission time budget. The loop mission runs collect cycles until
# (MISSION_TIME_LIMIT_S - FINAL_UNLOAD_RESERVE_S) elapses since the first
# tick after localization, then forces one last trip to the delivery zone,
# unloads whatever is on board, and parks. The reserve must cover the worst
# trip home (~half arena at 0.3 m/s ≈ 25 s) + discharge dwell + margin.
MISSION_TIME_LIMIT_S = 600.0
FINAL_UNLOAD_RESERVE_S = 75.0

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


def _robot_yaw(tf_buffer):
    """Current robot yaw in the odom frame (continuous, no AMCL jumps), or
    None if TF is not up yet."""
    try:
        t = tf_buffer.lookup_transform("odom", "base_link", Time())
        q = t.transform.rotation
        return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                          1.0 - 2.0 * (q.y * q.y + q.z * q.z))
    except Exception:
        return None


def _shared_tf_buffer(node):
    """One TF buffer shared by all behaviors (each TransformListener subscribes
    to /tf, so we only want a single one on the node)."""
    if not hasattr(node, "bt_tf_buffer"):
        node.bt_tf_buffer = Buffer()
        node.bt_tf_listener = TransformListener(node.bt_tf_buffer, node)
    return node.bt_tf_buffer


class ArenaMap:
    """Validity oracle backed by the STATIC arena map (clean_room_8x8).

    Subscribes once to /map (the map_server's latched grid — the same
    cleanroom map AMCL localizes against) and answers "is a disk of radius
    r around (x, y) entirely known free space?" via a precomputed numpy
    disk mask. Used to refuse vision detections projected into walls and
    to drop route points Nav2 could never plan to. The static map is
    deliberately preferred over the live global costmap: it cannot be
    polluted by transient sensor noise, needs no service polling, and the
    arena walls — the thing ghosts hide behind — never move.
    """

    FREE_MAX = 50          # occupancy below this counts as free (0..100 scale)

    def __init__(self, node):
        self.node = node
        self._grid = None      # int8 (rows=y, cols=x)
        self._meta = None
        self._disk_masks = {}  # radius_cells -> bool mask, cached
        latched = QoSProfile(depth=1,
                             reliability=ReliabilityPolicy.RELIABLE,
                             durability=DurabilityPolicy.TRANSIENT_LOCAL)
        node.create_subscription(OccupancyGrid, '/map', self._on_map, latched)

    def _on_map(self, msg):
        self._meta = msg.info
        self._grid = np.asarray(msg.data, dtype=np.int8).reshape(
            msg.info.height, msg.info.width)
        self.node.get_logger().info(
            f"[arena-map] static map loaded: {msg.info.width}x{msg.info.height} "
            f"@ {msg.info.resolution:.3f} m/cell")

    def _disk(self, r_cells):
        if r_cells not in self._disk_masks:
            axis = np.arange(-r_cells, r_cells + 1)
            yy, xx = np.meshgrid(axis, axis, indexing='ij')
            self._disk_masks[r_cells] = (xx * xx + yy * yy) <= r_cells * r_cells
        return self._disk_masks[r_cells]

    def disk_is_free(self, x, y, radius_m):
        """True/False once the map is in; None while it has not arrived yet
        (callers fall back to their pre-map behavior on None)."""
        if self._grid is None:
            return None
        res = self._meta.resolution
        col = int((x - self._meta.origin.position.x) / res)
        row = int((y - self._meta.origin.position.y) / res)
        r = max(0, int(math.ceil(radius_m / res)))
        h, w = self._grid.shape
        if not (r <= col < w - r and r <= row < h - r):
            return False   # outside the mapped area (or too close to its edge)
        window = self._grid[row - r:row + r + 1, col - r:col + r + 1]
        cells = window[self._disk(r)]
        # unknown (-1) is NOT free: a block "behind" the wall projects there
        return bool(((cells >= 0) & (cells < self.FREE_MAX)).all())


def _shared_arena_map(node):
    if not hasattr(node, "bt_arena_map"):
        node.bt_arena_map = ArenaMap(node)
    return node.bt_arena_map


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

    # Floor-height gate, map frame: a real block sits ON the floor, so its
    # detected center must land near z=0 after the camera->map transform.
    # Lower bound -0.06: depth noise + residual mount-calibration error.
    # Upper bound +0.22: a double-stacked duplo tops out ~0.12, plus the same
    # error budget. Anything outside (people's shoes, wall tops, points
    # mis-projected during rotation) is not a block on the floor — and this
    # gate exercises the full 3D TF chain, which an x/y-only check never did.
    Z_RANGE = (-0.06, 0.22)

    # In-wall clearance for accepting a detection (meters). Deliberately
    # TINY: blocks resting against a wall are collectable (the pullback
    # pass), so only the block's own footprint must be free map space.
    DETECTION_CLEARANCE_M = 0.04

    # Pre-map fallback rectangle (the room's free space on clean_room_8x8
    # under the calibrated origin). Only consulted until /map arrives; the
    # ArenaMap disk check replaces it afterwards.
    X_RANGE = (0.0, 8.8)
    Y_RANGE = (-8.0, 0.0)

    def __init__(self, node, tf_buffer):
        self.node = node
        self.tf_buffer = tf_buffer
        self.arena_map = _shared_arena_map(node)
        self.blocks = []  # [(x, y)] map frame
        self.collected_since_discharge = 0  # drives the discharge trigger
        node.create_subscription(
            PointStamped, '/eyerobot/vision/lego_markers_map', self._on_detection, 10)
        # Foxglove visualization: known blocks as green cubes on /bt/blocks.
        self.marker_pub = node.create_publisher(MarkerArray, '/bt/blocks', 10)
        node.create_timer(0.5, self._prune_eaten)

    def _reject(self, p, why):
        # Throttled: the vision node re-publishes tracked blocks at frame
        # rate, so a persistent ghost would otherwise spam the log.
        self.node.get_logger().warning(
            f"[blocks] IGNORED detection at map ({p[0]:.2f}, {p[1]:.2f}): {why}",
            throttle_duration_sec=5.0)

    def _on_detection(self, msg):
        p = (msg.point.x, msg.point.y)
        if not (self.Z_RANGE[0] <= msg.point.z <= self.Z_RANGE[1]):
            self._reject(p, f"z={msg.point.z:+.2f} not on the floor")
            return
        free = self.arena_map.disk_is_free(p[0], p[1], self.DETECTION_CLEARANCE_M)
        if free is False:
            self._reject(p, "inside a wall / outside the mapped arena")
            return
        if free is None and not (self.X_RANGE[0] <= p[0] <= self.X_RANGE[1]
                                 and self.Y_RANGE[0] <= p[1] <= self.Y_RANGE[1]):
            self._reject(p, "out of arena rectangle (map not loaded yet)")
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
    """Shared goal-visualization publishers: /bt/route (nav_msgs/Path, the
    connected line), /bt/route_points (MarkerArray, one fat orange sphere
    per goal) and /bt/goal_point (geometry_msgs/PointStamped, the current
    destination as a flat x,y point at z=0 — renders in any panel that can
    show a point on the map, no 3D markers needed)."""
    if not hasattr(node, "bt_route_pub"):
        node.bt_route_pub = node.create_publisher(NavPath, '/bt/route', 10)
        node.bt_route_points_pub = node.create_publisher(
            MarkerArray, '/bt/route_points', 10)
        node.bt_goal_point_pub = node.create_publisher(
            PointStamped, '/bt/goal_point', 10)
    return node.bt_route_pub


def _publish_route(node, poses):
    _route_publisher(node)   # ensure both publishers exist
    stamp = node.get_clock().now().to_msg()
    path = NavPath()
    path.header.frame_id = "map"
    path.header.stamp = stamp
    path.poses = list(poses)
    node.bt_route_pub.publish(path)

    arr = MarkerArray()
    wipe = Marker()
    wipe.header.frame_id = "map"
    wipe.action = Marker.DELETEALL
    arr.markers.append(wipe)
    for i, ps in enumerate(poses):
        m = Marker()
        m.header.frame_id = "map"
        m.header.stamp = stamp
        m.ns = "route"
        m.id = i
        m.type = Marker.SPHERE
        m.action = Marker.ADD
        m.pose.position.x = ps.pose.position.x
        m.pose.position.y = ps.pose.position.y
        m.pose.position.z = 0.10
        m.pose.orientation.w = 1.0
        m.scale.x = m.scale.y = m.scale.z = 0.20
        m.color.r = 1.0
        m.color.g = 0.5
        m.color.a = 0.95
        arr.markers.append(m)
    node.bt_route_points_pub.publish(arr)

    if poses:
        goal_pt = PointStamped()
        goal_pt.header.frame_id = "map"
        goal_pt.header.stamp = stamp
        goal_pt.point.x = poses[-1].pose.position.x
        goal_pt.point.y = poses[-1].pose.position.y
        node.bt_goal_point_pub.publish(goal_pt)


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

    AMCL self-initializes at the base pose (set_initial_pose + initial_pose
    in nav2_params.yaml — the green marker in ref.png), so this normally
    passes within seconds of Nav2 activating; no manual pose-setting needed.
    It still gates the start because map→odom only appears once AMCL is up,
    and if the robot does NOT start at the base pose the operator must
    relocalize (Foxglove Set-pose) before the mission may move. Deliberately
    NOT wrapped in a timeout — starting unlocalized would send the robot to
    wrong places.
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

        # Goal generation guard: when a goal is PREEMPTED by a newer one
        # (FollowBlockQueue replans mid-route), the old goal's result
        # callback still fires — without the generation tag it would
        # overwrite goal_status with the stale CANCELED/ABORTED and fail a
        # perfectly healthy replacement route.
        self._goal_gen = getattr(self, "_goal_gen", 0) + 1
        gen = self._goal_gen

        goal_msg = NavigateThroughPoses.Goal()
        goal_msg.poses = self._build_poses()
        _publish_route(self.node, goal_msg.poses)
        self.logger.info(f"[{self.name}] Routing through {self.sent_count} pose(s): {self.pending}")
        send_goal_future = self.action_client.send_goal_async(
            goal_msg, feedback_callback=lambda m: self._feedback_callback(m, gen))
        send_goal_future.add_done_callback(lambda f: self._goal_response_callback(f, gen))

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

    def _feedback_callback(self, feedback_msg, gen):
        if gen == self._goal_gen:
            self.feedback_remaining = feedback_msg.feedback.number_of_poses_remaining

    def _goal_response_callback(self, future, gen):
        if gen != self._goal_gen:
            return   # response for a goal we already replaced
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.logger.error(f"[{self.name}] Route rejected by Nav2 planner!")
            self.goal_status = GoalStatus.STATUS_ABORTED
            return

        result_future = self.goal_handle.get_result_async()
        result_future.add_done_callback(lambda f: self._goal_result_callback(f, gen))

    def _goal_result_callback(self, future, gen):
        if gen == self._goal_gen:
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


# Drive-through overshoot: NavigateThroughPoses flows THROUGH the
# intermediate poses, but the FINAL pose is only approached to within
# Nav2's xy_goal_tolerance — which can leave the last block sitting just
# outside the fans. Extending the route one waypoint PAST the last block
# (along the approach line) turns the final block into a flow-through
# point too, without ever stopping.
OVERSHOOT_M = 0.30
OVERSHOOT_CLEARANCE_M = 0.12   # the overshoot point must be drivable space


def _greedy_block_route(robot, blocks, arena_map, max_blocks=5):
    """Greedy nearest-neighbor route over the given blocks + the overshoot
    waypoint. Returns [] when no (reachable) blocks exist. Blocks failing
    the static-map check are dropped defensively (memory normally holds only
    validated blocks; this catches pre-map stowaways before they abort a
    Nav2 route)."""
    blocks = [b for b in blocks
              if arena_map.disk_is_free(b[0], b[1], 0.04) is not False]
    if not blocks:
        return []
    pos = robot or blocks[0]
    route = []
    while blocks and len(route) < max_blocks:
        blocks.sort(key=lambda b: math.hypot(b[0] - pos[0], b[1] - pos[1]))
        nxt = blocks.pop(0)
        route.append(nxt)
        pos = nxt
    approach_from = route[-2] if len(route) > 1 else (robot or route[-1])
    dx = route[-1][0] - approach_from[0]
    dy = route[-1][1] - approach_from[1]
    norm = math.hypot(dx, dy)
    if norm > 1e-6:
        over = (route[-1][0] + dx / norm * OVERSHOOT_M,
                route[-1][1] + dy / norm * OVERSHOOT_M)
        if arena_map.disk_is_free(over[0], over[1], OVERSHOOT_CLEARANCE_M):
            route.append(over)
    return route


class PlanBlockRoute(py_trees.behaviour.Behaviour):
    """Snapshot up to `max_blocks` nearest vision-detected blocks into a route.

    Greedy nearest-neighbor ordering from the robot's current position; the
    result lands on the shared node as `bt_planned_route`. FAILURE when no
    blocks are known (lets a Selector fall back to the search scan).
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
        self.arena_map = _shared_arena_map(self.node)

    def update(self) -> Status:
        route = _greedy_block_route(_robot_xy(self.tf_buffer),
                                    list(self.memory.blocks),
                                    self.arena_map, self.max_blocks)
        if not route:
            self.logger.info(f"[{self.name}] no (reachable) blocks known — falling back.")
            return Status.FAILURE
        self.node.bt_planned_route = route
        self.logger.info(f"[{self.name}] route over {len(route)} point(s): "
                         + ", ".join(f"({x:.2f},{y:.2f})" for x, y in route))
        return Status.SUCCESS


class GoThroughPlanned(GoThroughPoses):
    """GoThroughPoses whose route comes from PlanBlockRoute at activation time."""
    def initialise(self) -> None:
        self.waypoints = [tuple(p) for p in getattr(self.node, 'bt_planned_route', [])]
        super().initialise()


class FollowBlockQueue(GoThroughPlanned):
    """GoThroughPlanned that keeps the route synchronized with BlockMemory.

    Nav2 cannot append poses to a running NavigateThroughPoses goal, but a
    new goal PREEMPTS the active one seamlessly — so the "position queue"
    is: whenever the camera registers a block that is not on the current
    route, re-plan greedily over EVERYTHING still in memory (remaining route
    blocks included — memory only drops a block when it is eaten) from the
    live robot position, and send the replacement goal. Rate-limited so a
    burst of detections costs one replan, not five. The goal-generation
    guard in GoThroughPoses keeps the preempted goal's stale result from
    failing the new one.
    """

    REPLAN_MIN_PERIOD_S = 3.0

    def setup(self, **kwargs):
        super().setup(**kwargs)
        self.memory = _shared_block_memory(self.node, self.tf_buffer)
        self.arena_map = _shared_arena_map(self.node)

    def initialise(self) -> None:
        super().initialise()
        self._last_replan_s = self._now_s()

    def _has_unrouted_block(self):
        return any(
            all(math.hypot(b[0] - w[0], b[1] - w[1]) > BlockMemory.MERGE_RADIUS
                for w in self.pending)
            for b in self.memory.blocks)

    def update(self) -> Status:
        # Fold new detections in only while a goal is healthily in flight
        # (not during abort recovery / retry backoff).
        if (self.goal_status is None and self.goal_handle is not None
                and self.pending and self._retry_at_s is None
                and self._now_s() - self._last_replan_s > self.REPLAN_MIN_PERIOD_S
                and self._has_unrouted_block()):
            route = _greedy_block_route(_robot_xy(self.tf_buffer),
                                        list(self.memory.blocks),
                                        self.arena_map)
            if route:
                self.logger.info(
                    f"[{self.name}] new block(s) spotted — replanning over "
                    f"{len(route)} point(s) and preempting the route.")
                self.pending = route
                self.pb_level = [0] * len(route)
                self._last_replan_s = self._now_s()
                self._send_goal()
                return Status.RUNNING
        return super().update()


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


def _wrap_deg(d):
    """Fold an angle difference into [-180, 180)."""
    return (d + 180.0) % 360.0 - 180.0


class ChargeThroughBlock(py_trees.behaviour.Behaviour):
    """Mop-up pass after a Nav2 route: drive straight THROUGH any block the
    route left within reach.

    Nav2 finishes a route within its goal tolerance, which can leave the
    last block ~20 cm outside the intake. If a known block remains within
    TRIGGER_RANGE_M when this runs, steer-while-moving (no stop, no in-place
    rotation — the flow-through constraint holds) through the block position
    plus PASS_BEYOND_M, so the fans pass over its center. SUCCESS when the
    pass completes or there is nothing in reach; FAILURE only if the laser
    says the path is blocked. The block memory's eat-prune then records the
    collection on its own.
    """

    TRIGGER_RANGE_M = 0.90
    PASS_BEYOND_M = 0.25
    REACHED_M = 0.12
    SPEED_M_S = 0.14
    STEER_GAIN = 1.8
    STEER_WZ_MAX = 0.6
    STOP_DIST_M = 0.30          # laser front-sector floor (walls, not blocks)

    def __init__(self, name="Charge_Through_Block"):
        super().__init__(name)
        self.node = None
        self._cmd_pub = None
        self._target = None

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
        self.tf_buffer = _shared_tf_buffer(self.node)
        self.memory = _shared_block_memory(self.node, self.tf_buffer)

    def initialise(self):
        self._target = None
        robot = _robot_xy(self.tf_buffer)
        if robot is None or not self.memory.blocks:
            return
        nearest = min(self.memory.blocks,
                      key=lambda b: math.hypot(b[0] - robot[0], b[1] - robot[1]))
        dist = math.hypot(nearest[0] - robot[0], nearest[1] - robot[1])
        if dist > self.TRIGGER_RANGE_M:
            return
        # Aim PAST the block along the robot->block line: the intake must
        # cross the block's center, not park next to it.
        ux, uy = (nearest[0] - robot[0]) / dist, (nearest[1] - robot[1]) / dist
        self._target = (nearest[0] + ux * self.PASS_BEYOND_M,
                        nearest[1] + uy * self.PASS_BEYOND_M)
        self.logger.info(f"[{self.name}] block {dist:.2f} m away after route — "
                         f"charging through to ({self._target[0]:.2f}, {self._target[1]:.2f})")

    def _stop(self):
        if self._cmd_pub is not None:
            self._cmd_pub.publish(Twist())

    def _front_clearance(self):
        scan = self.node.bt_scan_cache["msg"]
        if scan is None:
            return None
        best = float('inf')
        a = scan.angle_min
        for r in scan.ranges:
            bearing = math.degrees(a)
            a += scan.angle_increment
            if abs(_wrap_deg(bearing)) > 20.0:
                continue
            if math.isfinite(r) and r > scan.range_min:
                best = min(best, r)
        return best

    def update(self) -> Status:
        if self._target is None:
            return Status.SUCCESS   # nothing left in reach — pass not needed
        robot = _robot_xy(self.tf_buffer)
        yaw = _robot_yaw(self.tf_buffer)
        if robot is None or yaw is None:
            return Status.RUNNING
        dist = math.hypot(self._target[0] - robot[0], self._target[1] - robot[1])
        if dist < self.REACHED_M:
            self._stop()
            self.logger.info(f"[{self.name}] pass complete.")
            return Status.SUCCESS
        clearance = self._front_clearance()
        if clearance is not None and clearance < self.STOP_DIST_M:
            self._stop()
            self.logger.warning(f"[{self.name}] wall {clearance:.2f} m ahead — abandoning pass.")
            return Status.FAILURE
        # Steer while moving: bearing P-control toward the through-point.
        # NOTE: yaw here is map-frame (the target is map-frame); _robot_yaw
        # reads odom yaw, so use the map-frame heading from TF instead.
        bearing = math.atan2(self._target[1] - robot[1], self._target[0] - robot[0])
        try:
            t = self.tf_buffer.lookup_transform("map", "base_link", Time())
            q = t.transform.rotation
            yaw_map = math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                                 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        except Exception:
            return Status.RUNNING
        err = math.atan2(math.sin(bearing - yaw_map), math.cos(bearing - yaw_map))
        cmd = Twist()
        cmd.linear.x = self.SPEED_M_S
        cmd.angular.z = max(-self.STEER_WZ_MAX,
                            min(self.STEER_WZ_MAX, self.STEER_GAIN * err))
        self._cmd_pub.publish(cmd)
        return Status.RUNNING

    def terminate(self, new_status):
        self._stop()


class TurnRight(py_trees.behaviour.Behaviour):
    """Rotate clockwise in place by `angle_deg` — the search scan.

    Stops EARLY (SUCCESS) the moment vision knows at least one block: this
    is a scan for blocks, not a precision turn. Yaw is integrated from the
    odom frame (continuous, no AMCL jumps), so the turn is correct even
    while AMCL refines. Wrap with a Timeout — a dead /cmd_vel chain would
    otherwise spin the tree here forever.
    """

    SPEED_RAD_S = 0.5

    def __init__(self, name="Turn_Right", angle_deg=90.0):
        super().__init__(name)
        self.angle_rad = math.radians(angle_deg)
        self.node = None
        self._cmd_pub = None

    def setup(self, **kwargs):
        self.node = kwargs.get("node")
        if self.node is None:
            raise RuntimeError("ROS 2 node context missing.")
        self._cmd_pub = self.node.create_publisher(Twist, '/cmd_vel', 10)
        self.tf_buffer = _shared_tf_buffer(self.node)
        self.memory = _shared_block_memory(self.node, self.tf_buffer)

    def initialise(self):
        self._last_yaw = None
        self._turned = 0.0

    def _stop(self):
        if self._cmd_pub is not None:
            self._cmd_pub.publish(Twist())

    def update(self) -> Status:
        if self.memory.blocks:
            self._stop()
            self.logger.info(
                f"[{self.name}] vision sees {len(self.memory.blocks)} block(s) "
                f"after {math.degrees(-self._turned):.0f} deg — stopping scan.")
            return Status.SUCCESS
        yaw = _robot_yaw(self.tf_buffer)
        if yaw is None:
            return Status.RUNNING   # TF not up yet; Timeout wrapper bounds this
        if self._last_yaw is not None:
            self._turned += math.atan2(math.sin(yaw - self._last_yaw),
                                       math.cos(yaw - self._last_yaw))
        self._last_yaw = yaw
        if self._turned <= -self.angle_rad:   # clockwise = negative yaw delta
            self._stop()
            self.logger.info(f"[{self.name}] turned {math.degrees(-self._turned):.0f} deg, "
                             "no blocks in sight — continuing search.")
            return Status.SUCCESS
        cmd = Twist()
        cmd.angular.z = -self.SPEED_RAD_S
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

    HEADING_GAIN = 2.0         # rad/s per rad of heading error
    HEADING_WZ_MAX = 0.5

    def __init__(self, name="Seek_Block_Forward"):
        super().__init__(name)
        self.node = None
        self._cmd_pub = None
        self.memory = None
        self.tf_buffer = None
        self._target_yaw = None

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
        self.tf_buffer = _shared_tf_buffer(self.node)
        self.memory = _shared_block_memory(self.node, self.tf_buffer)

    def initialise(self):
        self._target_yaw = None   # re-latch the heading on every activation

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
        # Heading hold: latch the yaw at seek start and P-control angular.z to
        # keep it. Open-loop linear.x alone veered/turned on the real robot
        # (wheel asymmetry + fan reaction torque) — Nav2 normally closes this
        # loop for us; here we must do it ourselves.
        cmd = Twist()
        cmd.linear.x = self.SPEED_M_S
        yaw = _robot_yaw(self.tf_buffer)
        if yaw is not None:
            if self._target_yaw is None:
                self._target_yaw = yaw
            err = math.atan2(math.sin(self._target_yaw - yaw),
                             math.cos(self._target_yaw - yaw))
            cmd.angular.z = max(-self.HEADING_WZ_MAX,
                                min(self.HEADING_WZ_MAX, self.HEADING_GAIN * err))
        self._cmd_pub.publish(cmd)
        return Status.RUNNING

    def terminate(self, new_status):
        self._stop()


class TimeAlmostUp(py_trees.behaviour.Behaviour):
    """SUCCESS once the mission clock leaves only the final-unload reserve.

    The clock starts at this behavior's FIRST tick ever — i.e. right after
    the first localization, when the mission actually begins — and persists
    across loop iterations (the behavior instance lives as long as the
    tree). FAILURE while there is still collecting time left.
    """
    def __init__(self, name="Time_Almost_Up",
                 limit_s=MISSION_TIME_LIMIT_S, reserve_s=FINAL_UNLOAD_RESERVE_S):
        super().__init__(name)
        self.cutoff_s = limit_s - reserve_s
        self.node = None
        self._t0 = None

    def setup(self, **kwargs):
        self.node = kwargs.get("node")
        if self.node is None:
            raise RuntimeError("ROS 2 node context missing.")

    def update(self) -> Status:
        now = self.node.get_clock().now()
        if self._t0 is None:
            self._t0 = now
            self.logger.info(f"[{self.name}] mission clock started "
                             f"(cutoff in {self.cutoff_s:.0f} s).")
        elapsed = (now - self._t0).nanoseconds * 1e-9
        if elapsed >= self.cutoff_s:
            self.logger.warning(f"[{self.name}] {elapsed:.0f} s elapsed — "
                                "forcing the final unload.")
            return Status.SUCCESS
        return Status.FAILURE


class Park(py_trees.behaviour.Behaviour):
    """RUNNING forever — pins the tree once the mission is over so the loop
    cannot restart after the final unload."""
    def __init__(self, name="Mission_Over_Park"):
        super().__init__(name)
        self.node = None

    def setup(self, **kwargs):
        self.node = kwargs.get("node")

    def update(self) -> Status:
        if self.node is not None:
            self.node.get_logger().info(
                "[park] mission complete — robot parked at base.",
                throttle_duration_sec=30.0)
        return Status.RUNNING


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
# TREE COMPOSITION
# =========================================================

# Mission calibration points, MAP frame, derived from ros2_ws/maps/ref.png
# under the current clean_room_8x8.yaml origin. Third element = arrival yaw.
# POSE_BASE (the green marker in ref.png) is the initial pose AND the
# delivery zone — the loop mission unloads there and restarts from there.
# Arrival yaw 2.38 (facing the arena origin) is the validated unload
# orientation — confirmed on hardware, do not "simplify" to a flat angle.
POSE_BASE = (1.005, -0.955, 2.381699)             # green point; face arena origin
# Geometric center of the arena free space (BlockMemory X_RANGE x Y_RANGE).
# Only used by the test_center smoke-test mission.
POSE_ARENA_CENTER = (4.4, -4.0, 0.0)


def _goto(name, arena_pose, timeout_s):
    """GoToPose at a calibrated mission pose, wrapped in the standard timeout/skip."""
    x, y = arena_to_map(arena_pose[0], arena_pose[1])
    return wrap_with_timeout(GoToPose(name, x, y, target_yaw=arena_pose[2]), timeout_s)


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


def _with_timeout(behaviour_node, duration_seconds):
    """Timeout WITHOUT FailureIsSuccess — for children inside a Selector, where
    a failure must fall through to the next option instead of faking success."""
    return py_trees.decorators.Timeout(
        child=behaviour_node, duration=duration_seconds,
        name=f"{behaviour_node.name}_Timeout")


def _collect_round():
    """One search-and-collect pass.

    Find blocks: if BlockMemory already knows some, plan straight away;
    otherwise scan — turn right (stops early the moment vision spots a
    block), creep forward if still nothing, then plan. Collect by flowing
    THROUGH the planned block positions (NavigateThroughPoses — never
    stop-and-pick, the fans absorb on the pass).

    A dry round (nothing found / seek hit a wall) FAILS; the caller wraps it
    skippable, so the mission loop just comes around again — and since the
    turn moved the robot 90 deg, consecutive dry rounds scan the whole room.
    """
    seq = py_trees.composites.Sequence(name="Round", memory=True)

    find = py_trees.composites.Selector(name="Round_Find", memory=True)
    find.add_child(PlanBlockRoute("Plan_Known_Blocks"))
    search = py_trees.composites.Sequence(name="Round_Search", memory=True)
    search.add_child(_with_timeout(TurnRight("Turn_Right_Scan", angle_deg=90.0), 30.0))
    search.add_child(_with_timeout(SeekBlockForward("Seek_Forward"), 25.0))
    search.add_child(PlanBlockRoute("Plan_Found_Blocks"))
    find.add_child(search)
    seq.add_child(find)

    # Dynamic queue: every block detected while driving preempts the route
    # with a re-plan that includes it. 180 s: the queue legitimately grows
    # mid-leg, so this leg earns more budget than a frozen route would.
    seq.add_child(_with_timeout(FollowBlockQueue("Drive_Block_Queue"), 180.0))

    # Mop-up: Nav2 ends a route within its goal tolerance, which can leave
    # the last block just outside the fans (the planned overshoot waypoint
    # usually prevents this, but it is skipped when it would land in a
    # wall). Skippable: a failed pass must not kill the round.
    seq.add_child(wrap_with_timeout(ChargeThroughBlock("Mop_Up_Pass"), 20.0))
    return seq


def create_tree(mission="loop"):
    """Mission selector (--mission CLI flag / bt_mission launch argument).

    loop (default)  Endless collect cycle: localize -> fans on -> [turn
           right, search/detect blocks, plan a route, flow through it] ->
           once >= DISCHARGE_BLOCK_COUNT blocks are on board, drive to the
           delivery zone (POSE_BASE, also the initial pose), unload, and
           start again. The root sequence completing IS the loop: py_trees
           re-initialises it on the next tick, forever.
    test_center  Nav2 smoke test: localize, then ONE goal at the arena
           center (POSE_ARENA_CENTER) — no fans, no collection, no unload.
    """
    root = py_trees.composites.Sequence(name=f"Mission_{mission}", memory=True)

    if mission == "test_center":
        root.add_child(WaitForLocalization())
        root.add_child(_goto("Test_Center", POSE_ARENA_CENTER, 120.0))
        return root

    # Prologue (re-checked every loop iteration, instant when already up):
    # localized first, then fans spinning BEFORE any motion (blocks must be
    # absorbable from the very first meter).
    root.add_child(WaitForLocalization())

    # Time budget: once only the unload reserve is left, skip collecting,
    # deliver whatever is on board, stop the intake and park for good.
    # While time remains, TimeAlmostUp FAILS and the wrapper skips onward.
    timeout_unload = py_trees.composites.Sequence(name="Final_Unload_On_Time", memory=True)
    timeout_unload.add_child(TimeAlmostUp())
    timeout_unload.add_child(_discharge_at_base("TimeUp"))
    timeout_unload.add_child(SetMotor("Fans_Off_Final", '/cmd_fans', 0.0))
    timeout_unload.add_child(Park())
    root.add_child(py_trees.decorators.FailureIsSuccess(
        child=timeout_unload, name="Final_Unload_Skippable"))

    root.add_child(SetMotor("Fans_On", '/cmd_fans', FAN_SPEED))

    # One collect round per loop pass; a dry round must not stall the loop.
    root.add_child(py_trees.decorators.FailureIsSuccess(
        child=_collect_round(), name="Round_Skippable"))

    # Unload gate: only when the on-board count reaches the target.
    # _discharge_at_base ends AT the base = the initial pose, count reset —
    # the loop then restarts from exactly the mission's starting state.
    unload = py_trees.composites.Sequence(name="Unload_When_Full", memory=True)
    unload.add_child(HoldEnoughBlocks(f"Hold_{DISCHARGE_BLOCK_COUNT}"))
    unload.add_child(_discharge_at_base("Loop"))
    root.add_child(py_trees.decorators.FailureIsSuccess(
        child=unload, name="Unload_Skippable"))

    return root


def main(args=None):
    # --mission selects the tree composition; ROS args pass through untouched.
    parser = argparse.ArgumentParser(description="EyeRobot mission behavior tree")
    parser.add_argument('--mission', default='loop',
                        choices=['loop', 'test_center'],
                        help="loop = endless search/collect/unload cycle (default); "
                             "test_center = Nav2 smoke test, single goal at the arena center")
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
