#!/usr/bin/env bash
# Record a full odometry session for offline review in Foxglove.
#
# Run this INSIDE the Docker container while the stack is running:
#   ./record_run.sh
#
# The bag lands in /eyerobot/bags/ (bind-mounted = EyeRobot/ on the Jetson host)
# so it survives container restarts and can be scp'd to the PC.
#
# Stop recording: Ctrl-C
# Review on PC:   open Foxglove Studio → Open local file → select the .mcap

set -e

BAGS_DIR="/eyerobot/bags"
STAMP=$(date +%Y%m%d_%H%M%S)
OUT="${BAGS_DIR}/run_${STAMP}"

mkdir -p "${BAGS_DIR}"

echo "Recording to: ${OUT}"
echo "Stop with Ctrl-C when done driving."
echo ""

ros2 bag record -o "${OUT}" \
  /odom \
  /odometry/filtered \
  /path \
  /path_encoder \
  /path_imu \
  /ekf_path \
  /pose2d \
  /pose2d_ekf \
  /oak/imu/data_raw \
  /tf \
  /tf_static \
  /robot_description

echo ""
echo "Bag saved: ${OUT}"
echo "On the PC:  scp -r eyerobot@<JETSON_IP>:~/CleanTest/EyeRobot/bags/run_${STAMP} ~/bags/"
