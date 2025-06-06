# Daily Random

Generates pseudo-random gate and CV patterns based on the current date and time.

## I/O Assignments

- `ain`: not used
- `din`: external clock input
- `b1`: not used
- `b2`: not used
- `k1`: not used
- `k2`: not used
- `cv1`: daily gate sequence (updates at midnight local time)
- `cv2`: hourly gate sequence (updates at the top of every hour)
- `cv3`: minute gate sequence (updates at the top of every minute)
- `cv4`: daily CV sequence (updates at midnight local time)
- `cv5`: hourly CV sequence (updates at the top of every hour)
- `cv6`: minute CV sequence (updates at the top of every minute)

## Required Hardware

This script _can_ be used on a normal EuroPi, but will result in highly predictable
patterns. For best results, connect a Realtime Clock (RTC) to EuroPi's secondary I2C
header pins, located on the underside of the board.

See [Realtime Clock Installation](/software/realtime_clock.md) for instructions on
installing and configuring the realtime clock.
