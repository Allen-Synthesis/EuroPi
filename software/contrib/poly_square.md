# Poly Square

An audio-rate oscillator? On the EuroPi? You bet!

This script makes use of a small PIO program to produce six square wave oscillators, each of which
can be set to different frequencies. For a brief primer on the Pi Pico's PIO, visit
https://blues.io/blog/raspberry-pi-pico-pio/. The core PIO program for this script had its origins
in Ben Everard's great little article on HackSpace: https://hackspace.raspberrypi.com/articles/raspberry-pi-picos-pio-for-mere-mortals-part-3-sound.
Is it all just assembly code magic? Yes, sort of, but it really isn't all that scary if you take the
time to learn how the different PIO instructions work. There are only 9 of them!

The Poly Square is six independent oscillators which output on CVs 1-6. The base pitch is set by the
analog input, which is interpreted as a V/oct input with 0V = C. Knob 1 allows for detuning of the 6
voices, and as the knob is turned clockwise, the spread between them increases. Button 2 toggles the
maximum detune between a half step and a major 9th. Knob 2 sets the polyphony mode.

## Controls
- digital_in: unused
- analog_in: V/oct
- knob_1: detune
- knob_2: polyphony mode
- button_1: while depressed, 'tuning mode' is turned on; this changes the knob functionality:
    - knob_1: coarse tune (up to 8 octaves)
    - knob_2: fine tune (up to an octave swing)
- button_2: toggles the maximum detune between a half step and a major 9th
- output_1: oscillator 1
- output_2: oscillator 2
- output_3: oscillator 3
- output_4: oscillator 4
- output_5: oscillator 5
- output_6: oscillator 6

## The polyphony modes

The following is a table of all available polyphony modes, as well as the offset of each CV output
from the root note (shown in half steps):

| Mode         | CV1 | CV2 | CV3 | CV4 | CV5 | CV6 |
|--------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Unison       | 0   | 0   | 0   | 0   | 0   | 0   |
| 5th          | 0   | 0   | 7   | 0   | 0   | 7   |
| Octave       | 0   | 0   | 12  | 0   | 0   | 12  |
| Power chord  | 0   | 7   | 12  | 0   | 7   | 12  |
| Stacked 5ths | 0   | 7   | 14  | 0   | 7   | 14  |
| Minor triad  | 0   | 7   | 15  | 0   | 7   | 15  |
| Major triad  | 0   | 7   | 16  | 0   | 7   | 16  |
| Diminished   | 0   | 6   | 15  | 0   | 6   | 15  |
| Augmented    | 0   | 8   | 16  | 0   | 8   | 16  |
| Major 6th    | 0   | 4   | 9   | 0   | 4   | 9   |
| Major 7th    | 0   | 4   | 11  | 0   | 4   | 11  |
| Minor 7th    | 0   | 3   | 10  | 0   | 3   | 10  |
| Major penta. | 0   | 2   | 4   | 7   | 9   | 12  |
| Minor penta. | 0   | 2   | 3   | 7   | 9   | 12  |
| Whole tone   | 0   | 2   | 4   | 6   | 8   | 10  |

## Tuning mode

When button 1 is depressed, tuning mode is activated, and it remains active until the button is
released. While in tuning mode, the base pitch for a 0V signal may be adjusted. In tuning mode, knob
1 is repurposed to adjust coarse tuning (up to 8 octaves) while knob 2 handles fine tuning (up to an
octave). Tuning settings are saved to storage when button 1 is released.

Credits:
- The Europi hardware and firmware was designed by Allen Synthesis: https://github.com/Allen-Synthesis/EuroPi
- The basis of the PIO code is from an example written by Ben Everard in a HackSpace article:
  https://hackspace.raspberrypi.com/articles/raspberry-pi-picos-pio-for-mere-mortals-part-3-sound
- Thanks to djmjr (github.com/djmjr) for testing that 6 oscillators can be run simultaneously, and
  for the idea to refrain from adjusting tuning settings until the knobs have been moved

## Basic Usage

1. Switch on
2. Connect outputs to mixer, filters, what have you
3. Send V/oct signal to analog input
4. Enjoy square waves

## Details

Polyphony modes are easy to add! Just add them to the PolySquare.modes list.
