# Copyright 2023 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Shared classes for quantization support

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@year   2023
"""

from europi import experimental_config, MAX_OUTPUT_VOLTAGE

## 1.0V/O is the Eurorack/Moog standard, but Buchla uses 1.2V/O
VOLTS_PER_OCTAVE = experimental_config.VOLTS_PER_OCTAVE

## Standard western music scale has 12 semitones per octave
SEMITONES_PER_OCTAVE = 12

## How many volts per semitone
VOLTS_PER_SEMITONE = float(VOLTS_PER_OCTAVE) / float(SEMITONES_PER_OCTAVE)

## Labels for the 12 semitones (using sharps, not flats)
SEMITONE_LABELS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


class Quantizer:
    """Represents a set of semitones we can quantize input voltages to

    By default this represents a chromatic scale, with all notes enabled.  Notes can be changed
    by setting scale[n] = True/False, where n is the index of the semitone to toggle

    Implements __get_item__ and __set_item__ so you can use Quantizer like an array to set notes on/off
    """

    def __init__(self, notes=None, name=""):
        """Constructor; can specify what notes are enabled/disabled

        @param notes  A boolean array of length SEMITONES_PER_OCTAVE indicating what semitones are enabled (True)
                      or disabled (False).  Defaults to a chromatic scale (all notes enabled) if None is passed.
                      The values of notes are copied into a new array to prevent possible issues with multiple
                      Quantizer instances sharing the same set of notes.

        @raises ValueError if len(notes) is not equal to SEMITONES_PER_OCTAVE
        """
        if notes is None:
            self.notes = [True] * SEMITONES_PER_OCTAVE
        else:
            if len(notes) != SEMITONES_PER_OCTAVE:
                raise ValueError(
                    f"Wrong size for notes array: {len(notes)} but expected {SEMITONES_PER_OCTAVE}"
                )

            self.notes = [n for n in notes]

        self.name = name

    def __getitem__(self, n):
        return self.notes[n % len(self.notes)]

    def __setitem__(self, n, value):
        self.notes[n % len(self.notes)] = value

    def __len__(self):
        return len(self.notes)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return "".join(["1" if self.notes[i] else "0" for i in range(len(self.notes))])

    def quantize(self, analog_in, root=0):
        """Take an analog input voltage and round it to the nearest note on our scale

        @param analog_in  The input voltage to quantize, as a float
        @param root       An integer in the range [0, 12) indicating the number of semitones up to transpose
                          the quantized scale

        @return A tuple of the form (voltage, note) where voltage is
                the raw voltage to output, and note is a value from
                0-11 indicating the semitone
        """
        # Make sure we've got at least 1 note in the scale enabled, otherwise we might have infinite loop problems
        # If we have nothing to quantize to, just output zero for both outputs
        if not (True in self.notes):
            return (0, 0)

        # offset the input voltage by the root to transpose down
        analog_in = analog_in - VOLTS_PER_SEMITONE * root

        # first get the closest chromatic voltage to the input
        nearest_chromatic_volt = round(analog_in / VOLTS_PER_SEMITONE) * VOLTS_PER_SEMITONE

        # then convert that to a 0-12 value indicating the nearest semitone
        base_volts = int(nearest_chromatic_volt)
        nearest_semitone = (nearest_chromatic_volt - base_volts) / VOLTS_PER_SEMITONE

        # go through our scale and determine the nearest on-scale note
        nearest_on_scale = 0
        best_delta = 255
        for note in range(len(self.notes)):
            if self.notes[note]:
                delta = abs(nearest_semitone - note)
                if delta < best_delta:
                    nearest_on_scale = note
                    best_delta = delta

        # re-apply the root to transpose back up
        volts = base_volts + nearest_on_scale * VOLTS_PER_SEMITONE + root * VOLTS_PER_SEMITONE

        # If the calculated voltage is above what we can actually output, move down in semitones until we get
        # to something on the scale
        # Author's Note:
        #  The likeliest way for this to trigger is if MAX_OUTPUT_VOLTAGE is set significantly lower than
        #  MAX_INPUT_VOLTAGE (e.g. 10V in, 5V out) and/or @root is set very high and @analog_in is close
        #  to MAX_OUTPUT_VOLTAGE
        highest_volts = volts
        highest_note = nearest_on_scale
        while volts > MAX_OUTPUT_VOLTAGE:
            highest_volts -= VOLTS_PER_SEMITONE
            highest_note = (highest_note - 1) % len(self.notes)
            if self.notes[highest_note]:
                volts = highest_volts
                nearest_on_scale = highest_note

        return (volts, nearest_on_scale)


class CommonScales:
    """A collection of common scales that can be used in other scripts to support quantization

    The Major135[6|7] and Minor135[6|7] scales are inspired by the Doepfer A-156 quantizer
    """

    # fmt: off
    #                         C      C#     D      D#     E      F      F#     G      G#     A      A#     B
    Chromatic    = Quantizer([True,  True,  True,  True,  True,  True,  True,  True,  True,  True,  True,  True],  "Chromatic")
    NatMajor     = Quantizer([True,  False, True,  False, True,  True,  False, True,  False, True,  False, True],  "Nat Major")
    HarMajor     = Quantizer([True,  False, True,  False, True,  True,  False, True,  True,  False, True,  False], "Har Major")
    Major135     = Quantizer([True,  False, False, False, True,  False, False, True,  False, False, False, False], "Maj 135")
    Major1356    = Quantizer([True,  False, False, False, True,  False, False, True,  False, True,  False, False], "Maj 1356")
    Major1357    = Quantizer([True,  False, False, False, True,  False, False, True,  False, False, False, True],  "Maj 1357")

    NatMinor     = Quantizer([True,  False, True,  True,  False, True,  False, True,  True,  False, True,  False], "Nat Minor")
    HarMinor     = Quantizer([True,  False, True,  True,  False, True,  False, True,  True,  False, False, True],  "Har Minor")
    Minor135     = Quantizer([True,  False, False, True,  False, False, False, True,  False, False, False, False], "Min 135")
    Minor1356    = Quantizer([True,  False, False, True,  False, False, False, True,  True,  False, False, False], "Min 1356")
    Minor1357    = Quantizer([True,  False, False, True,  False, False, False, True,  False, False, True,  False], "Min 1357")

    MajorBlues   = Quantizer([True,  False, True,  True,  True,  False, False, True,  False, True,  False, False], "Maj Blues")
    MinorBlues   = Quantizer([True,  False, False, True,  False, True,  True,  True,  False, False, True,  False], "Min Blues")

    WholeTone    = Quantizer([True,  False, True,  False, True,  False, True,  False, True,  False, True,  False], "Whole")
    Pentatonic   = Quantizer([True,  False, True,  False, True,  False, False, True,  False, True,  False, False], "Penta")
    Dominant7    = Quantizer([True,  False, False, False, True,  False, False, True,  False, False, True,  False], "Dom7")
    # fmt: on


class Intervals:
    """A collection of musical intervals as indices for the Quantizer __get_item__ and __set_item__ methods

    For example, if you have a Quantizer and want to enable the Perfect4th you can simply use

    q = Quantizer(...)
    q[Intervals.P4] = True

    This class uses the short notation for intervals.  See https://en.wikipedia.org/wiki/Interval_(music)
    for more information.

    The abridged summary:
        - single case-sensitive letter for the interval type
        - a number from 1-8 indicating the size of the interval
        - P = perfect
        - M = major
        - m = minor
        - d = diminished
        - A = augmented
        - three exceptions:
            - S = semitone (equivalent to m2/A1)
            - T = Tone (equivalent to M2/d3)
            - TT = Tritone (equivalent to d5/A4)
    """

    # fmt: off
    P1 =  0
    d2 =  0
    m2 =  1
    A1 =  1
    S  =  1
    M2 =  2
    d3 =  2
    T  =  2
    m3 =  3
    A2 =  3
    M3 =  4
    d4 =  4
    P4 =  5
    A3 =  5
    d5 =  6
    A4 =  6
    TT =  6
    P5 =  7
    d6 =  7
    m6 =  8
    A5 =  8
    M6 =  9
    d7 =  9
    m7 = 10
    A6 = 10
    M7 = 11
    d8 = 11
    P8 = 12
    A7 = 12
    # fmt: on
