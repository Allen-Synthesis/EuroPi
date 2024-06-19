#!/usr/bin/env python3
"""Arpeggiator & ascending/descending scale generator

Outputs ascending/descending quantized CV, with additional outputs
a perfect fifth up/down (following the circle of fifths)
"""

from europi import *
from europi_script import EuroPiScript

from experimental.quantizer import CommonScales, Intervals, SEMITONE_LABELS, VOLTS_PER_OCTAVE, VOLTS_PER_SEMITONE, SEMITONES_PER_OCTAVE

class Arpeggiator(EuroPiScript):
    def __init__(self):
        super().__init__()

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

        self.current_scale_index = 0

        self.trigger_recvd = False

        self.scale_changed = False

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

    def save(self):
        state = {
            "scale": self.current_scale_index
        }
        self.save_state_json(state)

    def main(self):
        settings = self.load_state_json()
        self.current_scale_index = settings.get("scale", 0)
        
        ascending_semitones = []
        descending_semitones = []

        self.scale_changed = True

        n_notes_played = 0
        current_octave = 0

        while True:
            scale = self.scales[self.current_scale_index]

            if self.scale_changed:
                self.save()

                ascending_semitones = [
                    i for i in range(len(scale.notes)) if scale[i]
                ]
                descending_semitones = [
                    i for i in range(len(scale.notes)) if scale[i]
                ]
                descending_semitones.reverse()
                
                self.scale_changed = False
                n_notes_played = 0
                current_octave = 0
                
            root_octave = int(k1.percent() * 5)
            n_octaves = int(k2.percent() * 5) + 1
            root = int(ain.read_voltage() / VOLTS_PER_SEMITONE) % SEMITONES_PER_OCTAVE

            if self.trigger_recvd:
                self.trigger_recvd = False
                x = ascending_semitones.pop(0)
                ascending_semitones.append(x)
                
                x = descending_semitones.pop(0)
                descending_semitones.append(x)

                n_notes_played += 1
                
                if n_notes_played >= len(ascending_semitones):
                    current_octave += 1
                    n_notes_played = 0

                    if current_octave >= n_octaves:
                        current_octave = 0

            volts = (root_octave + current_octave * VOLTS_PER_OCTAVE) + (root + ascending_semitones[0]) * VOLTS_PER_SEMITONE
            cv1.voltage(volts)

            volts = (root_octave + current_octave * VOLTS_PER_OCTAVE) + (root + ascending_semitones[0] - Intervals.P5) * VOLTS_PER_SEMITONE
            cv2.voltage(volts)

            volts = (root_octave + current_octave * VOLTS_PER_OCTAVE) + (root + ascending_semitones[0] + Intervals.P5) * VOLTS_PER_SEMITONE
            cv3.voltage(volts)

            volts = (root_octave + current_octave * VOLTS_PER_OCTAVE) + (root + descending_semitones[0]) * VOLTS_PER_SEMITONE
            cv4.voltage(volts)

            volts = (root_octave + current_octave * VOLTS_PER_OCTAVE) + (root + descending_semitones[0] - Intervals.P5) * VOLTS_PER_SEMITONE
            cv5.voltage(volts)

            volts = (root_octave + current_octave * VOLTS_PER_OCTAVE) + (root + descending_semitones[0] + Intervals.P5) * VOLTS_PER_SEMITONE
            cv6.voltage(volts)

            oled.fill(0)
            oled.centre_text(f"""{SEMITONE_LABELS[root]}{root_octave}
{scale}
{current_octave+1}/{n_octaves}""")
            oled.show()


if __name__ == "__main__":
    Arpeggiator().main()
