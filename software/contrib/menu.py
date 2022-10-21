"""See menu.md for details."""
# Reset the module state and display bootsplash screen.
from europi import bootsplash, usb_connected

#  This is a fix for a USB connection issue documented in GitHub issue #179, and its removal condition is set out in GitHub issue #184
if usb_connected.value() == 0:
    from time import sleep
    sleep(0.5)

bootsplash()

from bootloader import BootloaderMenu

from contrib.knob_playground import KnobPlayground
from contrib.bernoulli_gates import BernoulliGates
from contrib.coin_toss import CoinToss
from contrib.consequencer import Consequencer
from contrib.cvecorder import CVecorder
from contrib.diagnostic import Diagnostic
from contrib.hamlet import Hamlet
from contrib.harmonic_lfos import HarmonicLFOs
from contrib.hello_world import HelloWorld
from contrib.logic import Logic
from contrib.master_clock import MasterClock
from contrib.noddy_holder import NoddyHolder
from contrib.piconacci import Piconacci
from contrib.polyrhythmic_sequencer import PolyrhythmSeq
from contrib.poly_square import PolySquare
from contrib.probapoly import Probapoly
from contrib.quantizer import QuantizerScript
from contrib.radio_scanner import RadioScanner
from contrib.scope import Scope
from contrib.sequential_switch import SequentialSwitch
from contrib.smooth_random_voltages import SmoothRandomVoltages
from contrib.strange_attractor import StrangeAttractor
from contrib.turing_machine import EuroPiTuringMachine
from calibrate import Calibrate

# Scripts that are included in the menu
EUROPI_SCRIPT_CLASSES = [
    KnobPlayground,
    BernoulliGates,
    CoinToss,
    Consequencer,
    CVecorder,
    Diagnostic,
    Hamlet,
    HarmonicLFOs,
    HelloWorld,
    Logic,
    MasterClock,
    NoddyHolder,
    Piconacci,
    PolyrhythmSeq,
    PolySquare,
    Probapoly,
    QuantizerScript,
    RadioScanner,
    Scope,
    SequentialSwitch,
    SmoothRandomVoltages,
    StrangeAttractor,
    EuroPiTuringMachine,
    Calibrate,
]


if __name__ == "__main__":
    BootloaderMenu(EUROPI_SCRIPT_CLASSES).main()
