# Euclidean Rhythm

author: Bridgee

date: 03/19/22

labels: CV Generation

### General
This app is a six-Euclidean-rhythm gate generator.

> The **Euclidean rhythm** in music was discovered by [Godfried Toussaint](https://en.wikipedia.org/wiki/Godfried_Toussaint) in 2004 and is described in a 2005 paper "The [Euclidean Algorithm](https://en.wikipedia.org/wiki/Euclidean_algorithm) Generates Traditional Musical Rhythms".[[1\]](https://en.wikipedia.org/wiki/Euclidean_rhythm#cite_note-gtpdf-1) The [greatest common divisor](https://en.wikipedia.org/wiki/Greatest_common_divisor) of two numbers is used [rhythmically](https://en.wikipedia.org/wiki/Rhythm) giving the number of [beats](https://en.wikipedia.org/wiki/Beat_(music)) and silences, generating almost all of the most important [world music](https://en.wikipedia.org/wiki/World_music) rhythms,[[2\]](https://en.wikipedia.org/wiki/Euclidean_rhythm#cite_note-gtweb-2) except [Indian](https://en.wikipedia.org/wiki/Music_of_India).[[3\]](https://en.wikipedia.org/wiki/Euclidean_rhythm#cite_note-extv-3) The beats in the resulting rhythms are as equidistant as possible; the same results can be obtained from the [Bresenham](https://en.wikipedia.org/wiki/Bresenham's_line_algorithm) algorithm.
>
> [Euclidean rhythm - Wikipedia](https://en.wikipedia.org/wiki/Euclidean_rhythm)

In general, for each Euclidean gate generator, you have three parameters to play with, which are **length**, **fill**, and **offset**.

**Length** is how long your pattern is. 

**Fill** is the density of your triggers.

**Offset** moves your pattern around.

For example E(length, fill, offset) = E(4, 9, 0) = E(4, 9) = [1, 0, 1, 0, 1, 0, 1, 0, 0], the 1st, 3rd, 5th, and 7th notes will be triggered. Then, E(4, 9, 1) = [0, 1, 0, 1, 0, 1, 0, 1, 0], where the  2st, 4rd, 6th, and 8th notes will be triggered.

The algorithm for generating the Euclidean pattern is called Björklund's Algorithm, and can be found here:

[brianhouse/bjorklund: Euclidean rhythms: Björklund's algorithm in Python](https://github.com/brianhouse/bjorklund)

## Control

**Knob 1** selects the current editable parameters (length, fill, offset, cv target). A **4-dot indicator** show which parameter is enabled.

To edit the parameter, use the two buttons.

The **cv target** can be either length, fill, or target, marked as L, F, O. The final value be added by the CV value from the analogue input.

**Button 1** is adding, and **Button 2** is subtracting 

**Knob 2** selects the current editable gate and clock mode (gate 1, gate 2, gate 3, gate 4, gate 5, gate 6, gate 7, and clock editing mode). There will be a **blinking rectangular box**, if a gate is selected.

In **clock editing mode** (Knob 2 all the way to the right), use the two button to select internal/external clock.

If the internal clock is enabled, use Knob 1 to edit the clock from 20~280 bpm.

If the external clock is enabled, the tempo is decided by the digital input.

The **rectangular box** is blinking with the tempo.



    digital in: clock
    analogue in: change the enealbed cv target
    knob 1: parameter selection
    knob 2: gate selection/ clock edting mode
    button 1: subtracting current parameter/internal clock
    button 2: adding current parameter/external clock
    cv1-cv6: 6 independent euclidean gates
