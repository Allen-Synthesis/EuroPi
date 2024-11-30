"""
Contains objects used for interactive settings menus

Menu interaction is done using K2 and B2:
- rotate K2 to select the menu item
- short-press to enter edit mode
- rotate K2 to select an option
- short-press K2 to apply the new option
- long-press K2 to change between the 2 menu levels (if
  possible)

Menu items are specified as dictionaries for the purposes of the constructors.
Whenever `item_dict` is referenced in a docstring, it is a dict of the form:
```
{
    !"item": ConfigPoint,
    ?"prefix": str,
    ?"graphics: {key:FrameBuffer|bytearray...}
    ?"labels": {key:str...},
    ?"callback": function(new_value, old_value, config_point, arg=None),
    ?"callback_arg": Object,
    ?"children": [
        item_dict,
        item_dict,
    ]
}
```
"""

import europi
from configuration import *
from framebuf import FrameBuffer, MONO_HLSB


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
            item_dict,
            item_dict,
            ...
        ]

        The graphics and labels dictionaries are key/value pairs where the key corresponds to a valid option
        from the ConfigPoint. FloatConfigPoint may NOT have labels or graphics, but Boolean-, Integer-, and Choice-
        ConfigPoints may.

        FrameBuffers for graphics must be 12x12 pixels in MONO_HLSB format
        """
        self.items = []
        for item in menu_spec:
            self.items.append(
                MenuItem(item)
            )

        self.active_item = europi.k2.choice(self.items)

    def short_press(self):
        """
        Handle a short button press

        This enters edit mode, or applies the selection and
        exits edit mode
        """
        self.active_item.short_press()

    def long_press(self):
        """
        Handle a long button press

        This changes between the two menu levels (if possible)
        """
        if self.active_item.children:
            self.active_item = europi.k2.choice(self.active_item.children)
        elif self.active_item.parent:
            self.active_item = self.active_item.parent

    def draw(self, oled=europi.oled):
        """
        Draw the menu to the given display

        You should call the display's .fill(0) function before calling this in order to clear the screen. Otherwise
        the menu item will be drawn on top of whatever is on the screen right now. (In some cases this may be the
        desired result, but when in doubt, call oled.fill(0) first).

        You MUST call the display's .show() function after calling this in order to send the buffer to the display
        hardware

        @param oled  The display object to draw to
        """
        self.active_item = europi.k2.choice(self.visible_items)
        self.active_item.draw(oled)

    @property
    def visible_items(self):
        items = []
        if self.active_item.parent:
            # we're in a child menu
            for item in self.active_item.parent.children:
                if item.is_visible:
                    items.append(item)
        else:
            # we're at the top-level menu
            for item in self.items:
                if item.is_visible:
                    items.append(item)
        return items


class MenuItem:
    """
    A single menu item

    The menu item is a wrapper around a ConfigPoint, and uses
    that object's values as the available selections.
    """

    def __init__(self, item_dict):
        """
        Create a new menu item around a ConfigPoint

        If the item has a callback function defined, it will be invoked once during initialization

        @param item_dict  The specification for this menu item
        """
        # are we in edit mode?
        self.edit_mode = False

        # is this menu item currently visible?
        # setting this to False removes it from the menu, allowing us to show/hide menu items
        # this is managed externally, and should be handled using the callback functions
        self.is_visible = True

        # the configuration setting that we're controlling via this menu item
        self.config_point = item_dict["item"]

        self.prefix = item_dict.get("prefix", "")

        if "graphics" in item_dict:
            if type(self.config_point) is FloatConfigPoint:
                raise Exception(f"Cannot add graphics to {self.config_point.name}; unsupported type")
            self.graphics = item_dict["graphics"]
        else:
            self.graphics = None

        if "labels" in item_dict:
            if type(self.config_point) is FloatConfigPoint:
                raise Exception(f"Cannot add labels to {self.config_point.name}; unsupported type")
            self.labels = item_dict["labels"]
        else:
            self.labels = None

        if "children" in item_dict:
            self.children = []
            for c in item_dict["children"]:
                self.children.append(
                    MenuItem(c)
                )
                self.children[-1].parent = self
        else:
            self.children = None
            self.parent = None

        self.callback_fn = item_dict.get("callback", None)
        self.callback_arg = item_dict.get("callback_arg", None)

        self.choices = self.get_option_list()

        # assign the initial value
        # this will trigger the callback function once during initialization
        self._value = None
        self.value = self.config_point.default

    def short_press(self):
        """
        Handle a short button press

        This enters edit mode, or applies the selection and
        exits edit mode
        """
        if self.edit_mode:
            # apply the currently-selected choice if we're in edit mode
            self.value = k2.choice(self.choices)

        self.edit_mode = not self.edit_mode

    def draw(self, oled=europi.oled):
        """
        Draw the current item to the display object

        You MUST call the display's .show() function after calling this in order to send the buffer to the display
        hardware

        @param oled  A Display instance (or compatible class) to render the item
        """
        SELECT_OPTION_Y = 16

        if self.edit_mode:
            display_value = k2.choice(self.choices)
        else:
            display_value = self.value

        text_left = 0
        prefix_left = 1
        prefix_right = len(self.prefix) * europi.CHAR_WIDTH
        title_left = len(self.prefix) * europi.CHAR_WIDTH + 4

        # If we're in a top-level menu the submenu is non-empty. In that case, the prefix in inverted text
        # Otherwise, the title in inverted text to indicate we're in the sub-menu
        if self.children and len(self.children) != 0:
            oled.fill_rect(prefix_left-1, 0, prefix_right + 1, europi.CHAR_HEIGHT + 2, 1)
            oled.text(self.prefix, prefix_left, 1, 0)
            oled.text(self.name, title_left, 1, 1)
        else:
            oled.fill_rect(title_left-1, 0, len(self.name) * europi.CHAR_WIDTH + 2, europi.CHAR_HEIGHT + 2, 1)
            oled.text(self.prefix, prefix_left, 1, 1)
            oled.text(self.name, title_left, 1, 0)

        if self.graphics:
            gfx = self.graphics[display_value]
            text_left = 14  # graphics are 12x12, so add 2 pixel padding
            if type(gfx) is bytearray:
                gfx = FrameBuffer(gfx, 12, 12, MONO_HLSB)
            oled.blit(gfx, 0, SELECT_OPTION_Y)

        if self.labels:
            display_text = self.labels[display_value]
        else:
            display_text = str(display_value)

        if self.edit_mode:
            # draw the value in inverted text
            text_width = len(display_text)*CHAR_WIDTH

            oled.fill_rect(text_left, SELECT_OPTION_Y, text_left + text_width + 3, CHAR_HEIGHT + 4, 1)
            oled.text(display_text, text_left + 1, SELECT_OPTION_Y + 2, 0)
        else:
            # draw the selection in normal text
            oled.text(display_text, text_left + 1, SELECT_OPTION_Y + 2, 1)

    def get_option_list(self):
        """
        Get the list of options the user can choose from

        @return  A list of choices
        """
        t = type(self.config_point)
        if t is FloatConfigPoint:
            FLOAT_RESOLUTION = 0.01
            items = []
            x = self.config_point.minimum
            while x <= self.config_point.maximum:
                items.append(x)
                x += FLOAT_RESOLUTION
        elif t is IntegerConfigPoint:
            items = list(range(self.config_point.minimum, self.config_point.maximum + 1))
        elif t is BooleanConfigPoint:
            items = [False, True]
        elif t is ChoiceConfigPoint:
            items = self.config_point.choices
        else:
            raise Exception(f"Unsupported ConfigPoint type: {type(self.config_point)}")

        return items

    @property
    def name(self):
        return self.config_point.name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        validation = self.config_point.validate(v)
        if not validation.is_valid:
            raise Exception(f"{v} is not a valid value for {self.config_point.name}")

        old_value = self._value
        self._value = v
        if self.callback_fn:
            self.callback_fn(v, old_value, self.config_point, self.callback_arg)
