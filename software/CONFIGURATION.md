# Configuration Customization

Certain properties of the module, such as screen rotation, CPU clock speed, and Raspberry Pi Pico model, can be
set using a static configuration file.  This file is located at `/config/config_EuroPiConfig.json` on the
Raspberry Pi Pico. If this file does not exist, default settings will be loaded.  The following shows the
default configuration:
```json
{
    "europi_model": "europi",
    "pico_model": "pico",
    "cpu_freq": 250000000,
    "rotate_display": false,
    "display_width": 128,
    "display_height": 32,
    "display_sda": 0,
    "display_scl": 1,
    "display_channel": 0
    "max_output_voltage": 10,
    "max_input_voltage": 12,
    "gate_voltage": 5
}
```

- `europi_model` specifies the type of EuroPi module. Currently only `"europi"` is supported
- `pico_model` must be one of `"pico"` or `"pico w"`
- `cpu_freq` must be one of `250000000` or `125000000`
- `rotate_display` must be one of `false` or `true`
- `display_width` is the width of the screen in pixels. The standard EuroPi screen is 128 pixels wide
- `display_height` is the height of the screen in pixels. The standard EuroPi screen is 32 pixels tall
- `display_sda` is the I²C SDA pin used for the display. Only SDA capable pins can be selected
- `display_scl` is the I²C SCL pin used for the display. Only SCL capable pins can be selected
- `display_channel` is the I²C channel used for the display, either 0 or 1.
- `volts_per_octave` must be one of `1.0` (Eurorack standard) or `1.2` (Buchla standard)
- `max_output_voltage` is an integer in the range `[0, 10]` indicating the maximum voltage CV output can generate.
  The hardware is capable of 10V maximum
- `max_input_voltage` is an integer in the range `[0, 12]` indicating the maximum allowed voltage into the `ain` jack.
  The hardware is capable of 12V maximum
- `gate_voltage` is an integer in the range `[0, 12]` indicating the voltage that an output will produce when `cvx.on()` is called



# Experimental configuration

Other configuration properties are used by [experimental features](software/firmware/experimental/__init__.py)
and can be set using a similar static configuration file. This file is located at `/config/config_ExperimentalConfig.json` 
on the Raspberry Pi Pico. If this file does not exist, default settings will be loaded.  The following
shows the default configuration:

```json
{
    "volts_per_octave": 1.0,
}
```

- `volts_per_octave` must be one of `1.0` (Eurorack standard) or `1.2` (Buchla standard)
