# Kompari

This program is a EuriPi re-imagining of Allen Synthesis' Kompari module.

## Inputs & Outputs

`AIN` is used for the input signal.  `K1` and `K2` define the lower & upper bounds for comparisons based on
the knob position.

Outputs:
- `CV1` +5V if `K1` < `AIN`, otherwise 0
- `CV2` +5V if `AIN` < `K2`, otherwise 0
- `CV3` +5V if `K1` < `AIN` < `K2`, otherwise 0
- `CV4` `max(K1, AIN)`
- `CV5` `min(AIN, K2)`
- `CV6` `max(K1, min(AIN, K2))`
