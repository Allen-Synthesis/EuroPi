# Copyright 2024 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See menu.md for details."""
# Reset the module state and display bootsplash screen.
from europi import bootsplash

bootsplash()

from bootloader import BootloaderMenu
from collections import OrderedDict
import europi_config

## Scripts that are included in the menu
#
#  Keys are the names displayed in the menu, values are the fully-qualified names
#  of the classes to launch.  The classes MUST be EuriPiScript subclasses
#
#  The OLED can display up to 16 characters horizontally, so make sure the names fit
#  that width requirement
#
# fmt: off
EUROPI_SCRIPTS = OrderedDict([
#   ["0123456789abcdef",  "contrib.spam.Eggs"],
    ["Arpeggiator",       "contrib.arp.Arpeggiator"],
    ["Bernoulli Gates",   "contrib.bernoulli_gates.BernoulliGates"],
    ["Bezier Curves",     "contrib.bezier.Bezier"],
    ["Binary Counter",    "contrib.binary_counter.BinaryCounter"],
    ["Bit Garden",        "contrib.bit_garden.BitGarden"],
    ["Bouncing Pixels",   "contrib.bouncing_pixels.BouncingPixels"],
    ["Clock Modifier",    "contrib.clock_mod.ClockModifier"],
    ["Coin Toss",         "contrib.coin_toss.CoinToss"],
    ["Consequencer",      "contrib.consequencer.Consequencer"],
    ["Conway",            "contrib.conway.Conway"],
    ["CVecorder",         "contrib.cvecorder.CVecorder"],
    ["Daily Random",      "contrib.daily_random.DailyRandom"],
    ["DCSN-2",            "contrib.dscn2.Dcsn2"],
    ["DFAM Controller",   "contrib.dfam.DfamController"],
    ["EgressusMelodiam",  "contrib.egressus_melodiam.EgressusMelodiam"],
    ["EnvelopeGen",       "contrib.envelope_generator.EnvelopeGenerator"],
    ["Euclid",            "contrib.euclid.EuclideanRhythms"],
    ["Gates & Triggers",  "contrib.gates_and_triggers.GatesAndTriggers"],
    ["Gate Phaser",       "contrib.gate_phaser.GatePhaser"],
    ["Hamlet",            "contrib.hamlet.Hamlet"],
    ["HarmonicLFOs",      "contrib.harmonic_lfos.HarmonicLFOs"],
    ["HTTP Interface",    "contrib.http_control.HttpControl"],
    ["Itty Bitty",        "contrib.itty_bitty.IttyBitty"],
    ["Kompari",           "contrib.kompari.Kompari"],
    ["Logic",             "contrib.logic.Logic"],
    ["Lutra",             "contrib.lutra.Lutra"],
    ["MasterClock",       "contrib.master_clock.MasterClock"],
    ["Morse",             "contrib.morse.Morse"],
    ["NoddyHolder",       "contrib.noddy_holder.NoddyHolder"],
    ["Ocean Surge",       "contrib.ocean_surge.OceanSurge"],
    ["OSC Interface",     "contrib.osc_control.OscControl"],
    ["Pam's Workout",     "contrib.pams.PamsWorkout2"],
    ["Particle Phys.",    "contrib.particle_physics.ParticlePhysics"],
    ["Pet Rock",          "contrib.pet_rock.PetRock"],
    ["Piconacci",         "contrib.piconacci.Piconacci"],
    ["Poly Square",       "contrib.poly_square.PolySquare"],
    ["PolyrhythmSeq",     "contrib.polyrhythmic_sequencer.PolyrhythmSeq"],
    ["Probapoly",         "contrib.probapoly.Probapoly"],
    ["Quantizer",         "contrib.quantizer.QuantizerScript"],
    ["RadioScanner",      "contrib.radio_scanner.RadioScanner"],
    ["Scope",             "contrib.scope.Scope"],
    ["Seq. Switch",       "contrib.sequential_switch.SequentialSwitch"],
    ["Sigma",             "contrib.sigma.Sigma"],
    ["Slopes",            "contrib.slopes.Slopes"],
    ["Smooth Rnd Volts",  "contrib.smooth_random_voltages.SmoothRandomVoltages"],
    ["StrangeAttractor",  "contrib.strange_attractor.StrangeAttractor"],
    ["Traffic",           "contrib.traffic.Traffic"],
    ["Turing Machine",    "contrib.turing_machine.EuroPiTuringMachine"],
    ["Volts",             "contrib.volts.OffsetVoltages"],

    # Examples & proof-of-concept scripts that aren't generally useful
    # but someone might want to enable to test out
    #["Custom Fonts",      "contrib.custom_font_demo.CustomFontDemo"],
    #["HelloWorld",        "contrib.hello_world.HelloWorld"],
    #["KnobPlayground",    "contrib.knob_playground.KnobPlayground"],
    #["Menu Example",      "contrib.settings_menu_example.SettingsMenuExample"],


    # System tools, in alphabetical order with a _ prefix

    ["_About",            "tools.about.About"],
    ["_BootloaderMode",   "bootloader_mode.BootloaderMode"],
    ["_Calibrate",        "tools.calibrate.Calibrate"],
    ["_Config Editor",    "tools.conf_edit.ConfigurationEditor"],
    ["_Diagnostic",       "tools.diagnostic.Diagnostic"],
    ["_Exp Cfg Editor",   "tools.experimental_conf_edit.ExperimentalConfigurationEditor"],
])
# fmt: on


# Remove scripts that require wifi if the Pico model in use doesn't
# have a wifi module included
cfg = europi_config.load_europi_config()
if (
    cfg.PICO_MODEL != europi_config.MODEL_PICO_W
    and cfg.PICO_MODEL != europi_config.MODEL_PICO_2W
):
    EUROPI_SCRIPTS.pop("HTTP Interface")
    EUROPI_SCRIPTS.pop("OSC Interface")


if __name__ == "__main__":
    BootloaderMenu(EUROPI_SCRIPTS).main()
