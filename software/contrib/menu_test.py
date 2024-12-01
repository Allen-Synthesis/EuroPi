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

        # Create menu items for each CV channel
        cv_menus = []
        for i in range(6):
            menu_prefix = f"CV{i+1}"
            config_prefix = f"cv{i+1}"
            cv_menus.append(
                SettingMenuItem(
                    ChoiceConfigPoint(
                        f"{config_prefix}_mod",
                        self.CLOCK_MODS,
                        "x1"
                    ),
                    prefix = menu_prefix,
                    title = "Mod",
                    graphics = self.CLOCK_MOD_GFX,
                    children = [
                        SettingMenuItem(
                            ChoiceConfigPoint(
                                f"{config_prefix}_wave",
                                self.WAVE_SHAPES,
                                "Square"
                            ),
                            prefix = menu_prefix,
                            title = "Wave",
                            graphics = self.WAVE_SHAPE_GFX,
                        ),
                        SettingMenuItem(
                             IntegerConfigPoint(
                                f"{config_prefix}_width",
                                0,
                                100,
                                50
                            ),
                            prefix = menu_prefix,
                            title = "Width",
                        ),
                        SettingMenuItem(
                             IntegerConfigPoint(
                                f"{config_prefix}_amplitude",
                                0,
                                100,
                                50
                            ),
                            prefix = menu_prefix,
                            title = "Amplitude",
                        ),
                        SettingMenuItem(
                             IntegerConfigPoint(
                                f"{config_prefix}_phase",
                                0,
                                100,
                                50
                            ),
                            prefix = menu_prefix,
                            title = "Phase",
                        )
                    ]
                )
            )

        self.menu = SettingsMenu(
            menu_items = [
                SettingMenuItem(
                    IntegerConfigPoint(
                        "bpm",
                        1,
                        240,
                        60
                    ),
                    prefix = "Clk",
                    title = "BPM",
                    children = [
                        SettingMenuItem(
                            ChoiceConfigPoint(
                                "din_mode",
                                ["Gate", "Trigger", "Reset"],
                                "Gate"
                            ),
                            prefix = "Clk",
                            title = "DIN Mode"
                        ),
                        SettingMenuItem(
                            BooleanConfigPoint(
                                "reset_on_start",
                                True
                            ),
                            prefix = "Clk",
                            title = "Clk-Rst",
                            labels = {
                                True: "On",
                                False: "Off"
                            }
                        )
                    ]
                )
            ] + cv_menus
        )

        # Load the default values from the menu
        self.menu.load_defaults("DEBUG_MENU.json")

    def main(self):
        while True:
            oled.fill(0)
            self.menu.draw()
            oled.show()

            if self.menu.settings_dirty:
                self.menu.save("DEBUG_MENU.json")

if __name__ == "__main__":
    MenuTest().main()
