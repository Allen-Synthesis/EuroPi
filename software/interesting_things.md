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
