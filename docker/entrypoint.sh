#!/usr/bin/env bash
# Container entrypoint: source ROS 2 + the EyeRobot overlay (if built), then exec
# whatever command was given (defaults to an interactive bash in the workspace).
set -e

source "/opt/ros/${ROS_DISTRO}/setup.bash"

# Source the workspace overlay if it has been built (docker/build_ws.sh).
if [ -f "${EYEROBOT_WS}/install/setup.bash" ]; then
  source "${EYEROBOT_WS}/install/setup.bash"
fi

# Sensible defaults for a single-robot DDS setup; override with -e at run time.
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"

cd "${EYEROBOT_WS}" 2>/dev/null || true
exec "$@"
