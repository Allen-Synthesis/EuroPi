# Radio Scanner

## Concept

I once bought a shortwave radio after seeing one belonging to my friend, and found that the
experience of scanning through to try and find interesting sounds in two planes, and wanted to
apply this concept to Eurorack.

This program allows you to control up to 6 parameters, but all based on the key two CV outputs
controlled by knobs 1 and 2.


| Inspiration (Shortwave radio)         | EuroPi Program                       |
|:-------------------------------------:|:------------------------------------:|
| ![](https://i.imgur.com/ZJUMUeT.png)  | ![](https://i.imgur.com/ubOxajY.png) |

## Usage

Knob 1 controls CV1, Knob 2 controls CV2.

CV3 is the difference between CV1 and CV2.

The bottom row of CV outputs (CV4, CV5, CV6) are the inverse of whichever output is above it.

Pressing button 1 will allow you to rotate the outputs, inspired by the
[4MS Rotating Clock Divider](https://4mscompany.com/rcd.php). The digital input also triggers a
rotation.

Pressing button 2 will change the mapping of the analogue input, with 3 options:
- Off
- Knob 1
- Knob 2

When the analogue input is mapped to either of the two knobs, it will apply the incoming CV as an
offset to the knob value, so you still have manual control.
