#!/usr/bin/env bash

# --- CLEANUP TRAP ---
# If this script is interrupted (Ctrl+C), forcefully kill all background processes
trap 'echo "Stopping autonomous mission..."; kill $(jobs -p) 2>/dev/null; exit' SIGINT SIGTERM

echo "========================================="
echo "   STARTING EYEROBOT AUTONOMOUS STACK   "
echo "========================================="

# 1. Start the micro-ROS Agent (Hardware communication)
echo "[1/4] Launching micro-ROS Agent..."
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/esp32 -b 115200 &
sleep 2

# 2. Launch Core Sensors, Odometry, Hardware Controllers and the Behavior Tree.
# bt:=true starts the autonomous_controller behavior_tree node; it waits for
# the Nav2 action servers (step 3) and then for AMCL localization, so the
# mission does NOT start until you set the initial pose in Foxglove (Set pose).
echo "[2/4] Launching eyerobot core (LiDAR + EKF + behavior tree)..."
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true bt:=true &

echo "Waiting 3 seconds for IMU calibration window..."
sleep 3

# 3. Launch Navigation 2 Stack (AMCL Localization + Global/Local Costmaps)
echo "[3/4] Launching Nav2 Server..."
# clean_room_8x8: GIMP-cleaned map with origin corrected to match the original
# room_8x8 frame (see maps/clean_room_8x8.yaml). full_nav so Nav2 runs the
# planner/controller and publishes /cmd_vel for the BT's navigation goals.
ros2 launch manual_controller nav2.launch.py map:=/eyerobot/ros2_ws/maps/clean_room_8x8.yaml full_nav:=true &
sleep 2

# 4. Bridge the Nav2 velocity commands to the hardware controller
echo "[4/4] Bridging velocity command topics..."
ros2 run topic_tools relay /cmd_vel /diff_drive_controller/cmd_vel_unstamped &
sleep 2

echo "==========================================================="
echo " SYSTEM READY. Set the AMCL initial pose in Foxglove to"
echo " start the mission (the behavior tree is waiting for it)."
echo "==========================================================="

# Keep the whole stack (agent, sensors, BT, Nav2, relay) running until Ctrl+C.
wait