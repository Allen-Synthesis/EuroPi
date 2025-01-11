# Pet Rock

A EuroPi clone of [Johan Senzel's Pet Rock](https://petrock.site/).

This script generates pseudo-random gate sequences based on the phase of the moon.

## I/O Assignments

- `din`: external clock input for sequence A
- `ain`: external clock input for sequence B
- `b1`: manually advance sequence A
- `b2`: manually advance sequence B
- `k1`: speed control for sequence A
- `k2`: speed control for sequence B
- `cv1`: primary gate output for sequence A
- `cv2`: inverted gate output for sequence A
- `cv3`: end of sequence trigger for sequence A
- `cv4`: primary gate output for sequence B
- `cv5`: inverted gate output for sequence B
- `cv6`: end of sequence trigger for sequence B

Both sequence A and sequence B can be internally clocked by setting the speed using `K1` and `K2`. Turning
these knobs fully anticlockwise will stop the internal clocks.

## Required Hardware

This script requires a Realtime Clock (RTC) to EuroPi's secondary I2C header pins,
located on the underside of the board.

See [Realtime Clock Installation](/software/realtime_clock.md) for instructions on
installing and configuring the realtime clock.
