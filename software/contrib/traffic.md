# Traffic

This script is inspired by [Jasmine & Olive Tree's Traffic](https://jasmineandolivetrees.com/products/traffic).
Instead of 3 trigger inputs, this version only has 2.

Traffic has 3 output channels (`cv1`-`cv3`), which output a CV signal when a trigger is received on either
of the two inputs.  The value of the output signal depends on:
1. which input the trigger was received on and
2. the gains for that trigger on each channel.

For example, suppose the gains for channel A are set to `[0.25, 0.6]`. Whenever a trigger on `din` is received,
channel 1 (`cv1`) will output `MAX_VOLTAGE * 0.25 = 2.5V`. Whenever a trigger on `ain` in received, channel A
will output `MAX_VOLTAGE * 0.6 = 6V`.

The same occurs for channels B and C on `cv2` and `cv3`, each with their own pair of gains for the two inputs.

`cv6` outputs a 10ms, 5V gate every time a trigger is received on _either_ input.

`cv4` and `cv5` have no equivalent on the original Traffic module, but are used here as difference channels:
- `cv4` is the absolute difference between `cv1` and `cv2`
- `cv4` is the absolute difference between `cv1` and `cv3`

For a video tutorial on how the original Traffic module works, please see
https://youtu.be/Pn7_NCCKcJc?si=OJ78FRa9PvjD8oSd. The functionality of this script is very much the same, but limited
to two input triggers.


## Setting the gains

Turning `k1` and `k2` will set the gains for channel A. Pressing and holding `b1` while rotating the knobs will set the
gains for channel B. Pressing and holding `b2` while rotating the knobs will set the gains for channel C.

The gains for channels B and C are saved to the module's onboard memory, and will persist across power-cycles.  The
gains for channel A are always read from the current knob positions on startup.


## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Trigger input 1                                                   |
| `ain`         | Trigger input 2                                                   |
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
