# EyeRobot

ESP32 (motors, micro-ROS) + first-gen Jetson Nano running ROS 2 Humble in Docker.
Firmware is pre-flashed and the container image + workspace are already built —
below are just the commands to connect and run.

## Connect

From your PC. One-time: `ssh-copy-id eyerobot@128.179.186.106` (password `eyerobot`).

```
./ssh_jetson.sh
```

Drops you into the container shell. Run it again in a new terminal for each node.

## Run

micro-ROS agent — motors/encoders ↔ ROS (ESP32 on USB):

```
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB1 -b 115200
```

Teleop — drive the robot (`w/a/s/d` wheels, `q/e` fans, `r/t` belt):

```
ros2 run manual_controller manual_controller
```

## Optional

Dual odometry — encoder-only vs encoder+IMU paths (`/path_encoder`, `/path_imu`):

```
ros2 run manual_controller dual_odometry
```

### Visualization (RViz)

RViz runs **on your PC, not the Jetson**. First launch this on the Jetson then the rviz script on PC.

```
ros2 launch manual_controller manual_controller.launch.py
```
```
./rviz_eyerobot.sh                  # or: ./rviz_eyerobot.sh <jetson-ip>
```

`rviz_eyerobot.sh` runs `dds_setup.sh` first, which works around two things that
otherwise stop the Jetson's topics from reaching the PC: campus WiFi blocking DDS
discovery multicast, and both machines sharing `docker0` at `172.17.0.1` (DDS sends
data to its own docker bridge, so topics list but `echo` is empty). It writes
WiFi-only DDS profiles for both ends. `run_eyerobot.sh` does the same automatically.
If RViz still stays empty, re-run after confirming the Jetson IP is correct.

---

Build/image details: `docker/README.md`. Firmware: `firmware/DOCS.md`.
