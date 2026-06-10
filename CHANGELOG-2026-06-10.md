# EyeRobot — 2026-06-10 session: changes & optimizations

One marathon session from "motors misbehave and the IMU is unusable" to
"EKF agrees with physical reality to ~1° per turn and the square closes."
Reverse-chronological debugging, forward-chronological summary.

## Firmware (ESP32) — motor control rebuilt

- **Left wheel positive-feedback bug (the big one).** `invert_encoder=false,
  invert_motor=true` with an encoder that counts negative-on-forward made the
  left PI loop positive feedback: forward commands railed the duty and the
  wheel ran away to free speed (~11 rad/s vs 8.3 setpoint) while the right
  tracked. Fixed to `(true, true)` in `AppBus.hpp`; host `left_feedback_sign`
  flipped to `+1` in `Robot.xacro` to match (the two MUST deploy together).
- **PI retune from measured plant gain** (100% duty ≈ 11 rad/s ≈ 10 000
  ticks/s): `Kp 0.1 → 0.01` (old value saturated at ±100 for any error over
  ~1 rad/s — bang-bang), `Ki 0.02 → 0.04`. Steady-state ripple is now ±1
  quantization step (±0.11 rad/s), which is the measurement floor, not a loop
  problem.
- **Feedforward launch** (`duty = sign·15 + 0.01·setpoint + PI trim`): kills
  the wind-up-then-lurch launch (LED ramping while the wheel sat stuck below
  gearbox breakaway, then jumping at full integral).
- **Min sustainable speed floor** (1.0 rad/s, hardware-verified): non-zero
  setpoints below it are floored, so the bottom of the host accel ramp becomes
  immediate motion instead of launch latency.
- **Active braking**: commanded stop now regulates to zero (reverse torque ∝
  remaining speed) and releases below ~0.33 rad/s; the old coast-only
  behavior guarded against oscillation from the broken loop. Safety stops
  (command timeout, micro-ROS link loss) now brake instead of rolling out.
- **PWM 10 kHz → 21 kHz**: above audible, under the DC Motor Driver 2x15A
  Lite's 25 kHz cap; switching-loss caution scales with load current and our
  motors draw a few A against a 15 A/ch rating. (Residual noise was diagnosed
  as mechanical.)

## Drive stack (ros2_control / teleop)

- Teleop publishes to `/diff_drive_controller/cmd_vel_unstamped` (nothing
  ever subscribed to `/cmd_vel` after the ros2_control migration). Keys
  remapped: **w/a/s/d** drive, **q/e** fans, **r/t** belt (latched),
  **space** stops everything, u/j i/k o/l speed scaling.
- Accel limits tuned by feel: gentle launch 0.54 m/s² (1 s to max),
  **asymmetric braking −1.5 m/s²** so stops actually engage the firmware's
  active braking; `cmd_vel_timeout 0.5 → 0.25` (watch for held-key stutter
  vs OS auto-repeat initial delay — known trade-off).
- `enable_odom_tf` is overridden from the `ekf` launch flag (was a hand-edit
  footgun; with `ekf:=false` nothing published `odom→base_link` at all).
  *(Note: this auto-switch was in the wheel-only changeset — verify it
  survived the git restore on each machine.)*

## The IMU saga — root causes, in discovery order

1. depthai container crashed: `DEPTH` pipeline with all outputs disabled
   trips a device assert → `RGB` pipeline, IMU independent
   (`i_enable_imu`), `i_nn_type none`, `rectify_rgb:=false`.
2. Madgwick waited forever for `imu/mag`: params yaml keyed by bare node name
   doesn't match a namespaced node → `/**:`.
3. Madgwick waited forever for data: the driver publishes `/oak/imu/data`,
   not `/oak/imu`; and Madgwick's default output collides with the driver's
   raw topic → chain rewired to `data → (remap) → data_raw → Madgwick →
   /oak/imu/fused`.
4. OAK TF island: `parent_frame:=base_link` + `cam_pos_*` attach the camera
   tree; `oak_imu_frame`/`imu_link` provided for robot_localization.
5. EKF dropped IMU silently: `imu0_queue_size 10 → 100` (200 Hz vs 30 Hz
   filter on a loaded Nano); Humble's TF-lookup warnings are commented out
   upstream, so all of this fails silently.
6. **The real boss: the OAK-D is mounted ~58° from vertical** (looking at the
   floor). The gyro z-axis only carried cos(58°) ≈ 0.5 of the yaw rate — the
   mysterious "EKF reads 54% of every rotation" — and the sign flakiness was
   the same projection. Fix: `imu_remap` now **gravity-aligns at startup** —
   averages the accelerometer while still (~2 s), builds the minimal rotation
   taking measured "up" to +z, rotates all gyro/accel data through it. Logs
   `mount tilt = …` (measured 58.0°) and `gyro bias = …` as self-check.
   No hand-tuned signs, no hardcoded angle; remount the camera and it
   recalibrates next launch.
7. Startup gyro-bias subtraction kills the ~1°/min stationary drift; the
   remaining ~0.26°/min is bias instability (sensor physics — lidar layer
   absorbs it; optional ZUPT re-trim possible).

**Validation:** wheel geometry confirmed (−362° per real 360° slow turn,
2.00 m / 2.00 m straight); EKF after the tilt fix: −369° for a ~370° turn.
Fast pivots make wheel yaw over-read by up to ~25% (skid) — the gyro is now
the better yaw source at speed.

## Infrastructure & tooling

- **udev rules** (`docker/99-eyerobot-usb.rules`, measured IDs: CP2102 lidar
  `10c4:ea60`, CH340 ESP32 `1a86:7523`): stable `/dev/esp32` & `/dev/rplidar`,
  used by the agent command and `lidar_port` launch default. Guide: `UDEV.md`.
- **Foxglove**: bridge in the launch (`foxglove:=false` to disable),
  `urdf_relay` re-publishes at 1 Hz so late panels get the URDF, mesh
  resolution documented (`URDF.md`), `/wheel_path` + `/ekf_path` +
  `/pose2d_wheel` + `/pose2d_ekf` for trajectory comparison.
- **Multi-agent code review** → `ANALYSIS.md`: defect list with file:line
  (encoder reset/dropout clamp bug, async L/R feedback quantization, teleop
  timeout interaction, firmware transport error handling, anti-windup gap…),
  serial bandwidth budget (~55% at 115200; 50 Hz feedback needs 921600),
  package-choice verdicts, ranked action plan — **largely still TODO**.
- Cleanup: deleted `state_estimator_node.py`, `dual_odometry_node.py` (dead
  estimators superseded by ros2_control + EKF), `GUIDE.md` (documented the
  dead architecture), `new_urdf.zip`.

## Hard-won process lessons

- **Prove which code is running before debugging.** Three "fix didn't work"
  episodes were stale builds/launches (params load once at process start;
  PC↔Jetson sync via manual commit/pull; mixed `--symlink-install`/plain
  builds half-convert packages). Cheap proof: a log line only the new code
  prints (`mount tilt = …`), `git log -1` on both machines.
- Restart the micro-ROS agent after every ESP32 reflash (stale session =
  motors gated to zero = "you killed motor control").
- Replug the OAK-D after a depthai crash (half-booted XLink state hangs the
  next launch).
- When a scale factor is suspiciously close to cos(something), go look at
  the hardware.
