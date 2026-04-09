@ -0,0 +1,127 @@
# EyeRobot Project, ROS 2 Deployment

This repository provides a standardized, Docker-based development environment for the **NVIDIA Jetson Nano**. It simplifies the deployment of **RPLidar A1/A2** sensors and integrates **Rosbridge** for high-performance remote telemetry and visualization.

---

## 1. System Specifications
To ensure full hardware acceleration (GPU) and sensor access, your system must meet these requirements:
* **Hardware:** NVIDIA Jetson Nano (4GB or 2GB Developer Kit).
* **OS:** Linux for Tegra (L4T) R32.7.1 (Standard for Jetson Nano).
* **LiDAR:** RPLidar A1/A2 connected via USB.
* **Visualization:** Foxglove Studio installed on a remote PC (Windows/Linux/Mac).

---

## 🛠 2. Initial Setup & Installation

Follow these steps once to configure your host Jetson Nano.

### A. Host Configuration
Run these commands to install Docker and the NVIDIA Container Runtime (to allow Docker to use the Jetson GPU):
```bash
# Update and install Docker
sudo apt-get update && sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

> **Note:** Logout and log back in to apply the `usermod` group changes.

### B. Project Setup
Clone the repository and build the container:

```bash
git clone https://github.com/Gwen678/EyeRobot.git
cd EyeRobot

# Build the Docker image (Name: eyerobot)
sudo docker build -t eyerobot .
```

### C. The `eyerun` Shortcut (Alias)
To avoid typing long Docker commands, create this shortcut in your `.bashrc`:

```bash
echo "alias eyerun='sudo docker run -it --rm --runtime nvidia --network host --privileged -v /dev:/dev eyerobot'" >> ~/.bashrc
source ~/.bashrc
```

---

## 3. Execution Workflow

### Step 1: Start the Environment
Simply open a terminal on your Jetson and type:

```bash
eyerun
```

### Step 2: Launch the LiDAR Driver
Inside the session opened by `eyerun` (ROS 2 is automatically sourced):

```bash
# For RPLidar A1:
ros2 launch rplidar_ros2 rplidar_a1_launch.py

```

### Step 3: Launch Telemetry Bridge
Open a second terminal and join the running container to start the bridge:

```bash
# Join the active 'eyerobot' session automatically
docker exec -it $(docker ps -qf "ancestor=eyerobot") bash

# Launch the WebSocket server for Foxglove
ros2 launch rosbridge_server rosbridge_websocket_launch.xml address:=0.0.0.0
```

---

## 4. Remote Visualization (Foxglove Studio)
1. Open Foxglove Studio on your laptop.
2. Click **Open Connection** and choose **Rosbridge**.
3. **URL:** `ws://<JETSON_IP>:9090` (Get your IP by typing `hostname -I` on the Jetson).
4. **Configuration:**
   * Add a **3D Panel**.
   * Set **Fixed Frame** to `laser`.
   * Add the Topic `/scan`.

---

## 🔄 5. Developer & Collaboration Workflow

### Sharing your work
If you modify files in the `src/` folder:

```bash
git add .
git commit -m "feat: updated lidar launch parameters"
git push origin main
```

### Getting updates from the team
```bash
git pull origin main
# Always rebuild the image if the source code changed
sudo docker build -t eyerobot .
```

---

## 6. Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Lidar not spinning** | Check USB connection and run `sudo chmod 666 /dev/ttyUSB0` on the host. |
| **Foxglove won't connect** | Ensure both devices are on the same Wi-Fi and the Jetson IP is correct. |
| **Package not found** | Verify that `colcon build` finished successfully during the Docker build. |
