#!/usr/bin/env python3
"""Lutra -- A EuroPi reimagining of Expert Sleepers' Otterly

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

import math
import time

class WaveGenerator:

    ## Supported wave shapes
    WAVE_SHAPES_NAMES = [
        "Sine",
        "Square",
        "Triangle",
        "Saw",
        "Ramp",
    ]

    WAVE_SHAPES_NAMES_TO_SHAPES = {
        "sine": 0,
        "square": 1,
        "triangle": 2,
        "saw": 3,
        "ramp": 4,
    }

    WAVE_SHAPE_SINE = 0
    WAVE_SHAPE_SQUARE = 1
    WAVE_SHAPE_TRIANGLE = 2
    WAVE_SHAPE_SAW = 3
    WAVE_SHAPE_RAMP = 4
    NUM_WAVE_SHAPES = 5

    ## 12x12 pixel images of the wave shapes
    WAVE_SHAPE_IMAGES = [
        FrameBuffer(bytearray(b'\x10\x00(\x00D\x00D\x00\x82\x00\x82\x00\x82\x10\x82\x10\x01\x10\x01\x10\x00\xa0\x00@'), 12, 12, MONO_HLSB),              # SINE
        FrameBuffer(bytearray(b'\xfe\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x82\x00\x83\xf0'), 12, 12, MONO_HLSB),  # SQUARE
        FrameBuffer(bytearray(b'\x06\x00\x06\x00\t\x00\t\x00\x10\x80\x10\x80 @ @@ @ \x80\x10\x80\x10'), 12, 12, MONO_HLSB),                              # TRIANGLE
        FrameBuffer(bytearray(b'\x80\x00\xc0\x00\xa0\x00\x90\x00\x88\x00\x84\x00\x82\x00\x81\x00\x80\x80\x80@\x80 \x80\x10'), 12, 12, MONO_HLSB),        # SAW
        FrameBuffer(bytearray(b'\x00\x10\x000\x00P\x00\x90\x01\x10\x02\x10\x04\x10\x08\x10\x10\x10 \x10@\x10\x80\x10'), 12, 12, MONO_HLSB),              # RAMP
    ]

    IMAGE_SIZE = (12, 12)

    """Generates the output wave forms

    We give the generator the desired ticks for 1 complete wave shape
    """
    def __init__(self, cv_output):
        self.cv_output = cv_output
        self.shape = 0

        self.cycle_ticks = 1000
        self.current_tick = 0

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
        else:
            volts = 0

        self.current_tick = self.current_tick + 1
        if self.current_tick >= self.cycle_ticks:
            self.current_tick = 0

        self.cv_output.voltage(volts)
        return volts

class Lutra(EuroPiScript):
    AIN_MODE_SPREAD = 0
    AIN_MODE_SPEED = 1

    AIN_MODE_NAMES = [
        "Spread",
        "Speed"
    ]

    MIN_CYCLE_TICKS = 10
    MAX_CYCLE_TICKS = 1600

    def __init__(self):
        self.waves = [
            WaveGenerator(cv) for cv in cvs
        ]
        self.config_dirty = False
        self.hold_low = False

        def hold_reset():
            self.hold_low = True
        b1.handler(hold_reset)
        din.handler(hold_reset)

        def resync():
            """Resynchronize all of the outputs
            """
            self.hold_low = False
            for wave in self.waves:
                wave.reset()
        b1.handler_falling(resync)
        din.handler_falling(resync)

        @b2.handler
        def change_wave():
            """Change the current wave shape
            """
            shape = (self.waves[0].shape + 1) % WaveGenerator.NUM_WAVE_SHAPES
            for wave in self.waves:
                wave.shape = shape
            self.config_dirty = True

        self.load()

    def load(self):
        """Load and apply the saved configuration

        @exception  ValueError if the configuration contains invalid values
        """
        cfg = self.load_state_json()
        ain_mode = cfg.get("ain", "spread").lower()
        if ain_mode == "spread":
            self.ain_mode = self.AIN_MODE_SPREAD
        elif ain_mode == "speed":
            self.ain_mode = self.AIN_MODE_SPEED
        else:
            raise ValueError(f"Unknown AIN mode: {ain_mode}")

        shape = cfg.get("shape", "sine").lower()
        if shape in WaveGenerator.WAVE_SHAPES_NAMES_TO_SHAPES.keys():
            for wave in self.waves:
                wave.shape = WaveGenerator.WAVE_SHAPES_NAMES_TO_SHAPES[shape]
        else:
            raise ValueError(f"Unknown wave shape: {shape}")

    def save(self):
        """Write the configuration file & set config_dirty to False
        """
        cfg = {
            "ain": self.AIN_MODE_NAMES[self.ain_mode].lower(),
            "wave": WaveGenerator.WAVE_SHAPES_NAMES[self.waves[0].shape].lower()
        }
        self.save_state_json(cfg)
        self.config_dirty = False

    def main(self):
        # To keep a rolling display of the waves, save a screen's width's worth of pixels
        display_pixels = [
            [] for cv in cvs
        ]

        while True:
            # Read the CV inputs and apply them
            # Round to 2 decimal places to reduce noise
            ain_percent = round(ain.percent(), 2)
            k1_percent = round(k1.percent(), 2)
            k2_percent = round(k2.percent(), 2)

            if self.ain_mode == self.AIN_MODE_SPREAD:
                k_speed = k1_percent
                k_spread = clamp(k2_percent + ain_percent, 0, 1)
            else:
                k_speed = clamp(k1_percent + ain_percent, 0, 1)
                k_spread = k2_percent

            base_ticks = int((1.0 - k_speed) * (self.MAX_CYCLE_TICKS - self.MIN_CYCLE_TICKS) + self.MIN_CYCLE_TICKS)
            for i in range(len(cvs)):
                spread_adjust = int(base_ticks * i * k_spread / 10)
                self.waves[i].change_cycle_length(base_ticks - spread_adjust)

            for i in range(len(cvs)):
                if self.hold_low:
                    display_pixels[i].append(OLED_HEIGHT-1)
                    cvs[i].off()
                else:
                    volts = self.waves[i].tick()
                    display_pixels[i].append(int(OLED_HEIGHT - 1 - volts / MAX_OUTPUT_VOLTAGE * (OLED_HEIGHT-1)))

                if len(display_pixels[i]) >= OLED_WIDTH:
                        display_pixels[i].pop(0)

            if self.config_dirty:
                self.save()

            oled.fill(0)
            for channel in display_pixels:
                for px in range(len(channel)):
                    oled.pixel(px, channel[px], 1)
            oled.blit(WaveGenerator.WAVE_SHAPE_IMAGES[self.waves[0].shape], 0, 0)
            oled.show()

if __name__ == "__main__":
    Lutra().main()
