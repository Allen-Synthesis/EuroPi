# Slopes

Slopes is a CV processor that analyzes an incoming signal and generates outputs based on the shape
of that input.

## Inputs & Outputs

- `ain`: The analogue signal to process. Due to technical limitations this signal should ideally be
  an LFO, smooth random voltage, or envelope. Audio-rate signals can be patched in, but will likely
  not be analyzed correctly due to processing latency.
- `k1`: Noise filter. Increasing `k1` will make the signal processing less sensitive, but will also
  reduce random noise.
- `k2`: CV output attenuator. At maximum, `cv4`-`6` will output `0-10V`. At 50% `cv4`-`6` will
  output `0-5V`. At 0% `cv4`-`6` will produce no output

- `cv1`: A gate signal that is high when `ain` is rising and low when `ain` is falling
- `cv2`: A gate signal that is high when `ain` is falling and low when `ain` is rising
- `cv3`: A gate signal that is high when `ain` is flat (i.e. holding the same voltage across
  samples)
- `cv4`: A CV signal representing the positive slope of `ain`; the faster `ain` is rising, the
  stronger the CV signal
- `cv5`: A CV signal representing the negative slope of `ain`; the faster `ain` is falling, the
  stronger the CV signal
- `cv6`: A CV signal representing the overall maginude of the slope, ignoring the direction
  (i.e. the sum of `cv4` and `cv5`)

Unused:
- `din`
- `b1`
- `b2`

The display is not used by `Slopes` and will remain off at all times.
