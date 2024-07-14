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
            configuration.choice(name="AIN_MODE", choices=["frequency", "curve"], default="frequency"),
            configuration.choice(name="LOGIC_MODE", choices=["and", "or", "xor", "nand", "nor", "xnor"], default="xor")
        ]

    def save(self):
        """Write the persistent settings file
        """
        cfg = {

        }
        self.save_settings_json(cfg)
        self.settings_dirty = False

    def main(self):
        while True:
            if self.settings_dirty:
                self.save()

if __name__ == "__main__":
    Bezier().main()
