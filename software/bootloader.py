"""
Default EuroPi main entry point which loads a menu of scripts available.

Copy this file to main.py on your EuroPi pico to install the menu bootloader.

When a script is selected, subsequent boots will automatically launch that 
script. To return to the bootloader menu, press both buttons simultaneously.

"""
from machine import reset
from europi import b1, b2
import os

def reset_menu():
    os.remove("menu_state.py")
    reset()

b1.handler_both(b2, reset_menu)
b2.handler_both(b1, reset_menu)


# If a previously selected script was saved, load it and execute it.
try:
    from menu_state import MODULE_PATH, CLASS_NAME
    module = __import__(MODULE_PATH, globals(), locals(), [CLASS_NAME])
    cls = getattr(module, CLASS_NAME)
    script = cls()
    script.main()
except ImportError:
    pass  # No previous script available, proceed to menu.

# Otherwise, launch the menu
from bootloader import launch_menu
launch_menu()
