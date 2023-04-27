# Pam's "EuroPi" Workout

This program is an homage to ALM's Pamela's "NEW" Workout and Pamela's "PRO"
Workout modules, designed for the EuroPi. It is intended to be used as a
main clock generator, euclidean rhythm generator, clocked LFO, clocked
random voltage source, etc... with optional quantization.

The module itself will generate the master clock signal with a configurable
BPM (1-300 BPM supported). Each output has an independently controlled
clock multiplier or divider, chosen from the following:

```
[x16, x12, x8, x6, x4, x3, x2, x1, /2, /3, /4, /6, /8, /12, /16]
```

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | External start/stop input                                         |
| `ain`         | Routable CV input to control other parameters                     |
| `b1`          | Start/Stop input                                                  |
| `b2`          | Press to enter/exit edit mode. Long-press to enter/leave sub-menu |
| `k1`          | Scroll through the settings in the current menu                   |
| `k2`          | Scroll through allowed values for the current setting             |
| `cv1` - `cv6` | Output signals. Configuration is explained below                  |

## Menu Navigation

Rotate `k1` to scroll through the current menu. Pressing and holding `b2` for 0.5s will
enter a sub-menu. Pressing and holding `b2` again will return to the parent menu.

On any given setting, pressing `b2` (without holding) will enter edit mode for that
item. Rotate `k2` to choose the desired value for the item, and press `b2` again
to apply it.

The menu layout is as follows:

```
Clock
 +-- BPM*
 |    +-- DIN Mode
 |    +-- Reset
 |
CV1
 +-- Mod.*
 |    +-- Wave Shape**
 |    +-- Wave Width (PWM/Symmetry)*
 |    +-- Wave Amplitude*
 |    +-- Skip Probability*
 |    +-- Euclidean Steps*
 |    +-- Euclidean Triggers*
 |    +-- Euclidean Rotation*
 |    +-- Quantization Scale*
 |
CV2 to 6
 +-- Same as CV1
 |
AIN
 +-- Gain
 |    +-- Precision
```

`*` These settings can be automatically selected using voltage coming into `ain`.

`**` This setting can be set up to work as a sample & hold for the signal coming into `ain`.

## Main Clock Options

The main clock menu has the following options:

- `BPM` -- the main BPM for the clock. Must be in the range `[1, 300]`.

The submenu for the main clock has the following options:

- `DIN Mode` -- either `Gate` or `Trigger`.  If `Gate` the clock will run when the input is high. Otherwise
  the clock will toggle on/off on the rising edge of the input signal
- `Reset` -- if true, all waves & euclidean patterns will reset when the clock starts.
  Otherwise they will continue from where they stopped

## CV Channel Options

Each of the 6 CV output channels has the following options:

- `Mod` -- the clock modifier: `/16` to `x16`.  `x1` will output one waveform every beat (dictated by the BPM).
  Multipliers (`xN`) will output `N` waveforms every beat.  Divisions (`/N`) will output a waveform every `N`
  beats.

The clock modifer is ignored if the wave is `Start`, `Reset` or `Run`, as these waves change only when the clock
itself starts/stops and are not controlled by the BPM.

The submenu for each CV output has the following options:

- `Wave` -- the wave shape to output. Square/Triangle/Sine/Random/Reset/Start/Run
  - ![Square Wave](./pams-docs/wave_square.png) Square: square/pulse wave with adjustable width
  - ![Triangle Wave](./pams-docs/wave_triangle.png) Triangle: triangle wave with adjustable symmetry (saw to symmetrical triangle to ramp)
  - ![Sine Wave](./pams-docs/wave_sine.png) Sine: bog-standard sine wave
  - ![Random Wave](./pams-docs/wave_random.png) Random: outputs a random voltage at the start of every euclidean pulse, holding that voltage until the next pulse
    (if `EStep` is zero then every clock tick is assumed to be a euclidean pulse)
  - ![Reset Wave](./pams-docs/wave_reset.png) Reset: a trigger that fires when the clock stops (can be used to trigger other modules to reset, e.g. sequencers
    sequential switches, other euclidean generators)
  - ![Start Wave](./pams-docs/wave_start.png) Start: a trigger that fires when the clock starts (can be used to trigger other modules)
  - ![Run Wave](./pams-docs/wave_run.png) Run: a gate that is high when the clock is running and low when the clock is stopped
  - ![AIN](./pams-docs/wave_ain.png) AIN: acts as a sample & hold of `ain`, with a sample taken at the start of every euclidean pulse
    (if `EStep` is zero then every clock tick is assumed to be a euclidean pulse)
- `Width` -- width of the resulting wave. See below for the effects of width adjustment on different wave shapes
- `Ampl.` -- the maximum amplitude of the output as a percentage of the 12V hardware maximum
- `Skip%` -- the probability that a square pulse or euclidean trigger will be skipped
- `EStep` -- the number of steps in the euclidean rhythm. If zero, the euclidean generator is disabled
- `ETrig` -- the number of pulses in the euclidean rhythm
- `ERot` -- rotation of the euclidean rhythm
- `Quant` -- quantization scale

### Effects of Width on Different Wave Shapes

- Square: Duty cycle control. 0% is always off, 100% is always on
- Triangle: Symmetry control. 50% results in a symmetrical wave, 0% results in a saw wave,
  100% results in a ramp
- Sine: ignored
- Random: offset voltage as a percentage of the maximum output
- Reset: ignored
- Start: ignored
- Run: ignored
- AIN: offset voltage as a percentage of the maximum output

### Reset and Run Waves

The Reset wave fires only when the clock is stopped and can be used to help synchronize
external modules (e.g. other sequencers, sequential switches, etc...)

The Run wave fires once when the clock is started. The duration of the trigger is at least
10ms, but may be longer depending on the BPM. This allows you to start other modules at the
same time as Pam's Workout on the EuroPi.

The duration of the `Run` trigger is based on the BPM of the master clock and the static PPQN of 48.
The trigger turns on immediately and stays on for each PPQN pulse until it's stayed on for at least
10ms. The table below shows approximate trigger times for some common BPM settings:

| BPM | Trigger length (ms, approx.) | PPQN pulses |
|-----|------------------------------|-------------|
| 300 | 12.5                         | 3           |
| 240 | 10.4                         | 2           |
| 120 | 10.4                         | 1           |
| 90  | 13.9                         | 1           |
| 60  | 20.8                         | 1           |
| 40  | 31.2                         | 1           |
| 30  | 41.7                         | 1           |

Most modules that use an external start trigger signal respond to the rising edge of the wave, so
the variablility of the trigger width shouldn't cause any harmful effects in most cases.

Note: Some modules, like the original Pamela's "NEW" Workout, use a gate signal to indicate
on/off, turning on when the gate is high and off when it is low. To create an output of this nature,
set an output channel to use a square wave and set the width to 100%. Ensure that skip and euclidean
steps are both zero to make sure the signal stays high. Make sure the amplitude is at least 50%.

### Quantization

All quantizers are tuned to treat the root note of their respective scales as C.  There is no
support for transposition; you will need to either combine outputs through a mixer or tune your
oscillator to a different base frequency to transpose the output.

The following scales are available:

- `None` -- no quantization
- `Chromatic` -- all 12 semitones can be output
- `Nat Maj` -- natural major scale (C D E F G A B)
- `Har Maj` -- harmonic major scale (C D E F G A# B#)
- `Maj 135` -- natural major triad (C E G)
- `Maj 1356` -- natural major triad + 6th (C E G A)
- `Maj 1357` -- natural major triad + 7th (C E G B)
- `Nat Min` -- natural minor scale (C D Eb F G Ab Bb)
- `Har Min` -- harmonoc minor scale (C D Eb F G Ab B)
- `Min 135` -- natural minor triad (C Eb G)
- `Min 1356` -- natural minor triad + 6th (C Eb G Ab)
- `Min 1357` -- natural minor triad + 7th (C Eb G Bb)
- `Maj Blues` -- major blues scale (C D Eb E G A)
- `Min Blues` -- minor blues scale (C Eb F Gb G Bb)
- `Whole` -- whole tone scale (C D E F# G# A#)
- `Penta` -- pentatonic scale (C D E G A)
- `Dom 7` -- dominant 7th chord (C E G Bb)

## External CV Routing

The input signal to `ain` can be configured to control many parameters of the system.
A value of 0V is the equivalent of choosing the first item from the available menu
and 12V is the equivalent of choosing the last item in the menu.

NOTE: the `Wave Shape` parameter of the CV outputs works differently. Instead of dynamically
choosing the output wave shape, the CV output acts as a sample & hold of the signal coming into
`ain. The digital attenuation (see below) is applied BEFORE the sample & hold operation is applied.
The `Amplitude` parameter acts as a secondary virtual attenuator, and the `Width` parameter acts
as an offset voltage.

There is digital attenuation/gain via the `AIN > Gain` setting.  This sets the percentage
of the input signal that is passed to settings listenting to `ain`.

For example, if your modulation source can only output up to 5V you should set the gain to
`12.0 / 5.0 * 100.0 = 240%`.  This will allow the modulation source to fully sweep the
range of options available.

The `AIN > Precision` setting allows control over the number of samples taken when reading
the input.  Higher precision can result in slower processing, which may introduce errors
when running at high clock speeds
