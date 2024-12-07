#!/usr/bin/env python3
"""A EuroPi clone of ALM's Pamela's NEW Workout

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@year   2023

See pams.md for complete feature list
"""

from europi import *
from europi_script import EuroPiScript

from configuration import *

from experimental.euclid import generate_euclidean_pattern
from experimental.knobs import KnobBank
from experimental.quantizer import CommonScales, Quantizer, SEMITONE_LABELS, SEMITONES_PER_OCTAVE
from experimental.screensaver import OledWithScreensaver
from experimental.settings_menu import *

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
QUANTIZER_NAMES = [
    "None",
    "Chromatic",

    # Major scales
    "Nat Maj",
    "Har Maj",
    "Maj 135",
    "Maj 1356",
    "Maj 1357",

    # Minor scales
    "Nat Min",
    "Har Min",
    "Min 135",
    "Min 1356",
    "Min 1357",

    # Blues scales
    "Maj Blues",
    "Min Blues",

    # Misc
    "Whole",
    "Penta",
    "Dom 7",
]

QUANTIZERS = {
    "None"      : None,
    "Chromatic" : CommonScales.Chromatic,

    # Major scales
    "Nat Maj"   : CommonScales.NatMajor,
    "Har Maj"   : CommonScales.HarMajor,
    "Maj 135"   : CommonScales.Major135,
    "Maj 1356"  : CommonScales.Major1356,
    "Maj 1357"  : CommonScales.Major1357,

    # Minor scales
    "Nat Min"   : CommonScales.NatMinor,
    "Har Min"   : CommonScales.HarMinor,
    "Min 135"   : CommonScales.Minor135,
    "Min 1356"  : CommonScales.Minor1356,
    "Min 1357"  : CommonScales.Minor1357,

    # Blues scales
    "Maj Blues" : CommonScales.MajorBlues,
    "Min Blues" : CommonScales.MinorBlues,

    # Misc
    "Whole"     : CommonScales.WholeTone,
    "Penta"     : CommonScales.Pentatonic,
    "Dom 7"     : CommonScales.Dominant7,
}


## Always-on gate when the clock is running
CLOCK_MOD_RUN = 100

## Short trigger on clock start
CLOCK_MOD_START = 102

## Short trigger on clock stop
CLOCK_MOD_RESET = 103


## Available clock modifiers
CLOCK_MOD_NAMES = [
    "/16",
    "/12",
    "/8",
    "/6",
    "/4",
    "/3",
    "/2",
    "x1",
    "x2",
    "x3",
    "x4",
    "x6",
    "x8",
    "x12",
    "x16",
    "Run",
    "Start",
    "Reset",
]
CLOCK_MULTIPLIERS = {
    "/16": 1/16.0,
    "/12": 1/12.0,
    "/8" : 1/8.0,
    "/6" : 1/6.0,
    "/4" : 1/4.0,
    "/3" : 1/3.0,
    "/2" : 1/2.0,
    "x1" : 1.0,
    "x2" : 2.0,
    "x3" : 3.0,
    "x4" : 4.0,
    "x6" : 6.0,
    "x8" : 8.0,
    "x12": 12.0,
    "x16": 16.0,
    "Run": CLOCK_MOD_RUN,
    "Start": CLOCK_MOD_START,
    "Reset": CLOCK_MOD_RESET,
}
## Some clock mods have graphics
CLOCK_MOD_IMGS = {
    "Run": bytearray(b'\xff\xf0\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00'),    # run gate
    "Start": bytearray(b'\xe0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xbf\xf0'),  # start trigger
    "Reset": bytearray(b'\x03\xf0\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\xfe\x00'),  # reset trigger
}

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
WAVE_SHAPE_LABELS = {
    WAVE_SQUARE: "Square",
    WAVE_TRIANGLE: "Triangle",
    WAVE_SIN: "Sine",
    WAVE_ADSR: "ADSR",
    WAVE_RANDOM: "Random",
    WAVE_AIN: "AIN",
    WAVE_KNOB: "KNOB",
}

## Images of teh wave shapes
#
#  These are 12x12 bitmaps. See:
#  - https://github.com/Allen-Synthesis/EuroPi/blob/main/software/oled_tips.md
#  - https://github.com/novaspirit/img2bytearray
WAVE_SHAPE_IMGS = {
    WAVE_SQUARE: bytearray(b'\xfe\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x83\xf0'),
    WAVE_TRIANGLE: bytearray(b'\x06\x00\x06\x00\t\x00\t\x00\x10\x80\x10\x80 @ @@ @ \x80\x10\x80\x10'),
    WAVE_SIN: bytearray(b'\x10\x00(\x00D\x00D\x00\x82\x00\x82\x00\x82\x10\x82\x10\x01\x10\x01\x10\x00\xa0\x00@'),
    WAVE_ADSR: bytearray(b' \x00 \x000\x000\x00H\x00H\x00G\xc0@@\x80 \x80 \x80\x10\x80\x10'),
    WAVE_RANDOM: bytearray(b'\x00\x00\x08\x00\x08\x00\x14\x00\x16\x80\x16\xa0\x11\xa0Q\xf0Pp`P@\x10\x80\x00'),
    WAVE_AIN: bytearray(b'\x00\x00|\x00|\x00d\x00d\x00g\x80a\x80\xe1\xb0\xe1\xb0\x01\xf0\x00\x00\x00\x00'),
    WAVE_KNOB: bytearray(b'\x06\x00\x19\x80 @@ @ \x80\x10\x82\x10A @\xa0 @\x19\x80\x06\x00'),
}

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

## True/False labels for yes/no settings (e.g. mute)
OK_CANCEL_LABELS = {
    False: "Cancel",
    True: "OK",
}
YES_NO_LABELS = {
    False: "N",
    True: "Y",
}
ON_OFF_LABELS = {
    False: "Off",
    True: "On",
}

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


class AnalogInReader:
    """A wrapper for `ain` that can be shared across multiple Settings

    This allows `ain` to be read once during the main loop, but keep its value across multiple
    accesses across each output channel.  It also adds gain & precision settings that can
    be adjusted in application's menu
    """
    def __init__(self, cv_in):
        self.cv_in = cv_in
        self.last_percent = 0.0

        self.gain = 1.0
        self.precision = DEFAULT_SAMPLES

    def update(self):
        """Read the current voltage from the analog input using the configured precision

        Sets self.last_voltage, which is returned by self.get_value()

        @return The voltage read from the analog input multiplied by self.gain
        """
        self.last_percent = self.cv_in.percent(self.precision) * self.gain
        return self.last_percent

    def percent(self):
        return self.last_percent

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

        self.bpm = SettingMenuItem(
            config_point = IntegerConfigPoint(
                "bpm",
                self.MIN_BPM,
                self.MAX_BPM,
                60
            ),
            prefix="Clk",
            title = "BPM",
            callback = self.recalculate_timer_hz,
        )
        self.reset_on_start = SettingMenuItem(
            config_point = BooleanConfigPoint(
                "reset_on_start",
                True
            ),
            prefix = "Clk",
            title="Stop-Rst",
            labels=ON_OFF_LABELS,
        )

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

            if self.reset_on_start.value:
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
                if ch.clock_mod.value == CLOCK_MOD_RESET:
                    ch.cv_out.voltage(MAX_OUTPUT_VOLTAGE * ch.amplitude.value / 100.0)
                else:
                    ch.cv_out.off()
            time.sleep(0.01)   # time.sleep works in SECONDS not ms
            for ch in self.channels:
                if ch.clock_mod.value == CLOCK_MOD_RESET:
                    ch.cv_out.off()

    def running_time(self):
        """Return how long the clock has been running
        """
        if self.is_running:
            now = time.ticks_ms()
            return time.ticks_diff(now, self.start_time)
        else:
            return 0

    def recalculate_timer_hz(self, new_value=None, old_value=None, config_point=None, arg=None):
        """Callback function for when the BPM changes

        If the timer is currently running deinitialize it and reset it to use the correct BPM
        """
        self.tick_hz = self.bpm.value / 60.0 * self.PPQN

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
        @param n  The CV number 1-6
        """

        self.cv_n = n
        self.out_volts = 0.0
        self.cv_out = cv_out
        self.clock = clock

        ## What quantization are we using?
        #
        #  See contrib.pams.QUANTIZERS
        self.quantizer = SettingMenuItem(
            config_point = ChoiceConfigPoint(
                f"cv{n}_quantizer",
                QUANTIZER_NAMES,
                "None"
            ),
            prefix=f"CV{n}",
            title="Quant.",
            callback = self.update_menu_visibility,
            autoselect_cv = True,
            autoselect_knob = True,
            value_map=QUANTIZERS,
        )

        ## The root of the quantized scale (ignored if quantizer is None)
        self.root = SettingMenuItem(
            config_point = ChoiceConfigPoint(
                f"cv{n}_root",
                list(range(SEMITONES_PER_OCTAVE)),
                0
            ),
            prefix = f"CV{n}",
            title = "Q Root",
            labels = SEMITONE_LABELS
        )

        ## The clock modifier for this channel
        #
        #  - 1.0 is the same as the main clock's BPM
        #  - <1.0 will tick slower than the BPM (e.g. 0.5 will tick once every 2 beats)
        #  - >1.0 will tick faster than the BPM (e.g. 3.0 will tick 3 times per beat)
        self.clock_mod = SettingMenuItem(
            config_point = ChoiceConfigPoint(
                f"cv{n}_mod",
                CLOCK_MOD_NAMES,
                "x1"
            ),
            prefix = f"CV{n}",
            title = "Mod",
            value_map = CLOCK_MULTIPLIERS,
            callback = self.request_clock_mod,
            graphics = CLOCK_MOD_IMGS,
        )

        ## To prevent phase misalignment we use this as the active clock modifier
        #
        #  If clock_mod is changed, we apply it to this when it is safe to do so
        self.real_clock_mod = self.clock_mod.mapped_value

        ## Indicates if clock_mod and real_clock_mod are the same or not
        self.clock_mod_dirty = False

        ## What shape of wave are we generating?
        #
        #  For now, stick to square waves for triggers & gates
        self.wave_shape = SettingMenuItem(
            config_point = ChoiceConfigPoint(
                f"cv{n}_wave",
                WAVE_SHAPES,
                WAVE_SQUARE,
            ),
            prefix = f"CV{n}",
            title = "Wave",
            labels = WAVE_SHAPE_LABELS,
            graphics = WAVE_SHAPE_IMGS,
            callback = self.update_menu_visibility,
        )

        ## The phase offset of the output as a [0, 100] percentage
        self.phase = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_phase",
                0,
                100,
                0
            ),
            prefix = f"CV{n}",
            title = "Phase"
        )

        ## The amplitude of the output as a [0, 100] percentage
        self.amplitude = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_amplitude",
                0,
                100,
                50
            ),
            prefix = f"CV{n}",
            title = "Ampl"
        )

        ## Wave width
        self.width = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_width",
                0,
                100,
                50
            ),
            prefix = f"CV{n}",
            title = "Width"
        )

        ## Euclidean -- number of steps in the pattern (0 = disabled)
        self.e_step = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_e_step",
                0,
                self.MAX_EUCLID_LENGTH,
                0
            ),
            prefix = f"CV{n}",
            title = "EStep",
            callback = self.change_e_length,
        )

        ## Euclidean -- number of triggers in the pattern
        self.e_trig = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_e_trig",
                0,
                self.MAX_EUCLID_LENGTH,
                0
            ),
            prefix = f"CV{n}",
            title = "ETrig",
            callback = self.recalculate_e_pattern,
        )

        ## Euclidean -- rotation of the pattern
        self.e_rot = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_e_rot",
                0,
                self.MAX_EUCLID_LENGTH,
                0
            ),
            prefix = f"CV{n}",
            title = "ERot",
            callback = self.recalculate_e_pattern,
        )

        ## Probability that we skip an output [0-100]
        self.skip = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_skip",
                0,
                100,
                0
            ),
            prefix = f"CV{n}",
            title = "Skip%"
        )

        # ADSR settings
        self.attack = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_attack",
                0,
                100,
                10
            ),
            prefix = f"CV{n}",
            title = "Attack"
        )
        self.decay = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_decay",
                0,
                100,
                10
            ),
            prefix = f"CV{n}",
            title = "Decay"
        )
        self.sustain = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_sustsain",
                0,
                100,
                50
            ),
            prefix = f"CV{n}",
            title = "Sustain"
        )
        self.release = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_release",
                0,
                100,
                50
            ),
            prefix = f"CV{n}",
            title = "Release"
        )

        ## Swing percentage
        #
        #  50% -> even, no swing
        #  <50% -> short-long-short-long-...
        #  >50% -> long-short-long-short-...
        self.swing = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"cv{n}_swing",
                0,
                100,
                50
            ),
            prefix = f"CV{n}",
            title = "Swing%"
        )

        ## Allows muting a channel during runtime
        #
        #  A muted channel can still be edited
        self.mute = SettingMenuItem(
            config_point = BooleanConfigPoint(
                f"cv{n}_mute",
                False
            ),
            prefix = f"CV{n}",
            title="Mute",
            labels = YES_NO_LABELS
        )

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

    def update_menu_visibility(self, new_value=None, old_value=None, config_point=None, arg=None):
        """Callback function for changing the visibility of menu items

        @param sender  The Setting object that called this function
        @param args    The callback arguments passed from the Setting
        """

        # hide the ADSR settings if we're not in ADSR mode
        wave_shape = self.wave_shape.value
        show_adsr = wave_shape == WAVE_ADSR
        self.attack.is_visible = show_adsr
        self.decay.is_visible = show_adsr
        self.sustain.is_visible = show_adsr
        self.release.is_visible = show_adsr

        # hide the quantization root if we're not quantizing
        show_root = self.quantizer.mapped_value is not None
        self.root.is_visible = show_root

        # hide the width parameter if we're reading from AIN or KNOB, or outputting a sine wave
        show_width = wave_shape != WAVE_AIN and wave_shape != WAVE_KNOB and wave_shape != WAVE_SIN
        self.width.is_visible = show_width

    def change_e_length(self, new_value=None, old_value=None, config_point=None, arg=None):
        self.e_trig.modify_choices(list(range(self.e_step.value+1)), self.e_step.value)
        self.e_rot.modify_choices(list(range(self.e_step.value+1)), self.e_step.value)
        self.recalculate_e_pattern()

    def request_clock_mod(self, new_value=None, old_value=None, config_point=None, arg=None):
        self.clock_mod_dirty = True

    def change_clock_mod(self):
        self.real_clock_mod = self.clock_mod.mapped_value
        self.clock_mod_dirty = False

    def recalculate_e_pattern(self, new_value=None, old_value=None, config_point=None, arg=None):
        """Recalulate the euclidean pattern this channel outputs
        """
        # always assume we're doing some kind of euclidean pattern
        e_pattern = [1]
        if self.e_step.value > 0:
            e_pattern = generate_euclidean_pattern(self.e_step.value, self.e_trig.value, self.e_rot.value)

        self.next_e_pattern = e_pattern

    def square_wave(self, tick, n_ticks):
        """Calculate the [0, 1] value of a square wave with PWM

        @param tick  The current tick, in the range [0, n_ticks)
        @param n_ticks  The number of ticks in which the wave must complete

        @return A value in the range [0, 1] indicating the height of the wave at this tick
        """
        # the first part of the square wave is on, the last part is off
        # cutoff depends on the duty-cycle/pulse width
        duty_cycle = n_ticks * self.width.value / 100.0

        # because of phase offset the wave _can_ start at e.g. 75% of the ticks and end at the following window's 25%
        start_tick = self.phase.value * n_ticks / 100.0
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
        rising_ticks = round(n_ticks * self.width.value / 100.0)
        falling_ticks = n_ticks - rising_ticks
        peak = 1.0
        y = 0.0

        tick = int(tick + self.phase.value * n_ticks / 100.0) % n_ticks

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
        theta = (tick + self.phase.value / 100.0 * n_ticks) / n_ticks * 2 * math.pi  # covert the tick to radians
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
        tick = int(tick + self.phase.value * n_ticks / 100.0) % n_ticks

        # the ADSR envelope only lasts for n_ticks * width%, so reduce the size of the window for further calculations
        n_ticks = int(n_ticks * self.width.value / 100.0)

        attack_ticks = int(n_ticks * self.attack.value / 100.0)
        decay_ticks = int((n_ticks - attack_ticks) * self.decay.value / 100.0)
        release_ticks = int((n_ticks - decay_ticks - attack_ticks) * self.release.value / 100.0)
        sustain_ticks = n_ticks - attack_ticks - decay_ticks - release_ticks
        sustain_level = self.sustain.value / 100.0

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
                out_volts = MAX_OUTPUT_VOLTAGE * self.amplitude.value / 100.0
            else:
                out_volts = 0.0
        elif self.real_clock_mod == CLOCK_MOD_RUN:
            out_volts = MAX_OUTPUT_VOLTAGE * self.amplitude.value / 100.0
        elif self.real_clock_mod == CLOCK_MOD_RESET:
            # reset waves are always low; the clock's stop() function handles triggering them
            out_volts = 0.0
        else:
            if self.wave_counter % 2 == 0:
                # first half of the swing; if swing < 50% this is short, otherwise long
                swing_amt = self.swing.value / 100.0
            else:
                # second half of the swing; if swing < 50% this is long, otherwise short
                swing_amt = (100 - self.swing.value) / 100.0
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
            rising_edge = (wave_position == int(self.phase.value * ticks_per_note / 100.0)) and e_step
            # determine if we should skip this sample playback
            if rising_edge:
                self.skip_this_step = random.randint(0, 100) < self.skip.value
                self.wave_counter += 1

            wave_sample = int(e_step) * int (not self.skip_this_step)
            if self.wave_shape.value == WAVE_RANDOM:
                if rising_edge and not self.skip_this_step:
                    wave_sample = random.random() * (self.amplitude.value / 100.0) + (self.width.value / 100.0)
                else:
                    wave_sample = self.previous_wave_sample
            elif self.wave_shape.value == WAVE_AIN:
                if rising_edge and not self.skip_this_step:
                    wave_sample = CV_INS["AIN"].percent() * self.amplitude.value / 100.0
                else:
                    wave_sample = self.previous_wave_sample
            elif self.wave_shape.value == WAVE_KNOB:
                if rising_edge and not self.skip_this_step:
                    wave_sample = CV_INS["KNOB"].percent() * self.amplitude.value / 100.0
                else:
                    wave_sample = self.previous_wave_sample
            elif self.wave_shape.value == WAVE_SQUARE:
                wave_sample = wave_sample * self.square_wave(wave_position, ticks_per_note) * (self.amplitude.value / 100.0)
            elif self.wave_shape.value == WAVE_TRIANGLE:
                wave_sample = wave_sample * self.triangle_wave(wave_position, ticks_per_note) * (self.amplitude.value / 100.0)
            elif self.wave_shape.value == WAVE_SIN:
                wave_sample = wave_sample * self.sine_wave(wave_position, ticks_per_note) * (self.amplitude.value / 100.0)
            elif self.wave_shape.value == WAVE_ADSR:
                wave_sample = wave_sample * self.adsr_wave(wave_position, ticks_per_note) * (self.amplitude.value / 100.0)
            else:
                wave_sample = 0.0

            self.previous_wave_sample = wave_sample
            out_volts = wave_sample * MAX_OUTPUT_VOLTAGE

            if self.quantizer.mapped_value is not None:
                (out_volts, note) = self.quantizer.mapped_value.quantize(out_volts, self.root.value)

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
        if self.mute.value:
            self.cv_out.off()
        else:
            self.cv_out.voltage(self.out_volts)


class PamsWorkout2(EuroPiScript):
    """The main script for the Pam's Workout implementation
    """

    def __init__(self):
        super().__init__()

        self.din_mode = SettingMenuItem(
            config_point = ChoiceConfigPoint(
                "din",
                DIN_MODES,
                DIN_MODE_GATE
            ),
            prefix = "Clk",
            title = "DIN Mode"
        )

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

        # Create the main menu
        menu_items = [
            self.clock.bpm
        ]
        self.clock.bpm.add_child(self.din_mode)
        self.clock.bpm.add_child(self.clock.reset_on_start)
        for ch in self.channels:
            ch.clock_mod.add_child(ch.wave_shape)
            ch.clock_mod.add_child(ch.width)
            ch.clock_mod.add_child(ch.amplitude)
            ch.clock_mod.add_child(ch.phase)
            ch.clock_mod.add_child(ch.attack)
            ch.clock_mod.add_child(ch.decay)
            ch.clock_mod.add_child(ch.sustain)
            ch.clock_mod.add_child(ch.release)
            ch.clock_mod.add_child(ch.skip)
            ch.clock_mod.add_child(ch.e_step)
            ch.clock_mod.add_child(ch.e_trig)
            ch.clock_mod.add_child(ch.e_rot)
            ch.clock_mod.add_child(ch.swing)
            ch.clock_mod.add_child(ch.quantizer)
            ch.clock_mod.add_child(ch.root)
            ch.clock_mod.add_child(ch.mute)

            # TODO: add menu items to load/save banks

            # add the channel to the menu items
            menu_items.append(ch.clock_mod)

        # TODO: re-add AIN, K1 gains?
        # This feels unnecessary with the menu handling the dynamic inputs internally

        ## The main application menu
        self.main_menu = SettingsMenu(
            menu_items = menu_items,
            navigation_button = b2,
            navigation_knob = k2_bank,
            autoselect_cv = CV_INS["AIN"],
            autoselect_knob = CV_INS["KNOB"],
            short_press_cb = lambda: ssoled.notify_user_interaction(),
            long_press_cb = lambda: ssoled.notify_user_interaction()
        )
        self.main_menu.load_defaults(self._state_filename)

        # TODO: load the saved banks from storage

        @din.handler
        def on_din_rising():
            if self.din_mode.value == DIN_MODE_GATE:
                self.clock.start()
            elif self.din_mode.value == DIN_MODE_RESET:
                for ch in self.channels:
                    ch.reset()
            else:
                if self.clock.is_running:
                    self.clock.stop()
                else:
                    self.clock.start()

        @din.handler_falling
        def on_din_falling():
            if self.din_mode.value == DIN_MODE_GATE:
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

    def main(self):
        while True:
            for cv_in in CV_INS.values():
                cv_in.update()

            ssoled.fill(0)
            self.main_menu.draw(ssoled)
            if self.main_menu.settings_dirty:
                self.main_menu.save(self._state_filename)

            # draw a simple header to indicate status
            if self.clock.is_running:
                imgFB = FrameBuffer(STATUS_IMG_PLAY, STATUS_IMG_WIDTH, STATUS_IMG_HEIGHT, MONO_HLSB)
            else:
                imgFB = FrameBuffer(STATUS_IMG_PAUSE, STATUS_IMG_WIDTH, STATUS_IMG_HEIGHT, MONO_HLSB)
            ssoled.blit(imgFB, OLED_WIDTH - STATUS_IMG_WIDTH, 0)

            ssoled.show()

if __name__=="__main__":
    PamsWorkout2().main()
