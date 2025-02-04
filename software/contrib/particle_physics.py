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
"""A 1D physics simulating LFO, inspired by the ADDAC503
(https://www.addacsystem.com/en/products/modules/addac500-series/addac503)
"""

from europi import *
from europi_script import EuroPiScript

from experimental.knobs import KnobBank
from experimental.math_extras import rescale

import math
import time


EARTH_GRAVITY = 9.8
MIN_GRAVITY = 0.1
MAX_GRAVITY = 20

MIN_HEIGHT = 0.1
MAX_HEIGHT = 10.0

MIN_SPEED = -5.0
MAX_SPEED = 5.0

MIN_ELASTICITY = 0.0
MAX_ELASTICITY = 0.9

## If a bounce reaches no higher than this, assume we've come to rest
ASSUME_STOP_PEAK = 0.002


class Particle:
    def __init__(self):
        self.y = 0.0
        self.dy = 0.0

        self.last_update_at = time.ticks_ms()

        self.hit_ground = False
        self.reached_apogee = False
        self.stopped = True

        self.peak_height = 0.0

    def set_initial_position(self, height, velocity):
        self.peak_height = height
        self.y = height
        self.dy = velocity
        self.last_update_at = time.ticks_ms()

    def update(self, g, elasticity):
        """Update the particle position based on the ambient gravity & elasticy of the particle
        """
        now = time.ticks_ms()
        delta_t = time.ticks_diff(now, self.last_update_at) / 1000.0

        new_dy = self.dy - delta_t * g
        new_y = self.y + self.dy * delta_t

        # if we were going up, but now we're going down we've reached apogee
        self.reached_apogee = new_dy <= 0 and self.dy >= 0

        if self.reached_apogee:
            self.peak_height = self.y

        # if the vertical position is zero or negative, we've hit the ground
        self.hit_ground = new_y <= 0

        if self.hit_ground:
            #new_y = 0
            new_dy = abs(self.dy * elasticity)  # bounce upwards, reduding the velocity by our elasticity modifier

        self.stopped = self.peak_height <= ASSUME_STOP_PEAK

        if self.stopped:
            new_y = 0
            new_dy = 0

        self.dy = new_dy
        self.y = new_y
        self.last_update_at = now

class ParticlePhysics(EuroPiScript):
    def __init__(self):
        settings = self.load_state_json()

        self.gravity = settings.get("gravity", 9.8)
        self.initial_velocity = settings.get("initial_velocity", 0.0)
        self.release_height = settings.get("height", 10.0)
        self.elasticity = settings.get("elasticity", 0.75)

        self.k1_bank =  (
            KnobBank.builder(k1)
            .with_locked_knob("height", initial_percentage_value=rescale(self.release_height, MIN_HEIGHT, MAX_HEIGHT, 0, 1))
            .with_locked_knob("gravity", initial_percentage_value=rescale(self.gravity, MIN_GRAVITY, MAX_GRAVITY, 0, 1))
            .build()
        )

        self.k2_bank =  (
            KnobBank.builder(k2)
            .with_locked_knob("elasticity", initial_percentage_value=rescale(self.elasticity, MIN_ELASTICITY, MAX_ELASTICITY, 0, 1))
            .with_locked_knob("speed", initial_percentage_value=rescale(self.initial_velocity, MIN_SPEED, MAX_SPEED, 0, 1))

            .build()
        )

        self.particle = Particle()

        self.release_before_next_update = False

        self.alt_knobs = False

        @din.handler
        def on_din_rising():
            self.reset()

        @b1.handler
        def on_b1_press():
            self.reset()

        @b2.handler
        def on_b2_press():
            self.alt_knobs = True
            self.k1_bank.next()
            self.k2_bank.next()

        @b2.handler_falling
        def on_b2_release():
            self.alt_knobs = False
            self.k1_bank.next()
            self.k2_bank.next()


    @classmethod
    def display_name(cls):
        return "ParticlePhysics"

    def save(self):
        state = {
            "gravity"          : self.gravity,
            "initial_velocity" : self.initial_velocity,
            "height"           : self.release_height,
            "elasticity"       : self.elasticity
        }
        self.save_state_json(state)

    def reset(self):
        self.release_before_next_update = True

    def draw(self):
        oled.fill(0)
        row_1_color = 1
        row_2_color = 2
        if self.alt_knobs:
            oled.fill_rect(0, CHAR_HEIGHT+1, OLED_WIDTH, CHAR_HEIGHT+1, 1)
            row_2_color = 0
        else:
            oled.fill_rect(0, 0, OLED_WIDTH, CHAR_HEIGHT+1, 1)
            row_1_color = 0


        oled.text(f"h: {self.release_height:0.2f}  e: {self.elasticity:0.2f}", 0, 0, row_1_color)
        oled.text(f"g: {self.gravity:0.2f}  v: {self.initial_velocity:0.2f}", 0, CHAR_HEIGHT+1, row_2_color)

        # a horizontal representation of the particle bouncing off the left edge of the screen
        oled.pixel(int(rescale(self.particle.y, 0, self.release_height, 0, OLED_WIDTH)), 3 * CHAR_HEIGHT, 1)

        oled.show()

    def main(self):
        while True:
            g = round(rescale(self.k1_bank["gravity"].percent(), 0, 1, MIN_GRAVITY, MAX_GRAVITY), 2)
            h = round(rescale(self.k1_bank["height"].percent(), 0, 1, MIN_HEIGHT, MAX_HEIGHT), 2)
            v = round(rescale(self.k2_bank["speed"].percent(), 0, 1, MIN_SPEED, MAX_SPEED), 2)
            e = round(rescale(self.k2_bank["elasticity"].percent(), 0, 1, MIN_ELASTICITY, MAX_ELASTICITY), 2)

            # the maximum veliocity we can attain, given the current parameters
            # d = 1/2 aT^2 -> T = sqrt(2d/a)
            h2 = 0
            v2 = 0
            if v > 0:
                # initial upward velocity; add this to the initial height
                t = v / g
                h2 = v * t
            else:
                v2 = abs(v)
            t = math.sqrt(2 * (h+h2) / g)
            max_v = g * t + v2

            if g != self.gravity or \
                    h != self.release_height or \
                    v != self.initial_velocity or \
                    e != self.elasticity:
                self.gravity = g
                self.initial_velocity = v
                self.release_height = h
                self.elasticity = e
                self.save()

            self.draw()

            if self.release_before_next_update:
                self.particle.set_initial_position(self.release_height, self.initial_velocity)
                self.release_before_next_update = False

            self.particle.update(self.gravity, self.elasticity)

            # CV 1 outputs a gate whenever we hit the ground
            if self.particle.hit_ground:
                cv1.on()
            else:
                cv1.off()

            # CV 2 outputs a trigger whenever we reach peak altitude and start falling again
            if self.particle.reached_apogee:
                cv2.on()
            else:
                cv2.off()

            # CV 3 outputs a gate when the particle comes to rest
            if self.particle.stopped:
                cv3.on()
            else:
                cv3.off()

            # CV 4 outputs control voltage based on the height of the particle
            cv4.voltage(rescale(self.particle.y, 0, MAX_HEIGHT, 0, MAX_OUTPUT_VOLTAGE))

            # CV 5 outputs control voltage based on the speed of the particle
            cv5.voltage(rescale(abs(self.particle.dy), 0, max_v, 0, MAX_OUTPUT_VOLTAGE))

            # TODO: I don't know what to use CV6 for. But hopefully I'll think of something
            cv6.off()


if __name__ == "__main__":
    ParticlePhysics().main()
