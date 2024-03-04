# Troubleshooting the EuroPi module

This document should help you fix any problems you might be having with the hardware or software of the module.
If you have any other issues that aren't covered in this document, please create an Issue on this GitHub repository using the template.
You can search through this file for the error message you are getting or just press Ctrl-F and paste the first line of the message given in Thonny.

## No inputs or outputs are working

#### Steps to fix
1. Make sure your module is connected to both USB for programming and rack power for ±12V supply
2. Make sure the Pico and Jack PCBs are firmly pressed together, and held by the standoff

## Couldn't find the device automatically

```diff
- Couldn't find the device automatically.
- Check the connection (making sure the device is not in bootloader mode) or choose
- "Configure interpreter" in the interpreter menu (bottom-right corner of the window)
- to select specific port or another interpreter.
```

This means that your device is either not connected, or not being detected.
#### Steps to fix
1. Make sure the USB cable is connected firmly to both the Pico and your computer
2. Make sure your USB cable is capable of data transfer rather than just power
3. Re-flash the firmware by following the process set out in the [programming instructions](/software/programming_instructions.md)
4. Re-flash the firmware using the 'flash_nuke.uf2' found on the [Adafruit website](https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython), and then re-flash it again using the most recent firmware


## Calibration gets stuck on 10V

This means that the value the module recorded for 10V when you were sending in voltages to the analogue input cannot be reached by the CV output.
This could mean either:
1. The value you sent in for 10V was more than 10V
2. The module actually cannot reach 10V

To test if it is 1 or 2, first retry calibration, making sure the voltages you send in are accurate (never more than 10V). Measure this with a multimeter if you can to be sure.

If this doesn't fix the issue, then you know that your module cannot reach 10V on its own. There are a few things this could be:
1. The LEDs you used draw more current than the standard ones in the BOM, and are thus causing the output voltage to drop below 10V
2. There is a bridge/missing solder joint which is causing the output stage to have a lower gain factor than it should, and thus can't reach 10V
3. (Very unlikely) The output jack is broken and is not connected to the circuit properly

The easiest way to test a few of these possibilities at once is to set the output to the highest value possible, with this code:
```
from europi import *
cv1._set_duty(65535)
```
Simply create a new file with only this code in it, and then run the code with the module connected.
Now, use a multimeter to measure the voltage at the end of a mono cable plugged into the jack, and see if it is above 10V. As long as it is over 10V, even if only by about 0.5V, then this proves that the problem is not any of the above. If this is the case (the voltage is above 10V) then reflash the firmware using the instructions at the bottom of [the steps to fix above](#steps-to-fix-1).

If it was less than 10V, then check all of the solder joints on both PCBs, but especially all of the ones around the TL074 op-amps. If you see any joint that looks like it could be either bridging two pins or cracked, then clean up the joint with some solder braid or a solder sucker (a braid is preferred as it's less likely to damage the board) and re-solder.

If none of this solves the issue, then please post in the support channel of the [Discord server](https://discord.gg/JaQwtCnBV5) with photos of your PCBs, and we can see if we can spot anything!

## EuroPi Hardware Error

```diff
- EuroPi Hardware Error:
- Make sure the OLED display is connected correctly
```

This means that the Pico cannot detect the OLED display.
#### Steps to fix
1. Make sure that the solder joints between the OLED board and the PCB are secure and free of dirt
2. If you have a multimeter, test the continuity of each pin with the appropriate pin on the Pico according to [the pinout](hardware/EuroPi/europi_pinout.pdf)
3. Make sure your PCB standoffs are screwed on tightly; if the two board slip apart by any more than a millimetre or two then the connection will not be made
4. Make sure your OLED matches one of the two compatible pin configurations as outlined in the [build guide](hardware/EuroPi/build_guide.md#oled-configuration)


## Backend terminated or disconnected

```diff
- Backend terminated or disconnected. Use 'Stop/Restart' to restart.
```

The module has become disconnected from your computer.
#### Steps to fix
1. Try pressing Stop/Restart
2. Follow the steps to fix for 'EuroPi Hardware Error'
