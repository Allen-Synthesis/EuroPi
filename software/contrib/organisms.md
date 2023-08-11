# Organisms

author: roryjamesallen

date: 11/08/23

labels: Random, Generative, LFO

### General
This script births 6 *organisms* on start-up which all live in *the simulation*, interacting with each other to produce 6 varied control voltage outputs.

## The Organisms
- Each organism has a 'boredom' attribute expressed as a percentage between 0 and 100
- Each organism has a 'speed' attribute expressed as a number between 1 and 10
- When moving, each organism has a 'destination' expressed as a set of coordinates

## Each tick of the simulation...
- Each organism's boredom will increase by 1 if they aren't moving, or decrease by 2 if they are
- As an organism gets more bored, it becomes more likely that it will begin walking/pick a new destination if already walking
- If an organism has just begun to walk, it will pick a new destination on the screen
- If an organism is already walking, it will move towards its destination at its own speed
- If an organism reaches its destination (or would exceed it in the next tick) it stops walking
- If two organisms come within a certain distance of each other, they will "fight" - a white rectangle around the OLED indicates that a fight is taking place
- When two organisms fight, there is a 50% chance that either will win
- The winner's speed increases by 1, and the loser's decreases by 1

The resulting 6 CV outputs are essentially LFOs with a slight stepping nature, as the clock runs in discrete ticks.
They are truly generative, as their attributes (speed for example) have a real effect on their future (a faster organism is more likely to fight often and therefore affect its own speed)


    digital in: n/a
    analogue in: n/a
    knob 1: simulation speed
    knob 2: n/a
    button 1: n/a
    button 2: n/a
    cv1: organism 1's position
    cv2: organism 2's position
    cv3: organism 3's position
    cv4: organism 4's position
    cv5: organism 5's position
    cv6: organism 6's position
