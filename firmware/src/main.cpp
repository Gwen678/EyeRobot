#include "AppBus.hpp"
#include "MicroRosTask.hpp"
#include "MotorTask.hpp"

#include "driver/gpio.h"
#include "esp_rom_gpio.h"
#include "soc/gpio_sig_map.h"

static AppBus g_bus;

// All motor control pins wired to the ESP32, including disabled motors (fans, belt).
// H-bridges must be held off at boot; kMotorConfigs only covers enabled motors.
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
    // Drive all motor pins low before any task or micro-ROS entity is created.
    // Prevents H-bridges from seeing a spurious enable while the agent link is down.
    force_motor_outputs_low();

    static MotorTask right_wheel(MotorID::RIGHT_WHEEL, g_bus);
    static MotorTask left_wheel (MotorID::LEFT_WHEEL,  g_bus);
    static MotorTask belt       (MotorID::BELT,        g_bus);
    static MotorTask right_fan  (MotorID::RIGHT_FAN,   g_bus);
    static MotorTask left_fan   (MotorID::LEFT_FAN,    g_bus);

    static MicroRosTask micro_ros_task(g_bus);
}
