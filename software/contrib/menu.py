"""See menu.md for details."""
from bootloader import BootloaderMenu

from contrib.coin_toss import CoinToss
from contrib.consequencer import Consequencer
from contrib.diagnostic import Diagnostic
from contrib.harmonic_lfos import HarmonicLFOs
from contrib.hello_world import HelloWorld
from contrib.polyrhythmic_sequencer import PolyrhythmSeq
from contrib.radio_scanner import RadioScanner
from contrib.scope import Scope
from calibrate import Calibrate

# Scripts that are included in the menu
EUROPI_SCRIPT_CLASSES = [
    CoinToss,
    Consequencer,
    Diagnostic,
    HarmonicLFOs,
    HelloWorld,
    PolyrhythmSeq,
    RadioScanner,
    Scope,
    Calibrate,
]


if __name__ == "__main__":
    BootloaderMenu(EUROPI_SCRIPT_CLASSES).main()
