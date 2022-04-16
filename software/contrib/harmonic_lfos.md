# Harmonically Related LFOs

author: rory allen

date: 12/01/22

labels: LFO, Random

Six harmonically related sine/saw/square wave LFOs

    digital in: Reset all LFOs
    analogue in: Added to master rate
    knob 1: Master rate
    knob 2: Adjusts the master clock division of the currently selected LFO
    button 1: Change mode between sine/saw/square
    button 2: Select the next LFO
    cv1/cv2/cv3/cv4/cv5/cv6: LFO outputs


#### Editing/understanding the program
There is a list named ```divisions``` which controls the relationship of each LFO to the master clock, in terms of its division.
You could change them to all be evenly divisible, for example ```[1, 2, 4, 8, 16, 32]```, or to be very 'unrelated', for example ```[1.24, 5.27, 9.46, 13.45, 17.23, 23.54]```.
The last example would only come back into sync after 2,472,424,774,707 cycles, which is approximately 78400 years at one second per cycle.
The default example uses all prime numbers (except 1 if you want to be technical), and will only sync up around 15,015 cycles.
You can change any of these values during operation of the program by using knob 2, and button 2 to change which LFO you have selected. The maximum division is controlled by the MAX_HARMONIC variable at the top of the script.

Both the values stored in the divisions list and the mode (LFO wave shape) are saved to a file, so will be retained after shut down. For this reason there isn't much point in changing the values of the LFO divisions in code, as they will be overwritten and saved as soon as you use knob 2 to alter them.

There is also a variable named ```MAX_VOLTAGE```, which is likely only going to be 10 or 5 depending on which you prefer in your system, and what modules you are controlling. This is inherited by the MAX_OUTPUT_VOLTAGE set in europi.py, but you can override it if you use this script for something specific.
