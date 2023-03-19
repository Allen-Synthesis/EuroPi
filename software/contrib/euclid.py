#!/usr/bin/env python3
"""Euclidean rhythm generator for the EuroPi

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@author Brian House
@year   2011, 2023

@license MIT
"""

from europi import *
from europi_script import EuroPiScript

def generate_euclidean_pattern(steps, pulses, rot=0):
    """Generates an array indicating the on/off steps of Euclid(k, n)

    Copied from https://github.com/brianhouse/bjorklund with all due gratitude

    @param steps  The number of steps in the pattern
    @param pulses The number of ON steps in the pattern (must be <= steps)
    @param rot    Optional rotation to offset the pattern. Must be in the range [0, steps-1]
    
    @return An int array of length steps consisting of 1 and 0 values only
    
    @exception ValueError if pulses or rot is out of range
    
    @license MIT -- https://github.com/brianhouse/bjorklund/blob/master/LICENSE.txt
    """
    steps = int(steps)
    pulses = int(pulses)
    rot = int(rot)
    if pulses > steps or pulses < 0:
        raise ValueError
    if rot >= steps or steps < 0:
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
        
        ## The on/off pattern we generate
        self.pattern = []
        
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
            self.cv.on()
        

class EuclideanRhythms(EuroPiScript):
    """Generates 6 different Euclidean rhythms, one per output

    Must be clocked externally into DIN
    """
    
    def __init__(self):
        super().__init__()
        
        self.generators = [
            EuclidGenerator(cv1),
            EuclidGenerator(cv2),
            EuclidGenerator(cv3),
            EuclidGenerator(cv4),
            EuclidGenerator(cv5),
            EuclidGenerator(cv6)
        ]
        
        self.load()
        
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
            pass
            
        @b2.handler
        def on_b2_press():
            """Handler for pressing button 2
            """
            pass
        
    @classmethod
    def display_name(cls):
        return "Euclid"
        
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
            }
            state.append(d)
        self.save_state_json(state)
        
    def main(self):
        while True:
            # TODO: implement the UI logic
            # for now, just sleep forever
            time.sleep(0.01)
    
if __name__=="__main__":
    EuclideanRhythms().main()