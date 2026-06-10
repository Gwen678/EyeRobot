#!/usr/bin/env python3
import math

import rclpy
from rclpy.action import ActionClient
from rclpy.time import Time
import py_trees
import py_trees_ros
from py_trees.common import Status
from tf2_ros import Buffer, TransformListener

# ROS 2 Navigation Messages
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose, NavigateThroughPoses
from action_msgs.msg import GoalStatus

VERBOSE = True

# Pullback retry distances (meters). If Nav2 cannot plan through a target
# (e.g. a lego block sitting against a wall, inside the costmap inflation
# radius), we retry with that pose pulled back along its approach line. The
# robot then passes nose-first just short of the block and the front fans
# absorb it on the close pass — we never need to physically reach the
# block's center.
PULLBACK_OFFSETS = (0.0, 0.25, 0.45)


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
    """A reusable Behavior Tree leaf node that sends the robot to specific coordinates via Nav2."""
    def __init__(self, name="Go_To_Pose", target_x=0.0, target_y=0.0):
        super().__init__(name)
        self.target_x = target_x
        self.target_y = target_y

        self.node = None
        self.action_client = None
        self.goal_handle = None
        self.goal_status = None
        self.tick_count = 0
        self.attempt = 0

    def setup(self, **kwargs):
        """Extracts the ROS 2 node from the py_trees_ros environment setup."""
        self.node = kwargs.get("node")
        if self.node is None:
            self.logger.error(f"[{self.name}] ROS 2 node context not found in setup!")
            raise RuntimeError("ROS 2 node context missing.")

        self.action_client = ActionClient(self.node, NavigateToPose, 'navigate_to_pose')
        self.action_client.wait_for_server()
        self.tf_buffer = _shared_tf_buffer(self.node)

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
            self.logger.warn(f"[{self.name}] No map->base_link TF; retrying exact target without pullback.")

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
        send_goal_future = self.action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self._goal_response_callback)

    def initialise(self) -> None:
        """Fires every time the behavior switches from inactive to active."""
        self.tick_count = 0
        self.attempt = 0
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
            if self.attempt + 1 < len(PULLBACK_OFFSETS):
                self.attempt += 1
                offset = PULLBACK_OFFSETS[self.attempt]
                self.logger.warn(f"[{self.name}] Nav2 aborted; retry {self.attempt} with {offset} m pullback.")
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
            self.logger.warn(f"[{self.name}] Interrupted! Canceling active navigation.")
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

    def setup(self, **kwargs):
        """Extracts the ROS 2 node from the py_trees_ros environment setup."""
        self.node = kwargs.get("node")
        if self.node is None:
            self.logger.error(f"[{self.name}] ROS 2 node context not found in setup!")
            raise RuntimeError("ROS 2 node context missing.")

        self.action_client = ActionClient(self.node, NavigateThroughPoses, 'navigate_through_poses')
        self.action_client.wait_for_server()
        self.tf_buffer = _shared_tf_buffer(self.node)

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
        self.logger.info(f"[{self.name}] Routing through {self.sent_count} pose(s): {self.pending}")
        send_goal_future = self.action_client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_callback)
        send_goal_future.add_done_callback(self._goal_response_callback)

    def initialise(self) -> None:
        """Fires every time the behavior switches from inactive to active."""
        self.tick_count = 0
        self.pending = list(self.waypoints)
        self.pb_level = [0] * len(self.pending)
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
            self.logger.warn(
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
            self.logger.warn(f"[{self.name}] Interrupted! Canceling active navigation.")
            self.goal_handle.cancel_goal_async()

        self.goal_handle = None
        self.goal_status = None


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

class AlignWithWall(py_trees.behaviour.Behaviour):
    def __init__(self, name="Align_With_Wall"): super().__init__(name)
    def update(self): return Status.SUCCESS

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
# TREE COMPOSITION WITH NESTED WAYPOINTS
# =========================================================

def create_tree():
    # Main overall mission line
    root = py_trees.composites.Sequence(name="Mission_Principale", memory=True)

    # 0. Gate: do nothing until AMCL is localized (no timeout wrapper — see class doc).
    root.add_child(WaitForLocalization())

    # 1. Create a dedicated composite branch for the Button Phase
    goto_button_branch = py_trees.composites.Sequence(name="GoToButton_Branch", memory=True)

    # One flow-through route: the robot passes the intermediate poses without
    # stopping (blocks are absorbed by the fans in passing). The timeout covers
    # the whole route including pullback retries on infeasible poses.
    # GoToPose remains available for single stop-at-goal moves (e.g. parking in
    # front of the button before pushing it).
    goto_button_branch.add_child(wrap_with_timeout(
        GoThroughPoses("Button_Route", [(1.0, 0.0), (1.0, 1.0), (0.0, 0.0)]), 90.0))
    
    # 2. Append the branches and actions directly to the main mission tree
    root.add_child(goto_button_branch)
    root.add_child(wrap_with_timeout(PushButton(), 5.0))
    root.add_child(wrap_with_timeout(AlignWithWall(), 5.0))
    root.add_child(wrap_with_timeout(ClimbDoor(), 5.0))
    root.add_child(wrap_with_timeout(GoToStart(), 5.0))
    root.add_child(wrap_with_timeout(Delivery(), 5.0))
        
    return root


def main(args=None):
    rclpy.init(args=args)
    tree_root = create_tree()
    
    if VERBOSE:
        print("\n--- BEHAVIOR TREE STRUCTURE ---")
        print(py_trees.display.unicode_tree(tree_root))
        print("-------------------------------\n")
    
    tree = py_trees_ros.trees.BehaviourTree(
        root=tree_root,
        unicode_tree_debug=False
    )

    tree.setup(node_name="autonomous_controller", timeout=15.0)
    
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