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
* A 10 pin Eurorack shrouded power header is now used to prevent accidental reverse powering the module
* The 5V supply for the Pico is now regulated down from the +12V supply, so no 5V rail is required from your Eurorack power supply
* The power supply is now diode protected to prevent back-flow of voltage when the module is connected via USB
* All jacks are protected from overvoltage input (previously the Pico GPIO pin was directly exposed to any input, potentially leading to damage)
