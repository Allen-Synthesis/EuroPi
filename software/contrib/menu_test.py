from europi import *
from europi_script import EuroPiScript

from configuration import *
from experimental.settings_menu import *

class MenuTest(EuroPiScript):
    CLOCK_MODS = [
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
        "x16",
        "Run",
        "Start",
        "Reset",
    ]

    WAVE_SHAPES = [
        "Square",
        "Tri",
        "Sine",
    ]

    WAVE_SHAPE_GFX = {
        "Sine": bytearray(b'\x10\x00(\x00D\x00D\x00\x82\x00\x82\x00\x82\x10\x82\x10\x01\x10\x01\x10\x00\xa0\x00@'),
        "Tri": bytearray(b'\x06\x00\x06\x00\t\x00\t\x00\x10\x80\x10\x80 @ @@ @ \x80\x10\x80\x10'),
        "Square": bytearray(b'\xfe\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x83\xf0'),
    }

    CLOCK_MOD_GFX = {
        "Run": bytearray(b'\xff\xf0\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00'),    # run gate
        "Start": bytearray(b'\xe0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xbf\xf0'),  # start trigger
        "Reset": bytearray(b'\x03\xf0\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\xfe\x00')   # reset trigger
    }

    def __init__(self):
        super().__init__()

        self.menu_spec = [
            {
                "item": IntegerConfigPoint(
                    "bpm",
                    1,
                    240,
                    60
                ),
                "title": "BPM",
                "prefix": "Clk",
                "children": [
                    {
                        "item": ChoiceConfigPoint(
                            "din_mode",
                            ["Gate", "Trigger", "Reset"],
                            "Gate"
                        ),
                        "title": "DIN Mode",
                        "prefix": "Clk"
                    },
                    {
                        "item": BooleanConfigPoint(
                            "reset_on_start",
                            True
                        ),
                        "title": "Clk-Rst",
                        "prefix": "Clk",
                        "labels": {
                            True: "On",
                            False: "Off"
                        }
                    }
                ]
            },
            {
                "item": ChoiceConfigPoint(
                    "cv1_mod",
                    self.CLOCK_MODS,
                    "x1"
                ),
                "title": "Mod",
                "prefix": "CV1",
                "graphics": self.CLOCK_MOD_GFX,
                "children": [
                    {
                        "item": ChoiceConfigPoint(
                            "cv1_wave",
                            self.WAVE_SHAPES,
                            "Square"
                        ),
                        "title": "Wave",
                        "prefix": "CV1",
                        "graphics": self.WAVE_SHAPE_GFX,
                    },
                    {
                        "item": IntegerConfigPoint(
                            "cv1_width",
                            0,
                            100,
                            50
                        ),
                        "title": "Width",
                        "prefix": "CV1",
                    },
                    {
                        "item": IntegerConfigPoint(
                            "cv1_phase",
                            0,
                            100,
                            50
                        ),
                        "title": "Phase",
                        "prefix": "CV1",
                    },
                    {
                        "item": IntegerConfigPoint(
                            "cv1_amplitude",
                            0,
                            100,
                            50
                        ),
                        "title": "Amplitude",
                        "prefix": "CV1",
                    }
                ]
            },
            {
                "item": ChoiceConfigPoint(
                    "cv2_mod",
                    self.CLOCK_MODS,
                    "x1"
                ),
                "title": "Mod",
                "prefix": "CV2",
                "graphics": self.CLOCK_MOD_GFX,
                "children": [
                    {
                        "item": ChoiceConfigPoint(
                            "cv2_wave",
                            self.WAVE_SHAPES,
                            "Square"
                        ),
                        "title": "Wave",
                        "prefix": "CV2",
                        "graphics": self.WAVE_SHAPE_GFX,
                    },
                    {
                        "item": IntegerConfigPoint(
                            "cv2_width",
                            0,
                            100,
                            50
                        ),
                        "title": "Width",
                        "prefix": "CV2",
                    },
                    {
                        "item": IntegerConfigPoint(
                            "cv2_phase",
                            0,
                            100,
                            50
                        ),
                        "title": "Phase",
                        "prefix": "CV2",
                    },
                    {
                        "item": IntegerConfigPoint(
                            "cv2_amplitude",
                            0,
                            100,
                            50
                        ),
                        "title": "Amplitude",
                        "prefix": "CV2",
                    }
                ]
            }
        ]

        self.menu = SettingsMenu(self.menu_spec)

    def main(self):
        while True:
            oled.fill(0)
            self.menu.draw()
            oled.show()

            if self.menu.settings_dirty:
                self.menu.save("DEBUG_MENU.json")
                self.menu.settings_dirty = False

if __name__ == "__main__":
    MenuTest().main()
