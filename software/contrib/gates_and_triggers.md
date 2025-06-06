# Gates and Triggers (G&T)

This program is inspired by the [After Later Audio G&T](https://afterlateraudio.com/products/gt-gates-and-triggers)
module.  The program converts a gate or trigger signal on `din` into a gate signal with a variable
length and rising/falling edge triggers.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Incoming gate or trigger signal                                   |
| `ain`         | CV control over output gate length                                |
| `b1`          | Manual input equivalent to `din`                                  |
| `b2`          | Manual toggle input                                               |
| `k1`          | Primary gate duration control                                     |
| `k2`          | Attenuator for CV input on `ain`                                  |
| `cv1`         | Gate output for `din`/`b1`                                        |
| `cv2`         | Trigger output for the rising edge of `din`/`b1`                  |
| `cv3`         | Trigger output for the falling edge of `din`/`b1`                 |
| `cv4`         | Trigger output for the falling edge of `cv1`                      |
| `cv5`         | Toggle output; changes state on every incoming rising edge        |
| `cv6`         | Trigger output for the falling edge of `cv5`                      |

Gate/trigger input on `din` should be at least 0.8V. Ideally the trigger duration should
be at least 10ms, though shorter triggers may be usable.

`ain` expects an input range of 0-10V.  `k2` acts as an attenuator for this input signal.

The gate output on `cv1` has a range of 50ms to 1s, depending on the position of `k1`.  The
knob response is quadratic, giving finer precision at the higher (clockwise) end.

When `ain` receives maximum voltage and `k2` is set to maximum gain, the duration of the gate on
`cv1` is increased by 2 seconds, giving an absolute maximum gate duration of 3 seconds. The
following formula gives the exact calculation of the gate duration:
```
k1 in range [0, 100]
k2 in range [0, 1]
ain in range [0, 1]
MAX_GATE = 1s
MIN_GATE = 50ms

q(x) = (MAX_GATE - MIN_GATE) / 10 * sqrt(x) + MIN_GATE

t = max(
    MIN_GATE,
    q(k1) + k2 * ain * 2s
)
```
Gate time is rounded to the nearest millisecond.

## Fine-tuning Gate Duration

`k1` offers fairly coarse control over the gate length of `cv1`, especially at low values.  If you
need to fine-tune a gate duration in the 50-150ms range you should set `k1` to its minimum value and
use a combination of a constant voltage into `ain` and a relatively low gain set on `k2`.  By
adjusting the value of your input voltage and turning `k2` you should be able to fine-tune the gate
duration much more accurately.

For example to accurately achieve 60ms gates, patch the output from an adjustable voltage source
such as Intellijel's Quadratt (0-5V) or Molten Modular's Motion Meter (0-10V) into `ain`. Turn `k1`
to its minimum setting and leave it there. Slowly increase `k2` and your voltage source while
keeping an eye on EuroPi's display. When the display reads `Gate: 60ms` stop adjusting `k2` and the
input voltage.  While fiddly, this method will provide much finer control for short gate durations.

## Timing Diagram

The following diagram shows the input and output states of the module.  The height of the input to
`din` or `b1` is irrelevant, as long as it is enough to trigger the rising-edge interrupt service
handler on the module (approx. 0.8V minimum).

```
DIN or B1
         __________          __________
________|          |________|          |___________________
        .          .        .          .
B2      .          .        .          .
        .          .        .          .           __   _
__________________________________________________|  |_| |_
        .          .        .          .          .    .
        .          .        .          .          .    .
CV1     .          .        .          .          .    .
        .______    .        .__________________   .    .
________|      |____________|          .       |____________
        .  L1  .   .        .       L2 .       .  .    .
        .      .   .        .          .       .  .    .
CV2     .      .   .        .          .       .  .    .
        ._     .   .        ._         .       .  .    .
________| |_________________| |_____________________________
        .T     .   .        .T         .       .  .    .
        .      .   .        .          .       .  .    .
CV3     .      .   .        .          .       .  .    .
        .      .   ._       .          ._      .  .    .
___________________| |_________________| |_________________
        .      .    T       .           T      .  .    .
CV4     .      .            .                  .  .    .
        .      ._           .                  ._ .    .
_______________| |_____________________________| |_________
        .       T           .                   T .    .
CV5     .                   .                     .    .
        .___________________.                     .____.
________|                   |_____________________|    |___
                            .                          .
CV6                         .                          .
                            ._                         ._
____________________________| |________________________| |_
                             T                          T
```

We assume that between the first and second pulses, the combined CV input via `k1`, `k2`, and `ain`
has changed, resulting in different gate lengths (`L1` and `L2`, above).  The trigger durations
marked with `T` are 10ms.

## Delayed Triggers

If you need a delayed trigger, `cv4` can be used; set the gate duration of `cv1` to the desired
delay duration.  `cv4` will fire a 10ms trigger on the falling edge of `cv1`, which will correspond
with the rising edge of `din` plus the delay.  Note that using `cv4` in this way will limit the
usefulness of `cv1` and `cv3`, as the gate length will be used to control the delay.

There is no way to add a delay between the signal received from `din` or `b1` and the rising edge
of the gate on `cv1`.
