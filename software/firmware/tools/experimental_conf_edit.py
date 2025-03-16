# Copyright 2024 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
A global configuration-editor menu

Used to edit the global EuroPiConfig settings -- use at your own peril!
"""

from europi import *
from europi_script import EuroPiScript

from configuration import ConfigFile

from experimental.experimental_config import *
from experimental.knobs import KnobBank
from experimental.settings_menu import *

from framebuf import FrameBuffer, MONO_HLSB


## Lockable knob bank for K2 to make menu navigation a little easier
#
#  Note that this does mean _sometimes_ you'll need to sweep the knob all the way left/right
#  to unlock it
k2_bank = (
    KnobBank.builder(k2)
    .with_unlocked_knob("main_menu")
    .with_locked_knob("submenu", initial_percentage_value=0)
    .with_locked_knob("choice", initial_percentage_value=0)
    .build()
)


class SectionHeader(MenuItem):
    def __init__(self, title, children):
        super().__init__(children=children)
        self.title = title

    def draw(self, oled):
        oled.centre_text(f"{self.title}\n\nHold B2 to edit")


class ExperimentalConfigurationEditor(EuroPiScript):
    def __init__(self):
        super().__init__()

        # fmt: off
        boolean_labels = {
            True: "Yes",
            False: "No"
        }

        quantizer_items = []
        rtc_items = []
        wifi_items = []

        config_points = ExperimentalConfig.config_points()
        for cfg in config_points:
            if type(cfg) is BooleanConfigPoint:
                labels = boolean_labels
            else:
                labels = None

            if cfg.name == "VOLTS_PER_OCTAVE":
                title = "V/Oct"
                prefix = "Quant"
                items = quantizer_items
            elif cfg.name == "ENABLE_WEBREPL":
                title = "WebREPL"
                prefix = "WiFi"
                items = wifi_items
            elif "RTC" in cfg.name or "UTC" in cfg.name:
                title = cfg.name.replace("RTC", "").replace("_", ' ').lower().strip()
                prefix = "RTC"
                items = rtc_items
            elif "WIFI" in cfg.name:
                title = cfg.name.replace("WIFI", "").replace("_", ' ').lower().strip()
                prefix = "WiFi"
                items = wifi_items

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
            menu_items=[
                # Voltage properties
                SectionHeader(
                    title="Quantizer",
                    children=quantizer_items,
                ),

                # System properties
                SectionHeader(
                    title="Realtime Clk",
                    children=rtc_items,
                ),

                # Display properties
                SectionHeader(
                    title="WiFi",
                    children=wifi_items,
                ),
            ],
            navigation_knob=k2_bank,
        )
        self.menu.load_defaults(ConfigFile.config_filename(ExperimentalConfig))
        # fmt: on

    def main(self):
        # fmt: off
        disk_icon = bytearray(b'\xff\xf0\x9f\xe8\x9f$\x9f"\x9f!\x9f\xe1\x80\x01\xbf\xfd\xa0\x05\xaf\xf5\xa0\x05\xaf\xf5\xa0\x05\xbf\xfd\x80\x01\xff\xff')
        # fmt: on

        icon_height = OLED_HEIGHT // 2 - 8
        text_height = OLED_HEIGHT // 2 - CHAR_HEIGHT // 2

        while True:
            if self.menu.ui_dirty:
                oled.fill(0)
                self.menu.draw()
                oled.show()

            if self.menu.settings_dirty:
                # visually indicate we're saving
                oled.fill(0)
                oled.blit(FrameBuffer(disk_icon, 16, 16, MONO_HLSB), 0, icon_height)
                oled.text("Saving...", 18, text_height, 1)
                oled.show()

                self.menu.save(ConfigFile.config_filename(ExperimentalConfig))
                time.sleep(0.5)

                oled.fill(0)
                self.menu.draw()
                oled.show()


if __name__ == "__main__":
    ExperimentalConfigurationEditor().main()
