"""See menu.md for details."""
# Reset the module state and display bootsplash screen.
from europi import bootsplash, usb_connected

#  This is a fix for a USB connection issue documented in GitHub issue #179, and its removal condition is set out in GitHub issue #184
if usb_connected.value() == 0:
    from time import sleep

    sleep(0.5)

bootsplash()


from bootloader import BootloaderMenu
from collections import OrderedDict

# Scripts that are included in the menu
EUROPI_SCRIPTS = OrderedDict([
    ["Bernoulli Gates", "contrib.bernoulli_gates.BernoulliGates"],
    ["Coin Toss", "contrib.coin_toss.CoinToss"],
    ["Consequencer", "contrib.consequencer.Consequencer"],
    ["CVecorder", "contrib.cvecorder.CVecorder"],
    ["Diagnostic", "contrib.diagnostic.Diagnostic"],
    ["EnvelopeGen", "contrib.envelope_generator.EnvelopeGenerator"],
    ["Euclid", "contrib.euclid.EuclideanRhythms"],
    ["Hamlet", "contrib.hamlet.Hamlet"],
    ["HarminicLFO", "contrib.harmonic_lfos.HarmonicLFOs"],
    ["HelloWorld", "contrib.hello_world.HelloWorld"],
    ["KnobPlayground", "contrib.knob_playground.KnobPlayground"],
    ["Kompari", "contrib.kompari.Kompari"],
    ["Logic", "contrib.logic.Logic"],
    ["MasterClock", "contrib.master_clock.MasterClock"],
    ["NoddyHolder", "contrib.noddy_holder.NoddyHolder"],
    ["Pam's Workout", "contrib.pams.PamsWorkout"],
    ["Piconacci", "contrib.piconacci.Piconacci"],
    ["PolyrhythmSeq", "contrib.polyrhythmic_sequencer.PolyrhythmSeq"],
    ["PolySquare", "contrib.poly_square.PolySquare"],
    ["Probapoly", "contrib.probapoly.Probapoly"],
    ["Quantizer", "contrib.quantizer.QuantizerScript"],
    ["RadioScanner", "contrib.radio_scanner.RadioScanner"],
    ["Scope", "contrib.scope.Scope"],
    ["Seq. Switch", "contrib.sequential_switch.SequentialSwitch"],
    ["SmoothRandomVoltages", "contrib.smooth_random_voltages.SmoothRandomVoltages"],
    ["StrangeAttractor", "contrib.strange_attractor.StrangeAttractor"],
    ["Turing Machine", "contrib.turing_machine.EuroPiTuringMachine"],
    ["_Calibrate", "calibrate.Calibrate"],
])


if __name__ == "__main__":
    BootloaderMenu(EUROPI_SCRIPTS).main()
