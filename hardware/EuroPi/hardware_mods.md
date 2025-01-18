# Hardware Mods

This file documents some common hardware modifications to EuroPi. These modifications are wholly
at your own risk; if performed wrong they could cause damage to your module!

## Alternative to OLED jumper wires

Instead of [soldering jumper wires](/hardware/EuroPi/build_guide.md#oled-configuration) to configure
the OLED, you can instead install a 2x4 bank of headers and use 4 jumpers. This makes it easy to
reconfigure the OLED connection, which may be useful if you ever need to replace the display.

<img src="https://github.com/user-attachments/assets/a308995c-de30-41ae-a7e0-2f714e3f8513" width="420">

_Header pins and jumpers used in the CPC orientation_

## Reducing analogue input noise

The original analogue input stage, as designed by Émilie Gillet (of Mutable Instruments fame) includes
a 1nF capacitor located in parallel with the final resistor:

<img src="https://github.com/user-attachments/assets/02dbf7f8-5e39-422a-82a9-104fbe0589e7" width="600">

_The input stage of Mutable Instruments Braids. Note the `1n` capacitor in the upper-right._

If you find your EuroPi's V/Oct outputs are incorrect, or are seeing an undesirable amount of jitter on
`AIN`, you can add a 1nF capacitor in parallel with `R23`. The easiest way to do this is to _carefully_
solder the 1nF capacitor directly to the back-side of `R23`, as shown below:

<img src="https://github.com/user-attachments/assets/2d7d6dcc-7dc1-433d-98c0-6ff8be978cc7" width="360">

_A 1nF capacitor soldered to the back-side of the EuroPi PCB, in parallel with `R23`_

After soldering the 1nF capactor in place, you should [recalibrate EuroPi](/software/firmware/tools/calibrate.md).
