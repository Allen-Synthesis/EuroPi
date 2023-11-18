# John Conway's Game of LiFO

This script implements [John Conway's Game Of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) as the
procedural kernel for multiple LFOs.

The game is played on a 128x32 field (the size of the OLED). Every pixel is a cell. On every step an empty space will
spawn a new cell if it has exactly 3 neighbours. Cells with 2 or 3 neighbours stay alive. Cells with 1 or 0 neighbours
die of loneliness. Cells with 4 or more neighbours die of overcrowding.

This program acts as a free-running LFO; it is not clockable externally.

On every step, a number of random new cells will also spawn, based on the CV input provided on `ain`. `k2` acts
as an attenuator for the signal on `ain`.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Clear the field & start a new random spawn                        |
| `ain`         | Offset control for spawn density                                  |
| `b1`          | Manual equivalent to `din`                                        |
| `b2`          | Manual equivalent to `din`                                        |
| `k1`          | Base spawn density                                                |
| `k2`          | Attenuverter for `ain`                                            |
| `cv1` - `cv6` | Output signals. See below for details                             |

## Outputs

The six outputs are stepped CV outputs, whose values vary according to the game state.

- `cv1`: outputs 0-10V depending on the percentage of the field occupied by living cells
- `cv2`: outputs 0-10V depending on the ratio between the number of new births and the current population
- `cv3`: outputs 0-10V depending on the ratio between the number of deaths in the most recent generation and the
        current population
- `cv4`: outputs a 5V gate signal if the number of births in the last generation was greater than the number
         of deaths
- `cv5`: outputs a 5V gate signal if the number of deaths in the last generation was greater than the number
         of births
- `cv6`: outputs a 5V gate signal if the field has reached a point of stasis

## Stasis Detection

Because of the modest computing power available, this program uses some simple statistics to infer if the game has
reached a point of stasis. There is a chance that a false-positive will be detected.

The game is assumed to have reached a state of stasis under these conditions:
1. At least 12 generations have passed since the last reset
2. The number of game spaces that have changed from dead to alive or alive to dead is equal to zero OR
3. The sum of population changes in groups of 2, 3, or 4 generations has a standard deviation of 1.0 or less

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

We calculate the standard deviation of each set of buckets, giving:
```
Size 2: 6.69328
Size 3: 18.08833
Size 4: 9.672412
```

In this case, none of the deviations are less than or equal to 1.0, so the system is not in stasis.

Conversely, given these populations:
```
[0, -9, -3, 5, -8, -9, 2, -8, -5, -6, -11, 4]

Size 2: [-9, 2, -17, -6, -11, -7] -> 5.715476
Size 3: [-12, -12, -11, -13]      -> 0.7071068
Size 4: [-7, -23, -18]            -> 6.683312
```
we would assume we have reached stasis, as the standard deviation of the size-3 buckets is less than 1.0.

## LFO Rate Variablility

Because of the implementation of Conway's Game of Life, when the field is densely-populated, e.g. immediately after a
reset with a high spawn rate, the outputs will change relatively slow.  As cells die off and the field becomes more
sparse the rate will increase.  This is normal.

## Patch Ideas

The LFO will effectively stall if stasis is achieved.  By patching `cv6` into `din` you can force the simulation to
restart if the stasis conditions are achieved.

Alternatively, patch an external LFO into DIN to periodically reset the simulation.

You can create interesting feedback by patching `cv1`-`cv3` into `ain` and using the gate signals from `cv4`-`cv6`
to control the simulation reset rate & reset density.

If the variation in the LFO rate causes problems you can take the outputs from Conway and connect them to an
externally-clocked Sample & Hold module. This will smooth out the changes in the update frequency of Conway.
