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

"""Implements Seeds cellular automaton for generating chaotic patterns.

Uses simple birth/death rules to create dynamic, never-settling patterns:
1. A dead cell becomes alive with exactly two neighbors
2. All living cells die in the next generation
3. No survival conditions exist

Outputs:
- CV1: Global population density
- CV2: Birth rate activity
- CV3: Total state changes
- CV4: High birth rate gate

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

class Seeds(BaseAutomata):
    """
    Seeds cellular automaton implementation.
    
    Rules:
    1. A dead cell becomes alive if it has exactly two live neighbors
    2. All living cells die in the next generation
    
    Creates chaotic, rapidly changing patterns that rarely stabilize.
    Similar to Conway's Game of Life but without stable patterns.
    """
    def __init__(self, width, height, current_food_chance, current_tick_limit):
        super().__init__(width, height, current_food_chance, current_tick_limit)
        self.name = "Seeds"
        # Seeds creates TV static-like patterns that rarely reach true stasis
        # Only consider it stasis if completely dead or truly minimal change
        self.use_stasis = False
        
    @micropython.viper
    def simulate_generation(self, sim_current, sim_next) -> int:
        """Simulate one generation of Seeds using hybrid bit-parallel optimization.
        
        Uses bit-parallel operations for both neighbor counting and state transitions:
        1. Dead cells are checked for exactly 2 neighbors using bit masking
        2. All living cells die in one step (simple clear operation)
        3. New births are processed 8 cells at a time within each byte
        
        The simulation is optimized for the Seeds ruleset where all living cells
        die each generation, allowing for simplified state tracking and transitions.
        
        Args:
            sim_current: Current state buffer
            sim_next: Buffer for next generation state
            
        Returns:
            Packed 32-bit int containing births (lower 16 bits) and deaths (upper 16 bits)
        """
        bytes_per_row = int(self.bytes_per_row)
        last_byte_index = int(self.last_byte_index)
        height = int(self.height)
        width = int(self.width)
        
        # Get pointers to arrays
        current_field_ptr = ptr8(sim_current)
        next_field_ptr = ptr8(sim_next)
        popcount_table_ptr = ptr8(POPCOUNT)
        
        # Initialize counters for MicroPython compatibility
        total_born = 0
        total_died = 0
        
        # Clear next generation array
        grid_len = bytes_per_row * height
        for i in range(grid_len):
            next_field_ptr[i] = 0

        # Iterate rows (0-31)
        for row_index in range(height):
            row_byte_offset = int(row_index * bytes_per_row)
            
            # Calculate neighbor row offsets with wrap-around
            top_row_byte_offset = ((row_index - 1) % height) * bytes_per_row
            bottom_row_byte_offset = ((row_index + 1) % height) * bytes_per_row

            # Process each byte in row (0-15)
            for byte_index_in_row in range(bytes_per_row):
                current_byte_addr = row_byte_offset + byte_index_in_row
                current_row_byte = current_field_ptr[current_byte_addr]
                
                # All living cells die in Seeds rule (all current cells contribute to death count)
                total_died = total_died + int(current_row_byte)
                
                # Calculate neighbor byte addresses with wrap-around
                left_byte_idx = (byte_index_in_row - 1) % bytes_per_row
                right_byte_idx = (byte_index_in_row + 1) % bytes_per_row
                
                # Fetch neighbor bytes
                top_left = int(current_field_ptr[top_row_byte_offset + left_byte_idx])
                top_mid = int(current_field_ptr[top_row_byte_offset + byte_index_in_row])
                top_right = int(current_field_ptr[top_row_byte_offset + right_byte_idx])
                
                mid_left = int(current_field_ptr[row_byte_offset + left_byte_idx])
                mid_right = int(current_field_ptr[row_byte_offset + right_byte_idx])
                
                bot_left = int(current_field_ptr[bottom_row_byte_offset + left_byte_idx])
                bot_mid = int(current_field_ptr[bottom_row_byte_offset + byte_index_in_row])
                bot_right = int(current_field_ptr[bottom_row_byte_offset + right_byte_idx])

                # Top neighbors - shift to align with current byte
                top_left_mask = (top_mid << 1) | (top_left >> 7)  # Carry from left byte
                top_mid_mask = top_mid
                top_right_mask = (top_mid >> 1) | (top_right << 7)  # Carry from right byte

                # Horizontal neighbors  
                left_mask = (current_row_byte << 1) | (mid_left >> 7)   # Left neighbor
                right_mask = (current_row_byte >> 1) | (mid_right << 7)  # Right neighbor

                # Bottom neighbors
                bot_left_mask = (bot_mid << 1) | (bot_left >> 7)
                bot_mid_mask = bot_mid  
                bot_right_mask = (bot_mid >> 1) | (bot_right << 7)

                neighbor_mask_1 = top_left_mask
                neighbor_mask_2 = top_mid_mask
                neighbor_mask_3 = top_right_mask
                neighbor_mask_4 = left_mask
                neighbor_mask_5 = right_mask
                neighbor_mask_6 = bot_left_mask
                neighbor_mask_7 = bot_mid_mask
                neighbor_mask_8 = bot_right_mask

                # bit-sliced accumulator code
                neighbor_sum_bit0 = 0
                neighbor_sum_bit1 = 0
                neighbor_sum_bit2 = 0

                # Inline bitwise half-add chain
                carry_bit0 = neighbor_sum_bit0 & neighbor_mask_1; neighbor_sum_bit0 ^= neighbor_mask_1
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                carry_bit0 = neighbor_sum_bit0 & neighbor_mask_2; neighbor_sum_bit0 ^= neighbor_mask_2
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                carry_bit0 = neighbor_sum_bit0 & neighbor_mask_3; neighbor_sum_bit0 ^= neighbor_mask_3
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                carry_bit0 = neighbor_sum_bit0 & neighbor_mask_4; neighbor_sum_bit0 ^= neighbor_mask_4
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                carry_bit0 = neighbor_sum_bit0 & neighbor_mask_5; neighbor_sum_bit0 ^= neighbor_mask_5
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                carry_bit0 = neighbor_sum_bit0 & neighbor_mask_6; neighbor_sum_bit0 ^= neighbor_mask_6
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                carry_bit0 = neighbor_sum_bit0 & neighbor_mask_7; neighbor_sum_bit0 ^= neighbor_mask_7
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                carry_bit0 = neighbor_sum_bit0 & neighbor_mask_8; neighbor_sum_bit0 ^= neighbor_mask_8
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1

                # Apply Seeds rules bit-parallel
                # Rule: Dead cell with exactly 2 neighbors becomes alive
                # Rule: All living cells die
                
                # Check for exactly 2 neighbors: bit2=0, bit1=1, bit0=0
                inv_bit2_mask = (~neighbor_sum_bit2) & 0xFF
                exact_two_mask = inv_bit2_mask & neighbor_sum_bit1 & (~neighbor_sum_bit0 & 0xFF)
                
                # Current state mask: only dead cells can be born
                dead_cells = (~current_row_byte) & 0xFF
                
                # Apply Seeds rule: dead cells with exactly 2 neighbors become alive
                new_byte = dead_cells & exact_two_mask
                
                # Count births for statistics
                birth_count = popcount_table_ptr[new_byte]
                total_born += birth_count
                
                # Store result
                next_field_ptr[current_byte_addr] = new_byte

        return (total_born & 0xffff) | ((total_died & 0xffff) << 16)

    @micropython.native
    def feed_rule(self, sim_current, sim_next, food_chance, num_alive):
        from random import randint
        if food_chance <= 0: return num_alive
        
        new_alive = num_alive
        for i in range(len(sim_current)):
            b = sim_current[i]
            for bit in (1, 2, 4, 8, 16, 32, 64, 128):
                if randint(0, 200) < food_chance and not (b & bit):
                    new_alive += 1
                    b |= bit
            sim_current[i] = sim_next[i] = b
        return new_alive

    @micropython.native  
    def cv1_out(self, c):
        """CV1 output: Global population density.
        
        Higher voltage = more cells alive relative to grid size.
        0V = empty grid, 10V = all cells alive.
        """
        from europi import cv1
        cv1.voltage(10 * c.num_alive / (c.width * c.height) if c.num_alive else 0)

    @micropython.native
    def cv2_out(self, c):
        """CV2 output: Birth rate.
        
        Higher voltage = more cells born in last generation.
        Scales with number of births, maxing at 100 births.
        """
        from europi import cv2
        cv2.voltage(10 * min(c.num_born / 100.0, 1.0) if c.num_born else 0)

    @micropython.native
    def cv3_out(self, c):
        """CV3 output: Total activity level.
        
        Higher voltage = more total state changes (births + deaths).
        Scales with total changes, maxing at 200 changes.
        """
        from europi import cv3
        cv3.voltage(10 * min((c.num_born + c.num_died) / 200.0, 1.0) if c.num_born + c.num_died else 0)

    @micropython.native
    def cv4_out(self, c):
        """CV4 output: High birth rate gate.
        
        HIGH when more than 50 cells born in last generation.
        LOW when fewer births occurred.
        """
        from europi import cv4
        cv4.on() if c.num_born > 50 else cv4.off()
