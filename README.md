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

One terminal each (re-run `./ssh_jetson.sh` for a new container shell). Start them
in this order.

micro-ROS agent — motors/encoders ↔ ROS (ESP32 on USB):

```
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB1 -b 115200
```

Odometry stack — wheel odometry + the encoder-vs-IMU path comparison + URDF/TF for RViz:

```
ros2 launch manual_controller manual_controller.launch.py
```

Publishes `/odom` (and the `odom`→`base_link` TF) from `state_estimator`, plus two
comparison trajectories from `dual_odometry`: `/path_encoder` (heading from the
wheels) and `/path_imu` (heading from the IMU, distance from the wheels). Teleop and
RViz stay off here on purpose — run them in their own terminals (below).

IMU — software-fused orientation on `/oak/imu/data_raw`, feeds the `/path_imu` heading:

```
ros2 launch oak_imu oak_imu.launch.py orientation:=gyro
```

Keep the robot **still for ~2 s at startup** until it logs `gyro_bias=…` (gyro-bias
calibration). The OAK-D Lite IMU (BMI270) has no on-chip fusion, so this node fuses
accel+gyro on the host. It opens the OAK directly, so don't run a depthai camera
driver at the same time — only one process can own the camera over USB.

`orientation:=complementary` gives the full orientation: roll/pitch from the
accelerometer (drift-free — this is the ramp/tilt signal) and yaw from the gyro
(drifts slowly; no magnetometer). `gyro` integrates all three axes but its yaw and
tilt both drift. For the floor-path yaw comparison `dual_odometry` ignores this
mode entirely (it derives yaw from the gyro rate about gravity directly).

Teleop — drive the robot (`w/a/s/d` wheels, `q/e` fans, `r/t` belt):

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
