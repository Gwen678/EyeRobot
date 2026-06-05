#!/usr/bin/env bash
# Build the EyeRobot ROS 2 workspace — run this INSIDE the container.
#   ./docker/run.sh        # then, at the container prompt:
#   /eyerobot/docker/build_ws.sh
set -euo pipefail

source "/opt/ros/${ROS_DISTRO}/setup.bash"
cd /eyerobot/ros2_ws

# depthai-ros needs the depthai-core C++ library as a sibling package.
if [ -d src/depthai-ros ] && [ ! -d src/depthai-core ]; then
  echo "→ Fetching depthai-core (required by depthai-ros) ..."
  git clone --branch ros-v3.2.1 --recurse-submodules \
    https://github.com/luxonis/depthai-core.git src/depthai-core
fi

echo "→ Resolving ROS dependencies with rosdep ..."
rosdep install --from-paths src --ignore-src -y --rosdistro "${ROS_DISTRO}" || \
  echo "  (rosdep reported issues — continuing; check the log if the build fails)"

echo "→ colcon build (symlink-install, Release) ..."
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

echo
echo "✓ Built. Source the overlay:"
echo "    source /eyerobot/ros2_ws/install/setup.bash"
