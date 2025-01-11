# Pet Rock

A EuroPi clone of [Johan Senzel's Pet Rock](https://petrock.site/).

This script generates pseudo-random gate sequences based on the phase of the moon.

## I/O Assignments

- `din`: external clock input for sequence A
- `ain`: external clock input for sequence B
- `b1`: manually advance sequence A
- `b2`: manually advance sequence B
- `k1`: not used
- `k2`: not used
- `cv1`: primary gate output for sequence A
- `cv2`: inverted gate output for sequence A
- `cv3`: end of sequence trigger for sequence A
- `cv4`: primary gate output for sequence B
- `cv5`: inverted gate output for sequence B
- `cv6`: end of sequence trigger for sequence B

## Required Hardware

This script requires a Realtime Clock (RTC) to EuroPi's secondary I2C header pins,
located on the underside of the board.

See [Realtime Clock Installation](/software/realtime_clock.md) for instructions on
installing and configuring the realtime clock.
