#include "AppBus.hpp"
#include "MicroRosTask.hpp"
#include "MotorTask.hpp"

#include "driver/gpio.h"
#include "esp_rom_gpio.h"
#include "soc/gpio_sig_map.h"

static AppBus g_bus;

// Every motor-driver control line physically wired to the ESP32, INCLUDING
// motors whose tasks are currently disabled in kMotorConfigs (fans, belt).
// Those H-bridges still need to be held off at boot — if their PWM/DIR pins are
// left floating they pick up noise and the motor runs away. kMotorConfigs only
// covers the enabled motors, so we cannot derive this list from it.
static constexpr gpio_num_t kAllMotorControlPins[] = {
    (gpio_num_t)BELT_PWM_PIN,        (gpio_num_t)BELT_DIR_PIN,
    (gpio_num_t)RIGHT_WHEEL_PWM_PIN, (gpio_num_t)RIGHT_WHEEL_DIR_PIN,
    (gpio_num_t)LEFT_WHEEL_PWM_PIN,  (gpio_num_t)LEFT_WHEEL_DIR_PIN,
    (gpio_num_t)RIGHT_FAN_PWM_PIN,   (gpio_num_t)RIGHT_FAN_DIR_PIN,
    (gpio_num_t)LEFT_FAN_PWM_PIN,    (gpio_num_t)LEFT_FAN_DIR_PIN,
};

static void force_motor_outputs_low()
{
    uint64_t motor_pin_mask = 0;

    for (gpio_num_t pin : kAllMotorControlPins) {
        gpio_reset_pin(pin);
        esp_rom_gpio_connect_out_signal(pin, SIG_GPIO_OUT_IDX, false, false);
        motor_pin_mask |= (1ULL << pin);
    }

    gpio_config_t cfg = {};
    cfg.pin_bit_mask = motor_pin_mask;
    cfg.mode = GPIO_MODE_OUTPUT;
    cfg.pull_up_en = GPIO_PULLUP_DISABLE;
    cfg.pull_down_en = GPIO_PULLDOWN_ENABLE;
    cfg.intr_type = GPIO_INTR_DISABLE;
    ESP_ERROR_CHECK(gpio_config(&cfg));

    for (gpio_num_t pin : kAllMotorControlPins) {
        ESP_ERROR_CHECK(gpio_set_level(pin, 0));
    }
}

extern "C" void app_main(void)
{
    // Force every motor control line to a defined stopped state (PWM duty 0,
    // DIR low) the instant the firmware starts — synchronously, before any
    // motor task or micro-ROS entity is created and well before the agent
    // handshake. This guarantees the H-bridges never see a spurious enable
    // while the link is down (e.g. powered standalone with no agent).
    force_motor_outputs_low();

    static MotorTask right_wheel(MotorID::RIGHT_WHEEL, g_bus);
    static MotorTask left_wheel (MotorID::LEFT_WHEEL,  g_bus);
    static MotorTask belt       (MotorID::BELT,        g_bus);
    static MotorTask right_fan  (MotorID::RIGHT_FAN,   g_bus);
    static MotorTask left_fan   (MotorID::LEFT_FAN,    g_bus);

    static MicroRosTask micro_ros_task(g_bus);
}
