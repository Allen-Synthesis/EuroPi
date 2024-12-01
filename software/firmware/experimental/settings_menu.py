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
Whenever `item_dict` is referenced in a docstring, it is a dict of the following form:
```
{
    !"item": ConfigPoint,
    ?"title": str,
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
- ! indicates required
- ? indicates optional

item: a ConfigPoint the user manipulates. Every ConfigPoint must have a unique name
title: the text displayed on screen to represent the current ConfigPoint. Default to item.name if unspecified
prefix: optional text to display to the left of the title; used to visually indicate the parent menu name
graphics: an optional array of graphics to draw beside each option
labels: an optional array of strings to use instead of the raw choices from the ConfigPoint
callback: a function to call when the user changes the value of the config point
callback_arg: an optional additional argument to pass to the callback function
children: an optional array of menu items that act as the submenu to this item, accessed by long-pressing the button

No more than 2 menu levels should ever be specified. No checks are done to prevent this, but specifying more than
2 menu levels may result in unreachable submenus.

The graphics and labels dictionaries are key/value pairs where the key corresponds to a valid option
from the ConfigPoint. FloatConfigPoint may NOT have labels or graphics, but Boolean-, Integer-, and Choice-
ConfigPoints may.

FrameBuffers for graphics must be 12x12 pixels in MONO_HLSB format. bytearrays for graphics must be able to be
sent to a FrameBuffer constructor to create the buffer described.
"""

import europi

from configuration import *
from experimental.knobs import KnobBank
from framebuf import FrameBuffer, MONO_HLSB
import time


class SettingsMenu:
    """
    A menu-based GUI for any EuroPi script.

    This class is assumed to be the main interaction method for the program.
    """

    # Treat a long press as anything more than 500ms
    LONG_PRESS_MS = 500

    def __init__(
        self,
        menu_spec,
        button=europi.b2,
        knob=europi.k2,
        short_press_cb=lambda: None,
        long_press_cb=lambda: None,
    ):
        """
        Create a new menu from the given specification

        Long/short press callbacks are invoked inside the handler for the falling edge of the button. It is recommended
        to avoid any lengthy operations inside these callbacks, as they may prevent other interrupts from being
        handled properly.

        @param menu_spec  A dict representing the structure of the menu
        @param button  The button the user presses to interact with the menu
        @param knob  The knob the user turns to scroll through the menu. This may be an experimental.knobs.KnobBank
                     with 3 menu levels called "main_menu", "submenu" and "choice", or a raw knob like europi.k2
        @param short_press_cb  An optional callback function to invoke when the user interacts with a short-press of
                               the button
        @param long_press_cb  An optional callback function to invoke when the user interacts with a long-press of
                              the button
        """
        self._knob = knob
        self.button = button

        self.short_press_cb = short_press_cb
        self.long_press_cb = long_press_cb

        self.button.handler(self.on_button_press)
        self.button.handler_falling(self.on_button_release)

        self.items = []
        for item in menu_spec:
            self.items.append(MenuItem(self, item))

        self.active_items = self.items
        self.active_item = self.knob.choice(self.items)

        self.button_down_at = time.ticks_ms()

        # Indicates to the application that we need to save the settings to disk
        self.settings_dirty = False

        self.config_points_by_name = {}
        self.menu_items_by_name = {}
        for item in self.items:
            self.config_points_by_name[item.config_point.name] = item.config_point
            self.menu_items_by_name[item.config_point.name] = item
            if item.children:
                for c in item.children:
                    self.config_points_by_name[c.config_point.name] = c.config_point
                    self.menu_items_by_name[c.config_point.name] = c

    @property
    def knob(self):
        if type(self._knob) is KnobBank:
            return self._knob.current
        else:
            return self._knob

    def get_config_points(self):
        """
        Get the config points for the menu so we can load/save them as needed
        """
        return list(self.config_points_by_name.values())

    def load_defaults(self, settings_file):
        """
        Load the initial settings from the file

        @param settings_file  The path to a JSON file where the user's settings are saved
        """
        spec = ConfigSpec(self.get_config_points())
        settings = ConfigFile.load_from_file(settings_file, spec)
        for k in settings.keys():
            self.menu_items_by_name[k].value = settings[k]

    def save(self, settings_file):
        """
        Save the current settings to the specified file
        """
        data = {}
        for item in self.menu_items_by_name.values():
            data[item.config_point.name] = item.value
        ConfigFile.save_to_file(settings_file, data)

    def on_button_press(self):
        """Handler for the rising edge of the button signal"""
        self.button_down_at = time.ticks_ms()

    def on_button_release(self):
        """Handler for the falling edge of the button signal"""
        if time.ticks_diff(time.ticks_ms(), self.button_down_at) >= self.LONG_PRESS_MS:
            self.long_press()
        else:
            self.short_press()

    def short_press(self):
        """
        Handle a short button press

        This enters edit mode, or applies the selection and
        exits edit mode
        """
        self.active_item.short_press()

        # Cycle the knob bank, if necessary
        if type(self.knob) is KnobBank:
            if self.active_item.edit_mode:
                self.knob.set_current("choice")
            elif self.active_item.children:
                self.knob.set_current("main_menu")
            else:
                self.active_item.set_current("submenu")

        self.short_press_cb()

    def long_press(self):
        """
        Handle a long button press

        This changes between the two menu levels (if possible)
        """
        # exit editable mode when we change menu levels
        self.active_item.edit_mode = False

        # we're in the top-level menu; go to the submenu if it exists
        if self.active_items == self.items:
            if self.active_item.children:
                self.active_items = self.active_item.children
                if type(self.knob) is KnobBank:
                    self.knob.set_current("submenu")
        else:
            self.active_items = self.items
            if type(self.knob) is KnobBank:
                self.knob.set_current("main_menu")

        self.long_press_cb()

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
        if not self.active_item.edit_mode:
            self.active_item = self.knob.choice(self.visible_items)
        self.active_item.draw(oled)

    @property
    def visible_items(self):
        """
        Get the set of visible menu items for the current state of the menu

        Menu items can be shown/hidden by setting their is_visible property. Normally this should be done in
        a value-change callback of a menu item to show/hide dependent other items.
        """
        items = []
        for item in self.active_items:
            if item.is_visible:
                items.append(item)
        return items


class MenuItem:
    """
    A single menu item

    The menu item is a wrapper around a ConfigPoint, and uses
    that object's values as the available selections.
    """

    def __init__(self, menu, item_dict):
        """
        Create a new menu item around a ConfigPoint

        If the item has a callback function defined, it will be invoked once during initialization

        @param menu  The SettingsMenu that owns this item
        @param item_dict  The specification for this menu item
        """
        self.menu = menu
        self.parent = None
        self.children = None

        # are we in edit mode?
        self.edit_mode = False

        # is this menu item currently visible?
        # setting this to False removes it from the menu, allowing us to show/hide menu items
        # this is managed externally, and should be handled using the callback functions
        self.is_visible = True

        # the configuration setting that we're controlling via this menu item
        self.config_point = item_dict["item"]

        self.title = item_dict.get("title", self.config_point.name)
        self.prefix = item_dict.get("prefix", "")

        if "graphics" in item_dict:
            if type(self.config_point) is FloatConfigPoint:
                raise Exception(
                    f"Cannot add graphics to {self.config_point.name}; unsupported type"
                )
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
                self.children.append(MenuItem(menu, c))
                self.children[-1].parent = self

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
            self.value = self.menu.knob.choice(self.choices)
            self.menu.settings_dirty = True

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
            display_value = self.menu.knob.choice(self.choices)
        else:
            display_value = self.value

        text_left = 0
        prefix_left = 1
        prefix_right = len(self.prefix) * europi.CHAR_WIDTH
        title_left = len(self.prefix) * europi.CHAR_WIDTH + 4

        # If we're in a top-level menu the submenu is non-empty. In that case, the prefix in inverted text
        # Otherwise, the title in inverted text to indicate we're in the sub-menu
        if self.children and len(self.children) > 0:
            oled.fill_rect(prefix_left - 1, 0, prefix_right + 1, europi.CHAR_HEIGHT + 2, 1)
            oled.text(self.prefix, prefix_left, 1, 0)
            oled.text(self.title, title_left, 1, 1)
        else:
            oled.fill_rect(
                title_left - 1,
                0,
                len(self.title) * europi.CHAR_WIDTH + 2,
                europi.CHAR_HEIGHT + 2,
                1,
            )
            oled.text(self.prefix, prefix_left, 1, 1)
            oled.text(self.title, title_left, 1, 0)

        if self.graphics:
            gfx = self.graphics.get(display_value, None)
            if gfx:
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
            text_width = len(display_text) * europi.CHAR_WIDTH

            oled.fill_rect(
                text_left,
                SELECT_OPTION_Y,
                text_left + text_width + 3,
                europi.CHAR_HEIGHT + 4,
                1,
            )
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
