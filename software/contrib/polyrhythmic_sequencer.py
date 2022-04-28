"""
Polyrhythmic Sequencer
author: Adam Wonak (github.com/awonak)
date: 2022-01-17
labels: polyrhythms, sequencer, triggers

EuroPi version of a Subharmonicon style polyrhythmic sequencer.
Partially inspired by m0wh: https://github.com/m0wh/subharmonicon-sequencer
Demo video: https://youtu.be/vMAVqVQIpW0

Page 1 is the first 4 note sequence, page 2 is the second 4 note sequence, page
3 is the polyrhythms assignable to each sequence. Use knob 1 to select between
the 4 steps and use knob 2 to edit that step. On page 3 there are 4 polyrhythm
options ranging from triggering every 1 beat to every 16 beats. On this page
button 2 assigns which sequence this polyrhythm should apply to. Button 1 will
cycle through the pages. The script needs a clock source in the digital input
to play.

digital_in: clock in
analog_in: unused

knob_1: select step option for current page
knob_2: adjust the value of the selected option

button_1: cycle through editable parameters (seq1, seq1, poly)
button_2: edit current parameter options

output_1: pitch 1
output_2: trigger 1
output_3: trigger logical AND
output_4: pitch 2
output_5: trigger 2
output_6: trigger logical XOR

"""
try:
    # Local development
    from software.firmware.europi import OLED_WIDTH, OLED_HEIGHT, CHAR_HEIGHT
    from software.firmware.europi import din, k1, k2, oled, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6
    from software.firmware.europi_script import EuroPiScript
except ImportError:
    # Device import path
    from europi import *
    from europi_script import EuroPiScript

from collections import namedtuple
import struct
import machine
from utime import ticks_diff, ticks_ms


# Script Constants
MENU_DURATION = 1200

VOLT_PER_OCT = 1 / 12

NOTES = [
    "C0", "C#0", "D0", "D#0", "E0", "F0", "F#0", "G0", "G#0", "A0", "A#0", "B0",
    "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
    "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
    "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3",
    "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
]


class Sequence:
    def __init__(self, notes, pitch_cv, trigger_cv):
        self.notes = notes
        self.pitch_cv = pitch_cv
        self.trigger_cv = trigger_cv
        self.step_index = 0

        # Save state struct
        self.format_string = "4s"
        self.State = namedtuple("State", "note_indexes")

    def set_state(self, state):
        """Update instance variables with given state bytestring."""
        state = self.State(*struct.unpack(self.format_string, state))
        self.notes = [NOTES[n] for n in state.note_indexes]

    def get_state(self):
        """Return state byte string."""
        note_indexes = [NOTES.index(n) for n in self.notes]
        return struct.pack(self.format_string, bytes(note_indexes))

    def _pitch_cv(self, note: str) -> float:
        return NOTES.index(note) * VOLT_PER_OCT

    def _set_pitch(self):
        pitch = self._pitch_cv(self.current_note())
        self.pitch_cv.voltage(pitch)

    def current_note(self) -> str:
        return self.notes[self.step_index]

    def edit_step(self, step: int, note: str):
        """Set the given step to the given note value and update pitch cv out."""
        assert note in NOTES, f"Given note not in available notes: {note}"
        self.notes[step] = note
        self._set_pitch()

    def advance_step(self):
        """Advance the sequence step index."""
        self.step_index = (self.step_index + 1) % len(self.notes)

    def play_next_step(self):
        """Advance the sequence step and play the note."""
        self.advance_step()
        # Set cv output voltage to sequence step pitch.
        self._set_pitch()
        self.trigger_cv.on()

    def reset(self):
        """Reset the sequence back to the first note."""
        self.step_index = 0
        self._set_pitch()
        self.trigger_cv.off()


class PolyrhythmSeq(EuroPiScript):
    pages = ['SEQUENCE 1', 'SEQUENCE 2', 'POLYRHYTHM']
    # Two 4-step melodic sequences.
    seqs = [
        Sequence(["C0", "D#0", "D0", "G0"], cv1, cv2),
        Sequence(["G0", "F0", "D#0", "C0"], cv4, cv5),
    ]
    # 4 editable polyrhythms, assignable to the sequences.
    polys = [8, 3, 2, 5]
    # Indicates which sequences are assigned to each polyrhythm.
    # 0: none, 1: seq1, 2: seq2, 3: both seq1 and seq2.
    seq_poly = [2, 1, 1, 0]

    # Used to indicates if state has changed and not yet saved.
    _dirty = False
    _last_saved = 0

    def __init__(self):
        super().__init__()
        # Overclock the Pico for improved performance.
        machine.freq(250000000)

        # Configure EuroPi options to improve performance.
        b2.debounce_delay = 200
        oled.contrast(0)  # dim the oled

        # Current editable sequence.
        self.seq = self.seqs[0]

        self.page = 0
        self.param_index = 0
        self.counter = 0
        self.reset_timeout = 3000
        self._prev_k2 = None

        # Assign cv outputs to logical triggers.
        self.trigger_and = cv3
        self.trigger_xor = cv6

        # Save state struct
        self.format_string = "12s12s4s4s"
        self.State = namedtuple("State", "seq1 seq2 polys seq_poly")

        # Load state if previous state exists.
        self.load_state()

        @b1.handler
        def page_handler():
            # Pressing button 1 cycles through the pages of editable parameters.
            self._prev_k2 = None
            self.page = (self.page + 1) % len(self.pages)
            if self.page == 0:
                self.seq = self.seqs[0]
            if self.page == 1:
                self.seq = self.seqs[1]
            self._dirty = True

        @b2.handler
        def edit_parameter():
            # Pressing button 2 edits the current selected parameter.
            if self.page == 2:
                # Cycles through which sequence this polyrhythm is assigned to.
                self.seq_poly[self.param_index] = (
                    self.seq_poly[self.param_index] + 1) % len(self.seq_poly)
                self._dirty = True

        @din.handler
        def play_notes():
            # For each polyrhythm, check if each sequence is enabled and if the
            # current beat should play.
            seq1 = False
            seq2 = False
            # Check each polyrhythm to determine if a sequence should be triggered.
            for i, poly in enumerate(self.polys):
                if self.counter % poly == 0:
                    _seq1, _seq2 = self._trigger_seq(i)
                    seq1 = _seq1 or seq1
                    seq2 = _seq2 or seq2
            if seq1:
                self.seqs[0].play_next_step()
            if seq2:
                self.seqs[1].play_next_step()

            # Trigger logical AND / XOR
            if seq1 and seq2:
                self.trigger_and.on()
            if (seq1 or seq2) and seq1 != seq2:
                self.trigger_xor.on()

            self.counter = self.counter + 1

        @din.handler_falling
        def triggers_off():
            # Turn off all of the trigger CV outputs.
            [seq.trigger_cv.off() for seq in self.seqs]
            self.trigger_and.off()
            self.trigger_xor.off()

    def _trigger_seq(self, step: int):
        # Convert poly sequence enablement into binary to determine which
        # sequences are triggered on this step.
        status = f"{self.seq_poly[step]:02b}"
        # Reverse the binary string values to match display.
        return int(status[1]) == 1, int(status[0]) == 1

    def load_state(self):
        """Load state from previous run."""
        state = self.load_state_bytes()
        if state:
            self.set_state(state)

    def save_state(self):
        """Save state if it has changed since last call."""
        # Only save state if state has changed and more than 1s has elapsed
        # since last save.
        if self._dirty and self.last_saved() > 1000:
            state = self.get_state()
            self.save_state_bytes(state)
            self._dirty = False
            self._last_saved = ticks_ms()

    def get_state(self):
        """Get state as a byte string."""
        return struct.pack(self.format_string,
                           self.seqs[0].get_state(),
                           self.seqs[1].get_state(),
                           bytes(self.polys),
                           bytes(self.seq_poly))

    def set_state(self, state):
        """Update instance variables with given state bytestring."""
        try:
            _state = self.State(*struct.unpack(self.format_string, state))
        except ValueError as e:
            print(f"Unable to load state: {e}")
            return
        self.seqs[0].set_state(_state.seq1)
        self.seqs[1].set_state(_state.seq2)
        self.polys = list(_state.polys)
        self.seq_poly = list(_state.seq_poly)
    
    def reset_check(self):
        """Reset the sequences and triggers when no clock pulse detected for specified time."""
        if self.counter != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.reset_timeout:
            self.step = 0
            self.counter = 0
            [s.reset() for s in self.seqs]
            self.trigger_and.off()
            self.trigger_xor.off()

    def show_menu_header(self):
        if ticks_diff(ticks_ms(), b1.last_pressed()) < MENU_DURATION:
            oled.fill_rect(0, 0, OLED_WIDTH, CHAR_HEIGHT, 1)
            oled.text(f"{self.pages[self.page]}", 0, 0, 0)

    def edit_sequence(self):
        # Display each sequence step.
        for step in range(len(self.seq.notes)):
            # If the current step is selected, edit with the parameter edit knob.
            if step == self.param_index:
                selected_note = k2.choice(NOTES)
                if self._prev_k2 and self._prev_k2 != selected_note:
                    self.seq.edit_step(step, selected_note)
                    self._dirty = True
                self._prev_k2 = selected_note

            # Display the current step.
            padding_x = 4 + (int(OLED_WIDTH/4) * step)
            padding_y = 12
            oled.text(f"{self.seq.notes[step]:<3}", padding_x, padding_y, 1)

            # Display a bar under current playing step.
            if step == self.seq.step_index:
                x1 = (int(OLED_WIDTH / 4) * step)
                x2 = int(OLED_WIDTH / 4)
                oled.fill_rect(x1, OLED_HEIGHT - 6, x2, OLED_HEIGHT, 1)

    def edit_poly(self):
        # Display each polyrhythm option.
        for poly_index in range(len(self.polys)):
            # If the current polyrhythm is selected, edit with the parameter knob.
            if poly_index == self.param_index:
                poly = k2.range(16) + 1
                if self._prev_k2 and self._prev_k2 != poly:
                    self.polys[poly_index] = poly
                    self._dirty = True
                self._prev_k2 = poly

            # Display the current polyrhythm.
            padding_x = 8 + (int(OLED_WIDTH/4) * poly_index)
            padding_y = 12
            oled.text(f"{self.polys[poly_index]:>2}", padding_x, padding_y, 1)

            # Display graphic for seq 1 & 2 enablement.
            seq1, seq2 = self._trigger_seq(poly_index)
            y1 = OLED_HEIGHT - 10

            x1 = 9 + int(OLED_WIDTH/4) * poly_index
            (oled.fill_rect if seq1 else oled.rect)(x1, y1, 6, 6, 1)

            x1 = 17 + int(OLED_WIDTH/4) * poly_index
            (oled.fill_rect if seq2 else oled.rect)(x1, y1, 6, 6, 1)

    def main(self):
        while True:
            oled.fill(0)

            # Parameter edit index & display selected box
            self.param_index = k1.range(4)
            left_x = int((OLED_WIDTH/4) * self.param_index)
            right_x = int(OLED_WIDTH/4)
            oled.rect(left_x, 0, right_x, OLED_HEIGHT, 1)

            if self.page == 0 or self.page == 1:
                self.edit_sequence()

            if self.page == 2:
                self.edit_poly()
            
            self.reset_check()

            self.show_menu_header()
            oled.show()

            self.save_state()


# Main script execution
if __name__ == '__main__':
    script = PolyrhythmSeq()
    script.main()
