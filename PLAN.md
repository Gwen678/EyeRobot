# EyeRobot — Integration & Validation Plan

Steps are ordered by dependency. Each step has a clear pass/fail check.
Do not proceed to the next step until the current one passes.

---

## Optional: IMU Allan Variance Calibration

Run this once to get principled EKF process noise values instead of hand-tuned ones.
Requires 10–30 min of robot sitting perfectly still.

**Inside the container — record static IMU data:**
```bash
ros2 run oak_imu oak_imu_cube --orientation gyro --no-tf   # terminal 1
./record_static.sh                                          # terminal 2 — let run 30 min minimum
```

**Copy bag to PC:**
```bash
scp -r eyerobot@<JETSON_IP>:~/CleanTest/EyeRobot/bags/static_<timestamp> ~/bags/
```

**Analyse on PC (source ROS 2 first):**
```bash
python3 analyse_imu.py ~/bags/static_<timestamp>
```

Output: Allan deviation plot + recommended `Q[vyaw]` value for `ekf.yaml`.
Update `process_noise_covariance` diagonal entry [11][11] with the printed value,
then rebuild: `colcon build --packages-select manual_controller`.

---

## Step 1 — EKF validation (no lidar)  ✅

**Goal**: confirm EKF now fuses IMU yaw correctly after the QoS fix
(`/oak/imu/data_ekf` RELIABLE topic).

**Command:**
```bash
ros2 launch manual_controller eyerobot.launch.py ekf:=true
```

**Foxglove**: watch `/ekf_path` (red) vs `/path_imu` (olive).

**Test**: forward 1 m → turn 90° → forward 1 m → return to start.

**Reset between runs:**
```bash
ros2 service call /reset_odometry std_srvs/srv/Empty {}
ros2 service call /set_pose robot_localization/srv/SetPose \
  "{pose: {header: {frame_id: 'odom'}, pose: {pose: {orientation: {w: 1.0}}}}}"
```

| Result | Action |
|--------|--------|
| ✅ `ekf_path` tracks `path_imu` direction, turns match | Use EKF — continue to Step 2 |
| ❌ Still diverges / straight line | EKF broken — use `dual_odometry` as primary. Change Nav2 odom topic to `/odom_imu` |

---

## Step 2 — Lidar scan validation  ✅

**Goal**: confirm RPLidar A1M8 is publishing and the frame is correct.

**Command:**
```bash
ros2 launch manual_controller eyerobot.launch.py lidar:=true
```

**Foxglove**: add `/scan` (LaserScan). Set fixed frame to `odom`.

| Result | Action |
|--------|--------|
| ✅ Scan ring visible, centered on robot, walls readable | Continue |
| ❌ No scan | Check `ls /dev/ttyUSB*` — lidar may be on ttyUSB0 not ttyUSB1 |
| ❌ Scan ring in wrong position | Measure actual lidar height and update `lidar_mount` joint z in `Robot.xacro` (currently 0.20 m placeholder) |

---

## Step 3 — EKF + lidar TF chain  ✅

**Goal**: confirm `map→odom→base_link→laser` TF is intact and scan moves with the robot.

**Command:**
```bash
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true
```

**Foxglove**: add `/scan`. Drive the robot.

| Result | Action |
|--------|--------|
| ✅ Scan ring stays anchored to robot as it moves | Continue |
| ❌ Scan drifts or jumps | TF broken — run `ros2 run tf2_tools view_frames` and check the chain |

---

## Step 4 — AMCL localization on saved map

**Goal**: robot knows where it is on the map. AMCL provides `map→odom` TF.

**Available maps:**
```
/eyerobot/ros2_ws/maps/map.yaml
/eyerobot/ros2_ws/maps/map_fermee_sans_tapis.yaml
/eyerobot/ros2_ws/maps/map_ouverte_sans_tapis.yaml
```

**Commands (2 terminals):**
```bash
# Terminal 1
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true

# Terminal 2
ros2 launch manual_controller nav2.launch.py
# or with a specific map:
ros2 launch manual_controller nav2.launch.py map:=/eyerobot/ros2_ws/maps/map_fermee_sans_tapis.yaml
```

**Foxglove**: add `/map` (OccupancyGrid) + `/scan` (LaserScan) + `/amcl_pose`.

Place the robot at the real-world position of (0, 0, 0°) on the map before launching.
If the robot is elsewhere, publish an initial pose via Foxglove:
- Topic: `/initialpose`, type `geometry_msgs/PoseWithCovarianceStamped`, frame `map`

| Result | Action |
|--------|--------|
| ✅ Scan lines align with map walls, `/amcl_pose` covariance shrinks | Continue |
| ❌ Scan rotated relative to map | Wrong initial yaw — publish `/initialpose` with correct yaw |
| ❌ Scan translated but aligned | Wrong initial x/y — publish `/initialpose` with correct position |
| ❌ AMCL never converges | Drive the robot along a distinctive wall — gives AMCL more features to match |

---

## Step 5 — Costmaps

**Goal**: local and global costmaps show obstacles from live lidar scan.

**Commands:**
```bash
# Terminal 1 (same as Step 4)
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true

# Terminal 2
ros2 launch manual_controller nav2.launch.py full_nav:=true
```

**Foxglove**: add `/local_costmap/costmap` and `/global_costmap/costmap` (OccupancyGrid).

**Test**: drive toward a wall — inflated obstacle zone should appear ahead of the robot.

| Result | Action |
|--------|--------|
| ✅ Costmaps show inflated obstacles near walls | Continue |
| ❌ Costmaps empty | `/scan` not reaching Nav2 — check QoS or that lidar is running |

---

## Step 6 — cmd_vel bridge (manual test, no autonomous goal)

**Goal**: confirm `/cmd_vel` → wheel commands conversion is correct before sending
autonomous goals.

**Commands:**
```bash
# Terminal 1
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true cmd_vel_bridge:=true

# Terminal 2
ros2 launch manual_controller nav2.launch.py full_nav:=true
```

**Test** — publish a tiny forward command manually:
```bash
ros2 topic pub --once /cmd_vel geometry_msgs/Twist \
  "{linear: {x: 0.1}, angular: {z: 0.0}}"
```

Expected wheel speeds: `0.1 m/s ÷ 0.06 m = 1.67 rad/s` on both wheels.

```bash
ros2 topic echo /motor_rwheel_cmd --once
ros2 topic echo /motor_lwheel_cmd --once
```

| Result | Action |
|--------|--------|
| ✅ Both wheels show ~1.67 rad/s, robot nudges forward | Continue |
| ❌ No output on motor topics | Bridge not running — check `cmd_vel_bridge:=true` was passed |
| ❌ Robot turns instead of going straight | `left_command_sign` or `right_command_sign` wrong in bridge |

**Test turn:**
```bash
ros2 topic pub --once /cmd_vel geometry_msgs/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

Expected: right wheel positive, left wheel negative (or vice versa depending on sign convention).

---

## Step 7 — Full autonomous navigation

**Goal**: send a goal pose, robot drives there autonomously avoiding obstacles.

**Commands:** same as Step 6.

**Send a goal from Foxglove:**
- Panel → Publish → topic `/goal_pose`, type `geometry_msgs/PoseStamped`, frame `map`
- Set `x`, `y`, and orientation `w=1.0` (yaw=0) for a nearby reachable point

Or use the Foxglove 3D panel "Publish pose" tool if available.

| Result | Action |
|--------|--------|
| ✅ Robot plans path, drives to goal, stops | Done |
| ❌ Robot planned path but didn't move | cmd_vel bridge not running — check Step 6 |
| ❌ Robot oscillates or overshoots | Tune DWB controller gains in `nav2_params.yaml` (`max_vel_x`, `acc_lim_x`, `sim_time`) |
| ❌ Robot hits walls | Increase `inflation_radius` in `nav2_params.yaml` (currently 0.30 m) or fix footprint |
| ❌ AMCL loses localization mid-run | EKF odometry drifting — revisit Step 1 or run Allan calibration |

---

## Quick reference — all commands

```bash
# Robot stack (mix flags as needed)
ros2 launch manual_controller eyerobot.launch.py \
  lidar:=true ekf:=true cmd_vel_bridge:=true

# Localization only (AMCL → map->odom TF)
ros2 launch manual_controller nav2.launch.py \
  map:=/eyerobot/ros2_ws/maps/map_fermee_sans_tapis.yaml

# Full navigation stack
ros2 launch manual_controller nav2.launch.py full_nav:=true \
  map:=/eyerobot/ros2_ws/maps/map_fermee_sans_tapis.yaml

# Record a driving session for offline review
./record_run.sh

# Record static IMU data for Allan variance calibration
./record_static.sh

# Analyse IMU calibration bag (on PC, source ROS 2 first)
python3 analyse_imu.py ~/bags/static_<timestamp>

# Build after any code change
colcon build --packages-select manual_controller oak_imu && source install/setup.bash
```
