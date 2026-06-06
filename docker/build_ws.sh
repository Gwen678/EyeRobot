#!/usr/bin/env bash
# Build the EyeRobot ROS 2 workspace — run this INSIDE the container.
#   ./docker/run.sh        # then, at the container prompt:
#   /eyerobot/docker/build_ws.sh
set -euo pipefail

# This script runs INSIDE the container. If ROS_DISTRO/ROS aren't present, you're
# almost certainly on the Jetson host (Ubuntu 18.04, no ROS Humble) — bail early
# with a clear message instead of a confusing "/opt/ros//setup.bash" error.
if [ -z "${ROS_DISTRO:-}" ] || [ ! -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]; then
  echo "ERROR: ROS not found — run this INSIDE the container, not on the host." >&2
  echo "  cd <repo> && ./docker/run.sh    # then:  /eyerobot/docker/build_ws.sh" >&2
  exit 1
fi

# ROS 2's setup scripts reference vars (AMENT_TRACE_SETUP_FILES, ...) without
# defaults, so they trip `set -u`. Source them with nounset off, then restore it.
set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"
set -u
cd /eyerobot/ros2_ws

# arm64/Jetson: make vcpkg (depthai-core) use system cmake/ninja or its bootstrap
# fails. Only relevant if you build depthai-ros from source (see below).
export VCPKG_FORCE_SYSTEM_BINARIES=1

# ── Heavy third-party packages: prefer the apt binaries in the image ──────────
# slam_toolbox and depthai-ros are installed from apt in the Dockerfile (prebuilt
# arm64 — fast and reliable). Skip their source submodules so colcon builds only
# the EyeRobot packages. depthai-core is only needed for a SOURCE depthai-ros, so
# it's skipped too (and not cloned). To build one from source instead, export the
# matching flag, e.g.  BUILD_DEPTHAI_FROM_SOURCE=1 ./build_ws.sh
if [ "${BUILD_SLAM_FROM_SOURCE:-0}" != "1" ] && [ -d src/slam_toolbox ]; then
  touch src/slam_toolbox/COLCON_IGNORE
fi
if [ "${BUILD_DEPTHAI_FROM_SOURCE:-0}" != "1" ]; then
  [ -d src/depthai-ros ]  && touch src/depthai-ros/COLCON_IGNORE
  [ -d src/depthai-core ] && touch src/depthai-core/COLCON_IGNORE
else
  # Source depthai-ros needs the depthai-core C++ library as a sibling package.
  rm -f src/depthai-ros/COLCON_IGNORE src/depthai-core/COLCON_IGNORE 2>/dev/null || true
  if [ -d src/depthai-ros ] && [ ! -d src/depthai-core ]; then
    echo "→ Fetching depthai-core (required by source depthai-ros) ..."
    git clone --branch ros-v3.2.1 --recurse-submodules \
      https://github.com/luxonis/depthai-core.git src/depthai-core
  fi
fi

echo "→ Resolving ROS dependencies with rosdep ..."
rosdep install --from-paths src --ignore-src -y --rosdistro "${ROS_DISTRO}" || \
  echo "  (rosdep reported issues — continuing; check the log if the build fails)"

echo "→ colcon build (symlink-install, Release) ..."
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

echo
echo "✓ Built. Source the overlay:"
echo "    source /eyerobot/ros2_ws/install/setup.bash"
