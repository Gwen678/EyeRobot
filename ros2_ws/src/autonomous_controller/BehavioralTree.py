#!/usr/bin/env python3
import rclpy
import py_trees
import py_trees_ros
from py_trees.common import Status

VERBOSE = True  

class GoToButton(py_trees.behaviour.Behaviour):
    def __init__(self, name="Go_To_Button"):
        super().__init__(name)
        self.target_reached = False
        self.tick_count = 0

    def update(self):
        self.tick_count += 1
        if VERBOSE and self.tick_count % 10 == 0:
            print(f"[{self.name}] Navigating to button... (Waiting for timeout)")
        
        if self.target_reached:
            return Status.SUCCESS
        return Status.RUNNING

class PushButton(py_trees.behaviour.Behaviour):
    def __init__(self, name="Push_Button"):
        super().__init__(name)
        self.button_pushed = False
        self.tick_count = 0

    def update(self):
        self.tick_count += 1
        if VERBOSE and self.tick_count % 10 == 0:
            print(f"[{self.name}] Pushing mechanism active... (Waiting for timeout)")
            
        if self.button_pushed:
            return Status.SUCCESS
        return Status.RUNNING

class AlignWithWall(py_trees.behaviour.Behaviour):
    def __init__(self, name="Align_With_Wall"):
        super().__init__(name)
        self.is_aligned = False
        self.tick_count = 0

    def update(self):
        self.tick_count += 1
        if VERBOSE and self.tick_count % 10 == 0:
            print(f"[{self.name}] Aligning 4-wheeled base to wall... (Waiting for timeout)")
            
        if self.is_aligned:
            return Status.SUCCESS
        return Status.RUNNING

class ClimbDoor(py_trees.behaviour.Behaviour):
    def __init__(self, name="Climb_Door"):
        super().__init__(name)
        self.door_passed = False
        self.tick_count = 0

    def update(self):
        self.tick_count += 1
        if VERBOSE and self.tick_count % 10 == 0:
            print(f"[{self.name}] Crossing the door... (Waiting for timeout)")
            
        if self.door_passed:
            return Status.SUCCESS
        return Status.RUNNING

class GoToStart(py_trees.behaviour.Behaviour):
    def __init__(self, name="Go_To_Start"):
        super().__init__(name)
        self.at_start_zone = False
        self.tick_count = 0

    def update(self):
        self.tick_count += 1
        if VERBOSE and self.tick_count % 10 == 0:
            print(f"[{self.name}] Returning to start zone... (Waiting for timeout)")
            
        if self.at_start_zone:
            return Status.SUCCESS
        return Status.RUNNING

class Delivery(py_trees.behaviour.Behaviour):
    def __init__(self, name="Delivery"):
        super().__init__(name)
        self.delivered = False
        self.tick_count = 0

    def update(self):
        self.tick_count += 1
        if VERBOSE and self.tick_count % 10 == 0:
            print(f"[{self.name}] Executing delivery sequence... (Waiting for timeout)")
            
        if self.delivered:
            return Status.SUCCESS
        return Status.RUNNING

# =========================================================
# =========================================================

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
    
    steps_with_timeouts = [
        (GoToButton(), 3.0),      
        (PushButton(), 2.0),      
        (AlignWithWall(), 3.0),    
        (ClimbDoor(), 2.0),       
        (GoToStart(), 4.0),       
        (Delivery(), 2.0)        
    ]
    
    for action_node, duration in steps_with_timeouts:
        root.add_child(wrap_with_timeout(action_node, duration))
        
    return root


# =========================================================
# NŒUD ROS 2 PRINCIPAL
# =========================================================
def main(args=None):
    rclpy.init(args=args)
    
    tree_root = create_tree()
    
    if VERBOSE:
        print("\n--- BEHAVIOR TREE STRUCTURE ---")
        print(py_trees.display.unicode_tree(tree_root))
        print("-------------------------------\n")
    
    tree = py_trees_ros.trees.BehaviourTree(
        root=tree_root,
        unicode_tree_debug=False # Disabled default debug to prioritize our custom prints
    )

    tree.setup(node_name="autonomous_controller", timeout=15.0)
    
    if VERBOSE:
        print("Starting execution loop. Watch the timeouts trigger...\n")
        
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
