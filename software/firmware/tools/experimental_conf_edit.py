"""
A global configuration-editor menu

Used to edit the global EuroPiConfig settings -- use at your own peril!
"""

from europi import *
from europi_config import EuroPiConfig
from europi_script import EuroPiScript

from configuration import ConfigFile

from experimental.experimental_config import *
from experimental.settings_menu import *


class ExperimentalConfigurationEditor(EuroPiScript):
    def __init__(self):
        super().__init__()

        # fmt: off
        boolean_labels = {
            True: "Yes",
            False: "No"
        }

        items = []

        config_points = ExperimentalConfig.config_points()
        for cfg in config_points:
            if type(cfg) is BooleanConfigPoint:
                labels = boolean_labels
            else:
                labels = None

            title = cfg.name.replace("_", " ").lower().strip()
            prefix = "Ex."

            items.append(
                SettingMenuItem(
                    config_point=cfg,
                    labels=labels,
                    float_resolution=1,
                    prefix=prefix,
                    title=title,
                )
            )

        self.menu = SettingsMenu(
            menu_items=items
        )
        self.menu.load_defaults(ConfigFile.config_filename(ExperimentalConfig))
        # fmt: on

    def main(self):
        while True:
            oled.fill(0)
            self.menu.draw()
            oled.show()

            if self.menu.settings_dirty:
                self.menu.save(ConfigFile.config_filename(ExperimentalConfig))


if __name__ == "__main__":
    ExperimentalConfigurationEditor().main()
