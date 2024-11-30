from europi import *
from europi_script import EuroPiScript

from configuration import *
from experimental.settings_menu import *

class MenuTest(EuroPiScript):
    clock_mod = ChoiceConfigPoint(
        "Modifier",
        [
            "/16",
            "/12",
            "/8",
            "/6",
            "/5",
            "/4",
            "/3",
            "/2",
            "x1",
            "x2",
            "x3",
            "x4",
            "x5",
            "x6",
            "x7",
            "x8",
            "x12",
            "x16"
        ],
        "x1"
    )

    wave_shape = ChoiceConfigPoint(
        "Wave",
        [
            "Sine",
            "Tri",
            "Square"
        ],
        "Sine"
    )

    wave_gfx = {
        "Sine": bytearray(b'\x10\x00(\x00D\x00D\x00\x82\x00\x82\x00\x82\x10\x82\x10\x01\x10\x01\x10\x00\xa0\x00@'),
        "Tri": bytearray(b'\x06\x00\x06\x00\t\x00\t\x00\x10\x80\x10\x80 @ @@ @ \x80\x10\x80\x10'),
        "Square": bytearray(b'\xfe\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x83\xf0'),
    }


    def __init__(self):
        super().__init__()

        self.menu_spec = [
            {
                "item": self.clock_mod
            },
            {
                "item": self.wave_shape,
                "graphics": self.wave_gfx
            }
        ]

        self.menu = SettingsMenu(self.menu_spec)

    def main(self):
        while True:
            oled.fill(0)
            self.menu.draw()
            oled.show()

if __name__ == "__main__":
    MenuTest().main()
