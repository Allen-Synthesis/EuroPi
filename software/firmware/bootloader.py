import os
import time
from collections import OrderedDict

import machine

import europi
from europi import CHAR_HEIGHT, CHAR_WIDTH, Button, reset_state
from europi_script import EuroPiScript

from ui import Menu

SCRIPT_DIR = "/lib/contrib/"
REG_FILE_CODE = 0x8000


class BootloaderMenu(EuroPiScript):
    """A Menu which allows the user to select and execute one of the scripts available to this EuroPi. The menu will
    include the ``EuroPiScripts`` provided to it in the constructor. Button press handlers are added that allow the user
    to exit the script and return to the menu by holding both buttons down for a short period of time. If the module is
    restarted while a script is running it will boot right back into that same script.

    In the menu:

    * **Button 1:** choose the selected item
    * **Button 2:** choose the selected item
    * **Knob 1:** unused
    * **Knob 2:** change the current selection

    In a program that was launched from the menu:

    * Hold both buttons for at least 0.5s and release to return to the menu.

    :param script_classes: a list of Classes implementing EuroPiScript to be included in the menu
    """

    def __init__(self, script_classes):
        self.scripts_config = BootloaderMenu._build_scripts_config(script_classes)
        self.menu = Menu(
            items=list(sorted(self.scripts_config.keys())),
            select_func=self.launch,
            select_knob=europi.k2,
            choice_buttons=[europi.b1, europi.b2],
        )
        self.run_request = None

    @classmethod
    def _is_europi_script(cls, c):
        return issubclass(c, EuroPiScript)

    @staticmethod
    def _build_scripts_config(classes):
        return OrderedDict([(cls.display_name(), cls) for cls in classes if BootloaderMenu._is_europi_script(cls)])

    def launch(self, selected_item):
        self.run_request = selected_item

    def exit_to_menu(self):
        self.remove_state()
        # Attempt to save the state of this script if it has been implemented.
        self.save_state()
        machine.reset()  # why doesn't machine.soft_reset() work anymore?

    def main(self):
        state = self.load_state_str()

        if state:
            self.run_request = state

        else:

            # let the user make a selection
            old_selected = -1
            while not self.run_request:
                if old_selected != self.menu.selected:
                    old_selected = self.menu.selected
                    self.menu.draw_menu()
                time.sleep(0.1)
            self.save_state_str(self.run_request)

        # setup the exit handlers, and execute the selection
        reset_state()  # remove menu's button handlers
        europi.b1._handler_both(europi.b2, self.exit_to_menu)
        europi.b2._handler_both(europi.b1, self.exit_to_menu)

        time.sleep(0.25)
        selected_class = self.scripts_config[self.run_request]
        selected_class().main()
