# Walking

author: roryjamesallen

date: 25/08/2023

labels: Clock, Trigger, Gate, Random, Manual Gatre

A character walks along a scrolling landscape as long as an external clock causes the system to 'tick'. Every tick, the character will step forwards (the landscape will scroll), and a number of things can happen:
- There is a random chance, set by `knob 1` that a new plant will spawn on the right hand side of the screen
- If a previously spawned plant reaches the player, a trigger will be sent out of `cv2`
- The height/length that a jump will be can be set using `knob 2` and will be a discrete number of clock pulses
- If `b1` was pressed at the previous tick, the character will begin to jump, sending a trigger from `cv3` and a gate from `cv6`
- If the character was already jumping, the gate output from `cv6` will remain high
- `cv4` matches the position of `knob 1` and `cv5` matches the position of `k2`

    digital in: External clock
    analogue in: n/a
    knob 1: Random chance of a plant spawning on each tick
    knob 2: Jump height/length
    button 1: Begin jumping
    button 2: n/a
    cv1: Copy of external clock
    cv2: Character collides with a plant
    cv3: Jump beginning trigger
    cv4: `knob 1` position
    cv5: `knob 2` positon
    cv6: Jump gate
