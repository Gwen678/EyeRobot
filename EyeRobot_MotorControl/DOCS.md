# EyeRobot Motor Control Firmware

ESP32 firmware for the EyeRobot motor board. It drives five brushed DC motors and exposes commands and feedback over micro-ROS through USB serial.

Current control modes:

| Motor | Mode |
|---|---|
| Belt | Encoder PI speed control |
| Right wheel | Encoder PI speed control |
| Left wheel | Encoder PI speed control |
| Right fan | Open-loop sign control |
| Left fan | Open-loop sign control |

The PC-side WASD/RViz workflow is documented in the repository root `README.md`.

## Architecture

```text
app_main
├── force_motor_outputs_low()
├── MotorTask x 5
│   ├── owns MotorController
│   ├── owns Encoder for closed-loop motors
│   └── owns PiController for closed-loop motors
├── MicroRosTask
│   ├── subscribes to motor_*_cmd
│   └── publishes motor_*_fb
└── AppBus
    ├── to_motor[id]    latest MotorCmd
    └── from_motor[id]  latest MotorFeedback
```

Key design points:

- Control mode is explicit in `MotorConfig::mode`.
- Commands use latest-value semantics, not FIFO backlog.
- A stop command cannot sit behind older movement commands.
- Every motor has a command watchdog. If commands go stale, the motor stops.
- Closed-loop zero setpoint is a hard stop, not PI regulation around zero.
- Firmware drives all configured motor PWM/DIR pins low at the start of `app_main()`.

## Files

```text
include/
  pins.hpp              GPIO assignments
  AppBus.hpp            Motor IDs, motor configs, bus messages
  Channel.hpp           FreeRTOS queue wrapper with latest-value helpers
  MotorController.hpp   PWM + direction motor driver
  Encoder.hpp           ESP-IDF PCNT quadrature encoder
  PiController.hpp      PI controller with anti-windup
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

All pin definitions live in `include/pins.hpp`.

| Motor | PWM GPIO | DIR GPIO | ENC A GPIO | ENC B GPIO |
|---|---:|---:|---:|---:|
| Belt | 22 | 23 | 12 | 14 |
| Right wheel | 4 | 16 | 15 | 2 |
| Left wheel | 19 | 21 | 5 | 18 |
| Right fan | 27 | 26 | - | - |
| Left fan | 25 | 33 | - | - |

PWM uses LEDC at 20 kHz with 10-bit duty resolution.

## Motor Configuration

`include/AppBus.hpp` is the single source of truth for motor behavior:

```cpp
enum class MotorControlMode : uint8_t {
    ClosedLoopSpeed,
    OpenLoopSign,
};

struct MotorConfig {
    MotorID id;
    MotorControlMode mode;
    const char* fb_topic;
    const char* cmd_topic;
    gpio_num_t pwm_pin;
    gpio_num_t dir_pin;
    ledc_channel_t ledc_channel;
    int enc_a;
    int enc_b;
    float max_cmd_rads;
    float open_loop_duty_percent;
    uint32_t command_timeout_ms;
};
```

Closed-loop motors use:

- `mode = MotorControlMode::ClosedLoopSpeed`
- encoder pins
- `max_cmd_rads`
- `command_timeout_ms`

Fan motors use:

- `mode = MotorControlMode::OpenLoopSign`
- `enc_a = 0`, `enc_b = 0`
- `open_loop_duty_percent`
- `command_timeout_ms`

## Command And Feedback Bus

`Channel<T, N>` wraps a FreeRTOS queue. It still supports normal FIFO calls, but motor control uses the latest-value helpers:

| Method | Purpose |
|---|---|
| `sendLatest(msg)` | Enqueue newest data; if full, drop stale queued data first |
| `receiveLatest(msg, timeout)` | Receive one item, drain newer pending items, return newest |

This matters for safety. A stop command should not wait behind older motion commands.

## Closed-Loop MotorTask

Runs every 10 ms.

```text
receiveLatest command
sanitize command
clamp command to max_cmd_rads
convert rad/s to ticks/s
if command timed out: setpoint = 0

read encoder count
compute measured speed in ticks/s

if setpoint is near zero:
    reset PI
    motor.stop()
else:
    duty = pi.update(setpoint_tps, measured_tps, dt)
    motor.setSpeed(duty)

sendLatest feedback
```

Unit conversion:

```text
cmd.speed_rads * encoder_cfg::kTicksPerRad -> setpoint_tps
speed_tps / encoder_cfg::kTicksPerRad      -> feedback speed_rads
```

Zero setpoint behavior is deliberate: the PI controller is bypassed and the motor is stopped directly. This avoids a controller driving the motor because of encoder noise or sign errors while the requested speed is zero.

## Open-Loop Fan MotorTask

Runs every 10 ms.

```text
receiveLatest command
sanitize command
if command timed out: duty = 0

cmd > 0 -> +open_loop_duty_percent
cmd < 0 -> -open_loop_duty_percent
cmd = 0 -> stop

sendLatest zero feedback
```

Fans publish zero speed feedback because they have no encoder.

## MotorController

`MotorController` owns one PWM pin, one direction pin, and one LEDC channel.

Important behavior:

- `init()` drives PWM and DIR low before configuring LEDC.
- `stop()` sets PWM duty directly to zero, then drives direction low.
- `setSpeed(speed)` accepts a duty percentage in `[-100, 100]`.
- Positive speed sets direction forward and positive duty.
- Negative speed sets direction backward and positive duty magnitude.

The firmware can only control pins after the ESP32 has booted far enough to run application code. Hardware pulldowns or motor-driver enable/standby gating are still the robust way to guarantee no reset-time motion.

## Encoder

`Encoder` uses the ESP-IDF PCNT peripheral for 4x quadrature counting.

Constants in `include/Encoder.hpp`:

| Constant | Meaning |
|---|---|
| `kCprMotor` | Encoder pulses per motor-shaft revolution |
| `kGearRatio` | Gearbox ratio |
| `kTicksPerRev` | 4x quadrature ticks per output revolution |
| `kTicksPerRad` | Ticks per output radian |

If odometry direction is wrong in RViz, first try the Python node feedback sign parameters before changing encoder code:

```bash
ros2 launch manual_controller manual_controller.launch.py right_feedback_sign:=-1.0
```

## PI Tuning

Gains live at the top of `src/MotorTask.cpp`:

```cpp
static constexpr float kKp = 0.1f;
static constexpr float kKi = 0.5f;
```

The PI error is in ticks/s. The output is motor duty percent in `[-100, 100]`.

Suggested tuning:

1. Set `kKi = 0`.
2. Increase `kKp` until response is fast but not oscillating.
3. Increase `kKi` slowly to remove steady-state error.
4. Keep commands small while tuning.

## micro-ROS Interface

Node name:

```text
eyerobot_node
```

Command topics, host to ESP32:

| Topic | Type | Meaning |
|---|---|---|
| `/motor_belt_cmd` | `std_msgs/msg/Float32` | Belt speed setpoint in rad/s |
| `/motor_rwheel_cmd` | `std_msgs/msg/Float32` | Right wheel speed setpoint in rad/s |
| `/motor_lwheel_cmd` | `std_msgs/msg/Float32` | Left wheel speed setpoint in rad/s |
| `/motor_rfan_cmd` | `std_msgs/msg/Float32` | Right fan sign command |
| `/motor_lfan_cmd` | `std_msgs/msg/Float32` | Left fan sign command |

Feedback topics, ESP32 to host:

| Topic | Type | Meaning |
|---|---|---|
| `/motor_belt_fb` | `std_msgs/msg/Int32` | Belt speed in mrad/s |
| `/motor_rwheel_fb` | `std_msgs/msg/Int32` | Right wheel speed in mrad/s |
| `/motor_lwheel_fb` | `std_msgs/msg/Int32` | Left wheel speed in mrad/s |
| `/motor_rfan_fb` | `std_msgs/msg/Int32` | Always zero |
| `/motor_lfan_fb` | `std_msgs/msg/Int32` | Always zero |

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
ros2 topic pub --once /motor_belt_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_rwheel_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_lwheel_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_rfan_cmd std_msgs/msg/Float32 "{data: 0.0}"
ros2 topic pub --once /motor_lfan_cmd std_msgs/msg/Float32 "{data: 0.0}"
```
