## Overclocking
This code will read the analogue input and replicate the voltage read at CV output 1.
The second line will overclock the Pico to 250Mhz (the default clock speed is 125MHz).
This is as high as I have managed to safely overclock the Pico without causing unexpected crashes.
The '1' sent as a parameter to the read_voltage method, overrides the default 256 samples (usually averaged for higher accuracy), and only samples the analogue input once, making it much faster (but less accurate).

```python

from europi import *
import machine

machine.freq(250_000_000)

while True:
    input_voltage = ain.read_voltage(1)
    cv1.voltage(input_voltage)

```

This code proves the speed of the Pico to the extent that if you send audio to the analogue input, you can hear a very bitcrushed but recognisable version of it at CV output 1.


## Connecting I2C devices
EuroPi has 1 I2C channel available for connecting external devices. The header pins for this connection are located
between the Pico and the module's power connector.

To use an external I2C device, you will need to connect it to the ground, 3.3V supply, SDA, and SCL pins of the I2C
header. You must also specify the frequency of the I2C channel by creating or modifying `config/EuroPiConfig.json`
on the module:
```json
{
    "EXTERNAL_I2C_FREQUENCY": 400000
}
```
Specify the desired frequency with the `EXTERNAL_I2C_FREQUENCY` key in the JSON object. The default frequency is
`100000` (100k). Rates of up to 1M can be specified, but nothing faster than 400k has been officially tested.
(The OLED display connected to the other I2C channel uses a frequency of 400k).

By default the I2C channel uses a timeout of 50000 microseconds. To change this, set the `EXTERNAL_I2C_TIMEOUT`
parameter in `config/EuroPiConfig.json`:
```json
{
    "EXTERNAL_I2C_TIMEOUT": 100000
}
```
The timeout value specificed is in microseconds.

To use the external I2C connection in your programs, use
```python
from europi import external_i2c

external_i2c.writeto(...)
external_i2c.readfrom(...)
# etc...
```

The `external_i2c` object is an instance of `machine.I2C`, so refer to [the official documentation](https://docs.micropython.org/en/latest/library/machine.I2C.html)
for more information on using I2C.
