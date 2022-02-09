# Coin Toss

author: awonak

date: 03/01/22

labels: Clock, Random, CV Generation

Two pairs of clocked probability gates.

Knob 1 adjusts the master clock speed of gate change probability. Knob 2 moves
the probability thresholed between A and B with a 50% chance at noon. Output 
row 1 (cv1 and cv2) run at 1x speed and output row 2 (cv4 and cv5) run at
1/4x speed for interesting rhythmic patterns. Push button 1 to toggle between
internal and external clock source. Push button 2 to toggle between gate and
trigger mode. Analogue input is summed with the threshold knob value to allow
external threshold control.

    digital in: External clock (when in external clock mode)
    analogue in: Threshold control (summed with threshold knob)
    knob 1: internal clock speed
    knob 2: probability threshold
    button 1: toggle internal / external clock source
    button 2: toggle gate/trigger mode
    cv1/cv2: Coin 1 gate output pair when voltage above/below threshold
    cv4/cv5: Coin 2 gate output pair at 1/4x speed
    cv3: Coin 1 clock
    cv6: Coin 2 clock

For developing, I like to use Visual Studio Code as my IDE and `rshell` to copy
and run my scripts.

From the root dir of the repo, enter rshell:

    $ rshell
    > cp software/contrib/coin_toss.py /pyboard/main.py
    > repl pyboard ~ import main
