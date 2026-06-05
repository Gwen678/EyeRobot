# EyeRobot Motor Control Firmware

ESP32 firmware for the EyeRobot motor board. It drives five brushed DC motors and exposes commands and feedback over micro-ROS through USB serial.

## Control Mode

| Motor | Mode |
|---|---|
| Right wheel | Encoder PI speed (closed-loop) |
| Left wheel | Encoder PI speed (closed-loop) |
| Belt | Open-loop sign, 100% duty |
| Right fan | Open-loop sign, 100% duty |
| Left fan | Open-loop sign, 100% duty |

The **wheels run closed-loop PI** on the encoder speed: the commanded rad/s is a
real setpoint the controller tracks using the measured wheel speed
(`measured_tps`). Gains are `kKp = 0.03`, `kKi = 0.005` with integrator
anti-windup (`MotorTask.cpp` / `PiController.cpp`); the wheels top out near
`10.7 rad/s`. Mode is selected per motor via `MotorConfig::mode` in `AppBus.hpp`
(`ClosedLoopSpeed` for the wheels, `OpenLoopSign` for the belt and fans).

The **belt and fans run open-loop sign control** at full duty: they have no
encoder, so a command's sign picks the direction and any magnitude past the
`0.5 rad/s` deadband runs them flat-out.

The PC-side teleop / RViz workflow is documented in the repository root `README.md`.

## Architecture

```text
app_main
├── force_motor_outputs_low()   // pull all 10 PWM/DIR lines low before anything else
├── MotorTask x 5
│   ├── owns MotorController
│   ├── owns Encoder (wheels only; PI feedback + telemetry)
│   └── owns PiController (wheels only; closed-loop speed)
├── MicroRosTask
│   ├── subscribes to motor_*_cmd   (Float32, wheel setpoint / belt+fan sign)
│   ├── publishes  motor_*_fb        (Int32, accumulated ticks)
│   └── publishes  motor_*_speed     (Float32, measured rad/s)
└── AppBus
    ├── to_motor[id]    latest MotorCmd
    ├── from_motor[id]  latest MotorFeedback
    └── link_up         micro-ROS link state (motor safety gate)
```

Key design points:

- Control mode is explicit in `MotorConfig::mode` (`ClosedLoopSpeed` for the two
  wheels, `OpenLoopSign` for the belt and fans).
- Commands use latest-value semantics, not FIFO backlog. A stop command cannot
  sit behind older movement commands.
- Every motor has a 500 ms command watchdog. If commands go stale, the motor stops.
- A `link_up` safety gate (in `AppBus`) holds every motor at 0 whenever the
  micro-ROS agent link is not fully established — at boot before the first
  connection and throughout any reconnect. It defaults to false and is set true
  only after a successful entity setup, so a powered-but-disconnected ESP stays
  still. This decouples motor safety from the (blocking) reconnect loop.
- Open-loop control applies a `0.5 rad/s` deadband so a single corrupted
  best-effort sample cannot become a full-power twitch.
- Firmware drives all configured motor PWM/DIR pins low at the start of
  `app_main()`, before any task or micro-ROS entity is created.

## Files

```text
include/
  pins.hpp              GPIO assignments
  AppBus.hpp            Motor IDs, motor configs, bus messages
  Channel.hpp           FreeRTOS queue wrapper with latest-value helpers
  MotorController.hpp   PWM + direction motor driver
  Encoder.hpp           ESP-IDF PCNT quadrature encoder
  PiController.hpp      PI controller with anti-windup (drives the wheels)
  MotorTask.hpp         Per-motor control task
  MicroRosTask.hpp      micro-ROS task
  Thread.hpp            FreeRTOS task base class

src/
  main.cpp
  MotorController.cpp
  Encoder.cpp
  PiController.cpp
  MotorTask.cpp
  MicroRosTask.cpp
  Thread.cpp
  esp32_serial_transport.c/h
```

## GPIO Map

All pin definitions live in `include/pins.hpp`. LEDC channels are assigned in
`AppBus.hpp` (one channel per motor, all sharing `LEDC_TIMER_0`).

| Motor | PWM GPIO | DIR GPIO | ENC A GPIO | ENC B GPIO | LEDC ch |
|---|---:|---:|---:|---:|---:|
| Belt        | 5  | 18 | -  | -  | 2 |
| Right wheel | 22 | 23 | 32 | 4  | 0 |
| Left wheel  | 19 | 21 | 33 | 25 | 1 |
| Right fan   | 14 | 13 | -  | -  | 3 |
| Left fan    | 26 | 27 | -  | -  | 4 |

PWM uses LEDC at 20 kHz with 10-bit duty resolution.

The two wheel **motor** harnesses were cross-wired left↔right, so `pins.hpp`
swaps the wheels' PWM/DIR pins (right motor on 22/23, left on 19/21) while the
**encoder** pins stay on their original wheels (right 32/4, left 33/25).

Per-wheel polarity is then corrected in `kMotorConfigs`: the **left wheel** sets
`invert_motor = true` (otherwise its motor drives backward for a positive
command); both wheels keep `invert_encoder = false` (each encoder already counts
up on forward motion). `invert_motor` is applied *after* the PI, so the loop runs
in a clean `+command = forward`, `+measured = forward` frame (negative feedback)
and only the final actuator step accounts for wiring polarity.

## Motor Configuration

`include/AppBus.hpp` is the single source of truth for motor behavior:

```cpp
enum class MotorControlMode : uint8_t {
    ClosedLoopSpeed,   // the two wheels (encoder PI)
    OpenLoopSign,      // belt + two fans
};

struct MotorConfig {
    MotorID        id;
    MotorControlMode mode;
    const char*    fb_topic;       // Int32 accumulated ticks
    const char*    speed_topic;    // Float32 measured rad/s
    const char*    cmd_topic;      // Float32 command
    gpio_num_t     pwm_pin;
    gpio_num_t     dir_pin;
    ledc_channel_t ledc_channel;
    int            enc_a;
    int            enc_b;
    float          max_cmd_rads;
    float          open_loop_duty_percent;
    uint32_t       command_timeout_ms;
    bool           invert_encoder;  // negate encoder count (forward reads +)
    bool           invert_motor;    // negate duty after PI (+command = forward)
};
```

Encoder-less motors (belt, fans) use `enc_a = 0`, `enc_b = 0` as the
"no encoder" sentinel. The wheels read their encoders both for the PI feedback
and for the tick/speed feedback topics.

## Command And Feedback Bus

`Channel<T, N>` wraps a FreeRTOS queue. Motor control uses the latest-value helpers:

| Method | Purpose |
|---|---|
| `sendLatest(msg)` | Enqueue newest data; if full, drop stale queued data first |
| `receiveLatest(msg, timeout)` | Receive one item, drain newer pending items, return newest |

This matters for safety: a stop command should not wait behind older motion commands.

## MotorTask

Runs every 10 ms.

```text
receiveLatest command
sanitize command (reject NaN/Inf, clamp to max_cmd_rads)
if command timed out (500 ms) or micro-ROS link down: held command = 0

if has encoder (wheels):
    read PCNT count (negate if invert_encoder)
    measured_tps = (ticks - prev_ticks) / dt
    fb.ticks = ticks; fb.speed_rads = measured_tps / kTicksPerRad

closed-loop wheels (ClosedLoopSpeed):
    setpoint_tps = command_rads * kTicksPerRad
    near-zero setpoint -> hard stop (coast) + reset integrator
    else duty = pi.update(setpoint_tps, measured_tps, dt)

open-loop belt/fans (OpenLoopSign):
    cmd >  +0.5 rad/s -> +100% duty
    cmd <  -0.5 rad/s -> -100% duty
    otherwise         -> stop

if invert_motor: duty = -duty
setSpeed(duty) or stop
sendLatest feedback
```

The PI runs in the command frame (`+command`/`+measured`), and `invert_motor` is
applied only to the final duty — so wiring polarity never leaks into the loop.

## MotorController

`MotorController` owns one PWM pin, one direction pin, and one LEDC channel.

Important behavior:

- `init()` drives PWM and DIR low before configuring LEDC, and serializes the
  shared-timer/channel setup across the five tasks with a mutex (concurrent
  `ledc_*_config` calls could leave a channel at a stale non-zero duty).
- `stop()` sets PWM duty directly to zero (the driver gates output on PWM, so
  duty 0 stops regardless of DIR); DIR is left untouched.
- `setSpeed(speed)` accepts a duty percentage in `[-100, 100]`: positive sets
  DIR forward, negative sets DIR backward, both at the commanded magnitude.

The firmware can only control pins after the ESP32 has booted far enough to run
application code. Hardware pulldowns or motor-driver enable/standby gating remain
the robust way to guarantee no reset-time motion.

## Encoder

`Encoder` uses the ESP-IDF PCNT peripheral for 4x quadrature counting (wheels only).

Constants in `include/Encoder.hpp`:

| Constant | Value | Meaning |
|---|---:|---|
| `kCprMotor` | 16 | Encoder pulses per motor-shaft revolution |
| `kGearRatio` | 90 | Gearbox reduction |
| `kCprOutput` | 1440 | Pulses per output revolution |
| `kTicksPerRev` | 5756 | Calibrated 4x-quadrature ticks per output revolution |
| `kTicksPerRad` | ≈916 | Ticks per output radian |

Both the firmware (`kTicksPerRev`) and the host estimator
(`counts_per_output_rev`, default `5756`) use the same calibrated value — the
nominal 16 × 90 × 4 = 5760 reads a few counts high. The firmware uses it to turn
encoder ticks into the `measured_tps` / `speed_rads` the wheel PI regulates; the
host integrates the raw tick counts for odometry.

If odometry direction is wrong in RViz, prefer the host-side feedback-sign
parameters before changing encoder code:

```bash
ros2 run manual_controller state_estimator --ros-args -p right_feedback_sign:=-1.0
```

## micro-ROS Interface

Node name:

```text
eyerobot_node
```

Command topics, host to ESP32 (`std_msgs/msg/Float32`):

| Topic | Meaning |
|---|---|
| `/motor_belt_cmd` | Belt direction (sign-only) |
| `/motor_rwheel_cmd` | Right wheel speed setpoint, rad/s (closed-loop PI) |
| `/motor_lwheel_cmd` | Left wheel speed setpoint, rad/s (closed-loop PI) |
| `/motor_rfan_cmd` | Right fan direction (sign-only) |
| `/motor_lfan_cmd` | Left fan direction (sign-only) |

Tick feedback topics, ESP32 to host (`std_msgs/msg/Int32`, accumulated ticks):

| Topic | Meaning |
|---|---|
| `/motor_rwheel_fb` | Right wheel accumulated encoder ticks |
| `/motor_lwheel_fb` | Left wheel accumulated encoder ticks |
| `/motor_belt_fb` | Always 0 (no encoder) |
| `/motor_rfan_fb` | Always 0 (no encoder) |
| `/motor_lfan_fb` | Always 0 (no encoder) |

Speed feedback topics, ESP32 to host (`std_msgs/msg/Float32`, rad/s):

| Topic | Meaning |
|---|---|
| `/motor_rwheel_speed` | Right wheel measured speed (rad/s) |
| `/motor_lwheel_speed` | Left wheel measured speed (rad/s) |
| `/motor_belt_speed` | Always 0 (no encoder) |
| `/motor_rfan_speed` | Always 0 (no encoder) |
| `/motor_lfan_speed` | Always 0 (no encoder) |

The speed topics carry the firmware's encoder speed estimate
(`fb.speed_rads = measured_tps / kTicksPerRad`) — the same measurement the wheel
PI regulates. Echo one (best-effort QoS) to confirm the loop tracks the
commanded setpoint:
`ros2 topic echo /motor_rwheel_speed --qos-reliability best_effort`.

All publishers and subscribers use **best-effort** QoS: a single shared UART
carries both the high-rate telemetry and the command stream, and reliable QoS
added ACK traffic / head-of-line stalls that starved the command path. The
firmware now creates **10 publishers** (5 tick + 5 speed) and **5 subscribers**.
Micro-XRCE-DDS needs the configured max set to N+1 to use N reliably, so
`RMW_UXRCE_MAX_PUBLISHERS` is **12** (`RMW_UXRCE_MAX_SUBSCRIPTIONS` stays 6) in
`components/micro_ros_espidf_component/colcon.meta`. That limit is baked into the
prebuilt `libmicroros.a` — after changing it, force a library regen (delete
`libmicroros.a` + `include` + `micro_ros_src/.install_built`, then
`pio run -t fullclean && pio run`).

Start the agent on the host:

```bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
```

## Build And Flash

From `EyeRobot_MotorControl`:

```bash
pio run
pio run --target upload --upload-port /dev/ttyUSB0
pio device monitor
```

Requirements:

- PlatformIO
- `espressif32 @ 6.7.0`
- ESP-IDF 5.2.x from PlatformIO
- micro-ROS ESP-IDF component under `components/`

## Manual Stop Commands

Useful during bring-up:

```bash
ros2 topic pub --once /motor_belt_cmd   std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_rwheel_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_lwheel_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_rfan_cmd   std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_lfan_cmd   std_msgs/msg/Float32 "{data: 0.0}"
```
