# Clock Modifier

This program performs clock multiplications and divisions based on an incoming gate signal on DIN.

Each output is a multiple or a division of the incoming clock signal on `DIN`.  The duration of the output gates
are not (currently) adjustable.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Incoming clock signal                                             |
| `ain`         | Unused (for now)                                                  |
| `b1`          | Hold to adjust clock mods for CV2 and CV5                         |
| `b2`          | Hold to adjust clock mods for CV3 and CV6                         |
| `k1`          | Clock modifier for CV1/2/3                                        |
| `k2`          | Clock modifier for CV4/5/6                                        |
| `cv1-6`       | Multiplied/divided clock signals                                  |
