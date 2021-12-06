# EuroPi Library

Before using any of this library, follow the instructions in [programming_instructions.md](/software/programming_instructions.md) to set up your module.  

The EuroPi library is a single file named *europi.py*.  
It should be imported into any custom program by using 'from europi import \*' to give you full access to the functions within, which are outlined below.  
Inputs and outputs are used as objects, which each have methods to allow them to be used.  
These methods are used by using the name of the object, for example 'cv3' followed by a '.' and then the method name, and finally a pair of brackets containing any parameters that the method requires.  
  
For example: 
```
cv3.voltage(4.5)  
```
Will set the CV output 3 to a voltage of 4.5V.  

## Outputs

The outputs are capable of providing 0-10V, which can be achieved using either the *duty()* or *voltage()* methods.  
  
So that there is no chance of not having the full range, the chosen resistor values actually give you a range of about 0-10.5V, which is why calibration is important if you want to be able to output precise voltages.

| Method        | Usage       | Parameter(s)       |
| ------------- | ----------- | ----------- |
|duty|Sets the output based on a fixed duty cycle|duty
|voltage|Sets the output to a fixed voltage|voltage
|on|Sets the output to 5V|n/a
|off|Sets the output to 0V|n/a
|toggle|'Flip' the output between 0V or 5V depending on current state|n/a
|value|Sets the output to 0V or 5V based on a binary input|0 or 1

## Analogue Input

The analogue input allows you to 'read' CV from anywhere between 0 and 12V.  
  
It is protected for the entire Eurorack range, so don't worry about plugging in a bipolar source, it will simply be clipped to 0-12V.  
  
The functions all take an optional parameter of samples, which will oversample the ADC and then take an average, which will take more time per reading, but will give you a statistically more accurate result. The default is 256, which I've found to be the sweet spot of performance vs accuracy, but if you want to process at the maximum speed you can use as little as 1, and the processor won't bog down until you get way up into the thousands if you wan't incredibly accurate (but quite slow) readings.

| Method        | Usage       | Parameter(s)       |
| ------------- | ----------- | ----------- |
|read_duty|Reads the raw ADC value and then applies offset and gain error values to increase accuracy|samples (default 256)
|read_voltage|Reads the ADC value as a voltage|samples (default 256)

## Digital Input and Buttons

It may seem a little strange to see the digital input and buttons grouped together, but if you think about it, all the button is doing is create an internal digital input when you press it. For this reason, the method for handling the event that should happen when either a button is pressed or a digital input detected is the same.  
  
A class is used named 'DigitalInput' in the europi.py library, which handles both the debounce (only used for buttons) and the handler (what happens when a press/input is detected).  
  
| Method        | Usage       | Parameter(s)       |
| ------------- | ----------- | ----------- |
|value|Reads the current value of the input|n/a
|handler|Assign a new function to be used as the handler|function

It should be noted that the value will be 0 when the input is 'high', and 1 when 'low'. This is simply a hardware technicality, but will not affect the use of the handler, only the .value() mathod.  
  
To use the handler method, you simply define whatever you want to happen when a button or the digital input is triggered, and then use x.handler(new_function). Do not include the brackets for the function, and replace the 'x' in the example with the name of your input, either b1, b2, or din.

## OLED Display

The OLED Display works by collecting all the applied commands and only updates the physical display when oled.show() is called.  
This allows you to perform more complicated graphics without slowing your program, or to perform the calculations for other functions, but only update the display every few steps to prevent lag.

More explanations and tips about the the display can be found in the [oled_tips](/software/oled_tips.md) file

## Knobs
The knobs are used almost exclusively by methods which use the current position in different ways.

| Method        | Usage       | Parameter(s)       |
| ------------- | ----------- | ----------- |
|read_position|Returns the position as a value between zero and provided integer|integer
|choice|Returns a value from the provided list depending on the current position|list

Read_position has a default value of 100, meaning if you simply use kx.read_position() you will return a percent style value from 0-100.  
  
There is also the optional parameter of samples (which must come after the normal parameter), the same as the analogue input uses (the knob positions are 'read' via an analogue to digital converter). It has a default value of 256, but you can use higher or lower depending on if you value speed or accuracy more.  
If you really want to avoid 'noise' which would present as a flickering value despite the knob being still, then I'd suggest using higher samples (and probably a smaller number to divide the position by).
  
The ADCs used to read the knob position are only 12 bit, which means that any read_position value above 4096 (2^12) will not actually be any finer resolution, but will instead just go up in steps. For example using 8192 would only return values which go up in steps of 2.
