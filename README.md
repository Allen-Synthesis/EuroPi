# EuroPi V2
Resources for the EuroPi Version 2

This second version of the EuroPi project completely overhauls the hardware, adding improvements that make the module able to complete a plethora of additional functions.

![Imgur](https://i.imgur.com/wHL7558.png)

The hardware for this version has been redesigned from the ground up, however from a user standpoint specific improvements on the previous specification can are as follows:

* Outputs are now capable of providing 0-10V (previously 0-3.3V)
* 6 outputs, all capable of either digital or CV output (previously 4 digital and 4 analogue)
* All outputs have an indicator LED for easy visualisation of outputs (previously only LEDs on the digital outputs)
* One analogue (CV) input is now available, which can 'read' 0-10V (previously no CV input)
* One digital (clock, trigger, gate) input is now available (previously no digital input)
* A 128x32 OLED display has been added to allow for further menu control and usability when changing patches often

And these are some more technical changes which may be useful to know if you're planning to modify the module:

* The buttons have hardware debouncing to allow users to change out capacitor values for reduced accidental 'double click'
* A 10 pin Eurorack shrouded power header is now used to prevent accidental reverse powering of the module
* The 5V supply for the Pico is now regulated down from the +12V supply, so no 5V rail is required from your Eurorack power supply
* The power supply is now diode protected to prevent back-powering your rack when the module is connected via USB
* All jacks are protected from overvoltage input (previously the Pico GPIO pin was directly exposed to any input, potentially leading to damage)


This module, and any documentation included in this repository, is entirely open-source, so anyone is welcome to design their own versions of the idea, or modify my designs.
The only thing I would ask is that you refrain from using the brand name 'Allen Synthesis' on your DIY builds if they have modified my files in any way, just to prevent any confusion if they end up being re-sold or distributed.
 
Recreate any of the files found in this repository at your own risk; I will attempt to solve any issues that you might have with my designs, but I can't guarantee that there are not minor bugs in any of the documents, both hardware and software.
