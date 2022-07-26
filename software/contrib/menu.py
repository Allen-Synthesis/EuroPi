"""See menu.md for details."""
from bootloader import BootloaderMenu

from contrib.bernoulli_gates import BernoulliGates
from contrib.coin_toss import CoinToss
from contrib.consequencer import Consequencer
from contrib.cvecorder import CVecorder
from contrib.diagnostic import Diagnostic
from contrib.hamlet import Hamlet
from contrib.harmonic_lfos import HarmonicLFOs
from contrib.hello_world import HelloWorld
from contrib.noddy_holder import NoddyHolder
from contrib.polyrhythmic_sequencer import PolyrhythmSeq
from contrib.poly_square import PolySquare
from contrib.radio_scanner import RadioScanner
from contrib.scope import Scope
from contrib.strange_attractor import StrangeAttractor
from calibrate import Calibrate

# Scripts that are included in the menu
EUROPI_SCRIPT_CLASSES = [
    BernoulliGates,
    CoinToss,
    Consequencer,
    CVecorder,
    Diagnostic,
    Hamlet,
    HarmonicLFOs,
    HelloWorld,
    NoddyHolder,
    PolyrhythmSeq,
    PolySquare,
    RadioScanner,
    Scope,
    StrangeAttractor,
    Calibrate,
]


if __name__ == "__main__":
    BootloaderMenu(EUROPI_SCRIPT_CLASSES).main()
