# Logic

This program implements six digital logic operations, with each
operation's result sent to a different output jack.

- `ain`: the first boolean input; any signal above 0.8V is treated
  as ON, anything below that is OFF. (Note: this is the same voltage
  threshold used on the digital input.)
- `din`: the second boolean input
- `cv1`: `ain` AND `din`
- `cv2`: `ain` OR `din`
- `cv3`: `ain` XOR `din`
- `cv4`: `ain` NAND `din`
- `cv5`: `ain` NOR `din`
- `cv6`: `ain` XNOR `din`

The outputs are as follows:

| Output No. | Operation |
|------------|-----------|
| Out 1      | AND       |
| Out 2      | OR        |
| Out 3      | XOR       |
| Out 4      | NAND      |
| Out 5      | NOR       |
| Out 6      | XNOR      |

The following table shows the value for each operation for every
input combination:

| Din | Ain | AND | OR | XOR | NAND | NOR | XNOR |
|-----|-----|-----|----|-----|------|-----|------|
|  0  |  0  |  0  |  0 |  0  |  1   |  1  |  1   |
|  0  |  1  |  0  |  1 |  1  |  1   |  0  |  0   |
|  1  |  0  |  0  |  1 |  1  |  1   |  0  |  0   |
|  1  |  1  |  1  |  1 |  0  |  0   |  0  |  1   |

The screen will go to sleep after 20 minutes of inactivity. Pressing
either button will wake the screen up.

The knobs are not used in this program.