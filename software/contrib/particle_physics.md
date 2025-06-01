# Particle Physics

This program implements a very basic particle physics model where an object falls under gravity and
bounces. Every bounce reduces the velocity proportional to an elasticity constant.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Releases the particle from initial conditions                     |
| `ain`         | Unused                                                            |
| `b1`          | Releases the particle from initial conditions                     |
| `b2`          | Alt button to be held while turning `k1` or `k2`                  |
| `k1`          | Edit the drop height (alt: edit gravity)                          |
| `k2`          | Edit elasticity coefficient (alt: edit initial velocity)          |
| `cv1` - `cv5` | Output signals. Configuration is explained below                  |
| `cv6`         | Unused                                                            |

## CV Outputs

`cv1` outputs a 5V trigger every time the particle touches the ground.  When at rest this trigger
becomes a gate, indicating that the particle is always touching the ground.

`cv2` outputs a 5V trigger every time the particle reaches its peak altitude for the bounce and
begins falling again. When at rest this becomes a gate, indicating that the particle is always at
peak altitude.

`cv3` outputs a gate when the particle is at rest.  This can be patched into `din` to automatically
reset the particle when it comes to rest.

`cv4` outputs a control signal in the range `[0, 10]V`, proportional to the particles height.

`cv5` outputs a control signal in the range `[0, 10]V`, proportional to the particles absolute
velocity.  (Because EuroPi can only output positive voltages this output will be high when the
particle is moving quickly up or down.)

## Physics, Explained

For clarity, positive values are up and negative values are down.  Units don't matter, but if it
helps assume everything is SI units (meters, m/s, m/s^2).

- let `(y, dy)` be a 1-D particle, representing its height `y` and velocity `dy`
- let `h` be the particle's initial height above the ground
- let `v` be the particle's initial velocity in the vertical direction
- let `g` be the acceleration due to gravity
- let `e` be the elasticity coefficient, such that `0 < e < 1`
- when released, `(y, dy) = (h, v)`

At every tick of the main loop, the particle's position and velocity are updated:
```
dt = the time between this tick and the previous one

dy' = dy - g * dt
y' = y + dy * dt
```

If `y'` is less than or equal to zero we assume the particle has it the ground and further modify
`dy'`:

```
dy' = |dy| * e
```

To avoid floating point rounding causing the particle to bounce forever, we assume it has come to
rest if its peak height for any bounce is `0.002`. When this occurs, `y` and `dy` are both set to
zero and the simulation effectively stops.
