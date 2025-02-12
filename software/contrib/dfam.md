# DFAM Controller

This program is intended to be used with the Moog DFAM semi-modular. It allows for sequences less than
8 steps long to be played and features a fast-reset button and reset input

## I/O Mapping

| I/O           | Usage
|---------------|--------------------------|
| `din`         | External clock signal    |
| `ain`         | External reset signal    |
| `b1`          | Manual advance button    |
| `b2`          | Manual reset button      |
| `k1`          | Pattern length selection |
| `k2`          | Step size selection      |
| `cv1`         | Clock output             |
| `cv2`         | End of sequence gate     |
| `cv3`         | Unused                   |
| `cv4`         | Unused                   |
| `cv5`         | Unused                   |
| `cv6`         | Unused                   |

## Patching

Connect your clock source or square LFO to `din` and connect `cv1` to DFAM's `ADV/CLOCK` input.

Optionally, connect a reset source to `ain` to automatically reset EuroPi and DFAM (e.g. a clock-stop signal
from [`Pam's Workout`](/software/contrib/pams.md)).

## Preparing DFAM

Patch EuroPi and DFAM as described above.

Manually advance DFAM so the last sequence LED is
illuminated. Then start DFAM by pressing the Start/Stop button. DFAM will now automatically
advance every time a pulse is sent from `cv1` of EuroPi
