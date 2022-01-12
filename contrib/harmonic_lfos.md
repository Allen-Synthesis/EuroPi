# Harmonically Related LFOs

author: rory allen

date: 12/01/22

Six harmonically related sine wave LFOs

    digital in: Reset all LFOs
    analogue in: Added to master rate
    knob 1: Master rate
    knob 2: Random chance of changing an LFO's division
    button 1: Reset all LFOs
    button 2: Change mode between sine/saw/square
    cv1/cv2/cv3/cv4/cv5/cv6: Harmonically related LFOs


#### Editing/understanding the program
There is a list named ```HARMONICS```, by editing which you can change the relationships of the LFOs.
You could change them to all be evenly divisible, for example [1,2,4,8,16,32], or to be very 'unrelated', for example [1.24, 5.27, 9.46, 13.45, 17.23, 23.54].
The last example would only come back into sync after 2472424774707 cycles, which is approximately 78400 years.
The default example uses all prime numbers (except 1 if you want to be technical), and will only sync up around every 4 hours.

The default values for harmonics give some nice relationships which do come back into sync after not too long, but you're welcome to change them to your own needs.

There is also a variable named ```MAX_VOLTAGE```, which is likely only going to be 10 or 5 depending on which you prefer in your system, and what modules you are controlling.
