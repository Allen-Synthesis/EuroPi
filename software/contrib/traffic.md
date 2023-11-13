# Traffic

This script is inspired by [Jasmine & Olive Tree's Traffic](https://jasmineandolivetrees.com/products/traffic).
Instead of 3 gate inputs, this version only has 2.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Gate input 1                                                      |
| `ain`         | Gate input 2                                                      |
| `b1`          | Hold to adjust gains for channel A                                |
| `b2`          | Hold to adjust gains for channel B                                |
| `k1`          | Input 1 gain for channel A/B/C                                    |
| `k2`          | Input 2 gain for channel A/B/C                                    |
| `cv1`         | Channel A output                                                  |
| `cv2`         | Channel B output                                                  |
| `cv3`         | Channel C output                                                  |
| `cv4`         | Channel A minus channel B (absolute value)                        |
| `cv5`         | Channel A minus channel C (absolute value)                        |
| `cv6`         | 10ms, 5V trigger whenever a rising edge occurs on `ain` or `din`  |
