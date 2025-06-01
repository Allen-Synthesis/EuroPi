# Kompari

This program is a EuroPi re-imagining of [Allen Synthesis' Kompari](https://www.allensynthesis.co.uk/modules/kompari.html)
module.

An input signal is converted to a normalized `0-1` level and compared with the two knobs' levels,
outputting gate and CV signals.

## Inputs & Outputs

Inputs:
- `ain`: input signal to compare with knob posiotions
- `din`: not used
- `k1`: lower bound for comparisons with `ain`
- `k2`: upper bound for comparisons with `ain`
- `b1`: not used
- `b2`: not used

Outputs:
- `cv1`: +5V if `K1` < `AIN`, otherwise 0V
- `cv2`: +5V if `AIN` < `K2`, otherwise 0V
- `cv3`: +5V if `K1` < `AIN` < `K2`, otherwise 0V
- `cv4`: `max(K1, AIN) * MAX_OUTPUT_VOLTAGE`
- `cv5`: `min(AIN, K2) * MAX_OUTPUT_VOLTAGE`
- `cv6`: `max(K1, min(AIN, K2)) * MAX_OUTPUT_VOLTAGE`

Output calculations treat `K1`, `K2`, and `AIN` as values in the range `[0.0, 1.0]`.
