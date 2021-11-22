# EuroPi Library

Before using any of this library, follow the instructions in [programming_instructions.md](https://github.com/Allen-Synthesis/EuroPi/blob/main/software/programming_instructions.md) to set up your module.  
  
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

## Analogue Input

The analogue input allows you to 'read' CV from anywhere between 0 and 12V.  
  
It is protected for the entire Eurorack range, so don't worry about plugging in a bipolar source, it will simply be clipped to 0-12V.  
  
The functions all take an optional parameter of samples, which will oversample the ADC and then take an average, which will take more time per reading, but will give you a statistically more accurate result. The default is 256, which I've found to be the sweet spot of performance vs accuracy, but if you want to process at the maximum speed you can use as little as 1, and the processor won't bog down until you get way up into the thousands if you wan't incredibly accurate (but quite slow) readings.

| Method        | Usage       | Parameter(s)       |
| ------------- | ----------- | ----------- |
|read_raw|Reads the raw ADC value (averaged from number of samples)|samples (default 256)
|read_duty|Reads the raw ADC value and then applies offset and gain error values to increase accuracy|samples (default 256)
|read_voltage|Reads the ADC value as a voltage|samples (default 256)

## OLED Display

The OLED Display works by collecting all the applied commands and only updates the physical display when oled.show() is called.  
This allows you to perform more complicated graphics without slowing your program, or to perform the calculations for other functions, but only update the display every few steps to prevent lag.

More explanations and tips about the the display can be found in the [oled_tips](https://github.com/Allen-Synthesis/EuroPi/blob/main/software/oled_tips.md) file
