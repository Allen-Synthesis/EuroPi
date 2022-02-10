import machine
import os
import sys
import time
from collections import OrderedDict

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

import europi
from europi import oled, clamp, reset_state
from europi import Button
from europi import CHAR_HEIGHT, CHAR_WIDTH

SCRIPT_DIR = "/lib/contrib/"
REG_FILE_CODE = 0x8000

# Scripts that are not included in the menu
EXCLUDED_SCRIPTS = ["menu.py"]


class LongPressAndTapButton(Button):
    """A button that supports a handler for taping this button while long pressing an other."""

    def __init__(self, pin, other_button, debounce_delay=200):
        super().__init__(pin, debounce_delay)
        self.other_button = other_button
        self._short_press_falling_handler = lambda: None
        self._long_press_and_tap_falling_handler = lambda: None

    def _longpress_and_tap_falling_wrapper(self):
        if self.other_button.value() and time.ticks_diff(time.ticks_ms(), self.other_button.last_pressed()) > 300:
            return self._long_press_and_tap_falling_handler()
        return self._short_press_falling_handler()

    def handler_falling(self, func):
        # put our handler between our parent's _bounce_wrapper and the calling script's handler
        if not callable(func):
            raise ValueError("Provided handler func is not callable")
        self._short_press_falling_handler = func
        super().handler_falling(self._longpress_and_tap_falling_wrapper)

    def handler_falling_longpress_and_tap(self, func):
        if not callable(func):
            raise ValueError("Provided handler func is not callable")
        self._long_press_and_tap_falling_handler = func
        super().handler_falling(self._longpress_and_tap_falling_wrapper)


class Menu:
    """A class representing a menu displayable on the EuroPi screen. The user can navigate the menu using the buttons.

    - b1: move selection up
    - b2: move selection down
    - longpress one button and tap the other: select the item
    """

    def __init__(self, items, select_func, selected=0):
        """
        :param items: a list of the menu items
        :param select_func: the function to call when a menu selection is made
        :param selected: the index of the initial menu selection
        """
        self.items = items
        self.items.append("----- MENU -----")
        self.select_func = select_func
        self.selected = clamp(selected, 0, len(items))

        b1_pin_id = int(repr(europi.b1.pin)[4])  # TODO: make PIN constants
        b2_pin_id = int(repr(europi.b2.pin)[4])  # TODO: make PIN constants
        europi.b1 = LongPressAndTapButton(b1_pin_id, other_button=europi.b2)
        europi.b2 = LongPressAndTapButton(b2_pin_id, other_button=europi.b1)

        self.init_handlers()

    def init_handlers(self):
        @europi.b1.handler_falling
        def up():

            self.selected = self.prev()

        @europi.b2.handler_falling
        def down():
            self.selected = self.next()

        def select():
            if self.selected != len(self.items) - 1:  # ignore the '-- MENU --' item
                self.select_func(self.items[self.selected])

        europi.b1.handler_falling_longpress_and_tap(select)
        europi.b2.handler_falling_longpress_and_tap(select)

    def next(self):
        next = self.selected + 1
        if next >= len(self.items):
            next = 0
        return next

    def prev(self):
        prev = self.selected - 1
        if prev < 0:
            prev = len(self.items) - 1
        return prev

    def inverted_text(self, s, x, y):
        """displays the given text with an inverted background"""
        oled.fill_rect(x, y, CHAR_WIDTH * len(s), CHAR_HEIGHT, 1)
        oled.text(s, x, y, 0)

    def draw_menu(self):
        oled.fill(0)
        # TODO: abstract these to the oled lib
        oled.text(f"{self.items[self.prev()]}", 2, 3, 1)
        self.inverted_text(f"{self.items[self.selected]}", 2, 13)
        oled.text(f"{self.items[self.next()]}", 2, 23, 1)
        oled.show()


class BootloaderMenu(Menu):
    """A Menu which allows the user to select and execute one of the scripts available to this EuroPi. Includes the
    contents of the contrib directory as well as the calibrate script. In addition, handlers are added that allow the
    user to exit the running script by rebooting the board back to this menu. This is achieved with the 'hold one button
    and tap the other' action.
    """

    def __init__(self):
        self.scripts_config = BootloaderMenu._build_scripts_config(BootloaderMenu._get_contrib_scripts())
        super().__init__(list(self.scripts_config.keys()), self.launch)
        self.run_request = None
        self.exit_request = asyncio.Event()

    def _is_script(filestat):
        # must be a regular file whose name ends in '.py' and is not in the excluded list
        return filestat[0][-3:] == ".py" and filestat[1] == REG_FILE_CODE and filestat[0] not in EXCLUDED_SCRIPTS

    def _get_contrib_scripts():
        return [f[0] for f in os.ilistdir(SCRIPT_DIR) if BootloaderMenu._is_script(f)]

    def _build_scripts_config(scripts):
        scripts.sort()
        scripts_config = OrderedDict([(k.replace("_", " ")[:-3], f"contrib.{k[:-3]}") for k in scripts])
        scripts_config["calibrate"] = "calibrate"
        return scripts_config

    def launch(self, selected_item):
        """run the selected contrib script"""
        script_name = self.scripts_config[selected_item]
        self.run_request = script_name

    def exit_to_menu(self):
        self.exit_request.set()

    async def run(self):

        # let the user make a selection
        old_selected = -1
        while not self.run_request:
            if old_selected != self.selected:
                old_selected = self.selected
                self.draw_menu()
            await asyncio.sleep(0.1)

        # remove the menu handler, setup the exit handlers, and execute the selection
        reset_state()

        europi.b1.handler_falling_longpress_and_tap(self.exit_to_menu)
        europi.b2.handler_falling_longpress_and_tap(self.exit_to_menu)

        asyncio.create_task(self._run_script(self.run_request))

    async def _run_script(self, script_name):
        await asyncio.sleep(0.25)
        __import__(script_name)


async def main():
    # set_global_exception()  # Debug aid
    menu = BootloaderMenu()
    await menu.run()
    await menu.exit_request.wait()
    machine.soft_reset()


def set_global_exception():
    def handle_exception(loop, context):
        import sys

        sys.print_exception(context["exception"])
        sys.exit()

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


if __name__ == "__main__":
    asyncio.run(main())
