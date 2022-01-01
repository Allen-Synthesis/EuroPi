# Build Guide

This document will go through the assembly of the EuroPi module.  
If you have bought only a Panel + PCB kit, you will need to also buy all of the components found in the [bill of materials](/hardware/bill_of_materials.md).  
  
This build is entirely through-hole (not even any pre-soldered SMD components!) so don't worry if you're fairly new to DIY, these instructions should be all you need to make your module!
  
## Required tools
- Soldering Iron + Solder
- Wire Snips / Scissors
- Multimeter (Very nice to have but non-essential)


## Pico PCB

The 'Pico PCB' is the PCB with the outline of the Pico on it.  
The 'front' of the Pico PCB is the side with the actual Raspberry Pi Pico on it, and the 'back' is the side with the transistor outline on it.

### Resistors

#### Solder the 1k resistors to the front (R1, R2, R3, R4)

#### Solder the 22k resistors to the front (R21, R22, R23)

#### Solder the 100k resistors to the front (R28, R29, R30, R31, R32, R33, R34)

#### Solder the 220k resistors to the front (R35, R36, R37, R38, R39, R40)

#### Solder the 10k resistors to the back (R24, R25, R26)

#### Solder the 100k resistor to the back (R27)


### Diodes

#### Solder the Schottky diodes to the front (D2, D3, D4), taking care of the polarity

#### Solder the Schottky diode to the back (D1), taking care of the polarity


### Small Capacitors

#### Solder the 100nF capacitors to the front (C3, C4, C5, C6, C9, C10, C11, C12, C13, C14)


### IC Sockets

#### Solder the 14 Pin IC sockets to the front (TL072-1, TL072-2), lining up the notch with the white square on the PCB

#### Solder the 8 pin IC socket to the front (MCP6002), lining up the notch with the white square on the PCB


### Transistor

#### Solder the NPN transistor to the back (Q1), lining up the flat edge with the line on the PCB


### Medium Capacitors

#### Solder the 1uF capacitors to the front (C1, C2), taking care of the polarity


### Headers

#### Solder the female headers to the back

#### Solder the shrouded power header to the front

#### Solder the I²C header to the front

#### Solder the female Pico headers to the front


### Large Capacitors

#### Solder the 10uF capacitors to the front (C15, C16), taking care of the polarity


### 7805

#### Solder the 7805 power regulator to the front, with the metal side in line with the white stripe on the PCB



## Jack PCB

The 'Jack PCB' is the remaining board, with the outlines for the front panel components.  
The 'front' of the Jack PCB is the side with the OLED, jack, and button outlines, and the 'back' is the side with the OLED configuration diagram.

### Resistors

#### Solder the 1k resistors to the back (R7, R8, R9, R10, R11, R12, R13, R14, R15, R16, R17, R18, R19, R20)


### Small Capacitors

#### Solder the 100nF capacitors to the back (C8, C9). If your board has a polarity marking, ignore it.


### Headers

#### Solder the male headers to the back

#### OLED Configuration
There are two pin configurations that the OLED used in this build commonly comes in, which are labelled on the board 'THT' (The Pi Hut), and 'CPC' (CPC, AliExpress, most other suppliers).  
The Pi Hut display is preferable as it does not have pre-soldered headers, so is easier to mount on the board. However the CPC display is still entirely usable.  
  
This configuration setup allows you to tell the module which display you are using, as their pins are ordered differently:  
TPH: VCC, GND, SDA, SCL  
CPC: SDA, SCL, VCC, GND
  
Don't ask my why there is still not a standard for I²C pin layout in the year 2021, but here we are, and here is how to tell the module which layout you are using:
  
This next stage is technically optional; if you know you have got the right display and won't be changing it, you can just make the 4 connections using solder or snipped off resistor legs rather than using a header and jumpers.  

#### Solder the OLED Configuration Header to the back (only if choosing to use this method rather than bridging with solder or resistor legs)

#### Place jumpers/shunts over the pins so that the connections are made according to the diagram on the PCB, either all 4 vertical or all 4 horizontal.

#### If using solder instead, then make the 4 connections according to the diagram without soldering on the header.


### Front Panel Components

#### Solder the push buttons to the front (SW1, SW2)

#### Solder the OLED Display to the front
This is quite an awkward operation as the distance the headers need to occupy is not standard to the lengths that 2.54mm headers come in. If you are using a CPC display, your headers are probably pre-soldered, in which case you need to press the display down onto the configuration header you previously soldered, and use something like an elastic band to hold it in place.  
  
If your display is CPC, the pins will be flush with the PCB if it's at the correct height, which is difficult but possible to solder.  
  
If your display is TPH, you can either solder pins and do it the same way as the CPC method, or use extra-long pin headers instead which will make the soldering process easier, as they will protrude far enough to get a better solder joint.

#### Place the potentiometers (VR1, VR2) onto the front but don't solder yet

#### Place the jacks (J1, J2, J3, J4, J5, J6, J7, J8) onto the front but don't solder yet

#### Place the LEDs (LED1, LED2, LED3, LED4, LED5, LED6) onto the front but don't solder yet, lining up the short leg with the white stripe on the PCB

#### Push the front panel onto the components, lining up the LEDs so they are flush

#### Place an elastic band or hair bobble around the PCB and panel to hold them together

#### Solder all the components from the back


## Finish off the assembly

#### Screw the PCB standoff onto the Jack PCB so that the standoff is on the back and the screw on the front

#### Push the two PCBs together, keeping them both straight to avoid bending the header pins

#### Screw the second screw into the PCB standoff through front of the Pico PCB to hold the two PCBs together firmly
Don't over-tighten so hard that you damage the PCB, but you also don't want this to rattle loose so make sure it is secure.

#### If not already soldered, solder the headers to the Pico so that they are on the opposite side to the black integrated chips

#### Push the Pico into its slot on the Pico PCB

#### Finally, pop the TL074 and MCP6002 Op-Amps into their respective sockets


### (Optional) Multimeter Tests
Use your multimeter set to continuity mode for these tests.

#### Check the continuity of +12V to the middle left pin of the TL074-2 op-amp

#### Check the continuity of -12V to the middle right pin of the TL074-2 op-amp

#### Check that there is no continuity between +12V and -12V, between +12V and Ground, and between -12V and Ground on the power header

If there is continuity on any checks where there shouldn't be, or there isn't on checks where there should, then make sure your solder joints are good and that there is no dirt or stray solder bridging any connections. Also make sure that your diodes and power cable are all the correct orientation.

### Smoke Test

#### Connect your module to your Eurorack power supply without any other modules connected
Make sure the cable is connected so that the 'key' on the cable slots into the notch on the header, and the red stripe is on the bottom side of the module.
Turn on your power supply and check for any smoke or discolouration of the PCB around the power connector, and immediately unplug if either occur.  
If all is groovy, the congratulations, you've finished building your EuroPi!



## Admire your handiwork!

#### If you have any issues with the build process or programming that are not covered in the [troubleshooting guide](/troubleshooting.md) then please drop us an email at [contact@allensynthesis.co.uk](mailto:contact@allensynthesis.com)

#### Share photos of your build with us on [Instagram](https://www.instagram.com/allensynthesis/), or [email us](mailto:contact@allensynthesis.com)!

#### Now just follow the [programming instructions](/software/programming_instructions.md) to get ready to use your new EuroPi!
