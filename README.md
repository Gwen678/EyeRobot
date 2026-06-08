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

Three terminals (re-run `./ssh_jetson.sh` for a new container shell). Start them
in this order.

**Terminal 1** — micro-ROS agent (motors/encoders ↔ ROS, ESP32 on USB):

```
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
```

**Terminal 2** — full stack (odometry + IMU + URDF/TF):

```
ros2 launch manual_controller eyerobot.launch.py ekf:=true
```

Starts `state_estimator` (`/odom`, `odom`→`base_link` TF), `dual_odometry`
(`/path_encoder` heading from wheels, `/path_imu` heading from IMU), the OAK-D IMU
(`/oak/imu/data_raw`, gyro mode), and `robot_state_publisher`/`joint_state_publisher`
for the URDF. Keep the robot **still for ~2 s** until it logs `gyro bias = …` before
driving — the BMI270 has no on-chip fusion and bias is averaged at startup.

**Terminal 3** — keyboard teleop (`w/a/s/d` wheels, `q/e` fans, `r/t` belt):

```
ros2 run manual_controller manual_controller
```

### Visualization (RViz)

RViz runs **on your PC, not the Jetson**, with the stack above already running on the
Jetson. The PC needs its own native build of the workspace first (the Jetson's build
is ARM and won't load on an x86 PC):

```
cd ros2_ws && colcon build --packages-select robot_description manual_controller
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
