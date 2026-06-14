#include "PiController.hpp"

PiController::PiController(float kp, float ki, float out_min, float out_max)
    : _kp(kp), _ki(ki), _out_min(out_min), _out_max(out_max) {}

float PiController::update(float setpoint, float measurement, float dt)
{
    const float error = setpoint - measurement;

    float output = _kp * error;

    // Integral term with antiwindup. Skip when ki == 0 (pure P): no integral
    // contribution and the windup clamp would divide by zero.
    if (_ki != 0.0f) {
        _integral += error * dt;

        // Clamp the integrator so its contribution alone stays within limits.
        const float integral_max = _out_max / _ki;
        const float integral_min = _out_min / _ki;
        if (_integral > integral_max) _integral = integral_max;
        else if (_integral < integral_min) _integral = integral_min;

        output += _ki * _integral;
    }

    if (output > _out_max) output = _out_max;
    else if (output < _out_min) output = _out_min;

    return output;
}

void PiController::reset()
{
    _integral = 0.0f;
}

void PiController::setGains(float kp, float ki)
{
    _kp = kp;
    _ki = ki;
}

void PiController::setLimits(float out_min, float out_max)
{
    _out_min = out_min;
    _out_max = out_max;
}
