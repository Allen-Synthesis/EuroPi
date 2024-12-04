"""
Contains objects used for interactive settings menus

Menu interaction is done using a knob and a button (K2 and B2 by default):
- rotate the knob to select the menu item
- short-press to enter edit mode
- rotate knob to select an option
- short-press button to apply the new option
- long-press button to change between the 2 menu levels (if
  possible)
"""

import europi

from configuration import *
from experimental.knobs import KnobBank
from framebuf import FrameBuffer, MONO_HLSB
from machine import Timer
import time


AIN_GRAPHICS = bytearray(b'\x00\x00|\x00|\x00d\x00d\x00g\x80a\x80\xe1\xb0\xe1\xb0\x01\xf0\x00\x00\x00\x00')
KNOB_GRAPHICS = bytearray(b'\x06\x00\x19\x80 @@ @ \x80\x10\x82\x10A @\xa0 @\x19\x80\x06\x00')

AIN_LABEL = "AIN"
KNOB_LABEL = "Knob"

AUTOSELECT_AIN = "autoselect_ain"
AUTOSELECT_KNOB = "autoselect_knob"


class MenuItem:
    """
    Generic class for anything we can display in the menu
    """

    def __init__(
        self, children: list[object] = None, parent: object = None, is_visible: bool = True
    ):
        """
        Create a new abstract menu item

        @param parent  A MenuItem representing this item's parent, if this item is the bottom-level of a
                       multi-level menu
        @param children  A list of MenuItems representing this item's children, if this is the top-level of a
                         multi-level menu
        @param is_visible  Is this menu item visible by default?
        """
        self.menu = None
        self.parent = parent
        self.children = children
        self.is_visible = is_visible

        if parent and children:
            raise Exception("Cannot specify parent and children in the same menu item")

    def short_press(self):
        """Handler for when the user short-presses the button"""
        pass

    def draw(self, oled=europi.oled):
        """
        Draw the item to the screen

        @param oled   A Display-compatible object we draw to
        """
        pass

    @property
    def is_editable(self):
        return False

    @is_editable.setter
    def is_editable(self, can_edit):
        pass

    @property
    def is_visible(self):
        return self._is_visible

    @is_visible.setter
    def is_visible(self, is_visible):
        self._is_visible = is_visible


class SettingsMenu:
    """
    A menu-based GUI for any EuroPi script.

    This class is assumed to be the main interaction method for the program.
    """

    # Treat a long press as anything more than 500ms
    LONG_PRESS_MS = 500

    def __init__(
        self,
        menu_items=None,
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

        @param menu_items  A list of MenuItem objects representing the top-level of the menu
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

        self._ui_dirty = True

        self.short_press_cb = short_press_cb
        self.long_press_cb = long_press_cb

        self.button.handler(self.on_button_press)
        self.button.handler_falling(self.on_button_release)

        self.items = []
        if menu_items:
            for item in menu_items:
                self.items.append(item)

        self.active_items = self.items
        self.active_item = self.knob.choice(self.items)

        self.button_down_at = time.ticks_ms()

        # Indicates to the application that we need to save the settings to disk
        self.settings_dirty = False

        # Iterate through the menu and get all of the config points
        self.config_points_by_name = {}
        self.menu_items_by_name = {}
        for item in self.items:
            item.menu = self

            if type(item) is SettingMenuItem:
                self.config_points_by_name[item.config_point.name] = item.config_point
                self.menu_items_by_name[item.config_point.name] = item

            if item.children:
                for c in item.children:
                    c.menu = self

                    if type(c) is SettingMenuItem:
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
            self.menu_items_by_name[k].choose(settings[k])

    def save(self, settings_file):
        """
        Save the current settings to the specified file
        """
        data = {}
        for item in self.menu_items_by_name.values():
            data[item.config_point.name] = item.value_choice
        ConfigFile.save_to_file(settings_file, data)
        self.settings_dirty = False

    def on_button_press(self):
        """Handler for the rising edge of the button signal"""
        self.button_down_at = time.ticks_ms()
        self._ui_dirty = True

    def on_button_release(self):
        """Handler for the falling edge of the button signal"""
        self._ui_dirty = True
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
            if self.active_item.is_editable:
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
        self.active_item.is_editable = False

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
        if not self.active_item.is_editable:
            self.active_item = self.knob.choice(self.visible_items)
        self.active_item.draw(oled)
        self._ui_dirty = False

    @property
    def ui_dirty(self):
        """
        Is the UI currently dirty and needs re-drawing?

        This will be true if the user has pressed the button or rotated the knob sufficiently
        to change the active item
        """
        return self._ui_dirty or self.active_item != self.knob.choice(self.visible_items)

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


class SettingMenuItem(MenuItem):
    """
    A single menu item that presents a setting the user can manipulate

    The menu item is a wrapper around a ConfigPoint, and uses
    that object's values as the available selections.
    """

    def __init__(
        self,
        config_point: ConfigPoint = None,
        parent: MenuItem = None,
        children: list[MenuItem] = None,
        title: str = None,
        prefix: str = None,
        graphics: dict = None,
        labels: dict = None,
        callback=lambda new_value, old_value, config_point, arg: None,
        callback_arg=None,
        float_resolution=2,
        value_map: dict = None,
        is_visible: bool = True,
        knob_in: europi.Knob = None,
        analog_in: europi.AnalogueInput = None,
    ):
        """
        Create a new menu item around a ConfigPoint

        If the item has a callback function defined, it will be invoked once during initialization

        @param config_point  The configration option this menu item controls
        @param parent  If the menu has multiple levels, what is this item's parent control?
        @param children  If this menu has multiple levels, whar are this item's child controls?
        @param title  The title to display at the top of the display when this control is active
        @param prefix  A prefix to display before the title when this control is active
        @param graphics  A dict of values mapped to FrameBuffer or bytearray objects, representing 12x12 MONO_HLSB
                         graphics to display along with the keyed values
        @param labels  A dict of values mapped to strings, representing human-readible versions of the ConfigPoint
                       options
        @param float_resolution  The resolution of floating-point config points (ignored if config_point is not
                                 a FloatConfigPoint)
        @param value_map  An optional dict to map the underlying simple ConfigPoint values to more complex objects
                          e.g. map the string "CMaj" to a Quantizer object
        @param is_visible  Is this menu item visible by default?
        @param knob_in  If set to a Knob instance, allow the user to use a knob to automatically choose values for
                        this setting
        @param analog_in  If set to an analogue input, allow the user to automatically choose values for this
                          setting via CV control
        """
        super().__init__(parent=parent, children=children, is_visible=is_visible)

        self.timer = Timer()

        # are we in edit mode?
        self.edit_mode = False

        self.analog_in = analog_in
        self.knob_in = knob_in

        self.graphics = graphics
        self.labels = labels
        self.value_map = value_map

        # the configuration setting that we're controlling via this menu item
        # convert everything to a choice configuration; this way we can add the knob/ain options too
        if type(config_point) is FloatConfigPoint:
            self.float_resolution = float_resolution
        self.src_config = config_point
        choices = self.get_option_list()
        self.config_point = ChoiceConfigPoint(
            config_point.name,
            choices=choices,
            default=config_point.default,
        )

        self.NUM_AUTOINPUT_CHOICES = 0
        if self.analog_in or self.knob_in:
            if self.analog_in:
                self.NUM_AUTOINPUT_CHOICES += 1
            if self.knob_in:
                self.NUM_AUTOINPUT_CHOICES += 1

            if not self.graphics:
                self.graphics = {}
            self.graphics[AUTOSELECT_AIN] = AIN_GRAPHICS
            self.graphics[AUTOSELECT_KNOB] = KNOB_GRAPHICS

            if not self.labels:
                self.labels = {}
            self.labels[AUTOSELECT_AIN] = AIN_LABEL
            self.labels[AUTOSELECT_KNOB] = KNOB_LABEL

        if title:
            self.title = title
        else:
            self.title = self.config_point.name

        if prefix:
            self.prefix = prefix
        else:
            self.prefix = ""

        self.callback_fn = callback
        self.callback_arg = callback_arg

        # assign the initial value without firing any callbacks
        self._value = self.config_point.default
        self._value_choice = self.config_point.default

    def refresh_choices(self, new_default=None):
        """
        Regenerate this item's available choices

        This is needed if we externally modify e.g. the maximum/minimum values of the underlying
        config point as a result of one option needing to be within a range determined by another.

        @param new_default  A value to assign to this setting if its existing value is out-of-range
        """
        self.config_point.choices = self.get_option_list()
        still_valid = self.config_point.validate(self.value)
        if not still_valid.is_valid:
            self.choose(new_default)

    def short_press(self):
        """
        Handle a short button press

        This enters edit mode, or applies the selection and
        exits edit mode
        """
        if self.is_editable:
            new_choice = self.menu.knob.choice(self.config_point.choices)
            if new_choice != self.value_choice:
                # apply the currently-selected choice if we're in edit mode
                self.choose(new_choice)
                self.ui_dirty = True
                self.menu.settings_dirty = True

        self.is_editable = not self.is_editable

    def draw(self, oled=europi.oled):
        """
        Draw the current item to the display object

        You MUST call the display's .show() function after calling this in order to send the buffer to the display
        hardware

        @param oled  A Display instance (or compatible class) to render the item
        """
        SELECT_OPTION_Y = 16

        if self.is_editable:
            display_value = self.menu.knob.choice(self.config_point.choices)
        else:
            display_value = self.value_choice

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
            display_text = self.labels.get(display_value, str(display_value))
        else:
            display_text = str(display_value)

        if self.is_editable:
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
        t = type(self.src_config)
        if t is FloatConfigPoint:
            FLOAT_RESOLUTION = 1.0 / (10**self.float_resolution)
            items = []
            x = self.src_config.minimum
            while x <= self.src_config.maximum:
                items.append(x)
                x += FLOAT_RESOLUTION
        elif t is IntegerConfigPoint:
            items = list(range(self.src_config.minimum, self.src_config.maximum + 1))
        elif t is BooleanConfigPoint:
            items = [False, True]
        elif t is ChoiceConfigPoint:
            items = self.src_config.choices
        else:
            raise Exception(f"Unsupported ConfigPoint type: {type(self.src_config)}")

        # Add the autoselect inputs, if needed
        if self.knob_in:
            items.append(AUTOSELECT_KNOB)
        if self.analog_in:
            items.append(AUTOSELECT_AIN)

        return items

    def sample_ain(self, timer):
        """
        Read from AIN and use it to dynamically choose an item

        @param timer  The timer that fired this callback
        """
        index = int(self.analog_in.percent() * (len(self.config_point.choices) - self.NUM_AUTOINPUT_CHOICES))
        item = self.config_point.choices[index]
        if item != self._value:
            old_value = self._value
            self._value = item
            self.callback_fn(item, old_value, self.config_point, self.callback_arg)

    def sample_knob(self, timer):
        """
        Read from the secondary knob and use it to dynamically choose an item

        @param timer  The timer that fired this callback
        """
        index = int(self.knob_in.percent() * (len(self.config_point.choices) - self.NUM_AUTOINPUT_CHOICES))
        item = self.config_point.choices[index]
        if item != self._value:
            old_value = self._value
            self._value = item
            self.callback_fn(item, old_value, self.config_point, self.callback_arg)

    def choose(self, choice):
        """
        Set the raw value of this item's ConfigPoint

        @param choice  The value to assign to the ConfigPoint.

        @exception  ValueError if the given choice is not valid for this setting
        """
        # kick out early if we aren't actually choosing anything
        if choice == self.value_choice:
            return

        validation = self.config_point.validate(choice)
        if not validation.is_valid:
            raise ValueError(f"{choice} is not a valid value for {self.config_point.name}")

        if self.value_choice == AUTOSELECT_AIN or self.value_choice == AUTOSELECT_KNOB:
            self.timer.deinit()

        old_value = self._value_choice
        self._value_choice = choice

        if self._value_choice == AUTOSELECT_AIN:
            self.timer.init(freq=10, mode=Timer.PERIODIC, callback=self.sample_ain)
        elif self._value_choice == AUTOSELECT_KNOB:
            self.timer.init(freq=10, mode=Timer.PERIODIC, callback=self.sample_knob)
        else:
            self.callback_fn(choice, old_value, self.config_point, self.callback_arg)

    @property
    def value_choice(self):
        """The value the user has chosen from the menu"""
        return self._value_choice

    @property
    def value(self):
        """
        Get the raw value of this item's ConfigPoint

        You should use .mapped_value if you have assigned a value_map to the constructor
        """
        return self._value

    @property
    def mapped_value(self):
        """
        Get the value of this item mapped by the value_map

        If value_map was not set by the constructor, this property returns the same
        thing as .value
        """
        if self.value_map:
            return self.value_map[self._value]
        return self._value

    @property
    def is_editable(self):
        return self.edit_mode

    @is_editable.setter
    def is_editable(self, can_edit):
        self.edit_mode = can_edit
