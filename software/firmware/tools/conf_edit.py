"""
A global configuration-editor menu

Used to edit the global EuroPiConfig settings -- use at your own peril!
"""

from europi import *
from europi_config import EuroPiConfig
from europi_script import EuroPiScript

from configuration import ConfigFile

from experimental.settings_menu import *


class SectionHeader(MenuItem):
    def __init__(self, title, children):
        super().__init__(children=children)
        self.title = title

    def draw(self, oled):
        oled.centre_text(f"{self.title}\n\nHold B2 to edit")


class ConfigurationEditor(EuroPiScript):
    def __init__(self):
        super().__init__()

        boolean_labels = {
            True: "Yes",
            False: "No"
        }

        # fmt: off
        voltage_items = []
        system_items = []
        display_items = []
        i2c_items = []

        config_points = EuroPiConfig.config_points()
        for cfg in config_points:
            if "EXTERNAL_I2C" in cfg.name:
                i2c_items.append(
                    SettingMenuItem(
                        config_point=cfg,
                        prefix="I2C",
                        title=cfg.name.replace("EXTERNAL_I2C", "").replace("_", ' ').lower().strip(),
                        float_resolution=1,
                        labels=boolean_labels
                    )
                )
            elif "DISPLAY" in cfg.name:
                display_items.append(
                    SettingMenuItem(
                        config_point=cfg,
                        prefix="Display",
                        title=cfg.name.replace("DISPLAY", "").replace("_", ' ').lower().strip(),
                        float_resolution=1,
                        labels=boolean_labels
                    )
                )
            elif "VOLTAGE" in cfg.name:
                voltage_items.append(
                    SettingMenuItem(
                        config_point=cfg,
                        prefix="Voltage",
                        title=cfg.name.replace("VOLTAGE", "").replace("_", ' ').lower().replace("input", "in").replace("output", "out").strip(),
                        float_resolution=1,
                        labels=boolean_labels
                    )
                )
            else:
                system_items.append(
                    SettingMenuItem(
                        config_point=cfg,
                        prefix="Sys",
                        title=cfg.name.replace("_", ' ').lower().strip(),
                        float_resolution=1,
                        labels=boolean_labels
                    )
                )

        self.menu = SettingsMenu(
            menu_items=[
                # Voltage properties
                SectionHeader(
                    title="Voltage",
                    children=voltage_items
                ),

                # System properties
                SectionHeader(
                    title="System",
                    children=system_items
                ),

                # Display properties
                SectionHeader(
                    title="Display",
                    children=display_items
                ),

                # External I2C properties
                SectionHeader(
                    title="I2C",
                    children=i2c_items
                ),
            ]
        )
        self.menu.load_defaults(ConfigFile.config_filename(EuroPiConfig))
        # fmt: on

    def main(self):
        while True:
            oled.fill(0)
            self.menu.draw()
            oled.show()

            if self.menu.settings_dirty:
                self.menu.save(ConfigFile.config_filename(EuroPiConfig))


if __name__ == "__main__":
    ConfigurationEditor().main()
