from europi import b1, b2, k1, oled
from machine import reset
import utime as time

# In order for a script to be included in the menu, it must be imported here
from contrib.coin_toss import CoinToss
from contrib.consequencer import Consequencer
from contrib.diagnostic import Diagnostic
from contrib.harmonic_lfos import HarmonicLFOs
from contrib.radio_scanner import RadioScanner
from contrib.polyrhythmic_sequencer import PolyrhythmSeq


# Load all imported scripts that subclass EuroPiScript.
SCRIPTS = [
    CoinToss,
    Consequencer,
    Diagnostic,
    HarmonicLFOs,
    RadioScanner,
    PolyrhythmSeq,
]


def display_choice(cls):
    oled.centre_text(cls.__qualname__)


def save_choice(cls):
    with open(f'menu_state.py', 'w') as file:
        file.write(f"MODULE_PATH=\"{cls.__module__}\"\nCLASS_NAME=\"{cls.__name__}\"\n")

def launch_menu():

    # Bootloader script selection.
    while True:
        cls = k1.choice(SCRIPTS)
        display_choice(cls)

        # If button 1 is pressed, execute the currently selected script.
        if b1.value() == 1 or b2.value() == 1:
            # Save script path to menu_state.py.
            save_choice(cls)
            # Reset to clear memory and launch saved script.
            reset()

        time.sleep_ms(100)
