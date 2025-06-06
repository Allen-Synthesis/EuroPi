# Traffic

This script is inspired by [Jasmine & Olive Tree's Traffic](https://jasmineandolivetrees.com/products/traffic).
Instead of 3 trigger inputs, this version only has 2.

Traffic has 3 output channels (`cv1`-`cv3`), which output CVs signals. The value of the output
signal depends on:
1. which input the trigger was received most recently and
2. the gains for that trigger on each channel.

For example, suppose the gains for channel A are set to `[0.25, 0.6]`. Whenever a trigger on `din`
(trigger input 1) is received, channel A (`cv1`) will output `MAX_VOLTAGE * 0.25 = 2.5V`. Whenever a
trigger on `ain` (trigger input 2) in received, channel A will output `MAX_VOLTAGE * 0.6 = 6V`.

The same occurs for channels B and C on `cv2` and `cv3`, each with their own pair of gains for the
two inputs.

Changing the gains will immediately update the output value, if the gain for that input is active.
i.e. if `din` last detected a trigger, changing the gains for `din` on channel A/B/C will affect the
voltage on `cv1/2/3` immediately.

`cv6` outputs a 10ms, 5V gate every time a trigger is received on _either_ input.

`cv4` and `cv5` have no equivalent on the original Traffic module, but are used here as difference
channels:
- `cv4` is the absolute difference between `cv1` and `cv2`
- `cv4` is the absolute difference between `cv1` and `cv3`

For a video tutorial on how the original Traffic module works, please see
https://youtu.be/Pn7_NCCKcJc?si=OJ78FRa9PvjD8oSd. The functionality of this script is very much the
same, but limited to two input triggers.


## Setting the gains

Turning `k1` and `k2` will set the gains for channel A. Pressing and holding `b1` while rotating the
knobs will set the gains for channel B. Pressing and holding `b2` while rotating the knobs will set
the gains for channel C.

The gains for channels B and C are saved to the module's onboard memory, and will persist across
power-cycles.  The gains for channel A are always read from the current knob positions on startup.

Note that this each channel makes used of "locked knobs."  This means that when changing the active
channel by pressing or releasing `b1` or `b2` it may be necessary to sweep the knob to its prior
position before the gain can be changed. This helps prevent accidentally changing the gains by
pressing the buttons.


## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Trigger input 1                                                   |
| `ain`         | Trigger input 2                                                   |
| `b1`          | Hold to adjust gains for channel B                                |
| `b2`          | Hold to adjust gains for channel C                                |
| `k1`          | Input 1 gain for channel A/B/C                                    |
| `k2`          | Input 2 gain for channel A/B/C                                    |
| `cv1`         | Channel A output                                                  |
| `cv2`         | Channel B output                                                  |
| `cv3`         | Channel C output                                                  |
| `cv4`         | Channel A minus channel B (absolute value)                        |
| `cv5`         | Channel A minus channel C (absolute value)                        |
| `cv6`         | 10ms, 5V trigger whenever a rising edge occurs on `ain` or `din`  |
