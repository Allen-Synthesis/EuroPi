#!/usr/bin/env python3
"""A 1D physics simulating LFO, inspired by the ADDAC503
(https://www.addacsystem.com/en/products/modules/addac500-series/addac503)
"""

from europi import *
from europi_script import EuroPiScript

from experimental.knobs import KnobBank

import math
import time


EARTH_GRAVITY = 9.8
MIN_GRAVITY = 0.1
MAX_GRAVITY = 10*EARTH_GRAVITY

MIN_HEIGHT = 0.1
MAX_HEIGHT = 20.0

MIN_SPEED = -10.0
MAX_SPEED = 10.0

MIN_ELASTICITY = 0.01
MAX_ELASTICITY = 1.0

def rescale(x, old_min, old_max, new_min, new_max):
    if x <= old_min:
        return new_min
    elif x >= old_max:
        return new_max
    else:
        return (x - old_min) / (old_max - old_min) * (new_max - new_min) + new_min

class Particle:
    def __init__(self):
        self.y = 0.0
        self.dy = 0.0

        self.last_update_at = time.ticks_ms()

    def set_initial_position(self, height, velocity):
        self.y = height
        self.dy = velocity
        self.last_update_at = time.ticks_ms()

    def update(self, g, elasticity):
        """Update the particle position based on the ambient gravity & elasticy of the particle

        @return A tuple of the form (hit_apogee, hit_ground) indicating whether the particle has
                its maximum height and/or the ground
        """
        hit_ground = False
        hit_apogee = False

        now = time.ticks_ms()
        delta_t = time.ticks_diff(now, self.last_update_at) / 1000.0

        new_dy = self.dy - delta_t * g

        if new_dy < 0 and self.dy >= 0:
            hit_apogee = True

        self.dy = new_dy
        self.y += self.dy * delta_t

        if self.y < 0:
            hit_ground = True
            self.y = 0
            self.dy = -self.dy * elasticity

        self.last_update_at = now
        return (hit_apogee, hit_ground)

class MarblePhysics(EuroPiScript):
    def __init__(self):
        settings = self.load_state_json()

        self.gravity = settings.get("gravity", 9.8)
        self.initial_velocity = settings.get("initial_velocity", 0.0)
        self.release_height = settings.get("height", 10.0)
        self.elasticity = settings.get("elasticity", 0.75)

        self.k1_bank =  (
            KnobBank.builder(k1)
            .with_locked_knob("height", initial_percentage_value=rescale(self.initial_velocity, MIN_HEIGHT, MAX_HEIGHT, 0, 1))
            .with_locked_knob("gravity", initial_percentage_value=rescale(self.gravity, MIN_GRAVITY, MAX_GRAVITY, 0, 1))
            .build()
        )

        self.k2_bank =  (
            KnobBank.builder(k2)
            .with_locked_knob("elasticity", initial_percentage_value=rescale(self.gravity, MIN_ELASTICITY, MAX_ELASTICITY, 0, 1))
            .with_locked_knob("speed", initial_percentage_value=rescale(self.initial_velocity, MIN_SPEED, MAX_SPEED, 0, 1))

            .build()
        )

        self.particle = Particle()

        self.alt_knobs = False

        @din.handler
        def on_din_rising():
            self.release()

        @b1.handler
        def on_b1_press():
            self.release()

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
        return "MarblePhysics"

    def save(self):
        state = {
            "gravity"          : self.gravity,
            "initial_velocity" : self.initial_velocity,
            "height"           : self.release_height,
            "elasticity"       : self.elasticity
        }
        self.save_state_json(state)

    def release(self):
        self.particle.set_initial_position(self.release_height, self.initial_velocity)

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


        oled.text(f"h: {self.release_height:0.2f}  e:{self.elasticity:0.2f}", 0, 0, row_1_color)
        oled.text(f"g: {self.gravity:0.2f}  v:{self.initial_velocity:0.2f}", 0, CHAR_HEIGHT+1, row_2_color)
        oled.show()

    def main(self):
        while True:
            g = rescale(self.k1_bank["gravity"].percent(), 0, 1, MIN_GRAVITY, MAX_GRAVITY)
            h = rescale(self.k1_bank["height"].percent(), 0, 1, MIN_HEIGHT, MAX_HEIGHT)
            v = rescale(self.k2_bank["speed"].percent(), 0, 1, MIN_SPEED, MAX_SPEED)
            e = rescale(self.k2_bank["elasticity"].percent(), 0, 1, MIN_ELASTICITY, MAX_ELASTICITY)

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

            (hit_apogee, hit_ground) = self.particle.update(self.gravity, self.elasticity)

            # CV 1 outputs a trigger whenever we hit the ground
            if hit_ground:
                cv1.voltage(5)
            else:
                cv1.voltage(0)

            # CV 4 outputs a trigger whenever we reach peak altitude and start falling again
            if hit_apogee:
                cv4.voltage(5)
            else:
                cv4.voltage(0)

            # CV 2 outputs control voltage based on the height of the particle
            cv2.voltage(rescale(self.particle.y, 0, MAX_HEIGHT, 0, MAX_OUTPUT_VOLTAGE))

            # CV 3 outputs control voltage based on the speed of the particle
            cv3.voltage(rescale(abs(self.particle.dy), -max_v, max_v, 0, MAX_OUTPUT_VOLTAGE))

            # TODO: we've got to be able to figure out _something_ to do with these, I'm just out of ideas
            # right now
            cv5.off()
            cv6.off()


if __name__ == "__main__":
    MarblePhysics().main()
