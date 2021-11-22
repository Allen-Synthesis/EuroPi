# EuroPi Library

The EuroPi library is a single file named *europi.py*.  
It should be imported into any custom program by using 'from europi import \*' to give you full access to the functions within, which are outlined below.  
Inputs and outputs are used as objects, which each have methods to allow them to be used.  
These methods are used by using the name of the object, for example 'cv3' followed by a '.' and then the method name, and finally a pair of brackets containing any parameters that the method requires.  
  
For example: cv3.voltage(4.5)  
Will set the CV output 3 to a voltage of 4.5V.  

## Calibration
The module uses the *europi.py* library file as a calibration program if run directly rather than imported. Simple connect the module to Eurorack power (this is required for the op-amps to be powered for output amplification), then connect the module to your computer via USB, and open the *europi.py* file inside the *lib* folder.  
Now, just run the program and follow the instructions on-screen. You will need access to two accurate reference voltages.  
By default these are 1 and 10 volts, but if you have easier access to two other values (not exceeding the range 0-10V), you can change the values of *LOW_VOLTAGE* and *HIGH_VOLTAGE* variables before you run the program. For best results make sure the values are fairly far apart, hence the choice of 1 and 10V by default.  
  
When the program has finished, you will have calibrated inputs and outputs, allowing you to make proper use of methods such as *ain.read_voltage()* and *cv1.voltage(x)*. This calibration only uses output 1 to calibrate the output levels, which means in theory the resistor tolerances for the other outputs could cause a slight error in amplification factor for those. For this reason, it is recommended to use output 1 as the 1V/Oct output of any program you might use, or else re-write the calibration program to calibrate each output independently (or just be happy with very slightly skewed 1V/Oct outputs from other outputs).  
  
The program automatically generates a file named *calibration.txt* which is stored in the *lib* folder, and which contains the values used by the program each time *europi.py* is imported, so make sure you don't delete or modify it.  
  
If you have not calibrated your module but wish to use methods such as *ain.read_voltage()*, you just need to run the program once, and then stop it after about 5 seconds and a *calibration.txt* file will be generated with default values.
This work-around will allow access to the functions without error, but it won't give you the accuracy that the actual calibration would achieve and your voltages likely wouldn't be usable for anything critical such as 1V/Oct.

### Calibration.txt
| Line | Meaning |
| ------------- | ----------- |
|1|ADC voltage multiplier
|2|ADC offset (in volts)
|3|Output voltage multiplier

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
