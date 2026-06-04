#include "MotorTask.hpp"

#include <cmath>

#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static constexpr uint32_t kPeriodMs = 10;
static constexpr float    kDt       = kPeriodMs / 1000.0f;

static constexpr float kKp     =  0.1f;
static constexpr float kKi     =  0.5f;
static constexpr float kOutMin = -100.0f;
static constexpr float kOutMax =  100.0f;
static constexpr float kStopSetpointEpsilonTps = 1.0f;

// Open-loop sign control turns ANY nonzero command into full duty, so a single
// corrupted/duplicated best-effort sample would become a full-power twitch.
// Ignore sub-threshold magnitudes — well below real commands (~5-8 rad/s).
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

    ESP_ERROR_CHECK(_motor.init());
    if (closed_loop) {
        ESP_ERROR_CHECK(_encoder.init());
        ESP_ERROR_CHECK(_encoder.start());
    }

    TickType_t wake_time = xTaskGetTickCount();
    TickType_t last_command_tick = wake_time;
    const TickType_t command_timeout_ticks = pdMS_TO_TICKS(_cfg.command_timeout_ms);

    float setpoint_tps = 0.0f;
    float open_duty = 0.0f;
    int32_t prev_ticks = 0;

    while (true) {
        vTaskDelayUntil(&wake_time, pdMS_TO_TICKS(kPeriodMs));
        const TickType_t now = xTaskGetTickCount();

        MotorCmd cmd;
        if (_bus.to_motor[idx].receiveLatest(cmd, 0)) {
            last_command_tick = now;
            const float speed_rads = sanitize_command(cmd.speed_rads, _cfg.max_cmd_rads);

            if (closed_loop) {
                setpoint_tps = speed_rads * encoder_cfg::kTicksPerRad;
                if (is_stop_setpoint(setpoint_tps)) {
                    _pi.reset();
                }
            } else {
                open_duty = open_loop_duty_from_command(speed_rads, _cfg.open_loop_duty_percent);
            }
        }

        if ((now - last_command_tick) > command_timeout_ticks) {
            setpoint_tps = 0.0f;
            open_duty = 0.0f;
            _pi.reset();
        }

        MotorFeedback fb;

        if (closed_loop) {
            const int32_t ticks     = _encoder.getCount();
            const float   speed_tps = (ticks - prev_ticks) / kDt;
            prev_ticks = ticks;

            if (is_stop_setpoint(setpoint_tps)) {
                _pi.reset();
                _motor.stop();
            } else {
                const float duty = _pi.update(setpoint_tps, speed_tps, kDt);
                _motor.setSpeed(duty);
            }

            fb.ticks      = ticks;
            fb.speed_rads = speed_tps / encoder_cfg::kTicksPerRad;
        } else {
            if (open_duty == 0.0f) {
                _motor.stop();
            } else {
                _motor.setSpeed(open_duty);
            }

            fb.ticks      = 0;
            fb.speed_rads = 0.0f;
        }

        _bus.from_motor[idx].sendLatest(fb);
    }
}
