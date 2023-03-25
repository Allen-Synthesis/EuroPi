# Euclid

This script generates six different Euclidean rhythms, one
on each output. The length, number of steps, and rotation
of each pattern can be independently adjusted.

## I/O Assignments

- `ain`: not used
- `din`: external clock input
- `b1`: Open the settings menu for the selected CV channel, or apply the current
  option if we're already in the settings menu
- `b2`: Toggle between the CV channel select menu & settings menu for that channel
- `k1`: Scroll between the CV channels in the main menu, or the available settings
  for that channel in the settings menu
- `k2`: Scroll through the options for the current setting in the settings menu
- `cv1` to `cv6`: euclidean rhythm outputs

## Settings

- Steps: the number of steps in the pattern (1-32)
- Pulses: the number of pulses in the pattern (0-steps)
- Rotation: rotate the pattern a set number of steps (0-steps)
- Skip %: The probability that any given pulse will be skipped

## Defaults

The script will initialize the six outputs with the following patterns by default:
- CV1: 8 steps, 5 pulses
- CV2: 16 steps, 7 pulses
- CV3: 16 steps, 11 pulses
- CV4: 32 steps, 9 pulses
- CV5: 32 steps, 15 pulses
- CV6: 32 steps, 19 pulses

The default patterns all have the rotation and skip set to zero.

The defaults can be edited through the settings menu, with any custom settings
re-applied automatically when the script restarts.

## Screensaver

After 20 minutes the screen will automatically go blank.  Pressing either button
will wake the screen up and return to the channel menu.