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

class GoToButton(py_trees.behaviour.Behaviour):
    def __init__(self, name="Go_To_Button"):
        super().__init__(name)
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
        
        # Initialize the Action Client pointing to Nav2's standard server
        self.action_client = ActionClient(self.node, NavigateToPose, 'navigate_to_pose')
        self.logger.info(f"[{self.name}] Waiting for Nav2 navigate_to_pose action server...")
        self.action_client.wait_for_server()

    def initialise(self) -> None:
        """Fires once when the behavior switches from another node to this one."""
        self.tick_count = 0
        self.goal_status = None
        self.goal_handle = None
        
        self.logger.info(f"[{self.name}] Sending goal coordinate to Nav2...")

        # Define your checkpoint (e.g., 1.0 meter straight ahead in the map frame)
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.node.get_clock().now().to_msg()
        
        # Set target checkpoint coordinates
        goal_msg.pose.pose.position.x = 1.0  # 1 meter forward
        goal_msg.pose.pose.position.y = 0.0
        goal_msg.pose.pose.orientation.w = 1.0 # Facing forward

        # Send the goal asynchronously to avoid freezing the Behavior Tree loop
        send_goal_future = self.action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future):
        """Callback tracking if Nav2 accepted or rejected our target checkpoint."""
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.logger.error(f"[{self.name}] Target checkpoint rejected by Nav2 planner!")
            self.goal_status = GoalStatus.STATUS_ABORTED
            return

        self.logger.info(f"[{self.name}] Target accepted. Moving...")
        result_future = self.goal_handle.get_result_async()
        result_future.add_done_callback(self._goal_result_callback)

    def _goal_result_callback(self, future):
        """Callback tracking if Nav2 finished navigating or encountered a obstacle failure."""
        status = future.result().status
        self.goal_status = status

    def update(self) -> Status:
        """Evaluates every 50ms while this behavior is actively running."""
        self.tick_count += 1
        
        if VERBOSE and self.tick_count % 20 == 0:
            print(f"[{self.name}] Nav2 is calculating and driving... (Tick: {self.tick_count})")

        # 1. If Nav2 hasn't responded or is actively processing paths
        if self.goal_status is None:
            return Status.RUNNING

        # 2. Check Nav2 state outputs
        if self.goal_status == GoalStatus.STATUS_SUCCEEDED:
            self.logger.info(f"[{self.name}] Successfully reached the checkpoint!")
            return Status.SUCCESS
        
        if self.goal_status in [GoalStatus.STATUS_ABORTED, GoalStatus.STATUS_CANCELED, GoalStatus.STATUS_UNKNOWN]:
            self.logger.error(f"[{self.name}] Nav2 failed to reach checkpoint or was blocked.")
            return Status.FAILURE

        return Status.RUNNING

    def terminate(self, new_status: Status) -> None:
        """Fires automatically when the node stops running (Success, Failure, or Overridden)."""
        # Failsafe: If the tree switches or times out, tell Nav2 to stop immediately
        if new_status == Status.INVALID and self.goal_handle is not None:
            self.logger.warn(f"[{self.name}] Behavior interrupted! Canceling active navigation.")
            self.goal_handle.cancel_goal_async()
        
        self.goal_handle = None
        self.goal_status = None


# =========================================================
# The rest of your structural blocks remain unchanged
# =========================================================

class PushButton(py_trees.behaviour.Behaviour):
    def __init__(self, name="Push_Button"):
        super().__init__(name)
        self.button_pushed = False
    def update(self):
        # Placeholder success loop for downstream actions
        return Status.SUCCESS if self.button_pushed else Status.RUNNING

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


def create_tree():
    root = py_trees.composites.Sequence(name="Mission_Principale", memory=True)
    
    # Notice we bumped the timeout to 15s to give the physical robot time to travel
    steps_with_timeouts = [
        (GoToButton(), 15.0),      
        (PushButton(), 2.0),      
        (AlignWithWall(), 3.0),    
        (ClimbDoor(), 2.0),       
        (GoToStart(), 4.0),       
        (Delivery(), 2.0)        
    ]
    
    for action_node, duration in steps_with_timeouts:
        root.add_child(wrap_with_timeout(action_node, duration))
        
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

    # Passes the underlying ROS 2 node context into all behaviors for Action Client binding
    tree.setup(node_name="autonomous_controller", timeout=15.0)
    
    try:
        tree.tick_tock(period_ms=50)
        rclpy.spin(tree.node)
    except KeyboardInterrupt:
        tree.node.get_logger().info('Stopping the behavior tree due to user interruption.')
    finally:
        tree.shutdown()
        rclpy.shutdown()

if __name__ == '__main__':
    main()