"""
Contains objects used for interactive settings menus

Menu interaction is done using K2 and B2:
- rotate K2 to select the menu item
- short-press to enter edit mode
- rotate K2 to select an option
- short-press K2 to apply the new option
- long-press K2 to change between the 2 menu levels (if
  possible)
"""

from configuration import *


class SettingsMenu:
    """
    The top-level settings menu.

    Contains MenuItem instances
    """

    def __init__(self, menu_spec):
        """
        Create a new menu from the given specification

        @param menu_spec  A dict representing the structure of the menu

        Menu Specification
        - ! indicates required
        - ? indicates optional
        [
            {
                !"item": ConfigPoint,
                ?"graphics": [bytearray...],
                ?"children": [
                    {
                        "item": ConfigPoint,
                        ?"graphics": [bytearray...],
                    },
                    {
                        "item": ConfigPoint,
                        ?"graphics": [bytearray...],
                    }
                ]
            },
            ...
        ]

        bytearrays must represent a 12x12 pixel binary image
        """
        self.items = []
        for item in menu_spec:
            self.items.append(
                MenuItem(item)
            )

    def short_press(self):
        """
        Handle a short button press

        This enters edit mode, or applies the selection and
        exits edit mode
        """
        pass

    def long_press(self):
        """
        Handle a long button press

        This changes between the two menu levels (if possible)
        """
        pass


class MenuItem:
    """
    A single menu item

    The menu item is a wrapper around a ConfigPoint, and uses
    that object's values as the available selections.
    """

    def __init__(self, item_spec):
        """
        Create a new menu item around a ConfigPoint

        @param item_spec  The specification for this menu item

        Menu Item Specification:
        {
            !"item": ConfigPoint,
            ?"graphics: [bytearray...],
            ?"children": [item_spec...]
        }
        """
        # are we in edit mode?
        self.edit_mode = False

        self.config_point = item_spec["item"]
        if "graphics" in item_spec:
            self.graphics = item_spec["graphics"]
        else:
            self.graphics = None

        if "children" in item_spec:
            self.children = []
            for c in item_spec["children"]:
                self.children.append(
                    MenuItem(c)
                )
                self.children[-1].parent = self
        else:
            self.children = None

    def short_press(self):
        """
        Handle a short button press

        This enters edit mode, or applies the selection and
        exits edit mode
        """
        self.edit_mode = not self.edit_mode

    def long_press(self):
        """
        Handle a long button press

        This changes between the two menu levels (if possible)
        """
        pass

    def draw(self, oled):
        """
        Draw the current item to the display object

        @param oled  A Display instance (or compatible class) to render the item
        """
        pass
