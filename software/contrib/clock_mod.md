# Clock Modifier

This program performs clock multiplications and divisions based on an incoming gate signal on DIN.

Each output is a multiple or a division of the incoming clock signal on `DIN`.  The duration of the
output gates are not adjustable and are fixed to approximately a 50% duty cycle (some rounding will
occur).

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Incoming clock signal                                             |
| `ain`         | Reset input                                                       |
| `b1`          | Hold to adjust clock mods for CV2 and CV5                         |
| `b2`          | Hold to adjust clock mods for CV3 and CV6                         |
| `k1`          | Clock modifier for CV1/2/3                                        |
| `k2`          | Clock modifier for CV4/5/6                                        |
| `cv1-6`       | Multiplied/divided clock signals                                  |

The outputs will begin firing automatically when clock signals are received on `din`, and will stop
if the input signals are stopped for 5s or longer.  Upon stopping all output channels will reset.
(NOTE: this means the signal coming into `din` cannot be 0.2Hz or slower!)

Applying a signal of at least 0.8V to `ain` will reset all output channels.

## Persistence

The clock modifiers for output channels 1 and 4 are read directly from the positions of `k1` and
`k2` on startup. The modifiers for the other channels (2, 3, 5, and 6) are saved in a configuration
file and will persist across restarts.

## Note on Phase Alignment

Changing the clock modifers while the module is running is possible, but can (and generally will)
result in some phase-shifting of the outputs. e.g. if `cv1` and `cv2` are set to `x1`, changing
`cv1` to `x2` and then back to `x1` will probably result in `cv1` and `cv2` no longer being
synchronized.

This can be mitigated either by not adjusting the clock modifers while the module is running, or by
patching a reset signal into `ain` to force the module to re-synchronize periodically.
Alternatively, embrace the chaos and use the de-syncronization as a performance effect.
