# Coin Toss

Two pairs of clocked probability gates.

## Inputs & Outputs

Inputs:
- `din`: External clock (when in external clock mode)
- `ain`: Threshold control (summed with threshold knob)
- `k1`: internal clock speed
- `k2`: probability threshold
- `b1`: toggle internal / external clock source
- `b2`: toggle gate/trigger mode

Outputs:
- `cv1` & `cv2`: Coin 1 gate output pair when voltage above/below threshold
- `cv3`: Coin 1 clock
- `cv4` & `cv5`: Coin 2 gate output pair at 1/4x speed
- `cv6`: Coin 2 clock

Knob 1 adjusts the master clock speed of gate change probability. Knob 2 moves
the probability thresholed between A and B with a 50% chance at noon. Output
row 1 (cv1 and cv2) run at 1x speed and output row 2 (cv4 and cv5) run at
1/4x speed for interesting rhythmic patterns. Push button 1 to toggle between
internal and external clock source. Push button 2 to toggle between gate and
trigger mode. Analogue input is summed with the threshold knob value to allow
external threshold control.
