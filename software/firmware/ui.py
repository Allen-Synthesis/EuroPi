"""This module provides reusable UI components.
"""
from europi import CHAR_HEIGHT, CHAR_WIDTH, b1, k1, oled


class Menu:
    """A class representing a menu displayable on the EuroPi screen. The user can select a menu item using the
    configured knob and select it with the configured button(s).

    :param items: a list of the menu items
    :param select_func: the function to call when a menu item is chosen. The function will be called with single argument, the selected item.
    :param select_knob: the knob used to select the menu item, defaults to k1
    :param choice_buttons: a List of Buttons that can be pressed to choose the selected item. Defaults to b1
    """

    def __init__(self, items, select_func, select_knob=k1, choice_buttons=None):
        self.items = items
        self.items.append("----- MENU -----")
        self.select_func = select_func
        self.select_knob = select_knob
        choice_buttons = choice_buttons or [b1]

        # init handlers
        def select():
            if self.selected != len(self.items) - 1:  # ignore the '-- MENU --' item
                self.select_func(self.items[self.selected])

        for b in choice_buttons:
            b.handler_falling(select)

    @property
    def selected(self):
        """The currently selected menu item."""
        return self.select_knob.read_position(steps=len(self.items) - 1)

    def _inverted_text(self, s, x, y):
        """displays the given text with an inverted background"""
        oled.fill_rect(x, y-1, CHAR_WIDTH * len(s), CHAR_HEIGHT+2, 1)
        oled.text(s, x, y, 0)

    def draw_menu(self):
        """This function should be called by your script's main loop in order to display and refresh the menu."""
        current = self.selected
        oled.fill(0)
        oled.text(f"{self.items[current - 1]}", 2, 3, 1)
        self._inverted_text(f"{self.items[current]}", 2, 13)
        if current != len(self.items) - 2:
            # don't show the title at the bottom of the menu
            oled.text(f"{self.items[current + 1]}", 2, 23, 1)
        oled.show()
