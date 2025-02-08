#!/usr/bin/env python3
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
"""Gaussian-based, clocked, quantized CV generator

Inspired by Magnetic Freak's Gaussian module.

@author  Chris Iverach-Brereton
@year    2024
"""

from europi import *
from europi_script import EuroPiScript

import configuration
import time

from experimental.bisect import bisect_left
from experimental.knobs import *
from experimental.random_extras import normal
from experimental.screensaver import Screensaver


class OutputBin:
    """Generic class for different output modes"""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def closest(self, v):
        """Abstract function to be implemented by subclasses

        @param v  The input voltage to assign to a bin
        """
        raise Exception("Not implemented")


class ContinuousBin(OutputBin):
    """Smooth, continuous output"""
    def __init__(self, name):
        super().__init__(name)

    def closest(self, v):
        return v


class VoltageBin(OutputBin):
    """Quantizes a random voltage to the closest bin"""
    def __init__(self, name, bins):
        """Create a new set of bins

        @param name  The human-readable display name for this set of bins
        @param bins  A list of voltages we are allowed to output
        """
        super().__init__(name)
        self.bins = [float(b) for b in bins]
        self.bins.sort()

    def closest(self, v):
        """Quantize an input voltage to the closest bin. If two bins are equally close, choose the lower one.

        Our internal bins are sorted, so we can do a binary search for that sweet, sweet O(log(n)) efficiency

        @param v  A voltage in the range 0-10 to quantize
        @return   The closest voltage bin to @v
        """
        i = bisect_left(self.bins, v)
        if i == 0:
            return self.bins[0]
        if i == len(self.bins):
            return self.bins[-1]
        prev = self.bins[i - 1]
        next = self.bins[i + 1]
        if abs(v - next) < abs(v - prev):
            return next
        else:
            return prev


class DelayedOutput:
    """A class that handles setting a CV output on or after a given tick"""

    # We're not currently queued to do any output
    STATE_IDLE = 0

    # We've been assigned a time in the future to set the voltage
    STATE_WAITING = 1

    # The voltage has been applied and the gate is currently high
    STATE_GATE_HIGH = 2

    def __init__(self, cv, gate):
        """Create a new delayed output manager

        @param cv                The output for CV voltage
        @param gate              The output for a gate voltage
        """
        self.cv = cv
        self.gate = gate
        self.state = self.STATE_IDLE

        self.gate_high_tick = time.ticks_ms()
        self.gate_low_tick = time.ticks_ms()

    def process(self, now=None):
        if now is None:
            now = time.ticks_ms()

        if self.state == self.STATE_WAITING and time.ticks_diff(now, self.gate_high_tick) >= 0:
            self.cv.voltage(self.target_volts)
            self.gate.on()
            self.state = self.STATE_GATE_HIGH

        elif self.state == self.STATE_GATE_HIGH and time.ticks_diff(now, self.gate_low_tick) >= 0:
            self.gate.off()
            self.state = self.STATE_IDLE

    def voltage_at(self, v, tick, gate_duration_ms=10):
        """Specify the voltage we want to apply at the desired tick

        Call @process() to actually apply the voltage if needed

        @param v     The desired voltags (volts)
        @param tick  The tick (ms) we want the voltage to change at
        @param gate_duration_ms  The desired duration of the high cycle of the output gate
        """

        self.state = self.STATE_WAITING
        self.target_volts = v
        self.gate_high_tick = tick
        self.gate_low_tick = time.ticks_add(self.gate_high_tick, gate_duration_ms)


class Sigma(EuroPiScript):
    """The main class for this script

    Handles all I/O, renders the UI
    """

    AIN_ROUTE_NONE = 0
    AIN_ROUTE_MEAN = 1
    AIN_ROUTE_STDEV = 2
    AIN_ROUTE_JITTER = 3
    AIN_ROUTE_BIN = 4
    N_AIN_ROUTES = 5

    AIN_ROUTE_NAMES = [
        "None",
        "Mean",
        "Spread",
        "Jitter",
        "Bin"
    ]

    def __init__(self):
        super().__init__()

        self.outputs = [
            DelayedOutput(cv4, cv1),
            DelayedOutput(cv5, cv2),
            DelayedOutput(cv6, cv3)
        ]

        ## Voltage bins for bin mode
        self.voltage_bins = [
            ContinuousBin("Continuous"),
            VoltageBin("Bin 2", [0, 10]),
            VoltageBin("Bin 3", [0, 5, 10]),
            VoltageBin("Bin 6", [0, 2, 4, 6, 8, 10]),
            VoltageBin("Bin 7", [0, 1.7, 3.4, 5, 6.6, 8.3, 10]),
            VoltageBin("Bin 9", [0, 1.25, 2.5, 3.75, 5, 6.25, 7.5, 8.75, 10])
        ]

        # create bins for the quantized 1V/oct modes
        VOLTS_PER_TONE = 1.0 / 6
        VOLTS_PER_SEMITONE = 1.0 / 12
        VOLTS_PER_QUARTERTONE = 1.0 / 24
        tones = []
        semitones = []
        quartertones = []
        for oct in range(10):
            for tone in range(6):
                tones.append(oct + VOLTS_PER_TONE * tone)

            for semitone in range(12):
                semitones.append(oct + VOLTS_PER_SEMITONE * semitone)

            for quartertone in range(24):
                quartertones.append(oct + VOLTS_PER_QUARTERTONE * quartertone)

        self.voltage_bins.append(VoltageBin("Tone", tones))
        self.voltage_bins.append(VoltageBin("Semitone", semitones))
        self.voltage_bins.append(VoltageBin("Quartertone", quartertones))

        cfg = self.load_state_json()

        self.mean = cfg.get("mean", 0.5)
        self.stdev = cfg.get("stdev", 0.5)
        self.ain_route = cfg.get("ain_route", 0)
        self.voltage_bin = cfg.get("bin", 0)
        self.jitter = cfg.get("jitter", 0)

        # create the lockable knobs
        #  Note that this does mean _sometimes_ you'll need to sweep the knob all the way left/right
        #  to unlock it
        self.k1_bank = (
            KnobBank.builder(k1)
            .with_unlocked_knob("mean")
            .with_locked_knob("jitter", initial_percentage_value=cfg.get("jitter", 0.5))
            .build()
        )
        self.k2_bank = (
            KnobBank.builder(k2)
            .with_unlocked_knob("stdev")
            .with_locked_knob("bin", initial_percentage_value=self.voltage_bin / len(self.voltage_bins))
            .build()
        )

        self.config_dirty = False
        self.output_dirty = False

        self.last_interaction_at = time.ticks_ms()
        self.screensaver = Screensaver()

        self.last_clock_at = time.ticks_ms()

        self.clock_duration_ms = 0
        self.clock_duty_cycle_ms = 0

        @b1.handler
        def on_b1_rise():
            self.k1_bank.set_current("jitter")
            self.k2_bank.set_current("bin")
            self.last_interaction_at = time.ticks_ms()

        @b1.handler_falling
        def on_b1_fall():
            self.k1_bank.set_current("mean")
            self.k2_bank.set_current("stdev")
            self.config_dirty = True

        @b2.handler
        def on_b2_rise():
            self.ain_route = (self.ain_route + 1) % self.N_AIN_ROUTES
            self.config_dirty = True
            self.last_interaction_at = time.ticks_ms()

        @din.handler
        def on_din_rise():
            self.output_dirty = True
            now = time.ticks_ms()
            self.clock_duration_ms = time.ticks_diff(now, self.last_clock_at)
            self.last_clock_at = now

        @din.handler_falling
        def on_din_fall():
            now = time.ticks_ms()
            self.clock_duty_cycle_ms = time.ticks_diff(now, self.last_clock_at)

    def save(self):
        """Save the current state to the persistence file"""
        self.config_dirty = False
        cfg = {
            "ain_route": self.ain_route,
            "mean": self.mean,
            "jitter": self.jitter,
            "stdev": self.stdev,
            "bin": self.voltage_bin,
        }
        self.save_state_json(cfg)

    def read_inputs(self):
        self.mean = self.k1_bank["mean"].percent()
        self.stdev = self.k2_bank["stdev"].percent()
        self.jitter = self.k1_bank["jitter"].percent()
        self.voltage_bin = int(self.k2_bank["bin"].percent() * len(self.voltage_bins))

        # Apply attenuation to our CV-controlled input
        if self.ain_route == self.AIN_ROUTE_MEAN:
            self.mean = self.mean * ain.percent()
        elif self.ain_route == self.AIN_ROUTE_STDEV:
            self.stdev = self.stdev * ain.percent()
        elif self.ain_route == self.AIN_ROUTE_JITTER:
            self.jitter = self.jitter * ain.percent()
        elif self.ain_route == self.AIN_ROUTE_BIN:
            self.voltage_bin = int(self.k2_bank["bin"].percent() * ain.percent() * len(self.voltage_bins))

        if self.voltage_bin == len(self.voltage_bins):
            self.voltage_bin = len(self.voltage_bins) - 1  # keep the index in bounds if we reach 1.0

    def set_outputs(self, now):
        for cv in self.outputs:
            cv.process(now)

    def calculate_jitter(self, now):
        self.output_dirty = False

        for cv in self.outputs:
            if cv == self.outputs[0]:
                target_tick = now
            else:
                target_tick = time.ticks_add(now, int(abs(normal(mean = 0, stdev = self.jitter) * self.clock_duration_ms / 4)))

            x = normal(mean = self.mean * MAX_OUTPUT_VOLTAGE, stdev = self.stdev * 2)
            v = self.voltage_bins[self.voltage_bin].closest(x)
            cv.voltage_at(
                v,
                target_tick,
                self.clock_duty_cycle_ms
            )

    def main(self):
        turn_off_all_cvs()

        self.ui_dirty = True

        DISPLAY_PRECISION = 100
        prev_mean = int(self.mean * DISPLAY_PRECISION)
        prev_stdev = int(self.stdev * DISPLAY_PRECISION)
        prev_jitter = int(self.jitter * DISPLAY_PRECISION)
        prev_bin = self.voltage_bin

        while True:
            now = time.ticks_ms()

            self.read_inputs()
            if self.output_dirty:
                self.calculate_jitter(now)
            self.set_outputs(now)

            new_mean = int(self.mean * DISPLAY_PRECISION)
            new_stdev = int(self.stdev * DISPLAY_PRECISION)
            new_jitter = int(self.jitter * DISPLAY_PRECISION)

            self.ui_dirty = (self.ui_dirty or
                self.config_dirty or
                new_mean != prev_mean or
                new_stdev != prev_stdev or
                new_jitter != prev_jitter or
                self.voltage_bin != prev_bin
            )

            if self.ui_dirty:
                self.last_interaction_at = now

            prev_mean = new_mean
            prev_stdev = new_stdev
            prev_jitter = new_jitter
            prev_bin = self.voltage_bin

            if self.config_dirty:
                self.save()

            if time.ticks_diff(now, self.last_interaction_at) > self.screensaver.ACTIVATE_TIMEOUT_MS:
                self.screensaver.draw()
                last_interaction_at = time.ticks_add(now, -self.screensaver.ACTIVATE_TIMEOUT_MS*2)
            elif self.ui_dirty:
                self.ui_dirty = False
                oled.fill(0)
                oled.centre_text(f"""{self.mean:0.2f} {self.stdev:0.2f} {self.jitter:0.2f}
{self.voltage_bins[self.voltage_bin]}
CV: {self.AIN_ROUTE_NAMES[self.ain_route]}""")

if __name__ == "__main__":
    Sigma().main()
