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

Stasis is considered acheived either when there are no changes in the state of the field, or if less than 5% of
the field's spaces have changed and the number of births equals the number of deaths

## Patch Ideas

The LFO will effectively stall if stasis is achieved.  By patching `cv6` into `din` you can force the simulation to
restart if the stasis conditions are achieved.

Alternatively, patch an external LFO into DIN to periodically reset the simulation.

You can create interesting feedback by patching `cv1`-`cv3` into `ain` and using the gate signals from `cv4`-`cv6`
to control the simulation reset rate & reset density.
