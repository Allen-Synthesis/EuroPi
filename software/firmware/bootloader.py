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
import europi
import gc
import machine
import sys
import time

from collections import OrderedDict
from europi import oled, OLED_HEIGHT, OLED_WIDTH, CHAR_HEIGHT, CHAR_WIDTH, reset_state
from europi_log import *
from europi_script import EuroPiScript
from ui import Menu

SCRIPT_DIR = "/lib/contrib/"
REG_FILE_CODE = 0x8000
DEBUG = False


class PrintMemoryUse:
    def __init__(self, label=""):
        self.label = label

    def __enter__(self):
        gc.collect()  # Note that preemptive GC is required to get all of the scripts loaded
        if DEBUG:
            self.before = gc.mem_free()

    def __exit__(self, *args):
        if DEBUG:
            gc.collect()
            after = gc.mem_free()
            log_info(
                f"free: {after/1024: >6.2f}k, used: {(self.before - after)/1024: >6.2f}k   {self.label}",
                "bootloader",
            )


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
    """

    def __init__(self, scripts):
        """Create the bootloader menu

        @param scripts  Dictionary where the keys are the display names of the classes to include in the menu and the
                        values are the fully-qualified names of the EuroPiScript classes that we launch
        """
        self.scripts = scripts
        self.run_request = None

    @staticmethod
    def show_progress(percentage):
        oled.hline(0, OLED_HEIGHT - 1, int(OLED_WIDTH * percentage), 1)
        oled.show()

    @staticmethod
    def get_class_for_name(script_class_name) -> type:
        try:
            module, clazz = script_class_name.rsplit(".", 1)
            return getattr(__import__(module, None, None, [None]), clazz)
        except Exception as e:
            log_warning(
                f"Warning: Ignoring bad qualified class name: {script_class_name}\n  caused by: {e}",
                "bootloader",
            )
            return None

    @classmethod
    def _is_europi_script(cls, c):
        return issubclass(c, EuroPiScript)

    @classmethod
    def show_error(cls, title, message, duration=1):
        """Show a brief error message on-screen saying we can't launch the requested script

        @param title    The title of the error
        @param message  The body of the error message
        @param duration The number of seconds the message should show. If negative the message is shown forever
        """
        oled.centre_text(f"--{title}--\n{message}")

        if duration > 0:
            time.sleep(duration)

    def launch(self, selected_item):
        """Callback function for when the user chooses a menu item to launch

        Sets run_request to the name of the class to launch.  No validation is done here to keep this
        callback small
        """
        self.run_request = self.scripts[selected_item]

    def exit_to_menu(self):
        self.remove_state()
        # Attempt to save the state of this script if it has been implemented.
        self.save_state()  # TODO: isn't this the wrong state?
        machine.reset()  # why doesn't machine.soft_reset() work anymore?

    def run_menu(self) -> type:
        """Prompt the user to select a EuroPiScript class from the menu and return it

        If the class is not a valid EuroPiScript an error message is shown and selection continues

        @return The type corresponding to self.run_request as set by the self.launch callback
        """
        self.menu = Menu(
            items=list(sorted(self.scripts.keys())),
            select_func=self.launch,
            select_knob=europi.k2,
            choice_buttons=[europi.b1, europi.b2],
        )

        # let the user make a selection
        # the menu selection returns the desired class name but doesn't validate it
        # that validation is handled here
        launch_class = None
        old_selected = -1
        while launch_class is None:
            if self.run_request:
                launch_class = self.get_class_for_name(self.run_request)
                if not self._is_europi_script(launch_class):
                    self.show_error("Launch Err", "Invalid script class")
                    launch_class = None
                    self.run_request = None
            else:
                if old_selected != self.menu.selected:
                    old_selected = self.menu.selected
                    self.menu.draw_menu()
                time.sleep(0.1)

        return launch_class

    def main(self):
        saved_state = self.load_state_json()
        script_class_name = saved_state.get("last_launched", None)
        script_class = None

        if script_class_name:
            script_class = self.get_class_for_name(script_class_name)

        if not script_class:
            script_class = self.run_menu()
            self.save_state_json(
                {"last_launched": f"{script_class.__module__}.{script_class.__name__}"}
            )
            machine.reset()
        else:
            # setup the exit handlers, and execute the selection
            europi.b1._handler_both(europi.b2, self.exit_to_menu)
            europi.b2._handler_both(europi.b1, self.exit_to_menu)

            try:
                if (
                    europi.europi_config.MENU_AFTER_POWER_ON
                    or script_class_name == "calibrate.Calibrate"
                ):
                    # Remove the last-launched file to force the module back to the menu after it powers-on next time
                    self.save_state_json({})

                script_class().main()
            except Exception as err:
                # set all outputs to zero for safety
                europi.turn_off_all_cvs()

                # in case we have the USB cable connected, print the stack trace for debugging
                # otherwise, just halt and show the error message
                log_error(f"Failed to run script: {err}", "bootloader")
                sys.print_exception(err)

                # show the type & first portion of the exception on the OLED
                # we can only fit so many characters, so truncate as needed
                MAX_CHARS = OLED_WIDTH // CHAR_WIDTH
                self.show_error(
                    "Crash", f"{err.__class__.__name__[0:MAX_CHARS]}\n{str(err)[0:MAX_CHARS]}", -1
                )

                # Log the crash to a file for later analysis/recovery
                try:
                    with open("last_crash.log", "w") as log_file:
                        log_file.write(f"{time.ticks_ms()}: {err}\n")
                        sys.print_exception(err, log_file)

                    log_error(f"Crash! See last_crash.txt for details: {err}", "bootloader")
                except:
                    # If we fail to create the error log, just silently fail; we don't need
                    # an additional exception to handle
                    pass
