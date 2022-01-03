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
4. Re-flash the firmware using the 'flash_nuke.uf2', and then re-flash it again using the most recent firmware


## EuroPi Hardware Error

```diff
- EuroPi Hardware Error:
- Make sure the OLED display is connected correctly
```

This means that the Pico cannot detect the OLED display.
#### Steps to fix
1. Make sure that the solder joints between the OLED board and the PCB are secure and free of dirt
2. If you have a multimeter, test the continuity of each pin with the appropriate pin on the Pico according to [the pinout](hardware/europi_pinout.pdf)
3. Make sure your PCB standoffs are screwed on tightly; if the two board slip apart by any more than a millimetre or two then the connection will not be made
4. Make sure your OLED matches one of the two compatible pin configurations as outlined in the [build guide](https://github.com/roryjamesallen/EuroPi/blob/main/hardware/build_guide.md#oled-configuration)


## Backend terminated or disconnected

```diff
- Backend terminated or disconnected. Use 'Stop/Restart' to restart.
```

The module has become disconnected from your computer.
#### Steps to fix
1. Try pressing Stop/Restart
2. Follow the steps to fix for 'EuroPi Hardware Error'
