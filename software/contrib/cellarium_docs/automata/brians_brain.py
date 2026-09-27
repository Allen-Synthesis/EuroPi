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

"""Implements Brian's Brain cellular automaton for complex wave patterns.

Three-state cellular automaton with cyclic state transitions:
1. OFF cells (0) become ON (1) if exactly 2 neighbors are ON
2. ON cells (1) become DYING (2) in the next generation
3. DYING cells (2) become OFF (0) in the next generation

Creates oscillating wave-like patterns using dual grid buffers for
state tracking. Named after Brian Silverman who discovered this rule.

Outputs:
- CV1: Wave pattern complexity
- CV2: Current activation level
- CV3: Grid state entropy
- CV4: Pattern stability gate

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
from contrib.cellarium_docs.automata_base import BaseAutomata, POPCOUNT, LOG2, EPSILON

class BriansBrain(BaseAutomata):
    """
    Brian's Brain cellular automaton implementation using bit-parallel optimization.
    
    Three-state cellular automaton with rules:
    1. OFF cells (0) become ON (1) if exactly 2 neighbors are ON
    2. ON cells (1) become DYING (2) in the next generation
    3. DYING cells (2) become OFF (0) in the next generation
    
    Creates complex, oscillating patterns with wave-like behavior.
    Named after Brian Silverman, who discovered this rule.
    """
    def __init__(self, width, height, current_food_chance, current_tick_limit):
        super().__init__(width, height, current_food_chance, current_tick_limit)
        self.name = "Brian's Brain"
        self.stasis_max_pop_delta = 24
        self.min_stasis_pattern_length = 8
        self.max_stasis_pattern_length = 12
        
        # Brian's Brain has 3 states: Off(0), On(1), Dying(2)
        # We'll use two grids to represent the states
        # firing_grid: cells that are "firing" (on)
        # dying_grid: cells that are "dying" (refractory)
        grid_size = (width * height + 7) // 8
        self.firing_grid = bytearray(grid_size)
        self.dying_grid = bytearray(grid_size)
        self.next_firing = bytearray(grid_size)
        self.next_dying = bytearray(grid_size)
        
    @micropython.viper
    def simulate_generation(self, sim_current, sim_next) -> int:
        """Simulate one generation of Brian's Brain using hybrid bit-parallel optimization.
        
        Uses bit-parallel operations within bytes for efficient state tracking of the
        three cell states (Off, On, Dying) using two separate bit grids:
        - firing_grid: tracks cells that are currently "On"
        - dying_grid: tracks cells that are in "Dying" state
        
        The simulation processes 8 cells at once using bit operations for neighbor counting
        and state transitions. Neighbor gathering is done at byte level with appropriate 
        shifting for edge cases.
        
        Args:
            sim_current: Current state buffer (display grid)
            sim_next: Buffer for next generation state (display grid)
            
        Returns:
            Packed 32-bit int containing births (lower 16 bits) and deaths (upper 16 bits)
        """
        bpr = int(self.bytes_per_row)
        h = int(self.height)
        w = int(self.width)
        
        # Get pointers to all arrays
        firing_ptr = ptr8(self.firing_grid)
        dying_ptr = ptr8(self.dying_grid)
        next_firing_ptr = ptr8(self.next_firing)
        next_dying_ptr = ptr8(self.next_dying)
        current_ptr = ptr8(sim_current)
        next_ptr = ptr8(sim_next)
        popcount_ptr = ptr8(POPCOUNT)
        
        total_born = total_died = 0
        
        # Clear next generation arrays
        grid_len = int(len(self.firing_grid))
        for i in range(grid_len):
            next_firing_ptr[i] = next_dying_ptr[i] = 0

        # Process each row with bit-parallel neighbor counting
        for row in range(h):
            row_offset = row * bpr
            top_row_offset = ((row - 1) % h) * bpr
            bottom_row_offset = ((row + 1) % h) * bpr
            
            # Process each byte in the row
            for byte_idx in range(bpr):
                current_byte_addr = row_offset + byte_idx
                firing_byte = firing_ptr[current_byte_addr]
                dying_byte = dying_ptr[current_byte_addr]
                
                # Calculate neighbor byte indices with wrap-around
                left_byte_idx = (byte_idx - 1) % bpr
                right_byte_idx = (byte_idx + 1) % bpr
                
                # Fetch all 9 neighbor bytes for bit-parallel processing
                top_left = firing_ptr[top_row_offset + left_byte_idx]
                top_mid = firing_ptr[top_row_offset + byte_idx]
                top_right = firing_ptr[top_row_offset + right_byte_idx]
                
                mid_left = firing_ptr[row_offset + left_byte_idx]
                mid_right = firing_ptr[row_offset + right_byte_idx]
                
                bot_left = firing_ptr[bottom_row_offset + left_byte_idx]
                bot_mid = firing_ptr[bottom_row_offset + byte_idx]
                bot_right = firing_ptr[bottom_row_offset + right_byte_idx]

                # Create bit-aligned neighbor masks (like in life.py)
                top_left_mask = (top_mid << 1) | (top_left >> 7)
                top_mid_mask = top_mid
                top_right_mask = (top_mid >> 1) | (top_right << 7)
                
                left_mask = (firing_byte << 1) | (mid_left >> 7)
                right_mask = (firing_byte >> 1) | (mid_right << 7)
                
                bot_left_mask = (bot_mid << 1) | (bot_left >> 7)
                bot_mid_mask = bot_mid
                bot_right_mask = (bot_mid >> 1) | (bot_right << 7)

                # Bit-parallel neighbor counting using binary addition (like life.py)
                neighbor_sum_bit0 = 0
                neighbor_sum_bit1 = 0
                neighbor_sum_bit2 = 0

                # Manually unroll neighbor mask addition for viper compatibility
                # Process each of the 8 neighbor masks with inline half-adder chain
                
                # Mask 1: top_left_mask
                carry_bit0 = neighbor_sum_bit0 & top_left_mask; neighbor_sum_bit0 ^= top_left_mask
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                
                # Mask 2: top_mid_mask  
                carry_bit0 = neighbor_sum_bit0 & top_mid_mask; neighbor_sum_bit0 ^= top_mid_mask
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                
                # Mask 3: top_right_mask
                carry_bit0 = neighbor_sum_bit0 & top_right_mask; neighbor_sum_bit0 ^= top_right_mask
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                
                # Mask 4: left_mask
                carry_bit0 = neighbor_sum_bit0 & left_mask; neighbor_sum_bit0 ^= left_mask
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                
                # Mask 5: right_mask
                carry_bit0 = neighbor_sum_bit0 & right_mask; neighbor_sum_bit0 ^= right_mask
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                
                # Mask 6: bot_left_mask
                carry_bit0 = neighbor_sum_bit0 & bot_left_mask; neighbor_sum_bit0 ^= bot_left_mask
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                
                # Mask 7: bot_mid_mask
                carry_bit0 = neighbor_sum_bit0 & bot_mid_mask; neighbor_sum_bit0 ^= bot_mid_mask
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1
                
                # Mask 8: bot_right_mask
                carry_bit0 = neighbor_sum_bit0 & bot_right_mask; neighbor_sum_bit0 ^= bot_right_mask
                carry_bit1 = neighbor_sum_bit1 & carry_bit0; neighbor_sum_bit1 ^= carry_bit0; neighbor_sum_bit2 ^= carry_bit1

                # Apply Brian's Brain rules bit-parallel
                # Rule: Off cell with exactly 2 neighbors becomes firing
                # Rule: Firing cell becomes dying
                # Rule: Dying cell becomes off
                
                # Check for exactly 2 neighbors: bit2=0, bit1=1, bit0=0
                inv_bit2_mask = (~neighbor_sum_bit2) & 0xFF
                exact_two_mask = inv_bit2_mask & neighbor_sum_bit1 & (~neighbor_sum_bit0 & 0xFF)
                
                # Current state masks - simplified
                off_cells = (~firing_byte) & (~dying_byte)  # Neither firing nor dying
                
                # Apply rules
                new_firing_byte = off_cells & exact_two_mask  # Off cells with 2 neighbors become firing
                new_dying_byte = firing_byte  # All firing cells become dying
                
                # Count births and deaths for statistics
                birth_count = popcount_ptr[new_firing_byte]
                death_count = popcount_ptr[firing_byte]  # Firing cells that will die
                
                total_born += birth_count
                total_died += death_count
                
                # Store results
                next_firing_ptr[current_byte_addr] = new_firing_byte
                next_dying_ptr[current_byte_addr] = new_dying_byte
                next_ptr[current_byte_addr] = new_firing_byte  # Display shows firing cells

        # Swap arrays efficiently
        for i in range(grid_len):
            # Swap firing grids
            temp_firing = firing_ptr[i]
            firing_ptr[i] = next_firing_ptr[i]
            next_firing_ptr[i] = temp_firing
            
            # Swap dying grids  
            temp_dying = dying_ptr[i]
            dying_ptr[i] = next_dying_ptr[i]
            next_dying_ptr[i] = temp_dying
        
        return (total_born & 0xffff) | ((total_died & 0xffff) << 16)
    
    @micropython.native
    def feed_rule(self, sim_current, sim_next, food_chance, num_alive):
        """Add random firing cells based on food chance"""
        from random import randint
        if food_chance <= 0: return num_alive
        
        # Initialize variables separately for MicroPython compatibility
        new_alive = num_alive
        w = self.width
        h = self.height
        bpr = self.bytes_per_row
        
        # Reduce iterations for better performance
        for _ in range(food_chance * 3):  # Reduced from 5 to 3
            # Calculate random position
            x = randint(0, w - 1)
            y = randint(0, h - 1)
            
            # Calculate byte and bit positions
            byte_idx = x >> 3  # Divide by 8
            bit_pos = x & 7    # Remainder of divide by 8
            
            # Calculate grid index and bit mask
            grid_idx = y * bpr + byte_idx
            bit_mask = 1 << bit_pos
            
            # Check if position is empty (not firing AND not dying)
            if not (self.firing_grid[grid_idx] & bit_mask) and not (self.dying_grid[grid_idx] & bit_mask):
                self.firing_grid[grid_idx] |= bit_mask
                sim_current[grid_idx] |= bit_mask
                sim_next[grid_idx] |= bit_mask
                new_alive += 1
        return new_alive

    @micropython.native
    def reset(self):
        """Reset all grids to empty state"""
        super().reset()
        for i in range(len(self.firing_grid)):
            self.firing_grid[i] = self.dying_grid[i] = self.next_firing[i] = self.next_dying[i] = 0

    @micropython.native
    def cv1_out(self, c):
        """Output firing cell density to CV1"""
        # Use the main alive counter instead of recalculating
        cv1.voltage(10 * c.num_alive / (self.width * self.height) if c.num_alive else 0)

    @micropython.native
    def cv2_out(self, c):
        """Output dying cell ratio to CV2"""
        # Estimate dying cells as a ratio of recent deaths instead of counting
        if c.num_alive > 0:
            dying_ratio = min(c.num_died / max(c.num_alive, 1), 1.0)
            cv2.voltage(10 * dying_ratio)
        else:
            cv2.voltage(0)

    @micropython.native
    def cv3_out(self, c): 
        """Output birth rate to CV3"""
        cv3.voltage(10 * min(c.num_born / 50.0, 1.0) if c.num_born else 0)

    @micropython.native
    def cv4_out(self, c): 
        """Output activity gate to CV4"""
        cv4.on() if c.num_born > 10 else cv4.off()