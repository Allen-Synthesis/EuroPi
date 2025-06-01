# Ocean Surge

This program is a loose clone of the [ADDAC 508 "Swell Physics"](https://www.addacsystem.com/en/products/modules/addac500-series/addac508).
The program uses a [trochoidal wave](https://en.wikipedia.org/wiki/Trochoidal_wave) to simulate
the motion of 3 buoys floating on the ocean surface. The relative elevations of these buoys
generates control voltage signals, while logical comparisons between them output gate signals.

## Controls, Inputs, and Outputs

| Control   | Effect
|-----------|----------------------------------------|
| `b1`      | Change clip mode (clip, reflect, wrap) |
| `b2       | Shift control for knobs                |
| `k1`      | Swell size                             |
| `b2 + k1` | Buoy spread                            |
| `k2`      | Agitation                              |
| `b2 + k2` | Simulation speed                       |
| `din`     | Unused                                 |
| `ain`     | CV control (see below)                 |

| Output | Description                                        |
|--------|----------------------------------------------------|
| `cv1`  | 0-10V representing the height of buoy 1            |
| `cv2`  | 0-10V representing the height of buoy 2            |
| `cv3`  | 0-10V representing the height of buoy 3            |
| `cv4`  | Gate on if buoy 1 is lower than buoy 2             |
| `cv5`  | Gate on if buoy 2 if higher than buoy 3            |
| `cv6`  | 0-10V representing the average height of all buoys |

### CV Routing

`ain` can be used to control any one of:
- Swell Size
- Buoy Spread
- Agitation
- Simulation speed

By default it will control the agitation.

To change the CV routing, create/edit `config/OceanSurge.json`:
```json
{
    "CV_TARGET": "agitation"
}
```
where `CV_TARGET` is one of:
- `agitation`
- `buoy_spread`
- `sim_speed`
- `swell_size`

## Wave Demo

[This demo](https://www.desmos.com/calculator/yv8qomtzdf) provides a nice, interactive visualization
of the wave used in the simulation.

The `d` parameter is not used by Ocean Surge.

The `l` parameter corresponds to the `Swell Size` (`k1`) control

The `r` parameter corresponds to the `Agitation` (`k2`) control
