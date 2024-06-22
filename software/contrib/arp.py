#!/usr/bin/env python3
"""Arpeggiator & ascending/descending scale generator

Outputs ascending/descending quantized CV, with additional outputs
a perfect fifth up/down (following the circle of fifths)
"""

from europi import *
from europi_script import EuroPiScript

from experimental.quantizer import CommonScales, SEMITONE_LABELS, VOLTS_PER_OCTAVE, VOLTS_PER_SEMITONE, SEMITONES_PER_OCTAVE

import random

MODE_ASCENDING = 0
MODE_DESCENDING = 1
MODE_RANDOM = 2

class Arpeggio:
    def __init__(self, scale, mode):
        """Create an arpeggio using the notes from the given scale

        @param scale  A quantizer scales whose notes will be used
        @param mode   One of ascending, descending, or random
        """
        self.change_scale(scale)
        self.mode = mode

    def change_scale(self, scale):
        """Change the current scale

        @param scale  The new quantizer scale we want to use
        """
        self.semitones = [
            i for i in range(len(scale.notes)) if scale[i]
        ]

    def next_note(self):
        """Get the next note that should be played

        @return The semitone as an integer from 0-12
        """
        if self.mode == MODE_ASCENDING:
            semitone = self.semitones.pop(0)
            self.semitones.append(semitone)
        elif self.mode == MODE_DESCENDING:
            semitone = self.semitones.pop(-1)
            self.semitones.insert(0, semitone)
        else:
            semitone = random.choice(self.semitones)

        return semitone

    def __len__(self):
        return len(self.semitones)


class Arpeggiator(EuroPiScript):
    def __init__(self):
        super().__init__()

        ## The available scales to be played
        self.scales = [
            CommonScales.Chromatic,

            CommonScales.NatMajor,
            CommonScales.HarMajor,
            CommonScales.Major135,
            CommonScales.Major1356,
            CommonScales.Major1357,

            CommonScales.NatMinor,
            CommonScales.HarMinor,
            CommonScales.Minor135,
            CommonScales.Minor1356,
            CommonScales.Minor1357,

            CommonScales.MajorBlues,
            CommonScales.MinorBlues,

            CommonScales.WholeTone,
            CommonScales.Pentatonic,
            CommonScales.Dominant7
        ]

        ## The active scale within @self.scales
        self.current_scale_index = 0

        ## Have we received an external trigger to be processed?
        self.trigger_recvd = False

        ## Should we change the scale on the next trigger?
        self.scale_changed = False

        self.n_octaves = 1
        self.current_octave = 0
        self.root = 0
        self.root_octave = 0

        @din.handler
        def on_din():
            self.trigger_recvd = True

        @b1.handler
        def on_b1_press():
            self.current_scale_index = (self.current_scale_index - 1) % len(self.scales)
            self.scale_changed = True

        @b2.handler
        def on_b2_press():
            self.current_scale_index = (self.current_scale_index + 1) % len(self.scales)
            self.scale_changed = True

        self.load()
        self.set_scale()

    def save(self):
        state = {
            "scale": self.current_scale_index
        }
        self.save_state_json(state)

    def load(self):
        settings = self.load_state_json()
        self.current_scale_index = settings.get("scale", 0)

    def set_scale(self):
        # keep track of the number of notes we've played; once we play enough we may need to
        # go up/down an octave
        self.n_notes_played = 0

        # the current root octave for ascending arpeggios
        self.current_octave = 0

        scale = self.scales[self.current_scale_index]
        self.arps = [
            Arpeggio(scale, MODE_ASCENDING),  # ascending notes, ascending octaves
            Arpeggio(scale, MODE_ASCENDING),  # ascending notes, descending octaves
            Arpeggio(scale, MODE_RANDOM),     # random notes, ascending octaves
            Arpeggio(scale, MODE_DESCENDING), # descending notes, ascending octaves
            Arpeggio(scale, MODE_DESCENDING), # descending notes, descending octaves
            Arpeggio(scale, MODE_RANDOM)      # random notes, random octaves
        ]

    def tick(self):
        # apply the new scale in-sync with the incoming triggers so we don't get out-of-phase changes
        if self.scale_changed:
            self.scale_changed = False
            self.set_scale()

        # Increment the note & octave counter
        self.n_notes_played += 1
        if self.n_notes_played >= len(self.arps[0]):
            self.current_octave += 1
            self.n_notes_played = 0
            if self.current_octave >= self.n_octaves:
                self.current_octave = 0

        # apply the output voltages; each one is slightly unique

        # CV1: ascending arpeggio, ascending octaves
        volts = (self.root_octave + self.current_octave) * VOLTS_PER_OCTAVE + (self.root + self.arps[0].next_note()) * VOLTS_PER_SEMITONE
        cv1.voltage(volts)

        # CV2: ascending arpeggio, descending octaves
        volts = (self.root_octave + self.n_octaves - self.current_octave - 1) * VOLTS_PER_OCTAVE + (self.root + self.arps[1].next_note()) * VOLTS_PER_SEMITONE
        cv2.voltage(volts)

        # CV3: random arpeggio, ascending octaves
        volts = (self.root_octave + self.current_octave) * VOLTS_PER_OCTAVE + (self.root + self.arps[2].next_note()) * VOLTS_PER_SEMITONE
        cv3.voltage(volts)

        # CV4: descending arpeggio, ascending octaves
        volts = (self.root_octave + self.current_octave) * VOLTS_PER_OCTAVE + (self.root + self.arps[3].next_note()) * VOLTS_PER_SEMITONE
        cv4.voltage(volts)

        # CV5: descending arpeggio, descending octaves
        volts = (self.root_octave + self.n_octaves - self.current_octave - 1) * VOLTS_PER_OCTAVE + (self.root + self.arps[4].next_note()) * VOLTS_PER_SEMITONE
        cv5.voltage(volts)

        # CV6: random arpeggio, random octave
        volts = random.randint(self.root_octave, self.root_octave + self.n_octaves) * VOLTS_PER_OCTAVE + (self.root + self.arps[5].next_note()) * VOLTS_PER_SEMITONE
        cv6.voltage(volts)


    def main(self):
        while True:
            self.root_octave = int(k1.percent() * 5)
            self.n_octaves = int(k2.percent() * 5) + 1
            self.root = int(ain.read_voltage() / VOLTS_PER_SEMITONE) % SEMITONES_PER_OCTAVE

            if self.trigger_recvd:
                self.trigger_recvd = False
                self.tick()

            oled.fill(0)
            oled.centre_text(f"""{SEMITONE_LABELS[self.root]}{self.root_octave}
{self.scales[self.current_scale_index]}
{self.current_octave+1}/{self.n_octaves}""")
            oled.show()


if __name__ == "__main__":
    Arpeggiator().main()
