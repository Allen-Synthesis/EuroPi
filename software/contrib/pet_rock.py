# Copyright 2024 Allen Synthesis
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
A clone of Pet Rock by Jonah Senzel.

Tracks the phase of the moon using a realtime clock and generates
pseudo-random gate sequences based on the date & moon phase

The original code is written in C++ and released under the
CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en)

Original source code is located here: https://github.com/jsenzel1/petrock

This re-implementation is not a perfect 1:1 copy of the original, but attempts
to faithfully recreate the idea behind it for the EuroPi module.

Instead of using colours to differentiate between the moods, this program
displays moods using Tarot and/or playing card suits:
- swords (red)
- cups (blue)
- shields (wands/clubs is the official tarot suit here, but clubs goes with the
  english card suits below, and shields fit with swords, and are found in some
  swiss-german decks of cards) (yellow)
- pentacles (green)

An additional 4 moods were included in the original C++ firmware, but were
deprecated. They are also re-implemented here, but disabled by default:
- hearts
- spades
- diamonds
- clubs
"""

from europi import *
from europi_script import EuroPiScript

import configuration
from framebuf import FrameBuffer, MONO_HLSB
import math
import random
import time

from experimental.a_to_d import AnalogReaderDigitalWrapper
from experimental.experimental_config import RTC_NONE
from experimental.math_extras import rescale
from experimental.random_extras import shuffle
from experimental.rtc import *


class Algo:
    """
    Generic algorithm for generating the gate sequences

    All pseudo-random algorithms inherit from this class
    """

    CHANNEL_A = 1
    CHANNEL_B = 2

    def __init__(self, channel, weekday, cycle, continuity, algorithm, mood_name):
        """
        Child constructors must call this first

        Child constructors must initialize self.sequence by appending {0, 1} values to it

        @param channel  1 for channel A, 2 for channel B
        @param weekday  The current weekday 1-7 (M-Su)
        @param cycle  The current moon phase: 0-7 (new to waning crescent)
        @param continuity  A random value shared between both A and B channels: 0-100
        @param algorithm  The name of the generator algorithm (used for logging only)
        @param mood_name  The name of the mood symbol/suit (used for logging only)
        """
        self.algorithm_name = algorithm
        self.mood_name = mood_name

        self.channel = channel

        if channel == self.CHANNEL_A:
            self.gate_out = cv1
            self.inv_out = cv2
            self.eos_out = cv3
        else:
            self.gate_out = cv4
            self.inv_out = cv5
            self.eos_out = cv6

        self.weekday = weekday
        self.cycle = cycle
        self.continuity = continuity

        self.sequence = []
        self.index = 0

        self.state_dirty = False

    def sanitize_sequence(self, sequence=None):
        """
        Ensure that the sequence is neither all-1 nor all-0

        If either is true, flip a random element

        This should be called after generating the sequence in the child class constructors

        @param sequence  If none, self.sequence is sanitized
        """
        if sequence is None:
            sequence = self.sequence

        empty = True
        full = True
        for n in sequence:
            if n == 0:
                full = False
            else:
                empty = False

        # flip an item if the pattern is wholly uniform
        if empty or full:
            sequence[random.randint(0, len(sequence) -1)] = (sequence[random.randint(0, len(sequence) -1)] + 1) % 2

    def __str__(self):
        return f"{self.sequence}"

    def __eq__(self, other):
        """
        Return True if both sequences are identical
        """
        if len(self.sequence) == len(other.sequence):
            for i in range(len(self.sequence)):
                if self.sequence[i] != other.sequence[i]:
                    return False
            return True
        return False

    @staticmethod
    def map(x, in_min, in_max, out_min, out_max):
        # treat the output as inclusive
        out_max = out_max + 1
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def tick(self):
        """
        Advance the sequence
        """
        self.index = (self.index + 1 ) % len(self.sequence)
        self.state_dirty = True

    def set_outputs(self):
        """
        Set the outputs high/low as needed
        """
        if self.sequence[self.index]:
            self.gate_out.on()
            self.inv_out.off()
        else:
            self.gate_out.off()
            self.inv_out.on()

        if self.index == len(self.sequence) - 1:
            self.eos_out.on()

        self.state_dirty = False

    def outputs_off(self):
        self.gate_out.off()
        self.inv_out.off()
        self.eos_out.off()


class AlgoPlain(Algo):
    """
    A straight-forward random-fill

    We choose a length based on the moon phase and then fill it with on/off signals
    using a coin-toss.

    This _could_ result in all-on or all-off patterns, but this is generally unlikely

    This corresponds to the red mood in the original firmware
    """

    # swords
    mood_graphics = bytearray(b'\x00\x00\x00\x1f\x00\x00\x00!\x00\x00\x00A\x00\x00\x00\x81\x00\x00\x01\x01\x00\x00\x02\x02\x00\x00\x04\x04\x00\x00\x08\x08\x00\x00\x10\x10\x00\x00  \x00\x00@@\x00\x00\x80\x80\x00\x01\x01\x00\x00\x02\x02\x00\x04\x04\x04\x00\x04\x08\x08\x00\x06\x10\x10\x00\x07  \x00\x03\xc0@\x00\x01\xc0\x80\x00\x00\xe1\x00\x00\x00r\x00\x00\x00\xfc\x00\x00\x01\xdc\x00\x00\x03\x8e\x00\x00\x07\x07\x00\x00~\x03\xc0\x00|\x00\x00\x00|\x00\x00\x00|\x00\x00\x00|\x00\x00\x00\x00\x00\x00\x00')

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity, "plain", "swords")

        seqmax = 0

        if cycle == MoonPhase.NEW_MOON:
            seqmax = random.randint(5, 7)
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WANING_CRESCENT:
            seqmax = random.randint(4, 16)
        elif cycle == MoonPhase.FIRST_QUARTER or cycle == MoonPhase.THIRD_QUARTER:
            seqmax = Algo.map(continuity, 0, 100, 6, 12)
            seqmax = seqmax * self.channel  # channel B is twice as long as A
        elif cycle == MoonPhase.WAXING_GIBBOUS:
            seqmax = 12
        elif cycle == MoonPhase.WANING_GIBBOUS:
            seqmax = 16
        else:
            seqmax = 16

        # From Jonah S:
        # Randomly populate rhythm
        # this may seems weird/cheesy, but as I note in the manual - I decided to focus on
        # one and only one translated elements for the moon cycle, which is the length
        # relationship of A and B - I found through practice that the random population of
        # steps actually produces great results, the key is how many steps you use, and the
        # relationship between the 2 step lengths. The interesting difference is comparing
        # for example a pair of 8 step rhythms, vs a 7 step rhythm, and a 15 step rhythm
        # being played against each other - this is the "meta movement" of the rhythmic
        # flavor, in every algo/mood
        for i in range(seqmax):
            self.sequence.append(random.randint(0, 1))

        self.sanitize_sequence()


class AlgoReich(Algo):
    """
    Choose a random pattern length pased on the moon phase and our continuity variable
    and fill the pattern with on/off using a fixed density

    This corresponds to the blue mood in the original firmware
    """

    # cups
    mood_graphics = bytearray(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xfe?\xff\xff\xfc?\xff\xff\xfc\x1f\xff\xff\xf8\x0f\xff\xff\xf0\x07\xff\xff\xe0\x03\xff\xff\xc0\x01\xff\xff\x80\x00\x7f\xfe\x00\x00\x0f\xf0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x0f\xf0\x00\x00\x7f\xfe\x00\x01\xff\xff\x80\x03\xff\xff\xc0')

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity, "reich", "cups")

        if cycle == MoonPhase.NEW_MOON:
            seqmax = random.randint(3, 5)
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WAXING_CRESCENT:
            if channel == Algo.CHANNEL_A:
                seqmax = Algo.map(continuity, 0, 100, 3, 8)
            else:
                a = Algo.map(continuity, 0, 100, 3, 8)
                b = 0
                while b == 0 or b == a or b == a*2 or b*2 == a:
                    b = random.randint(3, 8)

                seqmax = b
        elif cycle == MoonPhase.FIRST_QUARTER or cycle == MoonPhase.THIRD_QUARTER:
            seqmax = Algo.map(continuity, 0, 100, 5, 9)
            seqmax = seqmax * channel  # B is double A
        elif cycle == MoonPhase.WAXING_GIBBOUS or cycle == MoonPhase.WANING_GIBBOUS:
            seqmax = Algo.map(continuity, 0, 100, 4, 8)
        else:
            seqmax = 8

        seqDensity=50
        for i in range(seqmax):
            if random.randint(0, 99) < seqDensity:
                self.sequence.append(1)
            else:
                self.sequence.append(0)

        self.sanitize_sequence()


class AlgoSparse(Algo):
    """
    Chooses a fixed length based on moon phase and fills the pattern with a low-density
    on/off pattern (10% on)

    This corresponds to the yellow mood in the original firmware
    """

    # shields
    mood_graphics = bytearray(b'\xff\xff\xff\xff\x9f\xff\xff\xff\x8f\xff\xe0?\x87\xff\xf0\x7f\x83\xff\xb8\xef\xc1\xff\x98\xcf\xe0\xff\x80\x0f\xf0\x7f\x80\x0f\xf8?\x80\x0f\xfc\x1f\x98\xcf\xfe\x0f\xb8\xef\xff\x07\xf0\x7f\xff\x83\xe0?\xff\xc1\xff\xff\xff\xe0\xff\xff\xff\xf0\x7f\xff\xff\xf8?\xff\x7f\xfc\x1f\xfe?\xfe\x0f\xfc\x1f\xff\x07\xf8\x0f\xff\x83\xf0\x07\xff\xc1\xe0\x03\xff\xe0\xc0\x01\xff\xf0\x80\x00\xff\xf9\x00\x00\x7f\xfe\x00\x00?\xfc\x00\x00\x1f\xf8\x00\x00\x0f\xf0\x00\x00\x07\xe0\x00\x00\x03\xc0\x00\x00\x01\x80\x00')

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity, "sparse", "shields")

        if cycle == MoonPhase.NEW_MOON:
            seqmax = random.randint(10, 19)
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WANING_CRESCENT:
            seqmax = random.randint(15, 30)
        elif cycle == MoonPhase.FIRST_QUARTER:
            if channel == Algo.CHANNEL_A:
                seqmax = 32
            else:
                seqmax = 64
        elif cycle == MoonPhase.THIRD_QUARTER:
            if channel == Algo.CHANNEL_A:
                seqmax = 24
            else:
                seqmax = 48
        elif cycle == MoonPhase.WAXING_GIBBOUS:
            seqmax = 32
        elif cycle == MoonPhase.WANING_GIBBOUS:
            seqmax = 24
        else:
            seqmax = 64

        densityPercent = 10

        for i in range(seqmax):
            self.sequence.append(0)

        seedStepInd = random.randint(0, seqmax - 1)
        self.sequence[seedStepInd] = 1

        for i in range(seqmax):
            if random.randint(0, 99) < densityPercent:
                self.sequence[i] = 1

        self.sanitize_sequence()


class AlgoVari(Algo):
    """
    Generates two sub-sequences A & B, repeating each a fixed number of times

    e.g. if sequence a is 0011 and sequence b is 1010, with 2 repeats the final pattern
    is 0011 0011 1010 1010

    This corresponds to the green mood in the original firmware
    """

    # pentacles
    mood_graphics = bytearray(b'\x00\x07\xe0\x00\x009\x9c\x00\x00\xc1\x83\x00\x01\x01\x80\x80\x02\x02@@\x04\x02@ \x08\x02@\x10\x10\x04 \x08 \x04 \x04 \x04 \x04@\x08\x10\x02\x7f\xff\xff\xfeP\x08\x10\n\x88\x10\x08\x11\x84\x10\x08!\x83\x10\x08\xc1\x80\xa0\x05\x01\x80`\x06\x01\x800\x0c\x01@H\x12\x02@Fb\x02@A\x82\x02 \x81\x81\x04 \x86a\x04\x10\x88\x11\x08\t0\x0c\x90\x05@\x02\xa0\x03\x80\x01\xc0\x01\x00\x00\x80\x00\xc0\x03\x00\x008\x1c\x00\x00\x07\xe0\x00')

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity, "vari", "pentacles")

        if cycle == MoonPhase.NEW_MOON:
            seqmax = random.randint(3, 19)
            repeats = 3
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WANING_CRESCENT:
            seqmax = random.randint(8, 12)
            repeats = random.randint(3, 6)
        elif cycle == MoonPhase.FIRST_QUARTER or cycle == MoonPhase.THIRD_QUARTER:
            seqmax = 8
            if channel == Algo.CHANNEL_A:
                repeats = 4
            else:
                repeats = 8
        elif cycle == MoonPhase.WAXING_GIBBOUS or cycle == MoonPhase.WANING_GIBBOUS:
            seqmax = 16
            repeats = 4
        else:
            seqmax = 12
            repeats = 3

        seq_a = []
        seq_b = []
        for i in range(seqmax):
            r = random.randint(0, 1)
            seq_a.append(r)
            seq_b.append(r)

        for i in range(seqmax-1, -1, -1):
            j = random.randint(0, i)

            tmp = seq_b[i]
            seq_b[i] = seq_b[j]
            seq_b[j] = i

        # the whole sequence is r * [seq_a] + r * [seq_b]
        for r in range(repeats):
            for n in seq_a:
                self.sequence.append(n)
        for r in range(repeats):
            for n in seq_b:
                self.sequence.append(n)

        self.sanitize_sequence()


class AlgoBlocks(Algo):
    """
    Builds the sequence by randomly choosing N pre-defined pattern blocks

    One of the unimplemented algorithms in the original firmware
    """

    # hearts
    mood_graphics = bytearray(b'\x07\xe0\x07\xe0\x1f\xf8\x1f\xf8?\xfc?\xfc\x7f\xfe\x7f\xfe\x7f\xfe\x7f\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xfe?\xff\xff\xfc\x1f\xff\xff\xf8\x1f\xff\xff\xf8\x0f\xff\xff\xf0\x07\xff\xff\xe0\x07\xff\xff\xe0\x03\xff\xff\xc0\x01\xff\xff\x80\x01\xff\xff\x80\x00\xff\xff\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00?\xfc\x00\x00\x1f\xf8\x00\x00\x1f\xf8\x00\x00\x0f\xf0\x00\x00\x07\xe0\x00\x00\x07\xe0\x00\x00\x03\xc0\x00\x00\x01\x80\x00')

    blocks = [
        [0, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 0, 1, 0],
        [1, 0, 0, 1],
        [1, 1, 1, 0],
        [1, 0, 1, 1],
        [0, 0, 1, 0],
        [1, 1, 1, 1],
    ]

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity, "blocks", "hearts")

        # This is wholly original
        # the original, deprecated code has a to-do here
        if cycle == MoonPhase.NEW_MOON:
            numblocks = 2
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WANING_CRESCENT:
            numblocks = random.randint(3, 4)
        elif cycle == MoonPhase.FIRST_QUARTER or cycle == MoonPhase.THIRD_QUARTER:
            numblocks = random.randint(2, 3)
            numblocks = numblocks * self.channel  # B is double A
        elif cycle == MoonPhase.WAXING_GIBBOUS or cycle == MoonPhase.WANING_GIBBOUS:
            numblocks = random.randint(4, 5)
        else:
            numblocks = 6

        for i in range(numblocks):
            block = AlgoBlocks.blocks[random.randint(0, len(AlgoBlocks.blocks) - 1)]
            for n in block:
                self.sequence.append(n)

        self.sanitize_sequence()


class AlgoCulture(Algo):
    """
    Chooses a pre-programmed rhythm based on the weekday and adds a random number
    of coin-toss steps to the end of it

    The back half of the rhythms is zero, resulting in some interesting hand-offs between
    the main and inverted outputs.

    One of the unimplemented algorithms in the original firmware
    """

    # spades
    mood_graphics = bytearray(b'\x00\x01\x80\x00\x00\x03\xc0\x00\x00\x07\xe0\x00\x00\x0f\xf0\x00\x00\x1f\xf8\x00\x00?\xfc\x00\x00\x7f\xfe\x00\x00\xff\xff\x00\x01\xff\xff\x80\x03\xff\xff\xc0\x07\xff\xff\xe0\x0f\xff\xff\xf0\x1f\xff\xff\xf8?\xff\xff\xfc\x7f\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xfe\x7f\xff\xff\xfe?\xfd\xbf\xfc\x1f\xf9\x9f\xf8\x07\xe1\x87\xe0\x00\x01\x80\x00\x00\x01\x80\x00\x00\x01\x80\x00\x00\x07\xe0\x00\x00\x1f\xf8\x00\x00?\xfc\x00')

    rhythms = [
        [1,0,0,1,1,0,1,0,1,0,0,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,1,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,1,0,0,1,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,1,0,1,0,1,0,1,0,0,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,1,1,1,1,0,0,1,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,1,0,1,1,0,1,0,1,1,0,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,1,0,0,1,0,0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity, "culture", "spades")

        # add or remove some steps based on the moon phase
        if cycle == MoonPhase.NEW_MOON:
            extra_steps = random.randint(-16, -8)
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WANING_CRESCENT:
            extra_steps = random.randint(0, 4)
        elif cycle == MoonPhase.FIRST_QUARTER or cycle == MoonPhase.THIRD_QUARTER:
            extra_steps = random.randint(-8, 8)
        elif cycle == MoonPhase.WAXING_GIBBOUS or cycle == MoonPhase.WANING_GIBBOUS:
            extra_steps = random.randint(-4, 12)
        else:
            extra_steps = random.randint(-4, 4)

        rhythm = AlgoCulture.rhythms[weekday]
        for i in range(len(rhythm) + extra_steps):
            if i < len(rhythm):
                self.sequence.append(rhythm[i])
            else:
                self.sequence.append(0)

        # backfill the second half-ish of the rhythm with randomness
        for i in range(15, len(self.sequence)):
            self.sequence[i] = random.randint(0, 1)

        self.sanitize_sequence()


class AlgoOver(Algo):
    """
    Generates two sub-sequences and overwrites parts of the main sequence with each
    after each complete cycle

    One of the unimplemented algorithms in the original firmware
    """

    # diamonds
    mood_graphics = bytearray(b'\x00\x01\x80\x00\x00\x01\x80\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x07\xe0\x00\x00\x07\xe0\x00\x00\x0f\xf0\x00\x00\x0f\xf0\x00\x00\x1f\xf8\x00\x00\x1f\xf8\x00\x00?\xfc\x00\x00?\xfc\x00\x00\x7f\xfe\x00\x00\xff\xff\x00\x03\xff\xff\xc0\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x03\xff\xff\xc0\x00\xff\xff\x00\x00\x7f\xfe\x00\x00?\xfc\x00\x00?\xfc\x00\x00\x1f\xf8\x00\x00\x1f\xf8\x00\x00\x0f\xf0\x00\x00\x0f\xf0\x00\x00\x07\xe0\x00\x00\x07\xe0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x01\x80\x00\x00\x01\x80\x00')

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity, "over", "diamonds")

        densityPercent = 50

        # same lengths as AlgoPlain
        if cycle == MoonPhase.NEW_MOON:
            seqmax = random.randint(5, 7)
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WANING_CRESCENT:
            seqmax = random.randint(4, 16)
        elif cycle == MoonPhase.FIRST_QUARTER or cycle == MoonPhase.THIRD_QUARTER:
            seqmax = Algo.map(continuity, 0, 100, 6, 12)
            seqmax = seqmax * self.channel  # channel B is twice as long as A
        elif cycle == MoonPhase.WAXING_GIBBOUS:
            seqmax = 12
        elif cycle == MoonPhase.WANING_GIBBOUS:
            seqmax = 16
        else:
            seqmax = 16

        self.seq1 = []
        self.seq2 = []

        for i in range(seqmax):
            if random.randint(0, 99) < densityPercent:
                self.seq1.append(1)
            else:
                self.seq1.append(0)

            if random.randint(0, 99) < densityPercent:
                self.seq2.append(1)
            else:
                self.seq2.append(0)


        self.swaps = list(range(seqmax))
        shuffle(self.swaps)
        self.switch_index = 0
        self.swap = True

        self.sanitize_sequence(self.seq1)
        self.sanitize_sequence(self.seq2)

        for n in self.seq1:
            self.sequence.append(n)

    def tick(self):
        super().tick()

        # overwrite steps betwen seq1 and seq2
        if self.index == 0:
            overwrite_index = self.swaps[self.switch_index]
            self.switch_index += 1

            if self.switch_index > len(self.sequence) - 1:
                self.switch_index = 0
                self.swap = not self.swap

            if not self.swap:
                self.sequence[overwrite_index] = self.seq2[overwrite_index]
            else:
                self.sequence[overwrite_index] = self.seq1[overwrite_index]


class AlgoWonk(Algo):
    """
    Generates a fixed-length pattern with a random density based on the weekday. We then
    "wonk" a number of steps based on the moon phase

    Wonking means we choose a random on-step, turn it off, and then turn the step before
    or after on.

    One of the unimplemented algorithms in the original firmware
    """

    # clubs
    mood_graphics = bytearray(b'\x00\x07\xe0\x00\x00\x0f\xf0\x00\x00\x1f\xf8\x00\x00?\xfc\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x0f\xff\xff\xf0\x1f\xff\xff\xf8?\xff\xff\xfc\x7f\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xfb\xdf\xfe?\xf3\xcf\xfc\x1f\xe3\xc7\xf8\x0f\xc3\xc3\xf0\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x07\xe0\x00\x00\x0f\xf0\x00\x00\x1f\xf8\x00\x00?\xfc\x00\x00\x7f\xfe\x00')

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity, "wonk", "clubs")

        densityPercent = Algo.map(weekday, 1, 7, 30, 60)

        seqmax = 32

        for i in range(seqmax):
            self.sequence.append(0)


        # ensure there is at least 1 filled step
        self.sequence[random.randint(0, seqmax - 1)] = 1

        steps_placed = 0
        for i in range(0, seqmax, 4):
            if random.randint(0, 99) < densityPercent:
                self.sequence[i] = 1
                steps_placed += 1

        steps_to_wonk = Algo.map(cycle, 0, 7, 1, steps_placed)
        steps_wonked = 0
        while steps_wonked < steps_to_wonk:
            chosen_step = random.randint(0, seqmax - 1)

            if self.sequence[chosen_step] == 1:
                steps_wonked += 1
                self.sequence[chosen_step] = 0

                r = random.randint(0, 1)
                if chosen_step == 0:
                    self.sequence[chosen_step + 1] = 1
                elif chosen_step == seqmax - 1:
                    self.sequence[chosen_step - 1] = 1
                elif r == 0:
                    self.sequence[chosen_step + 1] = 1
                else:
                    self.sequence[chosen_step - 1] = 1

        self.sanitize_sequence()


class MoonPhase:
    """
    Calculates the current moon phase
    """

    NEW_MOON = 0
    WAXING_CRESCENT = 1
    FIRST_QUARTER = 2
    WAXING_GIBBOUS = 3
    FULL_MOON = 4
    WANING_GIBBOUS = 5
    THIRD_QUARTER = 6
    WANING_CRESCENT = 7

    moon_phase_images = [
        bytearray(b'\x00\x07\xc0\x00\x000\x0c\x00\x00\x80\x01\x00\x03\x00\x00\xc0\x04\x00\x00 \x08\x00\x00\x10\x00\x00\x00\x00\x10\x00\x00\x08 \x00\x00\x04\x00\x00\x00\x00@\x00\x00\x02@\x00\x00\x02\x00\x00\x00\x00\x80\x00\x00\x01\x80\x00\x00\x01\x80\x00\x00\x01\x80\x00\x00\x01\x80\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x02@\x00\x00\x02\x00\x00\x00\x00 \x00\x00\x04\x10\x00\x00\x08\x10\x00\x00\x08\x08\x00\x00\x10\x04\x00\x00 \x01\x00\x00\x80\x00\x80\x01\x00\x000\x0c\x00\x00\x07\xc0\x00'),
        bytearray(b'\x00\x0b\xe0\x00\x000\xfe\x00\x00\x80\x1f\x00\x01\x00\x0f\xc0\x04\x00\x03\xe0\x00\x00\x01\xf0\x00\x00\x00\xf8\x10\x00\x00\xf8 \x00\x00|\x00\x00\x00>@\x00\x00>@\x00\x00>\x00\x00\x00\x1e\x00\x00\x00\x1f\x80\x00\x00\x1f\x00\x00\x00\x1f\x80\x00\x00\x1f\x00\x00\x00\x1f\x00\x00\x00\x1f\x00\x00\x00\x1e@\x00\x00>@\x00\x00>\x00\x00\x00< \x00\x00|\x10\x00\x00\xf8\x00\x00\x00\xf8\x08\x00\x01\xf0\x00\x00\x03\xe0\x01\x00\x0f\xc0\x00\x80\x1f\x00\x000\xfc\x00\x00\x0b\xe0\x00'),
        bytearray(b'\x00\x02\xe0\x00\x000\xfe\x00\x00\x80\xff\x00\x01\x00\xff\xc0\x04\x00\xff\xe0\x00\x00\xff\xf0\x00\x00\xff\xf8\x10\x00\xff\xf8 \x00\xff\xfc\x00\x00\xff\xfe@\x00\xff\xfe@\x00\xff\xfe\x00\x00\xff\xfe\x00\x00\xff\xff\x80\x00\xff\xff\x00\x00\xff\xff\x80\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xfe@\x00\xff\xfe@\x00\xff\xfe\x00\x00\xff\xfc \x00\xff\xfc\x10\x00\xff\xf8\x00\x00\xff\xf8\x08\x00\xff\xf0\x00\x00\xff\xe0\x01\x00\xff\xc0\x00\x80\xff\x00\x000\xfc\x00\x00\x02\xe0\x00'),
        bytearray(b'\x00\x02\x90\x00\x000\xfc\x00\x00\x83\xff\x00\x01\x07\xff\xc0\x04\x0f\xff\xe0\x00\x1f\xff\xf0\x00?\xff\xf8\x10\x7f\xff\xf8 \x7f\xff\xfc\x00\xff\xff\xfe@\xff\xff\xfe@\xff\xff\xfe\x01\xff\xff\xfe\x01\xff\xff\xff\x81\xff\xff\xff\x01\xff\xff\xff\x81\xff\xff\xff\x01\xff\xff\xff\x01\xff\xff\xff\x01\xff\xff\xfe@\xff\xff\xfe@\xff\xff\xfe\x00\xff\xff\xfc \x7f\xff\xfc\x10\x7f\xff\xf8\x00?\xff\xf8\x08\x1f\xff\xf0\x00\x0f\xff\xe0\x01\x07\xff\xc0\x00\x83\xff\x00\x000\xfc\x00\x00\x02\x90\x00'),
        bytearray(b'\x00\x07\xc0\x00\x00?\xfc\x00\x00\xff\xff\x00\x03\xff\xff\xc0\x07\xff\xff\xe0\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x1f\xff\xff\xf8?\xff\xff\xfc?\xff\xff\xfc\x7f\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xfe?\xff\xff\xfc?\xff\xff\xfc\x1f\xff\xff\xf8\x1f\xff\xff\xf8\x0f\xff\xff\xf0\x07\xff\xff\xe0\x01\xff\xff\x80\x00\xff\xff\x00\x00?\xfc\x00\x00\x07\xc0\x00'),
        bytearray(b'\x00\t\x80\x00\x00\x7f\x0c\x00\x00\xff\xc1\x00\x03\xff\xe0\x80\x07\xff\xf0 \x0f\xff\xf8\x00\x1f\xff\xfc\x00\x1f\xff\xfe\x08?\xff\xfe\x04\x7f\xff\xff\x00\x7f\xff\xff\x02\x7f\xff\xff\x02\xff\xff\xff\x80\x7f\xff\xff\x80\xff\xff\xff\x81\xff\xff\xff\x81\xff\xff\xff\x80\xff\xff\xff\x81\xff\xff\xff\x80\x7f\xff\xff\x80\x7f\xff\xff\x02\x7f\xff\xff\x02?\xff\xff\x00?\xff\xfe\x04\x1f\xff\xfe\x08\x1f\xff\xfc\x00\x0f\xff\xf8\x00\x07\xff\xf0\x00\x03\xff\xe0\x80\x00\xff\xc1\x00\x00\x7f\x0c\x00\x00\t\x80\x00'),
        bytearray(b'\x00\x0b\x80\x00\x00\x7f\x0c\x00\x00\xff\x01\x00\x03\xff\x00\x80\x07\xff\x00 \x0f\xff\x00\x00\x1f\xff\x00\x00\x1f\xff\x00\x08?\xff\x00\x04\x7f\xff\x00\x00\x7f\xff\x00\x02\x7f\xff\x00\x02\xff\xff\x00\x00\x7f\xff\x00\x00\xff\xff\x00\x01\xff\xff\x00\x01\xff\xff\x00\x00\xff\xff\x00\x01\xff\xff\x00\x00\x7f\xff\x00\x00\x7f\xff\x00\x02\x7f\xff\x00\x02?\xff\x00\x00?\xff\x00\x04\x1f\xff\x00\x08\x1f\xff\x00\x00\x0f\xff\x00\x00\x07\xff\x00\x00\x03\xff\x00\x80\x00\xff\x01\x00\x00\x7f\x0c\x00\x00\x0b\x80\x00'),
        bytearray(b'\x00\x0b\xe0\x00\x00\x7f\x0c\x00\x00\xf8\x01\x00\x03\xf0\x00\x80\x07\xc0\x00 \x0f\x80\x00\x00\x1f\x00\x00\x00\x1f\x00\x00\x08>\x00\x00\x04|\x00\x00\x00|\x00\x00\x02|\x00\x00\x02\xf8\x00\x00\x00x\x00\x00\x00\xf8\x00\x00\x01\xf8\x00\x00\x01\xf8\x00\x00\x00\xf8\x00\x00\x01\xf8\x00\x00\x00x\x00\x00\x00|\x00\x00\x02|\x00\x00\x02<\x00\x00\x00>\x00\x00\x04\x1f\x00\x00\x08\x1f\x00\x00\x00\x0f\x80\x00\x00\x07\xc0\x00\x00\x03\xf0\x00\x80\x00\xf8\x01\x00\x00\x7f\x0c\x00\x00\x0b\xe0\x00'),
    ]

    @staticmethod
    def calculate_days_since_new_moon(date):
        """
        Calculate the number of days since a known full moon

        @see https://www.subsystems.us/uploads/9/8/9/4/98948044/moonphase.pdf

        @param date  The current UTC DateTime
        """
        if date.year < 2000:
            raise ValueError(f"Date out of range; check your RTC")

        y = date.year
        m = date.month
        d = date.day

        if m == Month.JANUARY or m == Month.FEBRUARY:
            y = y - 1
            m = m + 12

        a = math.floor(y/100)
        b = math.floor(a/4)
        c = 2 - a + b
        e = math.floor(365.25 * (y + 4716))
        f = math.floor(30.6001 * (m + 1))
        jd = c + d + e + f - 1524.5

        days_since_new_moon = jd - 2451549.5

        return days_since_new_moon

    @staticmethod
    def calculate_phase(date):
        """
        Calculate the current moon phase

        @param date  The current UTC DateTime
        """
        days_since_new_moon = MoonPhase.calculate_days_since_new_moon(date)

        yesterday_new_moons = (days_since_new_moon - 1) / 29.53
        today_new_moons = days_since_new_moon / 29.53
        tomorrow_new_moons = (days_since_new_moon + 1) / 29.53

        # we always want 1 day assigned to new, first quarter, full, and third quarter
        # so use yesterday, today, and tomorrow as a 3-day window
        # if tomorrow is on one side of the curve and yesterday was the other, treat today
        # as the "special" phase
        yesterday_fraction = yesterday_new_moons % 1
        today_fraction = today_new_moons % 1
        tomorrow_fraction = tomorrow_new_moons % 1

        # first cases are for the special 1-day events
        # check if we're in the transition area, and then decide if today is actually closest
        # to the event
        if yesterday_fraction > 0.75 and tomorrow_fraction < 0.25:
            if MoonPhase.closest_to_fraction(0.0, yesterday_fraction, today_fraction, tomorrow_fraction) == 0:
                return MoonPhase.NEW_MOON
            elif today_fraction > 0.75:
                return MoonPhase.WANING_CRESCENT
            else:
                return MoonPhase.WAXING_CRESCENT
        elif yesterday_fraction < 0.25 and tomorrow_fraction > 0.25:
            if MoonPhase.closest_to_fraction(0.25, yesterday_fraction, today_fraction, tomorrow_fraction) == 0:
                return MoonPhase.FIRST_QUARTER
            elif today_fraction < 0.25:
                return MoonPhase.WAXING_CRESCENT
            else:
                return MoonPhase.WAXING_GIBBOUS
        elif yesterday_fraction < 0.5 and tomorrow_fraction > 0.5:
            if MoonPhase.closest_to_fraction(0.5, yesterday_fraction, today_fraction, tomorrow_fraction) == 0:
                return MoonPhase.FULL_MOON
            elif today_fraction < 0.5:
                return MoonPhase.WAXING_GIBBOUS
            else:
                return MoonPhase.WANING_GIBBOUS
        elif yesterday_fraction < 0.75 and tomorrow_fraction > 0.75:
            if MoonPhase.closest_to_fraction(0.75, yesterday_fraction, today_fraction, tomorrow_fraction) == 0:
                return MoonPhase.THIRD_QUARTER
            elif today_fraction < 0.75:
                return MoonPhase.WANING_GIBBOUS
            else:
                return MoonPhase.WANING_CRESCENT
        elif today_fraction == 0.0:
            return MoonPhase.NEW_MOON
        elif today_fraction < 0.25:
            return MoonPhase.WAXING_CRESCENT
        elif today_fraction == 0.25:
            return MoonPhase.FIRST_QUARTER
        elif today_fraction < 0.5:
            return MoonPhase.WAXING_GIBBOUS
        elif today_fraction == 0.5:
            return MoonPhase.FULL_MOON
        elif today_fraction < 0.75:
            return MoonPhase.WANING_GIBBOUS
        elif today_fraction == 0.75:
            return MoonPhase.THIRD_QUARTER
        else:
            return MoonPhase.WANING_CRESCENT

    @staticmethod
    def closest_to_fraction(fraction, yesterday, today, tomorrow):
        yesterday = abs(fraction - yesterday)
        today = abs(fraction - today)
        tomorrow = abs(fraction - tomorrow)

        if yesterday < tomorrow and yesterday < today:  # yesterday is closest
            return -1
        elif today < yesterday and today < tomorrow:  # today is closest
            return 0
        else:
            return 1  # tomorrow is closest


class Mood:
    """
    The algorithm's "mood"

    Mood is one of 4 colours, which rotates every moon cycle
    """

    available_moods = [
        AlgoPlain,
        AlgoReich,
        AlgoSparse,
        AlgoVari
    ]

    @staticmethod
    def set_moods(moodstring):
        if moodstring == "all":
            Mood.available_moods = [
                AlgoPlain,
                AlgoReich,
                AlgoSparse,
                AlgoVari,
                AlgoBlocks,
                AlgoCulture,
                AlgoOver,
                AlgoWonk,
            ]
        elif moodstring == "alternate":
            Mood.available_moods = [
                AlgoBlocks,
                AlgoCulture,
                AlgoOver,
                AlgoWonk,
            ]
        else:  # "classic"
            Mood.available_moods = [
                AlgoPlain,
                AlgoReich,
                AlgoSparse,
                AlgoVari,
            ]

    @staticmethod
    def mood_algorithm(date):
        """
        Get the algorithm for the current mood

        @param date  The current UTC DateTime
        """
        days_since_new_moon = MoonPhase.calculate_days_since_new_moon(date)
        cycles = math.floor(days_since_new_moon / 29.53)

        return Mood.available_moods[cycles % len(Mood.available_moods)]


class IntervalTimer:
    """
    Uses ticks_ms and ticks_diff to fire a callback at fixed-ish intervals
    """

    MIN_INTERVAL = 10
    MAX_INTERVAL = 500

    def __init__(self, speed_knob, rise_cb=lambda: None, fall_cb=lambda: None):
        self.interval_ms = 0
        self.last_tick_at = time.ticks_ms()

        self.speed_knob = speed_knob

        self.rise_callback = rise_cb
        self.fall_callback = fall_cb

        self.next_rise = True

        self.update_interval()

    def update_interval(self):
        DEADZONE = 0.1
        p = self.speed_knob.percent()
        if p <= DEADZONE:
            # disable the timer for the first 10% of travel so we have an easy-off
            # for external clocking
            self.interval_ms = 0
        else:
            p = 1.0 - rescale(p, DEADZONE, 1, 0, 1)
            self.interval_ms = round(rescale(p, 0, 1, self.MIN_INTERVAL, self.MAX_INTERVAL))

    def tick(self):
        # kick out immediately if the timer is off
        if self.interval_ms <= 0:
            return

        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_tick_at) >= self.interval_ms:
            self.last_tick_at = now

            if self.next_rise:
                self.rise_callback()
                self.next_rise = False
            else:
                self.fall_callback()
                self.next_rise = True


class NoClockError(Exception):
    """
    A custom exception we can raise if the RTC is not configured correctly
    """
    def __init__(self, message):
        super().__init__(message)


class PetRock(EuroPiScript):

    def __init__(self):
        super().__init__()

        # validate the clock and raise a NoClockError if
        # we are using the default no-RTC implementation
        if experimental_config.RTC_IMPLEMENTATION == RTC_NONE:
            raise NoClockError("No clock configured")

        Mood.set_moods(self.config.MOODS)

        self.seed_offset = 1
        self.generate_sequences(clock.utcnow())

        self.din2 = AnalogReaderDigitalWrapper(
            ain,
            cb_rising = self.on_channel_b_trigger,
            cb_falling = self.on_channel_b_fall
        )
        b2.handler(self.on_channel_b_trigger)
        b2.handler_falling(self.on_channel_b_fall)
        self.timer_b = IntervalTimer(
            k2,
            rise_cb=self.on_channel_b_trigger,
            fall_cb=self.on_channel_b_fall
        )

        din.handler(self.on_channel_a_trigger)
        din.handler_falling(self.on_channel_a_fall)
        b1.handler(self.on_channel_a_trigger)
        b1.handler_falling(self.on_channel_a_fall)
        self.timer_a = IntervalTimer(
            k1,
            rise_cb=self.on_channel_a_trigger,
            fall_cb=self.on_channel_a_fall
        )

    @classmethod
    def config_points(cls):
        return [
            # What moods does the user want to use?
            # - classic: the original 4 moods from the hardware Pet Rock
            # - alternate: the 4 deprecated moods that weren't implemented
            # - all: all 8 possible moods
            configuration.choice(
                "MOODS",
                choices=[
                    "classic",
                    "alternate",
                    "all"
                ],
                default="classic",
            ),
        ]

    def generate_sequences(self, now):
        """
        Regenerate the day's rhythms

        @param now  The current UTC
        """
        if now.weekday is None:
            now.weekday = 0

        local_weekday = (now + local_timezone).weekday

        continuity = random.randint(0, 99)
        cycle = MoonPhase.calculate_phase(now)
        today_seed = now.day + now.month + now.year + self.seed_offset
        random.seed(today_seed)

        self.sequence_a = Mood.mood_algorithm(now)(Algo.CHANNEL_A, local_weekday, cycle, continuity)
        self.sequence_b = Mood.mood_algorithm(now)(Algo.CHANNEL_B, local_weekday, cycle, continuity)

        self.last_generation_at = clock.localnow()

        # print a YAML-like block with the sequences for debugging
        print(f"# Generated sequences at {self.last_generation_at} ({local_timezone})")
        print("parameters:")
        print(f"  continuity: {continuity}")
        print(f"  date: '{now} UTC'")
        print(f"  moon_phase: {cycle}")
        print(f"  today_seed: {today_seed}")
        print(f"  weekday: {local_weekday}")
        print("sequences:")
        print(f"  algorithm: {self.sequence_a.algorithm_name}")
        print(f"  mood: {self.sequence_a.mood_name}")
        print(f"  seq_a: {self.sequence_a}")
        print(f"  seq_b: {self.sequence_b}")

    def on_channel_a_trigger(self):
        self.sequence_a.tick()

    def on_channel_a_fall(self):
        self.sequence_a.outputs_off()

    def on_channel_b_trigger(self):
        self.sequence_b.tick()

    def on_channel_b_fall(self):
        self.sequence_b.outputs_off()

    def draw(self, utc_time):
        oled.fill(0)

        local_time = utc_time + local_timezone
        if local_time.weekday:
            oled.text(Weekday.NAME[local_time.weekday][0:3].upper(), OLED_WIDTH - CHAR_WIDTH * 3, 0, 1)

        oled.text(f"{local_time.hour:02}:{local_time.minute:02}", OLED_WIDTH - CHAR_WIDTH * 5, OLED_HEIGHT - CHAR_HEIGHT, 1)

        moon_phase = MoonPhase.calculate_phase(utc_time)
        moon_img = FrameBuffer(MoonPhase.moon_phase_images[moon_phase], 32, 32, MONO_HLSB)
        oled.blit(moon_img, 0, 0)

        mood_img = FrameBuffer(self.sequence_a.mood_graphics, 32, 32, MONO_HLSB)
        oled.blit(mood_img, 40, 0)

        oled.show()

    def run_test(self):
        self.draw(clock.utcnow())
        last_draw_at = clock.utcnow()

        fake_date = clock.utcnow()


        yesterday_moon_phase = -1
        while True:
            self.din2.update()

            self.timer_a.update_interval()
            self.timer_b.update_interval()

            self.timer_a.tick()
            self.timer_b.tick()

            local_time = clock.utcnow()

            ui_dirty = local_time.minute != last_draw_at.minute

            if ui_dirty:
                fake_date.minute = local_time.minute
                fake_date.hour = local_time.hour
                fake_date.day = fake_date.day + 1
                fake_date.weekday = fake_date.weekday + 1
                if fake_date.weekday == 8:
                    fake_date.weekday = 1
                if fake_date.day > fake_date.days_in_month:
                    fake_date.day = 1
                    fake_date.month = fake_date.month + 1

                    if fake_date.month == 13:
                        fake_date.month = 1
                        fake_date.year += 1

                self.generate_sequences(fake_date)
                self.sequence_a.state_dirty = True
                self.sequence_b.state_dirty = True

                # check that we don't have two consecutive special-phase days
                today_moon_phase = MoonPhase.calculate_phase(fake_date)
                if (
                    today_moon_phase == MoonPhase.NEW_MOON or
                    today_moon_phase == MoonPhase.FIRST_QUARTER or
                    today_moon_phase == MoonPhase.FULL_MOON or
                    today_moon_phase == MoonPhase.THIRD_QUARTER
                ):
                    if today_moon_phase == yesterday_moon_phase:
                        print(f"WARNING: two consecutive {today_moon_phase}-phases!")

                # check that the two sequences are different
                if self.sequence_a == self.sequence_b:
                    print("WARNING: identical sequences generated!")



                self.draw(fake_date)
                last_draw_at = local_time

            if self.sequence_a.state_dirty:
                self.sequence_a.set_outputs()

            if self.sequence_b.state_dirty:
                self.sequence_b.set_outputs()

    def main(self):
        self.draw(clock.utcnow())
        last_draw_at = clock.localnow()

        while True:
            self.din2.update()

            self.timer_a.update_interval()
            self.timer_b.update_interval()

            self.timer_a.tick()
            self.timer_b.tick()

            local_time = clock.localnow()

            ui_dirty = local_time.minute != last_draw_at.minute

            # if the day has rolled over, generate new sequences and mark them as dirty
            # so we'll continue playing
            if local_time.day != self.last_generation_at.day:
                self.generate_sequences(clock.utcnow())
                self.sequence_a.state_dirty = True
                self.sequence_b.state_dirty = True

                ui_dirty = True

            if self.sequence_a.state_dirty:
                self.sequence_a.set_outputs()

            if self.sequence_b.state_dirty:
                self.sequence_b.set_outputs()

            if ui_dirty:
                self.draw(clock.utcnow())
                last_draw_at = local_time


if __name__ == "__main__":
    PetRock().main()
