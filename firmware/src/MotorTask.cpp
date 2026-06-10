#include "MotorTask.hpp"

#include <cmath>

#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static constexpr uint32_t kPeriodMs = 10;
static constexpr float    kDt       = kPeriodMs / 1000.0f;


// Tuned against the measured plant gain: 100% duty ≈ 11 rad/s ≈ 10 000 ticks/s,
// so ~100 ticks/s per duty unit. Kp=0.01 → proportional loop gain ≈ 1 (no duty
// saturation below ~9 rad/s of error; the old 0.1 railed at ±100 for any error
// over ~1 rad/s and ran the loop as chattering bang-bang). Encoder quantization
// (1 tick / 10 ms = 100 tps) now maps to ±1 duty unit of noise instead of ±10.
// Ki=0.04 → integral pole ≈ 4 /s (~0.25 s to absorb the steady-state duty).
static constexpr float kKp     =  0.01f;
static constexpr float kKi     =  0.04f;
static constexpr float kOutMin = -100.0f;
static constexpr float kOutMax =  100.0f;
static constexpr float kStopSetpointEpsilonTps = 1.0f;
// Feedforward model, command frame. kDutyPerTps: ~100% duty ≈ 11 rad/s ≈
// 10 000 tps free speed → ~0.01 duty per tps. kBreakawayDuty: duty needed to
// start the wheel turning under robot load — TUNE on hardware: too low brings
// back the delayed-launch symptom, too high makes the slowest crawl jumpy.
static constexpr float kDutyPerTps    = 0.01f;
static constexpr float kBreakawayDuty = 15.0f;

// Active braking releases below this measured speed (~0.33 rad/s): braking to
// a perfect 0 would leave the integrator fighting stiction and measurement
// quantization (1 tick / 10 ms = 100 tps), causing creep/twitch at standstill.
// Friction handles the last fraction of a rad/s.
static constexpr float kBrakeReleaseTps = 300.0f;

// Open-loop sign control (fans/belt) turns ANY nonzero command into full duty,
// so a single corrupted/duplicated best-effort sample would become a full-power
// twitch. Ignore sub-threshold magnitudes — well below real commands (~5-8 rad/s).
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
    // Read the encoder for telemetry whenever the motor has one wired, even in
    // open-loop mode — otherwise the wheel feedback topics always report 0.
    // enc pins of 0 are the "no encoder" sentinel used for the fans/belt.
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

        // Safety net only: zero the held command if the stream stops (comms
        // loss). During normal operation the teleop node republishes at a fixed
        // rate, so the command persists and a key for one motor never clears
        // another.
        if ((now - last_command_tick) > command_timeout_ticks) {
            _command_rads = 0.0f;
        }

        // Hard safety gate: while the micro-ROS link is down (boot before the
        // first agent connection, or any reconnect) force the held command to 0
        // so the motor stays stopped regardless of the last received command.
        // This decouples motor safety from the (blocking) reconnect loop — the
        // robot stays still at 0 the whole time the agent is unreachable.
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

        // Compute the desired duty in the COMMAND frame (+ = forward), then apply
        // the per-wheel motor-polarity correction so +duty physically drives this
        // wheel forward. Keeping invert_motor out of the PI means the loop sees a
        // coherent +command/+measured frame (negative feedback) and only the
        // final actuator step accounts for wiring polarity.
        float duty   = 0.0f;
        bool  stop   = false;
        if (closed_loop) {
            const float setpoint_tps = _command_rads * encoder_cfg::kTicksPerRad;
            // Commanded direction flipped: drop integral built up for the old
            // direction so the reversal isn't sluggish unwinding it.
            if (setpoint_tps * prev_setpoint_tps < 0.0f) {
                _pi.reset();
            }
            prev_setpoint_tps = setpoint_tps;

            if (is_stop_setpoint(setpoint_tps)) {
                // Commanded stop → active braking: regulate to 0 while the
                // wheel still moves (reverse torque ∝ remaining speed), then
                // release and coast once (nearly) stationary so the integrator
                // can't hold torque against stiction at standstill. The old
                // hard-coast-only behaviour guarded against a spin/brake
                // oscillation that came from the broken loop (bang-bang gains
                // + inverted left feedback), both fixed since.
                if (std::abs(measured_tps) < kBrakeReleaseTps) {
                    _pi.reset();
                    stop = true;
                } else {
                    duty = _pi.update(0.0f, measured_tps, kDt);
                }
            } else {
                // Feedforward + PI trim. Without feedforward the integrator has
                // to wind the duty up from 0 past the gearbox breakaway on
                // every launch: the wheel sits still (PWM LED ramping) and then
                // jumps off with the accumulated integral — visible as
                // "nothing, nothing, full speed". Seed the duty with the known
                // plant model instead and let the PI correct the residual.
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
