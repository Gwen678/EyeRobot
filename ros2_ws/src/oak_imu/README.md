# oak_imu — OAK-D Lite IMU → RViz cube

ROS 2 (Humble) package that reads the **raw IMU** of a Luxonis **OAK-D Lite**
(BMI270: accelerometer + gyroscope, no magnetometer) via the DepthAI library and
shows the real-time orientation as a **cube in RViz**. It publishes
`/oak/imu/data_raw`, which the `manual_controller` **dual_odometry** node consumes
for the encoder+IMU-yaw trajectory comparison.

This is the **raw** stage. Orientation from raw data drifts (gyro) or is noisy
(accel) — that is on purpose; filtering is the next step.

## Package layout (in `EyeRobot/ros2_ws/src/oak_imu/`)
```
oak_imu/
├── oak_imu/oak_imu_cube.py  # the node (reads IMU, publishes Imu + TF + Marker)
├── launch/oak_imu.launch.py # ros2 launch oak_imu oak_imu.launch.py
├── rviz/imu_cube.rviz       # standalone cube view (Grid + TF + cube Marker)
├── requirements.txt         # depthai==2.30.0.0 (pip, not rosdep)
├── package.xml / setup.py   # ament_python package
```

## What it publishes
| Topic / channel        | Type                          | Notes                             |
|------------------------|-------------------------------|-----------------------------------|
| `/oak/imu/data_raw`    | `sensor_msgs/Imu`             | accel (m/s²) + gyro (rad/s)       |
| `/oak/imu/cube`        | `visualization_msgs/Marker`   | the cube, in `imu_link`           |
| `/oak/imu/trail`       | `visualization_msgs/Marker`   | LINE_STRIP path of integrated pos |
| TF `world → imu_link`  | `tf2`                         | estimated orientation + position  |

## Axis remap (important)
The BMI270 frame is rotated **180° about X** relative to the ROS convention
(REP-103): at rest it reads accel **Z = −9.81**, but ROS expects **+9.81**. The
node remaps both accel and gyro with signs `(1, -1, -1)` (override with
`--accel-signs` / `--gyro-signs`). Without this, rotation about Y/Z appears
**inverted** and gravity is upside-down.

## Install
```bash
# 1) DepthAI python (v2 API, pinned)
pip install -r requirements.txt
#    or: pip install 'depthai==2.30.0.0'

# 2) Plug the OAK-D Lite into a USB3 port.
```
On Linux, set up DepthAI udev rules once so the device is reachable without root:
```bash
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | \
  sudo tee /etc/udev/rules.d/80-movidius.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## Build & run
```bash
cd EyeRobot/ros2_ws
colcon build --packages-select oak_imu
source install/setup.bash

# Just the IMU publisher (what the pipeline needs):
ros2 run oak_imu oak_imu_cube
ros2 run oak_imu oak_imu_cube --ros-args        # (args after --, e.g. below)
ros2 run oak_imu oak_imu_cube --orientation accel

# Publisher + standalone rotating-cube RViz view:
ros2 launch oak_imu oak_imu.launch.py rviz:=true
ros2 launch oak_imu oak_imu.launch.py orientation:=complementary
```
In the full pipeline, run this publisher alongside `manual_controller` so
`dual_odometry` gets `/oak/imu/data_raw` (the encoder+IMU-yaw green path).

## Orientation modes (`--orientation`)
- **`gyro`** *(default, raw)* — integrate angular velocity. Full 3-DOF rotation,
  but **drifts** with time. This drift is what we'll fix with filtering.
- **`accel`** — roll/pitch directly from the gravity vector. No drift, but no yaw
  (no magnetometer) and noisy while moving.
- **`complementary`** — first taste of fusion: gyro for fast motion, accel to
  correct roll/pitch drift. `--alpha 0.98` sets the gyro trust.

## Encoder vs encoder+IMU-yaw comparison (`odom_compare.py`)
Two dead-reckoned trajectories drawn together in RViz, differing in **only** the
yaw source (same encoder distance for both), so you can see how much the IMU
heading helps:
- **RED** `/compare/path_encoder` — pure wheel odometry (yaw from wheel difference)
- **GREEN** `/compare/path_imu_yaw` — encoder distance + IMU yaw

Wheel-difference yaw drifts on every slip/scrub; IMU yaw doesn't, so the green
line stays truer. Subscribes `/motor_rwheel_fb`, `/motor_lwheel_fb` (Int32 ticks
from the EyeRobot firmware) and `/oak/imu/data_raw` (from `oak_imu_cube.py`).
Geometry matches the EyeRobot `state_estimator` (5756 cpr, r=0.06, sep=0.150).

```bash
# needs the micro-ROS agent running (encoder topics) + OAK plugged in
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0   # elsewhere
ros2 launch ./launch/odom_compare.launch.py        # IMU node + compare + RViz
```
If the IMU yaw turns the wrong way vs the encoders (mounting), flip it:
`python3 odom_compare.py --ros-args -p imu_yaw_sign:=-1.0`. This is a comparison
demo; the eventual fusion is a `robot_localization` EKF (`/odom` + `/imu`).

## Position
**Default is gyro-only orientation** (cube fixed at the origin, rotates with the
IMU). Real position will come from the **wheel encoders fused with the IMU** via
an EKF (`robot_localization`) — encoders give x/y, the IMU gives heading. The
accelerometer double-integration below is a retired experiment, kept behind the
`--position` flag because raw IMU cannot hold position (see why below).

### `--position`: accel double integration (experiment, drifts)
The node rotates the measured acceleration into the world frame, subtracts a
slowly-estimated gravity vector (high-pass), and integrates **accel → velocity →
position**. The cube then physically moves in RViz and leaves a yellow trail.

**The hard part is gravity, not the integration.** Gravity is ~9.81 m/s², so a
few degrees of orientation error during a turn leaks `sin(err)·9.81` m/s² of
*fake* horizontal acceleration that double-integrates into runaway drift — which
is why **turning used to fling the cube away**.

Fixes, in order of importance:
- **Gyro-bias subtraction** (the big one). The raw gyro reads a constant ~0.25°/s
  even at rest; integrating it slowly rotates the orientation, which rotates the
  world-frame gravity away from the calibrated reference and leaks fake accel
  into the integral. The bias is measured during the startup still-period (and
  refreshed during ZUPT) and subtracted from every reading — this cut rest
  orientation creep from ~3°/12s to ~0.02°/12s. (Accel bias is already cancelled
  by the gravity calibration.)
- **Rotation-invariant motion gate** (`--accel-deadband`, default 0.5 m/s²). A
  spinning-in-place sensor still only senses gravity, so `|accel| ≈ g`. We gate
  integration on `| |accel| − g |`, which only changes for *real* linear
  acceleration. Turning is therefore ignored regardless of how fast you spin.
- **Startup gravity calibration** (`--calib-time`): hold still ~1 s; the node
  freezes the gravity vector + magnitude `g`.
- **ZUPT + velocity bleed** (`--zupt-*`, `--vel-bleed`, `--motion-hold`): when no
  linear motion is detected, velocity bleeds to zero and position freezes; when
  fully still, gravity is slowly relearned. A debounce (`--motion-hold`) stops a
  brief accel→decel zero-crossing from being mistaken for a stop.

Hold still → cube parks; **turn it → it stays put**; translate it → it travels
and stays. Watch the raw, ungated estimate (full drift) with `--no-zupt`.

**The drift⇄spring dial (`--vel-damping`).** An accelerometer cannot tell a real
sustained move from a slow bias — both are "persistent velocity". So velocity
damping is a tradeoff, not a cure:
- `1.0` (off): full moves register, but slow bias drifts (a travelling sinusoid).
- `0.95`: drift killed, but real moves shrink/spring back (time-constant ~0.1 s,
  shorter than a hand move).
- `~0.998` (default): time-constant ~2.5 s — longer than a ~1 s hand move (keeps
  ~85–90 % of it) but short enough to bleed off slow drift. Tune 0.995↔0.999.

This is still a *demo*, not metric odometry: a constant-velocity slide produces
no acceleration (invisible), and bias accumulates between stops. Drift-free
position needs visual(-inertial) odometry from the OAK cameras — beyond raw IMU.

Disable it with `--no-position` for orientation-only.

## Quick checks
```bash
ros2 topic hz /oak/imu/data_raw     # should be ~200 Hz
ros2 topic echo /oak/imu/data_raw   # see raw values
ros2 run tf2_tools view_frames      # confirm world -> imu_link
```

## Notes / gotchas
- **No IMU?** A few very early OAK-D Lite units shipped without an IMU. The node
  prints the connected IMU on startup and warns if there is none.
- **DepthAI v3** has a different IMU API — keep the pinned **v2** for this node.
- Move the camera and the cube should follow in real time. In `gyro` mode, leave
  it still and watch the cube slowly drift → motivation for the filter step.

## Next: filtering
The hook is already there — start from `--orientation complementary`, then we can
swap in a Madgwick/Mahony or EKF filter for a drift-free, low-noise pose.
