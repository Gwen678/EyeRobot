#pragma once

#include <cstdint>
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_err.h"

namespace motor_cfg {
// Pins and LEDC channel are assigned per motor in kMotorConfigs and passed to
// the constructor; only the shared LEDC timer/resolution/frequency live here.
constexpr ledc_mode_t LEDC_MODE = LEDC_LOW_SPEED_MODE;
constexpr ledc_timer_t LEDC_TIMER = LEDC_TIMER_0;
constexpr ledc_timer_bit_t LEDC_RES = LEDC_TIMER_10_BIT;

// 21 kHz: above audible (10 kHz whined badly) and under the DC Motor Driver
// 2x15A Lite's 25 kHz cap. Its fast-switching damage caution scales with load
// current — our motors draw a few A, far below the 15 A/channel rating, so
// switching loss stays small. Kept below 25 kHz so the optocoupler rise/fall
// times don't eat into duty linearity. 10-bit resolution is fine up to ~78 kHz.
constexpr uint32_t PWM_FREQ_HZ = 21000;
constexpr uint32_t DUTY_MAX = (1u << 10) - 1u;
}


enum class Direction {
    forward,
    backward
};


class MotorController {
public:
    MotorController(gpio_num_t pwm_pin,
                    gpio_num_t dir_pin,
                    ledc_channel_t ledc_channel,
                    ledc_timer_t ledc_timer = motor_cfg::LEDC_TIMER);

    esp_err_t init();

    esp_err_t forward();
    esp_err_t backward();
    esp_err_t stop();

    esp_err_t setDutyRaw(uint32_t duty);
    esp_err_t setPercent(float percent);
    esp_err_t setDirection(Direction dir);
    esp_err_t setSpeed(float speed);

    gpio_num_t pwmPin() const { return _pwm_pin; }
    gpio_num_t dirPin() const { return _dir_pin; }

private:
    esp_err_t configure_pwm_timer(ledc_timer_t timer);
    esp_err_t configure_pwm_channel(gpio_num_t gpio, ledc_timer_t timer, ledc_channel_t channel);
    esp_err_t configure_direction_pin(gpio_num_t gpio);

    gpio_num_t _pwm_pin;
    gpio_num_t _dir_pin;
    ledc_channel_t _ledc_channel;
    ledc_timer_t _ledc_timer;
};