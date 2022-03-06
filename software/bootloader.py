"""
Default EuroPi main entry point which loads a menu of scripts available.

Copy this file to main.py on your EuroPi pico along with menu.py to
install the menu bootloader.

When a script is selected, subsequent boots will automatically launch that 
script. To return to the bootloader menu, press both buttons.

"""
from machine import soft_reset
from europi import b1, b2, oled
import os, time

def reset_menu():
    os.remove("menu_state.py")
    soft_reset()

b1.handler_both(b2, reset_menu)
b2.handler_both(b1, reset_menu)

oled.centre_text("EuroPi Booting...")
# Provide a 3 second delay before attempting to load previous script.
time.sleep(3)


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
from menu import launch_menu
launch_menu()
