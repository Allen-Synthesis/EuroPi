# Coin Toss

author: awonak

version: 1.0

Two pairs of clocked probability gates.

Knob 1 adjusts the master clock speed of gate change probability. Knob 2 moves
the probability thresholed between A and B with a 50% chance at noon. Digital
Out 1 and 2 run at 1x speed and Digital 3 and 4 run at 4x speed for
interesting rhythmic patterns. Push button 1 to toggle turbo mode which brings
the clock speed into audio rate.

    knob_1: master clock speed, rate of voltage change
    knob_2: probability threshold
    button_1: toggle speed normal/turbo
    button_2: toggle gate/trigger mode
    digital_1: Coin 1 gate on when voltage above threshold
    digital_2: Coin 2 gate on when voltage below threshold
    digital_3: Coin 2 gate on when voltage above threshold
    digital_4: Coin 2 gate on when voltage below threshold
