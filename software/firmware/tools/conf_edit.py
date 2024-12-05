"""
A global configuration-editor menu

Used to edit the global EuroPiConfig settings -- use at your own peril!
"""

from europi import *
from europi_config import EuroPiConfig
from europi_script import EuroPiScript

from configuration import ConfigFile

from experimental.settings_menu import *

class ConfigurationEditor(EuroPiScript):
    def __init__(self):
        super().__init__()

        config_points = EuroPiConfig.config_points()
        menu_items = [
            SettingMenuItem(
                config_point=cfg,
                float_resolution=1
            ) for cfg in config_points
        ]

        self.menu = SettingsMenu(
            menu_items=menu_items
        )
        self.menu.load_defaults(ConfigFile.config_filename(EuroPiConfig))

    def main(self):
        while True:
            oled.fill(0)
            self.menu.draw()
            oled.show()

            if self.menu.settings_dirty:
                self.menu.save(ConfigFile.config_filename(EuroPiConfig))

if __name__ == "__main__":
    ConfigurationEditor().main()
