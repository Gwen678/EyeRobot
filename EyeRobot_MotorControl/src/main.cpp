#include "MotorController.hpp"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_check.h"
#include "esp_log.h"

static const char *TAG = "MY_APP";

extern "C" void app_main(void) {
    MotorController motor;

    ESP_ERROR_CHECK(motor.init());

    while(1) {
        motor.setSpeed(0);
        vTaskDelay(pdMS_TO_TICKS(1000));

        motor.setSpeed(80);
        vTaskDelay(pdMS_TO_TICKS(2000));

        motor.setSpeed(0);
        vTaskDelay(pdMS_TO_TICKS(1000));

        motor.setSpeed(-80);
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}
