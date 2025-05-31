#!/usr/bin/env python3
"""
A loose clone of the ADDAC 508 "Swell Physics"

Uses a trochoidal wave to generate control voltages
"""

import configuration
from europi import *
from europi_script import EuroPiScript

from experimental.knobs import KnobBank
from experimental.math_extras import rescale
from experimental.screensaver import OledWithScreensaver
from experimental.thread import DigitalInputHelper

import machine
from math import (
    cos,
    pi,
    sin,
)

import _thread

two_pi = 2 * pi

ssoled = OledWithScreensaver()



class OceanSurge(EuroPiScript):
    BG_ERR = None

    MIN_RADIUS = 0.01
    MAX_RADIUS = 2

    MIN_LENGTH = 1
    MAX_LENGTH = 20

    MAX_BUOY_SPREAD = 10

    MIN_SPEED_INCREMENT = machine.freq() / 1_000_000_000_000
    MAX_SPEED_INCREMENT = MIN_SPEED_INCREMENT * 100

    CLIP_MODE_REFLECT = 0
    CLIP_MODE_WRAP = 1
    CLIP_MODE_CLIP = 2
    N_CLIP_MODES = 3

    CV_TARGET_NONE = -1
    CV_TARGET_AGITATION = 0
    CV_TARGET_BUOY_SPREAD = 1
    CV_TARGET_SPEED = 2
    CV_TARGET_SWELL_SIZE = 3

    def __init__(self):
        super().__init__()
        self.is_running = False

        self.wavelength = 10

        saved_state = self.load_state_json()
        self.speed = saved_state.get("speed", 0.5)
        self.spread = saved_state.get("spread", 0.5)
        self.swell_size = k1.percent()
        self.agitation = k2.percent()
        self.settings_dirty = False
        self.clip_mode = saved_state.get("clip_mode", self.CLIP_MODE_REFLECT)
        self.d = 2.0

        if self.config.CV_TARGET == "agitation":
            self.cv_target = self.CV_TARGET_AGITATION
        elif self.config.CV_TARGET == "buoy_spread":
            self.cv_target = self.CV_TARGET_BUOY_SPREAD
        elif self.config.CV_TARGET == "sim_speed":
            self.cv_target = self.CV_TARGET_SPEED
        elif self.config.CV_TARGET == "swell_size":
            self.cv_target = self.CV_TARGET_SWELL_SIZE
        else:
            self.cv_target = self.CV_TARGET_NONE

        self.shift = False

        self.k1_bank = (
            KnobBank.builder(k1)
            .with_unlocked_knob("swell_size")
            .with_locked_knob(
                "spread", initial_percentage_value=self.spread
            )
            .build()
        )

        self.k2_bank = (
            KnobBank.builder(k2)
            .with_unlocked_knob("agitation")
            .with_locked_knob(
                "speed", initial_percentage_value=self.speed
            )
            .build()
        )

        # Use B2 as a shift for knob controls
        def on_b2_press():
            self.shift = True
            self.k1_bank.set_current("spread")
            self.k2_bank.set_current("speed")
            ssoled.notify_user_interaction()

        def on_b2_release():
            self.shift = False
            self.k1_bank.set_current("swell_size")
            self.k2_bank.set_current("agitation")
            self.settings_dirty = True

        def on_b1_press():
            self.clip_mode = (self.clip_mode + 1) % self.N_CLIP_MODES
            self.settings_dirty = True
            ssoled.notify_user_interaction()

        self.digital_input_state = DigitalInputHelper(
            on_b2_rising = on_b2_press,
            on_b2_falling = on_b2_release,
            on_b1_rising = on_b1_press,
        )

    @classmethod
    def config_points(cls):
        return [
            configuration.choice(
                "CV_TARGET",
                [
                    "agitation",
                    "buoy_spread",
                    "sim_speed",
                    "swell_size",
                ],
                "agitation",
            ),
        ]

    def save(self):
        self.settings_dirty = False
        self.save_state_json({
            "spread": self.spread,
            "speed": self.speed,
        })

    def apply_clip(self, y):
        """
        Convert the wave to a CV value

        As configured, the wave will (at most) go from -2 to +2 on the Y axis. Depending on
        the clipping mode we either
            - truncate to -1 to +1
            - reflect at -1/+1
            - wrap through the limits (e.g. 1.5 -> -0.5)

        Then we shift the clipped wave to 0-1 & multiply by the max output voltage
        """
        if self.clip_mode == self.CLIP_MODE_CLIP:
            if y < -1:
                y = -1
            elif y > 1:
                y = 1
        elif self.clip_mode == self.CLIP_MODE_REFLECT:
            if y < -1 or y > 1:
                delta = abs(y) - 1
                if y > 1:
                    y = 1 - delta
                else:
                    y = -1 + delta
        elif self.clip_mode == self.CLIP_MODE_WRAP:
            if y < -1 or y > 1:
                delta = abs(y) - 1
                if y > 1:
                    y = -1 + delta
                else:
                    y = 1 - delta

        return y

    def wave_to_cv(self, y):
        y = (y + 1) / 2
        return y * MAX_OUTPUT_VOLTAGE

    def wave_x(self, a, b, t):
        return a + self.r * sin(t - 2 * pi * a / self.wavelength) * self.d ** b

    def wave_y(self, a, b, t):
        return b + self.r * cos(t - 2 * pi * a / self.wavelength) * self.d ** b

    def draw(self):
        # UI:
        # +----------------+
        # |Swl 0.0  Agt 0.0|
        # |Spr 0.0  Spd 0.0|
        # |                |
        # +----------------+
        ssoled.fill(0)


        if not self.shift:
            ssoled.fill_rect(0, 0, OLED_WIDTH, CHAR_HEIGHT+2, 1)
        else:
            ssoled.fill_rect(0, CHAR_HEIGHT+1, OLED_WIDTH, CHAR_HEIGHT+2, 1)

        ssoled.text(f"Swl {self.swell_size:0.1f}  Agt {self.agitation:0.1f}", 0, 1, 1 if self.shift else 0)
        ssoled.text(f"Spr {self.spread:0.1f}  Spd {self.speed:0.1f}", 0, CHAR_HEIGHT+2, 0 if self.shift else 1)
        if self.clip_mode == self.CLIP_MODE_CLIP:
            ssoled.text("clip", 0, 2*CHAR_HEIGHT, 1)
        elif self.clip_mode == self.CLIP_MODE_REFLECT:
            ssoled.text("reflect", 0, 2*CHAR_HEIGHT, 1)
        elif self.clip_mode == self.CLIP_MODE_WRAP:
            ssoled.text("wrap", 0, 2*CHAR_HEIGHT+2, 1)
        ssoled.show()

    def gui_thread(self):
        draw_rate = 30.0
        fps_sleep = 1.0 / draw_rate
        while self.is_running:
            try:
                self.draw()
                time.sleep(fps_sleep)
            except Exception as err:
                self.BG_ERR = err

        if self.is_running:
            self.BG_ERR = Exception('USB disconnected')

    def voltage_thread(self):
        sim_now = 0.0

        prev_swell = self.k1_bank["swell_size"].percent()
        prev_spread = self.k1_bank["spread"].percent()
        prev_agitation = self.k2_bank["agitation"].percent()
        prev_speed = self.k2_bank["speed"].percent()

        def ui_change(old, new):
            return abs(old - new) >= 0.01

        while self.is_running:
            if self.BG_ERR is not None:
                print(f'Background error {self.BG_ERR}')
                self.BG_ERR = None

            self.digital_input_state.update()

            # read the current knob values
            prev_swell = self.swell_size
            prev_spread = self.spread
            prev_agitation = self.agitation
            prev_speed = self.speed
            self.swell_size = self.k1_bank["swell_size"].percent()
            self.spread = self.k1_bank["spread"].percent()
            self.agitation = self.k2_bank["agitation"].percent()
            self.speed = self.k2_bank["speed"].percent()

            if (
                ui_change(prev_swell, self.swell_size)
                or ui_change(prev_spread, self.spread)
                or ui_change(prev_agitation, self.agitation)
                or ui_change(prev_speed, self.speed)
            ):
                ssoled.notify_user_interaction()

            if self.cv_target == self.CV_TARGET_AGITATION:
                self.agitation += ain.percent()
            elif self.cv_target == self.CV_TARGET_BUOY_SPREAD:
                self.spread += ain.percent()
            elif self.cv_target == self.CV_TARGET_SPEED:
                self.speed += ain.percent()
            elif self.cv_target == self.CV_TARGET_SWELL_SIZE:
                self.swell_size += ain.percent()

            # convert the knob values into our wave parameters
            self.r = rescale(self.agitation, 0.0, 1.0, self.MIN_RADIUS, self.MAX_RADIUS)
            self.wavelength = rescale(self.swell_size, 0.0, 1.0, self.MIN_LENGTH, self.MAX_LENGTH)

            buoy_x = self.MAX_BUOY_SPREAD * self.spread

            y1 = self.apply_clip(self.wave_y(-buoy_x, 0, sim_now))
            y2 = self.apply_clip(self.wave_y(0, 0, sim_now))
            y3 = self.apply_clip(self.wave_y(buoy_x, 0, sim_now))

            cv1.voltage(self.wave_to_cv(y1))
            cv2.voltage(self.wave_to_cv(y2))
            cv3.voltage(self.wave_to_cv(y3))

            if y1 < y2:
                cv4.on()
            else:
                cv4.off()

            if y2 > y3:
                cv5.on()
            else:
                cv5.off()

            cv6.voltage(
                self.wave_to_cv((y1 + y2 + y3) / 3.0)
            )

            sim_now += rescale(self.speed, 0, 1, self.MIN_SPEED_INCREMENT, self.MAX_SPEED_INCREMENT)
            if sim_now > two_pi:
                sim_now -= two_pi

            if self.settings_dirty:
                self.save()

    def main(self):
        self.is_running = True
        try:
            _thread.start_new_thread(self.gui_thread, ())
            self.voltage_thread()
        except KeyboardInterrupt as err:
            print(err)
            self.is_running = False
        finally:
            print("User aborted. Exiting.")

if __name__ == "__main__":
    OceanSurge().main()
