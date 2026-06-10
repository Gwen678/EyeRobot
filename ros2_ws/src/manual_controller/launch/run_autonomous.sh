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

# 2. Launch Core Sensors, Odometry, and Hardware Controllers
echo "[2/4] Launching eyerobot core (LiDAR + EKF)..."
# NOTE: If your colleague has flags to disable foxglove/paths, add them here
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true &

echo "Waiting 3 seconds for IMU calibration window..."
sleep 3

# 3. Launch Navigation 2 Stack (AMCL Localization + Global/Local Costmaps)
echo "[3/4] Launching Nav2 Server..."
ros2 launch manual_controller nav2.launch.py map:=/eyerobot/ros2_ws/maps/room_8x8.yaml full_nav:=true &
sleep 2

# 4. Bridge the Nav2 velocity commands to the hardware controller
echo "[4/4] Bridging velocity command topics..."
ros2 run topic_tools relay /cmd_vel /diff_drive_controller/cmd_vel_unstamped &
sleep 2

echo "========================================="
echo " SYSTEM READY. Launching Behavior Tree... "
echo "========================================="

# 5. Execute your Behavior Tree Engine in the foreground
echo "========================================="
echo "  [WAITING] Stack initialization complete."
echo "  Press [ENTER] when ready to start the autonomous mission."
echo "========================================="
read -p ""
python3 /eyerobot/ros2_ws/src/autonomous_controller/BehavioralTree.py

# If the behavior tree finishes naturally, trigger the trap to clean up the backend
kill $(jobs -p) 2>/dev/null