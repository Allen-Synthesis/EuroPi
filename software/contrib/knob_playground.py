from machine import ADC
from time import sleep

from europi import k1, k2, b1, b2, oled, MAX_UINT16
from europi_script import EuroPiScript
from experimental.knobs import KnobBank

"""
An example program showing the use of a KnobBank or LockableKnobs. This script is not meant to be merged into main, 
it only exists so that PR reviewers can try out a LockableKnob in physical hardware easily.
"""


class KnobPlayground(EuroPiScript):
    def __init__(self):
        super().__init__()
        self.next_k1 = False
        self.next_k2 = False

        self.kb1 = (
            KnobBank.builder(k1)
            .with_locked_knob("p1", initial_uint16_value=0, threshold_percentage=0.02)
            .with_locked_knob("p2", initial_uint16_value=MAX_UINT16 / 5)
            .with_locked_knob("p3", initial_uint16_value=MAX_UINT16 / 3)
            .build()
        )
        self.kb2 = (
            KnobBank.builder(k2)
            .with_disabled_knob()
            .with_locked_knob("p4", initial_percentage_value=0.5, threshold_from_choice_count=7)
            .with_locked_knob("p5", initial_percentage_value=1, threshold_from_choice_count=3)
            .build()
        )

        @b1.handler
        def next_knob1():
            self.next_k1 = True

        @b2.handler
        def next_knob2():
            self.next_k2 = True

    def main(self):
        choice_p4 = ["a", "b", "c", "d", "e", "f", "g"]
        choice_p5 = ["one", "two", "three"]

        while True:
            if self.next_k1:
                self.kb1.next()
                self.next_k1 = False
            if self.next_k2:
                self.kb2.next()
                self.next_k2 = False

            p1 = "X" if self.kb1.index == 0 else " "
            p2 = "*" if self.kb1.index == 1 else " "
            p3 = "*" if self.kb1.index == 2 else " "
            pd = "*" if self.kb2.index == 0 else " "
            p4 = "*" if self.kb2.index == 1 else " "
            p5 = "*" if self.kb2.index == 2 else " "
            text = (
                f"{p1} {self.kb1.p1.range(1000):4}  {pd} {k2.range()}      \n"
                + f"{p2} {int(round(self.kb1.p2.percent(), 2)*100):3}%  {p4} {self.kb2.p4.choice(choice_p4):5}\n"
                + f"{p3} {self.kb1.p3.read_position():4}  {p5} {self.kb2.p5.choice(choice_p5):5}"
            )
            oled.centre_text(text)


if __name__ == "__main__":
    KnobPlayground().main()
