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

"""Implements Conway's Game of Life as a dynamic grid evolution automaton.

Classic rules:
1. Any live cell with 2-3 neighbors survives
2. Any dead cell with 3 neighbors becomes alive
3. All other cells die or stay dead

Outputs 4 voltage signals:
- CV1: Entropy measurement of current state
- CV2: Birth rate relative to population 
- CV3: Death rate relative to population
- CV4: Population density gate

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

class Life(BaseAutomata):
    """
    Implementation of Conway's Game of Life cellular automaton.
    
    Classic rules:
    1. Any live cell with 2 or 3 live neighbors survives
    2. Any dead cell with exactly 3 live neighbors becomes alive
    3. All other cells die or stay dead
    """
    
    def __init__(self, width, height, current_food_value, current_tick_limit):
        super().__init__(width, height, current_food_value, current_tick_limit)
        self.name = "Game Of Life"
        self.stasis_max_pop_delta = 16
        self.min_stasis_pattern_length = 2
        self.max_stasis_pattern_length = 6
        
    @micropython.viper
    def simulate_generation(self, sim_current, sim_next) -> int:
        """Simulate one generation of the Game of Life using hybrid bit-parallel optimization.
        
        Uses bit-parallel operations within bytes for neighbor counting and rule application,
        processing 8 cells simultaneously. Neighbor gathering is done at byte level with
        appropriate shifting for edge cases.
        
        Args:
            sim_current: Current state buffer
            sim_next: Buffer for next generation state
            
        Returns:
            Packed 32-bit int containing births (lower 16 bits) and deaths (upper 16 bits)
        """
        # Viper core generation loop
        bpr = int(self.bytes_per_row)  # 16 for 128px wide (128/8 = 16
        height = int(self.height)  # 32
        width = int(self.width)    # 128
        
        current_field_ptr = ptr8(sim_current)
        next_field_ptr = ptr8(sim_next)
        popcount_table_ptr = ptr8(POPCOUNT)

        total_born = 0
        total_died = 0

        # Iterate rows (0-31)
        for row_index in range(height):
            row_byte_offset = int(row_index * bpr)
            
            # Calculate neighbor row offsets with wrap-around
            top_row_byte_offset = ((row_index - 1) % height) * bpr
            bottom_row_byte_offset = ((row_index + 1) % height) * bpr

            # Process each byte in row (0-15)
            for byte_index_in_row in range(bpr):
                current_byte_addr = row_byte_offset + byte_index_in_row
                current_row_byte = current_field_ptr[current_byte_addr]
                
                # Calculate neighbor byte addresses with wrap-around
                left_byte_idx = (byte_index_in_row - 1) % bpr
                right_byte_idx = (byte_index_in_row + 1) % bpr
                
                # Fetch neighbor bytes
                top_left = current_field_ptr[top_row_byte_offset + left_byte_idx]
                top_mid = current_field_ptr[top_row_byte_offset + byte_index_in_row]
                top_right = current_field_ptr[top_row_byte_offset + right_byte_idx]
                
                mid_left = current_field_ptr[row_byte_offset + left_byte_idx]
                mid_right = current_field_ptr[row_byte_offset + right_byte_idx]
                
                bot_left = current_field_ptr[bottom_row_byte_offset + left_byte_idx]
                bot_mid = current_field_ptr[bottom_row_byte_offset + byte_index_in_row]
                bot_right = current_field_ptr[bottom_row_byte_offset + right_byte_idx]

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

                # Rest of your bit-parallel logic remains the same...
                neighbor_mask_1 = top_left_mask
                neighbor_mask_2 = top_mid_mask
                neighbor_mask_3 = top_right_mask
                neighbor_mask_4 = left_mask
                neighbor_mask_5 = right_mask
                neighbor_mask_6 = bot_left_mask
                neighbor_mask_7 = bot_mid_mask
                neighbor_mask_8 = bot_right_mask

                # Your existing bit-sliced accumulator code...
                neighbor_sum_bit0 = 0
                neighbor_sum_bit1 = 0
                neighbor_sum_bit2 = 0

                # Inline bitwise half-add chain (keep your existing code)
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

                # Count bitplanes and apply Game of Life rules
                inv_bit2_mask = (~neighbor_sum_bit2) & 0xFF
                exact_two_mask = inv_bit2_mask & neighbor_sum_bit1 & (~neighbor_sum_bit0 & 0xFF)
                exact_three_mask = inv_bit2_mask & neighbor_sum_bit1 & neighbor_sum_bit0

                alive_mask = current_row_byte
                survive_mask = alive_mask & (exact_two_mask | exact_three_mask)
                birth_mask = (~alive_mask & 0xFF) & exact_three_mask
                death_mask = alive_mask & (~survive_mask & 0xFF)

                # Write next generation
                next_field_ptr[current_byte_addr] = survive_mask | birth_mask

                # Update counters
                birth_count = popcount_table_ptr[birth_mask]
                death_count = popcount_table_ptr[death_mask]

                total_born += birth_count
                total_died += death_count

        return ( (total_born & 0xffff) | (( total_died & 0xffff) << 16) )

    @micropython.native
    def feed_rule(self, sim_current, sim_next, food_chance, num_alive):
        food_chance = max(0, self.current_food_value / 10) #we don't want 100% chance if we can help it, so take the food value and divide it by some amount
        if food_chance <= 0:
            return num_alive
        new_alive = num_alive
        for i in range(len(sim_current)):
            b = sim_current[i]
            for bit in (1, 2, 4, 8, 16, 32, 64, 128):
                if randint(0,100) < food_chance:
                    if not (b & bit):
                        new_alive += 1
                    b |= bit
            sim_current[i] = b
            sim_next[i] = b
        return new_alive

    @micropython.native
    def reset(self):
        return True

    @micropython.native
    def cv1_out(self, c):
        """CV1 output: Entropy of the current generation.
        
        Higher voltage = more disorder/randomness in the pattern.
        """
        from europi import cv1
        cv1.voltage(10 * self.calculate_entropy(c.sim_current, c.num_alive))

    @micropython.native
    def cv2_out(self, c):
        """CV2 output: Birth rate relative to population.
        
        Higher voltage = more cells being born relative to total population.
        """
        from europi import cv2
        cv2.voltage(10 * c.num_born / c.num_alive) if c.num_alive > 0 else cv2.off()

    @micropython.native
    def cv3_out(self, c):
        """CV3 output: Population density.
        
        Higher voltage = more of the grid is occupied by living cells.
        """
        from europi import cv3
        cv3.voltage(10 * c.num_alive / (c.width * c.height))

    @micropython.native
    def cv4_out(self, c):
        """CV4 output: Population growth gate.
        
        HIGH when population is growing, LOW when shrinking.
        """
        from europi import cv4
        cv4.on() if c.num_born > c.num_died else cv4.off()

    @micropython.native
    def calculate_entropy(self, sim_current, num_alive):
        total, alive = len(sim_current) * 8, num_alive
        if alive == 0 or alive == total: return 0.0
        p = alive / total
        q = 1.0 - p
        if p < EPSILON: p = EPSILON
        if q < EPSILON: q = EPSILON
        return -(p * math.log(p) + q * math.log(q)) / LOG2