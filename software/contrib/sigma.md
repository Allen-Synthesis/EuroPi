# Sigma -- Gaussian CV Generator

This script is inspired by [Magnetic Freak's](https://magnetic-freak.com/) Gaussian module.
Please see the [user manual](https://magnetic-freak.com/wp-content/uploads/2022/08/Gaussian_Eurorack_UserGuide.pdf)
for details on the original module and a deeper dive into the mathematics used in this script.

## Gaussian Distributions

The Gaussian or Normal distribution is a bell-shaped curve often used in statistics. Unlike rolling
a d20 in Dungeons and Dragons, where there is an equal chance of the roll being 1, 2, 3, ..., 19,
or 20, a normal distribution is more likely to produce numbers in the middle of its range and less
likely to produce numbers at the extremes. The way in which this probability changes is determined
by the standard deviation of the curve, written using the Greek letter Sigma in statistics.

## Inputs & Outputs

Inputs:
- `din`: an external clock signal to trigger sampling. The pulse width of this signal controls the
  output pulse width
- `ain`: assignable CV control (can be disabled, or assigned to control `mean`,
  `standard deviation`, `jitter` or `bin mode`)
- `b1`: shift button; hold to change `k1` and `k2` modes
- `b2`: cycles through `ain` routing
- `k1`: mean control / shift: jitter control
- `k2`: spread control / shift: binning/quantizer mode select

`k1` or `k2` will act as an attenuator for the assigned control (mean/spread/jitter/binning).

Outputs are divided into 3 pairs: `cv1 & cv 4`, `cv2 & cv 5`, and `cv3 & cv 6`.  `cv1-3` output gate
signals with a duration equivalent to the duty cycle of the incoming clock on `din`.  `cv4-6` output
random control voltages according to the spread & mean controls and the binning mode.

## Distrubution Control

The following description assumes the binning mode is set to `continuous`.

Changing `k1` will move the average output voltage of the outputs.  Keeping the knob near-vertical
will keep the averate output close to 5V.

Increasing `k2` will increase the standard deviation of the outputs.  At the lowest setting the
outputs will be effectively locked to the mean set by `k1`.  As `k2` increases the spread of output
voltages increases.

## Jitter Control

By default all six output channels update simultaneously. By applying positive voltage to `ain` the
outputs can be desynchronized, updating at random intervals. `cv1 & 4` will always trigger in-time
with the clock on `din`, but the other pairs will trigger at normally-distributed intervals after
`cv1`.

## Binning and Quantize modes

The CV outputs on can be configured to either oscillate between fixed voltage levels, output
quantized 1V/Octave pitch levels, or a continuous smooth voltage.

In Bin mode the output voltage will oscillate between values chosen from the levels below:

| # Bins | CV Output Levels                                    | Delta (V) |
|--------|-----------------------------------------------------|-----------|
|    2   | 0V, 10V                                             | 10V       |
|    3   | 0V, 5V, 10V                                         | 5V        |
|    6   | 0V, 2V, 4V, 6V, 8V, 10V                             | 2V        |
|    7   | 0V, 1.7V, 3.4V, 5V, 6.6V, 8.3V, 10V                 | 1.7V      |
|    9   | 0V, 1.25V, 2.5V, 3.75V, 5V, 6.25V, 7.5V, 8.75V, 10V | 1.25V     |

In Quantize mode, the output voltage will be quantized to 1V/Octave scales with the following
resolution:

| Quantize Mode | Delta (V) |
|---------------|-----------|
| Tone          | 0.16667   |
| Semitone      | 0.08333   |
| Quartertone   | 0.41667   |
| Continuous    | inf`*`    |

Output will be in the range 0-10V

`*` Not actually infinte, but as high-resolution as the DAC chips will allow
