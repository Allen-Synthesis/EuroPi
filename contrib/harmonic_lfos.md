# Coin Toss

author: rory allen

date: 12/01/22

Six harmonically related sine wave LFOs

The only control is Knob 1, which controls the rate of the LFOs

There is a list named ```HARMONICS```, by editing which you can change the relationships of the LFOs.
You could change them to all be evenly divisible, for example [1,2,4,8,16,32], or to be very 'unrelated', for example [1.24, 5.27, 9.46, 13.45, 17.23, 23.54].
The last example would only come back into sync after 2472424774707 cycles, which is approximately 78400 years.

The default values for harmonics give some nice relationships which do come back into sync after not too long, but you're welcome to change them to your own needs.

There is also a variable named ```MAX_VOLTAGE```, which is likely only going to be 10 or 5 depending on which you prefer in your system, and what modules you are controlling.
