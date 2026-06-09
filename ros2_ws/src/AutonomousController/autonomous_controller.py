#!/usr/bin/env python3
from __future__ import annotations

import math
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Float32


class State(Enum):
    INITIALIZE = auto()
    STOP = auto()
    GO_TO_RAMP = auto()
    CLIMB_RAMP = auto()
    ALIGN_W_RAMP = auto()
    FIND_DUPLO = auto()
    EAT_DUPLO = auto()

class Robot:
    """Stores the current physical state and worldview of the robot."""
    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.checkpoint = (0.0, 0.0, 0.0)  # (x, y, theta) of the next navigation target
        self.checkpoint_tolerance = 0.1  # meters
        self.checkpoint_angle_tolerance = math.radians(10)  # converted to radians
        self.kp_linear = 1.0  # Proportional gain for linear speed
        self.kp_angle = 1.0  # Proportional gain for angle correction
    
    def set_checkpoint(self, x: float, y: float, theta: float) -> None:
        self.checkpoint = (x, y, theta)

    def set_relative_checkpoint(self, dx: float, dy: float, dtheta: float) -> None:
        desired_theta = math.atan2(dy, dx)
        self.set_checkpoint(self.x + dx, self.y + dy, desired_theta)

    def is_checkpoint_reached(self):
        dx = self.x - self.checkpoint[0]
        dy = self.y - self.checkpoint[1]
        dtheta = abs((self.theta - self.checkpoint[2] + math.pi) % (2 * math.pi) - math.pi)
        #if the robot is within the tolerance of the checkpoint, we consider it reached
        checkpoint_reached = (math.sqrt(dx**2 + dy**2) < self.checkpoint_tolerance) and (dtheta < self.checkpoint_angle_tolerance)
        return checkpoint_reached
    
    def dist_to_checkpoint(self) -> float:
        dx = self.x - self.checkpoint[0]
        dy = self.y - self.checkpoint[1]
        return math.sqrt(dx**2 + dy**2)
    
    def angle_to_checkpoint(self) -> float:
        desired_theta = math.atan2(self.checkpoint[1] - self.y, self.checkpoint[0] - self.x)
        angle_diff = (desired_theta - self.theta + math.pi) % (2 * math.pi) - math.pi
        return angle_diff
    
    def rotate_in_place(self,speed) -> tuple[float, float]:
        return speed, -speed
    
    def go_to_checkpoint(self): #replace this with nav2
        linear_speed = self.kp.linear * self.dist_to_checkpoint()
        angle_speed = self.kp_angle * self.angle_to_checkpoint() + self.kp_angle * ((self.theta - self.checkpoint[2] + math.pi) % (2 * math.pi) - math.pi)

        return linear_speed + angle_speed, linear_speed - angle_speed #TODO we might need to clip linear_speed+angle_speed to avoid saturation and ffectively turn



class Duplo:
    """Represents a detected Duplo block in the environment."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        # self.picked_up = False


class AutonomousControllerNode(Node):
    def __init__(self) -> None:
        super().__init__('autonomous_controller')

        self.verbose = True
        # --- Parameters ---
        self.declare_parameter('control_rate_hz', 20.0)
        self.declare_parameter('base_speed_rad_s', 8.0)
        
        self.control_rate = self.get_parameter('control_rate_hz').value
        self.base_speed = self.get_parameter('base_speed_rad_s').value

        # --- FSM Initialization ---
        self.current_state = State.INITIALIZE
        self.robot = Robot()
        self.next_duplo = None

        # --- Publishers (Matching your manual controller QoS) ---
        cmd_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.pub_r = self.create_publisher(Float32, 'motor_rwheel_cmd', cmd_qos)
        self.pub_l = self.create_publisher(Float32, 'motor_lwheel_cmd', cmd_qos)
        self.pub_rfan = self.create_publisher(Float32, 'motor_rfan_cmd', cmd_qos)
        self.pub_lfan = self.create_publisher(Float32, 'motor_lfan_cmd', cmd_qos)
        self.pub_belt = self.create_publisher(Float32, 'motor_belt_cmd', cmd_qos)

        # --- Subscriptions ---
        # TODO: Add subscriptions for your sensors here (e.g., Odometry, LiDAR)
        # self.sub_odom = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)

        self.timer = self.create_timer(1.0 / self.control_rate, self.main_loop) #TODO check if this works

        self.get_logger().info('Autonomous FSM Controller initialized.')

    def main_loop(self) -> None:
        self.update_sensors()
        self.evaluate_state_transitions()
        commands = self.execute_current_state()
        self.publish_commands(*commands)

    def update_sensors(self) -> None:
        """Update the internal Robot with fresh sensor data."""
        # TODO: Pull data from your subscription callbacks into the self.robot dataclass
        # Example: self.robot.obstacle_ahead = self._latest_lidar_flag
        return

    def evaluate_state_transitions(self) -> None:
        """Determines if the FSM should shift to a new state based on the environment."""
        if self.current_state == State.INITIALIZE:
            self.current_state = State.GO_TO_RAMP
            
        elif self.current_state == State.GO_TO_RAMP:
            if self.robot.is_checkpoint_reached():
                self.current_state = State.ALIGN_W_RAMP
                self.robot.set_checkpoint(7.75, 4.5, 0.0)
            else :
                self.robot.set_checkpoint(7.0, 3.0, 0.0)

        elif self.current_state == State.ALIGN_W_RAMP:
            if self.robot.is_checkpoint_reached():
                self.current_state = State.CLIMB_RAMP
            else :
                self.robot.set_checkpoint(7.75, 6.5, -np.pi/4)

        elif self.current_state == State.CLIMB_RAMP:
            None

        elif self.current_state == State.FIND_DUPLO:
            if self.next_duplo is not None:
                self.current_state = State.EAT_DUPLO
                self.robot.set_relative_checkpoint(self.next_duplo.x, self.next_duplo.y, 0.0)

        elif self.current_state == State.EAT_DUPLO:
            if self.robot.is_checkpoint_reached():
                self.next_duplo = None
                self.current_state = State.FIND_DUPLO


        if self.verbose:
            self.get_logger().info(f'Current State: {self.current_state.name}')


    def execute_current_state(self) -> tuple[float, float, float, float, float]:
        """Calculates motor commands based on the active state."""
        r_wheel, l_wheel, r_fan, l_fan, belt = 0.0, 0.0, 0.0, 0.0, 0.0

        if self.current_state == State.STOP:
            pass

        elif self.current_state == State.GO_TO_RAMP:
            r_wheel, l_wheel = self.robot.go_to_checkpoint()


            
        elif self.current_state == State.FIND_DUPLO:
            x, y, duplo_found = self.find_duplo()
            if duplo_found:
                self.next_duplo = Duplo(x, y)
            else:
                r_wheel, l_wheel = self.robot.rotate_in_place(self.base_speed)
                


        elif self.current_state == State.EAT_DUPLO:
            self.robot.go_to_checkpoint()



        return r_wheel, l_wheel, r_fan, l_fan, belt
            

    def find_duplo(self) -> tuple[float, float, bool]:
        """Processes sensor data to locate the nearest Duplo block."""
        x, y = 0.0, 0.0
        duplo_found = False

        #TODO : Analyse cam data

        return x, y, duplo_found

    def publish_commands(self, right: float, left: float, rfan: float, lfan: float, belt: float) -> None:
        """Pushes the computed commands to the micro-ROS bridge."""
        self.pub_r.publish(Float32(data=right))
        self.pub_l.publish(Float32(data=left))
        self.pub_rfan.publish(Float32(data=rfan))
        self.pub_lfan.publish(Float32(data=lfan))
        self.pub_belt.publish(Float32(data=belt))



def main(args=None) -> None: #TO be checked
    rclpy.init(args=args)
    node = AutonomousControllerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Autonomous controller interrupted by user.')
    finally:
        node.publish_commands(0.0, 0.0, 0.0, 0.0, 0.0)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()