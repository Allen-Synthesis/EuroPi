# Daily Random

Generates pseudo-random gate and CV patterns based on the current date and time.

## I/O Assignments

- `ain`: not used
- `din`: external clock input
- `b1`: not used
- `b2`: not used
- `k1`: not used
- `k2`: not used
- `cv1`: daily gate sequence (updates at midnight UTC)
- `cv2`: hourly gate sequence (updates at the top of every hour)
- `cv3`: minute gate sequence (updates at the top of every minute)
- `cv4`: daily CV sequence (updates at midnight UTC)
- `cv5`: hourly CV sequence (updates at the top of every hour)
- `cv6`: minute CV sequence (updates at the top of every minute)

## Required Hardware

This script _can_ be used on a normal EuroPi, but will result in highly predictable
patterns. For best result, connect a Realtime Clock (RTC) to EuroPi's secondary I2C
header pins, located on the underside of the board.

## Installing the clock

TODO: pictures of mounting a DS3231

## Configuring the clock

The default external I2C settings from `europi_config` should be used, unless you have
a specific need to change them in `config/EuroPiConfig.json`:
```json
{
    "EXTERNAL_I2C_SDA": 2,
    "EXTERNAL_I2C_SCL": 3,
    "EXTERNAL_I2C_CHANNEL": 1,
    "EXTERNAL_I2C_FREQUENCY": 100000,
    "EXTERNAL_I2C_TIMEOUT": 50000,
}
```

You will also need to edit `config/ExperimentalConfig.json`:
```json
{
    "RTC_IMPLEMENTATION": "ds3231"
}
```

Once installed and configured, if you have not already set the clock's time, you can do so by
connecting your EuroPi to Thonny's Python terminal and running the following commands:
```python
from experimental.rtc import clock, Month, Weekday
clock.source.set_datetime(clock.source.set_datetime((2025, Month.JUNE, 14, 22, 59, 0, Weekday.THURSDAY)))
```
You should change the day and time to match the current UTC time.
