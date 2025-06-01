# Bouncing Pixels

Pixels bounce around the display and trigger gates when hitting the edges.
Inspired by the classic bouncing DVD logo!

## Usage

Just boot up the script and you're already going! You can use the knobs to
adjust several parameters. The analogue input can be bound to any of them.
By default, it affects the speed. The analogue input is summed with the knob
value of its affected parameter, meaning that the knob sets a minimum value
for the analogue input to add to. Note that since the EuroPi takes analogue
inputs between 0V and 10V, AC signals must be biased properly or the bottom
half of the input will be clipped.

### Parameters

* *Speed* affects how fast the simulation runs. It translates to how fast the
  pixels move.
* *Width* controls how wide the playing field is.
* *Impulse speed* controls how much speed is added to each pixel when an impulse
  occurs.
* *Ball count* controls how many pixels are in play.

### Impulses

Impulses can be caused globally by pressing B2 or sending a signal to the
digital input (assuming it has not been reconfigured). When an impulse occurs,
velocity in a random direction. The speed added is the product of the impulse
speed parameter and a random number (between 0.5 and 2.0 by default).

### Deactivation

One possible over and under speed behaviour is that pixels are deactivated.
When deactivated, a pixel will not be processed or rendered until reset. Resets
can be manually triggered by pressing B1 or using the digital input (must be
configured). A reset is automatically triggered when all pixels in play are
deactivated.

## Outputs

* CV1: collision with top edge (25ms)
* CV2: collision with left edge (25ms)
* CV3: collision with right edge (25ms)
* CV4: collision with bottom edge (25ms)
* CV5: collision with any edge (10ms)
* CV6: collision with corner (100ms)

Denoted gate hold lengths are defaults. They can be changed in the
[configuration file](#Configuration).

## Controls

* K1: simulation speed
* K2: width
* Either button + K1: ball count
* Either button + K2: impulse speed
* B1 short press: reset
* B2 short press: send impulse
* Digital input: send impulse (customisable)
* Analogue input: speed (customisable)

Second layer knobs are "locking", which is to say you need to physically set the
knob to a position close to the registered value in order for it to latch and
start changing. This is to prevent abrupt changes in values when you press the
buttons. If you lose track of a knob position, try sweeping the full range to
get it to latch.

The short press threshold is set to 500ms by default. You can adjust this
length in the [configuration file](#Configuration).

The digital input can be set to trigger a reset instead of an impulse. Likewise,
the analogue input can be set to control any of the parameters controlled by
knobs. These behaviours can be defined [configuration file](#Configuration).

## Configuration

The script can be thoroughly customised using a configuration file. The
configuration file must be located at `/config/BouncingPixels.json` on the micro
controller.

### Sample configuration file

```json
{
    "LONG_PRESS_LENGTH": 500.0,
    "TIMESCALE_MIN": 0.0,
    "TIMESCALE_MAX": 100.0,
    "KNOB_CHANGE_THRESHOLD": 0.01,
    "DIN_FUNCTION": "impulse",
    "AIN_FUNCTION": "speed",
    "GATE_HOLD_LENGTH_TOP": 25.0,
    "GATE_HOLD_LENGTH_LEFT": 25.0,
    "GATE_HOLD_LENGTH_RIGHT": 25.0,
    "GATE_HOLD_LENGTH_BOTTOM": 25.0,
    "GATE_HOLD_LENGTH_ANY": 10.0,
    "GATE_HOLD_LENGTH_CORNER": 100.0,
    "ARENA_WIDTH_MIN": 30.0,
    "ARENA_WIDTH_MAX": 1920.0,
    "BALL_COUNT_MAX": 100,
    "BALL_COUNT_MIN": 1,
    "CORNER_COLLISION_MARGIN": 15.0,
    "START_SPEED_MIN": 10.0,
    "START_SPEED_MAX": 100.0,
    "ACCEL_MIN": -5.0,
    "ACCEL_MAX": 5.0,
    "BOUNCINESS_MIN": 0.8,
    "BOUNCINESS_MAX": 1.2,
    "BOUNCE_ANGLE_DEVIATION_MAX": 15.0,
    "UNDER_SPEED_BEHAVIOUR": "reset",
    "OVER_SPEED_BEHAVIOUR": "reset",
    "UNDER_SPEED_THRESHOLD": 5.0,
    "OVER_SPEED_THRESHOLD": 1000000,
    "IMPULSE_SPEED_MIN": 0,
    "IMPULSE_SPEED_MAX": 100000,
    "IMPULSE_SPEED_VARIATION_MIN": 0.5,
    "IMPULSE_SPEED_VARIATION_MAX": 2.0,
}
```

### Configuration values

| Key                           | Type                  | Possible values                                        | Default value | Description |
|-------------------------------|-----------------------|--------------------------------------------------------|---------------|-------------|
| `POLL_FREQUENCY`              | Floating point number | >= 5                                                   | 30            | How frequently the application polls for new inputs, expressed as times per second.<br><br>⚠️ **Changing this value is not recommended.** |
| `SAVE_PERIOD`                 | Floating point number | >= 0                                                   | 5000          | How frequently the application state is saved at most, expressed as seconds between saves.<br><br>⚠️ **Changing this value is not recommended.** |
| `RENDER_FREQUENCY`            | Floating point number | >= 1                                                   | 30            | How frequently the display display is updated at most, expressed as times per second.<br><br>⚠️ **Changing this value is not recommended.** |
| `LONG_PRESS_LENGTH`           | Floating point number | >= 0                                                   | 500           | How many milliseconds a button must be pressed for it to be considered a long press. |
| `TIMESCALE_MIN`               | Floating point number | any                                                    | 0             | The speed at which the simulation runs when the speed parameter is set to minimum. |
| `TIMESCALE_MAX`               | Floating point number | any                                                    | 100           | The speed at which the simulation runs when the speed parameter is set to maximum. |
| `KNOB_CHANGE_THRESHOLD`       | Floating point number | 0.0 - 0.1                                              | 0.01          | How much a knob must change for its value to update. A higher value reduces jitter, but decreases sensitivity. |
| `DIN_FUNCTION`                | Choice                | One of `impulse`, `reset`                              | `impulse`     | The function to trigger when the digital input is raised. |
| `AIN_FUNCTION`                | Choice                | One of `speed`, `impulse_speed`, `ball_count`, `width` | `speed`       | The parameter that the analogue input modulates. |
| `GATE_HOLD_LENGTH_TOP`        | Floating point number | 1 - 10,000                                             | 25            | How long the gate for top edge collisions is held open, expressed in milliseconds. |
| `GATE_HOLD_LENGTH_LEFT`       | Floating point number | 1 - 10,000                                             | 25            | How long the gate for left edge collisions is held open, expressed in milliseconds. |
| `GATE_HOLD_LENGTH_RIGHT`      | Floating point number | 1 - 10,000                                             | 25            | How long the gate for right edge collisions is held open, expressed in milliseconds. |
| `GATE_HOLD_LENGTH_BOTTOM`     | Floating point number | 1 - 10,000                                             | 25            | How long the gate for bottom edge collisions is held open, expressed in milliseconds. |
| `GATE_HOLD_LENGTH_ANY`        | Floating point number | 1 - 10,000                                             | 10            | How long the gate for any edge collisions is held open, expressed in milliseconds. |
| `GATE_HOLD_LENGTH_CORNER`     | Floating point number | 1 - 10,000                                             | 100           | How long the gate for corner collisions is held open, expressed in milliseconds. |
| `ARENA_WIDTH_MIN`             | Floating point number | 30 - 1,920                                             | 30            | The smallest width the playing field can have. Fifteen units equal one pixel. |
| `ARENA_WIDTH_MAX`             | Floating point number | 30 - 1,920                                             | 1920          | The largest width the playing field can have. Fifteen units equal one pixel. |
| `BALL_COUNT_MIN`              | Integer number        | 1 - 100                                                | 1             | The number of balls in play when the `ball_count` parameter is set to minimum. |
| `BALL_COUNT_MAX`              | Integer number        | 1 - 100                                                | 100           | The number of balls in play when the `ball_count` parameter is set to maximum. |
| `CORNER_COLLISION_MARGIN`     | Floating point number | 0 - 240                                                | 15            | How large a portion of the side edges are considered corners. Fifteen units equal one pixel on the display. |
| `START_SPEED_MIN`             | Floating point number | >= 0                                                   | 10            | The minimum speed a pixel may get upon reset, expressed as units per second. |
| `START_SPEED_MAX`             | Floating point number | >= 0                                                   | 100           | The maximum speed a pixel may get upon reset, expressed as units per second. |
| `ACCEL_MIN`                   | Floating point number | any                                                    | -5.0          | The minimum acceleration a pixel may get upon reset, expressed as units per second squared. |
| `ACCEL_MAX`                   | Floating point number | any                                                    | 5.0           | The maximum acceleration a pixel may get upon reset, expressed as units per second squared. |
| `BOUNCINESS_MIN`              | Floating point number | >= 0.0001                                              | 0.8           | The minimum bounce speed multiplier a pixel may get upon reset. |
| `BOUNCINESS_MAX`              | Floating point number | >= 0.0001                                              | 1.2           | The maximum bounce speed multiplier a pixel may get upon reset. |
| `BOUNCE_ANGLE_DEVIATION_MAX`  | Floating point number | 0 - 180                                                | 15            | The maximum angle a pixel might deviate from its calculated direction upon bouncing, expressed in degrees. |
| `UNDER_SPEED_BEHAVIOUR`       | Choice                | One of `impulse`, `reset`, `deactivate`, `noop`        | `reset`       | What a pixel should do when its speed goes below the under speed threshold. |
| `OVER_SPEED_BEHAVIOUR`        | Choice                | One of `reset`, `deactivate`                           | `reset`       | What a pixel should do when its speed goes above the over speed threshold. |
| `UNDER_SPEED_THRESHOLD`       | Floating point number | >= 0                                                   | 5.0           | The speed threshold under which a pixel activates its under speed behaviour. |
| `OVER_SPEED_THRESHOLD`        | Floating point number | >= 0                                                   | 1,000,000     | The speed threshold over which a pixel activates its over speed threshold. |
| `IMPULSE_SPEED_MIN`           | Floating point number | >= 0                                                   | 0             | The speed added to pixels by an impulse when the `impulse` parameter is at minimum. |
| `IMPULSE_SPEED_MAX`           | Floating point number | >= 0                                                   | 100,000       | The speed added to pixels by an impulse when the `impulse` parameter is at maximum. |
| `IMPULSE_SPEED_VARIATION_MIN` | Floating point number | >= 0                                                   | 0.5           | The smallest possible random multiplier for impulse speed. |
| `IMPULSE_SPEED_VARIATION_MAX` | Floating point number | >= 0                                                   | 2.0           | The largest possible random multiplier for impulse speed. |

## Known issues & limitations

* Gate lengths are not entirely precise. They're guaranteed to be at least the
  set length, but they may exceed it slightly on account of running on
  tick-based timers.
* Corners aren't actually corners, they're just the top and bottom most
  parts of the side edges. This means that if a pixel is traveling parallel and
  close to the top or bottom edge, it's possible that it bounces away from the
  edge upon hitting the corner collision area and thus triggers a corner gate
  without hitting both a horizontal and a vertical edge. Another consequence is
  that a corner gate will always trigger at the same time as a side gate,
  regardless of whether the pixel collides with a horizontal or vertical edge
  first.
* Collision handling cannot handle a pixel going fast enough to bounce with two
  opposing walls in one tick. If a pixel goes fast enough to do this, it
  triggers the over speed behaviour (i.e. by default, they will reset).
* This script consumes a relatively large amount of memory. Max ball counts over
  100 risk crashing the script. Ball counts over 20 consume enough memory to
  cause connection issues with Thonny. If you need to debug the script, you will
  probably want to lower the max ball count.

## Further development

If you fancy developing this script further, here are a few suggestions for what
you can do:

* Address any of the issues mentioned above.
* Implement gravity! You can add another set of knob banks (let the buttons
  trigger different banks) that control gravity magnitude and direction.
  The tricky part of implementing gravity comes from the fact that a pixel will
  have zero speed at the top of its arc when bouncing in place, and triggers the
  under speed behaviour.
* Allow more in-app configuration instead of relying on the configuration file.
* Implement visual feedback on the locked knob inputs. This would make the use
  of the second layer knobs easier.
