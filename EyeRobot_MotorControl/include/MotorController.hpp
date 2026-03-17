#pragma once

#include <cstdint>
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_err.h"

namespace motor_cfg {
constexpr gpio_num_t PWM_GPIO = GPIO_NUM_18;   // ESP32 -> M1_PWM
constexpr gpio_num_t DIR_GPIO = GPIO_NUM_19;   // ESP32 -> M1_EN

constexpr ledc_mode_t LEDC_MODE = LEDC_LOW_SPEED_MODE;
constexpr ledc_timer_t LEDC_TIMER = LEDC_TIMER_0;
constexpr ledc_channel_t LEDC_CHANNEL = LEDC_CHANNEL_0;
constexpr ledc_timer_bit_t LEDC_RES = LEDC_TIMER_10_BIT;

constexpr uint32_t PWM_FREQ_HZ = 20000;
constexpr uint32_t DUTY_MAX = (1u << 10) - 1u;
}


enum class Direction {
    forward,
    backward
};


class MotorController {
public:
    MotorController(gpio_num_t pwm_pin = motor_cfg::PWM_GPIO,
                    gpio_num_t dir_pin = motor_cfg::DIR_GPIO,
                    ledc_channel_t ledc_channel = motor_cfg::LEDC_CHANNEL,
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
    gpio_num_t _pwm_pin;
    gpio_num_t _dir_pin;
    ledc_channel_t _ledc_channel;
    ledc_timer_t _ledc_timer;
};