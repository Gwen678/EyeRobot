
FROM ros:humble-base

# =========================
# SYSTEM DEPENDENCIES (Blindé Ceres + SLAM)
# =========================
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-opencv \
    python3-cv-bridge \
    python3-colcon-common-extensions \
    libusb-1.0-0 \
    usbutils \
    build-essential \
    # --- BIBLIOTHÈQUES POUR CERES SOLVER & MATHS ---
    libceres-dev \
    libgoogle-glog-dev \
    libblas-dev \
    liblapack-dev \
    libsuitesparse-dev \
    # --- BIBLIOTHÈQUES DE CALCUL MULTI-THREAD ---
    libboost-all-dev \
    libtbb-dev \
    # --- Dépendances Nav2 et SLAM ---
    ros-humble-nav2-map-server \
    ros-humble-nav2-common \
    ros-humble-nav2-msgs \
    # --- Dépendances RViz (Slam_toolbox) ---
    ros-humble-rviz-common \
    ros-humble-rviz-default-plugins \
    ros-humble-micro-ros-agent \
    ros-humble-rviz2 \
    ros-humble-rviz-default-plugins \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher \
    ros-humble-micro-ros-agent \
    && rm -rf /var/lib/apt/lists/*

# =========================
# PYTHON PACKAGES
# =========================
RUN pip3 install --no-cache-dir \
    numpy==1.26.4 \
    pillow \
    flask \
    depthai==2.25.1.0 \
    blobconverter==1.4.3 \
    ultralytics

WORKDIR /ros2_ws

SHELL ["/bin/bash", "-c"]
CMD ["bash"]
