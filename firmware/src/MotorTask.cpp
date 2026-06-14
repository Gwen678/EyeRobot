#include "MotorTask.hpp"

#include <cmath>

#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static constexpr uint32_t kPeriodMs = 10;
static constexpr float    kDt       = kPeriodMs / 1000.0f;


// Tuned for ~100 ticks/s per duty unit (100% duty ~ 11 rad/s ~ 10000 ticks/s).
// Kp=0.01 gives loop gain ~1; Ki=0.04 gives integral pole ~4/s (~0.25 s to remove steady state duty).
static constexpr float kKp     =  0.01f;
static constexpr float kKi     =  0.04f;
static constexpr float kOutMin = -100.0f;
static constexpr float kOutMax =  100.0f;
static constexpr float kStopSetpointEpsilonTps = 1.0f;
// Minimum speed the drivetrain can sustain. Nonzero setpoints below this are
// raised to it (sign-preserving) to avoid commanding speeds the wheel cannot do.
static constexpr float kMinWheelRads = 1.0f;

// Feedforward model. kDutyPerTps: ~0.01 duty per tps (100% duty ~ 10000 tps free speed).
// kBreakawayDuty: duty needed to start the wheel turning under load. Tune on hardware.
static constexpr float kDutyPerTps    = 0.01f;
static constexpr float kBreakawayDuty = 15.0f;

// Active braking releases below this speed (~0.33 rad/s). Braking all the way to 0
// causes the integrator to fight static friction and rounding noise, causing slow drift at standstill.
static constexpr float kBrakeReleaseTps = 300.0f;

// Open loop sign control (fans/belt): ignore commands below this magnitude to avoid
// a corrupted best effort sample becoming a full-power jerk. Real commands are ~5-8 rad/s.
static constexpr float kOpenLoopDeadbandRads = 0.5f;

static float clamp_abs(float value, float max_abs)
{
    if (max_abs <= 0.0f) {
        return value;
    }
    if (value > max_abs) {
        return max_abs;
    }
    if (value < -max_abs) {
        return -max_abs;
    }
    return value;
}

static float sanitize_command(float speed_rads, float max_abs_rads)
{
    if (!std::isfinite(speed_rads)) {
        return 0.0f;
    }
    return clamp_abs(speed_rads, max_abs_rads);
}

static bool is_stop_setpoint(float setpoint_tps)
{
    return setpoint_tps > -kStopSetpointEpsilonTps &&
           setpoint_tps <  kStopSetpointEpsilonTps;
}

static float open_loop_duty_from_command(float speed_rads, float duty_percent)
{
    if (speed_rads >  kOpenLoopDeadbandRads) {
        return duty_percent;
    }
    if (speed_rads < -kOpenLoopDeadbandRads) {
        return -duty_percent;
    }
    return 0.0f;
}

MotorTask::MotorTask(MotorID id, AppBus& bus)
    : Thread(kMotorConfigs[static_cast<size_t>(id)].fb_topic, 4096, 5),
      _cfg(kMotorConfigs[static_cast<size_t>(id)]),
      _motor(_cfg.pwm_pin, _cfg.dir_pin, _cfg.ledc_channel),
      _encoder(_cfg.enc_a, _cfg.enc_b),
      _pi(kKp, kKi, kOutMin, kOutMax),
      _bus(bus)
{
    start();
}

void MotorTask::run()
{
    const size_t idx = static_cast<size_t>(_cfg.id);
    const bool closed_loop = (_cfg.mode == MotorControlMode::ClosedLoopSpeed);
    // Read the encoder for telemetry even in open loop mode; enc pins of 0
    // are the "no encoder" sentinel used for the fans/belt.
    const bool has_encoder = (_cfg.enc_a > 0 || _cfg.enc_b > 0);

    ESP_ERROR_CHECK(_motor.init());
    if (has_encoder) {
        ESP_ERROR_CHECK(_encoder.init());
        ESP_ERROR_CHECK(_encoder.start());
    }

    TickType_t wake_time = xTaskGetTickCount();
    TickType_t last_command_tick = wake_time;
    const TickType_t command_timeout_ticks = pdMS_TO_TICKS(_cfg.command_timeout_ms);

    int32_t prev_ticks = 0;
    float   prev_setpoint_tps = 0.0f;

    while (true) {
        vTaskDelayUntil(&wake_time, pdMS_TO_TICKS(kPeriodMs));
        const TickType_t now = xTaskGetTickCount();

        MotorCmd cmd;
        if (_bus.to_motor[idx].receiveLatest(cmd, 0)) {
            last_command_tick = now;
            _command_rads = sanitize_command(cmd.speed_rads, _cfg.max_cmd_rads);
        }

        // Safety: zero the held command on comms loss. During normal operation
        // the teleop node republishes at a fixed rate.
        if ((now - last_command_tick) > command_timeout_ticks) {
            _command_rads = 0.0f;
        }

        // Hard safety: force command to 0 while the micro-ROS link is down.
        // Keeps the robot still during boot or reconnect regardless of the last received command.
        if (!_bus.link_up.load(std::memory_order_relaxed)) {
            _command_rads = 0.0f;
        }

        MotorFeedback fb;
        fb.ticks      = 0;
        fb.speed_rads = 0.0f;

        float measured_tps = 0.0f;
        if (has_encoder) {
            const int32_t raw   = _encoder.getCount();
            const int32_t ticks = _cfg.invert_encoder ? -raw : raw;
            measured_tps = (ticks - prev_ticks) / kDt;
            prev_ticks   = ticks;
            fb.ticks      = ticks;
            fb.speed_rads = measured_tps / encoder_cfg::kTicksPerRad;
        }

        // Compute duty in the command frame (+ = forward), then apply per-wheel polarity.
        // Keeping invert_motor outside the PI ensures consistent +command/+measured frame.
        float duty   = 0.0f;
        bool  stop   = false;
        if (closed_loop) {
            float setpoint_tps = _command_rads * encoder_cfg::kTicksPerRad;
            // Raise below threshold commands to the minimum sustainable speed.
            // Zero stays zero (stop).
            if (!is_stop_setpoint(setpoint_tps)) {
                const float min_tps = kMinWheelRads * encoder_cfg::kTicksPerRad;
                if (setpoint_tps > 0.0f && setpoint_tps < min_tps) {
                    setpoint_tps = min_tps;
                } else if (setpoint_tps < 0.0f && setpoint_tps > -min_tps) {
                    setpoint_tps = -min_tps;
                }
            }
            // Direction flipped: reset integral to avoid slow reversal from unwinding old state.
            if (setpoint_tps * prev_setpoint_tps < 0.0f) {
                _pi.reset();
            }
            prev_setpoint_tps = setpoint_tps;

            if (is_stop_setpoint(setpoint_tps)) {
                // Commanded stop: actively brake while the wheel still moves,
                // then release and coast once nearly stationary to avoid holding torque against static friction.
                if (std::abs(measured_tps) < kBrakeReleaseTps) {
                    _pi.reset();
                    stop = true;
                } else {
                    duty = _pi.update(0.0f, measured_tps, kDt);
                }
            } else {
                // Feedforward + PI trim. Seed duty from the plant model so the
                // wheel moves immediately; PI corrects the steady state error.
                const float dir = (setpoint_tps > 0.0f) ? 1.0f : -1.0f;
                duty = dir * kBreakawayDuty
                     + kDutyPerTps * setpoint_tps
                     + _pi.update(setpoint_tps, measured_tps, kDt);
                duty = clamp_abs(duty, 100.0f);
            }
        } else {
            duty = open_loop_duty_from_command(_command_rads, _cfg.open_loop_duty_percent);
            stop = (duty == 0.0f);
        }

        if (_cfg.invert_motor) {
            duty = -duty;
        }

        if (stop) {
            _motor.stop();
        } else {
            _motor.setSpeed(duty);
        }

        _bus.from_motor[idx].sendLatest(fb);
    }
}
