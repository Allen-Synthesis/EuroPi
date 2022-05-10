# Poly Square

author: Tyler Schreiber (github.com/t-schreibs)  
date: 2022-05-10
labels: oscillator, poly

An oscillator? On the EuroPi? You bet!

This script makes use of a small PIO program to produce three square wave oscillators, each of which can be set to different frequencies. For a brief primer on the Pi Pico's PIO, visit https://blues.io/blog/raspberry-pi-pico-pio/. The core PIO program for this script had its origins in Ben Everard's great little article on HackSpace: https://hackspace.raspberrypi.com/articles/raspberry-pi-picos-pio-for-mere-mortals-part-3-sound. Is it all just assembly code magic? Yes, sort of, but it really isn't all that scary if you take the time to learn how the different PIO instructions work. There are only 9 of them!

The Poly Square is three independent oscillators which output on CVs 1-3. The base pitch is set by the analog input, which is interpreted as a V/oct input with 0V = C. Knob 1 allows for detuning of the 3 voices, and as the knob is turned clockwise, the spread between them increases. Knob 2 sets the polyphony mode. There are several available:

## The polyphony modes
- **Unison**: the oscillators are tuned to the same pitch
- **5th**: two oscillators are tuned to the same pitch and the third is tuned a 5th above
- **Octave**: two oscillators are tuned to the same pitch and the third is tuned an octave above
- **Power chord**: the second oscillator is tuned a 5th above the first, and the third is tuned an octave above the first
- **Stacked 5ths**: the second oscillator is tuned a 5th above the first, and the third is tuned a 9th above the first
- **Minor triad**: the second oscillator is tuned a 5th above the first, and the third is tuned a minor 10th above the first
- **Major triad**: the second oscillator is tuned a 5th above the first, and the third is tuned a major 10th above the first
- **Diminished**: the second oscillator is tuned a diminished 5th above the first, and the third is tuned a minor 10th above the first
- **Augmented**: the second oscillator is tuned an augmented 5th above the first, and the third is tuned a major 10th above the first
- **Major 6th**: the second oscillator is tuned a major 3rd above the first, and the third is tuned a major 6th above the first
- **Major 7th**: the second oscillator is tuned a major 3rd above the first, and the third is tuned a major 7th above the first
- **Minor 7th**: the second oscillator is tuned a minor 3rd above the first, and the third is tuned a minor 7th above the first

## Tuning mode
When button 1 is depressed, tuning mode is activated, and it remains active until the button is released. While in tuning mode, the base pitch for a 0V signal may be adjusted. In tuning mode, knob 1 is repurposed to adjust coarse tuning (up to an octave swing) while knob 2 handles fine tuning (up to a half step). Tuning settings are saved to storage when button 1 is released.

Credits:
- The Europi hardware and firmware was designed by Allen Synthesis: https://github.com/Allen-Synthesis/EuroPi
- The basis of the PIO code is from an example written by Ben Everard in a HackSpace article: https://hackspace.raspberrypi.com/articles/raspberry-pi-picos-pio-for-mere-mortals-part-3-sound

# Controls
- digital_in: unused
- analog_in: V/oct
- knob_1: detune
- knob_2: polyphony mode
- button_1: while depressed, 'tuning mode' is turned on; this changes the knob functionality:
    - knob_1: coarse tune (up to an octave swing)
    - knob_2: fine tune (up to a half step)
- output_1: oscillator 1
- output_2: oscillator 2
- output_3: oscillator 3
- output_4: unused
- output_5: unused
- output_6: unused

## Basic Usage
1. Switch on
2. Connect outputs to mixer, filters, what have you
3. Send V/oct signal to analog input
4. Send resulting square waves to modules

## Details
Polyphony modes are easy to add! Just add them to the PolySquare.modes list.

More oscillators can be added to the script - probably 8 in total (though the EuroPi only has 6 output jacks). I stuck with 3 because more seemed a bit, well, unwieldy. Plus I haven't tested performance with that many oscillators at once. But having 6 detunable voices would certainly produce an interesting sound, and most of the script is written to be fairly agnostic about the amount of oscillators in the PolySquare.oscillators list. If you do add more oscillators (or remove any, for that matter), make sure to update all of the polyphony modes so that they support the appropriate number of voices.