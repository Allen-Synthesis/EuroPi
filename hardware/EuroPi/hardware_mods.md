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

## Heatsink installation

Several vendors sell aluminium or copper heatsink blocks that can be installed on the Raspberry Pi Pico's processor
to help dissipate heat. If you find your EuroPi's CPU getting too warm during operation, you may find installing
a heatsink beneficial.

Most commercially-made heatinks have a self-adhesive, thermally-conductive pad on the back. Simply peel off the
backing and carefully press the heatink directly onto the CPU. Make sure the Pico is powered off while doing this,
and follow the manufacturer's guidelines for ESD protection to avoid accidentally damaging the electronics.

<img src="https://github.com/user-attachments/assets/09e3aa3e-d4bc-4956-9ea6-2e49a877a6ef" width="360">

_A Raspberry Pi Pico with an aluminium heatsink installed on the CPU_
