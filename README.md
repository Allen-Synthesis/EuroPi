[![discord members](https://discord-live-members-count-badge.vercel.app/api/discord-members?guildId=931297838804127794)](https://discord.gg/JaQwtCnBV5) [![Subreddit subscribers](https://img.shields.io/reddit/subreddit-subscribers/europi)](https://www.reddit.com/r/EuroPi/) [![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Allen-Synthesis/Europi)](https://github.com/Allen-Synthesis/EuroPi/releases)
# EuroPi
The EuroPi is a user reprogrammable [Eurorack](https://en.wikipedia.org/wiki/Eurorack) module developed by [Allen Synthesis](https://www.allensynthesis.co.uk) that uses the [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/) to process and produce modular level signals based on code written in [MicroPython](https://micropython.org/). The entire project is open-source.

## Documentation
### Hardware
The hardware source files and documentation (including build guides) can be found in the [hardware overview](hardware/README.md), and kits can be bought directly from [Allen Synthesis](https://allensynthesis.square.site/product/europi-panel-pcb/16?cp=true&sa=true&sbp=false&q=false).

### Software
Before using any of the software, follow the [programming_instructions](software/programming_instructions.md) to set up and calibrate your module.
A list of user contributed scripts (along with descriptions for their usage) can be found in [contrib/README.md](software/contrib/README.md).

The EuroPi firmware allows you to interact with the hardware easily using code written in MicroPython. You can read the full list of available functions in the [EuroPi API Documentation](https://allen-synthesis.github.io/EuroPi/), which also includes some examples of some of those functions can be used. Some of the less obvious but potentially useful functions are also explained in more depth in [interesting_things.md](software/interesting_things.md).

If you would like to extend any of the features of the EuroPi software, you can view the [firmware source code](software/firmware/europi.py), and make contributions of your own after reading the [contribution guidelines](contributing.md).

## Specification
* 6 0-10V Control Voltage outputs, each with indicator LED
* 2 Knobs with 12 bit resolution
* 2 Push Buttons
* 1 0-12V Control Voltage input with 12 bit resolution
* 1 Digital input for external clocking or gate sources
* 128x32 OLED Display
* I²C expansion header on the rear for extra sensors or outputs

![github banner](https://user-images.githubusercontent.com/79809962/157898134-44cc0534-ac3b-4051-9773-a3be95ba4602.jpg)

## License
This module, and any documentation included in this repository, is entirely "free" software and hardware. The hardware is [certified by the Open Source Hardware Association].(https://certification.oshwa.org/uk000048.html)

* Software: [Apache 2.0](software/LICENSE)
* Hardware: [CERN OHL-S v2](hardware/LICENSE)
* Documentation: [CC0 1.0](LICENSE)

Anyone is welcome to design their own versions of the idea, or modify my designs.
The only thing I would ask is that you refrain from using the brand name 'Allen Synthesis' on your DIY builds if they have modified my files in any way, just to prevent any confusion if they end up being re-sold or distributed. This is in line with section 8.2 of the CERN license. You may use the brand name if you have simply copied the files from this repository to replicate without modification.

If you have a bug fix or improvement that you think is worth sharing, then feel free to send over any pictures or documentation and it can be merged with the main project!

## Issues
If you find any bugs, either in the software, the hardware, or the documentation, please [create a GitHub issue](https://github.com/Allen-Synthesis/EuroPi/issues/new/choose) so it can be fixed by one of the maintainers. There are issue templates available, so please choose whichever is most relevant.

### Disclaimer
Recreate any of the files found in this repository at your own risk; I will attempt to solve any issues that you might have with my designs, but I can't guarantee that there are not minor bugs in any of the documents, both hardware and software. If you want a module or kit that you know will work and will have customer support, you can order one directly from [Allen Synthesis](https://allensynthesis.co.uk/).

### EuroPi Prototype
This repository relates to the EuroPi module, however some users may be expecting to see what is now referred to as the 'EuroPi Prototype'. The repository for this (now deprecated) module [can be found here](https://github.com/roryjamesallen/EuroPi-Prototype)
#### Improvements on the Prototype version
* All outputs are the full Eurorack unipolar range of 0-10V, previously only 0-3.3V
* Two inputs, previously no way to accept input from other modules
* The buttons have hardware debouncing to allow users to change out capacitor values for reduced accidental 'double click'
* A 10 pin Eurorack shrouded power header is now used to prevent accidental reverse powering of the module
* The 5V supply for the Pico is now regulated down from the +12V supply, so no 5V rail is required from your Eurorack power supply
* The power supply is now diode protected to prevent back-powering your rack when the module is connected via USB
* All jacks are protected from overvoltage input (previously the Pico GPIO pin was directly exposed to any input, potentially leading to damage)
