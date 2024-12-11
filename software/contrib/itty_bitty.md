# Itty Bitty

A gate & CV sequencer that uses the binary representation of an 8-bit integer to determine the of/off pattern.

The module has 2 channels, A and B.  Channel A is controlled by `K1` and outputs on `CV1-3`.  Channel B is controlled
by `K2` and outputs on `CV4-6`.

Inspired by an [Instagram post by Schreibmaschine](https://www.instagram.com/p/DDaZklkgzbr) describing an idea for a
new module.

## Ins & Outs

- `DIN`: an input clock/gate/trigger signal used to advance the sequences
- `AIN`: not used
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

Let `0 <= n <= 255` be the value the user selects with the knob. Every time we receive a clock signal we rotate
the bits 1 place to the left, giving us `n'`:
```
00000001 -> 00000010 -> 00000100 -> 00001000 -> 00010000 -> 00100000 -> 01000000 -> 10000000 -> 00000001
```

The "current bit` is the least-significant bit.

The trigger output will emit a trgger signal if the current 1s bit is 1, and no trigger if the current bit is 0. The
duration of the trigger is the same as the incoming clock signal (or the duration of the button press).

The gate output will go high if the current bit is 1, and will go low if the current bit is 0.

The CV output set to `MAX_OUTPUT_VOLTAGE * n' / 255`.
