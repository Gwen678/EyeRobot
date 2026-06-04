#include "Encoder.hpp"

// Hardware counter range before software accumulation kicks in.
static constexpr int kHighLimit =  30000;
static constexpr int kLowLimit  = -30000;

// GPIO 34-39 are input-only pads with no internal pull resistors; calling
// gpio_set_pull_mode() on them fails. With no external pull-ups wired, enable
// the internal pull-up on every encoder line that actually supports one. All
// current encoder pins (see pins.hpp) are < 34, so each gets an internal
// pull-up; this guard only matters if an input-only pad is reassigned here.
static void enable_internal_pullup(int pin)
{
    if (pin >= 0 && pin < 34) {
        gpio_set_pull_mode(static_cast<gpio_num_t>(pin), GPIO_PULLUP_ONLY);
    }
}

Encoder::Encoder(int pin_a, int pin_b)
    : _pin_a(pin_a), _pin_b(pin_b) {}

Encoder::~Encoder()
{
    if (_chan_a) pcnt_del_channel(_chan_a);
    if (_chan_b) pcnt_del_channel(_chan_b);
    if (_unit)   pcnt_del_unit(_unit);
}

esp_err_t Encoder::init()
{
    // Create PCNT unit with automatic overflow accumulation (IDF >= 5.1).
    pcnt_unit_config_t unit_cfg = {};
    unit_cfg.low_limit        = kLowLimit;
    unit_cfg.high_limit       = kHighLimit;
    unit_cfg.flags.accum_count = 1;

    esp_err_t err = pcnt_new_unit(&unit_cfg, &_unit);
    if (err != ESP_OK) return err;

    // Channel A: signal = pin_a, control = pin_b
    //   A↑ B=H → +1 | A↑ B=L → −1
    //   A↓ B=H → −1 | A↓ B=L → +1
    pcnt_chan_config_t chan_a_cfg = {};
    chan_a_cfg.edge_gpio_num  = _pin_a;
    chan_a_cfg.level_gpio_num = _pin_b;

    err = pcnt_new_channel(_unit, &chan_a_cfg, &_chan_a);
    if (err != ESP_OK) return err;

    pcnt_channel_set_edge_action(_chan_a,
        PCNT_CHANNEL_EDGE_ACTION_INCREASE,   // rising edge default: +1
        PCNT_CHANNEL_EDGE_ACTION_DECREASE);  // falling edge default: -1
    pcnt_channel_set_level_action(_chan_a,
        PCNT_CHANNEL_LEVEL_ACTION_KEEP,      // B=HIGH: keep direction
        PCNT_CHANNEL_LEVEL_ACTION_INVERSE);  // B=LOW:  invert direction

    // Channel B: signal = pin_b, control = pin_a
    //   B↑ A=H → −1 | B↑ A=L → +1
    //   B↓ A=H → +1 | B↓ A=L → −1
    pcnt_chan_config_t chan_b_cfg = {};
    chan_b_cfg.edge_gpio_num  = _pin_b;
    chan_b_cfg.level_gpio_num = _pin_a;

    err = pcnt_new_channel(_unit, &chan_b_cfg, &_chan_b);
    if (err != ESP_OK) return err;

    pcnt_channel_set_edge_action(_chan_b,
        PCNT_CHANNEL_EDGE_ACTION_DECREASE,   // rising edge default: -1
        PCNT_CHANNEL_EDGE_ACTION_INCREASE);  // falling edge default: +1
    pcnt_channel_set_level_action(_chan_b,
        PCNT_CHANNEL_LEVEL_ACTION_KEEP,
        PCNT_CHANNEL_LEVEL_ACTION_INVERSE);

    // No external pull-ups wired: enable internal pull-ups where supported.
    enable_internal_pullup(_pin_a);
    enable_internal_pullup(_pin_b);

    err = pcnt_unit_enable(_unit);
    if (err != ESP_OK) return err;

    return pcnt_unit_clear_count(_unit);
}

esp_err_t Encoder::start()
{
    return pcnt_unit_start(_unit);
}

esp_err_t Encoder::stop()
{
    return pcnt_unit_stop(_unit);
}

int Encoder::getCount() const
{
    int count = 0;
    pcnt_unit_get_count(_unit, &count);
    return count;
}

void Encoder::clearCount()
{
    pcnt_unit_clear_count(_unit);
}
