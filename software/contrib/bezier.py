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
"""
Generates random voltages based on Bezier curves

Inspired by Addac Systems' & Monotrail's ADDAC507 collaboration
"""

from europi import *
from europi_script import EuroPiScript

from experimental.knobs import *
from experimental.math_extras import solve_linear_system
from experimental.screensaver import OledWithScreensaver

import configuration
import math
import random
import time

ssoled = OledWithScreensaver()

class LogicalOperator:
    """Abstract class used for saving the gate outputs' logical operation

    Subclasses must implement the compare(a, b) method
    """
    def compare(self, a, b):
        raise Exception("Not implemented")

class LogicalAnd(LogicalOperator):
    """Binary AND operator"""
    def compare(self, a, b):
        return a and b

class LogicalOr(LogicalOperator):
    """Binary OR operator"""
    def compare(self, a, b):
        return a or b

class LogicalXor(LogicalOperator):
    """Binary XOR operator"""
    def compare(self, a, b):
        return (a or b) and not (a and b)

class LogicalNand(LogicalOperator):
    """Binary NAND operator"""
    def compare(self, a, b):
        return not (a and b)

class LogicalNor(LogicalOperator):
    """Binary Nor operator"""
    def compare(self, a, b):
        return not (a or b)

class LogicalXnor(LogicalOperator):
    """Binary XNOR operator"""
    def compare(self, a, b):
        return (a and not b) or (not a and b)


CLIP_MODE_LIMIT = 0
CLIP_MODE_FOLD = 1
CLIP_MODE_THRU = 2
N_CLIP_MODES = 3

CLIP_MODE_NAMES = [
    "Limit",
    "Fold",
    "Thru"
]

AIN_MODE_FREQUENCY = "frequency"
AIN_MODE_CURVE = "curve"


class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x},{self.y}"


def linear_interpolate(x1, x2, t):
    """Linearly interpolate from one value to another

    @param x1 The initial value of x
    @param x2 The final value of x
    @param t  The time [0, 1]

    @return   The interpolated value of x
    """
    return x1 * (1-t) + x2 * t


class BezierCurve:
    """Calculates 2D bezier curves using quadratic interpolation

    The intermediate point, P1, always lies on the inverse diagonal o
    """
    def __init__(self):
        self.origin = Point2D(0, 0)
        self.next_point = Point2D(1, 0)

    def set_next_value(self, y):
        """Set the y value for the next time increment (0-1)
        """
        self.origin.y = self.next_point.y
        self.next_point.y = y

    def value_at(self, t, k):
        """Get the value of the bezier curve for a given time

        @param t  The time [0, 1]
        @param k  The curve constant, in the range [-1, 1]  See @interpolate for details on the curve constant
        """
        # Get 4 points on the curve so we can create a cubic equation for the curve
        p1 = self.interpolate(0, k)
        p2 = self.interpolate(1/3, k)
        p3 = self.interpolate(2/3, k)
        p4 = self.interpolate(1, k)

        # matrix representation
        m = [
            [p1.x**3, p1.x**2, p1.x, 1, p1.y],
            [p2.x**3, p2.x**2, p2.x, 1, p2.y],
            [p3.x**3, p3.x**2, p3.x, 1, p3.y],
            [p4.x**3, p4.x**2, p4.x, 1, p4.y],
        ]

        coeffs = solve_linear_system(m)
        return coeffs[0] * t**3 + coeffs[1] * t**2 + coeffs[2] * t + coeffs[3]


    def interpolate(self, t, k):
        """Calculate the 2D position for the given time

        See https://en.wikipedia.org/wiki/Bezier_curve#Cubic_curves for details on the math.

        @param t  The current interpolated time, between 0 and 1
        @param k  A constant indicating our progression from horizontal endpoints (smoothest) @ -1.0 to
                  linear @ 0.0 to vertical endpoints (spikiest) @ 1.0
        @return   The interpolated 2D point on the bezier curve
        """
        # Define 2 intermediate points, which are either horizontally or vertically aligned with the start and end points
        p0 = self.origin
        p1 = Point2D(0,0)
        p2 = Point2D(0,0)
        p3 = self.next_point

        if k <= 0:
            # start/endpoints aligned horizontally with intermediate points
            # /3 results in slightly smoother results; /2 was giving cusps on sharp peaks & valleys
            p1.x = p0.x - k/3
            p2.x = p3.x + k/3
            p1.y = p0.y
            p2.y = p3.y
        else:
            # start/endpoints aligned vertically with intermediate points
            p1.x = p0.x
            p2.x = p3.x

            dy = abs(p0.y - p3.y)

            if p0.y < p3.y:
                # p1 goes up, p2 goes down
                p1.y = p1.y + dy * k/2
                p2.y = p3.y - dy * k/2
            else:
                # p1 goes down, p2 goes up
                p1.y = p1.y - dy * k/2
                p2.y = p3.y + dy * k/2

        q0 = Point2D(
            linear_interpolate(p0.x, p1.x, t),
            linear_interpolate(p0.y, p1.y, t)
        )
        q1 = Point2D(
            linear_interpolate(p1.x, p2.x, t),
            linear_interpolate(p1.y, p2.y, t)
        )
        q2 = Point2D(
            linear_interpolate(p2.x, p3.x, t),
            linear_interpolate(p2.y, p3.y, t)
        )

        r0 = Point2D(
            linear_interpolate(q0.x, q1.x, t),
            linear_interpolate(q0.y, q1.y, t)
        )
        r1 = Point2D(
            linear_interpolate(q1.x, q2.x, t),
            linear_interpolate(q1.y, q2.y, t)
        )

        b = Point2D(
            linear_interpolate(r0.x, r1.x, t),
            linear_interpolate(r0.y, r1.y, t)
        )

        return b


class OutputChannel:
    """Wrapper for a CV output channel
    """
    def __init__(self, script, frequency_in, curve_in, cv_out):
        self.script = script
        self.curve = BezierCurve()

        self.cv_out = cv_out
        self.frequency_in = frequency_in
        self.curve_in = curve_in

        self.voltage_out = 0
        self.cv_out.off()
        self.last_tick_at = time.ticks_ms()
        self.change_voltage()

        self.frequency = 0.0
        self.curve_k = 0.0
        self.voltage_out = 0.0

        self.vizualization_samples = []

    def change_voltage(self):
        """Pick a random value between -0.1 and 1.1 and use it as the goal point for the bezier curve

        We intentionally overshoot the [0, 1] range in order to force the occasional effect from the clipping mode.
        """
        self.curve.set_next_value(random.random() * 1.2 - 0.1)

    def update(self, clip_mode=CLIP_MODE_LIMIT):
        now = time.ticks_ms()

        self.curve_k = self.curve_in.percent() * 2 -1  # [-1, 1]
        self.frequency = self.frequency_in.percent() * (self.script.config.MAX_FREQUENCY - self.script.config.MIN_FREQUENCY) + self.script.config.MIN_FREQUENCY

        if self.script.config.AIN_MODE == AIN_MODE_FREQUENCY:
            # increase the frequency according to the voltage on AIN
            self.frequency = self.frequency + ain.read_voltage() / self.script.config.MAX_INPUT_VOLTAGE * (self.script.config.MAX_FREQUENCY - self.script.config.MIN_FREQUENCY) + self.script.config.MIN_FREQUENCY
        elif self.script.config.AIN_MODE == AIN_MODE_CURVE:
            ain_k = ain.read_voltage() / self.script.config.MAX_INPUT_VOLTAGE * 2 -1  # [-1, 1]
            self.curve_k = (self.curve_k + ain_k) / 2

        t = 1000.0/self.frequency  # Hz -> ms

        elapsed_ms = time.ticks_diff(now, self.last_tick_at)
        if elapsed_ms >= t:
            self.change_voltage()
            self.last_tick_at = now
            elapsed_ms = 0

        self.voltage_out = self.curve.value_at(elapsed_ms / t, self.curve_k) * (self.script.config.MAX_VOLTAGE - self.script.config.MIN_VOLTAGE) + self.script.config.MIN_VOLTAGE

        if clip_mode == CLIP_MODE_LIMIT:
            self.voltage_out = self.clip_limit(self.voltage_out)
        elif clip_mode == CLIP_MODE_FOLD:
            self.voltage_out = self.clip_fold(self.voltage_out)
        elif clip_mode == CLIP_MODE_THRU:
            self.voltage_out = self.clip_thru(self.voltage_out)

        self.cv_out.voltage(self.voltage_out)

        self.vizualization_samples.append(int((self.voltage_out - self.script.config.MIN_VOLTAGE) / (self.script.config.MAX_VOLTAGE - self.script.config.MIN_VOLTAGE) * OLED_HEIGHT/3))
        if len(self.vizualization_samples) > OLED_WIDTH // 2:
            self.vizualization_samples.pop(0)

    def clip_limit(self, v):
        if v < self.script.config.MIN_VOLTAGE:
            return self.script.config.MIN_VOLTAGE
        elif v > self.script.config.MAX_VOLTAGE:
            return self.script.config.MAX_VOLTAGE
        else:
            return v

    def clip_fold(self, v):
        if v < self.script.config.MIN_VOLTAGE:
            return self.script.config.MIN_VOLTAGE - v
        elif v > self.script.config.MAX_VOLTAGE:
            return self.script.config.MAX_VOLTAGE + (self.script.config.MAX_VOLTAGE - v)
        else:
            return v

    def clip_thru(self, v):
        if v < self.script.config.MIN_VOLTAGE:
            return self.script.config.MAX_VOLTAGE - (self.script.config.MIN_VOLTAGE - v)
        elif v > self.script.config.MAX_VOLTAGE:
            return self.script.config.MIN_VOLTAGE - (self.script.config.MAX_VOLTAGE - v)
        else:
            return v


class Bezier(EuroPiScript):
    def __init__(self):
        super().__init__()

        cfg = self.load_state_json()

        self.frequency_in = (
            KnobBank.builder(k1)
            .with_unlocked_knob("channel_a")
            .with_locked_knob("channel_b", initial_percentage_value=cfg.get("channel_b_frequency", 0.5))
            .build()
        )

        self.curve_in = (
            KnobBank.builder(k2)
            .with_unlocked_knob("channel_a")
            .with_locked_knob("channel_b", initial_percentage_value=cfg.get("channel_b_curve", 0.5))
            .build()
        )

        # How do we handle clipping?
        self.clip_mode = cfg.get("clip_mode", CLIP_MODE_LIMIT)

        # How do we combine the gate outputs for cv6?
        if self.config.LOGIC_MODE == "and":
            self.gate_logic = LogicalAnd()
        elif self.config.LOGIC_MODE == "or":
            self.gate_logic = LogicalOr()
        elif self.config.LOGIC_MODE == "xor":
            self.gate_logic = LogicalXor()
        elif self.config.LOGIC_MODE == "nand":
            self.gate_logic = LogicalNand()
        elif self.config.LOGIC_MODE == "nor":
            self.gate_logic = LogicalNor()
        elif self.config.LOGIC_MODE == "xnor":
            self.gate_logic = LogicalXnor()
        else:
            raise Exception(f"Unknown logic mode {self.config.LOGIC_MODE}")

        # Are the settings dirty & need saving?
        self.settings_dirty = False

        self.curve_a = OutputChannel(self, self.frequency_in["channel_a"], self.curve_in["channel_a"], cv1)
        self.curve_b = OutputChannel(self, self.frequency_in["channel_b"], self.curve_in["channel_b"], cv2)

        # If DIN receives a signal, force the curves to change target value
        self.force_voltage_change = False

        @din.handler
        def on_din_rise():
            self.force_voltage_change = True

        @b1.handler
        def on_b1_press():
            self.clip_mode = (self.clip_mode + 1) % N_CLIP_MODES
            self.settings_dirty = True
            ssoled.notify_user_interaction()

        @b2.handler
        def on_b2_press():
            self.curve_in.set_current("channel_b")
            self.frequency_in.set_current("channel_b")
            ssoled.notify_user_interaction()

        @b2.handler_falling
        def on_b2_release():
            self.curve_in.set_current("channel_a")
            self.frequency_in.set_current("channel_a")
            self.settings_dirty = True
            ssoled.notify_user_interaction()

    @classmethod
    def config_points(cls):
        """Return the static configuration options for this class
        """
        def restrict_input_voltage(v):
            if v > europi_config.MAX_INPUT_VOLTAGE:
                return europi_config.MAX_INPUT_VOLTAGE
            return v

        return [
            configuration.floatingPoint(
                name="MAX_INPUT_VOLTAGE",
                minimum=0.0,
                maximum=europi_config.MAX_INPUT_VOLTAGE,
                default=restrict_input_voltage(10.0)
            ),
            configuration.floatingPoint(
                name="MIN_VOLTAGE",
                minimum=0.0,
                maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                default=0.0
            ),
            configuration.floatingPoint(
                name="MAX_VOLTAGE",
                minimum=0.0,
                maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                default=europi_config.MAX_OUTPUT_VOLTAGE
            ),
            configuration.floatingPoint(
                name="MIN_FREQUENCY",
                minimum=0.001,
                maximum=10.0,
                default=0.01
            ),
            configuration.floatingPoint(
                name="MAX_FREQUENCY",
                minimum=0.001,
                maximum=10.0,
                default=1.0
            ),
            configuration.choice(
                name="AIN_MODE",
                choices=["frequency", "curve"],
                default="frequency"
            ),
            configuration.choice(
                name="LOGIC_MODE",
                choices=["and", "or", "xor", "nand", "nor", "xnor"],
                default="xor"
            )
        ]

    def save(self):
        """Write the persistent settings file
        """
        cfg = {
            "channel_b_curve": self.curve_in["channel_b"].percent(),
            "channel_b_frequency": self.frequency_in["channel_b"].percent(),
            "clip_mode": self.clip_mode
        }
        self.save_state_json(cfg)
        self.settings_dirty = False

    def draw_graph(self, curve):
        # draw the live graphs
        for i in range(len(curve.vizualization_samples)):
            ssoled.pixel(i+OLED_WIDTH//2, OLED_HEIGHT - 1 - curve.vizualization_samples[i], 1)

    def main(self):
        GATE_DURATION = 0
        HALF_VOLTAGE = (self.config.MIN_VOLTAGE + self.config.MAX_VOLTAGE) / 2

        # Used to detect user interaction with the knobs
        UI_DEADZONE = 0.01
        prev_freq_value = self.frequency_in.current.percent()
        prev_curve_value = self.curve_in.current.percent()

        while True:
            now = time.ticks_ms()

            if self.force_voltage_change:
                self.force_voltage_change = False
                self.curve_a.change_voltage()
                self.curve_b.change_voltage()

            # set the main outputs, calculate the bezier curves
            self.curve_a.update()
            self.curve_b.update()

            # set cv3 to the average of the channels
            cv3.voltage((self.curve_a.voltage_out + self.curve_b.voltage_out) / 2)

            # set the trigger state for cv4
            if time.ticks_diff(now, self.curve_a.last_tick_at) <= GATE_DURATION:
                cv4.on()
                gate_a = True
            else:
                cv4.off()
                gate_a = False

            # set cv5 high/low, depending on the value of channel b
            if self.curve_b.voltage_out >= HALF_VOLTAGE:
                cv5.on()
                gate_b = True
            else:
                cv5.off()
                gate_b = False

            logic_gate_on = self.gate_logic.compare(gate_a, gate_b)
            if logic_gate_on:
                cv6.on()
            else:
                cv6.off()

            # save settings if needed
            if self.settings_dirty:
                self.save()

            # check if we've moved the knobs manually
            # Wake up from the screensaver if we have
            current_freq_value = self.frequency_in.current.percent()
            current_curve_value = self.curve_in.current.percent()
            if abs(current_freq_value - prev_freq_value) >= UI_DEADZONE or abs(current_curve_value - prev_curve_value) >= UI_DEADZONE:
                ssoled.notify_user_interaction()
            prev_freq_value = current_freq_value
            prev_curve_value = current_curve_value

            # UI:
            # +------------------------+
            # | A AA.AAHz  +kA.AA      |
            # | B BB.BBHz  -kB.BB      |
            # | Fold      ...--^-.--^  |
            # +------------------------+
            ssoled.fill(0)

            # Highlight either the first or second row to indicate it's being edited
            channel_a_active = self.curve_in.current == self.curve_in["channel_a"]

            if channel_a_active:
                ssoled.fill_rect(0, 0, OLED_WIDTH, CHAR_HEIGHT+2, 1)
            else:
                ssoled.fill_rect(0, CHAR_HEIGHT+1, OLED_WIDTH, CHAR_HEIGHT+2, 1)

            ssoled.text(f"A {self.curve_a.frequency:0.2f}Hz  {self.curve_a.curve_k:+0.2f}", 1, 1, 0 if channel_a_active else 1)
            ssoled.text(f"B {self.curve_b.frequency:0.2f}Hz  {self.curve_b.curve_k:+0.2f}", 1, CHAR_HEIGHT+2, 1 if channel_a_active else 0)
            ssoled.text(CLIP_MODE_NAMES[self.clip_mode], 1, 2*CHAR_HEIGHT + 4, 1)

            self.draw_graph(self.curve_a)
            self.draw_graph(self.curve_b)

            ssoled.show()

if __name__ == "__main__":
    Bezier().main()
