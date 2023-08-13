import europi
import gc
import machine
import time
import traceback

from collections import OrderedDict
from europi import (
    reset_state,
    OLED_HEIGHT,
    OLED_WIDTH,
    oled,
)
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
            print(
                f"free: {after/1024: >6.2f}k, used: {(self.before - after)/1024: >6.2f}k   {self.label}"
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

    :param scripts: a list of qualified class names of Classes implementing EuroPiScript to be included in the menu
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
            print(
                f"Warning: Ignoring bad qualified class name: {script_class_name}\n  caused by: {e}"
            )
            return None

    @classmethod
    def _is_europi_script(cls, c):
        return issubclass(c, EuroPiScript)

    @classmethod
    def show_error(self, title, message, duration=1):
        """Show a brief error message on-screen saying we can't launch the requested script

        @param title    The title of the error
        @param message  The body of the error message
        @param duration The number of seconds the message should show. If negative the message is shown forever
        """
        oled.fill(0)
        oled.centre_text(f"--{title}--\n{message}")
        oled.show()

        if duration > 0:
            time.sleep(duration)
        else:
            while True:
                time.sleep(1)

    def launch(self, selected_item):
        """Callback function for when the user chooses a menu item to launch

        Checks that the selected item is a valid EuroPiScript and then sets self.run_request to
        that class.

        If the selected item is not valid, show an error message
        """

        class_name = self.scripts[selected_item]
        clazz = self.get_class_for_name(class_name)
        if self._is_europi_script(clazz):
            self.run_request = clazz
        else:
            self.show_error("Launch Err", "Invalid script class")

    def exit_to_menu(self):
        self.remove_state()
        # Attempt to save the state of this script if it has been implemented.
        self.save_state()  # TODO: isn't this the wrong state?
        machine.reset()  # why doesn't machine.soft_reset() work anymore?

    def run_menu(self) -> type:
        self.menu = Menu(
            items=list(sorted(self.scripts.keys())),
            select_func=self.launch,
            select_knob=europi.k2,
            choice_buttons=[europi.b1, europi.b2],
        )

        # let the user make a selection
        old_selected = -1
        while not self.run_request:
            if old_selected != self.menu.selected:
                old_selected = self.menu.selected
                self.menu.draw_menu()
            time.sleep(0.1)
        return self.run_request

    def main(self):
        script_class_name = self.load_state_str()
        script_class = None

        if script_class_name:
            script_class = self.get_class_for_name(script_class_name)

        if not script_class:
            script_class = self.run_menu()
            self.save_state_str(f"{script_class.__module__}.{script_class.__name__}")
            machine.reset()
        else:
            # setup the exit handlers, and execute the selection
            europi.b1._handler_both(europi.b2, self.exit_to_menu)
            europi.b2._handler_both(europi.b1, self.exit_to_menu)

            try:
                script_class().main()
            except Exception:
                # in case we have the USB cable connected, print the stack trace for debugging
                # otherwise, just halt and show the error message
                print(f"[ERR ] Failed to run script: {err}")
                traceback.print_exc()
                self.show_error("Crash", f"Script died\n{type(err)}", -1)
