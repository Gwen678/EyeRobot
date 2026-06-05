# EyeRobot

This repository contains:

- `EyeRobot_MotorControl`: ESP32 firmware for five motors over micro-ROS.
- `ManualController`: ROS 2 Python package for keyboard driving and RViz odometry.
- `URDF` (`robot_description`): xacro + meshes for the RViz robot model.

## Control Mode

| Motor | Mode |
|---|---|
| Right wheel | Encoder PI speed (closed-loop) |
| Left wheel | Encoder PI speed (closed-loop) |
| Belt | Open-loop sign, full duty |
| Right fan | Open-loop sign, full duty |
| Left fan | Open-loop sign, full duty |

Each command is a `Float32` in rad/s. For the **wheels**, that value is a real
speed setpoint the closed-loop PI controller tracks from the encoder feedback
(`kKp = 0.03`, `kKi = 0.005` with anti-windup, in `MotorTask.cpp`); the wheels
top out around `10.7 rad/s`. For the **belt and fans** (no encoder) only the
**sign** matters: any magnitude past the `0.5 rad/s` deadband runs them at full
duty in that direction.

## Safety First

Before testing with motor power connected:

1. Put the robot on blocks so the wheels and belt can spin freely.
2. Keep a physical motor-power switch reachable.
3. Send stop commands before and after flashing:

```bash
ros2 topic pub --once /motor_rwheel_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_lwheel_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_belt_cmd  std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_rfan_cmd  std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_lfan_cmd  std_msgs/msg/Float32 "{data: 0.0}"
```

Note: open-loop motors run at full power for any out-of-deadband command, so
keep clear of the wheels, belt, and fans while testing.

## 1. Flash The ESP32

From the firmware directory:

```bash
cd EyeRobot_MotorControl
pio run
pio run --target upload --upload-port /dev/ttyUSB0
```

Adjust `/dev/ttyUSB0` if your ESP32 appears on another port.

## 2. Build The ROS Workspace

From the repository root:

```bash
git submodule update --init --recursive
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

This builds the local `micro_ros_msgs`, local `micro_ros_agent`,
`robot_description`, and `manual_controller` packages.

Do this again after editing ROS-side code.

## 3. One-Command Run

With the ESP32 flashed and connected over USB, from the repository root:

```bash
./run_eyerobot.sh
```

That opens **three terminal windows**, each running one part of the stack:

1. the micro-ROS serial agent (`/dev/ttyUSB0` @ 115200)
2. the keyboard teleop (click this window and drive)
3. the odometry + URDF + RViz window (`state_estimator` +
   `robot_state_publisher` + `joint_state_publisher` + RViz together)

If your ESP32 is on another port, pass it:

```bash
./run_eyerobot.sh /dev/ttyACM0
```

To log raw encoder deltas in the odometry window (for diagnosing odometry):

```bash
DEBUG_ENCODERS=true ./run_eyerobot.sh
```

Useful checks:

```bash
ros2 node list
ros2 topic list
ros2 topic echo /motor_rwheel_fb
```

You should see the firmware node as `eyerobot_node` once the agent connects.

## 4. Drive With The Keyboard

Run the teleop node in a focused terminal (it reads raw keypresses):

```bash
ros2 run manual_controller manual_controller
```

Keyboard controls:

| Key | Action | Behaviour |
|---|---|---|
| Hold `w` | Forward | Momentary (held to run) |
| Hold `s` | Backward | Momentary |
| Hold `a` | Pivot left | Momentary |
| Hold `d` | Pivot right | Momentary |
| Tap `q` | Fans on `>` | Latched (tap again to stop) |
| Tap `e` | Fans reverse `<` | Latched |
| Tap `r` | Belt forward `+` | Latched |
| Tap `t` | Belt reverse `-` | Latched |
| `space` or `x` | Stop all | — |
| `ctrl-c` | Quit | — |

Wheels are **momentary**: they stop ~`release_timeout_s` (default 0.2 s) after
the key stops auto-repeating. Fans and belt are **latched**: they keep running
until you tap their key again or hit stop. The fans are mechanically coupled to
spin opposite each other, so a single `q`/`e` tap drives both.

If you want the visualization without the launch script, start RViz separately:

```bash
rviz2 -d install/manual_controller/share/manual_controller/rviz/eyerobot.rviz
```

## 5. Tune Runtime Parameters

Common teleop / odometry parameters:

```bash
ros2 run manual_controller manual_controller --ros-args \
  -p command_speed_rad_s:=10.0 \
  -p turn_speed_rad_s:=5.0 \
  -p fan_command_rad_s:=8.0 \
  -p belt_command_rad_s:=8.0

ros2 run manual_controller state_estimator --ros-args \
  -p wheel_radius_m:=0.06 \
  -p wheel_separation_m:=0.150 \
  -p counts_per_output_rev:=5756.0
```

For the **wheels** (closed-loop PI) the `command_speed_rad_s` / `turn_speed_rad_s`
magnitude is the real speed setpoint in rad/s (cap ~`10.7`). For the **belt and
fans** (open-loop sign) the `*_command_rad_s` magnitude only needs to clear the
`0.5 rad/s` deadband — sign picks direction, magnitude does not set speed.

If a motor or encoder sign is inverted, fix it without changing firmware:

```bash
ros2 run manual_controller manual_controller --ros-args \
  -p right_command_sign:=-1.0 -p left_command_sign:=1.0

ros2 run manual_controller state_estimator --ros-args \
  -p right_feedback_sign:=-1.0 -p left_feedback_sign:=1.0
```

Important parameters:

| Parameter | Node | Default | Meaning |
|---|---|---:|---|
| `command_speed_rad_s` | teleop | `10.0` | Forward/backward wheel speed setpoint (rad/s) |
| `turn_speed_rad_s` | teleop | `5.0` | Pivot-turn command magnitude |
| `fan_command_rad_s` | teleop | `8.0` | Fan command magnitude (`q`/`e`) |
| `belt_command_rad_s` | teleop | `8.0` | Belt command magnitude (`r`/`t`) |
| `command_rate_hz` | teleop | `20.0` | Fixed command publish rate |
| `release_timeout_s` | teleop | `0.2` | Stop wheels if no key repeat arrives |
| `right_command_sign` | teleop | `1.0` | Host command polarity (signs fixed on the MCU; keep +1) |
| `left_command_sign` | teleop | `1.0` | Host command polarity (signs fixed on the MCU; keep +1) |
| `wheel_radius_m` | estimator | `0.06` | Wheel radius for odometry |
| `wheel_separation_m` | estimator | `0.150` | Track width for yaw rate |
| `counts_per_output_rev` | estimator | `5756.0` | Encoder counts per wheel revolution |
| `right_feedback_sign` | estimator | `1.0` | Invert right encoder feedback |
| `left_feedback_sign` | estimator | `1.0` | Invert left encoder feedback |

Encoder polarity is corrected in firmware (`MotorConfig::invert_encoder`), so
the feedback signs normally stay `+1.0`; flip one only for ad-hoc host testing.

## 6. Topics

Firmware command topics, host to ESP32 (`std_msgs/msg/Float32`):

| Topic | Meaning |
|---|---|
| `/motor_belt_cmd` | Belt direction (sign-only) |
| `/motor_rwheel_cmd` | Right wheel speed setpoint, rad/s (closed-loop PI) |
| `/motor_lwheel_cmd` | Left wheel speed setpoint, rad/s (closed-loop PI) |
| `/motor_rfan_cmd` | Right fan direction (sign-only) |
| `/motor_lfan_cmd` | Left fan direction (sign-only) |

Firmware tick feedback topics, ESP32 to host (`std_msgs/msg/Int32`):

| Topic | Meaning |
|---|---|
| `/motor_rwheel_fb` | Right wheel accumulated encoder ticks |
| `/motor_lwheel_fb` | Left wheel accumulated encoder ticks |
| `/motor_belt_fb` | Always 0 (no encoder) |
| `/motor_rfan_fb` | Always 0 (no encoder) |
| `/motor_lfan_fb` | Always 0 (no encoder) |

Firmware speed feedback topics, ESP32 to host (`std_msgs/msg/Float32`, rad/s):

| Topic | Meaning |
|---|---|
| `/motor_rwheel_speed` | Right wheel measured speed (rad/s) |
| `/motor_lwheel_speed` | Left wheel measured speed (rad/s) |
| `/motor_belt_speed` | Always 0 (no encoder) |
| `/motor_rfan_speed` | Always 0 (no encoder) |
| `/motor_lfan_speed` | Always 0 (no encoder) |

The state estimator integrates the **raw accumulated wheel tick counts** into
distance (exact position, no speed-integration drift). The `*_speed` topics
expose the firmware's encoder speed estimate in rad/s — the same measurement the
wheel PI regulates, handy for confirming the loop tracks the commanded setpoint
(`ros2 topic echo /motor_rwheel_speed --qos-reliability best_effort`).

PC visualization topics:

| Topic | Type | Meaning |
|---|---|---|
| `/odom` | `nav_msgs/msg/Odometry` | Integrated wheel odometry |
| `/path` | `nav_msgs/msg/Path` | RViz trail |
| TF `odom -> base_link` | `tf2` | Robot pose for RViz |

## 7. Cleanup

If `ros2 launch`/RViz/teleop orphan processes survive a crash:

```bash
./kill_eyerobot.sh
```

## 8. Troubleshooting

If nothing appears in ROS:

```bash
ros2 node list
ros2 topic list
```

Check that the micro-ROS agent is running on the same serial port as the ESP32.

If the robot moves but RViz goes backward:

- Try `right_feedback_sign:=-1.0` or `left_feedback_sign:=-1.0` on the estimator.
- Call the reset service after changing signs:
  `ros2 service call /reset_odometry std_srvs/srv/Empty`.

If a wheel command moves the wrong wheel direction:

- Try `right_command_sign:=-1.0` or `left_command_sign:=-1.0` on the teleop.

If a motor keeps moving after you release keys:

- Confirm the teleop is still running and publishing zeros:
  `ros2 topic echo /motor_rwheel_cmd`.
- The firmware has a 500 ms command watchdog; stale commands time out and stop.

## More Details

Firmware architecture details are in `EyeRobot_MotorControl/DOCS.md`.
