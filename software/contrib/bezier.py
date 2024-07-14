#!/usr/bin/env python3
"""
Generates random voltages based on Bezier curves

Inspired by Addac Systems' & Monotrail's ADDAC507 collaboration
"""

from europi import *
from europi_script import EuroPiScript

from experimental.knobs import *

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


class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x},{self.y}"


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

    def interpolate(self, t, k):
        """Calculate the 2D position for the given time

        See https://en.wikipedia.org/wiki/Bezier_curve#Cubic_curves for details on the math.

        @param t  The current interpolated time, between 0 and 1
        @param k  A constant indicating our progression from horizontal endpoints (smoothest) @ 0.0 to
                  linear @ 0.5 to vertical endpoints (spikiest) @ 1.0
        @return   The interpolated 2D point on the bezier curve
        """
        # calculate everything as if we're going from 0 to 1, and then invert/rescale as needed
        sin_x = math.sin(math.pi/2 * k)
        cos_x = math.cos(math.pi/2 * k)
        c1 = 0
        c2 = 0.5 * cos_x
        c3 = 1.0 - 0.5 * cos_x
        c4 = 1
        v1 = 0
        v4 = 1
        v2 = v1 + 0.5 * sin_x
        v3 = v4 - 0.5 * sin_x
        def X(t):
            return (1-t)**3 * c1 + 3 * t * (1-t)**2 * c2 + 3 * t**2 * (1-t)*c3 + t**3 * c4
        def Y(t):
            return (1-t)**3 * v1 + 3 * t * (1-t)**2 * v2 + 3 * t**2 * (1-t) * v3 + t**3 * v4
        q = Point2D(X(t), Y(t))

        # invert vertically if needed
        if self.next_point.y < self.origin.y:
            q.y = 1.0 - q.y

        # re-scale the Y axis
        q.y = rescale(q.y, 0, 1, min(self.origin.y, self.next_point.y), max(self.origin.y, self.next_point.y))

        return q


class Bezier(EuroPiScript):
    def __init__(self):
        super().__init__()

        cfg = self.load_settings_json()

        self.frequency_in = (
            KnobBank.builder(k2)
            .with_unlocked_knob("channel_a")
            .with_locked_knob("channel_b", initial_percentage_value=cfg.get("channel_b_freq", 0.5))
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

        # Do we need to re-render the GUI?
        self.ui_dirty = True

        @b1.handler
        def on_b1_press():
            self.clip_mode = (self.clip_mode + 1) % N_CLIP_MODES
            self.settings_dirty = True

        @b2.handler
        def on_b2_press():
            self.curve_in.next()
            self.frequency_in.next()

        @b2.handler_falling
        def on_b2_release():
            self.curve_in.next()
            self.frequency_in.next()
            self.settings_dirty = True

    @classmethod
    def config_points(cls):
        """Return the static configuration options for this class
        """
        return [
            configuration.floatingPoint(name="MIN_VOLTAGE", minimum=0.0, maximum=europi_config.MAX_OUTPUT_VOLTAGE, default=0.0),
            configuration.floatingPoint(name="MAX_VOLTAGE", minimum=0.0, maximum=europi_config.MAX_OUTPUT_VOLTAGE, default=europi_config.MAX_OUTPUT_VOLTAGE),
            configuration.floatingPoint(name="MIN_FREQUENCY", minimum=0.001, maximum=10.0, default=0.01),
            configuration.floatingPoint(name="MAX_FREQUENCY", minimum=0.001, maximum=10.0, default=1.0),
            configuration.choice(name="AIN_MODE", choices=["frequency", "curve"], default="frequency"),
            configuration.choice(name="LOGIC_MODE", choices=["and", "or", "xor", "nand", "nor", "xnor"], default="xor")
        ]

    def save(self):
        """Write the persistent settings file
        """
        cfg = {
            "channel_b_curve": self.curve_in["channel_b"].percent(),
            "channel_b_frequency": self.frequency_in_in["channel_b"].percent(),
            "clip_mode": self.clip_mode
        }
        self.save_settings_json(cfg)
        self.settings_dirty = False

    def main(self):
        while True:
            if self.settings_dirty:
                self.save()

if __name__ == "__main__":
    Bezier().main()
