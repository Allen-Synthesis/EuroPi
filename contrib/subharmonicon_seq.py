"""
Subharmonicon Sequencer
author: awonak
date: 2022-01-17


EuroPi version of a Subharmonicon polyrhythmic sequencer.
Partially inspired by m0wh: https://github.com/m0wh/subharmonicon-sequencer


digital_in: external clock
analog_in: unused

knob_1: cycle between inputs
knob_2: adjust value of current input

button_1: cycle through editable parameters (seq1, seq1, poly, )
button_2: edit current parameter options

output_1: pitch 1
output_2: trigger 1
output_3: (display) on when editing seq 1
output_4: pitch 2
output_5: trigger 2
output_6: (display) on when editing seq 2

"""

from europi import *
from time import sleep_ms, ticks_add, ticks_diff, ticks_ms
import machine

# Overclock the Pico for improved performance.
machine.freq(250000000)

# Configure EuroPi options to improve performance.
k1.set_samples(32)
k2.set_samples(128)
b2.debounce_delay = 200
oled.contrast(0)

MENU_DURATION = 1200

VOLT_PER_OCT = 1 / 12

NOTES = ["C", "C#", "D", "D#", "E" , "F", "F#", "G" , "G#", "A", "A#", "B"]


class SubharmoniconSeq:
    pages = ['SEQUENCE 1', 'SEQUENCE 2', 'POLYRHYTHM', 'TEMPO']
    seqs = [
        ["C", "D", "D#", "G"],
        ["G#", "F", "C", "F"],
    ]
    polys = [16, 2, 5, 9]
    seq_poly = [2, 1, 1, 1]
    #TODO we need to make function for easy conversions.

    def __init__(self):
        self.seq = self.seqs[0]
        self.seq_index = [0, 0]

        self.page = 0
        self.index = 0
        self._last_pressed = ticks_ms()
        self._prev_k2 = 0
        cv3.on()

        self.tempo = 120
        self.counter = 0

        @b1.handler
        def page_handler():
            self.page = (self.page + 1) % len(self.pages)
            self._last_pressed = ticks_ms()
            self._prev_k2 = None

            [o.off() for o in (cv3, cv6)]
            if self.page == 0:
                self.seq = self.seqs[0]
                cv3.on()
            if self.page == 1:
                self.seq = self.seqs[1]
                cv6.on()

        @b2.handler
        def edit_parameter():
            #TODO: add seq octave select for page 1 & 2
            if self.page == 2:
                self.seq_poly[self.index] = (self.seq_poly[self.index] + 1) % 4

    def _pitch_cv(self, note):
        return NOTES.index(note) * VOLT_PER_OCT

    def show_menu_header(self):
        if ticks_diff(ticks_ms(), self._last_pressed) < MENU_DURATION:
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
                oled.fill_rect(x1, 0, 32, 6, 1)

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
            #TODO we need to make function for easy conversions.
            status = f"{self.seq_poly[poly_index]:02b}"
            y1 = OLED_HEIGHT - 10

            x1 = 4 + int(OLED_WIDTH/4) * poly_index
            (oled.fill_rect if int(status[1]) == 1 else oled.rect)(x1, y1, 6, 6, 1)

            x1 = 12 + int(OLED_WIDTH/4) * poly_index
            (oled.fill_rect if int(status[0]) == 1 else oled.rect)(x1, y1, 6, 6, 1)
    
    def edit_tempo(self):
        # Clear the selected parameter index box on this page.
        oled.fill(0)
        tempo = k2.range(250) + 20
        if self._prev_k2 and self._prev_k2 != tempo:
            self.tempo = tempo
        self._prev_k2 = tempo
        oled.text(f"{self.tempo:>3}", 48, 12, 1)

    def play_notes(self):
        # For each polyrhythm, check if each sequence is enabled and if the current beat should play.
        for i, poly in enumerate(self.polys):
            if self.counter % poly == 0:
                #TODO we need to make function for easy conversions.
                status = f"{self.seq_poly[i]:02b}"
                if int(status[1]) == 1:
                    self.seq_index[0] = (self.seq_index[0] + 1) % 4
                    cv1.voltage(self._pitch_cv(self.seqs[0][self.seq_index[0]]))
                    cv2.on()
                if int(status[0]) == 1:
                    self.seq_index[1] = (self.seq_index[1] + 1) % 4
                    cv4.voltage(self._pitch_cv(self.seqs[1][self.seq_index[1]]))
                    cv5.on()
        sleep_ms(10)
        [c.off() for c in (cv2, cv5)]
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
    pass
    #reset_state()
