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
    button_1: toggle internal / external clock source
    button_2: toggle gate/trigger mode
    cv1 / cv4: Coin 1 gate on when voltage above threshold
    cv2 / cv5: Coin 2 gate on when voltage below threshold
    cv3: Coin 1 clock
    cv6: Coin 2 clock

I like to use Visual Studio Code as my IDE and `rshell` to copy and run my scripts.

From the root dir of the repo, enter rshell:

    $ rshell
    > cp contrib/coin_toss.py
    > repl pyboard ~ from  main import * ~ c=CoinToss() ~ c.main()
