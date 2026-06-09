# ─────────────────────────────────────────────────────────────────────────────
# EyeRobot dev container — Ubuntu 22.04 / ROS 2 Humble.
#
# ROS packages come from apt (nav2, slam_toolbox, rviz, … are all in the apt repo
# — verified). The micro-ROS agent is NOT in the standard apt repo (the team's
# original image only got it via a custom base with the micro-ROS repo added), so
# it's built from source below.
#
# The repo is bind-mounted at /eyerobot (docker/run.sh), so host edits are live
# and colcon build/ install/ land back in the tree.
# ─────────────────────────────────────────────────────────────────────────────
ARG BASE_IMAGE=ros:humble-ros-base
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# ── System + ROS deps (all from apt — works natively on Ubuntu 22.04) ────────
RUN apt-get update && apt-get install -y --no-install-recommends \
      git wget curl nano \
      python3-pip python3-colcon-common-extensions python3-rosdep python3-vcstool \
      python3-opencv python3-cv-bridge \
      build-essential \
      # USB / serial — Oak-D (USB3) and RPLidar (USB serial)
      libusb-1.0-0 libusb-1.0-0-dev usbutils udev \
      # math / solver libs (Ceres etc.) for slam_toolbox
      libceres-dev libgoogle-glog-dev libblas-dev liblapack-dev libsuitesparse-dev \
      libboost-all-dev libtbb-dev \
      # Nav2 + SLAM + state-estimation EKF (wheel odom + IMU fusion)
      ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-slam-toolbox \
      ros-humble-robot-localization \
      # ros2_control — controller manager + diff_drive_controller
      ros-humble-ros2-control ros-humble-ros2-controllers \
      # OAK-D camera ROS driver (apt — no vcpkg/source build) + IMU orientation filter
      ros-humble-depthai-ros ros-humble-imu-filter-madgwick \
      # RPLidar driver (ROS Index: rplidar_ros)
      ros-humble-rplidar-ros \
      # RViz + robot model
      ros-humble-rviz2 ros-humble-rviz-common ros-humble-rviz-default-plugins \
      ros-humble-rviz-imu-plugin \
      ros-humble-robot-state-publisher ros-humble-joint-state-publisher ros-humble-joint-state-publisher-gui \
      ros-humble-xacro \
      # vision / message deps used by the workspace packages
      ros-humble-image-transport ros-humble-vision-opencv \
      ros-humble-vision-msgs ros-humble-angles \
      # Foxglove bridge — WebSocket server so Foxglove Studio on the PC can
      # subscribe to all topics without any DDS crossing (SSH tunnel port 8765).
      ros-humble-foxglove-bridge \
 && rm -rf /var/lib/apt/lists/*

# ── Python deps (proven set) ─────────────────────────────────────────────────
# On the Jetson (arm64) torch/ultralytics resolve to CPU-only wheels — no NVIDIA
# CUDA wheel stack is pulled (that's x86-only), so this stays light. Set
# WITH_PERCEPTION=0 for an odometry-only image.
ARG WITH_PERCEPTION=1
RUN pip3 install --no-cache-dir \
      numpy==1.26.4 pillow flask \
      depthai==2.25.1.0 blobconverter==1.4.3 \
 && if [ "${WITH_PERCEPTION}" = "1" ]; then \
      pip3 install --no-cache-dir ultralytics ; \
    else \
      echo "Skipping perception (ultralytics). Set WITH_PERCEPTION=1 to include it." ; \
    fi

# ── micro-ROS agent (built from source) ──────────────────────────────────────
# Not in the standard apt repo, so build it with micro_ros_setup into /uros_ws.
# The agent's own rosdep pulls clang-tidy as a lint dep — skip it; the agent
# builds fine without it. apt lists are restored for this layer then cleaned.
RUN mkdir -p /uros_ws/src \
 && git clone -b ${ROS_DISTRO} https://github.com/micro-ROS/micro_ros_setup.git \
      /uros_ws/src/micro_ros_setup \
 && source /opt/ros/${ROS_DISTRO}/setup.bash \
 && cd /uros_ws \
 && apt-get update \
 && rosdep install --from-paths src --ignore-src -y --skip-keys "clang-tidy" \
 && colcon build \
 && source install/local_setup.bash \
 && ros2 run micro_ros_setup create_agent_ws.sh \
 && ros2 run micro_ros_setup build_agent.sh \
 && rm -rf /uros_ws/build /uros_ws/log /var/lib/apt/lists/*

# ── Workspace + shell setup ──────────────────────────────────────────────────
# Repo is mounted here at runtime (docker/run.sh -v REPO:/eyerobot).
ENV EYEROBOT_WS=/eyerobot/ros2_ws
WORKDIR ${EYEROBOT_WS}

# Auto-source ROS + the agent overlay + the (mounted) workspace overlay for EVERY
# shell and user. The ENTRYPOINT only covers `docker run`; `docker exec` shells
# bypass it. Writing to a single profile.d script that BOTH /etc/bash.bashrc
# (interactive non-login) and /etc/profile (login shells) source means it works
# no matter how anyone connects — not just root via .bashrc. The workspace overlay
# only exists after build_ws.sh, hence the guard.
RUN { \
      echo "source /opt/ros/${ROS_DISTRO}/setup.bash"; \
      echo "[ -f /uros_ws/install/local_setup.bash ] && source /uros_ws/install/local_setup.bash"; \
      echo "[ -f ${EYEROBOT_WS}/install/setup.bash ] && source ${EYEROBOT_WS}/install/setup.bash"; \
      echo "[ -f /eyerobot/dds_env.sh ] && source /eyerobot/dds_env.sh"; \
    } > /etc/profile.d/eyerobot_ros.sh \
 && echo "source /etc/profile.d/eyerobot_ros.sh" >> /etc/bash.bashrc

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
