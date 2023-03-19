#!/usr/bin/env python3
"""Euclidean rhythm generator for the EuroPi

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@author Brian House
@year   2023
"""

def generate_euclidean_pattern(steps, pulses, rot=0):
    """Generates an array indicating the on/off steps of Euclid(k, n)

    Copied from https://github.com/brianhouse/bjorklund with all due gratitude

    @param steps  The number of steps in the pattern
    @param pulses The number of ON steps in the pattern (must be <= steps)
    @param rot    Optional rotation to offset the pattern. Must be in the range [0, steps-1]
    
    @return An int array of length steps consisting of 1 and 0 values only
    
    @exception ValueError if pulses or rot is out of range
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

class EuclideanRhythms(EuroPiScript):
    