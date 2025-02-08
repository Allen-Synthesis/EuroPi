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
"""This module provides reusable UI components.
"""

from europi import CHAR_HEIGHT, CHAR_WIDTH, OLED_HEIGHT, b1, k1, oled


class Menu:
    """A class representing a menu displayable on the EuroPi screen. The user can select a menu item using the
    configured knob and select it with the configured button(s).

    :param items: a list of the menu items
    :param select_func: the function to call when a menu item is chosen. The function will be called with single argument, the selected item.
    :param select_knob: the knob used to select the menu item, defaults to k1
    :param choice_buttons: a List of Buttons that can be pressed to choose the selected item. Defaults to b1
    """

    def __init__(self, items, select_func, select_knob=k1, choice_buttons=None):
        self.items = ["----- MENU -----"] + items
        self.select_func = select_func
        self.select_knob = select_knob
        choice_buttons = choice_buttons or [b1]

        # init handlers
        def select():
            self.select_func(self.items[self.selected + 1])

        for b in choice_buttons:
            b.handler_falling(select)

    @property
    def selected(self):
        """The currently selected menu item."""
        return self.select_knob.read_position(steps=len(self.items) - 1)

    def _inverted_text(self, s, x, y):
        """displays the given text with an inverted background"""
        oled.fill_rect(x, y - 1, CHAR_WIDTH * len(s), CHAR_HEIGHT + 2, 1)
        oled.text(s, x, y, 0)

    def draw_menu(self):
        """This function should be called by your script's main loop in order to display and refresh the menu."""
        current = self.selected
        oled.fill(0)
        line_height = CHAR_HEIGHT + 2

        for line_number, item in enumerate(self.items):
            y_position = ((line_number - current) * line_height) + 1
            if (
                y_position <= (OLED_HEIGHT - line_height) and y_position > 0
            ):  # Only draw lines which can be fully displayed
                if line_number == (current + 1):
                    self._inverted_text(f"{item}", 2, y_position)
                else:
                    oled.text(f"{item}", 2, y_position, 1)

        oled.show()
