"""See menu.md for details."""
# Reset the module state and display bootsplash screen.
from europi import bootsplash, usb_connected

#  This is a fix for a USB connection issue documented in GitHub issue #179, and its removal condition is set out in GitHub issue #184
if usb_connected.value() == 0:
    from time import sleep

    sleep(0.5)

bootsplash()


from bootloader import BootloaderMenu

# Scripts that are included in the menu
EUROPI_SCRIPTS = [
    "contrib.bernoulli_gates.BernoulliGates",
    "contrib.coin_toss.CoinToss",
    "contrib.consequencer.Consequencer",
    "contrib.cvecorder.CVecorder",
    "contrib.diagnostic.Diagnostic",
    "contrib.euclid.EuclideanRhythms",
    "contrib.hamlet.Hamlet",
    "contrib.harmonic_lfos.HarmonicLFOs",
    "contrib.hello_world.HelloWorld",
    "contrib.knob_playground.KnobPlayground",
    "contrib.logic.Logic",
    "contrib.master_clock.MasterClock",
    "contrib.noddy_holder.NoddyHolder",
    "contrib.piconacci.Piconacci",
    "contrib.polyrhythmic_sequencer.PolyrhythmSeq",
    "contrib.poly_square.PolySquare",
    "contrib.probapoly.Probapoly",
    "contrib.quantizer.QuantizerScript",
    "contrib.radio_scanner.RadioScanner",
    "contrib.scope.Scope",
    "contrib.sequential_switch.SequentialSwitch",
    "contrib.smooth_random_voltages.SmoothRandomVoltages",
    "contrib.strange_attractor.StrangeAttractor",
    "contrib.turing_machine.EuroPiTuringMachine",
    "calibrate.Calibrate",
]


if __name__ == "__main__":
    BootloaderMenu(EUROPI_SCRIPTS).main()
