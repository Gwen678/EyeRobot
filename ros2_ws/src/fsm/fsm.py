import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped, Twist, Vector3
from sensor_msgs.msg import Imu
from nav2_msgs.action import NavigateToPose
import math
import time

class StrategyFSM(Node):
    def __init__(self):
        super().__init__('strategy_fsm')
        
        # --- MATCH CONFIGURATION ---
        self.state = 'INIT'
        self.lego_count = 0
        self.MAX_LEGOS = 6
        self.action_start_time = 0.0
        self.current_pitch = 0.0
        self.ramp_status = 'WAITING'
        
        # --- EXACT COORDINATES (8x8m Arena) ---
        self.POSE_BUTTON = self.create_pose(4.20, 7.50, 1.57)    # Facing the button
        self.POSE_DOOR = self.create_pose(8.235, -3.785, -1.570796)  # Door approach from pixel (285, 180), aligned with image vertical
        self.POSE_BASE = self.create_pose(1.005, -0.955, 2.381699)  # Drop-off point, facing arena origin
        self.POSE_RAMP_BASE = self.create_pose(4.985, -6.025, 0.0) # Ramp approach from pixel (220, 224.8), aligned with image horizontal
        
        # --- PUBLISHERS & SUBSCRIBERS ---
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)  # remapped into diff_drive_controller
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Replace Vector3 with the exact message type from your vision script
        self.create_subscription(Vector3, '/eyerobot/vision/lego_polar', self.vision_cb, 10)
        self.create_subscription(Imu, '/oak/imu/data_raw', self.imu_cb, 10)
        
        # Main control loop (runs at 10 Hz)
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("FSM Initialized. Ready for the match!")

    # -----------------------------------------------------------
    # MAIN LOOP (The Brain)
    # -----------------------------------------------------------
    def control_loop(self):
        cmd = Twist()
        
        if self.state == 'INIT':
            self.get_logger().info("Phase 1: Heading to the button...")
            self.send_nav2_goal(self.POSE_BUTTON)
            self.state = 'NAVIGATING'
            self.next_state = 'PUSH_BUTTON'
            
        elif self.state == 'PUSH_BUTTON':
            # Just arrived in front of the button, start the timer
            if self.action_start_time == 0.0:
                self.action_start_time = time.time()
                self.get_logger().info("Pushing the button...")
                
            elapsed = time.time() - self.action_start_time
            if elapsed < 2.0:
                cmd.linear.x = 0.15 # Move forward slowly but steadily
                self.cmd_pub.publish(cmd)
            else:
                # After 2 seconds, stop and move on
                cmd.linear.x = 0.0
                self.cmd_pub.publish(cmd)
                self.action_start_time = 0.0 # Reset timer
                self.get_logger().info("Button pressed! Crossing the door.")
                self.send_nav2_goal(self.POSE_DOOR)
                self.state = 'NAVIGATING'
                self.next_state = 'HUNT_ZONE_3'
                
        elif self.state == 'CLIMB_RAMP':
            self.handle_ramp()
            
        elif self.state == 'EMPTY_BASE':
            self.get_logger().info("Emptying Legos...")
            # Add a delay or trigger a servo motor here
            self.lego_count = 0
            self.get_logger().info("Inventory empty. Heading to the ramp.")
            self.send_nav2_goal(self.POSE_RAMP_BASE)
            self.state = 'NAVIGATING'
            self.next_state = 'CLIMB_RAMP'

    # -----------------------------------------------------------
    # SENSOR MANAGEMENT
    # -----------------------------------------------------------
    def imu_cb(self, msg):
        """ Converts the IMU quaternion to a Pitch angle """
        q = msg.orientation
        # Simplified math formula for pitch from a quaternion
        sinp = 2 * (q.w * q.y - q.z * q.x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)
        self.current_pitch = math.degrees(pitch)

    def vision_cb(self, msg):
        """ Called every time the camera sees a Lego """
        if self.lego_count >= self.MAX_LEGOS or self.state == 'NAVIGATING':
            return # Ignore vision if full or currently navigating
            
        if self.state in ['HUNT_ZONE_3', 'HUNT_ZONE_4']:
            # Visual servoing logic (adapt based on imu_plus_cam.py)
            cmd = Twist()
            # Basic example: move forward if lego is ahead (msg.x), turn based on angle (msg.y)
            cmd.linear.x = 0.2
            cmd.angular.z = msg.y * 1.5 
            self.cmd_pub.publish(cmd)
            
            # Simulate pickup (if lego is closer than 5 cm)
            if msg.x < 0.05 and msg.x > 0:
                self.lego_count += 1
                self.get_logger().info(f"Lego collected! ({self.lego_count}/{self.MAX_LEGOS})")
                
                if self.lego_count >= self.MAX_LEGOS:
                    self.get_logger().info("Robot FULL! Returning to base.")
                    self.send_nav2_goal(self.POSE_BASE)
                    self.state = 'NAVIGATING'
                    self.next_state = 'EMPTY_BASE'

    # -----------------------------------------------------------
    # RAMP LOGIC
    # -----------------------------------------------------------
    def handle_ramp(self):
        cmd = Twist()
        if self.ramp_status == 'WAITING':
            cmd.linear.x = 0.3
            if self.current_pitch > 12.0: # Detect uphill incline
                self.ramp_status = 'CLIMBING'
                self.get_logger().info("The robot is climbing the ramp!")
                
        elif self.ramp_status == 'CLIMBING':
            cmd.linear.x = 0.3
            if self.current_pitch < 5.0: # Robot levels out at the top
                self.ramp_status = 'REACHED'
                cmd.linear.x = 0.0
                self.get_logger().info("Top reached! Starting hunt in Zone 4.")
                self.state = 'HUNT_ZONE_4'
                self.ramp_status = 'WAITING' # Reset for the next round
                
        self.cmd_pub.publish(cmd)

    # -----------------------------------------------------------
    # NAV2 UTILITIES
    # -----------------------------------------------------------
    def create_pose(self, x, y, theta):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.pose.position.x = x
        pose.pose.position.y = y
        # Angle conversion (Euler) -> Quaternion for Z axis
        pose.pose.orientation.z = math.sin(theta / 2.0)
        pose.pose.orientation.w = math.cos(theta / 2.0)
        return pose

    def send_nav2_goal(self, pose):
        self.nav_client.wait_for_server()
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose
        send_goal_future = self.nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Nav2 rejected the destination.')
            return
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        # When Nav2 reaches the destination
        self.get_logger().info(f"Destination reached. Transitioning to: {self.next_state}")
        self.state = self.next_state

def main(args=None):
    rclpy.init(args=args)
    node = StrategyFSM()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
