# John Conway's Game of LiFO

This script implements [John Conway's Game Of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
as the procedural kernel for multiple LFOs.

The game is played on a 128x32 field (the size of the OLED). Every pixel is a cell. On every step an
empty space will spawn a new cell if it has exactly 3 neighbours. Cells with 2 or 3 neighbours stay
alive. Cells with 1 or 0 neighbours die of loneliness. Cells with 4 or more neighbours die of
overcrowding.

This program acts as a free-running LFO; it is not clockable externally.

On every step, a number of random new cells will also spawn, based on the CV input provided on
`ain`. `k2` acts as an attenuator for the signal on `ain`.

## Inputs

| Input         | Usage                                                             |
|---------------|-------------------------------------------------------------------|
| `din`         | Clear the field & start a new random spawn                        |
| `ain`         | Offset control for spawn density                                  |
| `b1`          | Manual equivalent to `din`                                        |
| `b2`          | Manual equivalent to `din`                                        |
| `k1`          | Base spawn density                                                |
| `k2`          | Attenuverter for `ain`                                            |

## Outputs

| Output | Description                                                                                                  |
|--------|--------------------------------------------------------------------------------------------------------------|
| `cv1`  | 0-10V depending on the Shannon entropy of the entire field                                                   |
| `cv2`  | 0-10V depending on the ratio between the number of births and the total population of the current generation |
| `cv3`  | 0-10V depending on the ratio between the number of births and the number of deaths in the current generation |
| `cv4`  | 5V trigger when every generation is computed                                                                 |
| `cv5`  | 5V gate if the number of births in the current generation was greater than the number of deaths              |
| `cv6`  | 5V trigger if the field has reached a point of stasis (see below)                                            |

If global voltage limits [have been changed](../CONFIGURATION.md) then those limits will be used
instead of the 10V or 5V values described above.

## Stasis Detection

Because of the modest computing power available, this program uses some simple statistics to infer
if the game has reached a point of stasis. There is a chance that false-positives and
false-negatives can be detected.

When the game is believed to have reached a state of stasis it will automatically reset, as if a
signal had been detected on `din`.  The field will clear and be filled with random data with a
density governed by `ain`, `k1`, and
`k2`.

The game is assumed to have reached a state of stasis under these conditions:
1. at least 12 generations have passed since the last reset, and one of
2. the number of game spaces that have changed from dead to alive or alive to dead is equal to
   zero, or
3. The sum of population changes in groups of 2, 3, or 4 generations has a standard deviation of
   1.0 or less and the absolute value of the mean of the group is less than 1.0.

To better-explain 3, consider the following 12 generations' of population changes:
```
[16, -17, 18, -14, 8, -23, 0, -3, 13, -12, 6, -5]
```

Grouping these changes into buckets of 2, 3, or 4 generations we produce these summed buckets:

```
Size 2: [-1, 4, -15, -3, 1, 1]
Size 3: [17, -29, 10, -11]
Size 4: [3, -18, 2]
```

We calculate the mean and standard deviation of each set of buckets, giving:
```
Size 2: -2.167, 6.69328
Size 3: -3.25, 18.08833
Size 4: -4.333, 9.672412
```

In this case none of the standard deviations nor means have a magnitude smaller than 1, so the
system is not considered to be in stasis.

Conversely, given these population changes:
```
[-12, 6, 4, 2, -12, 6, 4, 2, -12, 6, 4, 2]

Size 2: [-6, 6, -6, 6, -6, 6] -> 0.0, 6.0
Size 3: [-2, -4, -6, 12]      -> 0.0, 7.071068
Size 4: [0, 0, 0]             -> 0.0, 0.0
```
we would assume we have reached stasis, as the mean and standard deviation of the size-4 buckets are
less than 1.0.

## LFO Rate Variablility

Because of the implementation of Conway's Game of Life, when the field is densely-populated,
e.g. immediately after a reset with a high spawn rate, the outputs will change relatively slow.  As
cells die off and the field becomes more sparse the rate will increase.  This is normal.

## Patch Ideas

You can patch an external LFO into DIN to periodically reset the simulation before it reaches a
state of stasis.

You can create interesting feedback by patching `cv1`-`cv3` into `ain` and using the gate/trigger
signals from `cv4`-`cv6` to control the simulation reset rate & reset density.

If the variation in the LFO rate causes problems you can take the outputs from Conway and connect
them to an externally-clocked Sample & Hold module. This will smooth out the changes in the update
frequency of Conway.
