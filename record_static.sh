#!/usr/bin/env bash
# Record a STATIC IMU session for Allan variance analysis.
#
# IMPORTANT: the robot must not move at all during this recording.
# Minimum useful duration: 10 minutes. Ideal: 30+ minutes.
#
# Run this INSIDE the Docker container while oak_imu is running:
#   ros2 run oak_imu oak_imu_cube   # in another shell first
#   ./record_static.sh
#
# Stop: Ctrl-C
# Analyse on PC: python3 analyse_imu.py <bag_dir>

set -e

BAGS_DIR="/eyerobot/bags"
STAMP=$(date +%Y%m%d_%H%M%S)
OUT="${BAGS_DIR}/static_${STAMP}"

mkdir -p "${BAGS_DIR}"

echo "======================================================"
echo "  STATIC IMU RECORDING — do NOT move the robot"
echo "  Minimum: 10 min    Ideal: 30+ min"
echo "  Stop: Ctrl-C"
echo "======================================================"
echo "Output: ${OUT}"
echo ""

ros2 bag record -o "${OUT}" /oak/imu/data_raw

echo ""
echo "Bag saved: ${OUT}"
echo ""
echo "Copy to PC:"
echo "  scp -r eyerobot@<JETSON_IP>:~/CleanTest/EyeRobot/bags/static_${STAMP} ~/bags/"
echo ""
echo "Analyse on PC:"
echo "  python3 analyse_imu.py ~/bags/static_${STAMP}"
