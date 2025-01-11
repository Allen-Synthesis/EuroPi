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

## Configuration

Pet Rock can be configured to use different pseudo-random rhythm-generating algorithms. To choose, edit
`config/PetRock.json` to set the `MOODS` key:
```json
{
    "MOODS": "classic"
}
```

- `MOODS` can be one of `classic` (default), `alternate`, or `all`

Depending on the `MOODS` configured, the following algorithms are used, cycling every new moon:

**Classic**
- ![swords](./pet_rock-docs/swords.png) Plain
- ![cups](./pet_rock-docs/cups.png) Reich
- ![wands](./pet_rock-docs/wands.png) Sparse
- ![pentacles](./pet_rock-docs/pentacle.png) Vari

**Alternate**

These algorithms were implemented in the original Pet Rock firmware, but ultimately not used in the final
release.
- ![hearts](./pet_rock-docs/heart.png) Blocks
- ![spades](./pet_rock-docs/spade.png) Culture
- ![diamonds](./pet_rock-docs/diamond.png) Over
- ![shields](./pet_rock-docs/shield.png) Wonk

**All**

When `"all"` moods are selected, the order is the 4 classic algorithms, followed by the 4 alternate algorithms,
in the order listed above.


## Required Hardware

This script requires a Realtime Clock (RTC) to EuroPi's secondary I2C header pins,
located on the underside of the board.

See [Realtime Clock Installation](/software/realtime_clock.md) for instructions on
installing and configuring the realtime clock.
