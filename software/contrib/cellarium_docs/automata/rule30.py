# Copyright 2025 Allen Synthesis
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

"""Implements Rule 30 elementary cellular automaton for evolving patterns.

Performs cell state updates based on the classic Rule 30 formula:
next_state = left XOR (center OR right)

Each new line is calculated from the states of the cells in the line above
creating complex, chaotic patterns from simple rules.

Outputs:
- CV1: Global population density
- CV2: Current line activity
- CV3: Bottom row entropy
- CV4: Pattern complexity gate

@author Grybbit (https://github.com/Bearwynn)
@year 2025
"""

# Standard library imports
import math
from random import randint

# MicroPython imports
import micropython

# EuroPi imports
from europi import *

# Local imports
from contrib.cellarium_docs.automata_base import BaseAutomata, LOG2, EPSILON, POPCOUNT

class Rule30(BaseAutomata):
    """
    Rule 30 elementary cellular automaton implementation.
    Rule 30 name comes from Wolfram's classification system.
    
    A simple 1D cellular automaton that creates complex patterns from simple rules:
    - For each cell, look at itself and its two neighbors (left, center, right)
    - New state = XOR of left neighbor with (OR of center and right neighbor)
    - Pattern scrolls upward, with new cells generated at bottom
    """
    def __init__(self, width, height, current_food_chance, current_tick_limit):
        super().__init__(width, height, current_food_chance, current_tick_limit)
        self.name = "Rule 30"
        self.stasis_max_pop_delta = 8
        self.max_stasis_pattern_length = 2
        
    @micropython.viper
    def simulate_generation(self, sim_current, sim_next) -> int:
        """Simulate one generation of Rule 30 using scrolling with efficient bit operations.
        
        Implements Wolfram's Rule 30 using a combination of techniques:
        1. Vertical scrolling: Previous states move up one row each generation
        2. Bottom row generation: Uses Rule 30 formula (left XOR (center OR right))
        3. Bit-level processing: Each byte is processed bit by bit for precise rule application
        
        The implementation preserves the chaotic nature of Rule 30 while maintaining
        optimal performance through careful bit manipulation and state management.
        
        Args:
            sim_current: Current state buffer
            sim_next: Buffer for next generation state
            
        Returns:
            Packed 32-bit int containing births (lower 16 bits) and deaths (upper 16 bits)
        """
        bpr = int(self.bytes_per_row)
        h = int(self.height)
        
        # Get pointers to arrays
        curr_ptr = ptr8(sim_current)
        next_ptr = ptr8(sim_next)
        pop_ptr = ptr8(POPCOUNT)
        
        total_born = 0
        total_died = 0
        
        # clear next buffer first
        for i in range(bpr * h):
            next_ptr[i] = 0
        
        # Shift all lines up by one (skip if top row)
        if h > 1:
            for row in range(h - 1):
                src = (row + 1) * bpr
                tgt = row * bpr
                for i in range(bpr):
                    next_ptr[tgt + i] = curr_ptr[src + i]
        
        # Generate new bottom line using Rule 30
        src = tgt = (h - 1) * bpr
        for byte_idx in range(bpr):
            # Calculate indices with wrapping
            left_idx = (byte_idx - 1) % bpr
            right_idx = (byte_idx + 1) % bpr
            
            # Get cell states
            left_b = curr_ptr[src + left_idx]
            center_b = curr_ptr[src + byte_idx]
            right_b = curr_ptr[src + right_idx]
            
            # Initialize current and new states
            old_b = curr_ptr[tgt + byte_idx]
            new_b = 0
            
            for bit_pos in range(8):
                left_bit = (left_b >> 7) & 1 if bit_pos == 0 else (center_b >> (bit_pos - 1)) & 1
                center_bit = (center_b >> bit_pos) & 1
                right_bit = right_b & 1 if bit_pos == 7 else (center_b >> (bit_pos + 1)) & 1
                # Rule 30: XOR of left and (center OR right)
                new_b |= ((left_bit ^ (center_bit | right_bit)) << bit_pos)
            
            next_ptr[tgt + byte_idx] = new_b
            
            # Calculate births and deaths separately for MicroPython
            births = new_b & (~old_b)
            deaths = old_b & (~new_b)
            total_born += pop_ptr[births]
            total_died += pop_ptr[deaths]
            
        return (total_born & 0xffff) | ((total_died & 0xffff) << 16)
    
    @micropython.native
    def feed_rule(self, sim_current, sim_next, food_chance, num_alive):
        from random import randint
        if food_chance <= 0: return num_alive
        
        # Add food to bottom row
        new_alive = num_alive
        bottom_start = (self.height - 1) * self.bytes_per_row
        for i in range(bottom_start, bottom_start + self.bytes_per_row):
            b = sim_current[i]
            for bit in (1, 2, 4, 8, 16, 32, 64, 128):
                if randint(0, 100) < food_chance and not (b & bit):
                    new_alive += 1
                    b |= bit
            sim_current[i] = sim_next[i] = b
        return new_alive

    @micropython.native  
    def cv1_out(self, c):
        """CV1 output: Global population density.
        
        Higher voltage = more cells are alive across entire grid.
        """
        from europi import cv1
        cv1.voltage(10 * c.num_alive / (c.width * c.height) if c.num_alive else 0)

    @micropython.native
    def cv2_out(self, c):
        """CV2 output: Bottom row activity.
        
        Higher voltage = more cells are alive in the currently generating row.
        """
        from europi import cv2
        start = (c.height - 1) * self.bytes_per_row
        alive = sum(bin(c.sim_current[i]).count('1') for i in range(start, start + self.bytes_per_row))
        cv2.voltage(10 * alive / (self.bytes_per_row * 8))

    @micropython.native
    def cv3_out(self, c):
        """CV3 output: Bottom row entropy.
        
        Higher voltage = more randomness/chaos in the current generation row.
        0V = completely uniform (all on or all off).
        """
        from europi import cv3
        start = (c.height - 1) * self.bytes_per_row
        alive = sum(bin(c.sim_current[i]).count('1') for i in range(start, start + self.bytes_per_row))
        total = self.bytes_per_row * 8
        if not alive or alive == total: 
            cv3.voltage(0)
        else:
            p = alive / total
            entropy = -(p * math.log(p) + (1-p) * math.log(1-p)) / LOG2
            cv3.voltage(10 * entropy)

    @micropython.native
    def cv4_out(self, c):
        """CV4 output: Activity gate.
        
        HIGH when any cells changed state (born or died) in last generation.
        LOW when no changes occurred.
        """
        from europi import cv4
        cv4.on() if c.num_born or c.num_died else cv4.off()