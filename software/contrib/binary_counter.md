# Binary Counter

Binary Counter is a simple gate sequencer that uses binary numbers to turn gates on & off.

Starting from zero, every time a gate is received on `din`, the value of the counter is
incremented by `k`, and CV1-6 are set on/off according to the binary representation of the
counter.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Input gate signal                                                 |
| `ain`         | CV input to control `k`                                           |
| `b1`          | Manual gate signal                                                |
| `b2`          | Reset `n` to zero                                                 |
| `k1`          | Control for `k`                                                   |
| `k2`          | Attenuator for `ain`                                              |
| `cv1`         | Least significant bit output                                      |
| `cv2`         | 2s-bit output                                                     |
| `cv3`         | 4s-bit output                                                     |
| `cv4`         | 8s-bit output                                                     |
| `cv5`         | 16s-bit output                                                    |
| `cv6`         | Most significant bit output                                       |

## Configuration

This program has the following configuration options:

- `USE_GRAY_ENCODING`: if `true`, instead of traditional binary encoding, the pattern is encoded
  using [gray encoding](https://en.wikipedia.org/wiki/Gray_encoding). This means that consecutive
  gate patterns will always differ by exactly 1 bit.

| Decimal value | Traditional binary | Gray encoding |
|---------------|--------------------|---------------|
| 0             | `000000`           | `000000`      |
| 1             | `000001`           | `000001`      |
| 2             | `000010`           | `000011`      |
| 3             | `000011`           | `000010`      |
| 4             | `000100`           | `000110`      |
| 5             | `000101`           | `000111`      |
| 6             | `000110`           | `000101`      |
| 7             | `000111`           | `000100`      |
| ...           | ...                | ...           |

To enable Gray encoding, create/edit `/config/BinaryCounter.json` to contain the following:
```json
{
    "USE_GRAY_ENCODING": true
}

```
