# Gates and Triggers (G&T)

This program is inspired by the [After Later Audio G&T](https://afterlateraudio.com/products/gt-gates-and-triggers)
module.  The program converts a gate or trigger signal on `din` into a gate signal with a variable length and
rising/falling edge triggers.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Incoming gate or trigger signal                                   |
| `ain`         | CV control over output gate length                                |
| `b1`          | Manual input equivalent to `din`                                  |
| `b2`          | Manual toggle input (see below)                                   |
| `k1`          | Primary gate duration control                                     |
| `k2`          | Attenuator for CV input on `ain`                                  |
| `cv1`         | Gate output for `din`/`b1`                                        |
| `cv2`         | Trigger output for the rising edge of `din`/`b1`                  |
| `cv3`         | Trigger output for the falling edge of `din`/`b1`                 |
| `cv4`         | Trigger output for the falling edge of `cv1`                      |
| `cv5`         | Toggle output; changes state on every incoming rising edge        |
| `cv6`         | Trigger output for the falling edge of `cv5`                      |

The gate output on `cv1` has a normal range of 10ms to 2s, depending on the position of `k1`.  CV input to `ain` can
increase this duration.

`ain` expects an input range of 0-10V.  `k2` acts as an attenuator for this input signal.

`cv5` and `cv6` change state every time an incoming gate/trigger starts on `din` or when `b1` or `b2` is pressed.
Pressing `b2` will ONLY change the state of `cv5` and `cv6`, while `b1` will also output gate and trigger signals on
`cv1`-`cv4`.
