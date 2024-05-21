# Gates and Triggers (G&T)

This program is inspired by the [After Later Audio G&T](https://afterlateraudio.com/products/gt-gates-and-triggers)
module.  The program converts a gate or trigger signal on `din` into a gate signal with a variable length and
rising/falling edge triggers.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Incoming gate or trigger signal                                   |
| `ain`         | CV control over output gate length                                |
| `b1`          | Manual input equivalent to `din`                                  |
| `b2`          | Manual toggle input                                               |
| `k1`          | Primary gate duration control                                     |
| `k2`          | Attenuverter for CV input on `ain`                                |
| `cv1`         | Gate output for `din`/`b1`                                        |
| `cv2`         | Trigger output for the rising edge of `din`/`b1`                  |
| `cv3`         | Trigger output for the falling edge of `din`/`b1`                 |
| `cv4`         | Trigger output for the falling edge of `cv1`                      |
| `cv5`         | Toggle output; changes state on every incoming rising edge        |
| `cv6`         | Trigger output for the falling edge of `cv5`                      |

Gate/trigger input on `din` should be at least 0.8V. Ideally the trigger duration should
be at least 10ms, though shorter triggers may be usable.

`ain` expects an input range of 0-10V.  `k2` acts as an attenuverter for this input signal.

The gate output on `cv1` has a range of 50ms to 1s, depending on the position of `k1`.  The
knob response is quadratic, giving finer precision at the higher (clockwise) end.

When `ain` receives maximum voltage and `k2` is set to maximum gain, the duration of the gate on
`cv1` is increased by 2 seconds, giving an absolute maximum gate duration of 3 seconds.  When
`k2` is set to negative gain the minimum gate duration remains 50ms.

## Timing Diagram

The following diagram shows the input and output states of the module.  The height of the input to `din` or `b1` is
irrelevant, as long as it is enough to trigger the rising-edge interrupt service handler on the module (approx. 0.8V
minimum).

```
DIN or B1
         __________          __________
________|          |________|          |______________

B2
                                                   __
__________________________________________________|  |
        .          .        .          .          .
        .          .        .          .          .
CV1     .          .        .          .          .
        .______    .        .__________________   .
________|      |____________|          .       |______
        .  L1  .   .        .       L2 .       .  .
        .      .   .        .          .       .  .
CV2     .      .   .        .          .       .  .
        ._     .   .        ._         .       .  .
________| |_________________| |_______________________
        .      .   .        .          .       .  .
        .      .   .        .          .       .  .
CV3     .      .   .        .          .       .  .
        .      .   ._       .          ._      .  .
___________________| |_________________| |___________
        .      .            .                  .  .
CV4     .      .            .                  .  .
        .      ._           .                  ._ .
_______________| |_____________________________| |___
        .                   .                     .
CV5     .                   .                     .
        .___________________.                     .__
________|                   |_____________________|
                            .
CV6                         .
                            ._
____________________________| |_______________________
```

We assume that between the first and second pulses, the combined CV input via `k1`, `k2`, and `ain` has changed,
resulting in different gate lengths (`L1` and `L2`, above)

## Delayed Triggers

If you need a delayed trigger, `cv4` can be used; set the gate duration of `cv1` to the desired delay
duration.  `cv4` will fire a 10ms trigger on the falling edge of `cv1`, which will correspond with the
rising edge of `din` plus the delay.  Note that using `cv4` in this way will limit the usefulness of `cv1`
and `cv3`, as the gate length will be used to control the delay.

There is no way to add a delay between the signal received from `din` or `b1` and the rising edge of the gate on `cv1`.
