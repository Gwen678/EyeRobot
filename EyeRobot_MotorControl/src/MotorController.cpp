#include "MotorController.hpp"

#include "driver/gpio.h"
#include "driver/ledc.h"

MotorController::MotorController(gpio_num_t pwm_pin,
                                 gpio_num_t dir_pin,
                                 ledc_channel_t ledc_channel,
                                 ledc_timer_t ledc_timer)
    : _pwm_pin(pwm_pin),
      _dir_pin(dir_pin),
      _ledc_channel(ledc_channel),
      _ledc_timer(ledc_timer) {}

esp_err_t configure_pwm_timer(ledc_timer_t timer)
{
    ledc_timer_config_t timer_cfg = {};
    timer_cfg.speed_mode = motor_cfg::LEDC_MODE;
    timer_cfg.duty_resolution = motor_cfg::LEDC_RES;
    timer_cfg.timer_num = timer;
    timer_cfg.freq_hz = motor_cfg::PWM_FREQ_HZ;
    timer_cfg.clk_cfg = LEDC_AUTO_CLK;

    esp_err_t err = ledc_timer_config(&timer_cfg);
    return err;
}
esp_err_t configure_direction_pin(gpio_num_t gpio){
    gpio_config_t dir_cfg = {};
    dir_cfg.pin_bit_mask = (1ULL << gpio);
    dir_cfg.mode = GPIO_MODE_OUTPUT;
    dir_cfg.pull_up_en = GPIO_PULLUP_DISABLE;
    dir_cfg.pull_down_en = GPIO_PULLDOWN_DISABLE;
    dir_cfg.intr_type = GPIO_INTR_DISABLE;

    esp_err_t err = gpio_config(&dir_cfg);
    return err;
    
}

esp_err_t configure_pwm_channel(gpio_num_t gpio, ledc_timer_t timer, ledc_channel_t channel){
    ledc_channel_config_t ch_cfg = {};
    ch_cfg.gpio_num = gpio;
    ch_cfg.speed_mode = motor_cfg::LEDC_MODE;
    ch_cfg.channel = channel;
    ch_cfg.intr_type = LEDC_INTR_DISABLE;
    ch_cfg.timer_sel = timer;
    ch_cfg.duty = 0;
    ch_cfg.hpoint = 0;

    esp_err_t err = ledc_channel_config(&ch_cfg);
    return err;
}



esp_err_t MotorController::init() {
    esp_err_t err = configure_direction_pin(_dir_pin);
    if (err != ESP_OK) {
        return err;
    }

    err = configure_pwm_timer(_ledc_timer);
    if (err != ESP_OK) {
        return err;
    }

    err = configure_pwm_channel(_pwm_pin, _ledc_timer, _ledc_channel);
    if (err != ESP_OK) {
        return err;
    }

    err = setDirection(Direction::forward);
    if (err != ESP_OK) {
        return err;
    }

    return stop();
}

esp_err_t MotorController::setDirection(Direction forward_dir) {
    if (forward_dir == Direction::forward) {
        return gpio_set_level(_dir_pin, 1);
    } else {
        return gpio_set_level(_dir_pin, 0);
    }
}

esp_err_t MotorController::forward() {
    return setDirection(Direction::forward);
}

esp_err_t MotorController::backward() {
    return setDirection(Direction::backward);
}

esp_err_t MotorController::stop() {
    return setSpeed(0.0f);
}

esp_err_t MotorController::setDutyRaw(uint32_t duty) {
    if (duty > motor_cfg::DUTY_MAX) {
        duty = motor_cfg::DUTY_MAX;
    }

    esp_err_t err = ledc_set_duty(motor_cfg::LEDC_MODE, _ledc_channel, duty);
    if (err != ESP_OK) {
        return err;
    }

    return ledc_update_duty(motor_cfg::LEDC_MODE, _ledc_channel);
}

esp_err_t MotorController::setPercent(float percent) {
    if (percent < 0.0f) {
        percent = 0.0f;
    }
    if (percent > 100.0f) {
        percent = 100.0f;
    }

    const uint32_t duty =
        static_cast<uint32_t>((percent / 100.0f) * static_cast<float>(motor_cfg::DUTY_MAX));

    return setDutyRaw(duty);
}

esp_err_t MotorController::setSpeed(float speed) { // speed is in range [-100.0, 100.0]
    if (speed > 100.0f) {
        speed = 100.0f;
    }
    if (speed < -100.0f) {
        speed = -100.0f;
    }

    if (speed >= 0.0f) {
        esp_err_t err = forward();
        if (err != ESP_OK) {
            return err;
        }
        return setPercent(speed);
    } else {
        esp_err_t err = backward();
        if (err != ESP_OK) {
            return err;
        }
        return setPercent(speed);
    }
}