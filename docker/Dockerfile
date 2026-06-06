# ─────────────────────────────────────────────────────────────────────────────
# EyeRobot dev container — Ubuntu 22.04 / ROS 2 Humble + Nav2 + slam_toolbox +
# Oak-D + RPLidar + micro-ROS agent + YOLO perception.
#
# This is a DEV container: the repo is mounted at runtime (see docker/run.sh) and
# you build the workspace inside it with docker/build_ws.sh. Code edits on the
# host show up live; the colcon build/ install/ land in the mounted tree.
#
# BASE_IMAGE selects the platform:
#   • Default `ros:humble-ros-base` — Ubuntu 22.04, builds anywhere (x86 or as a
#     container on any Jetson). All ROS packages come from apt. Perception runs on
#     CPU torch unless the base provides a GPU torch.
#   • GPU on the Jetson requires JetPack 6 (L4T r36 = Ubuntu 22.04). Point
#     BASE_IMAGE at a matching Dusty-NV 22.04 image to get a Jetson-built CUDA
#     PyTorch, while still apt-installing the ROS packages below:
#       cat /etc/nv_tegra_release    # "R36 ... REVISION: x.y" -> r36.x.y
#       ./docker/build.sh --build-arg BASE_IMAGE=dustynv/ros:humble-desktop-l4t-r36.2.0
#     (JetPack 5 / L4T r35 is Ubuntu 20.04 and canNOT do 22.04 + apt-ROS + GPU
#      together — upgrade to JetPack 6 for the GPU-on-Jetson path.)
# ─────────────────────────────────────────────────────────────────────────────
ARG BASE_IMAGE=ros:humble-ros-base
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# ── Build tooling + ROS deps (apt works natively on Ubuntu 22.04) ────────────
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
      ros-humble-vision-msgs ros-humble-angles \
 && rm -rf /var/lib/apt/lists/*

# ── Python deps not available via rosdep ─────────────────────────────────────
# Core deps for the camera/IMU + lidar + web viewers. These are light.
RUN pip3 install --no-cache-dir \
      "numpy==1.26.4" pillow flask \
      "depthai==2.25.1.0" "blobconverter==1.4.3" \
      rplidar-roboticia

# Perception (YOLO). ON by default. Adaptive torch:
#   • Target = Jetson Nano (aarch64): plain `pip install torch` gives a CPU-only
#     wheel from PyPI. The multi-GB nvidia-cuda-* wheels that previously hung the
#     build are x86_64-only, so they are never pulled here — CPU inference only
#     (the Nano's GPU is unreachable from a 22.04 container on JetPack 4).
#   • If the base image already ships torch (e.g. a GPU dustynv base), keep it;
#     ultralytics is installed with --no-deps so pip never replaces it.
# Disable with: WITH_PERCEPTION=0 in docker/build.sh.
ARG WITH_PERCEPTION=1
RUN if [ "${WITH_PERCEPTION}" = "1" ]; then \
      if python3 -c "import torch" 2>/dev/null; then \
        echo "torch present in base (likely GPU): $(python3 -c 'import torch; print(torch.__version__, "cuda", torch.cuda.is_available())')" ; \
        echo "Installing ultralytics --no-deps so pip won't replace that torch, plus its runtime deps." ; \
        pip3 install --no-cache-dir --no-deps ultralytics ultralytics-thop \
        && pip3 install --no-cache-dir \
             opencv-python polars pillow pyyaml tqdm psutil py-cpuinfo \
             pandas requests matplotlib scipy ; \
      else \
        echo "No torch in base — installing CPU torch (aarch64 wheels) + ultralytics with full deps." ; \
        pip3 install --no-cache-dir torch torchvision \
        && pip3 install --no-cache-dir ultralytics ; \
      fi ; \
    else \
      echo "Skipping perception (torch/ultralytics). Set WITH_PERCEPTION=1 to include it." ; \
    fi

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
 && apt-get update \
 && rosdep install --from-paths src --ignore-src -y --skip-keys "clang-tidy" \
 && colcon build \
 && source install/local_setup.bash \
 && ros2 run micro_ros_setup create_agent_ws.sh \
 && ros2 run micro_ros_setup build_agent.sh \
 && rm -rf /uros_ws/build /uros_ws/log /var/lib/apt/lists/*

# Workspace is mounted here at runtime (docker/run.sh -v REPO:/eyerobot).
ENV EYEROBOT_WS=/eyerobot/ros2_ws
WORKDIR ${EYEROBOT_WS}

# Auto-source ROS + the micro-ROS agent + the (mounted) workspace overlay in
# interactive shells. The ENTRYPOINT covers `docker run`, but `docker exec` shells
# (run.sh's shell and attach.sh) bypass it — so source from .bashrc too. The
# workspace overlay only exists after build_ws.sh, hence the guards.
RUN { \
      echo "source /opt/ros/${ROS_DISTRO}/setup.bash"; \
      echo '[ -f /uros_ws/install/local_setup.bash ] && source /uros_ws/install/local_setup.bash'; \
      echo "[ -f ${EYEROBOT_WS}/install/setup.bash ] && source ${EYEROBOT_WS}/install/setup.bash"; \
    } >> /root/.bashrc

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
