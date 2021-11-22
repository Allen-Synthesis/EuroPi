# EuroPi

The EuroPi is a fully user reprogrammable module based on the Raspberry Pi Pico, which allows users to process inputs and controls to produce outputs based on code written in Python. The entire project is open-source.


This repository relates to the EuroPi module, however some users may be expecting to see what is now referred to as the 'EuroPi Prototype'. The repository for this (now deprecated) module [can be found here](https://github.com/roryjamesallen/EuroPi-Prototype)

You can find more about this (including a project diary) and other projects of mine on [my website](https://www.allensynthesis.co.uk)

![Imgur](https://i.imgur.com/wHL7558.png)

## New Features

### Obvious Improvements

* Outputs are now capable of providing 0-10V (previously 0-3.3V)
* 6 outputs, all capable of either digital or CV output (previously 4 digital and 4 analogue)
* All outputs have an indicator LED for easy visualisation of outputs (previously only LEDs on the digital outputs)
* One analogue (CV) input is now available, which can 'read' 0-12V (previously no CV input)
* One digital (clock, trigger, gate) input is now available (previously no digital input)
* A 128x32 OLED display has been added to allow for further menu control and usability when changing patches often

### More Technical Changes

* The buttons have hardware debouncing to allow users to change out capacitor values for reduced accidental 'double click'
* A 10 pin Eurorack shrouded power header is now used to prevent accidental reverse powering of the module
* The 5V supply for the Pico is now regulated down from the +12V supply, so no 5V rail is required from your Eurorack power supply
* The power supply is now diode protected to prevent back-powering your rack when the module is connected via USB
* All jacks are protected from overvoltage input (previously the Pico GPIO pin was directly exposed to any input, potentially leading to damage)

Please see the README.md files in the hardware and software folders for more specific information about each, including hardware specifications and how to use the *europi.py* library.


### Issues
If you find any bugs, either in the software, the hardware, or the documentation, please create an Issue on this repository by copy and pasting the [Issue Template](https://github.com/Allen-Synthesis/EuroPi/blob/main/.github/ISSUE_TEMPLATE/bug-report---hardware-issue.md) into a new Issue.


### License

This module, and any documentation included in this repository, is entirely "free" software and hardware, under the Creative Commons Share-Alike 4.0.  
Anyone is welcome to design their own versions of the idea, or modify my designs.
The only thing I would ask is that you refrain from using the brand name 'Allen Synthesis' on your DIY builds if they have modified my files in any way, just to prevent any confusion if they end up being re-sold or distributed. This is in line with section 3. A) 3. of the CC BY-SA License. You may use the brand name if you have simply copied the files from this repository to replicate without modification.
 
### Disclaimer
 
Recreate any of the files found in this repository at your own risk; I will attempt to solve any issues that you might have with my designs, but I can't guarantee that there are not minor bugs in any of the documents, both hardware and software.
