# DCSN-2

DSCN-2 is a loopable, random gate sequencer based on a binary tree. An incoming clock signal is
routed to one of two child nodes, and from there to one of four grandchild nodes.

Inspired by the [Robaux DCSN3](https://robaux.io/products/dcsn3).

## Ins & Outs

| I/O | Function
|-----|-----------------------------------------------------------------------------------|
| DIN | Incoming clock signal                                                             |
| AIN | CV control for randomness                                                         |
| K1  | Length of the pattern                                                             |
| K2  | Randomness; anticlockwise will lock the loop, clockwise will introduce randomness |
| B1  | Manually advance the pattern                                                      |
| B2  | Generates a new random pattern                                                    |
| CV1 | Child output 1                                                                    |
| CV2 | Grandchild output 1-1                                                             |
| CV3 | Grandchild output 1-2                                                             |
| CV4 | Child output 2                                                                    |
| CV5 | Grandchild output 2-1                                                             |
| CV6 | Grandchild output 2-2                                                             |

## Operation

Every time a clock signal is received on `DIN` the one child & one grandchild output is turned on;
all other outputs are turned off.  Depending on the randomness the pattern of gates will be looped,
fully random, or somewhere in between

The pulse width of the outputs is determined by the pulse width of the input clock.
