#!/usr/bin/env python3
# Copyright 2023 Allen Synthesis
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
"""Euclidean rhythm generator for the EuroPi

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@year   2023
"""

import random
import time

from europi import *
from europi_script import EuroPiScript

from experimental.euclid import generate_euclidean_pattern
from experimental.screensaver import Screensaver
from experimental.settings_menu import *


class EuclidGenerator:
    """Generates the euclidean rhythm for a single output
    """

    def __init__(self, cv_out, name, steps=1, pulses=0, rotation=0, skip=0):
        """Create a generator that sends its output to the given CV output

        @param cv_out  One of the six output jacks (cv1..cv6)
        @param steps  The initial number of steps (1-32)
        @param pulses  The initial number of pulses (0-32)
        @param rotation  The initial rotation (0-32)
        @param skip  The skip probability (0-1)
        """
        setting_prefix = name.lower()

        self.rotatation = None
        self.pulses = None
        self.steps = None

        self.steps = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"{setting_prefix}_steps",
                1,
                32,
                steps,
            ),
            prefix = name,
            title = "Steps",
            callback = self.update_steps,
            autoselect_cv = True,
            autoselect_knob = True,
        )

        self.rotation = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"{setting_prefix}_rotation",
                0,
                32,
                rotation,
            ),
            prefix = name,
            title = "Rotation",
            callback = self.update_rotation,
            autoselect_cv = True,
            autoselect_knob = True,
        )

        self.pulses = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"{setting_prefix}_pulses",
                0,
                32,
                pulses,
            ),
            prefix = name,
            title = "Pulses",
            callback = self.update_pulses,
            autoselect_cv = True,
            autoselect_knob = True,
        )

        self.skip = SettingMenuItem(
            config_point = IntegerConfigPoint(
                f"{setting_prefix}_skip_prob",
                0,
                100,
                skip,
            ),
            prefix = name,
            title = "Skip %",
            autoselect_cv = True,
            autoselect_knob = True,
        )

        ## The CV output this generator controls
        self.cv = cv_out

        ## The name for this channel
        self.name = name

        ## The current position within the pattern
        self.position = 0

        ## The on/off pattern we generate
        self.pattern = []

        ## Cached copy of the string representation
        #
        #  __str__(self) will do some extra string processing
        #  if this is None; otherwise its value is simply returned
        self.str = None

        # Initialize the pattern
        self.update_steps(self.steps.value, 0, None, None)
        self.regenerate()

    def update_steps(self, new_steps, old_steps, config_point, arg=None):
        """Update the max range of pulses & rotation to match the number of steps
        """
        self.pulses.modify_choices(choices=list(range(new_steps+1)), new_default=new_steps)
        self.rotation.modify_choices(choices=list(range(new_steps+1)), new_default=new_steps)

        self.regenerate()

    def update_pulses(self, new_pulses, old_pulses, config_point, arg=None):
        self.regenerate()

    def update_rotation(self, new_rot, old_rot, config_point, arg=None):
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
        self.pattern = generate_euclidean_pattern(self.steps.value, self.pulses.value, self.rotation.value)

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
            if self.skip.value / 100 > random.random():
                self.cv.off()
            else:
                self.cv.on()

        # clear the cached string representation
        self.str = None


class EuclidVisualization(MenuItem):
    """A  menu item for displaying a specific Euclidean channel
    """

    def __init__(self, generator, children=None, parent=None):
        super().__init__(children=children, parent=parent)

        self.generator = generator

    def draw(self, oled=oled):
        pattern_str = str(self.generator)
        oled.text(f"-- {self.generator.name} --", 0, 0)
        if len(pattern_str) > 16:
            pattern_row1 = pattern_str[0:16]
            pattern_row2 = pattern_str[16:]
            oled.text(f"{pattern_row1}", 0, 10)
            oled.text(f"{pattern_row2}", 0, 20)
        else:
            oled.text(f"{pattern_str}", 0, 10)


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
            EuclidGenerator(cv1, "CV1", 8, 5),
            EuclidGenerator(cv2, "CV2", 16, 7),
            EuclidGenerator(cv3, "CV3", 16, 11),
            EuclidGenerator(cv4, "CV4", 32, 9),
            EuclidGenerator(cv5, "CV5", 32, 15),
            EuclidGenerator(cv6, "CV6", 32, 19)
        ]

        menu_items = []
        for i in range(len(self.generators)):
            menu_items.append(
                EuclidVisualization(
                    self.generators[i],
                    children = [
                        self.generators[i].steps,
                        self.generators[i].pulses,
                        self.generators[i].rotation,
                        self.generators[i].skip,
                    ]
                )
            )

        self.menu = SettingsMenu(
            navigation_knob = k2,
            navigation_button = b2,
            menu_items = menu_items,
            short_press_cb = self.on_menu_short_press,
            long_press_cb = self.on_menu_long_press
        )
        self.menu.load_defaults(self._state_filename)

        # Is the visualization stale (i.e. have we received a pulse and not updated the visualization?)
        self.viz_dirty = True

        self.screensaver = Screensaver()

        self.last_user_interaction_at = time.ticks_ms()

        @din.handler
        def on_rising_clock():
            """Handler for the rising edge of the input clock

            Advance all of the rhythms
            """
            for g in self.generators:
                g.advance()
            self.viz_dirty = True

        @din.handler_falling
        def on_falling_clock():
            """Handler for the falling edge of the input clock

            Turn off all of the CVs so we don't stay on for adjacent pulses
            """
            turn_off_all_cvs()

        @b1.handler
        def on_b1_press():
            """Handler for pressing button 1

            Advance all of the rhythms
            """
            self.last_user_interaction_at = time.ticks_ms()
            for g in self.generators:
                g.advance()
            self.viz_dirty = True

        @b1.handler_falling
        def on_b1_release():
            """Handler for releasing button 1

            Turn off all of the CVs so we don't stay on for adjacent pulses
            """
            self.last_user_interaction_at = time.ticks_ms()
            turn_off_all_cvs()

    def on_menu_long_press(self):
        self.last_user_interaction_at = time.ticks_ms()

    def on_menu_short_press(self):
        self.last_user_interaction_at = time.ticks_ms()

    def main(self):

        # manually check the state of k1 since it's otherwise not used, but should
        # disable the screensaver
        prev_k1 = int(k1.percent() * 100)

        while True:
            now = time.ticks_ms()

            current_k1 = int(k1.percent() * 100)
            if current_k1 != prev_k1:
                self.last_user_interaction_at = now
                prev_k1 = current_k1

            if self.menu.ui_dirty:
                self.last_user_interaction_at = now

            if time.ticks_diff(now, self.last_user_interaction_at) >= self.screensaver.ACTIVATE_TIMEOUT_MS:
                self.last_user_interaction_at = time.ticks_add(now, -self.screensaver.ACTIVATE_TIMEOUT_MS)
                self.screensaver.draw()
            else:
                if self.viz_dirty or self.menu.ui_dirty:
                    self.viz_dirty = False
                    oled.fill(0)
                    self.menu.draw()
                    oled.show()

            if self.menu.settings_dirty:
                self.menu.save(self._state_filename)

if __name__=="__main__":
    EuclideanRhythms().main()
