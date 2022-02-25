"""
Default EuroPi main entry point which loads a menu of scripts available.

"""
from machine import reset
from europi import b1, b2

def reset_menu():
    with open(f'previously_selected.py', 'w') as file:
        file.write(f"")
    reset()

b1.handler_both(b2, reset_menu)
b2.handler_both(b1, reset_menu)


# If a previously selected script was saved, load it and execute it.
try:
    from previously_selected import MODULE_PATH, CLASS_NAME
    module = __import__(MODULE_PATH, globals(), locals(), [CLASS_NAME])
    cls = getattr(module, CLASS_NAME)
    script = cls()
    script.main()
except ImportError:
    pass  # No previous script available, proceed to menu.

# Otherwise, launch the menu
from bootloader import launch_menu
launch_menu()
