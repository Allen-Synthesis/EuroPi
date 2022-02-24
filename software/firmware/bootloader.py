from europi import *
import utime as time
from machine import reset

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


def bootloader():
    # Validate all scripts implement EuroPiScript or fail loudly.
    for script in SCRIPTS:
        if not issubclass(script, EuroPiScript):
            raise NotImplementedError(f"Script does not implement EuroPiScript: {script}")

    # Bootloader script selection.
    while True:
        cls = k1.choice(SCRIPTS)
        display_choice(cls)

        # If button 1 is pressed, execute the currently selected script.
        if b1.value() == 1 or b2.value() == 1:
            try:
                # Initialize and execute the main loop of the currently selected script.
                script = cls()
                script.main()

            finally:
                reset_state()

        time.sleep_ms(100)


if __name__ == '__main__':
    b1.handler_both(b2, reset)
    b2.handler_both(b1, reset)
    bootloader()
