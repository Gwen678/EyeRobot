#!/usr/bin/env python3
import rclpy
from rclpy.action import ActionClient
import py_trees
import py_trees_ros
from py_trees.common import Status

# ROS 2 Navigation Messages
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus

VERBOSE = True  

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

    def setup(self, **kwargs):
        """Extracts the ROS 2 node from the py_trees_ros environment setup."""
        self.node = kwargs.get("node")
        if self.node is None:
            self.logger.error(f"[{self.name}] ROS 2 node context not found in setup!")
            raise RuntimeError("ROS 2 node context missing.")
        
        self.action_client = ActionClient(self.node, NavigateToPose, 'navigate_to_pose')
        self.action_client.wait_for_server()

    def initialise(self) -> None:
        """Fires every time the behavior switches from inactive to active."""
        self.tick_count = 0
        self.goal_status = None
        self.goal_handle = None
        
        self.logger.info(f"[{self.name}] Target Goal: X={self.target_x}, Y={self.target_y}")

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.node.get_clock().now().to_msg()
        
        # Inject our instance-specific coordinates
        goal_msg.pose.pose.position.x = self.target_x
        goal_msg.pose.pose.position.y = self.target_y
        goal_msg.pose.pose.orientation.w = 1.0 

        send_goal_future = self.action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self._goal_response_callback)

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
        
        if self.goal_status in [GoalStatus.STATUS_ABORTED, GoalStatus.STATUS_CANCELED, GoalStatus.STATUS_UNKNOWN]:
            self.logger.error(f"[{self.name}] Nav2 failed to reach target.")
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
    
    # 1. Create a dedicated composite branch for the Button Phase
    goto_button_branch = py_trees.composites.Sequence(name="GoToButton_Branch", memory=True)
    
    # Add your two specific sequential waypoints inside this sub-branch
    goto_button_branch.add_child(wrap_with_timeout(GoToPose("Move_To_Button", 1.0, 0.0), 25.0))
    goto_button_branch.add_child(wrap_with_timeout(GoToPose("Pass_Door", 1.0, 1.0), 25.0))
    goto_button_branch.add_child(wrap_with_timeout(GoToPose("Return_To_Base", 0.0, 0.0), 25.0))
    
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