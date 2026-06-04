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
};
