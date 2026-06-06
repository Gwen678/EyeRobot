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
# EPFL WiFi (like most campus/enterprise WiFi) blocks the multicast that Fast DDS
# uses for discovery, so the PC and Jetson never find each other even though they
# can ping. This script forces UNICAST discovery by pointing Fast DDS straight at
# the Jetson's IP, which is what makes the topics actually reach RViz.
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

# Generate a Fast DDS profile that adds the Jetson as a unicast discovery peer.
# (Multicast stays on too — this is additive — so local nodes still discover via
# shared memory, but PDP announcements now also go straight to the Jetson.) Once
# the PC reaches the Jetson by unicast, the Jetson learns the PC's address and
# replies, so setting it on this side alone is enough to complete discovery.
DDS_PROFILE="${TMPDIR:-/tmp}/eyerobot_fastdds_${JETSON_HOST}.xml"
cat > "$DDS_PROFILE" <<XML
<?xml version="1.0" encoding="UTF-8" ?>
<dds xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
  <profiles>
    <participant profile_name="eyerobot_unicast" is_default_profile="true">
      <rtps>
        <builtin>
          <initialPeersList>
            <locator>
              <udpv4>
                <address>${JETSON_HOST}</address>
              </udpv4>
            </locator>
          </initialPeersList>
        </builtin>
      </rtps>
    </participant>
  </profiles>
</dds>
XML
export FASTRTPS_DEFAULT_PROFILES_FILE="$DDS_PROFILE"
echo "→ unicast discovery peer: $JETSON_HOST (domain $ROS_DOMAIN_ID, $RMW_IMPLEMENTATION)"

# Prefer the installed config; fall back to the source tree if not built here.
RVIZ_CFG="$(ros2 pkg prefix manual_controller 2>/dev/null)/share/manual_controller/rviz/eyerobot.rviz"
[ -f "$RVIZ_CFG" ] || RVIZ_CFG="$REPO/ros2_ws/src/manual_controller/rviz/eyerobot.rviz"

echo "→ rviz2 -d $RVIZ_CFG"
exec rviz2 -d "$RVIZ_CFG"
