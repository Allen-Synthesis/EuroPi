# John Conway's Game of LiFO

This script implements [John Conway's Game Of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) as the
procedural kernel for multiple LFOs.

The game is played on a 128x32 field (the size of the OLED). Every pixel is a cell. On every step an empty space will
spawn a new cell if it has exactly 3 neighbours. Cells with 2 or 3 neighbours stay alive. Cells with 1 or 0 neighbours
die of loneliness. Cells with 4 or more neighbours die of overcrowding.

Every time a rising edge on `din` is received, the game advances one step, checking the above.  Initially the field
is filled randomly with a density controlled by `k1`.  Pressing `b1` will reset the field with new random cells.

Pressing `b2` will manually advance the game by one step.

On every step, a number of random new cells will also spawn, based on the CV input provided on `ain`. `k2` acts
as an attenuator for the signal on `ain`.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | External clock in                                                 |
| `ain`         | CV control over new spawn rate                                    |
| `b1`          | Reset field                                                       |
| `b2`          | Manually advance clock                                            |
| `k1`          | Initial field density (on startup or `b1` press)                  |
| `k2`          | Attenuator for `ain`                                              |
| `cv1` - `cv6` | Output signals. See below for details                             |

## Outputs

The six outputs are stepped CV outputs, whose values vary according to the game state.

- `cv1`: outputs 0-10V depending on the percentage of the field occupied by living cells
- `cv2`: outputs 0-10V depending on the percentage of living cells that died during the last step
- `cv3`: outputs 0-10V depending on the percentage of empty spaces that spawned new cells
         (this ignores cells spawned as a result of `ain` -- only cells with 3 living neighbours count)
- `cv4`:
- `cv5`:
- `cv6`: outputs a 5V gate signal that is high when more than 50% of the field is filled with cells, otherwise 0V
