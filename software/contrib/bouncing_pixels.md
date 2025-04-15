# Bouncing Pixels

author: [Jorin](https://github.com/jorins)

date: 2025-04-12

labels: gates, random, simulation, triggers

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
* *Impulse speed* controls how much speed is added to each pixel when an impulse
  occurs.
* *Width* controls how wide the playing field is.
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
* K2: impulse speed
* Either button + K1: ball count
* Either button + K2: width
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
    "long_press_length": 500.0,
    "timescale_min": 0.0,
    "timescale_max": 100.0,
    "knob_change_threshold": 0.01,
    "din_function": "impulse",
    "ain_function": "speed",
    "gate_hold_length_top": 25.0,
    "gate_hold_length_left": 25.0,
    "gate_hold_length_right": 25.0,
    "gate_hold_length_bottom": 25.0,
    "gate_hold_length_any": 10.0,
    "gate_hold_length_corner": 100.0,
    "arena_width_min": 30.0,
    "arena_width_max": 1920.0,
    "ball_count_max": 100,
    "ball_count_min": 1,
    "corner_collision_margin": 15.0,
    "start_speed_min": 10.0,
    "start_speed_max": 100.0,
    "accel_min": -5.0,
    "accel_max": 5.0,
    "bounciness_min": 0.8,
    "bounciness_max": 1.2,
    "bounce_angle_deviation_max": 15.0,
    "under_speed_behaviour": "reset",
    "over_speed_behaviour": "reset",
    "under_speed_threshold": 5.0,
    "over_speed_threshold": 1000000,
    "impulse_speed_min": 0,
    "impulse_speed_max": 100000,
    "impulse_speed_variation_min": 0.5,
    "impulse_speed_variation_max": 2.0,
}
```

### Configuration values

| Key                           | Type                  | Possible values                                        | Default value | Description |
|-------------------------------|-----------------------|--------------------------------------------------------|---------------|-------------|
| `poll_frequency`              | Floating point number | 5 - 120                                                | 20            | How frequently the application polls for new inputs, expressed as times per second.<br><br>⚠️ **Changing this value is not recommended.** |
| `save_period`                 | Floating point number | >= 0                                                   | 5000          | How frequently the application state is saved at most, expressed as seconds between saves.<br><br>⚠️ **Changing this value is not recommended.** |
| `render_frequency`            | Floating point number | >= 1                                                   | 30            | How frequently the display display is updated at most, expressed as times per second.<br><br>⚠️ **Changing this value is not recommended.** |
| `long_press_length`           | Floating point number | >= 0                                                   | 500           | How many milliseconds a button must be pressed for it to be considered a long press. |
| `timescale_min`               | Floating point number | any                                                    | 0             | The speed at which the simulation runs when the speed parameter is set to minimum. |
| `timescale_max`               | Floating point number | any                                                    | 100           | The speed at which the simulation runs when the speed parameter is set to maximum. |
| `knob_change_threshold`       | Floating point number | 0.0 - 0.1                                              | 0.01          | How much a knob must change for its value to update. A higher value reduces jitter, but decreases sensitivity. |
| `din_function`                | Choice                | One of `impulse`, `reset`                              | `impulse`     | The function to trigger when the digital input is raised. |
| `ain_function`                | Choice                | One of `speed`, `impulse_speed`, `ball_count`, `width` | `speed`       | The parameter that the analogue input modulates. |
| `gate_hold_length_top`        | Floating point number | 1 - 10,000                                             | 25            | How long the gate for top edge collisions is held open, expressed in milliseconds. |
| `gate_hold_length_left`       | Floating point number | 1 - 10,000                                             | 25            | How long the gate for left edge collisions is held open, expressed in milliseconds. |
| `gate_hold_length_right`      | Floating point number | 1 - 10,000                                             | 25            | How long the gate for right edge collisions is held open, expressed in milliseconds. |
| `gate_hold_length_bottom`     | Floating point number | 1 - 10,000                                             | 25            | How long the gate for bottom edge collisions is held open, expressed in milliseconds. |
| `gate_hold_length_any`        | Floating point number | 1 - 10,000                                             | 10            | How long the gate for any edge collisions is held open, expressed in milliseconds. |
| `gate_hold_length_corner`     | Floating point number | 1 - 10,000                                             | 100           | How long the gate for corner collisions is held open, expressed in milliseconds. |
| `arena_width_min`             | Floating point number | 30 - 1,920                                             | 30            | The smallest width the playing field can have. Fifteen units equal one pixel. |
| `arena_width_max`             | Floating point number | 30 - 1,920                                             | 1920          | The largest width the playing field can have. Fifteen units equal one pixel. |
| `ball_count_min`              | Integer number        | >= 1                                                   | 1             | The number of balls in play when the `ball_count` parameter is set to minimum. |
| `ball_count_max`              | Integer number        | >= 1                                                   | 100           | The number of balls in play when the `ball_count` parameter is set to maximum. |
| `corner_collision_margin`     | Floating point number | 0 - 240                                                | 15            | How large a portion of the side edges are considered corners. Fifteen units equal one pixel on the display. |
| `start_speed_min`             | Floating point number | >= 0                                                   | 10            | The minimum speed a pixel may get upon reset, expressed as units per second. |
| `start_speed_max`             | Floating point number | >= 0                                                   | 100           | The maximum speed a pixel may get upon reset, expressed as units per second. |
| `accel_min`                   | Floating point number | any                                                    | -5.0          | The minimum acceleration a pixel may get upon reset, expressed as units per second squared. |
| `accel_max`                   | Floating point number | any                                                    | 5.0           | The maximum acceleration a pixel may get upon reset, expressed as units per second squared. |
| `bounciness_min`              | Floating point number | >= 0.0001                                              | 0.8           | The minimum bounce speed multiplier a pixel may get upon reset. |
| `bounciness_max`              | Floating point number | >= 0.0001                                              | 1.2           | The maximum bounce speed multiplier a pixel may get upon reset. |
| `bounce_angle_deviation_max`  | Floating point number | 0 - 180                                                | 15            | The maximum angle a pixel might deviate from its calculated direction upon bouncing, expressed in degrees. |
| `under_speed_behaviour`       | Choice                | One of `impulse`, `reset`, `deactivate`, `noop`        | `reset`       | What a pixel should do when its speed goes below the under speed threshold. |
| `over_speed_behaviour`        | Choice                | One of `reset`, `deactivate`                           | `reset`       | What a pixel should do when its speed goes above the over speed threshold. |
| `under_speed_threshold`       | Floating point number | >= 0                                                   | 5.0           | The speed threshold under which a pixel activates its under speed behaviour. |
| `over_speed_threshold`        | Floating point number | >= 0                                                   | 1,000,000     | The speed threshold over which a pixel activates its over speed threshold. |
| `impulse_speed_min`           | Floating point number | >= 0                                                   | 0             | The speed added to pixels by an impulse when the `impulse` parameter is at minimum. |
| `impulse_speed_max`           | Floating point number | >= 0                                                   | 100,000       | The speed added to pixels by an impulse when the `impulse` parameter is at maximum. |
| `impulse_speed_variation_min` | Floating point number | >= 0                                                   | 0.5           | The smallest possible random multiplier for impulse speed. |
| `impulse_speed_variation_max` | Floating point number | >= 0                                                   | 2.0           | The largest possible random multiplier for impulse speed. |

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