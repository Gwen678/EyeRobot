#!/usr/bin/env bash
# Open RViz on your dev PC with the EyeRobot config (URDF RobotModel + the two
# comparison paths: /path_encoder red, /path_imu green, plus /path and TF).
#
# Sources ROS 2 and this repo's workspace, then launches rviz2 -d eyerobot.rviz.
# The RobotModel reads /robot_description over the network, so the odometry +
# URDF stack must be running on the Jetson (e.g. `ros2 launch manual_controller
# manual_controller.launch.py`). The two paths show as soon as dual_odometry
# publishes; the IMU line only diverges once /oak/imu/data_raw has data.
#
# Two things break PC<->Jetson DDS on this setup, both handled by dds_setup.sh:
#   1. campus WiFi blocks the multicast Fast DDS uses for discovery, and
#   2. both machines have docker0 at the SAME 172.17.0.1, so DDS sends data to its
#      own docker bridge and topics echo empty.
# dds_setup.sh writes WiFi-only interface-whitelist profiles (unicast peer + only
# the WiFi NIC) for both ends, which is what makes the topics actually reach RViz.
#
# Usage:
#     ./rviz_eyerobot.sh                  # default Jetson IP below
#     ./rviz_eyerobot.sh 128.179.186.106  # override with the Jetson's current IP
#     JETSON_HOST=foo ./rviz_eyerobot.sh  # or via env
# Note: no `set -u` — ROS's setup.bash references unbound vars (e.g.
# AMENT_TRACE_SETUP_FILES) and would abort under nounset.
set -eo pipefail

# Repo root = this script's directory (so install/setup.bash resolves).
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROS_SETUP="/opt/ros/humble/setup.bash"
WS_SETUP="$REPO/ros2_ws/install/setup.bash"

# Must match the Jetson container (entrypoint.sh defaults): domain 0, Fast DDS.
JETSON_HOST="${JETSON_HOST:-${1:-128.179.186.106}}"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
export ROS_LOCALHOST_ONLY=0

if [ ! -f "$WS_SETUP" ]; then
  echo "ERROR: $WS_SETUP not found. Build the workspace first:" >&2
  echo "  cd $REPO/ros2_ws && source $ROS_SETUP && colcon build && source install/setup.bash" >&2
  exit 1
fi

source "$ROS_SETUP"
source "$WS_SETUP"

# Generate the WiFi-only DDS profiles (PC local + pushed to the Jetson) and use
# the PC one. dds_setup.sh prints the PC profile path on stdout.
DDS_PROFILE="$("$REPO/dds_setup.sh" "$JETSON_HOST")"
export FASTRTPS_DEFAULT_PROFILES_FILE="$DDS_PROFILE"
echo "→ DDS profile: $DDS_PROFILE (domain $ROS_DOMAIN_ID, $RMW_IMPLEMENTATION)"

# Publish the URDF LOCALLY on this PC so the RobotModel always has geometry, even
# though the Jetson's large latched /robot_description does not reliably cross DDS
# over the WiFi. robot_state_publisher expands the local xacro and also emits the
# base_link->wheel link TFs; odom->base_link still comes from the Jetson over /tf
# (small, like the path topics). joint_state_publisher feeds zeroed wheel joints
# so their transforms exist. Both die with RViz via the trap.
XACRO_FILE="$(ros2 pkg prefix robot_description)/share/robot_description/urdf/Robot.xacro"
if [ -f "$XACRO_FILE" ]; then
  # The URDF is multi-line XML; rcl's CLI parser can't take it as a `-p` override
  # (newlines break "parameter override rule" parsing). Hand it to
  # robot_state_publisher via a params file with a YAML literal block scalar
  # instead — every URDF line is indented under the `robot_description: |` key.
  PARAMS_FILE="$(mktemp --suffix=.yaml)"
  {
    echo "robot_state_publisher:"
    echo "  ros__parameters:"
    echo "    robot_description: |"
    xacro "$XACRO_FILE" | sed 's/^/      /'
  } > "$PARAMS_FILE"
  trap 'kill 0; rm -f "$PARAMS_FILE"' EXIT
  ros2 run robot_state_publisher robot_state_publisher \
    --ros-args --params-file "$PARAMS_FILE" &
  ros2 run joint_state_publisher joint_state_publisher &
  echo "→ publishing URDF locally (robot_description built on this PC)"
else
  echo "WARN: robot_description not built on this PC — RobotModel will rely on the" >&2
  echo "      Jetson's /robot_description crossing the network (often won't show)." >&2
fi

# Prefer the installed config; fall back to the source tree if not built here.
RVIZ_CFG="$(ros2 pkg prefix manual_controller 2>/dev/null)/share/manual_controller/rviz/eyerobot.rviz"
[ -f "$RVIZ_CFG" ] || RVIZ_CFG="$REPO/ros2_ws/src/manual_controller/rviz/eyerobot.rviz"

echo "→ rviz2 -d $RVIZ_CFG"
rviz2 -d "$RVIZ_CFG"
