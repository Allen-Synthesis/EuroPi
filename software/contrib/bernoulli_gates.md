# Bernoulli Gates

author: Bridgee

date: 03/13/22

labels: Random

### General
This app is based on Mutable Instruments Branches. Because EuroPi only have a pair of digital/analogue inputs, the dual Bernoulli gates share the same clock (from the digital input), and only one Bernoulli gate have CV input.

A Bernoulli gate takes a logic signal (trigger or gate) as an input, and routes it to either of its two outputs according to a random coin toss.

Knob 1 adjusts the probability of the Bernoulli gate 1, and Knob 2 adjusts the probability of the Bernoulli gate 2. 

Button 1 switches the mode of gate 1 between trigger mode, toggle mode, and gate mode (latch mode), and Button 2 switches the mode of gate 2 between trigger mode, toggle mode, and gate mode (latch mode).

### Tigger mode (Tr)

When the **trigger mode** is enabled, an output A/B changes to +5V for 10ms every time they are activated by the corresponding Bernoulli gate.

### Gate mode/Latch mode (G)

When the **gate mode** is enabled, an output A/B stays at +5V until the other output gets activated.

### Toggle mode (Tg)

In **toggle mode**, the module associates the “heads” and “tails” outcomes to a different pair of decisions: “continue sending the trigger to the same output as before” and “send the trigger to the opposite output”. As a result, when the probability knob 1 is set to its maximum value, the trigger will alternate between outputs A and B.





    digital in: trigger/clock
    analogue in: probability control of gate 1 (summed with Knob 1)
    knob 1: probability control of gate 1
    knob 2: probability control of gate 2
    button 1: mode switch of gate 1
    button 2: mode switch of gate 2
    cv1/cv2: output A/B of gate 1
    cv4/cv5: output A/B of gate 2
    cv3: copy of trigger/clock
    cv6: logic AND of the two output A
