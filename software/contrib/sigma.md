# Sigma -- Gaussian CV Generator

This script is inspired by [Magnetic Freak's](https://magnetic-freak.com/) Gaussian module.
Please see the [user manual](https://magnetic-freak.com/wp-content/uploads/2022/08/Gaussian_Eurorack_UserGuide.pdf)
for details on the original module and a deeper dive into the mathematics used in this script.

## Gaussian Distributions

The Gaussian or Normal distribution is a bell-shaped curve often used in statistics. Unlike rolling a d20 in
Dungeons and Dragons, where there is an equal chance of the roll being 1, 2, 3, ..., 19, or 20, a normal distribution
is more likely to produce numbers in the middle of its range and less likely to produce numbers at the extremes. The
way in which this probability changes is determined by the standard deviation of the curve, written using the
Greek letter Sigma in statistics.

## Inputs & Outputs

Inputs:
- `din`: an external clock signal to trigger sampling. The pulse width of this signal controls the output
  pulse width
- `ain`: CV control over spread
- `b1`: manual trigger input (used instead of or in addition to `din`)
- `b2`: cycles through the binning modes (see below)
- `k1`: spread control
- `k2`: mean control

`cv1`-`6` output 0-10V CV signals whose value is determined by the normal distribution & binning.
- `cv1`
- `cv2`
- `cv3`
- `cv4`
- `cv5`
- `cv6`

## Distrubution Control

`k1` and `k2` control the mean and standard deviation of the normal distribution at the heart of this script.

...

## Spread Control

By default all six output channels update simultaneously. By applying positive voltage to `ain` the outputs can be
desynchronized, updating at random intervals. `cv1` will always trigger in-time with the clock on `din`, but `cv2`-`5`
will trigger at normally-distributed intervals after `cv1`.

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

To use the outputs as gate triggers, use `Bin 2` mode; this will output 10V triggers. If your module requires
lower trigger voltage, use an external attenuator.

In Quantize mode, the output voltage will be quantized to 1V/Octave scales with the following resolution:

| Quantize Mode | Delta (V) |
|---------------|-----------|
| Tone          | 0.16667   |
| Semitone      | 0.08333   |
| Quartertone   | 0.41667   |
| Continuous    | inf`*`    |

Output will be in the range 0-10V

`*` Not actually infinte, but as high-resolution as the DAC chips will allow
