"""
Subharmonicon Sequencer
author: awonak
date: 2022-01-17

EuroPi version of a Subharmonicon polyrhythmic sequencer.
Partially inspired by m0wh: https://github.com/m0wh/subharmonicon-sequencer
Demo video: https://youtu.be/vMAVqVQIpW0

digital_in: unused
analog_in: unused

knob_1: cycle between inputs
knob_2: adjust value of current input

button_1: cycle through editable parameters (seq1, seq1, poly, tempo)
button_2: edit current parameter options

output_1: pitch 1
output_2: trigger 1
output_3: master clock
output_4: pitch 2
output_5: trigger 2
output_6: logical XOR

"""
try:
    # Local development
    from software.firmware.europi import OLED_WIDTH, OLED_HEIGHT, CHAR_HEIGHT
    from software.firmware.europi import k1, k2, oled, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6
    from software.firmware.europi import reset_state
except ImportError:
    # Device import path
    from europi import *
from time import sleep_ms, ticks_add, ticks_diff, ticks_ms
import machine

# Overclock the Pico for improved performance.
machine.freq(250000000)

# Configure EuroPi options to improve performance.
k1.set_samples(32)
k2.set_samples(32)
b2.debounce_delay = 200
oled.contrast(0)

# Script Constants
MENU_DURATION = 1200

VOLT_PER_OCT = 1 / 12

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

MAX_TEMPO = 250
MIN_TEMPO = 20


class SubharmoniconSeq:
    pages = ['SEQUENCE 1', 'SEQUENCE 2', 'POLYRHYTHM', 'TEMPO']
    seqs = [
        ["C", "D#", "D", "G"],
        ["G", "F", "D#", "C"],
    ]
    polys = [8, 3, 2, 5]
    seq_poly = [2, 1, 1, 0]

    def __init__(self):
        self.seq = self.seqs[0]
        self.seq_index = [0, 0]

        self.page = 0
        self.index = 0
        self._prev_k2 = 0

        self.tempo = 85
        self.counter = 0

        @b1.handler
        def page_handler():
            self._prev_k2 = None
            self.page = (self.page + 1) % len(self.pages)

            if self.page == 0:
                self.seq = self.seqs[0]
            if self.page == 1:
                self.seq = self.seqs[1]

        @b2.handler
        def edit_parameter():
            # TODO: add seq octave select for page 1 & 2
            if self.page == 2:
                self.seq_poly[self.index] = (self.seq_poly[self.index] + 1) % 4

    def _pitch_cv(self, note):
        return NOTES.index(note) * VOLT_PER_OCT

    def _trigger_seq(self, step):
        # Convert poly sequence enablement into binary to determine which
        # sequences are triggered on this step.
        status = f"{self.seq_poly[step]:02b}"
        # Reverse the binary string values to match display.
        return int(status[1]) == 1, int(status[0]) == 1

    def show_menu_header(self):
        if ticks_diff(ticks_ms(), b1.last_pressed) < MENU_DURATION:
            oled.fill_rect(0, 0, OLED_WIDTH, CHAR_HEIGHT, 1)
            oled.text(f"{self.pages[self.page]}", 0, 0, 0)

    def edit_sequence(self):
        # Display each sequence step.
        for step in range(len(self.seq)):
            padding_x = 7 + (int(OLED_WIDTH/4) * step)
            padding_y = 12
            # If the current step is selected, edit with the parameter edit knob.
            if step == self.index:
                selected_note = k2.choice(NOTES)
                if self._prev_k2 and self._prev_k2 != selected_note:
                    self.seq[step] = selected_note
                self._prev_k2 = selected_note
            # Display the current step.
            oled.text(f"{self.seq[step]:<2}", padding_x, padding_y, 1)

            # Display a bar over current playing step.
            if step == self.seq_index[0 if self.page == 0 else 1]:
                x1 = (int(OLED_WIDTH/4) * step)
                x2 = int(OLED_WIDTH/4)
                oled.fill_rect(x1, 0, x2, 6, 1)

    def edit_poly(self):
        # Display each polyrhythm option.
        for poly_index in range(len(self.polys)):
            padding_x = 7 + (int(OLED_WIDTH/4) * poly_index)
            padding_y = 12
            # If the current polyrhythm is selected, edit with the parameter knob.
            if poly_index == self.index:
                poly = k2.range(16) + 1
                if self._prev_k2 and self._prev_k2 != poly:
                    self.polys[poly_index] = poly
                self._prev_k2 = poly
            # Display the current polyrhythm.
            oled.text(f"{self.polys[poly_index]:>2}", padding_x, padding_y, 1)

            # Display graphic for seq 1 & 2 enablement.
            seq1, seq2 = self._trigger_seq(poly_index)
            y1 = OLED_HEIGHT - 10

            x1 = 4 + int(OLED_WIDTH/4) * poly_index
            (oled.fill_rect if seq1 else oled.rect)(x1, y1, 6, 6, 1)

            x1 = 12 + int(OLED_WIDTH/4) * poly_index
            (oled.fill_rect if seq2 else oled.rect)(x1, y1, 6, 6, 1)

    def edit_tempo(self):
        # Clear the selected parameter index box on this page.
        oled.fill(0)
        # Add high sample rate for accurate tempo readings.
        tempo = k2.range(MAX_TEMPO, 256) + MIN_TEMPO
        if self._prev_k2 and self._prev_k2 != tempo:
            self.tempo = tempo
        self._prev_k2 = tempo
        oled.text(f"{self.tempo:>3}", 48, 12, 1)

    def play_notes(self):
        # For each polyrhythm, check if each sequence is enabled and if the
        # current beat should play.
        seq1 = False
        seq2 = False
        for i, poly in enumerate(self.polys):
            cv3.on()
            if self.counter % poly == 0:
                _seq1, _seq2 = self._trigger_seq(i)
                if _seq1 and not seq1:
                    self.seq_index[0] = (self.seq_index[0] + 1) % 4
                    cv1.voltage(self._pitch_cv(
                        self.seqs[0][self.seq_index[0]]))
                    cv2.on()
                if _seq2 and not seq2:
                    self.seq_index[1] = (self.seq_index[1] + 1) % 4
                    cv4.voltage(self._pitch_cv(
                        self.seqs[1][self.seq_index[1]]))
                    cv5.on()
                seq1 = seq1 or _seq1
                seq2 = seq2 or _seq2
        
        # Trigger logical XOR
        if (seq1 or seq2) and seq1 != seq2:
            cv6.on()
        
        sleep_ms(10)
        [c.off() for c in (cv2, cv3, cv5, cv6)]
        self.counter = self.counter + 1

    def main(self):
        next = 0
        while True:
            oled.fill(0)

            # Parameter edit index & display selected box
            self.index = k1.range(4)
            left_x = int((OLED_WIDTH/4) * self.index)
            right_x = int(OLED_WIDTH/4)
            oled.rect(left_x, 0, right_x, OLED_HEIGHT, 1)

            if self.page == 0 or self.page == 1:
                self.edit_sequence()

            if self.page == 2:
                self.edit_poly()

            if self.page == 3:
                self.edit_tempo()

            # Play notes on the beat.
            if ticks_diff(ticks_ms(), next) > 0:
                wait = int(((60 * 1000) / self.tempo) / 4)
                next = ticks_add(ticks_ms(), wait)
                self.play_notes()

            self.show_menu_header()
            oled.show()


# Main script execution
try:
    script = SubharmoniconSeq()
    script.main()
finally:
    reset_state()
