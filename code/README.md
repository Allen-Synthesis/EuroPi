# EuroPi Library

The EuroPi library is a single file named 'europi.py'.  
It should be imported into any custom program by using 'from europi import \*' to give you full access to the functions within, which are outlined below.  
Inputs and outputs are used as objects, which each have methods to allow them to be used.  
These methods are used by using the name of the object, for example 'cv3' followed by a '.' and then the method name, and finally a pair of brackets containing any parameters that the method requires.  
  
For example: cv3.voltage(4.5)  
Will set the CV output 3 to a voltage of 4.5V.  

## Outputs
| Method        | Usage       | Parameter(s)       |
| ------------- | ----------- | ----------- |
|duty_raw|Sets the output based on a fixed duty cycle|duty_cycle
|duty|Sets the output based on a fixed duty cycle, offset and gain adjusted to be accurate|duty_cycle
|voltage|Sets the output to a fixed voltage|voltage
|on|Sets the output to 5V|n/a
|off|Sets the output to 0V|n/a

## Analogue Input

The analogue input allows you to 'read' CV from anywhere between 0 and 12V.  
Other than 'read_raw', the functions below require that the module has been calibrated (a calibration_data.txt file has been generated within the lib folder).  
If you have not calibrated your module but wish to use these functions, you can download a sample 'calibrations.txt' file from this folder and place it within a folder on your Pico named 'lib' manually.  
This work-around will allow access to the functions without error, but it won't give you the accuracy that the actual calibration would achieve and your voltages likely wouldn't be usable for anything critical such as 1V/Oct.

| Method        | Usage       | Parameter(s)       |
| ------------- | ----------- | ----------- |
|read_raw|Reads the raw ADC value (averaged from number of samples)|samples (default 256)
|read_duty|Reads the raw ADC value and then applies offset and gain error values to increase accuracy|samples (default 256)
|read_voltage|Reads the ADC value as a voltage|samples (default 256)

## OLED Display

The OLED Display works by collecting all the applied commands and only updates the physical display when oled.show() is called.  
This allows you to perform more complicated graphics without slowing your program, or to perform the calculations for other functions, but only update the display every few steps to prevent lag.

| Method        | Usage       | Parameter(s)       |
| ------------- | ----------- | ----------- |
|text|Writes text to the display|string, x coordinate, y coordinate
|line|Draws a line between two coordinates in either black (0) or white (1)|x1, y1, x2, y2, colour
|fill|Fills the display either black (0) or white (1)|colour
|show|Updates changes to the physical display|n/a|
|invert|Inverts the display based on an invert value of 0 or 1|invert
|contrast|Sets the display contrast from 0 to 255|contrast
