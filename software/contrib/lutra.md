# Lutra

Lutra is a re-imagining of [Expert Sleepers' Otterly](https://expert-sleepers.co.uk/otterley.html) module.

Each output channel is a free running LFO with a subtly different clock speed. The spread of clock speeds is controlled
by `k2` (and optionally `ain` -- see configuration below)

## Configuration

The functionality of `ain` can be configured by creating/editing `/saved_state_Lutra.txt` on the module. This JSON file
contains the saved configuration for the script.  The default values for this file are shown below:

```json
{
    "ain": "spread",
    "wave": "sine"
}
```

- `ain`: sets the mode for `ain`. Must be one of `spread` or `speed`.  If set to `spread` the spread of clock speeds
  of the outputs is controlled by `ain`.  If set to `speed` the master clock speed is controlled by `ain`.
- `wave`: sets the ouptut wave shape. Must be one of: `sine`, `square`, `triangle`, `saw`, or `ramp`.

The wave shape is shown in the upper-left corner of the display:
- ![Sine Wave](./lutra-docs/wave_sine.png) Sine
- ![Square Wave](./lutra-docs/wave_square.png) Square
- ![Triangle Wave](./lutra-docs/wave_triangle.png) Triangle
- ![Saw Wave](./lutra-docs/wave_saw.png) Saw
- ![Ramp Wave](./lutra-docs/wave_ramp.png) Ramp

## Knob Control

Turning `k1` fully anticlockwise will set the clock speed to the slowest setting. Turning `k1` fully clockwise will set
the clock speed to the fastest setting.

Turning `k2` fully anticlockwise will set the spread to zero; every output will have the same clock speed, (though
depending on previous settings and random noise) they may be phase-shifted from each other.

Turning `k2`clockwise will gradually increase the spread of clock speeds. `cv1` will always stay locked to the base
clock speed, with `cv2-6` becoming progressively faster.

## Re-syncing

When `b1` or `din` receive a high voltage all CV outputs are temporarily halted.  Once the input drops low again
all output LFOs will start again from the reset state.  In this way a very short gate(trigger) can be used to reset
the LFOs, or a longer gate can hold them in a reset state for as long as desired.

Note that if a gate signal is connected to `din` then both `din` and `b1` must be low for the LFOs to oscillate.

## CV Control

`ain` is expected to receive signals from zero to `MAX_INPUT_VOLTAGE` (default 12V -- see
[EuroPi configuration](/software/CONFIGURATION.md)).  Increasing the voltage will increase the speed or spread of
the LFOs.  Decreasing the speed/spread is not allowed, as EuroPi cannot accept negative voltages.  Instead it is
recommended to set `k1` and `k2` to set the minimum desired speed & spread with `ain` unpatched. Then send an
attenuated signal into `ain` to increase the speed/spread as desired.
