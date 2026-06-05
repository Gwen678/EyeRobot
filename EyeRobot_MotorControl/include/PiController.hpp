#pragma once

class PiController {
public:
    PiController(float kp, float ki, float out_min, float out_max);

    // Returns clamped output. Call at a fixed rate; dt is the period in seconds.
    float update(float setpoint, float measurement, float dt);

    void reset();
    void setGains(float kp, float ki);
    void setLimits(float out_min, float out_max);

private:
    float _kp, _ki;
    float _out_min, _out_max;
    float _integral = 0.0f;
};
