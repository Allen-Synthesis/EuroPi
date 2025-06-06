# Itty Bitty

A gate & CV sequencer that uses the binary representation of an 8-bit integer to determine the
of/off pattern.

The module has 2 channels, A and B.  Channel A is controlled by `K1` and outputs on `CV1-3`.
Channel B is controlled by `K2` and outputs on `CV4-6`.

Inspired by an [Instagram post by Schreibmaschine](https://www.instagram.com/p/DDaZklkgzbr)
describing an idea for a new module.

## Ins & Outs

- `DIN`: an input clock/gate/trigger signal used to advance the sequences
- `AIN`: optional CV control for sequence A and/or B (see configuration, below)
- `K1`: determines the value of sequence A: 0-255
- `K2`: determines the value of sequence B: 0-255
- `B1`: manually advance sequence A
- `B2`: manually advance sequence B
- `CV1`: trigger output of sequence A
- `CV2`: gate output of sequence A
- `CV3`: CV output of sequence A
- `CV4`: trigger output of sequence B
- `CV5`: gate output of sequence B
- `CV6`: CV output of sequence B

## How the sequence works

The numbers 0-255 can be represented in binary in 8 bits:
- `0`: `00000000`
- `1`: `00000001`
- `2`: `00000010`
- `3`: `00000011`
- ...
- `253`: `11111101`
- `254`: `11111110`
- `255`: `11111111`

Let `0 <= n <= 255` be the value the user selects with the knob. Every time we receive a clock
signal we rotate the bits 1 place to the left, giving us `n'`:
```
...
00000001
00000010
00000100
00001000
00010000
00100000
01000000
10000000
00000001
...
```

The "current bit` is the most-significant bit.

The trigger output will emit a trigger signal if the current 1s bit is 1, and no trigger if the
current bit is 0. The duration of the trigger is the same as the incoming clock signal (or the
duration of the button press).

The gate output will go high if the current bit is 1, and will go low if the current bit is 0.

The CV output set to `MAX_OUTPUT_VOLTAGE * reverse(n') / 255`. The bits are reversed so as to
prevent a situation where the CV is always high when the active bit is also high; this forcibly
de-couples the gate & CV outputs, which can lead to more interesting interactions between them.

### Example sequence

Let's assume sequence 83 is selected. `83 = 01010011`

| Step | Gate (High/Low) | Trigger (Y/N) | CV Out (10V max) |
|------|-----------------|---------------|------------------|
| 1    | Low             | N             | 7.921V           |
| 2    | High            | Y             | 3.961V           |
| 3    | Low             | N             | 6.980V           |
| 4    | High            | Y             | 3.490V           |
| 5    | Low             | N             | 6.745V           |
| 6    | Low             | N             | 3.723V           |
| 7    | High            | Y             | 1.686V           |
| 8    | High            | Y             | 5.843V           |

Time graph
```
Clock In
____      ____      ____      ____      ____      ____      ____      ____
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |
    |____|    |____|    |____|    |____|    |____|    |____|    |____|    |____
         .         .         .         .         .         .         .
Gate Out .         .         .         .         .         .         .
         ._________.         ._________.         .         .____________________
         |         |         |         |         .         |         .
_________|         |_________|         |___________________|         .
         .         .         .         .         .         .         .
Trigger Out        .         .         .         .         .         .
         ._        .         ._        .         .         ._        ._
         | |       .         | |       .         .         | |       | |
_________| |_________________| |___________________________| |_______| |________
         .         .         .         .         .         .         .
CV Out (approx)    .         .         .         .         .         .
10V---   .         .         .         .         .         .         .
         .         .         .         .         .         .         .
_________.         .         .         .         .         .         .
         |         ._________.         ._________.         .         .
         |         |         |         |         |         .         .__________
5V----   |         |         |         |         |         .         |
         |_________|         |_________|         |_________.         |
         .         .         ,         .         .         |         |
         .         .         .         .         .         |_________|
         .         .         .         .         .         .         .
0V----   .         .         .         .         .         .         .

```

## Configuration

This program has the following configuration options:

- `USE_AIN_A`: if `true`, channel A's value is determined by `AIN` and `k1` will act as an
  attenuator for the CV signal connected to `AIN`. Default: `false`
- `USE_AIN_B`: if `true`, channel B's value is determined by `AIN` and `k2` will act as an
  attenuator for the CV signal connected to `AIN`. Default: `false`
- `USE_GRAY_ENCODING`: if `true`, instead of traditional binary encoding, the pattern is encoded
  using [gray encoding](https://en.wikipedia.org/wiki/Gray_encoding). This means that consecutive
  sequences will always differ by exactly 1 bit. Default: `false`

| Decimal value | Traditional binary | Gray encoding |
|---------------|--------------------|---------------|
| 0             | `00000000`         | `000000000`   |
| 1             | `00000001`         | `000000001`   |
| 2             | `00000010`         | `000000011`   |
| 3             | `00000011`         | `000000010`   |
| 4             | `00000100`         | `000000110`   |
| 5             | `00000101`         | `000000111`   |
| 6             | `00000110`         | `000000101`   |
| 7             | `00000111`         | `000000100`   |
| ...           | ...                | ...           |

To enable Gray encoding, create/edit `/config/IttyBitty.json` to contain the following:
```json
{
    "USE_GRAY_ENCODING": true
}

```
