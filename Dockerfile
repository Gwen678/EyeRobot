FROM ros:humble-ros-base

# =========================
# SYSTEM DEPENDENCIES (Mis à jour avec Boost)
# =========================
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-opencv \
    python3-cv-bridge \
    python3-colcon-common-extensions \
    libusb-1.0-0 \
    usbutils \
    build-essential \
    # --- AJOUT DES BIBLIOTHÈQUES C++ BOOST ---
    libboost-all-dev \
    # --- Dépendances Nav2 et SLAM ---
    ros-humble-nav2-map-server \
    ros-humble-nav2-common \
    ros-humble-nav2-msgs \
    # --- Dépendances RViz (Slam_toolbox) ---
    ros-humble-rviz-common \
    ros-humble-rviz-default-plugins \
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

# =========================
# WORKSPACE
# =========================
WORKDIR /ros2_ws

# Copier le workspace propre
COPY ros2_ws /ros2_ws

# =========================
# BUILD ROS2 WORKSPACE
# =========================
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build"

# =========================
# ENTRYPOINT
# =========================
SHELL ["/bin/bash", "-c"]

CMD ["bash"]
