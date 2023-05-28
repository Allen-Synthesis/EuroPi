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
from experimental.quantizer import CommonScales, Quantizer
from experimental.screensaver import Screensaver

from collections import OrderedDict
from machine import Timer

import math
import time
import random

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
    ["x16", 16.0]
])

## Sorted list of labels for the clock modifers to display
CLOCK_MOD_LABELS = list(CLOCK_MODS.keys())

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

## Random wave
#
#  Width is ignored
WAVE_RANDOM = 3

## Reset gate
#
#  Turns on when the clock stops
WAVE_RESET = 4

## Start trigger
#
#  Turns on once when the clock starts
WAVE_START = 5

## Gate, on while the clock is running and
#  off when the clock stops
WAVE_RUN = 6

## Use raw AIN as the direct input
#
#  This lets you effectively use Pam's as a quantizer for
#  the AIN signal
WAVE_AIN = 7

## Available wave shapes
WAVE_SHAPES = [
    WAVE_SQUARE,
    WAVE_TRIANGLE,
    WAVE_SIN,
    WAVE_RANDOM,
    WAVE_RESET,
    WAVE_START,
    WAVE_RUN,
    WAVE_AIN
]

## Ordered list of labels for the wave shape chooser menu
WAVE_SHAPE_LABELS = [
    "Square",
    "Triangle",
    "Sine",
    "Random",
    "Reset",
    "Start",
    "Run",
    "AIN"
]

## Sorted list of wave shapes to display
#
#  Same order as WAVE_SHAPE_LABELS
#
#  These are 12x12 bitmaps. See:
#  - https://github.com/Allen-Synthesis/EuroPi/blob/main/software/oled_tips.md
#  - https://github.com/novaspirit/img2bytearray
WAVE_SHAPE_IMGS = [
    bytearray(b'\xfe\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x83\xf0'),
    bytearray(b'\x06\x00\x06\x00\t\x00\t\x00\x10\x80\x10\x80 @ @@ @ \x80\x10\x80\x10'),
    bytearray(b'\x10\x00(\x00D\x00D\x00\x82\x00\x82\x00\x82\x10\x82\x10\x01\x10\x01\x10\x00\xa0\x00@'),
    bytearray(b'\x00\x00\x08\x00\x08\x00\x14\x00\x16\x80\x16\xa0\x11\xa0Q\xf0Pp`P@\x10\x80\x00'),
    bytearray(b'\x03\xf0\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x00\xfe\x00'),
    bytearray(b'\xe0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xa0\x00\xbf\xf0'),
    bytearray(b'\xff\xf0\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00'),
    bytearray(b'\x00\x00|\x00|\x00d\x00d\x00g\x80a\x80\xe1\xb0\xe1\xb0\x01\xf0\x00\x00\x00\x00')
]

STATUS_IMG_LOCK = bytearray(b'\x06\x00\x19\x80\x19\x80`@`@`@\xff\xf0\xf9\xf0\xf9\xf0\xfd\xf0\xff\xf0\xff\xf0')
STATUS_IMG_PLAY = bytearray(b'\x00\x00\x18\x00\x18\x00\x1c\x00\x1c\x00\x1e\x00\x1f\x80\x1e\x00\x1e\x00\x1c\x00\x18\x00\x18\x00')
STATUS_IMG_PAUSE = bytearray(b'\x00\x00y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0y\xc0')

STATUS_IMG_WIDTH = 12
STATUS_IMG_HEIGHT = 12

## Duration before we activate the screensaver
SCREENSAVER_TIMEOUT_MS = 1000 * 60 * 5

## Duration before we blank the screen
BLANK_TIMEOUT_MS = 1000 * 60 * 20

## Do we use gate input on din to turn the module on/off
DIN_MODE_GATE = 'Gate'

## Do we toggle the module on/off with a trigger on din?
DIN_MODE_TRIGGER = 'Trig'

## Reset on a rising edge, but don't start/stop the clock
DIN_MODE_RESET = 'Reset'

DIN_MODES = [
    DIN_MODE_GATE,
    DIN_MODE_TRIGGER,
    DIN_MODE_RESET
]

class Setting:
    """A single setting that can be loaded, saved, or dynamically read from an analog input
    """
    def __init__(self, display_name, storage_name, display_options, options, allow_cv_in=True, on_change_fn=None, value_dict=None, default_value=None):
        self.display_name = display_name
        self.display_options = [o for o in display_options]

        self.on_change_fn = on_change_fn

        self.storage_name = storage_name
        self.options = [o for o in options]

        self.allow_cv_in = allow_cv_in
        if allow_cv_in:
            for cv in CV_INS.keys():
                self.display_options.append(cv)
                self.options.append(CV_INS[cv])

        self.value_dict = value_dict
        if default_value is not None:
            self.choice = self.options.index(default_value)
        else:
            self.choice = 0

    def __str__(self):
        return self.display_name

    def __len__(self):
        return len(self.options)

    def load(self, settings):
        if "value" in settings.keys():
            self.choice = settings["value"]

    def to_dict(self):
        return {
            "value": self.choice
        }

    def update_options(self, display_options, options):
        if self.choice >= len(options):
            self.choice = len(options)-1

        self.display_options = []
        for o in display_options:
            self.display_options.append(o)
        self.options = []
        for o in options:
            self.options.append(o)

        if self.allow_cv_in:
            for cv in CV_INS.keys():
                self.display_options.append(cv)
                self.options.append(CV_INS[cv])

    def get_value(self):
        if type(self.options[self.choice]) is AnalogInReader:
            n = round(self.options[self.choice].get_value() / MAX_INPUT_VOLTAGE * len(self.options) - len(CV_INS)) # remo
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
            self.on_change_fn()

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
        self.precision = Setting("Precision", "precision", ["Low", "Med", "High"], [int(DEFAULT_SAMPLES/2), DEFAULT_SAMPLES, int(DEFAULT_SAMPLES*2)], allow_cv_in=False, default_value=DEFAULT_SAMPLES)

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
        self.last_voltage = self.cv_in.read_voltage(self.precision.get_value()) * self.gain.get_value() / 100.0
        return self.last_voltage

    def get_value(self):
        return self.last_voltage

## Wrapped copies of all CV inputs so we can iterate through them
CV_INS = {
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
    MAX_BPM = 300

    def __init__(self, bpm):
        """Create the main clock to run at a given bpm
        @param bpm  The initial BPM to run the clock at
        """

        self.channels = []
        self.is_running = False

        self.bpm = Setting("BPM", "bpm", list(range(self.MIN_BPM, self.MAX_BPM+1)), list(range(self.MIN_BPM, self.MAX_BPM+1)), on_change_fn=self.recalculate_timer_hz, default_value=60)
        self.reset_on_start = Setting("Stop-Rst", "reset_on_start", ["On", "Off"], [True, False], False)

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
            self.elapsed_pulses = 0

            if self.reset_on_start.get_value():
                for ch in self.channels:
                    ch.reset()

            self.timer.init(freq=self.tick_hz, mode=Timer.PERIODIC, callback=self.on_tick)

    def stop(self):
        """Stop the timer
        """
        if self.is_running:
            self.is_running = False
            self.timer.deinit()

            # Fire a reset trigger on any channels that have the WAVE_RESET mode set
            # This trigger lasts 10ms
            # Turn all other channels off so we don't leave hot wires
            for ch in self.channels:
                if ch.wave_shape == WAVE_RESET:
                    ch.cv_out.voltage(MAX_OUTPUT_VOLTAGE * ch.amplitude / 100.0)
                else:
                    ch.cv_out.voltage(0.0)
            time.sleep(0.01)   # time.sleep works in SECONDS not ms
            for ch in self.channels:
                if ch.wave_shape == WAVE_RESET:
                    ch.cv_out.voltage(0)

    def running_time(self):
        """Return how long the clock has been running
        """
        if self.is_running:
            now = time.ticks_ms()
            return time.ticks_diff(now, self.start_time)
        else:
            return 0

    def recalculate_timer_hz(self):
        """Recalculate the frequency of the inner timer

        If the timer is currently running deinitialize it and reset it to use the correct BPM
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

    ## Minimum duration of a WAVE_START trigger
    #
    #  The actual length depends on clock rate and PPQN, and may be longer than this
    TRIGGER_LENGTH_MS = 10

    def __init__(self, cv_out, clock):
        """Create a new output to control a single cv output

        @param cv_out  One of the six output jacks
        @param clock  The MasterClock that controls the timing of this output
        """

        self.out_volts = 0.0
        self.cv_out = cv_out
        self.clock = clock

        ## What quantization are we using?
        #
        #  See contrib.pams.QUANTIZERS
        self.quantizer = Setting("Quant.", "quantizer", QUANTIZER_LABELS, QUANTIZER_LABELS, value_dict=QUANTIZERS)

        ## The clock modifier for this channel
        #
        #  - 1.0 is the same as the main clock's BPM
        #  - <1.0 will tick slower than the BPM (e.g. 0.5 will tick once every 2 beats)
        #  - >1.0 will tick faster than the BPM (e.g. 3.0 will tick 3 times per beat)
        self.clock_mod = Setting("Mod", "clock_mod", CLOCK_MOD_LABELS, CLOCK_MOD_LABELS, value_dict=CLOCK_MODS, default_value="x1")

        ## What shape of wave are we generating?
        #
        #  For now, stick to square waves for triggers & gates
        self.wave_shape = Setting("Wave", "wave", WAVE_SHAPE_LABELS, WAVE_SHAPES, default_value=WAVE_SQUARE, allow_cv_in=False)

        ## The phase offset of the output as a [0, 100] percentage
        self.phase = Setting("Phase", "phase", list(range(101)), list(range(101)), default_value=0)

        ## The amplitude of the output as a [0, 100] percentage
        self.amplitude = Setting("Ampl.", "ampl", list(range(101)), list(range(101)), default_value=50)

        ## Wave width
        self.width = Setting("Width", "width", list(range(101)), list(range(101)), default_value=50)

        ## Euclidean -- number of steps in the pattern (0 = disabled)
        self.e_step = Setting("EStep", "e_step", list(range(self.MAX_EUCLID_LENGTH+1)), list(range(self.MAX_EUCLID_LENGTH)), on_change_fn=self.change_e_length, default_value=0)

        ## Euclidean -- number of triggers in the pattern
        self.e_trig = Setting("ETrig", "e_trig", list(range(self.MAX_EUCLID_LENGTH+1)), list(range(self.MAX_EUCLID_LENGTH)), on_change_fn=self.recalculate_e_pattern, default_value=0)

        ## Euclidean -- rotation of the pattern
        self.e_rot = Setting("ERot", "e_rot", list(range(self.MAX_EUCLID_LENGTH+1)), list(range(self.MAX_EUCLID_LENGTH)), on_change_fn=self.recalculate_e_pattern, default_value=0)

        ## Probability that we skip an output [0-100]
        self.skip = Setting("Skip%", "skip", list(range(101)), list(range(101)), default_value=0)

        ## The position we're currently playing inside playback_pattern
        #
        #  This increments once every tick
        #  In prior revisions we pre-calculated the entire waveform, but that resulted in too much RAM overhead
        #  so instead we dynamically calculate the waveshape
        self.sample_position = 0

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
            "quantizer" : self.quantizer.to_dict()
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

        self.change_e_length()

    def change_e_length(self):
        self.e_trig.update_options(list(range(self.e_step.get_value()+1)), list(range(self.e_step.get_value()+1)))
        self.e_rot.update_options(list(range(self.e_step.get_value()+1)), list(range(self.e_step.get_value()+1)))
        self.recalculate_e_pattern()

    def recalculate_e_pattern(self):
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

    def reset(self):
        """Reset the current output to the beginning
        """
        self.e_position = 0
        if self.next_e_pattern:
            self.e_pattern = self.next_e_pattern
            self.next_e_pattern = None

        self.sample_position = 0

    def tick(self):
        """Advance the current pattern one tick and calculate the output voltage

        Call apply() to actually send the voltage. This lets us calculate all output channels and THEN set the
        outputs after so they're more synchronized
        """
        if self.wave_shape.get_value() == WAVE_START:
            # start waves are weird; they're only on during the first 10ms or 1 PPQN (whichever is longer)
            # and are otherwise always off
            gate_len = self.clock.running_time()
            if self.clock.elapsed_pulses == 0 or gate_len <= self.TRIGGER_LENGTH_MS:
                out_volts = MAX_OUTPUT_VOLTAGE * self.amplitude.get_value() / 100.0
            else:
                out_volts = 0.0
        elif self.wave_shape.get_value() == WAVE_RUN:
            out_volts = MAX_OUTPUT_VOLTAGE * self.amplitude.get_value() / 100.0
        elif self.wave_shape.get_value() == WAVE_RESET:
            # reset waves are always low; the clock's stop() function handles triggering them
            out_volts = 0.0
        else:
            ticks_per_note = round(MasterClock.PPQN / self.clock_mod.get_value())
            e_step = self.e_pattern[self.e_position]
            wave_position = self.sample_position
            # are we starting a new repeat of the pattern?
            rising_edge = wave_position == int(self.phase.get_value() * ticks_per_note / 100.0) and e_step
            # determine if we should skip this sample playback
            if rising_edge:
                self.skip_this_step = random.randint(0, 100) < self.skip.get_value()

            wave_sample = int(e_step) * int (not self.skip_this_step)
            if self.wave_shape.get_value() == WAVE_RANDOM:
                if rising_edge and not self.skip_this_step:
                    wave_sample = random.random() * (self.amplitude.get_value() / 100.0) + (self.width.get_value() / 100.0)
                else:
                    wave_sample = self.previous_wave_sample
            elif self.wave_shape.get_value() == WAVE_AIN:
                if rising_edge and not self.skip_this_step:
                    wave_sample = CV_INS["AIN"].get_value() / MAX_OUTPUT_VOLTAGE
                else:
                    wave_sample = self.previous_wave_sample
            elif self.wave_shape.get_value() == WAVE_SQUARE:
                wave_sample = wave_sample * self.square_wave(wave_position, ticks_per_note) * (self.amplitude.get_value() / 100.0)
            elif self.wave_shape.get_value() == WAVE_TRIANGLE:
                wave_sample = wave_sample * self.triangle_wave(wave_position, ticks_per_note) * (self.amplitude.get_value() / 100.0)
            elif self.wave_shape.get_value() == WAVE_SIN:
                wave_sample = wave_sample * self.sine_wave(wave_position, ticks_per_note) * (self.amplitude.get_value() / 100.0)

            self.previous_wave_sample = wave_sample
            out_volts = wave_sample * MAX_OUTPUT_VOLTAGE

            if self.quantizer.get_value() is not None:
                (out_volts, note) = self.quantizer.get_value().quantize(out_volts)

            # increment the position within each playback pattern
            # if we've queued a new euclidean pattern apply it now so we
            # can start playing them on the next tick
            self.sample_position = self.sample_position +1
            if self.sample_position >= ticks_per_note:
                self.sample_position = 0

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

        self.out_volts = out_volts

    def apply(self):
        """Apply the calculated voltage to the output channel
        """
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

        The OLED must be cleared before calling this function. You must call oled.show() after
        calling this function
        """

        text_left = 0
        prefix_left = 1
        prefix_right = len(self.prefix)*CHAR_WIDTH
        title_left = len(self.prefix)*CHAR_WIDTH + 4

        # If we're in a top-level menu the submenu is non-empty. In that case, the prefix in inverted text
        # Otherwise, the title in inverted text to indicate we're in the sub-menu
        if len(self.submenu) != 0:
            oled.fill_rect(prefix_left-1, 0, prefix_right+1, CHAR_HEIGHT+2, 1)
            oled.text(self.prefix, prefix_left, 1, 0)
            oled.text(str(self.setting), title_left, 1, 1)
        else:
            oled.fill_rect(title_left-1, 0, len(str(self.setting))*CHAR_WIDTH+2, CHAR_HEIGHT+2, 1)
            oled.text(self.prefix, prefix_left, 1, 1)
            oled.text(str(self.setting), title_left, 1, 0)

        if self.option_gfx is not None:
            # draw the option thumbnail to the screen
            text_left = 14
            if self.is_writable:
                img = k2.choice(self.option_gfx)
            else:
                key = self.setting.get_value()
                img = self.option_gfx[key]
            imgFB = FrameBuffer(img, 12, 12, MONO_HLSB)
            oled.blit(imgFB, 0, SELECT_OPTION_Y)


        if self.is_writable:
            # draw the selection in inverted text
            selected_item = k2.choice(self.setting.display_options)
            choice_text = f"{selected_item}"
            text_width = len(choice_text)*CHAR_WIDTH

            oled.fill_rect(text_left, SELECT_OPTION_Y, text_left+text_width+3, CHAR_HEIGHT+4, 1)
            oled.text(choice_text, text_left+1, SELECT_OPTION_Y+2, 0)
        else:
            # draw the selection in normal text
            choice_text = f"{self.setting.get_display_value()}"
            oled.text(choice_text, text_left+1, SELECT_OPTION_Y+2, 1)


    def on_click(self):
        if self.is_writable:
            self.set_editable(False)
            selected_index = k2.choice(list(range(len(self.setting))))
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
            self.items.append(SettingChooser(prefix, ch.clock_mod, None, [
                SettingChooser(prefix, ch.wave_shape, WAVE_SHAPE_IMGS),
                SettingChooser(prefix, ch.width),
                SettingChooser(prefix, ch.phase),
                SettingChooser(prefix, ch.amplitude),
                SettingChooser(prefix, ch.skip),
                SettingChooser(prefix, ch.e_step),
                SettingChooser(prefix, ch.e_trig),
                SettingChooser(prefix, ch.e_rot),
                SettingChooser(prefix, ch.quantizer)
            ]))
        for ch in CV_INS.keys():
            self.items.append(SettingChooser(ch, CV_INS[ch].gain, None, [
                SettingChooser(ch, CV_INS[ch].precision)
            ]))

        self.active_items = self.items

        ## The item we're actually drawing to the screen _right_now_
        self.visible_item = self.pams_workout.k1_bank.current.choice(self.active_items)

    def on_long_press(self):
        # return the active item to the read-only state
        self.visible_item.set_editable(False)

        # toggle between the two menu levels
        if self.active_items == self.items:
            self.active_items = self.visible_item.submenu
        else:
            self.active_items = self.items

    def on_click(self):
        self.visible_item.on_click()

    def draw(self):
        if not self.visible_item.is_editable():
            self.visible_item = self.pams_workout.k1_bank.current.choice(self.active_items)

        self.visible_item.draw()

class SplashScreen:
    """A splash screen we show during startup
    """
    def draw(self):
        """Draw the splash screen to the OLED

        Layout looks like this, where % indicates the EuroPi logo:
        ```
        +-------------------+
        | %%% Pam's Workout |
        | %%%               |
        +-------------------+
        ```
        """
        logo = bytearray(b"\x00\x01\xf0\x00\x00\x02\x08\x00\x00\x04\x04\x00\x03\xc4\x04\x00\x0c$\x02\x00\x10\x14\x01\x00\x10\x0b\xc0\x80 \x04\x00\x80A\x8a|\x80FJC\xc0H\x898\x00S\x08\x87\x00d\x08\x00\xc0X\x08p #\x88H L\xb8& \x91P\x11 \xa6\x91\x08\xa0\xc9\x12\x84`\x12\x12C\x00$\x11 \x80H\x0c\x90\x80@\x12\x88\x80 \x12F\x80\x10\x10A\x00\x10  \x00\x08  \x00\x04@@\x00\x02\x00\x80\x00\x01\x01\x00\x00\x00\xc6\x00\x00\x008\x00\x00")
        LOGO_WIDTH = 27
        LOGO_HEIGHT = 32

        # clear the screen
        oled.fill(0)

        # put the EuroPi leaf graphic on the side
        imgFB = FrameBuffer(logo, LOGO_WIDTH, LOGO_HEIGHT, MONO_HLSB)
        oled.blit(imgFB, 0, 0)

        oled.text("Pam's Workout", LOGO_WIDTH+2, 8)
        oled.show()

class PamsWorkout(EuroPiScript):
    """The main script for the Pam's Workout implementation
    """
    def __init__(self):
        super().__init__()

        self.din_mode = Setting("DIN Mode", "din", DIN_MODES, DIN_MODES, False)

        self.k1_bank = (
            KnobBank.builder(k1)
            .with_unlocked_knob("lvl_1")
            .with_locked_knob("lvl_2", initial_percentage_value=0)
            .build()
        )

        self.clock = MasterClock(120)
        self.channels = [
            PamsOutput(cv1, self.clock),
            PamsOutput(cv2, self.clock),
            PamsOutput(cv3, self.clock),
            PamsOutput(cv4, self.clock),
            PamsOutput(cv5, self.clock),
            PamsOutput(cv6, self.clock),
        ]
        self.clock.add_channels(self.channels)

        ## The master top-level menu
        self.main_menu = PamsMenu(self)

        ## The screensaver
        self.screensaver = Screensaver()

        ## How long ago was _either_ button pressed?
        #
        #  This is used to wake the screensaver up and suppress the normal
        #  button operations while doing so
        self.last_interaction_time = time.ticks_ms()

        @din.handler
        def on_din_rising():
            if self.din_mode == DIN_MODE_GATE:
                self.clock.start()
            elif self.din_mode == DIN_MODE_RESET:
                for ch in self.channels:
                    ch.reset()
            else:
                if self.clock.is_running:
                    self.clock.stop()
                else:
                    self.clock.start()

        @din.handler_falling
        def on_din_falling():
            if self.din_mode == DIN_MODE_GATE:
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
            self.last_interaction_time = time.ticks_ms()


        @b2.handler_falling
        def on_b2_release():
            """Handler for releasing button 2

            Handle long vs short presses differently

            Button 2 is used to cycle between screens

            If the screensaver is visible, just wake up the display & don't process
            the actual button click/long-press
            """
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_interaction_time) <= SCREENSAVER_TIMEOUT_MS:
                if time.ticks_diff(now, b2.last_pressed()) > LONG_PRESS_MS:
                    # long press
                    # change between the main & sub menus
                    self.k1_bank.next()
                    self.main_menu.on_long_press()
                else:
                    # short press
                    self.main_menu.on_click()
                    self.save()

            self.last_interaction_time = now

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

        except:
            print("[ERR ] Error loading saved configuration for PamsWorkout")
            print("[ERR ] Please delete the storage file and restart the module")

    def save(self):
        """Save current settings to the persistent storage
        """
        state = {
            "clock": self.clock.to_dict(),
            "channels": [],
            "din": self.din_mode.to_dict(),
            "ain": []
        }
        for i in range(len(self.channels)):
            state["channels"].append(self.channels[i].to_dict())
        for cv in CV_INS.keys():
            state["ain"].append(CV_INS[cv].to_dict())

        self.save_state_json(state)

    @classmethod
    def display_name(cls):
        return "Pam's Workout"

    def main(self):
        SplashScreen().draw()

        self.load()

        time.sleep(1.5)

        while True:
            now = time.ticks_ms()

            for cv in CV_INS.values():
                cv.update()

            elapsed_time = time.ticks_diff(now, self.last_interaction_time)
            if elapsed_time > BLANK_TIMEOUT_MS:
                self.screensaver.draw_blank()
            elif elapsed_time > SCREENSAVER_TIMEOUT_MS:
                self.screensaver.draw()
            else:
                oled.fill(0)
                self.main_menu.draw()

                # draw a simple header to indicate status
                if self.clock.is_running:
                    imgFB = FrameBuffer(STATUS_IMG_PLAY, STATUS_IMG_WIDTH, STATUS_IMG_HEIGHT, MONO_HLSB)
                else:
                    imgFB = FrameBuffer(STATUS_IMG_PAUSE, STATUS_IMG_WIDTH, STATUS_IMG_HEIGHT, MONO_HLSB)
                oled.blit(imgFB, OLED_WIDTH - STATUS_IMG_WIDTH, 0)

                oled.show()

if __name__=="__main__":
    PamsWorkout().main()
