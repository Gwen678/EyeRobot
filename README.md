# EyeRobot

ESP32 (motors, micro-ROS) + first-gen Jetson Nano running ROS 2 Humble in Docker.

## Repository layout

```
EyeRobot/
├── firmware/                  # ESP32 motor-control firmware (PlatformIO / ESP-IDF + FreeRTOS)
│   ├── include/               #   AppBus, Channel, Encoder, MotorController, PiController,
│   │                          #   MotorTask, MicroRosTask, Thread, pins
│   ├── src/                   #   task implementations + esp32_serial_transport + main.cpp
│   ├── components/            #   micro_ros_espidf_component (vendored)
│   └── platformio.ini         #   build envs (featheresp32 / upesy_wroom)
├── ros2_ws/                   # ROS 2 Humble workspace (Jetson)
│   ├── src/
│   │   ├── manual_controller/    # teleop, cmd_vel/fans/belt bridge, IMU remap, vision, launch + config
│   │   │   ├── manual_controller/   # nodes: manual_controller, cmd_vel_bridge, imu_remap,
│   │   │   │                        #   lego_vision (HSV), yolo_vision (VPU), block_tracker,
│   │   │   │                        #   odom_to_path, urdf_relay, nn_config
│   │   │   ├── launch/              # eyerobot, nav2, manual_controller, lego_test, run_autonomous.sh
│   │   │   └── config/             # ekf, imu_filter, diff_drive_controller, nav2_params,
│   │   │                           #   slam_toolbox_params, depthai_camera(_yolo)
│   │   ├── autonomous_controller/   # mission behaviour tree (behavioral_tree.py) + nav2_params_custom
│   │   ├── perception/              # trained model best.pt / best.blob + dataset/label/view tools
│   │   ├── eyerobot_hardware/       # ros2_control SystemInterface plugin (micro-ROS motor bridge)
│   │   └── robot_description/       # URDF (Robot.xacro), meshes, launch
│   └── maps/                  # saved SLAM maps (room_8x8, clean_room_8x8, ...)
├── docker/                    # Dockerfile + build/run/attach/stop scripts, udev rules
├── microros_agent/            # micro-ROS agent assets
├── ml/                        # detector training / dataset work
├── report/                    # compiled report PDF + figures, documents, CAD
├── third_party/               # vendored dependencies
└── ssh_jetson.sh              # SSH into the Jetson container
```

## Build (first time, or on a new machine)

```bash
./docker/build.sh                 # build the eyerobot:humble image (CPU; builds anywhere)
./docker/run.sh                   # start the container (detached) + open a shell
/eyerobot/docker/build_ws.sh      # inside the container: build the ROS 2 workspace
```

Remove the container: `./docker/stop.sh`. Image/build internals: `docker/README.md`.

## USB devices

| Stable name | Device | Fallback |
|-------------|--------|----------|
| `/dev/rplidar` | RPLidar A1M8 | `/dev/ttyUSB1` |
| `/dev/esp32`   | micro-ROS ESP32 | `/dev/ttyUSB0` |

Install the udev rules once on the **Jetson host**:

```bash
sudo cp docker/99-eyerobot-usb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Verify: `ls -l /dev/esp32 /dev/rplidar`. Full guide: `UDEV.md`.

## Connect

```bash
ssh-copy-id eyerobot@128.179.186.106   # one-time (password: eyerobot)
./ssh_jetson.sh                         # drops into the container shell; re-run per terminal
```

## Run

### Odometry only (no lidar)

**Terminal 1**: micro-ROS agent

```bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/esp32 -b 115200
```

**Terminal 2**: full stack (odometry + IMU + URDF/TF)

```bash
ros2 launch manual_controller eyerobot.launch.py ekf:=true
```

**Terminal 3**: keyboard control (wheels + fans + belt)

```bash
ros2 run manual_controller manual_controller
```

`w/s` drive, `a/d` turn, `q/e` fans, `r/t` belt, `space` stop, `u/j i/k o/l` adjust max/linear/angular speed.

### Mapping (SLAM)

**Terminal 1**: micro-ROS agent (as above)

**Terminal 2**: full stack with lidar + SLAM

```bash
ros2 launch manual_controller eyerobot.launch.py lidar:=true slam:=true ekf:=true
```

**Terminal 3**: keyboard control (as above)

**Terminal 4**: save map after driving the room

```bash
ros2 run nav2_map_server map_saver_cli -f /eyerobot/ros2_ws/maps/room_8x8 --ros-args -p map_subscribe_transient_local:=true
```

### Autonomous mission (one command)

```bash
bash /eyerobot/ros2_ws/src/manual_controller/launch/run_autonomous.sh full
```

Missions: `full` | `zone3` | `zone4` | `zone1` | `test_center`. Standalone BT: `ros2 run autonomous_controller behavior_tree --mission zone1`.

### Fallback: the same stack, terminal by terminal

**Terminal 1**: micro-ROS agent (as above)

**Terminal 2**: full stack with lidar (no SLAM), vision on

```bash
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true lego:=true
```

**Terminal 3**: Nav2 (AMCL + planner/controller)

```bash
ros2 launch manual_controller nav2.launch.py map:=/eyerobot/ros2_ws/maps/clean_room_8x8.yaml full_nav:=true
```

**Terminal 4**: behavior tree

```bash
ros2 run autonomous_controller behavior_tree --mission zone1
```

Do **not** run `slam:=true` and `nav2.launch.py` at the same time (both publish `map`->`odom`).

## Visualization (Foxglove)

Connect [Foxglove Studio](https://foxglove.dev) to `ws://<jetson-ip>:8765` (the `foxglove_bridge` starts with the launch file).

- Robot model: display `/robot_description_volatile` (not `/robot_description`).
- Send Nav2 goals: set the Publish *Pose* topic to `/goal_pose`, then click-drag on the map.
- Trajectory: display frame `odom`, enable `/wheel_path` and `/ekf_path`; pose readouts `/pose2d_wheel`, `/pose2d_ekf`.

---

Build/image details: `docker/README.md`. Firmware: `firmware/DOCS.md`.
Stable USB names: `UDEV.md`. Robot model in Foxglove: `URDF.md`.
Codebase review: `ANALYSIS.md`.
