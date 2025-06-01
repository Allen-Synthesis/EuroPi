# Bernoulli Gates

This script is based on Mutable Instruments Branches. Because EuroPi only haa a pair of digital/analogue
inputs, the dual Bernoulli gates share the same clock (from the digital input), and only one Bernoulli
gate has CV input.

A Bernoulli gate takes a logic signal (trigger or gate) as an input, and routes it to either of its
two outputs according to a random coin toss.

## Inputs & Outputs

Inputs:
- `din`: trigger/clock
- `ain`: probability control of gate 1 (summed with Knob 1)
- `k1`: probability control of gate 1
- `k2`: probability control of gate 2
- `b1`: mode switch of gate 1
- `b2`: mode switch of gate 2

Outputs:
- `cv1`: output A of gate 1
- `cv2`: output B of gate 1
- `cv3`: copy of input trigger/clock
- `cv4`: output A of gate 2
- `cv5`: output B of gate 2
- `cv6`: logical AND of both output A (`cv1` and `cv4`)

Turning a knob anticlockwise increases the probability that a signal will be routed to the
corresponding gate's A-output, while turning it clockwise increases the probablility of the signal
being routed to the gate's B-output. At 12-o'clock the probability of either is 50/50. Fully
anticlockwise the probability of either is 100/0 and fully clockwise is 0/100.

Gate modes can be switched between
- trigger: `Tr`
- toggle: `Tg`
- gate (latch): `G`
by pressing the buttons. These modes are described in more detail below.

## Tigger mode (Tr)

When the **trigger mode** is enabled, an output A/B changes to +5V for 10ms every time they are
activated by the corresponding Bernoulli gate.

## Toggle mode (Tg)

In **toggle mode**, the module associates the “heads” and “tails” outcomes to a different pair of
decisions: “continue sending the trigger to the same output as before” and “send the trigger to the
opposite output”. As a result, when the probability knob 1 is set to its maximum value, the trigger
will alternate between outputs A and B.

## Gate mode/Latch mode (G)

When the **gate mode** is enabled, an output A/B stays at +5V until the other output gets activated.
