# EyeRobot — codebase analysis (2026-06-10)

Multi-agent review of architecture, implementation, integration, and package
choices. Four parallel analyses: ESP32 firmware, ros2_control integration,
ROS nodes & configs, system architecture. Findings verified against source
with file:line references; severity reflects impact on the robot as deployed.

---

## Mysteries resolved

### Why the π-rolled IMU frame didn't flip EKF yaw

robot_localization (Humble) **does** rotate IMU angular velocity by the
sensor→base_link TF — `prepareTwist` applies
`target_frame_trans.getBasis() × ω` (verified in upstream `ros_filter.cpp`).
The observed non-flip means the transform looked up was not the rolled one:
either the IMU messages' `frame_id` was not actually `oak_imu_frame`, or it
was empty (resolves to identity). Humble has every warning in
`lookupTransformSafe` **commented out**, so all of this fails silently.
The current design — fixing signs in `imu_remap_node` and stamping `imu_link`
(rpy 0) — is sound and more debuggable. Keep data convention and URDF in sync
manually.

### wheel_separation: yaml 0.33 vs URDF 0.293

`Robot.xacro` places the wheels at Y=±0.146 (0.293 m track);
`diff_drive_controller.yaml:17` uses 0.33. The hardware rotation test
(−362° wheel-odom for a real 360°) validates **0.33** — the URDF axle
placement is what's wrong. Cosmetic until someone trusts the model geometry.

---

## High-severity defects

1. **Encoder reset/dropout handling inverted** — `eyerobot_hardware.cpp:185-194`.
   `prev_*` is committed *before* the plausibility check, so rejected jumps
   permanently delete distance (any feedback dropout >~3.5 s while driving).
   Conversely a firmware reboot from <28,780 accumulated counts (≈1.88 m)
   *passes* the clamp: a reset from +20,000 injects a 1.3 m phantom jump and a
   one-cycle ~1,090 rad/s velocity spike into `/diff_drive_controller/odom`,
   which the EKF fuses. Reboot (re-baseline) and dropout (integrate fully)
   need opposite handling; one heuristic currently covers both, wrongly.

2. **Default launch publishes no `odom→base_link`** —
   `diff_drive_controller.yaml` has `enable_odom_tf: false` (EKF owns the TF)
   but `ekf` defaults to `false` in both launch files. A bare
   `eyerobot.launch.py` has a hole in the TF tree; RViz/SLAM/Nav2 silently
   break. Fix: default `ekf:=true`, or tie `enable_odom_tf` to the flag.

3. **Async L/R feedback artifact, quantified** — firmware publishes both
   wheels in one 10 Hz tick (`MicroRosTask.cpp:43-62`) but they arrive as
   separate messages; the 50 Hz `read()` straddles the pair several times per
   second. Effect: zero-mean yaw kicks of ±0.30·v rad (±5.2° at 0.3 m/s) on
   wheel odom, and wheel velocity quantized 0/0/0/0/5× (counts at 10 Hz
   differenced with dt=20 ms). EKF yaw is immune by config (fuses only IMU
   vyaw); EKF vx is polluted. Fix: gate integration on a fresh L+R pair and
   compute velocity over the true inter-pair interval; later, a single paired
   firmware message kills it at the source. The firmware's per-wheel measured
   `speed_rads` topics are a ready-made better velocity source the plugin
   currently ignores.

4. **Held-key teleop fights `cmd_vel_timeout: 0.25`** — teleop publishes only
   on key events (`manual_controller_node.py`, blocking `getKey`), and the OS
   auto-repeat *initial delay* (typically 0.4–0.66 s) exceeds the timeout:
   every press-and-hold gets halt → brake → resume. Fix: re-publish the last
   command on a 10–20 Hz timer (the `teleop_twist_joy` pattern).

5. **Firmware serial transport error handling** —
   `esp32_serial_transport.c:25-53`. UART init checked with `== ESP_FAIL`
   (misses `ESP_ERR_NO_MEM` etc. → session runs over an unconfigured UART),
   and `uart_write_bytes`/`uart_read_bytes` returning −1 is cast to `size_t`
   (~SIZE_MAX) and handed to the XRCE framing layer. The only found paths that
   can silently corrupt the whole link. Fix: `!= ESP_OK`, clamp negatives to 0.

6. **`block_tracker` is dead-on-arrival** — three independent breaks:
   `dai.Device()` raises because `depthai_ros_driver` holds the OAK
   exclusively (driver now starts unconditionally); it publishes raw
   `/motor_*wheel_cmd` which ros2_control overwrites with zeros at 50 Hz; and
   it projects from a `camera_link` frame that doesn't exist (error swallowed
   by a bare `except`). Needs porting to `cmd_vel_unstamped` + `/oak/...`
   topics, or deletion.

## Medium severity

- **PI anti-windup is unaware of feedforward** (`MotorTask.cpp` /
  `PiController.cpp`): the integral clamp bounds the integral term alone, but
  the actuator output is FF+PI clamped to ±100 — the integral can wind fully
  while the output is railed. Guaranteed by `kDefaultMaxCmdRads = 20` >
  ~11 rad/s free speed. Fix: freeze integration when |FF+PI| saturates; cap
  `max_cmd_rads` near 10.
- **Direction-flip integral reset never fires through stop** —
  `setpoint·prev < 0` is false when a `+ → 0 → −` transition passes a stop
  sample (which teleop ramps always produce). Track the last *moving*
  setpoint's sign instead.
- **`measured_tps` assumes exactly 10 ms** — a missed deadline produces a
  near-zero then spiked velocity estimate injected into the PI. Use measured
  elapsed time.
- **Active braking is unlimited plug reversal** — full-speed stop steps PWM
  +100→−100 in one cycle (~2× stall current). Works, but a duty slew limit
  would be kind to the driver.
- **Hardware plugin lifecycle** — no destructor/`on_shutdown` joins
  `spin_thread_` (unclean exit → `std::terminate`); `read()` returns OK
  forever after firmware death (should return ERROR after a staleness timeout
  so controller_manager executes its safety stop).
- **`urdf_relay` published once at startup** — VOLATILE has no replay, so
  late-joining Foxglove panels got nothing. (Fixed 2026-06-10: 1 Hz
  re-publish.)
- **Topics-as-hardware-transport bypass** — anything on the graph can publish
  `motor_*_cmd` directly, skipping the diff_drive limiter and timeout; only
  the firmware's 500 ms timeout and ±20 rad/s clamp remain. Acceptable for a
  lab robot; do not ship.
- **micro-ROS agent is manual** — separate terminal, no respawn; agent death
  stops the robot (firmware gates correctly) but recovery is by hand. Put it
  in the launch with `respawn:=true`.

## Serial bandwidth (115200 baud)

≈11.5 KB/s usable; current load ≈5.5–6.5 KB/s (~55%): 10 Hz × 5 motors ×
(ticks+speed) feedback ≈2.4 KB/s, 50 Hz × 2 reliable wheel commands ≈3.2 KB/s
with ACK overhead. The correct fix for the feedback-rate mismatch (10→50 Hz)
adds ~9.6 KB/s and **does not fit** — raise the UART to 921600 first. The five
`*_speed` publishers (unused by the host today, always 0 for fans/belt) burn
~1.2 KB/s.

## Package-choice verdicts

| Choice | Verdict |
|---|---|
| micro-ROS over serial | **Keep** (debugged; raise baud rather than replace — a custom framed protocol would halve overhead but costs a working subsystem) |
| ros2_control + diff_drive_controller | **Keep** — odometry, limits, timeout, Nav2-standard interface, all config-driven; the custom predecessors are the proof of the alternative's cost |
| robot_localization EKF | **Keep, barely** — with vx+vyaw only it's ≈ gyro integration + projection; now that it's tuned, keep; don't add fused states |
| imu_filter_madgwick | **Keep** — the EKF only uses the angular velocity it passes through (its yaw is redundant gyro integration, and `two_d_mode` discards roll/pitch), BUT a planned ramp-finished detector will consume its pitch: Madgwick's gravity-referenced, transient-immune pitch is exactly the right signal to threshold (raw accel is most contaminated precisely while cresting the ramp). Verify pitch sign/axis on the real ramp once |
| depthai_ros_driver (IMU-only use) | **Replace eventually** with a small depthai-SDK node publishing IMU + frames — the driver locks the OAK exclusively, blocking all of `perception/` |
| slam_toolbox | **Keep** (maintained, apt, async degrades gracefully on the Nano; cartographer is unmaintained) |
| Docker on Nano | **Keep** — JetPack 4 can't run Humble natively; GPU unusable in the 22.04 container, accepted consciously |

## Layering of velocity limits

Sound separation overall: teleop = user intent, diff_drive = capability
envelope + smoothing, firmware = actuator physics (breakaway FF, PI,
min-speed floor). One genuine leak: the firmware's 1.0 rad/s min-speed floor
overrides the bottom of the host accel ramp, so true acceleration exceeds the
limiter's promise at launch and commanded-vs-actual consistency breaks at low
speed. Document it in `diff_drive_controller.yaml` (or mirror it as the
controller's min velocity).

## Hygiene

- `state_estimator_node.py` + `dual_odometry_node.py`: 800+ lines of dead
  code with live footguns (`publish_tf` default true fights the EKF;
  `/odometry/filtered` squatting; best-effort pubs incompatible with default
  subscribers). Delete, with their `setup.py` entry points.
- `GUIDE.md` documents the deleted architecture (oak_imu, dual_odometry).
- Stale on-disk `install/` trees contain deleted packages (`oak_imu`, old
  `rplidar_ros` with old-style launch names) — confusing if ever sourced.
- `imu_filter.yaml` sets three parameters Humble's Madgwick doesn't declare
  (silently ignored), and its header misstates the remap wiring.
- Stale comments: firmware "20 kHz" (now 21), "teleop re-sends at 20 Hz"
  (now controller_manager at 50), main.cpp claims fans/belt tasks disabled
  (all five run), lidar "centered" comment vs actual 0.28 m offset.
- Binary clutter at repo root (`yolov8n.pt`, `new_urdf.zip`).

## Action plan (ranked)

1. **Fresh-pair gating + clamp reorder** in `eyerobot_hardware` — biggest
   odometry accuracy win; host-only, no reflash.
2. **Teleop publish timer + default `ekf:=true`** — drivability + TF hole.
3. **Firmware batch** (one reflash): transport `!= ESP_OK` + clamped returns,
   output-aware anti-windup + `max_cmd_rads ≈ 10`, direction-flip reset via
   last-moving-sign, measured-dt velocity.
4. **921600 baud + 50 Hz paired feedback + delete `*_speed` publishers** —
   fixes the rate mismatch at the source (firmware + agent flag).
5. **Dead-code/docs sweep** — delete legacy estimators + `GUIDE.md`, fix stale
   comments, reconcile URDF wheel placement with the measured 0.33 m track.
6. **Ramp-finished detector** (future): small node subscribing to
   `/oak/imu/fused`, pitch = asin(2(qw·qy − qx·qz)), hysteresis + hold time →
   `ramp_state` bool. This is the consumer that justifies keeping Madgwick.
