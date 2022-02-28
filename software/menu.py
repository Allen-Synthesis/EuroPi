from europi import *
from machine import reset
import utime as time
import os

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
    with open(f'previously_selected.py', 'w') as file:
        file.write(f"MODULE_PATH=\"{cls.__module__}\"\nCLASS_NAME=\"{cls.__name__}\"\n")

def launch_menu():

    # Validate all scripts implement EuroPiScript or fail loudly.
    # for script in SCRIPTS:
    #     if not issubclass(script, EuroPiScript):
    #         raise NotImplementedError(f"Script does not implement EuroPiScript: {script}")

    # Bootloader script selection.
    while True:
        cls = k1.choice(SCRIPTS)
        display_choice(cls)

        # If button 1 is pressed, execute the currently selected script.
        if b1.value() == 1 or b2.value() == 1:
            # Save script path to previously_selected.py.
            save_choice(cls)
            # Reset to clear memory and launch saved script.
            reset()

        time.sleep_ms(100)
