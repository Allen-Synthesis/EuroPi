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
"""Implements Conway's Game of Life as a pseudo-random LFO kernel

Outputs 1-3 are 0-10V control voltages, outputs 4-6 are 5V gates

@author Chris I-B <ve4cib@gmail.com>
@year   2023
"""

from europi import *
from europi_script import EuroPiScript
from experimental.bitarray import *
from random import random as rnd

import micropython

import math
import array

# @micropython.native
# Docs: https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#the-native-code-emitter

# @micropython.viper
# Docs: https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#the-viper-code-emitter

# We re-use this constant a lot, so just save it for easy re-use
LOG2 = math.log(2)

# How many pixels are on the screen
NUM_PIXELS = OLED_HEIGHT * OLED_WIDTH

# Pre-calculate these for performance
OLED_WIDTH_BYTES = OLED_WIDTH // 8
if OLED_WIDTH % 8:
    OLED_WIDTH_BYTES += 1

@micropython.native
def stdev(l):
    """Return the standard deviation of a list of values

    @param l  The list of numbers we want to calculate the standard deviation of

    @return The standard deviation of the values in @l
    """
    mean = sum(l)/len(l)
    return ( sum([((x - mean) ** 2) for x in l]) / len(l) )**0.5

@micropython.native
def bitwise_entropy(arr):
    """Calculate the entropy of the bit string in a bytearray

    @param arr  A bytearray, treated as a bit string

    @return the Shannon Entropy of the string, assuming a 50/50 chance of any bit being 1 or 0
    """
    # Count how many bits are 1 in the whole bytearray
    count1s = 0
    for b in arr:
        for i in range(8):
            if b & (1 << i):
                count1s += 1

    # Make sure we don't have all-1 or all-0 in the array; handle those cases
    num_bits = len(arr) << 3
    if count1s == 0:
        return 0.0
    elif count1s == num_bits:
        return 1.0
    else:
        # Calculate the entropy of the string
        # E = sum(p(x) * log_2(p(x))) = sum(p(x) * log(p(x))) / log(2)
        prob_1 = count1s / num_bits
        p_x = [
            1.0 - prob_1,
            prob_1
        ]
        return -sum([ p * math.log(p) for p in p_x]) / LOG2

@micropython.native
class Conway(EuroPiScript):
    def __init__(self):
        # For ease of blitting, store the field as a bit array
        # Each byte is 8 horizontally adjacent pixels, with the most significant bit
        # on the left
        self.field = bytearray(OLED_HEIGHT * OLED_WIDTH_BYTES)
        self.next_field = bytearray(OLED_HEIGHT * OLED_WIDTH_BYTES)

        # Keep 2 separate frame buffer instances so we don't need to recreate the FB objects when we draw
        self.frame = FrameBuffer(self.field, OLED_WIDTH, OLED_HEIGHT, MONO_HLSB)
        self.next_frame = FrameBuffer(self.next_field, OLED_WIDTH, OLED_HEIGHT, MONO_HLSB)

        # Use 1D array for summed area table for better cache performance
        self.field_sum = array.array('H', [0] * (OLED_HEIGHT * OLED_WIDTH))

        # how many cells were born this tick?
        self.num_born = 0

        # how many cells died this tick?
        self.num_died = 0

        # how many cells are currently alive?
        # this gets updated on every tick and on random spawns
        self.num_alive = 0

        # Set to True if we want to clear the field & respawn
        self.reset_requested = False

        # keep the last few changes in population in a list to check if it's oscillating predictably
        self.population_deltas = []
        self.MAX_DELTAS = 12

        # statically allocated array we use to store the sums of cells when checking for statis
        self.statis_sums = [0] * self.MAX_DELTAS

        # Pre-calculate neighbor offsets for faster access
        self.neighbor_offsets = [-OLED_WIDTH-1, -OLED_WIDTH, -OLED_WIDTH+1, 
                                -1, 1,
                                OLED_WIDTH-1, OLED_WIDTH, OLED_WIDTH+1]

        @b1.handler
        def on_b1():
            self.reset_requested = True

        @b2.handler
        def on_b2():
            self.reset_requested = True

        @din.handler
        def on_din():
            self.reset_requested = True
    
    @micropython.native
    def calculate_spawn_level(self):
        """Calculate what percentage of the field should contain new cells

        We want to avoid having the spawn rate _too_ high as that can result in high CPU loads and RAM usage.
        - K1: [0, 0.5]
        - K2: [-0.5, 0.5]
        - AIN: [0, 1]

        P = K1 + K2 * AIN => [-0.5, 1.0]
        """
        base_spawn_level = k1.percent() / 2

        # get the level of AIN, attenuverted by K2
        cv_mod = ain.percent()/2
        cv_att = k2.percent() - 1
        cv_mod = cv_mod * cv_att

        spawn_level = clamp(base_spawn_level + cv_mod, 0, 1)
        return spawn_level
    
    @micropython.native
    def reset(self):
        """Clear the whole field and spawn random data in it
        """
        # Use experimental bitarray approach for faster clearing
        set_all_bits(self.next_field, 0)

        self.num_alive = 0
        self.population_deltas.clear()

        # fill the field with random cells
        fill_level = self.calculate_spawn_level()
        for i in range(NUM_PIXELS):
            x = rnd()
            is_alive = get_bit(self.field, i)
            if x < fill_level and not is_alive:
                # if the space isn't already filled and we want to fill it
                set_bit(self.field, i, True)
                set_bit(self.next_field, i, True)
                self.num_alive += 1
            elif x >= fill_level and is_alive:
                # if the space is filled and we want to clear it
                set_bit(self.field, i, False)
                set_bit(self.next_field, i, False)
                self.num_alive -= 1

        # Assume the whole field has changed
        self.num_changes = NUM_PIXELS

    @micropython.viper
    def update_field_sums(self):
        """Recalculate the summed area table using optimized viper code
        """
        field_sum_ptr = ptr16(self.field_sum)
        field_ptr = ptr8(self.field)
        width = int(OLED_WIDTH)
        height = int(OLED_WIDTH)
        
        # First row and column need special handling
        # First pixel
        bit_val = 1 if (field_ptr[0] & 0x80) else 0
        field_sum_ptr[0] = bit_val
        
        # First row
        for j in range(1, width):
            byte_idx = j >> 3
            bit_pos = 7 - (j & 7)
            bit_val = 1 if (field_ptr[byte_idx] & (1 << bit_pos)) else 0
            field_sum_ptr[j] = field_sum_ptr[j-1] + bit_val
        
        # First column  
        for i in range(1, height):
            idx = i * width
            byte_idx = idx >> 3
            bit_pos = 7 - (idx & 7)
            bit_val = 1 if (field_ptr[byte_idx] & (1 << bit_pos)) else 0
            field_sum_ptr[idx] = field_sum_ptr[idx - width] + bit_val
        
        # Rest of the matrix
        for i in range(1, height):
            for j in range(1, width):
                idx = i * width + j
                byte_idx = idx >> 3
                bit_pos = 7 - (idx & 7)
                bit_val = 1 if (field_ptr[byte_idx] & (1 << bit_pos)) else 0
                field_sum_ptr[idx] = (bit_val + 
                                    field_sum_ptr[idx - 1] + 
                                    field_sum_ptr[idx - width] - 
                                    field_sum_ptr[idx - width - 1])

    @micropython.viper
    def sum_cells(self, start_row: int, start_col: int, end_row: int, end_col: int) -> int:
        """Get the sum of all cells in a given sub-matrix using optimized viper code
        """
        field_sum_ptr = ptr16(self.field_sum)
        width = int(OLED_WIDTH)
        
        if start_row == 0 or start_col == 0:
            a = 0
        else:
            a = field_sum_ptr[(start_row - 1) * width + (start_col - 1)]

        if start_row == 0:
            c = 0
        else:
            c = field_sum_ptr[(start_row - 1) * width + end_col]

        if start_col == 0:
            g = 0
        else:
            g = field_sum_ptr[end_row * width + (start_col - 1)]

        i = field_sum_ptr[end_row * width + end_col]

        return i - c - g + a

    @micropython.native
    def draw(self):
        """Show the current playing field on the OLED
        """
        oled.blit(self.frame, 0, 0)
        oled.show()

    @micropython.native
    def tick(self):
        """Calculate the state of the next generation

        This checks the regions around every changed space in the previous generation, updating the
        total population and counting how many births & deaths this generation had.

        If a reset was requested, the field is cleared & randomly reset _before_ calculating the new generation
        """
        self.num_born = 0
        self.num_died = 0
        self.num_changes = 0

        if self.reset_requested:
            self.reset_requested = False
            self.reset()

        # iterate through every cell, calculating generational changes
        self.update_field_sums()
        
        # Use local variables for faster access
        field = self.field
        next_field = self.next_field
        width = OLED_WIDTH
        height = OLED_HEIGHT
        
        for i in range(height):
            top = max(0, i-1)
            bottom = min(height-1, i+1)

            for j in range(width):
                left = max(0, j-1)
                right = min(width-1, j+1)

                bit_index = i * width + j

                cell_present = get_bit(field, bit_index)

                num_neighbours = self.sum_cells(top, left, bottom, right)
                if cell_present:
                    num_neighbours = max(0, num_neighbours-1)

                if cell_present:
                    if num_neighbours == 2 or num_neighbours == 3:  # happy cell, stays alive
                        set_bit(next_field, bit_index, True)
                    else:                                           # sad cell, dies
                        set_bit(next_field, bit_index, False)
                        self.num_died += 1
                        self.num_alive -= 1
                        self.num_changes += 1
                else:
                    if num_neighbours == 3:                         # baby cell is born!
                        set_bit(next_field, bit_index, True)
                        self.num_alive += 1
                        self.num_born += 1
                        self.num_changes += 1
                    else:                                           # empty space remains empty
                        set_bit(next_field, bit_index, False)

        # swap field & next_field so we don't need to copy between arrays
        tmp = self.next_field
        self.next_field = self.field
        self.field = tmp

        # swap frame and next_frame for rendering
        tmp = self.next_frame
        self.next_frame = self.frame
        self.frame

    @micropython.native
    def check_for_stasis(self):
        """Check the population changes over time to see if we've reached a state of stasis
        """
        # we must have at least MAX_DELTAS generations of data
        if len(self.population_deltas) < self.MAX_DELTAS:
            return False

        # if there are no changes or everything is dead, we've reached static stasis
        if self.num_changes == 0 or self.num_alive == 0:
            return True

        # if the population is oscillating up and down predicatably, we've probably reached stasis
        # check for 2, 3, and 4 step repetitions
        for pattern_length in range(2, 5):
            count = self.MAX_DELTAS // pattern_length
            for i in range(count):
                self.statis_sums[i] = sum(self.population_deltas[i*pattern_length:i*pattern_length+pattern_length])

            # check the standard deviation
            deviation = stdev(self.statis_sums[0:count])
            mean = sum(self.statis_sums[0:count])/count
            if deviation <= 1 and abs(mean) <= 1:
                return True

        return False

    @micropython.native
    def main(self):
        """The main loop for the program

        Handles setting the CV output, drawing to the OLED, and triggering the simulation
        """
        turn_off_all_cvs()
        self.reset()

        in_stasis = False

        while True:
            # turn off the stasis gate while we calculate the next generation
            cv6.off()

            # turn on the FPS gate when we start calculating
            cv4.on()

            # calculate the next generation
            self.tick()

            # turn off the FPS gate when we're done calculating but before we draw
            cv4.off()

            # show the results on the OLED
            self.draw()

            # check for stasis conditions
            self.population_deltas.append(self.num_born - self.num_died)
            if len(self.population_deltas) > self.MAX_DELTAS:
                self.population_deltas.pop(0)
            in_stasis = self.check_for_stasis()

            cv1.voltage(MAX_OUTPUT_VOLTAGE * bitwise_entropy(self.field))
            if self.num_born > self.num_died:
                cv5.on()
            else:
                cv5.off()

            # Make sure we don't divide by zero
            if self.num_alive > 0:
                cv2.voltage(MAX_OUTPUT_VOLTAGE * self.num_born / self.num_alive)
            else:
                cv2.off()


            # Prevent values greater than 1 & division-by-zero errors
            hi = max(self.num_died, self.num_born)
            low = min(self.num_died, self.num_born)
            if (hi > 0):
                cv3.voltage(MAX_OUTPUT_VOLTAGE * (low/hi))
            else:
                cv3.off()

            # If we've achieved statis, set CV6 & trigger a reset
            if in_stasis:
                cv6.on()
                self.reset_requested = True

if __name__ == "__main__":
    Conway().main()
