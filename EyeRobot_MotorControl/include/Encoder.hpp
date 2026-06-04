#pragma once

#include "driver/gpio.h"
#include "driver/pulse_cnt.h"
#include "esp_err.h"

namespace encoder_cfg {
// Pins are assigned per motor in kMotorConfigs and passed to the constructor.
constexpr int   kCprMotor    = 16;                      // encoder pulses/rev at motor shaft
constexpr int   kGearRatio   = 90;                      // gearbox reduction (1440 / 16)
constexpr int   kCprOutput   = kCprMotor * kGearRatio;  // 1440 pulses/rev at output shaft
constexpr int   kTicksPerRev = kCprOutput * 4;          // 5760 ticks/rev (4x quadrature)
constexpr float kTicksPerRad = kTicksPerRev / (2.0f * 3.14159265358979f); // ≈ 917.0
}

// Full quadrature (4x) encoder using the ESP-IDF PCNT peripheral.
// Requires ESP-IDF >= 5.1 for accum_count overflow accumulation.
class Encoder {
public:
    Encoder(int pin_a, int pin_b);
    ~Encoder();

    Encoder(const Encoder&) = delete;
    Encoder& operator=(const Encoder&) = delete;

    esp_err_t init();
    esp_err_t start();
    esp_err_t stop();

    int  getCount() const;
    void clearCount();

private:
    int _pin_a;
    int _pin_b;

    pcnt_unit_handle_t    _unit   = nullptr;
    pcnt_channel_handle_t _chan_a = nullptr;
    pcnt_channel_handle_t _chan_b = nullptr;
};
