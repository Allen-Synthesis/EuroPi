# Logic

This program implements six digital logic operations, with each
operation's result sent to a different output jack.

The analogue input is treated as a digital low/high signal.  If
the analogue input's value is > 0.8V it is treated as ON.
Otherwise it is treated as off.  (Note: this is the same voltage
threshold used on the digital input.)

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

| Ain | Din | AND | OR | XOR | NAND | NOR | XNOR |
|-----|-----|-----|----|-----|------|-----|------|
|  0  |  0  |  0  |  0 |  0  |  1   |  1  |  1   |
|  0  |  1  |  0  |  1 |  1  |  1   |  0  |  0   |
|  1  |  0  |  0  |  1 |  1  |  1   |  0  |  0   |
|  1  |  1  |  1  |  1 |  0  |  0   |  0  |  1   |