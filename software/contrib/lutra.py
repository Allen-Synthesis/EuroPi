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
"""Lutra -- A EuroPi reimagining of Expert Sleepers' Otterley

This script is a free-running, syncable LFO with variable shapes.  Each output channel's clock speed is slightly
different, with the spread being controlled by K2 (and optionally AIN).  The overall speed is controlled by
K1 (and optionally AIN).  B1 & DIN both act as synchronization inputs. B2 cycles through the different output
waveforms.

Lutra: a genus of otters, including L. lutra, the eurasian otter and L. sumatrana, the hairy-nosed otter.

@author Chris Iverach-Brereton
@year   2024

@see    https://expert-sleepers.co.uk/otterley.html
"""

from europi import *
from europi_script import EuroPiScript

import configuration
import math
from random import random
import time

import _thread

from experimental.math_extras import rescale
from experimental.thread import DigitalInputHelper

class WaveGenerator:
    """Generates the output wave forms and sets the voltage going to one of the output jacks

    5 wave shapes are supported, with the cycle time expressed in "ticks." These ticks have no 1:1 relationship
    with any real-world time unit, and are simply defined by each iteration through the script's main loop.
    """

    ## Supported wave shapes
    WAVE_SHAPE_SINE = 0
    WAVE_SHAPE_SQUARE = 1
    WAVE_SHAPE_TRIANGLE = 2
    WAVE_SHAPE_SAW = 3
    WAVE_SHAPE_RAMP = 4
    WAVE_SHAPE_STEP_RANDOM = 5
    WAVE_SHAPE_SMOOTH_RANDOM = 6
    NUM_WAVE_SHAPES = 7

    WAVE_SHAPES_NAMES = [
        "Sine",
        "Square",
        "Triangle",
        "Saw",
        "Ramp",
        "Step_Random",
        "Smooth_Random",
    ]

    WAVE_SHAPES_NAMES_TO_SHAPES = {
        "sine": WAVE_SHAPE_SINE,
        "square": WAVE_SHAPE_SQUARE,
        "triangle": WAVE_SHAPE_TRIANGLE,
        "saw": WAVE_SHAPE_SAW,
        "ramp": WAVE_SHAPE_RAMP,
        "step_random": WAVE_SHAPE_STEP_RANDOM,
        "smooth_random": WAVE_SHAPE_SMOOTH_RANDOM,
    }

    ## 12x12 pixel images of the wave shapes
    WAVE_SHAPE_IMAGES = [
        FrameBuffer(bytearray(b'\x10\x00(\x00D\x00D\x00\x82\x00\x82\x00\x82\x10\x82\x10\x01\x10\x01\x10\x00\xa0\x00@'), 12, 12, MONO_HLSB),              # SINE
        FrameBuffer(bytearray(b'\xfe\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x83\xf0'), 12, 12, MONO_HLSB),  # SQUARE
        FrameBuffer(bytearray(b'\x06\x00\x06\x00\t\x00\t\x00\x10\x80\x10\x80 @ @@ @ \x80\x10\x80\x10'), 12, 12, MONO_HLSB),                              # TRIANGLE
        FrameBuffer(bytearray(b'\x80\x00\xc0\x00\xa0\x00\x90\x00\x88\x00\x84\x00\x82\x00\x81\x00\x80\x80\x80@\x80 \x80\x10'), 12, 12, MONO_HLSB),        # SAW
        FrameBuffer(bytearray(b'\x00\x10\x000\x00P\x00\x90\x01\x10\x02\x10\x04\x10\x08\x10\x10\x10 \x10@\x10\x80\x10'), 12, 12, MONO_HLSB),              # RAMP
        FrameBuffer(bytearray(b'\x00\xe0\x00\xa0\x00\xa0\x00\xa0<\xa0$\xa0$\xa0\xe4\xb0\x04\x80\x04\x80\x04\x80\x07\x80'), 12, 12, MONO_HLSB),           # STEP_RANDOM
        FrameBuffer(bytearray(b'\x00`\x00P\x00P\x08P\x14P$PD\x90\x82\x80\x02\x80\x02\x80\x02\x80\x01\x80'), 12, 12, MONO_HLSB),                          # SMOOTH_RANDOM
    ]

    IMAGE_SIZE = (12, 12)

    def __init__(self, cv_output):
        """Constructor

        @param cv_output  The CV output jack that the generated wave gets output on
        """
        self.cv_output = cv_output
        self.shape = 0

        self.cycle_ticks = 1000
        self.current_tick = 0

        self.prev_random_goal = random() * MAX_OUTPUT_VOLTAGE
        self.random_goal = random() * MAX_OUTPUT_VOLTAGE

    def reset(self):
        """Reset the wave to the beginning
        """
        self.current_tick = 0

    def change_cycle_length(self, new_length):
        """Change the number of steps in the pattern

        We need to preserve our relative progress to avoid skipping when changing the cycle length
        """
        if new_length != self.cycle_ticks:
            progress = self.current_tick / self.cycle_ticks
            self.cycle_ticks = new_length
            self.current_tick = int(new_length * progress)

    def tick(self):
        """Calculate the appropriate voltage for the output, given the current clock time

        @return The desired voltage
        """
        if self.shape == self.WAVE_SHAPE_SINE:
            # we want to start at -1 and go up, so we actually use a negative cos wave, but the shape is the same
            theta = (self.current_tick / self.cycle_ticks) * 2 * math.pi
            volts = (-math.cos(theta) + 1) / 2 * MAX_OUTPUT_VOLTAGE
        elif self.shape == self.WAVE_SHAPE_SQUARE:
            if self.current_tick < (self.cycle_ticks >> 1):
                volts = MAX_OUTPUT_VOLTAGE
            else:
                volts = 0
        elif self.shape == self.WAVE_SHAPE_TRIANGLE:
            half_cycle_ticks = (self.cycle_ticks >> 1)
            if self.current_tick < half_cycle_ticks:
                volts = self.current_tick / half_cycle_ticks * MAX_OUTPUT_VOLTAGE
            else:
                volts = MAX_OUTPUT_VOLTAGE - (self.current_tick - half_cycle_ticks) / half_cycle_ticks * MAX_OUTPUT_VOLTAGE
        elif self.shape == self.WAVE_SHAPE_SAW:
            volts = MAX_OUTPUT_VOLTAGE - self.current_tick / self.cycle_ticks * MAX_OUTPUT_VOLTAGE
        elif self.shape == self.WAVE_SHAPE_RAMP:
            volts = self.current_tick / self.cycle_ticks * MAX_OUTPUT_VOLTAGE
        elif self.shape == self.WAVE_SHAPE_STEP_RANDOM:
            volts = self.random_goal
        elif self.shape == self.WAVE_SHAPE_SMOOTH_RANDOM:
            slope = (self.random_goal - self.prev_random_goal) / self.cycle_ticks
            volts = slope * self.current_tick + self.prev_random_goal
        else:
            volts = 0

        self.current_tick = self.current_tick + 1
        if self.current_tick >= self.cycle_ticks:
            self.current_tick = 0
            self.prev_random_goal = self.random_goal
            self.random_goal = random() * MAX_OUTPUT_VOLTAGE

        self.cv_output.voltage(volts)
        return volts

class Lutra(EuroPiScript):
    """The main class for this script; handles running the main loop, configuring I/O, loading, and saving state.
    """

    # We support CV control over either LFO speed OR LFO spread via AIN.  This option is not exposed through a menu
    # and must be configured via the config file.  See lutra.md for details
    AIN_MODE_SPREAD = 0
    AIN_MODE_SPEED = 1
    AIN_MODE_NAMES = [
        "Spread",
        "Speed"
    ]

    # The maximum and minimum cycle time for the LFOs
    MIN_CYCLE_TICKS = 250
    MAX_CYCLE_TICKS = 10000

    # Maximum wave speed multipliers relative to cv1
    MAX_SPEED_MULTIPLIERS = [
        1/1,
        6/5,
        5/4,
        4/3,
        3/2,
        2/1
    ]

    def __init__(self):
        """Constructor

        This creates all of the necessary objects, but does not create the separate thread for handling the GUI;
        see @main for that.
        """
        super().__init__()

        self.waves = [
            WaveGenerator(cv) for cv in cvs
        ]
        self.config_dirty = False
        self.hold_low = False
        self.last_wave_change_at = time.ticks_ms()

        # Connect the B2 handler to our digital input helper
        # B1 and DIN are handled differently since they interact with each other
        # See @wave_generator_thread
        self.digital_input_state = DigitalInputHelper(
            on_b2_rising = self.on_b2_rising
        )

        # Save the last screen width's worth of output voltages converted to pixel heights
        # This speeds up rendering
        self.display_pixels = [
            [] for cv in cvs
        ]

        # To coordinate access to self.display_pixels between threads we need a mutex to make sure
        # we don't read the array while it's being modified
        self.pixel_lock = _thread.allocate_lock()

        self.load()

    @classmethod
    def config_points(cls):
        """Return the static configuration options for this class
        """
        return [
            configuration.choice(name="AIN_MODE", choices=["spread", "speed"], default="spread")
        ]

    def load(self):
        """Load and apply the saved state

        @exception  ValueError if the configuration contains invalid values
        """
        cfg = self.load_state_json()
        shape = cfg.get("wave", "sine").lower()
        if shape in WaveGenerator.WAVE_SHAPES_NAMES_TO_SHAPES.keys():
            for wave in self.waves:
                wave.shape = WaveGenerator.WAVE_SHAPES_NAMES_TO_SHAPES[shape]
        else:
            raise ValueError(f"Unknown wave shape: {shape}")

    def save(self):
        """Write the saved-state file & set config_dirty to False
        """
        cfg = {
            "wave": WaveGenerator.WAVE_SHAPES_NAMES[self.waves[0].shape].lower()
        }
        self.save_state_json(cfg)
        self.config_dirty = False

    def on_digital_in_rising(self):
        """Called when either B1 or DIN goes high

        Signals the wave generator thread that all outputs should be forced low
        """
        self.hold_low = True

    def on_digital_in_falling(self):
        """Called when both B1 and DIN are low

        Signals the wave generator thread that all outputs should reset
        """
        self.hold_low = False
        for wave in self.waves:
                wave.reset()

    def on_b2_rising(self):
        """Called when either B2 goes high

        Cycles through the active wave shape
        """
        shape = (self.waves[0].shape + 1) % WaveGenerator.NUM_WAVE_SHAPES
        for wave in self.waves:
            wave.shape = shape
        self.last_wave_change_at = time.ticks_ms()
        self.config_dirty = True

    def gui_render_thread(self):
        """A thread function that handles drawing the GUI
        """
        SHOW_WAVE_TIMEOUT = 3000

        # To prevent the module locking up when we connect the USB for e.g. debugging, kill this thread
        # if the USB state changes. Otherwise the second core will continue being busy, which makes connecting
        # to the Python terminal impossible
        usb_connected_at_start = usb_connected.value()
        while usb_connected.value() == usb_connected_at_start:
            now = time.ticks_ms()
            oled.fill(0)
            with self.pixel_lock:
                for channel in self.display_pixels:
                    for px in range(len(channel)):
                        oled.pixel(px, channel[px], 1)
            if time.ticks_diff(now, self.last_wave_change_at) < SHOW_WAVE_TIMEOUT:
                oled.blit(WaveGenerator.WAVE_SHAPE_IMAGES[self.waves[0].shape], 0, 0)
            oled.show()

    def wave_generation_thread(self):
        """A thread function that handles the underlying math of generating the waveforms
        """
        # To prevent the module locking up when we connect the USB for e.g. debugging, kill this thread
        # if the USB state changes
        usb_connected_at_start = usb_connected.value()
        while usb_connected.value() == usb_connected_at_start:
            # Read the digital inputs
            self.digital_input_state.update()

            # Manually handle B1 and DIN rising & falling
            # If either goes high, signal that we want to old the outputs low
            # If both become low, signal that all outputs should reset & output normally
            if self.digital_input_state.b1_rising or self.digital_input_state.din_rising:
                self.on_digital_in_rising()
            elif (
                (self.digital_input_state.b1_falling and not self.digital_input_state.din_high) or
                (self.digital_input_state.din_falling and not self.digital_input_state.b1_pressed)
            ):
                self.on_digital_in_falling()

            # Read the CV inputs and apply them
            # Round to 2 decimal places to reduce noise
            ain_percent = round(ain.percent(), 2)
            k1_percent = round(k1.percent(), 2)
            k2_percent = round(k2.percent(), 2)

            if self.config.AIN_MODE == self.AIN_MODE_SPREAD:
                k_speed = k1_percent
                k_spread = clamp(k2_percent + ain_percent, 0, 1)
            else:
                k_speed = clamp(k1_percent + ain_percent, 0, 1)
                k_spread = k2_percent

            base_ticks = int((1.0 - k_speed) * (self.MAX_CYCLE_TICKS - self.MIN_CYCLE_TICKS) + self.MIN_CYCLE_TICKS)
            for i in range(len(cvs)):
                base_tick_multiplier = rescale(k_spread, 0, 1, 1, self.MAX_SPEED_MULTIPLIERS[i])
                spread_ticks = int(base_ticks / base_tick_multiplier)
                self.waves[i].change_cycle_length(spread_ticks)

            for i in range(len(cvs)):
                pixel_height = OLED_HEIGHT - 1
                if self.hold_low:
                    cvs[i].off()
                else:
                    volts = self.waves[i].tick()
                    pixel_height = int(OLED_HEIGHT - 1 - volts / MAX_OUTPUT_VOLTAGE * (OLED_HEIGHT-1))

                with self.pixel_lock:
                    self.display_pixels[i].append(pixel_height)
                    if len(self.display_pixels[i]) >= OLED_WIDTH:
                        self.display_pixels[i].pop(0)

            if self.config_dirty:
                self.save()

    def main(self):
        gui_thread = _thread.start_new_thread(self.gui_render_thread, ())
        self.wave_generation_thread()

if __name__ == "__main__":
    Lutra().main()
