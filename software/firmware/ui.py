from europi import CHAR_HEIGHT, CHAR_WIDTH, b1, k1, oled


class Menu:
    """A class representing a menu displayable on the EuroPi screen. The user can navigate the menu using the configured
    knob and button(s).
    """

    def __init__(self, items, select_func, select_knob=k1, choice_buttons=None):
        """
        :param items: a list of the menu items
        :param select_func: the function to call when a menu item is chosen
        :param select_knob: the knob used to select the menu item, defaults to k1
        :param choice_buttons: a List of Buttons that can be pressed to choose the selected item. defaults to b1
        """
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
        return self.select_knob.read_position(steps=len(self.items) - 1)

    def inverted_text(self, s, x, y):
        """displays the given text with an inverted background"""
        oled.fill_rect(x, y, CHAR_WIDTH * len(s), CHAR_HEIGHT, 1)
        oled.text(s, x, y, 0)

    def draw_menu(self):
        current = self.selected
        oled.fill(0)
        # TODO: abstract these to the oled lib
        oled.text(f"{self.items[current - 1]}", 2, 3, 1)
        self.inverted_text(f"{self.items[current]}", 2, 13)
        if current != len(self.items) - 2:
            # don't show the title at the bottom of the menu
            oled.text(f"{self.items[current + 1]}", 2, 23, 1)
        oled.show()


