#pragma once

#include "AppBus.hpp"
#include "Encoder.hpp"
#include "MotorController.hpp"
#include "PiController.hpp"
#include "Thread.hpp"

class MotorTask : public Thread {
public:
    explicit MotorTask(MotorID id, AppBus& bus);

protected:
    void run() override;

private:
    const MotorConfig& _cfg;
    MotorController    _motor;
    Encoder            _encoder;
    PiController       _pi;
    AppBus&            _bus;

    // Latest commanded speed in rad/s, persisted across loop iterations. A new
    // micro-ROS command overwrites it; otherwise the loop keeps executing the
    // last value (until the safety timeout zeroes it on comms loss).
    float              _command_rads = 0.0f;
};
