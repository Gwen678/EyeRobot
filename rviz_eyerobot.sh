#!/usr/bin/env bash
# rviz_eyerobot.sh — RUN THIS ON YOUR PC. Opens RViz with the EyeRobot odometry
# comparison config (eyerobot.rviz): the RobotModel plus /path, /path_encoder,
# /path_imu (and /ekf_path if the EKF is running). The odometry stack itself runs
# on the Jetson — this only visualises its topics on the PC, which the Jetson
# Nano can't render itself.
#
# It does three things plain `rviz2` won't, all required for the topics to show:
#   1. Sources ROS 2 + this repo's PC-native workspace build.
#   2. Sets a PC-side Fast DDS profile (via dds_setup.sh) so the Jetson's topics
#      actually reach this PC. Two problems fixed:
#        - docker0 collision: both machines have docker0 at 172.17.0.1; DDS routes
#          data to its own bridge and packets vanish.  Fixed by restricting DDS to
#          the WiFi interface only (excludes docker0 as a locator on both sides).
#        - Campus WiFi blocks DDS multicast; fixed with unicast initial peers.
#      The Jetson side (dds_jetson.xml) is always-on in every container shell via
#      dds_env.sh.  This script only generates the PC-side profile dynamically
#      (current PC IP + Jetson peer) — no SSH push to the Jetson needed.
#   3. Publishes the URDF LOCALLY (robot_state_publisher + joint_state_publisher).
#      The Jetson's large latched /robot_description does not reliably cross the
#      WiFi, so the RobotModel needs a local source. The small odom->base_link TF
#      and the /path_* topics cross fine on their own.
#
# Prereq — build the workspace on this PC once (the Jetson's build is ARM):
#   cd ros2_ws && colcon build --packages-select robot_description manual_controller
#
# Usage:
#   ./rviz_eyerobot.sh                  # default Jetson IP below
#   ./rviz_eyerobot.sh 128.179.186.106  # override with the Jetson's current IP
#   JETSON_HOST=foo ./rviz_eyerobot.sh  # or via env
#
# No `set -u`: ROS's setup.bash references unbound vars and aborts under nounset.
set -eo pipefail

# Repo root = this script's directory.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROS_SETUP="/opt/ros/humble/setup.bash"
WS_SETUP="$REPO/ros2_ws/install/setup.bash"

# Must match the Jetson container's ROS env (domain 0, Fast DDS, networked).
JETSON_HOST="${JETSON_HOST:-${1:-128.179.186.106}}"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
export ROS_LOCALHOST_ONLY=0

if [ ! -f "$WS_SETUP" ]; then
  echo "ERROR: $WS_SETUP not found — build the PC-native workspace first:" >&2
  echo "  cd $REPO/ros2_ws && source $ROS_SETUP && \\" >&2
  echo "    colcon build --packages-select robot_description manual_controller && \\" >&2
  echo "    source install/setup.bash" >&2
  exit 1
fi

source "$ROS_SETUP"
source "$WS_SETUP"

# ── DDS: generate PC-side profile and activate it ─────────────────────────────
# dds_setup.sh generates the PC profile (WiFi interface + Jetson unicast peer)
# and prints the path on stdout.  The Jetson profile is static (dds_jetson.xml,
# always-on via dds_env.sh in the container) — no SSH push required.
if [ -x "$REPO/dds_setup.sh" ]; then
  DDS_PROFILE="$("$REPO/dds_setup.sh" "$JETSON_HOST")"
  export FASTRTPS_DEFAULT_PROFILES_FILE="$DDS_PROFILE"
  echo "→ DDS profile: $DDS_PROFILE (domain $ROS_DOMAIN_ID, $RMW_IMPLEMENTATION)"
else
  echo "WARN: dds_setup.sh not found/executable — if RViz stays empty, that's the" >&2
  echo "      PC<->Jetson DDS crossing (docker0 collision + WiFi multicast)." >&2
fi

# ── Publish the URDF locally so the RobotModel always has geometry ────────────
# The CLI -p override can't take the multi-line URDF (newlines break the parser),
# so hand it to robot_state_publisher via a params file with a YAML literal block.
# robot_state_publisher also emits base_link->wheel TFs; odom->base_link still
# comes from the Jetson over /tf. joint_state_publisher zeroes the wheel joints so
# their transforms exist. Both are reaped with RViz by the EXIT trap.
XACRO_FILE="$(ros2 pkg prefix robot_description 2>/dev/null)/share/robot_description/urdf/Robot.xacro"
if [ -f "$XACRO_FILE" ]; then
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
  trap 'kill 0' EXIT
  echo "WARN: robot_description not built on this PC — RobotModel will rely on the" >&2
  echo "      Jetson's /robot_description crossing the network (often won't show)." >&2
fi

# ── RViz ─────────────────────────────────────────────────────────────────────
# Prefer the installed config; fall back to the source tree.
RVIZ_CFG="$(ros2 pkg prefix manual_controller 2>/dev/null)/share/manual_controller/rviz/eyerobot.rviz"
[ -f "$RVIZ_CFG" ] || RVIZ_CFG="$REPO/ros2_ws/src/manual_controller/rviz/eyerobot.rviz"

echo "→ rviz2 -d $RVIZ_CFG"
rviz2 -d "$RVIZ_CFG"
