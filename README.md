# EyeRobot

This repository contains:

- `EyeRobot_MotorControl`: ESP32 firmware for five motors over micro-ROS.
- `ManualController`: ROS 2 Python package for keyboard driving and RViz odometry.

The current control split is:

- Belt, right wheel, left wheel: encoder speed PI control.
- Right fan, left fan: open-loop sign control.

## Safety First

Before testing with motor power connected:

1. Put the robot on blocks so the wheels and belt can spin freely.
2. Keep a physical motor-power switch reachable.
3. Start with low `command_speed_rad_s`.
4. Send stop commands before and after flashing:

```bash
ros2 topic pub --once /motor_rwheel_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_lwheel_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_belt_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_rfan_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_lfan_cmd std_msgs/msg/Float32 "{data: 0.0}"
```

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

This builds the local `micro_ros_msgs`, local `micro_ros_agent`, and `manual_controller` packages.

Do this again after editing ROS-side code.

## 3. One-Command Run

With the ESP32 flashed and connected over USB:

```bash
ros2 launch manual_controller manual_controller.launch.py
```

That starts:

- the micro-ROS serial agent
- the WASD keyboard controller
- RViz with the EyeRobot config

If your ESP32 is not on `/dev/ttyUSB0`, pass the serial device:

```bash
ros2 launch manual_controller manual_controller.launch.py serial_dev:=/dev/ttyACM0
```

If you want no RViz:

```bash
ros2 launch manual_controller manual_controller.launch.py rviz:=false
```

If the micro-ROS agent is already running in another terminal:

```bash
ros2 launch manual_controller manual_controller.launch.py micro_ros_agent:=false
```

Useful checks:

```bash
ros2 node list
ros2 topic list
ros2 topic echo /motor_rwheel_fb
```

You should see the firmware node as `eyerobot_node` once the agent is connected.

## 4. Drive With WASD And RViz

Main command:

```bash
ros2 launch manual_controller manual_controller.launch.py
```

If keyboard input is not captured through `ros2 launch`, run the controller directly in the focused terminal:

```bash
ros2 run manual_controller manual_controller
```

Then start RViz separately:

```bash
rviz2 -d install/manual_controller/share/manual_controller/rviz/eyerobot.rviz
```

Keyboard controls:

| Key | Action |
|---|---|
| Hold `w` | Forward |
| Hold `s` | Backward |
| Hold `a` | Pivot left |
| Hold `d` | Pivot right |
| `space` or `x` | Stop |
| `r` | Reset RViz odometry/path |
| `q` | Quit controller |

The controller is hold-to-run. If no key repeat arrives for `keyboard_timeout_s`, it publishes zero wheel commands.

## 5. Tune Runtime Parameters

Common launch parameters:

```bash
ros2 launch manual_controller manual_controller.launch.py \
  command_speed_rad_s:=4.0 \
  turn_speed_rad_s:=3.0 \
  wheel_radius_m:=0.035 \
  wheel_separation_m:=0.150
```

If a motor or encoder sign is inverted, fix it without changing firmware:

```bash
ros2 launch manual_controller manual_controller.launch.py \
  right_command_sign:=-1.0 \
  left_command_sign:=1.0 \
  right_feedback_sign:=-1.0 \
  left_feedback_sign:=1.0
```

Important parameters:

| Parameter | Default | Meaning |
|---|---:|---|
| `command_speed_rad_s` | `8.0` | Wheel speed setpoint for forward/backward |
| `turn_speed_rad_s` | `5.0` | Wheel speed setpoint for pivot turns |
| `keyboard_timeout_s` | `0.7` | Stop if no key repeat arrives |
| `feedback_timeout_s` | `0.5` | Treat stale wheel feedback as zero for odometry |
| `wheel_radius_m` | `0.035` | Used to convert wheel rad/s to linear speed |
| `wheel_separation_m` | `0.150` | Used to compute yaw rate |
| `right_command_sign` | `1.0` | Invert right motor command with `-1.0` |
| `left_command_sign` | `1.0` | Invert left motor command with `-1.0` |
| `right_feedback_sign` | `1.0` | Invert right encoder feedback with `-1.0` |
| `left_feedback_sign` | `1.0` | Invert left encoder feedback with `-1.0` |

## 6. Topics

Firmware command topics, host to ESP32:

| Topic | Type | Meaning |
|---|---|---|
| `/motor_belt_cmd` | `std_msgs/msg/Float32` | Belt speed setpoint in rad/s |
| `/motor_rwheel_cmd` | `std_msgs/msg/Float32` | Right wheel speed setpoint in rad/s |
| `/motor_lwheel_cmd` | `std_msgs/msg/Float32` | Left wheel speed setpoint in rad/s |
| `/motor_rfan_cmd` | `std_msgs/msg/Float32` | Right fan sign command |
| `/motor_lfan_cmd` | `std_msgs/msg/Float32` | Left fan sign command |

Firmware feedback topics, ESP32 to host:

| Topic | Type | Meaning |
|---|---|---|
| `/motor_belt_fb` | `std_msgs/msg/Int32` | Belt speed in mrad/s |
| `/motor_rwheel_fb` | `std_msgs/msg/Int32` | Right wheel speed in mrad/s |
| `/motor_lwheel_fb` | `std_msgs/msg/Int32` | Left wheel speed in mrad/s |
| `/motor_rfan_fb` | `std_msgs/msg/Int32` | Always zero, open-loop fan |
| `/motor_lfan_fb` | `std_msgs/msg/Int32` | Always zero, open-loop fan |

PC visualization topics:

| Topic | Type | Meaning |
|---|---|---|
| `/odom` | `nav_msgs/msg/Odometry` | Integrated wheel odometry |
| `/path` | `nav_msgs/msg/Path` | RViz trail |
| TF `odom -> base_link` | `tf2` | Robot pose for RViz |

## 7. Troubleshooting

If nothing appears in ROS:

```bash
ros2 node list
ros2 topic list
```

Check that the micro-ROS agent is running on the same serial port used by the ESP32.

If the robot moves but RViz goes backward:

- Try `right_feedback_sign:=-1.0` or `left_feedback_sign:=-1.0`.
- Press `r` in the controller terminal to reset odometry after changing signs.

If a wheel command moves the wrong wheel direction:

- Try `right_command_sign:=-1.0` or `left_command_sign:=-1.0`.

If a motor keeps moving after you release keys:

- Confirm the controller is still running and publishing zeros:

```bash
ros2 topic echo /motor_rwheel_cmd
ros2 topic echo /motor_lwheel_cmd
```

- The firmware also has a command watchdog; stale commands should time out after 500 ms.
- If the pin is low at the ESP32 but the motor still drives, inspect the motor driver input semantics and wiring.

## More Details

Firmware architecture details are in `EyeRobot_MotorControl/DOCS.md`.
