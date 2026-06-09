# EyeRobot

ESP32 (motors, micro-ROS) + first-gen Jetson Nano running ROS 2 Humble in Docker.
Firmware is pre-flashed and the container image + workspace are already built —
below are just the commands to connect and run.

## USB port mapping

| Port | Device |
|------|--------|
| `/dev/ttyUSB0` | RPLidar A1M8 |
| `/dev/ttyUSB1` | micro-ROS ESP32 |

## Connect

From your PC. One-time: `ssh-copy-id eyerobot@128.179.186.106` (password `eyerobot`).

```
./ssh_jetson.sh
```

Drops you into the container shell. Run it again in a new terminal for each node.

## Run

### Odometry only (no lidar)

**Terminal 1** — micro-ROS agent (motors/encoders ↔ ROS, ESP32 on ttyUSB1):

```
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB1 -b 115200
```

**Terminal 2** — full stack (odometry + IMU + URDF/TF):

```
ros2 launch manual_controller eyerobot.launch.py ekf:=true
```

Starts the ros2_control stack (`diff_drive_controller` — wheel odometry and the
`odom`→`base_link` TF), the OAK-D IMU via `depthai_ros_driver` (`/oak/imu`, IMU
only, camera streams disabled) filtered by `imu_filter_madgwick` (`/oak/imu/data`),
and `robot_state_publisher` for the URDF. With `ekf:=true`, `robot_localization`
fuses wheel odometry + IMU into `/odometry/filtered` (set `enable_odom_tf: false`
in `diff_drive_controller.yaml` so the EKF owns the `odom`→`base_link` TF).

**Terminal 3** — keyboard control (wheels + fans + belt, all in one terminal):

```
ros2 run manual_controller manual_controller
```

`w/s` forward/backward, `a/d` turn — published to
`/diff_drive_controller/cmd_vel_unstamped` (ros2_control caps velocity; no
acceleration ramp, commands apply immediately). `q/e` fans, `r/t` belt (latched — tap again to
stop), `space` stops everything. `u/j`, `i/k`, `o/l` adjust max/linear/angular
speed.

### Mapping (SLAM)

Run this once per room to build a map. Drive the full perimeter slowly.

**Terminal 1** — micro-ROS agent (same as above)

**Terminal 2** — full stack with lidar + SLAM:

```
ros2 launch manual_controller eyerobot.launch.py lidar:=true slam:=true ekf:=true
```

**Terminal 3** — keyboard control (same as above)

**Terminal 5** — save map after driving the room:

```
ros2 run nav2_map_server map_saver_cli -f /eyerobot/ros2_ws/maps/room_8x8 --ros-args -p map_subscribe_transient_local:=true
```

Check that the saved `.yaml` shows `resolution: 0.05`. If it shows `0.005` the map
came from a stale publisher — close all terminals, restart only the SLAM launch, and
save again.

### Localization + Navigation (AMCL + Nav2)

Requires a pre-built map. Run eyerobot.launch.py **without** `slam:=true`, then
start Nav2 in a separate terminal.

**Terminal 1** — micro-ROS agent

**Terminal 2** — full stack with lidar (no SLAM — AMCL owns map→odom):

```
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true
```

**Terminal 3** — Nav2 (AMCL localization + planner/controller):

```
ros2 launch manual_controller nav2.launch.py map:=/eyerobot/ros2_ws/maps/room_8x8.yaml
```

With `full_nav:=true`, Nav2 publishes `/cmd_vel` — but `diff_drive_controller`
listens on `/diff_drive_controller/cmd_vel_unstamped`, so bridge it first:

```
ros2 run topic_tools relay /cmd_vel /diff_drive_controller/cmd_vel_unstamped
```

The robot has obstacle avoidance active at all times via the live local costmap.

Do **not** run `slam:=true` and `nav2.launch.py` at the same time — both try to
publish `map→odom` and will conflict.

## Visualization (Foxglove)

Open [Foxglove Studio](https://foxglove.dev) on your PC and connect to
`ws://<jetson-ip>:8765`. The `foxglove_bridge` node starts automatically with
the launch file.

To visualize the robot model: add a **URDF** panel and set the topic to
`/robot_description_volatile`.

## Visualization (RViz)

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

## IMU calibration (Allan variance)

Record a static bag (robot not moving, ≥10 min):

```
ros2 bag record -o ~/bags/static_$(date +%Y%m%d_%H%M) /oak/imu
```

Analyse on the PC:

```
python3 analyse_imu.py ~/bags/static_<name>
```

Outputs per-axis angle random walk and bias values — use them to tune the
`imu0` covariances in `ros2_ws/src/manual_controller/config/ekf.yaml` and the
Madgwick gain in `config/imu_filter.yaml`.

---

Build/image details: `docker/README.md`. Firmware: `firmware/DOCS.md`.
