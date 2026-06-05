# EyeRobot

An ESP32 motor controller plus a Jetson Orin Nano running ROS 2 in Docker.
The ESP32 does closed-loop motor control and talks to the Jetson over micro-ROS.
The Jetson runs camera, lidar, SLAM, Nav2, perception and teleop.

## Layout

- `firmware/`: ESP32 PlatformIO firmware (motors, micro-ROS). Not a ROS package.
- `ros2_ws/src/`: the ROS 2 packages.
  - `manual_controller`: keyboard teleop and wheel odometry.
  - `robot_description`: URDF and meshes.
  - `perception`: Oak-D viewer, YOLO detection, lidar web viewer.
  - `sllidar_ros2`: RPLidar driver.
  - `depthai-ros`: Oak-D driver (submodule).
  - `slam_toolbox`: SLAM (submodule).
  - `rosbridge_*`: remote telemetry.
- `docker/`: container and helper scripts.
- `third_party/`: yolov5, depthai-model-zoo (submodules).

Build output (`build/`, `install/`, `log/`), datasets and `__pycache__` are git
ignored. Do not commit them.

## Clone

HTTPS is not enabled. Use SSH.

```
git clone --recurse-submodules -b feature/IMU git@github.com:Gwen678/EyeRobot.git
cd EyeRobot
```

If you already cloned without submodules:

```
git submodule update --init --recursive
```

## Jetson Docker

Connect:

```
ssh eyerobot@128.179.185.128   # password: eyerobot
```

Scripts in `docker/`:

- `docker/build.sh`: build the image.
- `docker/run.sh`: start the container and open a shell in `ros2_ws`.
- `docker/attach.sh`: open another shell in the running container.
- `docker/build_ws.sh`: run inside the container, builds the workspace.
- `docker/stop.sh`: stop and remove the container.

First run:

```
./docker/build.sh
./docker/run.sh
```

Then inside the container:

```
/eyerobot/docker/build_ws.sh
source install/setup.bash
```

The repo is mounted at `/eyerobot`, so edits and build output stay on the host.
The container keeps running after you exit. Use `docker/attach.sh` for more shells.

## Run the nodes

Inside the container, one shell per node:

```
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
ros2 launch sllidar_ros2 sllidar_a1_launch.py
ros2 launch depthai_ros_driver camera.launch.py
ros2 launch slam_toolbox online_async_launch.py
ros2 run manual_controller state_estimator
ros2 run manual_controller manual_controller
ros2 run perception detect_lego
python3 -m perception.oak_view
python3 -m perception.lidar_web
```

Pick the `sllidar` launch that matches your model (a1, a2m8, c1, s2, etc.).

## Firmware

The ESP32 firmware is flashed with PlatformIO, separate from ROS.

```
cd firmware
pio run
pio run --target upload --upload-port /dev/ttyUSB0
```

Details in `firmware/DOCS.md`.

## Remote visualization

```
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

Connect Foxglove to `ws://JETSON_IP:9090`.

## Troubleshooting

- Empty submodule folders: run `git submodule update --init --recursive`.
- Lidar permission denied: on the host run `sudo chmod 666 /dev/ttyUSB0`.
- depthai-ros build fails on depthai-core: `build_ws.sh` clones it. Adjust the
  branch in `docker/build_ws.sh` if the version mismatches.
- Missing ROS dependency: inside the container run
  `rosdep install --from-paths src --ignore-src -y`.
- GPU: the image is CPU only. For CUDA YOLO on the Jetson, use an NVIDIA L4T ROS
  base image in `docker/Dockerfile`.

## More docs

- `firmware/DOCS.md`: firmware and motor control.
