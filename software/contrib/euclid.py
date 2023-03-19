#!/usr/bin/env python3
"""Euclidean rhythm generator for the EuroPi

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@author Brian House
@year   2011, 2023

@license MIT
"""

from europi import *
from europi_script import EuroPiScript

import random
import time

def generate_euclidean_pattern(steps, pulses, rot=0):
    """Generates an array indicating the on/off steps of Euclid(k, n)

    Copied from https://github.com/brianhouse/bjorklund with all due gratitude

    @param steps  The number of steps in the pattern
    @param pulses The number of ON steps in the pattern (must be <= steps)
    @param rot    Optional rotation to offset the pattern. Must be in the range [0, steps]
    
    @return An int array of length steps consisting of 1 and 0 values only
    
    @exception ValueError if pulses or rot is out of range
    
    @license MIT -- https://github.com/brianhouse/bjorklund/blob/master/LICENSE.txt
    """
    steps = int(steps)
    pulses = int(pulses)
    rot = int(rot)
    if pulses > steps or pulses < 0:
        raise ValueError
    if rot > steps or steps < 0:
        raise ValueError
    pattern = []    
    counts = []
    remainders = []
    divisor = steps - pulses
    remainders.append(pulses)
    level = 0
    while True:
        counts.append(divisor // remainders[level])
        remainders.append(divisor % remainders[level])
        divisor = remainders[level]
        level = level + 1
        if remainders[level] <= 1:
            break
    counts.append(divisor)
    
    def build(level):
        if level == -1:
            pattern.append(0)
        elif level == -2:
            pattern.append(1)         
        else:
            for i in range(0, counts[level]):
                build(level - 1)
            if remainders[level] != 0:
                build(level - 2)
    
    build(level)
    i = pattern.index(1)
    pattern = pattern[i:] + pattern[0:i]
    
    # rotate the pattern if needed by removing the last item and
    # adding it to the start
    if rot != 0:
        for i in range(rot):
            x = pattern.pop(-1)
            pattern.insert(0, x)
    
    return pattern

class EuclidGenerator:
    """Generates the euclidean rhythm for a single output
    """
    
    def __init__(self, cv_pin):
        """Create a generator that sends its output to the given pin

        @param cv_pin  One of the six output jacks (cv1..cv6)
        """
        
        ## The CV output this generator controls
        self.cv = output_pin
        
        ## The current position within the pattern
        self.position = 0
        
        ## The number of steps in the pattern
        self.steps = 0
        
        ## The number of triggers in the pattern
        self.pulses = 0
        
        ## The rotation of the pattern
        self.rotation = 0
        
        ## The probability that we skip any given step when it triggers
        #
        #  Must be in the range [0, 1], where 0 means never skip and
        #  1 means always skip
        self.skip = 0
        
        ## The on/off pattern we generate
        self.pattern = []
        
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
        s = ""
        for i in range(len(self.pattern))
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
        return s
        
    def regenerate(self):
        """Re-calculate the pattern for this generator

        Call this after changing any of steps, pulses, or rotation to apply
        the changes.
        
        Changing the pattern will reset the position to zero
        """
        
        self.pattern = generate_euclidean_pattern(self.steps, self.pulses, self.rotation)
        self.position = 0
        
    def advance(self):
        """Advance to the next step in the pattern and set the CV output
        """
        
        # advance the position
        # to ease CPU usage don't do any divisions, just reset to zero
        # if we overflow
        self.position = self.position+1
        if self.position >= len(self.pattern):
            self.position = 0
            
        if self.pattern[self.position] == 0:
            self.cv.off()
        else:
            if self.skip > random.random():
                self.cv.off()
            else:
                self.cv.on()
        

class ChannelMenu:
    """A menu screen that lets us choose which CV channel to edit
    """
    def __init__(self, script):
        """Create the channel menu

        @param script  The EuclideanRhythms script that owns this menu
        """
        self.script = script
        
    def draw(self):
        generator_index = k1.range(len(self.script.generators))
        g = self.script.generators[generator_index]
        
        oled.fill(0)
        oled.text(f"-- CV {generator_index+1} --", 0, 0)
        oled.text(f"{g}", 0, 10)
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
        
    def set_generator(self, g):
        """Configure this menu to control a given EuclideanGenerator

        @param g  The EuclideanGenerator to control
        """
        self.generator = g
        
    def read_knobs(self):
        """Returns a tuple with the current options

        @return a tuple of the form (menu_item, lower_bound, upper_bound, current_setting, new_setting)
        """
        
        menu_item = k1.range(len(self.menu_items))
        lower_bound = 0
        upper_bound = 0
        current_setting = 0
        
        if menu_item == self.MENU_ITEMS_STEPS:
            lower_bound = 0
            upper_bound = 32
            current_setting = self.generator.steps
        elif menu_item == self.MENU_ITEMS_PULSES:
            lower_bound = 0
            upper_bound = self.generator.steps
            current_setting = self.generator.pulses
        elif menu_item == self.MENU_ITEM.ROTATION:
            lower_bound = 0
            upper_bound = self.generator.steps
            current_setting = self.generator.rotation
        elif menu_item == self.MENU_ITEM_SKIP:
            lower_bound = 0
            upper_bound = 100
            current_setting = int(self.generator.skip * 100)
            
        new_setting = k2.range(upper_bound-lower_bound+1) + lower_bound
        
        return (menu_item, lower_bound, upper_bound, current_setting, new_setting)
        
    def draw(self):
        (menu_item, lower_bound, upper_bound, current_setting, new_setting) = self.read_knobs()
        
        oled.fill(0)
        oled.text(f"-- {self.menu_items[menu_item]} --", 0, 0)
        oled.text(f"{current_setting} <- {new_setting}", 0, 10)
        oled.show()
        
    def apply_setting(self):
        """Apply the current setting
        """
        (menu_item, lower_bound, upper_bound, current_setting, new_setting) = self.read_knobs()
        
        if menu_item == self.MENU_ITEMS_STEPS:
            self.generator.steps = new_setting
            if self.generator.pulses > new_setting:
                self.generator.pulses = new_setting
            if self.generator.rotation > new_setting:
                self.generator.rotation = new_setting
        elif menu_item == self.MENU_ITEMS_PULSES:
            self.generator.pulses = new_setting
        elif menu_item == self.MENU_ITEM.ROTATION:
            self.generator.rotation = new_setting
        elif menu_item == self.MENU_ITEM_SKIP:
            self.generator.skip = new_setting / 100.0
            
        self.generator.regenerate()
        

class EuclideanRhythms(EuroPiScript):
    """Generates 6 different Euclidean rhythms, one per output

    Must be clocked externally into DIN
    """
    
    def __init__(self):
        super().__init__()
        
        ## The euclidean pattern generators for each CV output
        self.generators = [
            EuclidGenerator(cv1),
            EuclidGenerator(cv2),
            EuclidGenerator(cv3),
            EuclidGenerator(cv4),
            EuclidGenerator(cv5),
            EuclidGenerator(cv6)
        ]
        
        self.load()
        
        self.cv_menu = ChannelMenu(self)
        self.settings_menu = SettingsMenu(self)
        
        self.active_screen = self.cv_menu
        
        @din.handler
        def on_rising_clock():
            """Handler for the rising edge of the input clock

            Advance all of the rhythms
            """
            for g in self.generators:
                g.advance()
                
        @din.handler_falling
        def on_falling_clock():
            """Handler for the falling edge of the input clock

            Turn off all of the CVs so we don't stay on for adjacent pulses
            """
            for cv in cvs:
                cv.off()
            
        @b1.handler
        def on_b1_press():
            """Handler for pressing button 1
            """
            if self.active_screen == self.cv_menu:
                self.activate_settings_menu()
            else:
                self.settings_menu.apply_setting()
                self.save()
            
        @b2.handler
        def on_b2_press():
            """Handler for pressing button 2
            """
            if self.active_screen == self.cv_menu:
                self.activate_settings_menu()
            else:
                self.activate_channel_menu()
        
    @classmethod
    def display_name(cls):
        return "Euclid"
    
    def active_settings_menu(self):
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
        state = []
        for i in range(len(self.generators)):
            d = {
                "id": i,
                "steps": self.generators[i].steps,
                "pulses": self.generators[i].pulses,
                "rotation": self.generators[i].rotation,
                "skip": self.generators[i].skip
            }
            state.append(d)
        self.save_state_json(state)
        
    def main(self):
        while True:
            self.active_screen.draw()
    
if __name__=="__main__":
    EuclideanRhythms().main()