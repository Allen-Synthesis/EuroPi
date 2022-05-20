from europi import *
import machine
from europi_script import EuroPiScript

NOTES = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B",
}


class Mode:
    def __init__(self, name, intervals):
        self.intervals = intervals
        self.name = name

    def get_notes(self, root):
        notes = []
        for interval in self.intervals:
            notes.append((root + interval) % 12)
        return notes


class MoltQuantizer(EuroPiScript):
    def __init__(self):
        # Settings for improved performance.
        machine.freq(250_000_000)
        k1.set_samples(32)
        k2.set_samples(32)
        self.modes = [
            Mode("Mode 1", (0, 2, 4, 6, 8, 10)),
            Mode("Mode 2", (0, 1, 3, 4, 6, 7, 9, 10)),
            Mode("Mode 3", (0, 2, 3, 4, 6, 7, 8, 10, 11)),
            Mode("Mode 4", (0, 1, 2, 5, 6, 7, 8, 11)),
            Mode("Mode 5", (0, 1, 5, 6, 7, 11)),
            Mode("Mode 6", (0, 2, 4, 5, 6, 8, 10, 11)),
            Mode("Mode 7", (0, 1, 2, 3, 5, 6, 7, 8, 9, 11)),
            Mode("Major", (0, 2, 4, 5, 7, 9, 11)),
            Mode("Melodic minor", (0, 2, 3, 5, 7, 9, 11)),
            Mode("Major penta.", (0, 2, 4, 7, 9)),
            Mode("Minor penta.", (0, 2, 3, 7, 9)),
            Mode("Chromatic", (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)),
        ]
        self.current_mode = None
        self.root = 0
        self.voice_spread = 0
        self.ui_update_requested = False
        self.update_root_amount = 0
        self.current_pitch = None
        self.current_pitch_bias = 0.025
        self.load_state()
        self.update_settings()

        @b1.handler
        def decrement_root():
            self.update_root_amount -= 1

        @b2.handler
        def increment_root():
            self.update_root_amount += 1

    @classmethod
    def display_name(cls):
        return "MOLT quantizer"

    def get_quantized_pitch(self, input_pitch, pitches, scale_step_offset):
        return pitches[
            clamp(
                min(range(len(pitches)), key=lambda i: abs(pitches[i] - input_pitch))
                + scale_step_offset,
                0,
                len(pitches) - 1,
            )
        ]

    def get_pitches(self, notes):
        pitches = []
        for octave in range(10):
            for note in notes:
                pitches.append(octave + (note / 12))
        return sorted(pitches)

    def get_pitch(self, root, interval):
        return root + interval

    def get_note_name(self, note):
        return NOTES[note]

    def update_ui(self):
        if self.ui_update_requested:
            oled.centre_text(
                "root: "
                + self.get_note_name(self.root)
                + "\nspread: "
                + str(self.voice_spread)
                + "\n"
                + self.modes[self.current_mode].name
            )
            self.ui_update_requested = False

    def save_state(self):
        settings = {"r": self.root}
        self.save_state_json(settings)

    def load_state(self):
        settings = self.load_state_json()
        if "r" in settings:
            self.root = settings["r"]

    def update_root(self, steps):
        self.root = (self.root + steps) % 12
        self.current_pitch = None
        self.update_root_amount = 0
        self.save_state()

    def update_settings(self):
        if not self.update_root_amount == 0:
            self.update_root(self.update_root_amount)
            self.ui_update_requested = True
        new_voice_spread = k1.read_position(10)
        new_mode = k2.read_position(len(self.modes))
        if not (
            new_voice_spread == self.voice_spread and new_mode == self.current_mode
        ):
            self.voice_spread = k1.read_position(10)
            self.current_mode = k2.read_position(len(self.modes))
            self.current_pitch = None
            self.ui_update_requested = True

    def get_midpoint_distance(self, value, other_value):
        return abs(value - other_value) / 2

    def get_is_new_pitch(self, old_pitch, new_pitch, pitches, current_pitch_bias):
        if old_pitch == None:
            return True
        pitch_index = pitches.index(old_pitch)
        return (
            old_pitch <= min(pitches)
            or old_pitch >= max(pitches)
            or new_pitch
            < old_pitch
            - (
                self.get_midpoint_distance(old_pitch, pitches[(pitch_index - 1)])
                + current_pitch_bias
            )
            or new_pitch
            > old_pitch
            + (
                self.get_midpoint_distance(old_pitch, pitches[(pitch_index + 1)])
                + current_pitch_bias
            )
        )

    def play(self):
        notes = self.modes[self.current_mode].get_notes(self.root)
        input_pitch = ain.read_voltage(32)
        pitches = self.get_pitches(notes)
        if self.get_is_new_pitch(
            self.current_pitch, input_pitch, pitches, self.current_pitch_bias
        ):
            i = 0
            for cv in cvs:
                quantized_pitch = self.get_quantized_pitch(
                    input_pitch, pitches, self.voice_spread * i
                )
                cv.voltage(quantized_pitch)
                if i == 0:
                    self.current_pitch = quantized_pitch
                i += 1

    def main(self):
        while True:
            self.update_ui()
            self.play()
            self.update_settings()


# Main script execution
if __name__ == "__main__":
    MoltQuantizer().main()
