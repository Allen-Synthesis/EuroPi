# Volts

This script is non-interactive and simply generates 6 fixed voltages:

- `cv1`: 0.5V
- `cv2`: 1.0V
- `cv3`: 2.0V
- `cv4`: 2.5V
- `cv5`: 5.0V
- `cv6`: 10.0V

These can be used to apply fixed offsets for e.g. transposing a sequencer up a number of octaves,
shifting a bipolar LFO so it is positive, sending a contant voltage to a VCA to amplify a signal,
or calibrating other modules.

## Changing the voltages

The offset voltages can be changed by creating/editing `config/OffsetVoltages.json`:
```json
{
    "CV1": 0.5,
    "CV2": 1.0,
    "CV3": 2.0,
    "CV4": 2.5,
    "CV5": 5.0,
    "CV6": 10.0,
}
```
Simply set each cv to the desired voltage, save the file, and reset the module.
