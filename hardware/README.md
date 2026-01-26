# Hardware Overview
There are multiple versions of the hardware documented in this directory, the original EuroPi (through-hole), the new EuroPi-SMD (surface-mount), and a stripboard version (stripboard). Each has a different build guide and bill of materials, so make sure you follow the one you want to build.

**[surface-mount](surface-mount/)**: The simplest to DIY as you only need to solder on the components which stick through the panel, i.e. the jacks, knobs etc. All of the other circuitry is soldered onto the PCB already.

**[through-hole](through-hole/)**: A slightly more in depth build as you need to solder on every component, however only through-hole components are used, so this isn't as hard as it sounds. This is the build most people have made and was previously the only publicly available build at all.

**[stripboard](stripboard/)**: A much rougher layout and does not use a PCB at all, but instead uses 'stripboard'. This hasn't been tested nearly as much as the other two, but people have successfully built it and shared their version on Discord. Not developed or maintained by Allen Synthesis.

# Hardware Specifications
All hardware variants share the same specifications as the components and schematics are the same.

## Outputs
- 1k Output Impedance
- RC filter smoothed PWM
- ~1.5kHz Maximum usable frequency (without changing RC values)
- 0-10V

## Analogue Input
- 100k Input Impedance
- 0-12V Readable Range
- Protected for ±12V (TL074 limits, MCP6002 will always clip to ±3.3V)

## Digital Input
- 100k Input Impedance
- 0.8V threshold to read as high

## OLED
- SSD1306 0.91"
- 128 x 32 pixels
- I2C Protocol
