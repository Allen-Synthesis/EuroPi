# Configuration Customization

Certain properties of the module, such as screen rotation, CPU clock speed, and Raspberry Pi Pico model, can be
set using a static configuration file.  This file is located at `/config/EuroPiConfig.json` on the
Raspberry Pi Pico. If this file does not exist, default settings will be loaded.  The following shows the
default configuration:
```json
{
    "EUROPI_MODEL": "europi",
    "PICO_MODEL": "pico",
    "CPU_FREQ": "overclocked",
    "ROTATE_DISPLAY": false,
    "DISPLAY_WIDTH": 128,
    "DISPLAY_HEIGHT": 32,
    "DISPLAY_SDA": 0,
    "DISPLAY_SCL": 1,
    "DISPLAY_CHANNEL": 0,
    "EXTERNAL_I2C_SDA": 2,
    "EXTERNAL_I2C_SCL": 3,
    "EXTERNAL_I2C_CHANNEL": 1,
    "EXTERNAL_I2C_FREQUENCY": 100000,
    "EXTERNAL_I2C_TIMEOUT": 50000,
    "MAX_OUTPUT_VOLTAGE": 10.0,
    "MAX_INPUT_VOLTAGE": 10.0,
    "GATE_VOLTAGE": 5.0,
    "MENU_AFTER_POWER_ON": false
}
```

## System

Options:
- `EUROPI_MODEL` specifies the type of EuroPi module. Currently only `"europi"` is supported. Default: `"europi"`
- `PICO_MODEL` must be one of
  - `"pico"`,
  - `"pico h"`,
  - `"pico w"`,
  - `"pico 2"`, or
  - `"pico 2w"`.
  Default: `"pico"`.
- `CPU_FREQ` specifies whether or not the CPU should be overclocked. Must be one of `"overclocked"` or `"normal"`.
  Default: `"overclocked"`
- `MENU_AFTER_POWER_ON` is a boolean indicating whether or not the module should always return to the main menu when
  it powers on.  By default the EuroPi will re-launch the last-used program instead of returning to the main menu. Default: `false`

## Display

Options:
- `ROTATE_DISPLAY` must be one of `false` or `true`. Default: `false`
- `DISPLAY_WIDTH` is the width of the screen in pixels. The standard EuroPi screen is 128 pixels wide. Default: `128`
- `DISPLAY_HEIGHT` is the height of the screen in pixels. The standard EuroPi screen is 32 pixels tall. Default: `32`
- `DISPLAY_SDA` is the I²C SDA pin used for the display. Only SDA capable pins can be selected. Default: `0`
- `DISPLAY_SCL` is the I²C SCL pin used for the display. Only SCL capable pins can be selected. Default: `1`
- `DISPLAY_CHANNEL` is the I²C channel used for the display, either 0 or 1. Default: `0`
- `DISPLAY_CONTRAST` is a value indicating the display contrast. Higher numbers give higher contrast. `0` to `255`. Default: `255`

## External I²C

Options:
- `EXTERNAL_I2C_SDA` is the I²C SDA pin used for the external I²C interface. Only SDA capable pis can be selected. Default: `2`
- `EXTERNAL_I2C_SCL` is the I²C SCL pin used for the external I²C interface. Only SCL capable pins can be selected. Default: `3`
- `EXTERNAL_I2C_CHANNEL` is the I²C channel used for the external I²C interface, either 0 or 1. Default: `1`
- `EXTERNAL_I2C_FREQUENCY` is the I²C frequency used for the external I²C interface. Default: `100000`
- `EXTERNAL_I2C_TIMEOUT` is the I²C timeout in milliseconds for the external I²C interface. Default: `1000`

## I/O voltage

Options:
- `MAX_OUTPUT_VOLTAGE` is a float in the range `[0.0, 10.0]` indicating the maximum voltage CV output can generate. Default: `10.0`
  The hardware is capable of 10V maximum
- `MAX_INPUT_VOLTAGE` is a float in the range `[0.0, 12.0]` indicating the maximum allowed voltage into the `ain` jack.
  The hardware is capable of 12V maximum. Default: `10.0`
- `GATE_VOLTAGE` is a float in the range `[0.0, 10.0]` indicating the voltage that an output will produce when `cvx.on()`
  is called. This value must not be higher than `MAX_OUTPUT_VOLTAGE`. Default: `5.0`

I/O voltage options should specify no more than 1 decimal point. i.e. `2.5` is acceptable, but `1.234` is not.  These
limits are intended for broad compatibility configuration, not for precise tuning.

If you assembled your module with the Raspberry Pi Pico 2 (or a clone featuring the RP2350 microcontroller) make sure to
set the `PICO_MODEL` setting to `"pico2"`.

# Experimental configuration

Other configuration properties are used by [experimental features](/software/firmware/experimental/__init__.py)
and can be set using a similar static configuration file. This file is located at `/config/ExperimentalConfig.json`
on the Raspberry Pi Pico. If this file does not exist, default settings will be loaded.

## Quantization

Options:
- `VOLTS_PER_OCTAVE` must be one of `1.0` (Eurorack standard) or `1.2` (Buchla standard). Default: `1.0`

## Realtime Clock (RTC)

Options:
- `RTC_IMPLEMENTATION` is one of the following, representing the realtime clock enabled on your module:
  - `""`: there is no RTC present. (default)
  - `"ds3231"`: use a DS3231 module connected to the external I2C interface
  - `"ds1307"`: use a DS1307 module connected to the external I2C interface (THIS IS UNTESTED! USE AT YOUR OWN RISK)
  - `"ntp"`: use an NTP source as the external clock. Requires wifi-supported Pico and valid network configuration
    (see WiFi connection below)
- `NTP_SERVER`: if `RTC_IMPLEMENTATION` is `ntp`, sets the NTP server to use as a clock source.
  Default: `0.pool.ntp.org`.

## Timezone

Options:
- `UTC_OFFSET_HOURS`: The number of hours ahead/behind UTC the local timezone is (-24 to +24)
- `UTC_OFFSET_MINUTES`: The number of minutes ahead/behind UTC the local timezone is (-59 to +59)

## WiFi Connection

Options:
- `WIFI_MODE`: the wireless operation mode, one of:
- `"access_point"` (default): EuroPi acts as a wireless access point for other devices to connect to
  -`"client"`: connect EuroPi to an external wireless router or accesspoint (DHCP required)
- `WIFI_SSID`: the SSID of the wireless network to connect to (in `client` mode) or to broadcast
  (in `access_point` mode). Default: `"EuroPi"`
- `WIFI_BSSID`: the optional BSSID of the network to connect to (e.g. access point MAC address). Default: `""`
- `WIFI_PASSWORD`: the password of the wireless network. Default: `"europi"`
- `WIFI_CHANNEL`: the WiFi channel 1-13 to use in `access_point` mode; ignored in `client` mode. Default: `10`

WiFi options are only applicable if EuroPi has the Raspberry Pi Pico W or Raspberry Pi Pico 2 W board;
other Pico models do not contain wireless support.

**NOTE**: At the time of writing, the latest Micropython firmware for the Raspberry Pi Pico 2 W has a bug in
which the wireless card will not reliably work if the CPU is overclocked. If you have problems using wifi please
try changing `CPU_FREQ` to `normal` in `EuroPiConfig.json`.

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

`europi.py` contains objects called `europi_config` and `experimental_config` which implement the core & experimental
customizations described in the sections above.

When you import `europi` into your project you can access the `europi_config` object like this:
```python
from europi import *

# A voltage range we can select from in a user menu
VOLTAGE_RANGE = range(0, europi_config.MAX_OUTPUT_VOLTAGE)
```

Alternatively, you can access it using the fully qualified namespace:
```python
import europi

# A voltage range we can select from in a user menu
VOLTAGE_RANGE = range(0, europi.europi_config.MAX_OUTPUT_VOLTAGE)
```

# Note on Booleans

Python uses `True` and `False` to represent boolean values (starting with upper-case letters), but JSON uses `true` and
`false` (starting with lower-case letters).

This is an unavoidable inconsistency between the configuration file and the Python source code. When modifying the JSON
file to modify your configuration, make sure to use correct JSON boolean names, not Python names.
