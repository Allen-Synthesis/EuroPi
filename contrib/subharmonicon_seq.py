"""
Subharmonicon Sequencer
author: awonak
date: 2022-01-17


No internal clock, external only

digital_in: external clock
analog_in: assignable

knob_1: cycle between inputs
knob_2: adjust value of current input

button_1: cycle through editable parameters (seq1, seq1, poly, )
button_2: edit current parameter options

output_1: pitch 1
output_2: trigger 1
output_3: x
output_4: pitch 2
output_5: trigger 2
output_6: y
"""

from europi import *
from time import sleep_ms, ticks_add, ticks_diff, ticks_ms

# Lower read accuracy for performance
k1.set_samples(1)
k2.set_samples(1)


MENU_DURATION = 1200

notes = ["C", "C#", "D", "D#", "E" , "F", "F#", "G" , "G#", "A", "A#", "B"]


class SubharmoniconSeq:
    pages = ['SEQUENCE 1', 'SEQUENCE 2', 'POLYRHYTHM']
    seqs = [
        ["C", "D#", "F", "G#"],
        ["D#", "D", "C", "F"],
    ]
    polys = [16, 1, 5, 9]
    seq_poly = [
        [True, False, False, False],
        [False, True, False, False],
    ]

    def __init__(self):
        self.seq = self.seqs[0]

        self.last_pressed = ticks_ms()
        self.page = 0
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

    def show_menu_header(self):
        if ticks_diff(ticks_ms(), self.last_pressed) < MENU_DURATION:
            oled.fill_rect(0, 0, OLED_WIDTH, CHAR_HEIGHT, 1)
            oled.text(f"{self.pages[self.page]}", 0, 0, 0)
    
    def edit_sequence(self, index):
        for step in range(len(self.seq)):
            padding_x = 7 + (int(OLED_WIDTH/4) * step)
            padding_y = 12
            if step == index:
                choice = k2.choice(notes)
                if choice != self._prevk2:
                    self.seq[step] = choice
                    self._prevk2 = choice
            oled.text(f"{self.seq[step]:<2}", padding_x, padding_y, 1)
    
    def edit_poly(self, index):
        for choice in range(len(self.polys)):
            padding_x = 7 + (int(OLED_WIDTH/4) * choice)
            padding_y = 12
            if choice == index:
                poly = k2.range(16) + 1
                if poly != self._prevk2:
                    self.polys[choice] = poly
                    self._prevk2 = poly
            oled.text(f"{self.polys[choice]:>2}", padding_x, padding_y, 1)
            # oled.rect()  # TODO: b2 to enable s1 and s2
    
    def play_notes(self):
        for i, poly in enumerate(self.polys):
            if self.counter % poly == 0:
                # TODO: also set cv pitch
                if self.seq_poly[0][i]:
                    cv1.on()
                if self.seq_poly[1][i]:
                    cv4.on()
        sleep_ms(10)
        [c.off() for c in (cv1, cv4)]
        # TOOD: draw graphic of seq current step
        self.counter = self.counter + 1


    def main(self):
        next = 0
        while True:
            oled.fill(0)

            index = k1.range(4)

            left_x = int((OLED_WIDTH/4) * index)
            right_x = int(OLED_WIDTH/4)
            oled.rect(left_x, 0, right_x, OLED_HEIGHT, 1)

            if self.page == 0 or self.page == 1:
                self.edit_sequence(index)

            if self.page == 2:
                self.edit_poly(index)
            
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
    reset_state()
