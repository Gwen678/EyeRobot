#!/usr/bin/env bash

# --- CLEANUP TRAP ---
# If this script is interrupted (Ctrl+C), forcefully kill all background processes
trap 'echo "Stopping autonomous mission..."; kill $(jobs -p) 2>/dev/null; exit' SIGINT SIGTERM

echo "========================================="
echo "   STARTING EYEROBOT AUTONOMOUS STACK   "
echo "========================================="

# 1. Start the micro-ROS Agent (Hardware communication)
echo "[1/3] Launching micro-ROS Agent..."
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/esp32 -b 115200 &
sleep 2

# 2. Launch Core Sensors, Odometry, Hardware Controllers and the Behavior Tree.
# bt:=true starts the autonomous_controller behavior_tree node; it waits for
# the Nav2 action servers (step 3) and then for AMCL localization, so the
# mission does NOT start until you set the initial pose in Foxglove (Set pose).
echo "[2/3] Launching eyerobot core (LiDAR + EKF + behavior tree)..."
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true bt:=true &

# Wait for the IMU chain to be fully up (imu_remap publishes its first message
# only after the camera boots ~40 s and the 400-sample gyro calibration ends).
# Launching Nav2 earlier saturates the Nano's CPU during the depthai driver's
# fragile IMU startup window and the IMU stream never comes up (observed
# 2026-06-11; driver 2.7.x is load-sensitive at init). Keep the robot STILL.
echo "Waiting for IMU calibration (first /oak/imu/data_raw message, up to 90 s)..."
if timeout 90 ros2 topic echo --once /oak/imu/data_raw >/dev/null 2>&1; then
  echo "IMU chain up."
else
  # Hard abort: a mission without the IMU drifts in yaw and nobody notices a
  # warning scrolling past in the launch spam. Fix the IMU, then rerun.
  echo "============================================================"
  echo "  FATAL: no IMU data after 90 s. Aborting the whole stack."
  echo "  (power-cycle the OAK / check imu_remap logs, then rerun)"
  echo "============================================================"
  kill $(jobs -p) 2>/dev/null
  exit 1
fi

# 3. Launch Navigation 2 Stack (AMCL Localization + Global/Local Costmaps)
echo "[3/3] Launching Nav2 Server..."
# clean_room_8x8: GIMP-cleaned map with origin corrected to match the original
# room_8x8 frame (see maps/clean_room_8x8.yaml). full_nav so Nav2 runs the
# planner/controller and publishes /cmd_vel for the BT's navigation goals.
ros2 launch manual_controller nav2.launch.py map:=/eyerobot/ros2_ws/maps/clean_room_8x8.yaml full_nav:=true &
sleep 2

# (No cmd_vel relay needed: diff_drive_controller's subscription is remapped
# to /cmd_vel in manual_controller.launch.py, so Nav2 drives it directly.)

echo "==========================================================="
echo " SYSTEM READY. Set the AMCL initial pose in Foxglove to"
echo " start the mission (the behavior tree is waiting for it)."
echo "==========================================================="

# Keep the whole stack (agent, sensors, BT, Nav2, relay) running until Ctrl+C.
wait