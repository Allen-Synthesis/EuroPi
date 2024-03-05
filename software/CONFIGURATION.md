# Configuration Customization

Certain properties of the module, such as screen rotation, CPU clock speed, and Raspberry Pi Pico model, can be
set using a static configuration file.  This file is located at `/config/EuroPiConfig.json` on the
Raspberry Pi Pico. If this file does not exist, default settings will be loaded.  The following shows the
default configuration:
```json
{
    "EUROPI_MODEL": "europi",
    "PICO_MODEL": "pico",
    "CPU_FREQ": 250000000,
    "ROTATE_DISPLAY": false,
    "DISPLAY_WIDTH": 128,
    "DISPLAY_HEIGHT": 32,
    "DISPLAY_SDA": 0,
    "DISPLAY_SCL": 1,
    "DISPLAY_CHANNEL": 0,
    "MAX_OUTPUT_VOLTAGE": 10,
    "MAX_INPUT_VOLTAGE": 12,
    "GATE_VOLTAGE": 5
}
```

- `EUROPI_MODEL` specifies the type of EuroPi module. Currently only `"europi"` is supported
- `PICO_MODEL` must be one of `"pico"` or `"pico w"`
- `CPU_FREQ` must be one of `250000000` or `125000000`
- `ROTATE_DISPLAY` must be one of `false` or `true`
- `DISPLAY_WIDTH` is the width of the screen in pixels. The standard EuroPi screen is 128 pixels wide
- `DISPLAY_HEIGHT` is the height of the screen in pixels. The standard EuroPi screen is 32 pixels tall
- `DISPLAY_SDA` is the I²C SDA pin used for the display. Only SDA capable pins can be selected
- `DISPLAY_SCL` is the I²C SCL pin used for the display. Only SCL capable pins can be selected
- `DISPLAY_CHANNEL` is the I²C channel used for the display, either 0 or 1.
- `MAX_OUTPUT_VOLTAGE` is an integer in the range `[0, 10]` indicating the maximum voltage CV output can generate.
  The hardware is capable of 10V maximum
- `MAX_INPUT_VOLTAGE` is an integer in the range `[0, 12]` indicating the maximum allowed voltage into the `ain` jack.
  The hardware is capable of 12V maximum
- `GATE_VOLTAGE` is an integer in the range `[0, 10]` indicating the voltage that an output will produce when `cvx.on()`
  is called. This value must not be higher than `MAX_OUTPUT_VOLTAGE`



# Experimental configuration

Other configuration properties are used by [experimental features](/software/firmware/experimental/__init__.py)
and can be set using a similar static configuration file. This file is located at `/config/ExperimentalConfig.json`
on the Raspberry Pi Pico. If this file does not exist, default settings will be loaded.  The following
shows the default configuration:

```json
{
    "VOLTS_PER_OCTAVE": 1.0,
}
```

- `VOLTS_PER_OCTAVE` must be one of `1.0` (Eurorack standard) or `1.2` (Buchla standard)


# Accessing config members in Python code

The firmware converts the JSON file into a `ConfigSettings` object, where the JSON keys are converted
to Python attributes.  The JSON object's keys must follow these rules, otherwise a `ValueError` will be raised:

1. The string may not be empty
1. The string may only contain letters, numbers, and the underscore (`_`) character
1. The string may not begin with a number
1. The string should be in `ALL_CAPS`

The JSON key is converted into a Python attribute of the configuration object. For example, this JSON file
```json
{
  "CLOCK_MULTIPLIER": 4,
  "HARD_SYNC": true,
  "WAVE_SHAPE": "sine"
}
```
would produce a Python object with these attributes:
```python
>>> dir(config_object)
[
  '__class__',
  '__init__',
  '__module__',
  '__qualname__',
  '__dict__',
  'to_attr_name',
  'CLOCK_MULTIPLIER',
  'HARD_SYNC',
  'WAVE_SHAPE'
]

>>> config_object.CLOCK_MULTIPLIER
4

>>> config_object.HARD_SYNC
True

>>> config_object.WAVE_SHAPE
'sine'
```

The `europi` namespace contains `.europi_config` and `.experimental_config` members that contain all of the
configuration attributes described in the sections above:

```python
>>> from europi import europi_config
>>> dir(europi_config)
[
  '__class__',
  '__init__',
  '__module__',
  '__qualname__',
  '__dict__',
  'to_attr_name',
  'CPU_FREQ',
  'DISPLAY_CHANNEL',
  'DISPLAY_HEIGHT',
  'DISPLAY_SCL',
  'DISPLAY_SDA',
  'DISPLAY_WIDTH',
  'EUROPI_MODEL',
  'GATE_VOLTAGE',
  'MAX_INPUT_VOLTAGE',
  'MAX_OUTPUT_VOLTAGE',
  'PICO_MODEL',
  'ROTATE_DISPLAY'
]
```

When you import the `europi` namespace into your project you can access the `europi_config` object like this:
```python
from europi import *

# A voltage range we can select from in a user menu
VOLTAGE_RANGE = range(0, europi_config.MAX_OUTPUT_VOLTAGE)
```

Alternatively, you can access it using the fully qualified namespace too:
```python
import europi

# A voltage range we can select from in a user menu
VOLTAGE_RANGE = range(0, europi.europi_config.MAX_OUTPUT_VOLTAGE)
```
