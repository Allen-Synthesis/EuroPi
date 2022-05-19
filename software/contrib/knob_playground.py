from machine import ADC
from time import sleep

from europi import k1, k2, b1, b2, oled
from europi_script import EuroPiScript
from experimental.knobs import KnobBank


class KnobPlayground(EuroPiScript):
    def __init__(self):
        super().__init__()
        self.kb1 = KnobBank(k1, [("p1", 1), ("p2", 1), ("p3", 1)], include_disabled=False)
        self.kb2 = KnobBank(k2, [("p4", 1), ("p5", 1)])

        b1.handler(lambda: self.kb1.next())
        b2.handler(lambda: self.kb2.next())

    def main(self):
        choice_p4 = ["a", "b", "c", "d", "e", "f", "g"]
        choice_p5 = ["one", "two", "three"]

        while True:
            p1 = "*" if self.kb1.index == 0 else " "
            p2 = "*" if self.kb1.index == 1 else " "
            p3 = "*" if self.kb1.index == 2 else " "
            pd = "*" if self.kb2.index == 0 else " "
            p4 = "*" if self.kb2.index == 1 else " "
            p5 = "*" if self.kb2.index == 2 else " "
            text = (
                f"{p1} {self.kb1.p1.range(1000):4}  {pd}      \n"
                + f"{p2} {int(round(self.kb1.p2.percent(), 2)*100):3}%  {p4} {self.kb2.p4.choice(choice_p4):5}\n"
                + f"{p3} {self.kb1.p3.read_position():4}  {p5} {self.kb2.p5.choice(choice_p5):5}"
            )
            oled.centre_text(text)


if __name__ == "__main__":
    KnobPlayground().main()
