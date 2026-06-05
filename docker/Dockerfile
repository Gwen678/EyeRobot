# ─────────────────────────────────────────────────────────────────────────────
# EyeRobot dev container — ROS 2 Humble + Nav2 + slam_toolbox + Oak-D + RPLidar
# + YOLO perception. Multi-arch: runs on the Jetson Orin Nano (arm64) and on an
# x86 dev machine.
#
# This is a DEV container: the repo is mounted at runtime (see docker/run.sh) and
# you build the workspace inside it with docker/build_ws.sh. Code edits on the
# host show up live; the colcon build/ install/ land in the mounted tree.
#
# NOTE: CPU build of depthai/ultralytics. For CUDA-accelerated YOLO on the Jetson,
# switch the base image to an NVIDIA L4T ROS image (dustynv/ros:humble-*). See
# the README "GPU on Jetson" note.
# ─────────────────────────────────────────────────────────────────────────────
FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# ── Build tooling + ROS deps ─────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
      git wget curl nano \
      python3-pip python3-colcon-common-extensions python3-rosdep python3-vcstool \
      build-essential \
      # USB / serial — Oak-D (USB3) and RPLidar (USB serial)
      libusb-1.0-0 libusb-1.0-0-dev usbutils udev \
      # math / solver libs for slam_toolbox (built from source)
      libceres-dev libgoogle-glog-dev libblas-dev liblapack-dev libsuitesparse-dev \
      libboost-all-dev libtbb-dev \
      # ROS runtime nodes pulled from apt (not built from source)
      ros-humble-nav2-bringup ros-humble-navigation2 \
      ros-humble-rviz2 ros-humble-rviz-default-plugins ros-humble-rviz-imu-plugin \
      ros-humble-robot-state-publisher ros-humble-joint-state-publisher ros-humble-joint-state-publisher-gui \
      ros-humble-xacro \
      ros-humble-cv-bridge ros-humble-image-transport ros-humble-vision-opencv \
      # ex-submodule deps now from apt
      ros-humble-vision-msgs ros-humble-angles \
 && rm -rf /var/lib/apt/lists/*

# ── Python deps not available via rosdep ─────────────────────────────────────
RUN pip3 install --no-cache-dir \
      "numpy==1.26.4" pillow flask \
      "depthai==2.25.1.0" "blobconverter==1.4.3" \
      ultralytics \
      rplidar-roboticia

# rosdep is already initialized in the base image; just update the cache.
RUN rosdep update --rosdistro humble || true

# ── micro-ROS agent (built from source) ──────────────────────────────────────
# There is no `ros-humble-micro-ros-agent` apt package in the ROS 2 repos, so we
# build the agent with micro_ros_setup into /uros_ws. The entrypoint sources this
# overlay, making `ros2 run micro_ros_agent micro_ros_agent serial ...` available.
RUN mkdir -p /uros_ws/src \
 && git clone -b ${ROS_DISTRO} https://github.com/micro-ROS/micro_ros_setup.git \
      /uros_ws/src/micro_ros_setup \
 && source /opt/ros/${ROS_DISTRO}/setup.bash \
 && cd /uros_ws \
 && rosdep install --from-paths src --ignore-src -y \
 && colcon build \
 && source install/local_setup.bash \
 && ros2 run micro_ros_setup create_agent_ws.sh \
 && ros2 run micro_ros_setup build_agent.sh \
 && rm -rf /uros_ws/build /uros_ws/log

# Workspace is mounted here at runtime (docker/run.sh -v REPO:/eyerobot).
ENV EYEROBOT_WS=/eyerobot/ros2_ws
WORKDIR ${EYEROBOT_WS}

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
