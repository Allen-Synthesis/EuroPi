# Diagnostic

author: Matthew Jaskula

date: 2022-01-19

labels: utility

A diagnostic utility intended to help prove out a new EuroPi build and calibration. Each aspect of the EuroPi's hardware
is exercised.

- Input values, including knobs and buttons, are shown on the screen.
- Outputs are held at specific, predictable, and hopefully useful values.
- each button press rotates the voltages amongst the six outputs, which helps to test the LEDs.
- Inputs can be tested by self-patching the various CV outputs.
- The boundary of the screen is outlined.
- Temperature, as read by the Pico's onboard temperature sensor, is shown on screen; in degrees fahrenheit when a button 
    is pressed and degrees celsius otherwise.

Inputs and Outputs:
- **digital in:** value displayed on screen
- **analog in:** value displayed on screen
- **button 1:** rotate output voltages backwards
- **button 2:** rotate output voltages forwards
- **knob 1:** value 0-99 displayed on screen
- **knob 2:** value 0-99 displayed on screen
- **cv X:** output a constant voltage, one of [0, 0.5, 1, 2.5, 5, 10]