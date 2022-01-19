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


# Lower read accuracy for performance
k1.set_samples(32)
k2.set_samples(32)
b2.debounce_delay = 200
oled.contrast(0)

MENU_DURATION = 1200

VOLT_PER_OCT = 1 / 12

notes = ["C", "C#", "D", "D#", "E" , "F", "F#", "G" , "G#", "A", "A#", "B"]


class SubharmoniconSeq:
    pages = ['SEQUENCE 1', 'SEQUENCE 2', 'POLYRHYTHM', 'TEMPO']
    seqs = [
        ["C", "D", "D#", "G"],
        ["G#", "F", "C", "F"],
    ]
    polys = [16, 2, 5, 9]
    seq_poly = [2, 1, 1, 1]
    # TODO we need to make Sequence a class for easy conversions.

    def __init__(self):
        self.seq = self.seqs[0]
        self.seq_index = [0, 0]

        self.last_pressed = ticks_ms()
        self.page = 0
        self.index = 0
        cv3.on()

        self.tempo = 120
        self.counter = 0

        self._prevk2 = 0

        @b1.handler
        def page_handler():
            self.last_pressed = ticks_ms()
            self.page = (self.page + 1) % len(self.pages)

            [o.off() for o in (cv3, cv6)]
            if self.page == 0:
                self.seq = self.seqs[0]
                cv3.on()
            if self.page == 1:
                self.seq = self.seqs[1]
                cv6.on()

        @b2.handler
        def edit_parameter():
            if self.page == 2:
                self.seq_poly[self.index] = (self.seq_poly[self.index] + 1) % 4

    def _pitch_cv(self, note):
        return notes.index(note) * VOLT_PER_OCT

    def show_menu_header(self):
        if ticks_diff(ticks_ms(), self.last_pressed) < MENU_DURATION:
            oled.fill_rect(0, 0, OLED_WIDTH, CHAR_HEIGHT, 1)
            oled.text(f"{self.pages[self.page]}", 0, 0, 0)

    def edit_sequence(self):
        for step in range(len(self.seq)):
            padding_x = 7 + (int(OLED_WIDTH/4) * step)
            padding_y = 12
            if step == self.index:
                choice = k2.choice(notes)
                if choice != self._prevk2:
                    self.seq[step] = choice
                    self._prevk2 = choice
            oled.text(f"{self.seq[step]:<2}", padding_x, padding_y, 1)

            # Display bar over current playing step.
            if step == self.seq_index[0 if self.page == 0 else 1]:
                x1 = (int(OLED_WIDTH/4) * step)
                oled.fill_rect(x1, 0, 32, 6, 1)

    def edit_poly(self):
        for choice in range(len(self.polys)):
            padding_x = 7 + (int(OLED_WIDTH/4) * choice)
            padding_y = 12
            if choice == self.index:
                poly = k2.range(16) + 1
                if poly != self._prevk2:
                    self.polys[choice] = poly
                    self._prevk2 = poly
            oled.text(f"{self.polys[choice]:>2}", padding_x, padding_y, 1)

            # Display for seq 1 & 2 enablement.
            status = f"{self.seq_poly[choice]:02b}"
            y1 = OLED_HEIGHT - 10

            x1 = 4 + int(OLED_WIDTH/4) * choice
            (oled.fill_rect if int(status[1]) == 1 else oled.rect)(x1, y1, 6, 6, 1)

            x1 = 12 + int(OLED_WIDTH/4) * choice
            (oled.fill_rect if int(status[0]) == 1 else oled.rect)(x1, y1, 6, 6, 1)
    
    def edit_tempo(self):
        oled.fill(0)
        self.tempo = k2.range(250) + 20
        oled.text(f"{self.tempo:>3}", 48, 12, 1)

    def play_notes(self):
        for i, poly in enumerate(self.polys):
            if self.counter % poly == 0:
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
        # TOOD: draw graphic of seq current step
        self.counter = self.counter + 1


    def main(self):
        next = 0
        while True:
            oled.fill(0)

            # Parameter edit index
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

            # Play notes on the beat
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
