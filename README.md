@ -0,0 +1,127 @@
# EyeRobot Project, ROS 2 Deployment

This repository provides a standardized, Docker-based development environment for the **NVIDIA Jetson Nano**. It simplifies the deployment of **RPLidar A1/A2** sensors and integrates **Rosbridge** for high-performance remote telemetry and visualization.

---

# 1. Jetson SSH Access

To connect to the robot onboard computer (Jetson):

```bash
ssh eyerobot@128.179.185.128
```
### B. Project Setup
Clone the repository and build the container:
Username: eyerobot
Password: eyerobot

```bash
git clone https://github.com/Gwen678/EyeRobot.git
cd EyeRobot

# Build the Docker image (Name: eyerobot)
sudo docker build -t eyerobot .
```

---

## 2. Project Setup

Clone the repository:
```bash
git clone https://github.com/Gwen678/EyeRobot.git
cd EyeRobot
```


## 3. Build Docker image
```bash
docker build -t eyerobot .
```
## 4. Run container
```bash
docker run -it --rm \
    --net=host \
    --privileged \
    -v /dev:/dev \
    -v $(pwd)/ros2_ws:/ros2_ws \
    eyerobot
```
## 5. ROS2 Workspace Build

Inside the container:
```bash
cd /ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```
## 6. Launch Robot System
Full system launch exemple
```bash
ros2 launch robot_bringup bringup.launch.py
```
## 7. Developer & Collaboration Workflow

### Sharing your work
If you modify files in the `src/` folder:

```bash
git add .
git commit -m "feat: ..."
git push origin main
```

### Getting updates from the team
```bash
git pull origin main
# Always rebuild the image if the source code changed
sudo docker build -t eyerobot .
```

---

## 8. Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Lidar not spinning** | Check USB connection and run `sudo chmod 666 /dev/ttyUSB0` on the host. |
| **Foxglove won't connect** | Ensure both devices are on the same Wi-Fi and the Jetson IP is correct. |
| **Package not found** | Verify that `colcon build` finished successfully during the Docker build. |
