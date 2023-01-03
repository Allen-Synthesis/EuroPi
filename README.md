# EuroPi

<p>
  <a href="https://discord.gg/JaQwtCnBV5">
        <img src="https://discordapp.com/api/guilds/931297838804127794/widget.png?style=shield"
            alt="chat on Discord">
  </a>
  <a href="https://www.reddit.com/r/EuroPi/">
        <img src="https://img.shields.io/reddit/subreddit-subscribers/europi?style=social"
            alt="chat on Discord">
  </a>
  
</p>
  
The EuroPi is a fully user reprogrammable module based on the [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/), which allows users to process inputs and controls to produce outputs based on code written in Python. The entire project is open-source.


This repository relates to the EuroPi module, however some users may be expecting to see what is now referred to as the 'EuroPi Prototype'. The repository for this (now deprecated) module [can be found here](https://github.com/roryjamesallen/EuroPi-Prototype)

You can find more about this (including a project diary) and other projects of mine on [my website](https://www.allensynthesis.co.uk)

![github banner](https://user-images.githubusercontent.com/79809962/157898134-44cc0534-ac3b-4051-9773-a3be95ba4602.jpg)

## Capabilities

* 6 0-10V Control Voltage outputs, each with indicator LED
* 2 Knobs with 12 bit resolution
* 2 Push Buttons
* 1 0-12V Control Voltage input with 12 bit resolution
* 1 Digital input for external clocking or gate sources
* 128x32 OLED Display
* I²C expansion header on the rear for extra sensors or outputs

### Improvements on the Prototype version

* All outputs are the full Eurorack unipolar range of 0-10V, previously only 0-3.3V
* Two inputs, previously no way to accept input from other modules
* The buttons have hardware debouncing to allow users to change out capacitor values for reduced accidental 'double click'
* A 10 pin Eurorack shrouded power header is now used to prevent accidental reverse powering of the module
* The 5V supply for the Pico is now regulated down from the +12V supply, so no 5V rail is required from your Eurorack power supply
* The power supply is now diode protected to prevent back-powering your rack when the module is connected via USB
* All jacks are protected from overvoltage input (previously the Pico GPIO pin was directly exposed to any input, potentially leading to damage)

### Documentation

**Hardware**: Details of the hardware can be found at [hardware README](hardware/README.md). Additionally the [BoM](hardware/bill_of_materials.md) and the [build guide](hardware/build_guide.md) can be found in the hardware folder.


**Software**: Before using any of the software, follow the instructions in [programming_instructions.md](software/programming_instructions.md) to set up and calibrate your module.

A list of user contributed scripts and their usage can be found in [contrib/README.md](software/contrib/README.md).
There is also a [YouTube playlist](https://www.youtube.com/playlist?list=PLbingtr9KGPUdIODLWgzgAdIyN497YyEs) showcasing EuroPi and some of the different scripts available.

The EuroPi firmware API documentation can be found at https://allen-synthesis.github.io/EuroPi/. This documentation will explain all of the available features of the EuroPi firmware API. It also includes some examples of how to use various features of the firmware as well as [interesting_things.md](software/interesting_things.md).

If you would like to extend any of the features of the EuroPi software, you can view the firmware source code at [europi.py](software/firmware/europi.py).

### Issues
If you find any bugs, either in the software, the hardware, or the documentation, please create an Issue by clicking the 'Issue' tab along the top.  
Please feel free to create any issue you see fit, I'll either attempt to fix it or explain it.  
There are Issue templates available, so please choose whichever is most relevant, depending on if your Issue is a hardware or software bug, if it's a documentation error or suggestion, if it's a question about the project as a whole, or a suggestion about the project as a whole.


### License

This module, and any documentation included in this repository, is entirely "free" software and hardware, under different licenses depending on the software, hardware, and documentation itself.

* Software: [Apache 2.0](software/LICENSE)
* Hardware: [CERN OHL-S v2](hardware/LICENSE)
* Documentation: [CC0 1.0](LICENSE)

Anyone is welcome to design their own versions of the idea, or modify my designs.
The only thing I would ask is that you refrain from using the brand name 'Allen Synthesis' on your DIY builds if they have modified my files in any way, just to prevent any confusion if they end up being re-sold or distributed. This is in line with section 8.2 of the CERN license. You may use the brand name if you have simply copied the files from this repository to replicate without modification.
  
If you have a bug fix or improvement that you think is worth sharing, then feel free to send over any pictures or documentation and it can be merged with the main project!
 
### Disclaimer
 
Recreate any of the files found in this repository at your own risk; I will attempt to solve any issues that you might have with my designs, but I can't guarantee that there are not minor bugs in any of the documents, both hardware and software.
