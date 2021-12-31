# Build Guide

This document will go through the assembly of the EuroPi module.  
If you have bought only a Panel + PCB kit, you will need to also buy all of the components found in the [bill of materials](/hardware/bill_of_materials.md).  
  
This build is entirely through-hole (not even any pre-soldered SMD components!) so don't worry if you're fairly new to DIY, these instructions should be all you need to make your module!
  
## Required tools
- Soldering Iron + Solder
- Wire Snips / Scissors
- Multimeter (Very nice to have but non-essential)
- Two unique voltage sources within the range 0-10V (Only necessary if you wish to calibrate the module for increased accuracy)

## Assembly Preparation

Before you begin assembly, I recommend first grouping your components into these categories, either in little bags or just on the top of your work surface.  
You have likely already checked your Bill of Materials, but I would still suggest double checking that you have the specified number of each component in each category to prevent any disappointment half-way through the build.

#### Boards
- x1 Pico PCB
- x1 Jack PCB
- x1 Front Panel
- x1 Raspberry Pi Pico
- x2 20 Way 1 Row Male 2.54mm Header (If not already soldered to the Pico)
- x2 20 Way 1 Row Female 2.54mm Header

#### Power Supply Components
- x1 Eurorack Power Connector
- x1 Eurorack 16 to 10 pin Power Cable
- x1 7805 Linear Voltage Regulator
- x3 Schottky Diode

#### Resistors
- x20 1k
- x3 10k
- x3 22k
- x8 100k
- x6 220k
 
#### Capacitors
- x1 1uF
- x12 100nF
- x2 10uF
 
#### Front Panel Components
- x8 Thonkiconn Jack + Nut
- x2 Potentiometer + Nut
- x2 Knob
- x2 Push Button
- x1 OLED Display
- x1 4 Way 1 Row Male 2.54mm Header (If not already soldered to the OLED Display)
- x6 LEDs

#### Headers
- x3 8 Way 2 Row Male 2.54mm Header
- x4 2 Pin 2.54mm Shunt / Jumper
- x2 8 Way 2 Row Female 2.54mm Header

#### Extra Through Hole Components
- x2 14 Pin IC Socket
- x1 8 Pin IC Socket
- x2 TL074 Operational Amplifier
- x1 MCP6002 Operational Amplifier
- x1 NPN Transistor
- x1 Schottky Diode


## Assembly

The basic process of the assembly is simply soldering all of the components for each category listed above in order (with some exceptions), with certain tests along the way if you want to be safe.  

### Power Supply Soldering
This section only relates to the Pico PCB so you can put the Jack PCB to the side for a bit.

#### Solder the Eurorack power connector

#### Solder the 7805 Linear Voltage Regulator

#### Solder in the Schottky Diodes (D2 - D4)


### (Optional) Multimeter Tests
Use your multimeter set to continuity mode for these tests.

#### Check the continuity of +12V to the middle left pin of the TL074-2 PCB footprint

#### Check the continuity of -12V to the middle right pin of the TL074-2 PCB footprint

#### Check the continuity of Ground to the left/bottom pin of the C12 PCB footprint

#### Check that there is no continuity between +12V and -12V, between +12V and Ground, and between -12V and Ground

If there is continuity on any checks where there shouldn't be, or there isn't on checks where there should, then make sure your solder joints are good and that there is no dirt or stray solder bridging any connections. Also make sure that your diodes and power cable are all the correct orientation.

### Smoke Test

#### Connect the newly soldered power connector to your Eurorack Power supply with no other modules connected
Check for any smoke  or discolouration of the PCB around the power connector, and immediately unplug if either occur.  
If all is groovy, continue with the assembly. Otherwise, double check all your solder joints and your power supply.


### (Optional) Multimeter Tests

#### While plugged in and turned on, measure the voltage from Ground to the pin second from the top on the right of the Pico footprint pins
This voltage should be very close to 5V (within as much as half a volt is fine and usable, but a bigger error than that does indicate a problem with the regulator or your soldering). If it isn't, make sure you have the correct voltage regulator (7805), and that all your solder joints are solid.


### Solder the resistors
The resistors are on both the Pico PCB and the Jack PCB, so get these both ready.  

#### Start with all of the 1k resistors (R1 - R20)
  
#### Then the 22k resistors (R21 - R23)
  
#### Then the 10k resistors (R24 - R26)
  
#### Then the 100k resistors (R27 - R34)
  
#### Then the 220k resistors (R35 - R40)


### Solder the capacitors
The capacitors are also on both PCBs, so keep them both on hand.
  
#### Start with the 1uF capacitors (C1 - C2)
  
#### Then the 100nF capacitors (C3 - C14)
  
#### Then the 10uF capacitors (C15 - C16)
  
  
### Solder the extra through hole components

#### Solder the remaining Schottky Diode (D1) 
  
#### Solder the NPN Transistor (Q1)
  
#### Solder both 14 Pin IC Sockets
  
#### Solder the 8 Pin IC Socket

#### Don't put the ICs into their sockets yet, as the heating of the board can damage them
  
  
### Solder the headers

#### Solder the the male 8 Way 2 Row headers to the Pico PCB
  
#### Solder the 20 Way 1 Row female headers to the Pico PCB

#### Solder the 20 Way 1 Row male headers to the Raspberry Pi Pico (If not pre-soldered)
  
#### Solder the female 8 Way 2 Row headers to the Jack PCB


### OLED Configuration
There are two pin configurations that the OLED used in this build commonly comes in, which are labelled on the board 'THT' (The Pi Hut), and 'CPC' (CPC, AliExpress, most other suppliers).  
The Pi Hut display is preferable as it does not have pre-soldered headers, so is easier to mount on the board. However the CPC display is still entirely usable.  
  
This configuration setup allows you to tell the module which display you are using, as their pins are ordered differently:  
TPH: VCC, GND, SDA, SCL  
CPC: SDA, SCL, VCC, GND
  
Don't ask my why there is still not a standard for I²C pin layout in the year 2021, but here we are, and here is how to tell the module which layout you are using:
  
This next stage is technically optional; if you know you have got the right display and won't be changing it, you can just make the 4 connections using solder or snipped off resistor legs rather than using a header and jumpers.  

#### Solder the OLED configuration header

#### Place the 4 shunts/jumpers over the pins in the direction shown on the PCB for your display
For TPH, the shunts should all be vertical, and for CPC they should all be horizontal.


### Solder the OLED Display in place
This is quite an awkward operation as the distance the headers need to occupy is not standard to the lengths that 2.54mm headers come in. If you are using a CPC display, your headers are probably pre-soldered, in which case you need to press the display down onto the configuration header you previously soldered, and use something like an elastic band to hold it in place.  
  
If your display is CPC, the pins will be flush with the PCB if it's at the correct height, which is difficult but possible to solder.  
  
If your display is TPH, you can either solder pins and do it the same way as the CPC method, or use extra-long pin headers instead which will make the soldering process easier, as they will protrude far enough to get a better solder joint.

#### Solder the pins
As described above, the process will be slightly different if your pins end up being flush or protruding, but you should solder one pin first and then make sure the display is parallel in both axis; parallel to the PCB, and parallel to edge of the module.
  
Once the display is parallel, carefully solder the remaining pins, and then remove whatever method you used to hold the display in place.


### Solder the remaining front panel components

#### Solder the Thonkiconn jacks

#### Solder the LEDs, making sure to orient the shorter leg with the white stripe on the PCB.

#### Solder the Push Buttons with the flat side lined up with the PCB footprint

#### Solder the potentiometers. You do not need to solder the 'lugs' on either side, only the three small pins in a line.


### Finish off the assembly

#### Screw the PCB standoff onto the Jack PCB on the opposite side to the front panel components

#### Push the two PCBs together, keeping them both straight to avoid bending the pins

#### Screw the into the PCB standoff through the Pico PCB to hold the two PCBs together firmly
Don't over-tighten so hard that you damage the PCB, but you also don't want this to rattle loose so make sure it is secure.

#### Push the Pico into its slot

#### Finally, pop the TL074 and MCP6002 Op-Amps into their respective sockets


### Perform a final smoke test
If this test fails, try to see where the smoke is coming from and replace any components that appear damaged. Do all the continuity checks again before switching on the power a second time.

#### If you have any issues with the build process or programming that are not covered in the [troubleshooting guide](/troubleshooting.md) then please drop us an email at [contact@allensynthesis.co.uk](mailto:contact@allensynthesis.com)

## Admire your handiwork!

#### Share photos of your build with us on [Instagram](https://www.instagram.com/allensynthesis/), or [email us](mailto:contact@allensynthesis.com)!

#### Now just follow the [programming instructions](/software/programming_instructions.md) to get ready to use your new EuroPi!
