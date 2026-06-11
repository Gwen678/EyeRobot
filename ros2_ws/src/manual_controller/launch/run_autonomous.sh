#!/usr/bin/env bash

# --- CLEANUP ---
# Ordered shutdown. The old one-liner TERMed the ros2 launch processes the
# instant Ctrl+C arrived — killing them MID graceful shutdown, which orphans
# their component containers and leaves the OAK with an open XLink session
# (wedged camera / "IMU hung" on the next run) and stray micro-ROS agents.
# Correct order: SIGINT, then WAIT for the launches to stop their nodes,
# escalate only if they hang, sweep known stragglers at the end.
cleanup() {
  trap - SIGINT SIGTERM
  echo ""
  echo "Stopping autonomous mission (waiting for clean shutdown)..."
  kill -INT $(jobs -p) 2>/dev/null
  deadline=$((SECONDS + 15))
  while [ ${SECONDS} -lt ${deadline} ] && [ -n "$(jobs -rp)" ]; do
    sleep 1
  done
  if [ -n "$(jobs -rp)" ]; then
    echo "Some processes did not stop in 15 s — escalating..."
    kill -TERM $(jobs -rp) 2>/dev/null
    sleep 3
    kill -KILL $(jobs -rp) 2>/dev/null
  fi
  # Sweep processes that detached from our job table (the ros2 run wrapper
  # does not always forward signals to the agent binary).
  pkill -f micro_ros_agent 2>/dev/null
  echo "All stopped."
  exit "${1:-0}"
}
trap cleanup SIGINT SIGTERM

echo "========================================="
echo "   STARTING EYEROBOT AUTONOMOUS STACK   "
echo "========================================="

# Pre-flight: refuse to start on top of a stale stack. A previous session that
# died without Ctrl+C (SSH drop, killed terminal) leaves its nodes running —
# a zombie AMCL with old params publishes map->odom and silently bypasses the
# wait-for-initial-pose gate; a zombie oak driver blocks the camera (exclusive
# USB access); duplicate controllers fight over the motors.
# The micro-ROS agent is not a ROS graph node (it's a serial bridge), so check
# for it by process: a zombie agent holding /dev/esp32 makes the new one loop
# on connect/disconnect forever.
if pgrep -f micro_ros_agent >/dev/null 2>&1; then
  echo "FATAL: a micro_ros_agent is already running (stale session?)."
  echo "  pkill -f micro_ros_agent   — then rerun this script."
  exit 1
fi

# OAK IMU probe: the BMI270 occasionally fails to enumerate at device boot
# (known flaky init on this chip) and the only cure is a camera power-cycle.
# Catch it here in ~5 s instead of waiting for the 90 s IMU timeout below.
# Side benefit: opening/closing the device makes the OAK reboot its firmware,
# so this doubles as a warm reset before the driver attaches.
echo "Probing OAK IMU..."
IMU_TYPE=$(python3 -c "import depthai as dai; d = dai.Device(); print(d.getConnectedIMU())" 2>/dev/null | tail -1)
if [ -z "${IMU_TYPE}" ] || [ "${IMU_TYPE}" = "NONE" ]; then
  echo "============================================================"
  echo "  FATAL: OAK probe failed (returned '${IMU_TYPE}')."
  echo "  Either the IMU did not enumerate, the camera is wedged from"
  echo "  an abruptly killed session, or another process owns it"
  echo "  (detect_lego.py / block_tracker use the OAK directly)."
  echo "  Fix: close other camera scripts; unplug the camera USB,"
  echo "  wait 5 s, replug; rerun this script."
  echo "============================================================"
  exit 1
fi
echo "OAK IMU: ${IMU_TYPE}"

STALE=$(ros2 node list 2>/dev/null | grep -E "amcl|bt_navigator|controller_manager|^/oak$" | sort -u)
if [ -n "${STALE}" ]; then
  echo "============================================================"
  echo "  FATAL: nodes from a previous session are still running:"
  echo "${STALE}"
  echo "  Clean up first (safest: docker restart eyerobot on the"
  echo "  Jetson host), then rerun this script."
  echo "============================================================"
  exit 1
fi

# Clear stale Fast DDS shared-memory segments (left behind by killed sessions;
# cause "Failed init_port fastrtps_portXXXX: open_and_lock_file failed").
# Safe at this point: the checks above guarantee no ROS processes are running.
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null
ros2 daemon stop >/dev/null 2>&1   # daemon caches transports; restarts lazily

# Pre-compile the vision nodes: a node that crashes mid-run on import/syntax
# errors (numpy ABI mismatch, missing dep after a pip update) wedges the OAK
# USB session and looks like an IMU failure on the next run. Catch it in <2 s.
VISION_DIR=/eyerobot/ros2_ws/src/manual_controller/manual_controller
echo "Pre-checking vision nodes..."
if ! python3 -m py_compile "${VISION_DIR}/lego_vision_node.py" \
                           "${VISION_DIR}/yolo_vision_node.py" \
                           "${VISION_DIR}/nn_config.py" 2>&1; then
  echo "FATAL: a vision node has a syntax error — fix it before running."
  exit 1
fi
if ! python3 -c "
import sys
sys.path.insert(0, '/eyerobot/ros2_ws/install/manual_controller/lib/python3.10/site-packages')
import cv2, numpy, depthai
from cv_bridge import CvBridge
from tf2_ros import Buffer
from vision_msgs.msg import Detection3DArray
print('vision node imports OK')
" 2>&1; then
  echo "FATAL: vision node import check failed (see above). Fix the dep, then rerun."
  exit 1
fi

# 1. Start the micro-ROS Agent (Hardware communication)
echo "[1/3] Launching micro-ROS Agent..."
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/esp32 -b 115200 &
sleep 2

# Mission: 'loop' (default) = endless search/collect/unload cycle.
#   ./run_autonomous.sh test_center   -> Nav2 smoke test (one goal, arena center)
MISSION="${1:-loop}"

# 2. Launch Core Sensors, Odometry, Hardware Controllers and the Behavior Tree.
# Everything hardcoded ON: lidar + EKF + onboard-YOLO vision + BT. No SLAM —
# Nav2 (step 3) localizes against the saved map. bt:=true starts the behavior
# tree; it waits for the Nav2 action servers and AMCL localization, and AMCL
# self-initializes at the base pose (nav2_params.yaml set_initial_pose), so
# the mission starts on its own — place the robot at the base marker.
# detector defaults to yolo: the OAK runs the block model on its own VPU and
# yolo_vision_node feeds /eyerobot/vision/lego_markers_map for BlockMemory.
echo "[2/3] Launching eyerobot core (LiDAR + EKF + YOLO vision + behavior tree, mission: ${MISSION})..."
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true lego:=true bt:=true bt_mission:="${MISSION}" &

# Wait for the IMU chain to be fully up (imu_remap publishes its first message
# only after the camera boots ~40 s and the 400-sample gyro calibration ends).
# Launching Nav2 earlier saturates the Nano's CPU during the depthai driver's
# fragile IMU startup window and the IMU stream never comes up (observed
# 2026-06-11; driver 2.7.x is load-sensitive at init). Keep the robot STILL.
# The explicit message type matters: without it `ros2 topic echo` tries to
# infer the type from a live publisher and exits non-zero immediately when
# imu_remap hasn't started yet, instead of waiting.
echo "Waiting for IMU calibration (first /oak/imu/data_raw message, up to 90 s)..."
if timeout 90 ros2 topic echo --once /oak/imu/data_raw sensor_msgs/msg/Imu >/dev/null 2>&1; then
  echo "IMU chain up."
else
  # Hard abort: a mission without the IMU drifts in yaw and nobody notices a
  # warning scrolling past in the launch spam. Fix the IMU, then rerun.
  echo "============================================================"
  echo "  FATAL: no IMU data after 90 s. Aborting the whole stack."
  echo "  (power-cycle the OAK / check imu_remap logs, then rerun)"
  echo "============================================================"
  cleanup 1   # ordered shutdown — same path as Ctrl+C (exits for us)
fi

# 2b. Readiness gates BEFORE Nav2: each intermittent-boot failure mode gets
# a named wait + hard abort, so "sometimes it works" becomes "it either
# works or tells you exactly which link of the chain died this boot".

echo "Waiting for wheel odometry (/diff_drive_controller/odom, up to 30 s)..."
if ! timeout 30 ros2 topic echo --once /diff_drive_controller/odom nav_msgs/msg/Odometry >/dev/null 2>&1; then
  echo "============================================================"
  echo "  FATAL: no wheel odometry after 30 s."
  echo "  Chain: micro-ROS agent <-> ESP32 <-> controller_manager."
  echo "  Check the agent log (connect/disconnect loop = replug ESP32)."
  echo "============================================================"
  cleanup 1
fi
echo "Wheel odometry up."

echo "Waiting for lidar (/scan, up to 30 s)..."
if ! timeout 30 ros2 topic echo --once /scan sensor_msgs/msg/LaserScan >/dev/null 2>&1; then
  echo "============================================================"
  echo "  FATAL: no /scan after 30 s. RPLidar did not come up"
  echo "  (check /dev/rplidar + the rplidar node log), AMCL would"
  echo "  never localize. Aborting."
  echo "============================================================"
  cleanup 1
fi
echo "Lidar up."

# Camera mount TF: published by imu_remap after gravity calibration + the
# driver's URDF extrinsic. Without it EVERY map-frame detection is dropped
# and the BT searches in circles forever — refuse to proceed blind.
echo "Waiting for the camera mount TF (base_link -> oak_mount, up to 45 s)..."
if ! timeout 45 python3 -c "
import rclpy, rclpy.time
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
import time, sys
rclpy.init()
n = Node('mount_tf_probe')
buf = Buffer(); TransformListener(buf, n)
deadline = time.time() + 44
while time.time() < deadline:
    rclpy.spin_once(n, timeout_sec=0.2)
    if buf.can_transform('base_link', 'oak_mount', rclpy.time.Time()):
        sys.exit(0)
sys.exit(1)
" >/dev/null 2>&1; then
  echo "============================================================"
  echo "  FATAL: camera mount TF never published. The imu_remap log"
  echo "  says why ('camera mount TF pending: <reason>'):"
  echo "    - gravity calibration unfinished -> robot/fans moved"
  echo "    - driver extrinsic missing      -> camera TF chain issue"
  echo "  Vision cannot project to the map without it. Aborting."
  echo "============================================================"
  cleanup 1
fi
echo "Camera mount TF up — vision chain complete."

# 3. Launch Navigation 2 Stack (AMCL Localization + Global/Local Costmaps)
echo "[3/3] Launching Nav2 Server..."
# clean_room_8x8: GIMP-cleaned map with origin corrected to match the original
# room_8x8 frame (see maps/clean_room_8x8.yaml). full_nav so Nav2 runs the
# planner/controller and publishes /cmd_vel for the BT's navigation goals.
ros2 launch manual_controller nav2.launch.py map:=/eyerobot/ros2_ws/maps/clean_room_8x8.yaml full_nav:=true &
sleep 2

# 3b. Nav2 readiness: AMCL must produce the map frame (it self-initializes
# from the yaml pose). A boot where this fails = lifecycle activation died
# (bond timeout under load) — restarting Nav2 alone usually cures it.
echo "Waiting for localization (map -> base_link TF, up to 90 s)..."
if ! timeout 90 python3 -c "
import rclpy, rclpy.time
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
import time, sys
rclpy.init()
n = Node('map_tf_probe')
buf = Buffer(); TransformListener(buf, n)
deadline = time.time() + 89
while time.time() < deadline:
    rclpy.spin_once(n, timeout_sec=0.2)
    if buf.can_transform('map', 'base_link', rclpy.time.Time()):
        sys.exit(0)
sys.exit(1)
" >/dev/null 2>&1; then
  echo "============================================================"
  echo "  FATAL: no map -> base_link TF after 90 s: AMCL/map_server"
  echo "  never activated (lifecycle bond death under load?)."
  echo "  Check: ros2 node list | grep -E 'amcl|map_server'"
  echo "============================================================"
  cleanup 1
fi
echo "Localization up. Mission starts on its own."

# (No cmd_vel relay needed: diff_drive_controller's subscription is remapped
# to /cmd_vel in manual_controller.launch.py, so Nav2 drives it directly.)

echo "==========================================================="
echo " SYSTEM READY. AMCL self-initializes at the base pose —"
echo " with the robot at the base marker the mission starts on"
echo " its own once Nav2 is active. (Robot elsewhere? Foxglove"
echo " Set-pose to relocalize.)"
echo "==========================================================="

# Keep the whole stack (agent, sensors, BT, Nav2, relay) running until Ctrl+C.
wait