#!/usr/bin/env python3
"""Euclidean rhythm generator for the EuroPi

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@author Brian House
@year   2011, 2023

This script contains code released under the MIT license, as
noted below
"""

import random
import time

from europi import *
from europi_script import EuroPiScript

from experimental.euclid import generate_euclidean_pattern
from experimental.screensaver import Screensaver


class EuclidGenerator:
    """Generates the euclidean rhythm for a single output
    """

    def __init__(self, cv_out, steps=1, pulses=0, rotation=0, skip=0):
        """Create a generator that sends its output to the given CV output

        @param cv_out  One of the six output jacks (cv1..cv6)
        @param steps  The initial number of steps (1-32)
        @param pulses  The initial number of pulses (0-32)
        @param rotation  The initial rotation (0-32)
        @param skip  The skip probability (0-1)
        """

        ## The CV output this generator controls
        self.cv = cv_out

        ## The current position within the pattern
        self.position = 0

        ## The number of steps in the pattern
        self.steps = steps

        ## The number of triggers in the pattern
        self.pulses = pulses

        ## The rotation of the pattern
        self.rotation = rotation

        ## The probability that we skip any given step when it triggers
        #
        #  Must be in the range [0, 1], where 0 means never skip and
        #  1 means always skip
        self.skip = skip

        ## The on/off pattern we generate
        self.pattern = []

        ## Cached copy of the string representation
        #
        #  __str__(self) will do some extra string processing
        #  if this is None; otherwise its value is simply returned
        self.str = None

        self.regenerate()

    def __str__(self):
        """Return a string representation of the pattern

        The string consists of 4 characters:
            - ^ current beat, high
            - v current beat, low
            - | high beat
            - . low beat

        e.g. |.|.^|.|.||. is a 7/12 pattern, where the 5th note
        is currently playing
        """

        if self.str is None:
            s = ""
            for i in range(len(self.pattern)):
                if i == self.position:
                    if self.pattern[i] == 0:
                        s = s+"v"
                    else:
                        s = s+"^"
                else:
                    if self.pattern[i] == 0:
                        s = s+"."
                    else:
                        s = s+"|"
            self.str = s
        return self.str

    def regenerate(self):
        """Re-calculate the pattern for this generator

        Call this after changing any of steps, pulses, or rotation to apply
        the changes.

        Changing the pattern will reset the position to zero
        """

        self.position = 0
        self.pattern = generate_euclidean_pattern(self.steps, self.pulses, self.rotation)

        # clear the cached string representation
        self.str = None

    def advance(self):
        """Advance to the next step in the pattern and set the CV output
        """

        # advance the position
        # to ease CPU usage don't do any divisions, just reset to zero
        # if we overflow
        self.position = self.position+1
        if self.position >= len(self.pattern):
            self.position = 0

        if self.steps == 0 or self.pattern[self.position] == 0:
            self.cv.off()
        else:
            if self.skip > random.random():
                self.cv.off()
            else:
                self.cv.on()

        # clear the cached string representation
        self.str = None


class ChannelMenu:
    """A menu screen that lets us choose which CV channel to edit
    """
    def __init__(self, script):
        """Create the channel menu

        @param script  The EuclideanRhythms script that owns this menu
        """
        self.script = script
        self.first_render = True

        self.generator_index = None
        self.k2_percent = None
        self.read_knobs()

    def read_knobs(self):
        """Read the current state of the knobs and return whether or not the state has changed, requiring a re-render

        @return True if we should re-render the GUI, False if we can keep the previous render
        """
        index = k1.range(len(self.script.generators))
        percent = round(k2.percent() * 100)
        dirty = (
            self.generator_index != index or
            self.k2_percent != percent
        )
        if dirty:
            self.generator_index = index
            self.k2_percent = percent

        return dirty or self.first_render

    def draw(self):
        self.first_render = False
        g = self.script.generators[self.generator_index]
        pattern_str = str(g)

        oled.fill(0)
        oled.text(f"-- CV {self.generator_index+1} --", 0, 0)
        if len(pattern_str) > 16:
            pattern_row1 = pattern_str[0:16]
            pattern_row2 = pattern_str[16:]
            oled.text(f"{pattern_row1}", 0, 10)
            oled.text(f"{pattern_row2}", 0, 20)
        else:
            oled.text(f"{pattern_str}", 0, 10)

        oled.show()

class SettingsMenu:
    """A menu screen for controlling a single setting of the generator
    """
    def __init__(self, script):
        """Create the settings menu for a given generator

        @param script  The EuclideanRhythms script that owns this menu
        """
        self.script = script
        self.generator = script.generators[0]

        self.MENU_ITEMS_STEPS = 0
        self.MENU_ITEMS_PULSES = 1
        self.MENU_ITEMS_ROTATION = 2
        self.MENU_ITEMS_SKIP = 3
        self.menu_items = [
            "Steps",
            "Pulses",
            "Rot.",
            "Skip %"
        ]

        self.first_render = True

        self.menu_item = None
        self.lower_bound = None
        self.upper_bound = None
        self.current_setting = None
        self.new_setting = None
        self.read_knobs()

    def set_generator(self, g):
        """Configure this menu to control a given EuclideanGenerator

        @param g  The EuclideanGenerator to control
        """
        self.generator = g

    def read_knobs(self):
        """Returns a tuple with the current options

        @return True if the user has moved any inputs, requiring a re-render. Otherwise False
        """
        menu_item = k1.range(len(self.menu_items))
        lower_bound = 0
        upper_bound = 0
        current_setting = 0

        if menu_item == self.MENU_ITEMS_STEPS:
            lower_bound = 1
            upper_bound = 32
            current_setting = self.generator.steps
        elif menu_item == self.MENU_ITEMS_PULSES:
            lower_bound = 0
            upper_bound = self.generator.steps
            current_setting = self.generator.pulses
        elif menu_item == self.MENU_ITEMS_ROTATION:
            lower_bound = 0
            upper_bound = self.generator.steps
            current_setting = self.generator.rotation
        elif menu_item == self.MENU_ITEMS_SKIP:
            lower_bound = 0
            upper_bound = 100
            current_setting = int(self.generator.skip * 100)

        new_setting = k2.range(upper_bound-lower_bound+1) + lower_bound

        dirty = (
            self.menu_item != menu_item or
            self.lower_bound != lower_bound or
            self.upper_bound != upper_bound or
            self.current_setting != current_setting or
            self.new_setting != new_setting
        )

        if dirty:
            self.menu_item = menu_item
            self.lower_bound = lower_bound
            self.upper_bound = upper_bound
            self.current_setting = current_setting
            self.new_setting = new_setting

        return dirty or self.first_render

    def draw(self):
        self.first_render = False
        oled.fill(0)
        oled.text(f"-- {self.menu_items[self.menu_item]} --", 0, 0)
        oled.text(f"{self.current_setting} <- {self.new_setting}", 0, 10)
        oled.show()

    def apply_setting(self):
        """Apply the current setting
        """
        if self.menu_item == self.MENU_ITEMS_STEPS:
            self.generator.steps = self.new_setting
            if self.generator.pulses > self.new_setting:
                self.generator.pulses = self.new_setting
            if self.generator.rotation > self.new_setting:
                self.generator.rotation = self.new_setting
        elif self.menu_item == self.MENU_ITEMS_PULSES:
            self.generator.pulses = self.new_setting
        elif self.menu_item == self.MENU_ITEMS_ROTATION:
            self.generator.rotation = self.new_setting
        elif self.menu_item == self.MENU_ITEMS_SKIP:
            self.generator.skip = self.new_setting / 100.0

        self.generator.regenerate()


class EuclideanRhythms(EuroPiScript):
    """Generates 6 different Euclidean rhythms, one per output

    Must be clocked externally into DIN
    """

    def __init__(self):
        super().__init__()

        ## The euclidean pattern generators for each CV output
        #
        #  We pre-load the defaults with some interesting patterns so the script
        #  does _something_ out of the box
        self.generators = [
            EuclidGenerator(cv1, 8, 5),
            EuclidGenerator(cv2, 16, 7),
            EuclidGenerator(cv3, 16, 11),
            EuclidGenerator(cv4, 32, 9),
            EuclidGenerator(cv5, 32, 15),
            EuclidGenerator(cv6, 32, 19)
        ]

        self.load()

        # Do we need to save the current settings?
        self.settings_dirty = False

        # Do we need to re-draw the GUI?
        self.ui_dirty = True

        self.last_user_interaction_at = time.ticks_ms()

        self.channel_menu = ChannelMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.screensaver = Screensaver()

        self.active_screen = self.channel_menu

        @din.handler
        def on_rising_clock():
            """Handler for the rising edge of the input clock

            Advance all of the rhythms
            """
            for g in self.generators:
                g.advance()
            self.ui_dirty = True

        @din.handler_falling
        def on_falling_clock():
            """Handler for the falling edge of the input clock

            Turn off all of the CVs so we don't stay on for adjacent pulses
            """
            turn_off_all_cvs()

        @b1.handler
        def on_b1_press():
            """Handler for pressing button 1
            """
            self.ui_dirty = True
            self.last_user_interaction_at = time.ticks_ms()

            if self.active_screen == self.channel_menu:
                self.activate_settings_menu()
            else:
                self.settings_menu.apply_setting()
                self.settings_dirty = True

        @b2.handler
        def on_b2_press():
            """Handler for pressing button 2
            """
            self.ui_dirty = True
            self.last_user_interaction_at = time.ticks_ms()

            if self.active_screen == self.channel_menu:
                self.activate_settings_menu()
            else:
                self.activate_channel_menu()

    @classmethod
    def display_name(cls):
        return "Euclid"

    def activate_settings_menu(self):
        """ Change the active screen to the settings menu
        """
        channel_index = k1.range(len(self.generators))
        self.settings_menu.set_generator(self.generators[channel_index])
        self.active_screen = self.settings_menu

    def activate_channel_menu(self):
        """Change the active screen to the CV channel menu
        """
        self.active_screen = self.channel_menu

    def load(self):
        """Load the previously-saved parameters and restore them
        """
        state = self.load_state_json()

        for rhythm in state.get("rhythms", []):
            id = rhythm["id"]
            generator = self.generators[id]

            generator.steps = rhythm["steps"]
            generator.pulses = rhythm["pulses"]
            generator.rotation = rhythm["rotation"]
            generator.skip = rhythm["skip"]

            generator.regenerate()

    def save(self):
        """Write the current settings to the persistent storage
        """
        rhythms = []
        for i in range(len(self.generators)):
            d = {
                "id": i,
                "steps": self.generators[i].steps,
                "pulses": self.generators[i].pulses,
                "rotation": self.generators[i].rotation,
                "skip": self.generators[i].skip
            }
            rhythms.append(d)

        state = {
            "rhythms": rhythms
        }
        self.save_state_json(state)

    def main(self):
        while True:
            now = time.ticks_ms()

            if self.settings_dirty:
                self.settings_dirty = False
                self.save()

            if self.active_screen.read_knobs():
                self.last_user_interaction_at = now
                self.ui_dirty = True

            if time.ticks_diff(now, self.last_user_interaction_at) >= self.screensaver.ACTIVATE_TIMEOUT_MS:
                self.last_user_interaction_at = time.ticks_add(now, -self.screensaver.ACTIVATE_TIMEOUT_MS)
                self.screensaver.draw()
            elif self.ui_dirty:
                self.ui_dirty = False
                self.active_screen.draw()

if __name__=="__main__":
    EuclideanRhythms().main()
