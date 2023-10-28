# Gates and Triggers (G&T)

This program is inspired by the [After Later Audio G&T](https://afterlateraudio.com/products/gt-gates-and-triggers)
module.  The program treats `din` and `ain` both as digital inputs and outputs trigger/gate signals on `cv1` and `cv4`.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Incoming signal for `cv1`, `cv2`, and `cv3`                       |
| `ain`         | Incoming signal for `cv4`, `cv5`, and `cv5`                       |
| `b1`          | Manual input equivalent to `din`                                  |
| `b2`          | Manual input equivalent to `ain`                                  |
| `k1`          | Gate duration control for `cv1`                                   |
| `k2`          | Gate duration control for `cv2`                                   |
| `cv1`         | Gate output for `din`/`b1`                                        |
| `cv2`         | Trigger output for the rising edge of `din`/`b1`                  |
| `cv3`         | Trigger output for the falling edge of `din`/`b1`                 |
| `cv4`         | Gate output for `ain`/`b2`                                        |
| `cv5`         | Trigger output for the rising edge of `ain`/`b2`                  |
| `cv6`         | Trigger output for the falling edge of `ain`/`b2`                 |

The gate duration goes from 10ms to 2s, depending on the position of `k1`/`k2`.  The knob response is non-linear, so
there's more precision at the longer-end of the range.  Trigger outputs are always 10ms long.  All output signals are
5V.
