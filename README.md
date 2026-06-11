# EyeRobot

ESP32 (motors, micro-ROS) + first-gen Jetson Nano running ROS 2 Humble in Docker.
Firmware is pre-flashed and the container image + workspace are already built —
below are just the commands to connect and run.

## USB devices

| Stable name | Device | Fallback |
|-------------|--------|----------|
| `/dev/rplidar` | RPLidar A1M8 | `/dev/ttyUSB1` (enumeration-dependent!) |
| `/dev/esp32` | micro-ROS ESP32 | `/dev/ttyUSB0` (enumeration-dependent!) |

The stable names come from udev rules (`docker/99-eyerobot-usb.rules`, values
already measured for this robot's hardware — CP2102 lidar, CH340 ESP32).
One-time install on the **Jetson host** (not the container; the container
bind-mounts `/dev` so the symlinks appear inside):

```
sudo cp docker/99-eyerobot-usb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Unplug/replug both devices, then verify: `ls -l /dev/esp32 /dev/rplidar`.
Full guide (and what to do if the hardware changes): `UDEV.md`.

## Connect

From your PC. One-time: `ssh-copy-id eyerobot@128.179.186.106` (password `eyerobot`).

```
./ssh_jetson.sh
```

Drops you into the container shell. Run it again in a new terminal for each node.

## Run

### Odometry only (no lidar)

**Terminal 1** — micro-ROS agent (motors/encoders ↔ ROS):

```
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/esp32 -b 115200
```

(`/dev/esp32` needs the udev rules above; otherwise use the current `ttyUSBn`.)

**Terminal 2** — full stack (odometry + IMU + URDF/TF):

```
ros2 launch manual_controller eyerobot.launch.py ekf:=true
```

Starts the ros2_control stack (`diff_drive_controller` — wheel odometry and the
`odom`→`base_link` TF), the OAK-D IMU chain — `depthai_ros_driver` (raw on
`/oak/imu/data`) → `imu_remap` (axis signs + gyro bias, `/oak/imu/data_raw`) →
`imu_filter_madgwick` (fused on `/oak/imu/fused`) — and `robot_state_publisher`
for the URDF. **Keep the robot still for ~2 s after launch** until `imu_remap`
logs `gyro bias = …`: the gyro bias is averaged at startup and subtracted from
then on. With `ekf:=true`, `robot_localization`
fuses wheel odometry + IMU into `/odometry/filtered` (set `enable_odom_tf: false`
in `diff_drive_controller.yaml` so the EKF owns the `odom`→`base_link` TF).

**Terminal 3** — keyboard control (wheels + fans + belt, all in one terminal):

```
ros2 run manual_controller manual_controller
```

`w/s` forward/backward, `a/d` turn — published to `/cmd_vel`, which is
remapped straight into `diff_drive_controller` (ros2_control applies the
velocity/acceleration limits). `q/e` fans, `r/t` belt (latched — tap again to
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

### Autonomous mission (one command)

The whole stack — agent, sensors, Nav2, cmd_vel bridge, behavior tree — from a
single script (run in one container terminal):

```
bash /eyerobot/ros2_ws/src/manual_controller/launch/run_autonomous.sh
```
```
cd ../docker && ./build_ws.sh

cd ../ros2_ws && source install/setup.bash
```

`[mission]` selects the BT variant (default `full`): `zone1` = blocks only
(no button, no ramp); `zone3` = button + door phase, then zone 3 blocks;
`zone4` = ramp then zone 4 blocks, no button; `full` = everything. All
variants turn the fans on before the first motion and end with an
unconditional unload at base. Standalone equivalent:
`ros2 run autonomous_controller behavior_tree --mission zone1`.

It starts, in order: micro-ROS agent → wait for the IMU chain (aborts the
whole stack loudly if no IMU after 90 s) → `eyerobot.launch.py lidar:=true
ekf:=true lego:=true bt:=true` (vision + behavior tree are part of the launch)
→ Nav2 with `maps/clean_room_8x8.yaml` and `full_nav:=true`. Nav2's `/cmd_vel`
reaches `diff_drive_controller` directly (its subscription is remapped to
`/cmd_vel` — no relay node). The behavior tree arms itself: it waits for the
Nav2 action servers (30–60 s on the Nano, logged every 5 s), then for AMCL
localization — with the current config the mission starts as soon as AMCL
accepts the default start pose from `nav2_params_custom.yaml` (`initial_pose`
= arena/map `(1.0, 1.0)`). If you disable `set_initial_pose`, it will instead
idle until you seed AMCL manually from Foxglove. Ctrl+C tears everything down.

**How the BT collects blocks** (`autonomous_controller` package,
`autonomous_controller/behavioral_tree.py`):

- The lego vision node publishes map-frame detections on
  `/eyerobot/vision/lego_markers_map`; the BT's `BlockMemory` accumulates
  them (dedup at 0.30 m) and **drops any block the robot drives within
  0.35 m of** — with the roomba intake, driving over a block IS collecting
  it, so this doubles as the on-board block counter.
- Each collection round: if blocks are known, flow through the ≤5 nearest
  (`NavigateThroughPoses` — **no stopping**, fans absorb in passing);
  otherwise drive the next predefined sweep chunk (`ZONE*_SWEEP_CHUNKS`,
  still placeholder routes), which collects blindly and lets the camera
  discover blocks for the next round.
- After each round, the robot returns to base to discharge (fans reversed +
  belt on, 5 s) **only if ≥5 blocks were collected** since the last unload;
  otherwise it keeps collecting. The mission epilogue always unloads.
- If Nav2 aborts on an unreachable pose (block against a wall, inside the
  inflation radius), the BT pulls that pose back along its approach line
  (0.25 m, then 0.45 m) and resends the rest of the route; a pose that keeps
  failing is dropped so one bad block never kills the mission.

Mission poses (button, door, ramp, base) live in `behavioral_tree.py` in the
**arena frame** (lower-left arena corner = (0,0), from fsm.py) and are
passed through `arena_to_map()`, which is currently a no-op because
`clean_room_8x8.yaml` is re-zeroed so arena frame == map frame.
The BT is symlink-installed: editing it (or any config/launch file) takes
effect on relaunch without a rebuild.

### Fallback: the same stack, terminal by terminal

Requires a pre-built map. Run eyerobot.launch.py **without** `slam:=true`, then
start Nav2 in a separate terminal.

**Terminal 1** — micro-ROS agent (same as above)

**Terminal 2** — full stack with lidar (no SLAM — AMCL owns map→odom).
`lego:=true` runs the vision node — required for the BT's vision-planned
block routes (without it the BT falls back to the predefined sweeps):

```
ros2 launch manual_controller eyerobot.launch.py lidar:=true ekf:=true lego:=true
```

**Terminal 3** — Nav2 (AMCL localization + planner/controller; `full_nav:=true`
also starts the planner/controller/waypoint servers the BT's actions need):

```
ros2 launch manual_controller nav2.launch.py map:=/eyerobot/ros2_ws/maps/clean_room_8x8.yaml full_nav:=true
```

(No relay terminal needed: `diff_drive_controller`'s subscription is remapped
to `/cmd_vel` in `manual_controller.launch.py`, so Nav2, teleop, and anything
else publishing `/cmd_vel` drive the wheels directly.)

**Terminal 4** — behavior tree (or skip it and drive manually / send Nav2
goals from Foxglove). Either add `bt:=true bt_mission:=<mission>` to the
Terminal 2 launch instead, or run it standalone:

```
ros2 run autonomous_controller behavior_tree --mission zone1
```

Both ways it arms itself: the mission starts once AMCL receives its initial
pose from Foxglove.

The robot has obstacle avoidance active at all times via the live local costmap.

Do **not** run `slam:=true` and `nav2.launch.py` at the same time — both try to
publish `map→odom` and will conflict.

### AMCL sanity check (do this once per map before trusting navigation)

Verifies that the map yaml's `origin`/`resolution` match the image and that AMCL
can localize on it. Especially needed for `clean_room_8x8.yaml`, whose origin was
derived by pixel-correlating the GIMP-cleaned image against the original map.

1. Start the stack as above (Terminals 1–3) with the map you want to validate.
2. In Foxglove's 3D panel set the display frame to `map`, enable the `/map`
   topic and the `/scan` topic.
3. Give AMCL its initial guess: click **Set pose** (the pose-estimate tool in
   the 3D panel toolbar, publishes `/initialpose`), then click-drag on the map
   at the robot's real position, dragging in its facing direction.
4. The laser scan should snap onto the map walls within a second or two.
   Drive forward ~1 m and rotate in place — the scan must stay glued to the
   walls while the robot moves.

Reading the result:

- **Scan aligns and tracks** → map image + resolution are good, AMCL works.
- **Scan stays offset and AMCL never corrects it** → AMCL isn't localizing:
  it didn't receive the initial pose, or map→odom isn't being published
  (check `ros2 topic echo /amcl_pose` updates while driving).
- **Scan walls are scaled (too big/small) vs map walls** → wrong `resolution`
  (see the 0.05 vs 0.005 stale-publisher trap above).
- **Scan matches some walls but geometry disagrees** → the map image itself no
  longer matches the room; rebuild the map.

Note this check **cannot** detect a wrong yaml `origin`: the map renderer and
AMCL both place the grid using the same origin, so an origin error shifts the
displayed map and the pose estimate together and the scan still lands on the
walls. A wrong origin only bites coordinates authored *outside* this yaml —
hardcoded mission waypoints, saved lego positions, numeric `initial_pose`
params (for `clean_room_8x8.yaml` those were authored in the original
`room_8x8` frame, which its corrected origin is meant to reproduce). To
validate the origin: drive the robot to a known landmark, `ros2 topic echo
/amcl_pose`, and compare against that landmark's expected map coordinate.

## Visualization (Foxglove)

Open [Foxglove Studio](https://foxglove.dev) on your PC and connect to
`ws://<jetson-ip>:8765`. The `foxglove_bridge` node starts automatically with
the launch file.

To visualize the robot model: display the topic `/robot_description_volatile`
(URDF custom layer, or the topic row in newer Foxglove) — NOT
`/robot_description`: that topic is shared with the depthai driver's
camera-only URDF (last latched writer wins, and the camera boots last), so it
shows an OAK-D box instead of the robot. Details + mesh setup: `URDF.md`.

To send Nav2 goals: in the 3D panel settings → **Publish**, change the *Pose*
topic from its `/move_base_simple/goal` default to **`/goal_pose`** (one-time;
*Pose estimate* already defaults to `/initialpose`). With Nav2 up
(`full_nav:=true` + relay) and AMCL localized, use the publish-pose tool and
click-drag on the map (click = position, drag = heading) — `bt_navigator`
turns `/goal_pose` into a NavigateToPose action by itself. Publishing from
Foxglove needs the bridge's `clientPublish` capability (already enabled in
eyerobot.launch.py). Don't send manual goals while the `bt:=true` mission is
running — they preempt each other.

To see the trajectory: in the 3D panel set the display frame to `odom` and
enable the path topics — `/wheel_path` (raw wheel odometry, always published)
and `/ekf_path` (fused EKF estimate, needs `ekf:=true`). Driving a loop and
comparing where the two paths end up vs the robot's true position is the
quickest EKF-precision check. Numeric pose readouts: `/pose2d_wheel`,
`/pose2d_ekf` (x m, y m, yaw deg).

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
WiFi-only DDS profiles for both ends.
If RViz still stays empty, re-run after confirming the Jetson IP is correct.

## IMU calibration (Allan variance)

Record a static bag (robot not moving, ≥10 min):

```
ros2 bag record -o ~/bags/static_$(date +%Y%m%d_%H%M) /oak/imu/data
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
Stable USB names setup: `UDEV.md`. Robot model in Foxglove: `URDF.md`.
Codebase review (defects, architecture, package verdicts): `ANALYSIS.md`.
2026-06-10 overhaul session (motor control, IMU tilt fix, validation): `CHANGELOG-2026-06-10.md`.
