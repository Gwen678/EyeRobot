#pragma once

#include "Channel.hpp"
#include "pins.hpp"
#include "driver/gpio.h"
#include "driver/ledc.h"
#include <cstdint>
#include <cstddef>

// ── Motor identity ────────────────────────────────────────────────────────────

enum class MotorID : uint8_t {
    RIGHT_WHEEL = 0,
    LEFT_WHEEL  = 1,
    BELT        = 2,
    RIGHT_FAN   = 3,
    LEFT_FAN    = 4,
    COUNT
};

static constexpr size_t MOTOR_COUNT = static_cast<size_t>(MotorID::COUNT);

enum class MotorControlMode : uint8_t {
    ClosedLoopSpeed,
    OpenLoopSign,
};

// ── Per-motor hardware configuration ─────────────────────────────────────────
//
// Single source of truth: pins come from pins.hpp, LEDC channels are assigned
// here (one channel per motor, all sharing LEDC_TIMER_0 at 20 kHz).
// Belt and wheels use encoder speed PI. Fans are intentionally encoder-less and
// therefore use open-loop sign control.

struct MotorConfig {
    MotorID        id;
    MotorControlMode mode;
    const char*    fb_topic;       // micro-ROS feedback topic name
    const char*    cmd_topic;      // micro-ROS command subscription topic
    gpio_num_t     pwm_pin;
    gpio_num_t     dir_pin;
    ledc_channel_t ledc_channel;
    int            enc_a;
    int            enc_b;
    float          max_cmd_rads;
    float          open_loop_duty_percent;
    uint32_t       command_timeout_ms;
};

static constexpr float kDefaultMaxCmdRads = 20.0f;
// All motors run open-loop sign control; drive every one at full duty.
static constexpr float kFanDutyPercent = 100.0f;
static constexpr float kWheelOpenLoopDuty = 100.0f;
static constexpr float kBeltOpenLoopDuty = 100.0f;
static constexpr uint32_t kDefaultCommandTimeoutMs = 500;

static constexpr MotorConfig kMotorConfigs[MOTOR_COUNT] = {
    { MotorID::RIGHT_WHEEL,
      MotorControlMode::OpenLoopSign,
      "motor_rwheel_fb", "motor_rwheel_cmd",
      (gpio_num_t)RIGHT_WHEEL_PWM_PIN, (gpio_num_t)RIGHT_WHEEL_DIR_PIN,
      LEDC_CHANNEL_0,
      RIGHT_WHEEL_ENCODER_A_PIN, RIGHT_WHEEL_ENCODER_B_PIN,
      kDefaultMaxCmdRads, kWheelOpenLoopDuty, kDefaultCommandTimeoutMs },

    { MotorID::LEFT_WHEEL,
      MotorControlMode::OpenLoopSign,
      "motor_lwheel_fb", "motor_lwheel_cmd",
      (gpio_num_t)LEFT_WHEEL_PWM_PIN, (gpio_num_t)LEFT_WHEEL_DIR_PIN,
      LEDC_CHANNEL_1,
      LEFT_WHEEL_ENCODER_A_PIN, LEFT_WHEEL_ENCODER_B_PIN,
      kDefaultMaxCmdRads, kWheelOpenLoopDuty, kDefaultCommandTimeoutMs },

    { MotorID::BELT,
      MotorControlMode::OpenLoopSign,
      "motor_belt_fb",   "motor_belt_cmd",
      (gpio_num_t)BELT_PWM_PIN, (gpio_num_t)BELT_DIR_PIN,
      LEDC_CHANNEL_2,
      0, 0,
      kDefaultMaxCmdRads, kBeltOpenLoopDuty, kDefaultCommandTimeoutMs },

    { MotorID::RIGHT_FAN,
      MotorControlMode::OpenLoopSign,
      "motor_rfan_fb",   "motor_rfan_cmd",
      (gpio_num_t)RIGHT_FAN_PWM_PIN, (gpio_num_t)RIGHT_FAN_DIR_PIN,
      LEDC_CHANNEL_3,
      0, 0,
      kDefaultMaxCmdRads, kFanDutyPercent, kDefaultCommandTimeoutMs },

    { MotorID::LEFT_FAN,
      MotorControlMode::OpenLoopSign,
      "motor_lfan_fb",   "motor_lfan_cmd",
      (gpio_num_t)LEFT_FAN_PWM_PIN, (gpio_num_t)LEFT_FAN_DIR_PIN,
      LEDC_CHANNEL_4,
      0, 0,
      kDefaultMaxCmdRads, kFanDutyPercent, kDefaultCommandTimeoutMs },
};

// ── Bus message types ─────────────────────────────────────────────────────────

struct MotorCmd {
    float speed_rads;   // setpoint in rad/s (negative = backward)
};

struct MotorFeedback {
    int32_t ticks;      // accumulated encoder ticks (0 for encoder-less motors)
    float   speed_rads; // measured / simulated speed in rad/s
};

// ── Application bus ───────────────────────────────────────────────────────────
//
// One channel pair per motor, indexed by MotorID.
// MicroRosTask writes to_motor[id], MotorTask reads to_motor[id].
// MotorTask writes from_motor[id], MicroRosTask reads from_motor[id].

struct AppBus {
    Channel<MotorCmd,      4> to_motor[MOTOR_COUNT];
    Channel<MotorFeedback, 4> from_motor[MOTOR_COUNT];
};
