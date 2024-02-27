#!/usr/bin/env python3
"""A EuroPi clone of ALM's Pamela's NEW Workout

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@year   2023

See pams.md for complete feature list
"""

from europi import *
from europi_script import EuroPiScript

from experimental.euclid import generate_euclidean_pattern
from experimental.knobs import KnobBank
from experimental.quantizer import CommonScales, Quantizer, SEMITONE_LABELS, SEMITONES_PER_OCTAVE
from experimental.screensaver import OledWithScreensaver

from collections import OrderedDict
from machine import Timer

import gc
import math
import time
import random

## Screensaver-enabled display
ssoled = OledWithScreensaver()

## Lockable knob bank for K2 to make menu navigation a little easier
#
#  Note that this does mean _sometimes_ you'll need to sweep the knob all the way left/right
#  to unlock it
k2_bank = (
    KnobBank.builder(k2)
    .with_unlocked_knob("main_menu")
    .with_locked_knob("submenu", initial_percentage_value=0)
    .with_locked_knob("choice", initial_percentage_value=0)
    .build()
)

## Vertical screen offset for placing user input
SELECT_OPTION_Y = 16

## Exactly what it says on the tin; half the width of a character on the screen
HALF_CHAR_WIDTH = int(CHAR_WIDTH / 2)

## How many ms does a button need to be held to qualify as a long press?
LONG_PRESS_MS = 500

## The scales that each PamsOutput can quantize to
QUANTIZERS = OrderedDict([
    ["None"      , None],
    ["Chromatic" , CommonScales.Chromatic],

    # Major scales
    ["Nat Maj"   , CommonScales.NatMajor],
    ["Har Maj"   , CommonScales.HarMajor],
    ["Maj 135"   , CommonScales.Major135],
    ["Maj 1356"  , CommonScales.Major1356],
    ["Maj 1357"  , CommonScales.Major1357],

    # Minor scales
    ["Nat Min"   , CommonScales.NatMinor],
    ["Har Min"   , CommonScales.HarMinor],
    ["Min 135"   , CommonScales.Minor135],
    ["Min 1356"  , CommonScales.Minor1356],
    ["Min 1357"  , CommonScales.Minor1357],

    # Blues scales
    ["Maj Blues" , CommonScales.MajorBlues],
    ["Min Blues" , CommonScales.MinorBlues],

    # Misc
    ["Whole"     , CommonScales.WholeTone],
    ["Penta"     , CommonScales.Pentatonic],
    ["Dom 7"     , CommonScales.Dominant7]
])

## Sorted list of names for the quantizers to display
QUANTIZER_LABELS = list(QUANTIZERS.keys())

## Always-on gate when the clock is running
CLOCK_MOD_RUN = 100

## Short trigger on clock start
CLOCK_MOD_START = 102

## Short trigger on clock stop
CLOCK_MOD_RESET = 103


## Available clock modifiers
CLOCK_MODS = OrderedDict([
    ["/16" , 1/16.0],
    ["/12" , 1/12.0],
    ["/8" , 1/8.0],
    ["/6" , 1/6.0],
    ["/4" , 1/4.0],
    ["/3" , 1/3.0],
    ["/2" , 1/2.0],
    ["x1" , 1.0],
    ["x2" , 2.0],
    ["x3" , 3.0],
    ["x4" , 4.0],
    ["x6" , 6.0],
    ["x8" , 8.0],
    ["x12", 12.0],
    ["x16", 16.0],
    ["run", CLOCK_MOD_RUN],
    ["start", CLOCK_MOD_START],
    ["reset", CLOCK_MOD_RESET]
])

## Sorted list of string representations of the clock mods
CLOCK_MOD_LABELS = list(CLOCK_MODS.keys())

## Some clock mods have graphics instead of text
CLOCK_MOD_IMGS = OrderedDict([
    [1/16.0, None],  # /16
    [1/12.0, None],  # /12
    [1/8.0, None],  # /8
    [1/6.0, None],  # /6
    [1/4.0, None],  # /4
    [1/3.0, None],  # /3
    [1/2.0, None],  # /2
    [1.0, None],  # x1
    [2.0, None],  # x2
    [3.0, None],  # x3
    [4.0, None],  # x4
    [6.0, None],  # x6
    [8.0, None],  # x8
    [12.0, None],  # x12
    [16.0, None],  # x16
    [CLOCK_MOD_RUN, bytearray(b'\xff\xf0\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00')],    # run gate
    [CLOCK_MOD_START, bytearray(b'\xe0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xbf\xf0')],  # start trigger
    [CLOCK_MOD_RESET, bytearray(b'\x03\xf0\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\xfe\x00')]   # reset trigger
])

## Standard pulse/square wave with PWM
WAVE_SQUARE = 0

## Triangle wave
#
#  - When width is 50 this is a symmetrical triangle /\
#  - When width is < 50 we become more saw-like |\
#  - When sidth is > 50 we become more ramp-like /|
WAVE_TRIANGLE = 1

## Sine wave
#
#  Width is ignored
WAVE_SIN = 2

## A configurable ADSR envelope
WAVE_ADSR = 3

## Random wave
#
#  Width is ignored
WAVE_RANDOM = 4

## Use raw AIN as the direct input
#
#  This lets you effectively use Pam's as a quantizer for
#  the AIN signal
WAVE_AIN = 5

## Using K1 as the direct input
#
#  This lets you "play" K1 as a manual LFO, flat voltage,
#  etc...
WAVE_KNOB = 6

## Available wave shapes
WAVE_SHAPES = [
    WAVE_SQUARE,
    WAVE_TRIANGLE,
    WAVE_SIN,
    WAVE_ADSR,
    WAVE_RANDOM,
    WAVE_AIN,
    WAVE_KNOB
]

## Ordered list of labels for the wave shape chooser menu
WAVE_SHAPE_LABELS = [
    "Square",
    "Triangle",
    "Sine",
    "ADSR",
    "Random",
    "AIN",
    "KNOB"
]

## Sorted list of wave shapes to display
#
#  Same order as WAVE_SHAPE_LABELS
#
#  These are 12x12 bitmaps. See:
#  - https://github.com/Allen-Synthesis/EuroPi/blob/main/software/oled_tips.md
#  - https://github.com/novaspirit/img2bytearray
WAVE_SHAPE_IMGS = [
    bytearray(b'\xfe\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x83\xf0'),  # SQUARE
    bytearray(b'\x06\x00\x06\x00\t\x00\t\x00\x10\x80\x10\x80 @ @@ @ \x80\x10\x80\x10'),                              # TRIANGLE
    bytearray(b'\x10\x00(\x00D\x00D\x00\x82\x00\x82\x00\x82\x10\x82\x10\x01\x10\x01\x10\x00\xa0\x00@'),              # SINE
    bytearray(b' \x00 \x000\x000\x00H\x00H\x00G\xc0@@\x80 \x80 \x80\x10\x80\x10'),                                   # ADSR
    bytearray(b'\x00\x00\x08\x00\x08\x00\x14\x00\x16\x80\x16\xa0\x11\xa0Q\xf0Pp`P@\x10\x80\x00'),                    # RANDOM
    bytearray(b'\x00\x00|\x00|\x00d\x00d\x00g\x80a\x80\xe1\xb0\xe1\xb0\x01\xf0\x00\x00\x00\x00'),                    # AIN
    bytearray(b'\x06\x00\x19\x80 @@ @ \x80\x10\x82\x10A @\xa0 @\x19\x80\x06\x00')                                    # KNOB
]

STATUS_IMG_PLAY = bytearray(b'\x00\x00\x18\x00\x18\x00\x1c\x00\x1c\x00\x1e\x00\x1f\x80\x1e\x00\x1e\x00\x1c\x00\x18\x00\x18\x00')
STATUS_IMG_PAUSE = bytearray(b'\x00\x00y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0')

STATUS_IMG_WIDTH = 12
STATUS_IMG_HEIGHT = 12

## Do we use gate input on din to turn the module on/off
DIN_MODE_GATE = 'Gate'

## Do we toggle the module on/off with a trigger on din?
DIN_MODE_TRIGGER = 'Trig'

## Reset on a rising edge, but don't start/stop the clock
DIN_MODE_RESET = 'Reset'

## Sorted list of DIN modes for display
DIN_MODES = [
    DIN_MODE_GATE,
    DIN_MODE_TRIGGER,
    DIN_MODE_RESET
]

## True/False for yes/no settings (e.g. mute)
YES_NO_MODES = [
    False,
    True
]

## True/False labels for yes/no settings (e.g. mute)
OK_CANCEL_LABELS = [
    "Cancel",
    "OK"
]
YES_NO_LABELS = [
    "N",
    "Y"
]

## IDs for the load/save banks
#
#  Banks are shared across all channels
#  The -1 index is used to indicate "cancel"
BANK_IDs = list(range(-1, 6))

## Labels for the banks
BANK_LABELS = [
    "Cancel",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6"
]

## Integers 0-100 for choosing a percentage value
PERCENT_RANGE = list(range(101))

class Setting:
    """A single setting that can be loaded, saved, or dynamically read from an analog input
    """
    def __init__(self, display_name, storage_name, display_options, options, \
                 allow_cv_in=True, value_dict=None, default_value=None, on_change_fn=None, callback_arg=None,
                 is_visible=True):
        """Create a new setting

        @param display_name     The name displayed on the screen as the setting's title
        @param storage_name     The name used in the storage dictionary to identify this setting's persistent values
        @param display_options  The list of options we display to the user to choose from
        @param options          The raw options we choose from
        @param allow_cv_in      If true, we appent AIN to the options & display options
        @param value_dict       A dictionary that can convert between the list items in options & any other type
        @param default_value    This setting's default value
        @param on_change_fn     A callback function to call when this setting changes. The function must accept 1-2 args:
                                a reference to this Setting instance, and (optionally) the value passed to callback_arg
        @param callback_arg     An optional argument to passed as the 2nd argument to on_change_fn when it is called
        @param is_visible       Used to indicate whether or not this setting should be visible in the GUI
        """
        self.display_name = display_name
        self.display_options = [o for o in display_options]

        self.on_change_fn = on_change_fn
        self.callback_arg = callback_arg

        self.storage_name = storage_name
        self.options = [o for o in options]

        self.allow_cv_in = allow_cv_in
        if allow_cv_in:
            for cv in CV_INS.keys():
                self.display_options.append(cv)
                self.options.append(CV_INS[cv])

        self.value_dict = value_dict
        self.default_value = default_value
        if self.default_value is not None:
            self.choice = self.options.index(self.default_value)
        else:
            self.choice = 0

        self.is_visible = is_visible

    def __str__(self):
        return self.display_name

    def __len__(self):
        return len(self.options)

    def load(self, settings):
        if type(settings) is dict and "value" in settings.keys():
            self.choice = settings["value"]
        else:
            self.choice = settings

    def to_dict(self):
        return self.choice

    def update_options(self, display_options, options):
        if self.choice >= len(options):
            self.choice = len(options)-1

        self.display_options = [
            o for o in display_options
        ]
        self.options = [
            o for o in options
        ]

        if self.allow_cv_in:
            for cv in CV_INS.keys():
                self.display_options.append(cv)
                self.options.append(CV_INS[cv])

    def get_value(self):
        if type(self.options[self.choice]) is AnalogInReader:
            # Remove the CV inputs from the set of choices, since otherwise that would lead to weird recursion!
            n = round(self.options[self.choice].get_value() / MAX_INPUT_VOLTAGE * len(self.options) - len(CV_INS))
            if n < 0:
                n = 0
            elif n >= len(self.options) - len(CV_INS):
                n = len(self.options) - len(CV_INS) - 1
            key = n
        else:
            key = self.choice

        opt = self.options[key]

        if self.value_dict:
            return self.value_dict[opt]
        else:
            return opt

    def get_display_value(self):
        return self.display_options[self.choice]

    def choose(self, index):
        is_changing = self.choice != index
        self.choice = index
        if is_changing and self.on_change_fn:
            if self.callback_arg is not None:
                self.on_change_fn(self, self.callback_arg)
            else:
                self.on_change_fn(self)

    def reset_to_default(self):
        """Reset this setting to its default value
        """
        index = 0
        if self.default_value is not None:
            index = self.options.index(self.default_value)
        self.choose(index)

class AnalogInReader:
    """A wrapper for `ain` that can be shared across multiple Settings

    This allows `ain` to be read once during the main loop, but keep its value across multiple
    accesses across each output channel.  It also adds gain & precision settings that can
    be adjusted in application's menu
    """
    def __init__(self, cv_in):
        self.cv_in = cv_in
        self.last_voltage = 0.0

        self.gain = Setting("Gain", "gain", list(range(301)), list(range(301)), allow_cv_in=False, default_value=100)
        self.precision = Setting("Precision", "precision", ["Low", "Med", "High"], \
            [int(DEFAULT_SAMPLES/2), DEFAULT_SAMPLES, int(DEFAULT_SAMPLES*2)], allow_cv_in=False, default_value=DEFAULT_SAMPLES)

    def to_dict(self):
        return {
            "gain": self.gain.to_dict(),
            "precision": self.precision.to_dict()
        }

    def load_settings(self, settings):
        if "gain" in settings.keys():
            self.gain.load(settings["gain"])
        if "precision" in settings.keys():
            self.precision.load(settings["precision"])

    def update(self):
        """Read the current voltage from the analog input using the configured precision

        Sets self.last_voltage, which is returned by self.get_value()

        @return The voltage read from the analog input multiplied by self.gain
        """
        self.last_voltage = self.cv_in.percent(self.precision.get_value()) * MAX_INPUT_VOLTAGE * self.gain.get_value() / 100.0
        return self.last_voltage

    def get_value(self):
        return self.last_voltage

## Wrapped copies of all CV inputs so we can iterate through them
CV_INS = {
    "KNOB": AnalogInReader(k1),
    "AIN": AnalogInReader(ain)
}

class MasterClock:
    """The main clock that ticks and runs the outputs
    """

    ## The clock actually runs faster than its maximum BPM to allow
    #  clock divisions to work nicely
    #
    #  Use 48 internal clock pulses per quarter note. This is slow enough
    #  that we won't choke the CPU with interrupts, but smooth enough that we
    #  should be able to approximate complex waves.  Must be a multiple of
    #  3 to properly support triplets and a multiple of 16 to allow easy
    #  semi-quavers
    PPQN = 48

    ## The absolute slowest the clock can go
    MIN_BPM = 1

    ## The absolute fastest the clock can go
    MAX_BPM = 240

    def __init__(self, bpm):
        """Create the main clock to run at a given bpm
        @param bpm  The initial BPM to run the clock at
        """

        self.channels = []
        self.is_running = False

        self.bpm = Setting("BPM", "bpm", list(range(self.MIN_BPM, self.MAX_BPM+1)), list(range(self.MIN_BPM, self.MAX_BPM+1)), on_change_fn=self.recalculate_timer_hz, default_value=60)
        self.reset_on_start = Setting("Stop-Rst", "reset_on_start", ["Off", "On"], [False, True], default_value=True, allow_cv_in=False)

        self.tick_hz = 1.0
        self.timer = Timer()
        self.recalculate_timer_hz()

        self.elapsed_pulses = 0
        self.start_time = 0

    def add_channels(self, channels):
        """Add the CV channels that this clock is (indirectly) controlling

        @param channels  A list of PamsOutput objects corresponding to the
                         output channels
        """
        for ch in channels:
            self.channels.append(ch)

    def to_dict(self):
        """Return a dict with the clock's parameters
        """
        return {
            "bpm": self.bpm.to_dict(),
            "reset_on_start": self.reset_on_start.to_dict()
        }

    def load_settings(self, settings):
        """Apply settings loaded from the configuration file

        @param settings  A dict containing the same fields as to_dict(self)
        """
        if "bpm" in settings.keys():
            self.bpm.load(settings["bpm"])
        if "reset_on_start" in settings.keys():
            self.reset_on_start.load(settings["reset_on_start"])

        self.recalculate_timer_hz()

    def on_tick(self, timer):
        """Callback function for the timer's tick
        """
        if self.is_running:
            for ch in self.channels:
                ch.tick()
            self.elapsed_pulses = self.elapsed_pulses + 1
            for ch in self.channels:
                ch.apply()

    def start(self):
        """Start the timer
        """
        if not self.is_running:
            self.is_running = True
            self.start_time = time.ticks_ms()

            if self.reset_on_start.get_value():
                self.elapsed_pulses = 0
                for ch in self.channels:
                    ch.reset()

            self.timer.init(freq=self.tick_hz, mode=Timer.PERIODIC, callback=self.on_tick)

    def stop(self):
        """Stop the timer
        """
        if self.is_running:
            self.is_running = False
            self.timer.deinit()

            # Fire a reset trigger on any channels that have the CLOCK_MOD_RESET mode set
            # This trigger lasts 10ms
            # Turn all other channels off so we don't leave hot wires
            for ch in self.channels:
                if ch.clock_mod.get_value() == CLOCK_MOD_RESET:
                    ch.cv_out.voltage(MAX_OUTPUT_VOLTAGE * ch.amplitude.get_value() / 100.0)
                else:
                    ch.cv_out.off()
            time.sleep(0.01)   # time.sleep works in SECONDS not ms
            for ch in self.channels:
                if ch.clock_mod.get_value() == CLOCK_MOD_RESET:
                    ch.cv_out.off()

    def running_time(self):
        """Return how long the clock has been running
        """
        if self.is_running:
            now = time.ticks_ms()
            return time.ticks_diff(now, self.start_time)
        else:
            return 0

    def recalculate_timer_hz(self, bpm=None):
        """Recalculate the frequency of the inner timer

        If the timer is currently running deinitialize it and reset it to use the correct BPM

        @param bpm  The BPM setting when this is called as an on-change callback
        """
        self.tick_hz = self.bpm.get_value() / 60.0 * self.PPQN

        if self.is_running:
            self.timer.deinit()
            self.timer.init(freq=self.tick_hz, mode=Timer.PERIODIC, callback=self.on_tick)

class PamsOutput:
    """Controls a single output jack
    """

    ## The maximum length of a Euclidean pattern we allow
    #
    #  The maximum is somewhat arbitrary, but depends more on the UI since the knob
    #  resolution is only so good.
    MAX_EUCLID_LENGTH = 64

    ## Minimum duration of a CLOCK_MOD_START trigger
    #
    #  The actual length depends on clock rate and PPQN, and may be longer than this
    TRIGGER_LENGTH_MS = 10

    def __init__(self, cv_out, clock, n):
        """Create a new output to control a single cv output

        @param cv_out  One of the six output jacks
        @param clock  The MasterClock that controls the timing of this output
        """

        self.cv_n = n
        self.out_volts = 0.0
        self.cv_out = cv_out
        self.clock = clock

        ## What quantization are we using?
        #
        #  See contrib.pams.QUANTIZERS
        self.quantizer = Setting("Quant.", "quantizer", QUANTIZER_LABELS, QUANTIZER_LABELS, value_dict=QUANTIZERS, \
            on_change_fn=self.update_menu_visibility)

        ## The root of the quantized scale (ignored if quantizer is None)
        self.root = Setting("Q Root", "root", SEMITONE_LABELS, list(range(SEMITONES_PER_OCTAVE)))

        ## The clock modifier for this channel
        #
        #  - 1.0 is the same as the main clock's BPM
        #  - <1.0 will tick slower than the BPM (e.g. 0.5 will tick once every 2 beats)
        #  - >1.0 will tick faster than the BPM (e.g. 3.0 will tick 3 times per beat)
        self.clock_mod = Setting("Mod", "clock_mod", CLOCK_MOD_LABELS, CLOCK_MOD_LABELS, value_dict=CLOCK_MODS, \
            default_value="x1", allow_cv_in=False, on_change_fn=self.request_clock_mod)

        ## To prevent phase misalignment we use this as the active clock modifier
        #
        #  If clock_mod is changed, we apply it to this when it is safe to do so
        self.real_clock_mod = self.clock_mod.get_value()

        ## Indicates if clock_mod and real_clock_mod are the same or not
        self.clock_mod_dirty = False

        ## What shape of wave are we generating?
        #
        #  For now, stick to square waves for triggers & gates
        self.wave_shape = Setting("Wave", "wave", WAVE_SHAPE_LABELS, WAVE_SHAPES, default_value=WAVE_SQUARE, \
            allow_cv_in=False, on_change_fn=self.update_menu_visibility)

        ## The phase offset of the output as a [0, 100] percentage
        self.phase = Setting("Phase", "phase", PERCENT_RANGE, PERCENT_RANGE, default_value=0)

        ## The amplitude of the output as a [0, 100] percentage
        self.amplitude = Setting("Ampl.", "ampl", PERCENT_RANGE, PERCENT_RANGE, default_value=50)

        ## Wave width
        self.width = Setting("Width", "width", PERCENT_RANGE, PERCENT_RANGE, default_value=50)

        ## Euclidean -- number of steps in the pattern (0 = disabled)
        euclid_choices = list(range(self.MAX_EUCLID_LENGTH+1))
        self.e_step = Setting("EStep", "e_step", euclid_choices, euclid_choices, \
            on_change_fn=self.change_e_length, default_value=0)

        ## Euclidean -- number of triggers in the pattern
        self.e_trig = Setting("ETrig", "e_trig", euclid_choices, euclid_choices, \
            on_change_fn=self.recalculate_e_pattern, default_value=0)

        ## Euclidean -- rotation of the pattern
        self.e_rot = Setting("ERot", "e_rot", euclid_choices, euclid_choices, \
            on_change_fn=self.recalculate_e_pattern, default_value=0)

        ## Probability that we skip an output [0-100]
        self.skip = Setting("Skip%", "skip", PERCENT_RANGE, PERCENT_RANGE, default_value=0)

        # ADSR settings
        self.attack = Setting("Attack", "attack", PERCENT_RANGE, PERCENT_RANGE, default_value=10)
        self.decay = Setting("Decay", "decay", PERCENT_RANGE, PERCENT_RANGE, default_value=10)
        self.sustain = Setting("Sustain", "sustain", PERCENT_RANGE, PERCENT_RANGE, default_value=50)
        self.release = Setting("Release", "release", PERCENT_RANGE, PERCENT_RANGE, default_value=50)

        ## Swing percentage
        #
        #  50% -> even, no swing
        #  <50% -> short-long-short-long-...
        #  >50% -> long-short-long-short-...
        self.swing = Setting("Swing%", "swing", PERCENT_RANGE, PERCENT_RANGE, default_value=50)

        ## Allows muting a channel during runtime
        #
        #  A muted channel can still be edited
        self.mute = Setting("Mute", "mute", YES_NO_LABELS, YES_NO_MODES, False)

        ## All settings in an array so we can iterate through them in reset_settings(self)
        self.all_settings = [
            self.quantizer,
            self.root,
            self.clock_mod,
            self.wave_shape,
            self.phase,
            self.amplitude,
            self.width,
            self.e_step,
            self.e_trig,
            self.e_rot,
            self.skip,
            self.swing,
            self.mute,
            self.attack,
            self.decay,
            self.sustain,
            self.release
        ]

        ## Counter that increases every time we finish a full wave form
        self.wave_counter = 0

        ## The euclidean pattern we step through
        self.e_pattern = [1]

        ## Our current position within the euclidean pattern
        self.e_position = 0

        ## If we change patterns while playing store the next one here and
        #  change when the current pattern ends
        #
        #  This helps ensure all outputs stay synchronized. The down-side is
        #  that a slow pattern may take a long time to reset
        self.next_e_pattern = None

        ## The previous sample we played back
        self.previous_wave_sample = 0

        ## Used during the tick() function to store whether or not we're skipping
        #  the current step
        self.skip_this_step = False

        self.change_e_length()

        self.update_menu_visibility()

    def __str__(self):
        return f"out_cv{self.cv_n}"

    def update_menu_visibility(self, sender=None, args=None):
        """Callback function for changing the visibility of menu items

        @param sender  The Setting object that called this function
        @param args    The callback arguments passed from the Setting
        """

        # hide the ADSR settings if we're not in ADSR mode
        wave_shape = self.wave_shape.get_value()
        show_adsr = wave_shape == WAVE_ADSR
        self.attack.is_visible = show_adsr
        self.decay.is_visible = show_adsr
        self.sustain.is_visible = show_adsr
        self.release.is_visible = show_adsr

        # hide the quantization root if we're not quantizing
        show_root = self.quantizer.get_value() is not None
        self.root.is_visible = show_root

        # hide the width parameter if we're reading from AIN or KNOB, or outputting a sine wave
        show_width = wave_shape != WAVE_AIN and wave_shape != WAVE_KNOB and wave_shape != WAVE_SIN
        self.width.is_visible = show_width

    def to_dict(self):
        """Return a dictionary with all the configurable settings to write to disk
        """
        return {
            "clock_mod" : self.clock_mod.to_dict(),
            "e_step"    : self.e_step.to_dict(),
            "e_trig"    : self.e_trig.to_dict(),
            "e_rot"     : self.e_rot.to_dict(),
            "skip"      : self.skip.to_dict(),
            "wave"      : self.wave_shape.to_dict(),
            "phase"     : self.phase.to_dict(),
            "amplitude" : self.amplitude.to_dict(),
            "width"     : self.width.to_dict(),
            "quantizer" : self.quantizer.to_dict(),
            "root"      : self.root.to_dict(),
            "swing"     : self.swing.to_dict(),
            "mute"      : self.mute.to_dict(),
            "attack"    : self.attack.to_dict(),
            "decay"     : self.decay.to_dict(),
            "sustain"   : self.sustain.to_dict(),
            "release"   : self.release.to_dict(),
        }

    def load_settings(self, settings):
        """Apply the settings loaded from storage

        @param settings  A dict with the same keys as the one returned by to_dict()
        """
        if "clock_mod" in settings.keys():
            self.clock_mod.load(settings["clock_mod"])
        if "e_step" in settings.keys():
            self.e_step.load(settings["e_step"])
        if "e_trig" in settings.keys():
            self.e_trig.load(settings["e_trig"])
        if "e_rot" in settings.keys():
            self.e_rot.load(settings["e_rot"])
        if "skip" in settings.keys():
            self.skip.load(settings["skip"])
        if "wave" in settings.keys():
            self.wave_shape.load(settings["wave"])
        if "phase" in settings.keys():
            self.phase.load(settings["phase"])
        if "amplitude" in settings.keys():
            self.amplitude.load(settings["amplitude"])
        if "width" in settings.keys():
            self.width.load(settings["width"])
        if "quantizer" in settings.keys():
            self.quantizer.load(settings["quantizer"])
        if "root" in settings.keys():
            self.root.load(settings["root"])
        if "swing" in settings.keys():
            self.swing.load(settings["swing"])
        if "mute" in settings.keys():
            self.mute.load(settings["mute"])
        if "attack" in settings.keys():
            self.attack.load(settings["attack"])
        if "decay" in settings.keys():
            self.decay.load(settings["decay"])
        if "sustain" in settings.keys():
            self.sustain.load(settings["sustain"])
        if "release" in settings.keys():
            self.release.load(settings["release"])

        self.change_e_length()
        self.update_menu_visibility()
        self.real_clock_mod = self.clock_mod.get_value()

    def change_e_length(self, setting=None):
        self.e_trig.update_options(list(range(self.e_step.get_value()+1)), list(range(self.e_step.get_value()+1)))
        self.e_rot.update_options(list(range(self.e_step.get_value()+1)), list(range(self.e_step.get_value()+1)))
        self.recalculate_e_pattern()

    def request_clock_mod(self, setting=None):
        self.clock_mod_dirty = True

    def change_clock_mod(self):
        self.real_clock_mod = self.clock_mod.get_value()
        self.clock_mod_dirty = False

    def recalculate_e_pattern(self, setting=None):
        """Recalulate the euclidean pattern this channel outputs
        """
        # always assume we're doing some kind of euclidean pattern
        e_pattern = [1]
        if self.e_step.get_value() > 0:
            e_pattern = generate_euclidean_pattern(self.e_step.get_value(), self.e_trig.get_value(), self.e_rot.get_value())

        self.next_e_pattern = e_pattern

    def square_wave(self, tick, n_ticks):
        """Calculate the [0, 1] value of a square wave with PWM

        @param tick  The current tick, in the range [0, n_ticks)
        @param n_ticks  The number of ticks in which the wave must complete

        @return A value in the range [0, 1] indicating the height of the wave at this tick
        """
        # the first part of the square wave is on, the last part is off
        # cutoff depends on the duty-cycle/pulse width
        duty_cycle = n_ticks * self.width.get_value() / 100.0

        # because of phase offset the wave _can_ start at e.g. 75% of the ticks and end at the following window's 25%
        start_tick = self.phase.get_value() * n_ticks / 100.0
        end_tick = (start_tick + duty_cycle) % n_ticks

        if (start_tick < end_tick and tick >= start_tick and tick < end_tick) or \
           (start_tick > end_tick and (tick < end_tick or tick >= start_tick)):
            return 1.0
        else:
            return 0.0

    def triangle_wave(self, tick, n_ticks):
        """Calculate the [0, 1] value of a triangle wave

        @param tick  The current tick, in the range [0, n_ticks)
        @param n_ticks  The number of ticks in which the wave must complete

        @return A value in the range [0, 1] indicating the height of the wave at this tick
        """
        # rising and then falling, with the peak dependent on the pulse width
        rising_ticks = round(n_ticks * self.width.get_value() / 100.0)
        falling_ticks = n_ticks - rising_ticks
        peak = 1.0
        y = 0.0

        tick = int(tick + self.phase.get_value() * n_ticks / 100.0) % n_ticks

        if tick < rising_ticks:
            # we're on the rising side of the triangle wave
            step = peak / rising_ticks
            y = step * tick
        elif tick == rising_ticks:
            y = peak
        else:
            # we're on the falling side of the triangle
            step = peak / falling_ticks
            y = peak - step * (tick - rising_ticks)
        return y

    def sine_wave(self, tick, n_ticks):
        """Calculate the [0, 1] value of a sine wave

        @param tick  The current tick, in the range [0, n_ticks)
        @param n_ticks  The number of ticks in which the wave must complete

        @return A value in the range [0, 1] indicating the height of the wave at this tick

        Because EuroPi cannot output negative voltages, we shift the wave up so its middle is at 0.5 and peaks/troughs
        are at 1.0 and 0.0 respectively
        """
        # bog-standard sine wave
        theta = (tick + self.phase.get_value() / 100.0 * n_ticks) / n_ticks * 2 * math.pi  # covert the tick to radians
        s_theta = (math.sin(theta) + 1) / 2   # (sin(x) + 1)/2 since we can't output negative voltages
        return s_theta

    def adsr_wave(self, tick, n_ticks):
        """Calculate the [0, 1] level of an ADSR envelope

        Attack is the % of the total time that covers the attack phase, moving from 0 to 1 linearly

        Decay is the % of the remaining time that covers the decay phase, moving from 1 to X linearly

        Sustain is the % level to sustain at, defining X for the decay phase

        Release is the % of the remaining time that covers the release phase, moving from X to 0 linearly

           /\
          /  \______
         /          \
        /            \
        -A--D---S---R-
        ---n_ticks----
        """

        # apply the phase offset
        tick = int(tick + self.phase.get_value() * n_ticks / 100.0) % n_ticks

        # the ADSR envelope only lasts for n_ticks * width%, so reduce the size of the window for further calculations
        n_ticks = int(n_ticks * self.width.get_value() / 100.0)

        attack_ticks = int(n_ticks * self.attack.get_value() / 100.0)
        decay_ticks = int((n_ticks - attack_ticks) * self.decay.get_value() / 100.0)
        release_ticks = int((n_ticks - decay_ticks - attack_ticks) * self.release.get_value() / 100.0)
        sustain_ticks = n_ticks - attack_ticks - decay_ticks - release_ticks
        sustain_level = self.sustain.get_value() / 100.0

        if tick < attack_ticks:
            # attack phase
            slope = 1.0 / attack_ticks
            return tick * slope
        elif tick < attack_ticks + decay_ticks:
            # decay phase
            slope = (1 - sustain_level) / decay_ticks
            return 1 - slope * (tick - attack_ticks)
        elif tick < attack_ticks + decay_ticks + sustain_ticks:
            # sustain phase
            return sustain_level
        elif tick < attack_ticks + decay_ticks + sustain_ticks + release_ticks:
            # release phase
            slope = sustain_level / release_ticks
            return sustain_level - slope * (tick - attack_ticks - decay_ticks - sustain_ticks)
        else:
            # outside of the ADSR
            return 0.0

    def reset(self):
        """Reset the current output to the beginning
        """
        self.e_position = 0
        if self.next_e_pattern:
            self.e_pattern = self.next_e_pattern
            self.next_e_pattern = None

        self.wave_counter = 0
        self.change_clock_mod()

    def reset_settings(self):
        """Reset all settings to their default values
        """
        for s in self.all_settings:
            s.reset_to_default()

    def tick(self):
        """Advance the current pattern one tick and calculate the output voltage

        Call apply() to actually send the voltage. This lets us calculate all output channels and THEN set the
        outputs after so they're more synchronized
        """

        if self.real_clock_mod == CLOCK_MOD_START:
            # start waves are weird; they're only on during the first 10ms or 1 PPQN (whichever is longer)
            # and are otherwise always off
            gate_len = self.clock.running_time()
            if self.clock.elapsed_pulses == 0 or gate_len <= self.TRIGGER_LENGTH_MS:
                out_volts = MAX_OUTPUT_VOLTAGE * self.amplitude.get_value() / 100.0
            else:
                out_volts = 0.0
        elif self.real_clock_mod == CLOCK_MOD_RUN:
            out_volts = MAX_OUTPUT_VOLTAGE * self.amplitude.get_value() / 100.0
        elif self.real_clock_mod == CLOCK_MOD_RESET:
            # reset waves are always low; the clock's stop() function handles triggering them
            out_volts = 0.0
        else:
            if self.wave_counter % 2 == 0:
                # first half of the swing; if swing < 50% this is short, otherwise long
                swing_amt = self.swing.get_value() / 100.0
            else:
                # second half of the swing; if swing < 50% this is long, otherwise short
                swing_amt = (100 - self.swing.get_value()) / 100.0
            ticks_per_note = round(2 * MasterClock.PPQN / self.real_clock_mod * swing_amt)
            if ticks_per_note == 0:
                # we're swinging SO HARD that one beat is squashed out of existence!
                # move immediately to the other beat
                self.e_position = self.e_position + 1
                if self.e_position >= len(self.e_pattern):
                    self.e_position = 0
                ticks_per_note = round(2 * MasterClock.PPQN / self.real_clock_mod)

            e_step = self.e_pattern[self.e_position]
            wave_position = self.clock.elapsed_pulses % ticks_per_note
            # are we starting a new repeat of the pattern?
            rising_edge = (wave_position == int(self.phase.get_value() * ticks_per_note / 100.0)) and e_step
            # determine if we should skip this sample playback
            if rising_edge:
                self.skip_this_step = random.randint(0, 100) < self.skip.get_value()
                self.wave_counter += 1

            wave_sample = int(e_step) * int (not self.skip_this_step)
            if self.wave_shape.get_value() == WAVE_RANDOM:
                if rising_edge and not self.skip_this_step:
                    wave_sample = random.random() * (self.amplitude.get_value() / 100.0) + (self.width.get_value() / 100.0)
                else:
                    wave_sample = self.previous_wave_sample
            elif self.wave_shape.get_value() == WAVE_AIN:
                if rising_edge and not self.skip_this_step:
                    wave_sample = CV_INS["AIN"].get_value() / MAX_INPUT_VOLTAGE
                else:
                    wave_sample = self.previous_wave_sample
            elif self.wave_shape.get_value() == WAVE_KNOB:
                if rising_edge and not self.skip_this_step:
                    wave_sample = CV_INS["KNOB"].get_value() / MAX_INPUT_VOLTAGE
                else:
                    wave_sample = self.previous_wave_sample
            elif self.wave_shape.get_value() == WAVE_SQUARE:
                wave_sample = wave_sample * self.square_wave(wave_position, ticks_per_note) * (self.amplitude.get_value() / 100.0)
            elif self.wave_shape.get_value() == WAVE_TRIANGLE:
                wave_sample = wave_sample * self.triangle_wave(wave_position, ticks_per_note) * (self.amplitude.get_value() / 100.0)
            elif self.wave_shape.get_value() == WAVE_SIN:
                wave_sample = wave_sample * self.sine_wave(wave_position, ticks_per_note) * (self.amplitude.get_value() / 100.0)
            elif self.wave_shape.get_value() == WAVE_ADSR:
                wave_sample = wave_sample * self.adsr_wave(wave_position, ticks_per_note) * (self.amplitude.get_value() / 100.0)
            else:
                wave_sample = 0.0

            self.previous_wave_sample = wave_sample
            out_volts = wave_sample * MAX_OUTPUT_VOLTAGE

            if self.quantizer.get_value() is not None:
                (out_volts, note) = self.quantizer.get_value().quantize(out_volts, self.root.get_value())

            if wave_position == ticks_per_note - 1:
                if self.next_e_pattern:
                    # if we just finished a waveform and we have a new euclidean pattern, start it
                    # this will always line up with the current beat, but may be rotated relative to
                    # other patterns currently playing.
                    # rather than do a lot of math, treat this as a feature that if you change patterns
                    # while playing, the new pattern starts right away instead of waiting for for the
                    # end of (a potentially long, slow) pattern to finish
                    self.e_position = 0
                    self.e_pattern = self.next_e_pattern
                    self.next_e_pattern = None
                else:
                    # if we've reached end of the euclidean pattern start it again
                    self.e_position = self.e_position + 1
                    if self.e_position >= len(self.e_pattern):
                        self.e_position = 0

        # If the clock modifier was changed, apply the new value now
        if self.clock_mod_dirty:
            self.change_clock_mod()

        self.out_volts = out_volts

    def apply(self):
        """Apply the calculated voltage to the output channel

        If the channel is muted this will set the output to zero, regardless of anything else
        """
        if self.mute.get_value():
            self.cv_out.off()
        else:
            self.cv_out.voltage(self.out_volts)

class SettingChooser:
    """Menu UI element for displaying a Setting object and the options associated with it
    """
    def __init__(self, prefix, setting, gfx=None, submenu=[]):
        """Create a setting chooser for a given item

        @param prefix  A prefix we show before the option title (e.g. 'CV1 | ')
        @param setting  The Setting object we're manipulating
        @param submenu  A list of SettingChooser items that make up this setting's submenu
        @param gfx  A list of 12x12 pixel bitmaps we can optionally display beside option_txt
        """
        self.prefix = prefix
        self.setting = setting
        self.submenu = submenu
        self.option_gfx = gfx

        self.is_writable = False

    def __str__(self):
        return f"Setting Chooser for {self.prefix}{self.setting}"

    def set_editable(self, can_edit):
        """Set whether or not we can write to this setting

        @param can_edit  If True, we can write a new value
        """
        self.is_writable = can_edit

    def is_editable(self):
        return self.is_writable

    def draw(self):
        """Draw the menu to the screen

        The OLED must be cleared before calling this function. You must call ssoled.show() after
        calling this function
        """

        text_left = 0
        prefix_left = 1
        prefix_right = len(self.prefix)*CHAR_WIDTH
        title_left = len(self.prefix)*CHAR_WIDTH + 4

        # If we're in a top-level menu the submenu is non-empty. In that case, the prefix in inverted text
        # Otherwise, the title in inverted text to indicate we're in the sub-menu
        if len(self.submenu) != 0:
            ssoled.fill_rect(prefix_left-1, 0, prefix_right+1, CHAR_HEIGHT+2, 1)
            ssoled.text(self.prefix, prefix_left, 1, 0)
            ssoled.text(str(self.setting), title_left, 1, 1)
        else:
            ssoled.fill_rect(title_left-1, 0, len(str(self.setting))*CHAR_WIDTH+2, CHAR_HEIGHT+2, 1)
            ssoled.text(self.prefix, prefix_left, 1, 1)
            ssoled.text(str(self.setting), title_left, 1, 0)

        if self.option_gfx is not None:
            # draw the option thumbnail to the screen if it exists
            img = None
            if self.is_writable:
                if type(self.option_gfx) is dict or\
                   type(self.option_gfx) is OrderedDict:
                    key = k2_bank.current.choice(list(self.option_gfx.keys()))
                    img = self.option_gfx[key]
                else:
                    img = k2_bank.current.choice(self.option_gfx)
            else:
                key = self.setting.get_value()
                img = self.option_gfx[key]

            if img is not None:
                text_left = 14
                imgFB = FrameBuffer(img, 12, 12, MONO_HLSB)
                ssoled.blit(imgFB, 0, SELECT_OPTION_Y)


        if self.is_writable:
            # draw the selection in inverted text
            selected_item = k2_bank.current.choice(self.setting.display_options)
            choice_text = f"{selected_item}"
            text_width = len(choice_text)*CHAR_WIDTH

            ssoled.fill_rect(text_left, SELECT_OPTION_Y, text_left+text_width+3, CHAR_HEIGHT+4, 1)
            ssoled.text(choice_text, text_left+1, SELECT_OPTION_Y+2, 0)
        else:
            # draw the selection in normal text
            choice_text = f"{self.setting.get_display_value()}"
            ssoled.text(choice_text, text_left+1, SELECT_OPTION_Y+2, 1)


    def on_click(self):
        if self.is_writable:
            self.set_editable(False)
            selected_index = k2_bank.current.choice(list(range(len(self.setting))))
            self.setting.choose(selected_index)
        else:
            self.set_editable(True)

class PamsMenu:
    def __init__(self, script):
        """Create the top-level menu for the application

        @param script  The PamsWorkout object the meny belongs to
        """

        self.pams_workout = script

        self.items = [
            SettingChooser("Clk", script.clock.bpm, None, [
                SettingChooser("Clk", script.din_mode),
                SettingChooser("Clk", script.clock.reset_on_start)
            ])
        ]
        for i in range(len(script.channels)):
            prefix = f"CV{i+1}"
            ch = script.channels[i]
            self.items.append(SettingChooser(prefix, ch.clock_mod, CLOCK_MOD_IMGS, [
                SettingChooser(prefix, ch.wave_shape, WAVE_SHAPE_IMGS),
                SettingChooser(prefix, ch.width),
                SettingChooser(prefix, ch.phase),
                SettingChooser(prefix, ch.amplitude),
                SettingChooser(prefix, ch.attack),
                SettingChooser(prefix, ch.decay),
                SettingChooser(prefix, ch.sustain),
                SettingChooser(prefix, ch.release),
                SettingChooser(prefix, ch.skip),
                SettingChooser(prefix, ch.e_step),
                SettingChooser(prefix, ch.e_trig),
                SettingChooser(prefix, ch.e_rot),
                SettingChooser(prefix, ch.swing),
                SettingChooser(prefix, ch.quantizer),
                SettingChooser(prefix, ch.root),
                SettingChooser(prefix, ch.mute),
                SettingChooser(prefix, Setting("Save", "save", BANK_LABELS, BANK_IDs, allow_cv_in=False,
                    on_change_fn=self.save_channel, callback_arg=ch)),
                SettingChooser(prefix, Setting("Load", "load", BANK_LABELS, BANK_IDs, allow_cv_in=False,
                    on_change_fn=self.load_channel, callback_arg=ch)),
                SettingChooser(prefix, Setting("Reset", "reset", OK_CANCEL_LABELS, YES_NO_MODES, allow_cv_in=False,
                    on_change_fn=self.reset_channel, callback_arg=ch))
            ]))
        for ch in CV_INS.keys():
            self.items.append(SettingChooser(ch, CV_INS[ch].gain, None, [
                SettingChooser(ch, CV_INS[ch].precision)
            ]))

        self.active_items = self.items

        ## The item we're actually drawing to the screen _right_now_
        self.visible_item = k2_bank.current.choice(self.get_active_items())

    def get_active_items(self):
        """Return a list of the visible items in the active_items for this menu layer
        """
        return [
            item for item in self.active_items if item.setting.is_visible
        ]

    def on_long_press(self):
        # return the active item to the read-only state
        self.visible_item.set_editable(False)

        # toggle between the two menu levels
        if self.active_items == self.items:
            self.active_items = self.visible_item.submenu
            k2_bank.set_current("submenu")
        else:
            self.active_items = self.items
            k2_bank.set_current("main_menu")

    def on_click(self):
        self.visible_item.on_click()
        if self.visible_item.is_writable:
            k2_bank.set_current("choice")
        elif self.active_items == self.items:
            k2_bank.set_current("main_menu")
        else:
            k2_bank.set_current("submenu")

    def draw(self):
        if not self.visible_item.is_editable():
            self.visible_item = k2_bank.current.choice(self.get_active_items())

        self.visible_item.draw()

    def reset_channel(self, setting, channel):
        """Reset the given channel if the reset_setting is True

        @param setting  A Setting instance that calls this function as a callback
        @param channel  The channel to reset
        """

        if setting.get_value():
            # reset the given channel to default...
            channel.reset_settings()
            # ...then reset this setting back to N so we can reset again later
            setting.reset_to_default()

    def save_channel(self, setting, channel):
        """Save the channel settings to the selected bank

        @param setting   The Setting instance that calls this function as a callback
        @param channel   The channel to save
        """
        try:
            gc.collect()
            bank = setting.get_value()
            if bank >= 0 and bank < len(self.pams_workout.banks):
                self.pams_workout.banks[bank] = channel.to_dict()
        except Exception as err:
            print(f"Failed to save settings: {err}")
        finally:
            gc.collect()

    def load_channel(self, setting, channel):
        """Load the channel settings from the selected bank

        @param setting  The Setting instance that calls this function as a callback
        @param channel  The channel to load
        """
        try:
            gc.collect()
            bank = setting.get_value()
            if bank >= 0 and bank < len(self.pams_workout.banks):
                cfg = self.pams_workout.banks[bank]
                channel.load_settings(cfg)
        except Exception as err:
            print(f"Failed to load channel settings: {err}")
        finally:
            gc.collect()


class PamsWorkout(EuroPiScript):
    """The main script for the Pam's Workout implementation
    """

    def __init__(self):
        super().__init__()

        self.din_mode = Setting("DIN Mode", "din", DIN_MODES, DIN_MODES, False)

        self.clock = MasterClock(120)
        self.channels = [
            PamsOutput(cv1, self.clock, 1),
            PamsOutput(cv2, self.clock, 2),
            PamsOutput(cv3, self.clock, 3),
            PamsOutput(cv4, self.clock, 4),
            PamsOutput(cv5, self.clock, 5),
            PamsOutput(cv6, self.clock, 6),
        ]
        self.clock.add_channels(self.channels)

        ## The master top-level menu
        self.main_menu = PamsMenu(self)

        ## How long ago was _either_ button pressed?
        #
        #  This is used to wake the screensaver up and suppress the normal
        #  button operations while doing so
        self.last_interaction_time = time.ticks_ms()

        default_channel = PamsOutput(None, self.clock, 0)
        ## A set of 8 pre-generated banks for the CV outs
        #
        #  These can be overwritten with the Save command, or loaded with the Load command.
        self.banks = [
            default_channel.to_dict(),
            default_channel.to_dict(),
            default_channel.to_dict(),
            default_channel.to_dict(),
            default_channel.to_dict(),
            default_channel.to_dict(),
            default_channel.to_dict(),
            default_channel.to_dict()
        ]

        @din.handler
        def on_din_rising():
            if self.din_mode.get_value() == DIN_MODE_GATE:
                self.clock.start()
            elif self.din_mode.get_value() == DIN_MODE_RESET:
                for ch in self.channels:
                    ch.reset()
            else:
                if self.clock.is_running:
                    self.clock.stop()
                else:
                    self.clock.start()

        @din.handler_falling
        def on_din_falling():
            if self.din_mode.get_value() == DIN_MODE_GATE:
                self.clock.stop()

        @b1.handler
        def on_b1_press():
            """Handler for pressing button 1

            Button 1 starts/stops the master clock
            """
            if self.clock.is_running:
                self.clock.stop()
            else:
                self.clock.start()

        @b1.handler_falling
        def on_b1_release():
            """Handler for releasing button 1

            Wake up the display if it's asleep.  We do this on release to keep the
            wake up behavior the same for both buttons
            """
            ssoled.notify_user_interaction()


        @b2.handler_falling
        def on_b2_release():
            """Handler for releasing button 2

            Handle long vs short presses differently

            Button 2 is used to cycle between screens

            If the screensaver is visible, just wake up the display & don't process
            the actual button click/long-press
            """
            now = time.ticks_ms()
            if not ssoled.is_screenaver() and not ssoled.is_blank():
                if time.ticks_diff(now, b2.last_pressed()) > LONG_PRESS_MS:
                    # long press
                    # change between the main & sub menus
                    self.main_menu.on_long_press()
                else:
                    # short press
                    self.main_menu.on_click()
                    self.save()

            ssoled.notify_user_interaction()

    def load(self):
        """Load parameters from persistent storage and apply them
        """
        try:
            state = self.load_state_json()

            channel_cfgs = state.get("channels", [])
            for i in range(len(channel_cfgs)):
                self.channels[i].load_settings(channel_cfgs[i])

            clock_cfg = state.get("clock", None)
            if clock_cfg:
                self.clock.load_settings(clock_cfg)

            din_cfg = state.get("din", None)
            if din_cfg:
                self.din_mode.load(din_cfg)

            ain_cfg = state.get("ain", [])
            cv_keys = list(CV_INS.keys())
            for i in range(len(ain_cfg)):
                CV_INS[cv_keys[i]].load_settings(ain_cfg[i])

            self.banks = state.get("banks", self.banks)

        except Exception as err:
            print(f"[ERR ] Error loading saved configuration for PamsWorkout: {err}")
            print("[ERR ] Please delete the storage file and restart the module")

    def save(self):
        """Save current settings to the persistent storage
        """
        state = {
            "clock": self.clock.to_dict(),
            "channels": [
                self.channels[i].to_dict() for i in range(len(self.channels))
            ],
            "din": self.din_mode.to_dict(),
            "ain": [
                CV_INS[cv].to_dict() for cv in CV_INS.keys()
            ],
            "banks": self.banks
        }

        self.save_state_json(state)

    @classmethod
    def display_name(cls):
        return "Pam's Workout"

    def main(self):
        self.load()

        while True:
            now = time.ticks_ms()

            for cv in CV_INS.values():
                cv.update()

            ssoled.fill(0)
            self.main_menu.draw()

            # draw a simple header to indicate status
            if self.clock.is_running:
                imgFB = FrameBuffer(STATUS_IMG_PLAY, STATUS_IMG_WIDTH, STATUS_IMG_HEIGHT, MONO_HLSB)
            else:
                imgFB = FrameBuffer(STATUS_IMG_PAUSE, STATUS_IMG_WIDTH, STATUS_IMG_HEIGHT, MONO_HLSB)
            ssoled.blit(imgFB, OLED_WIDTH - STATUS_IMG_WIDTH, 0)

            ssoled.show()

if __name__=="__main__":
    PamsWorkout().main()
