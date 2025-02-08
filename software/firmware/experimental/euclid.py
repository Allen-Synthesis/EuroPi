# COPYRIGHT 2011 Brian House
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the “Software”), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


def generate_euclidean_pattern(steps, pulses, rot=0):
    """Generates an array indicating the on/off steps of Euclid(k, n)

    Copied from https://github.com/brianhouse/bjorklund with all due gratitude

    @param steps  The number of steps in the pattern
    @param pulses The number of ON steps in the pattern (must be <= steps)
    @param rot    Optional rotation to offset the pattern. Must be in the range [0, steps]

    @return An int array of length steps consisting of 1 and 0 values only

    @exception ValueError if pulses or rot is out of range

    @author Brian House
    @year 2011
    @license MIT
    """
    steps = int(steps)
    pulses = int(pulses)
    rot = int(rot)
    if pulses > steps:
        raise ValueError("Pulses cannot be greater than steps")
    if pulses < 0:
        raise ValueError("Pulses must be positive")
    if rot > steps:
        raise ValueError("Rotation cannot be greater than steps")
    if steps < 0:
        raise ValueError("Steps must be positive")
    if steps == 0:
        return []
    if pulses == 0:
        return [0] * steps
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
