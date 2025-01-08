# Realtime Clock

EuroPi does not natively include a realtime clock. An external clock module can be
installed and configured to provide time and date information to EuroPi's programs.

## What is a realtime clock?

A realtime clock is a clock with a battery that will continue to track the time
even when your synthesizer is powered-off. This allows EuroPi to know what the
current date and time are, even if the module has been turned off for some time.

Without a realtime clock, the only way to get the time is by using Micropython's
`time.ticks_ms()` or `time.ticks_us()` functions; these return the ticks (in
milliseconds or microseconds) since the module was powered-on, but won't accurately
represent the real-world time and date.

## What clock should I buy?

There are many I2C compatible realtime clock modules available. EuroPi has been
tested with the DS3231, though the similar DS1307 may also work.

These modules can be bought online from a variety of sources, for example:
- https://www.amazon.ca/dp/B09S8VF9GL
- https://shop.kincony.com/products/ds3231-rtc-module
- https://www.mouser.ca/ProductDetail/Analog-Devices-Maxim-Integrated/DS3231MPMB1
- https://www.aliexpress.com/item/1005001875764383.html

## How do I connect the clock?

The realtime clock should be connected to EuroPi's I2C header pins, located on the
rear of the module, between the Raspberry Pi Pico and the power header.

<img src="https://github.com/user-attachments/assets/17c94bbf-e5b6-44f9-9002-5dec3135c108" width="360">

_EuroPi's I2C header (circled)_

Depending on the size and depth of your synthesizer's case there are a few ways you
can mount the clock. For deep cases, the easiest solution is to simply use a standoff
to connect the clock to the Raspberry Pi Pico:

<img src="https://github.com/user-attachments/assets/5d028add-ff5d-42ee-83a7-dfe89ce1b043" width="360"> <img src="https://github.com/user-attachments/assets/86725f58-bea4-415f-9be7-94651ff3c728" width="360">

_The DS3231 RTC mounted to the Raspberry Pi Pico using a standoff_

For shallower cases, you can attach header pins and jumper wires to a pice of perfboard
or plastic, and mount the clock vertically.

TODO: pictures of the vertical mount

Other mounting solutions are also possible, for example attaching the clock behind a
blank panel or using double-sided foam tape to attach it directly to the inside of your
case. As long as the clock is securely fastened so it won't move around, and is connected
to the I2C header on EuroPi, it should be fine.

## How do I configure the clock?

The default external I2C settings from `europi_config` should be used, unless you have
a specific need to change them in `config/EuroPiConfig.json` (for example, your RTC module
needs a specific I2C frequency):
```json
{
    "EXTERNAL_I2C_SDA": 2,
    "EXTERNAL_I2C_SCL": 3,
    "EXTERNAL_I2C_CHANNEL": 1,
    "EXTERNAL_I2C_FREQUENCY": 100000,
    "EXTERNAL_I2C_TIMEOUT": 50000,
}
```

You will also need to edit `config/ExperimentalConfig.json` to specify what RTC module you
are using:
```json
{
    "RTC_IMPLEMENTATION": "ds3231"
}
```

See [Configuration](/software/CONFIGURATION.md) for more details on EuroPiConfig.json and
ExperimentalConfig.json.

## How do I set the time?

When you first connect your clock, it will probably not indicate the correct time. To set
the realtime clock's internal memory to the current time, connect and configure the clock
as described above, and then connect EuroPi to Thonny's Python terminal.

Inside the terminal, run the following commands:
```python
from experimental.rtc import clock, Month, Weekday
clock.source.set_datetime((2025, Month.JUNE, 14, 22, 59, 0, Weekday.THURSDAY))
```

The example above sets the date to Thursday, 25 June, 2025 at 22:59:00. Modify the
year, month, day, hour, minute, second, and weekday to the current UTC date and time
when you run the command.

Once you've done this, restart your EuroPi and run the following command to make sure
the clock is properly configured:
```python
from experimenta.rtc import clock
print(clock)
```
You should see the current date and time printed.

## Troubleshooting

If you see a warning of the form
```
WARNING: Oscillator stop flag set. Time may not be accurate.
```
when you print the time, this means the clock is not actually running and won't track the time
when the module is powered-off. Setting the time and date using the `set_datetime` method
described above should start the clock automatically, but if it does not you should refer
to your RTC module's datasheet to check how to clear the oscillator stop bit.
