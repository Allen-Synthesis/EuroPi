# Logic

This program implements six digital logic operations, with each
operation's result sent to a different output jack.

## I/O Mapping

| I/O   | Notes                          |
|-------|--------------------------------|
| `din` | The first digital input        |
| `ain` | The second digital input       |
| `k1`  | Unused                         |
| `k2`  | Unused                         |
| `b1`  | Alternate first digital input  |
| `b2`  | Alternate second digital input |
| `cv1` | Digital AND output             |
| `cv2` | Digital OR output              |
| `cv3` | Digital XOR output             |
| `cv4` | Digital NAND output            |
| `cv5` | Digital NOR output             |
| `cv6` | Digital XNOR output            |

Holding `b1` or `b2` will have the same effect as applying positive voltage
to `din` or `ain` respectively.

### Note on button interaction

Holding both buttons for a few seconds will send the reboot signal to the module,
forcing the module to return to the main menu.  For this reason it is recommended to
use only one button at a time when using the logic module performatively.

## Digital Logic Reference

| Din | Ain | AND | OR | XOR | NAND | NOR | XNOR |
|-----|-----|-----|----|-----|------|-----|------|
|  0  |  0  |  0  |  0 |  0  |  1   |  1  |  1   |
|  0  |  1  |  0  |  1 |  1  |  1   |  0  |  0   |
|  1  |  0  |  0  |  1 |  1  |  1   |  0  |  0   |
|  1  |  1  |  1  |  1 |  0  |  0   |  0  |  1   |

## Screensaver

The screen will go to sleep after 20 minutes of inactivity. Pressing
either button or moving either knob will wake the screen up.
