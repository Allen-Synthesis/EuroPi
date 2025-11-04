#!/usr/bin/env python3
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

"""Base class for cellular automata implementations in the Cellarium framework.

Provides foundational functionality and common features used by all cellular automata:
- Input and output handling
- Common utility methods

@author Unknown
@year 2025
"""

# Standard library imports
import math
from random import randint

# MicroPython imports
import micropython

# EuroPi imports
from europi import *
from europi_script import EuroPiScript

# Constants
POPCOUNT = bytes([bin(i).count("1") for i in range(256)])
LOG2 = math.log(2)
EPSILON = 1e-10

class BaseAutomata(EuroPiScript):
    def __init__(self, width, height, current_food_value, current_tick_limit):
        self.width = width
        self.height = height
        self.name = "Base Automaton"
        self.bytes_per_row = width // 8
        self.last_byte_index = self.bytes_per_row - 1
        self.current_food_value = current_food_value
        self.current_tick_limit = current_tick_limit
        self.stasis_max_pop_delta = 12
        self.min_stasis_pattern_length = 2
        self.max_stasis_pattern_length = 4
        self.use_stasis = True

    @micropython.native
    def update_input_data(self, current_food_value, current_tick_limit):
        self.current_food_value = current_food_value
        self.current_tick_limit = current_tick_limit

    @micropython.viper
    def simulate_generation(self, sim_current, sim_next) -> int:
        """Override to implement automata simulation logic.
        Returns packed integer: (births & 0xffff) | ((deaths & 0xffff) << 16)"""
        total_born = int(0)
        total_died = int(1)
        return ( (total_born & 0xffff) | (( total_died & 0xffff) << 16) )

    @micropython.native
    def feed_rule(self, sim_current, sim_next, food_chance, num_alive):
        """Override for feeding logic. Returns new num_alive count."""
        return num_alive
    
    @micropython.native
    def reset(self):
        """Override for reset logic."""
        reset = True
        return reset
        
    @micropython.native
    def stasis_rule(self, MAX_POP_DELTA, pop_deltas, num_born, num_died, num_alive=0):
        """Enhanced stasis detection with configurable pattern length.
        
        Detects repeating patterns in population deltas over a configurable number of generations.
        Uses self.stasis_pattern_length to determine how many generations to check for repetition.
        """
        if self.use_stasis is False:
            return False
        
        in_stasis = False
        pop_delta_count = len(pop_deltas)
        
        # Use instance variables, but fall back to parameter for compatibility
        max_deltas = self.stasis_max_pop_delta
        min_pattern_length = self.min_stasis_pattern_length
        max_pattern_length = self.max_stasis_pattern_length
        
        # Ensure pattern length doesn't exceed available data
        pattern_length = min(pattern_length, max_deltas // 2, pop_delta_count // 2)
        
        # Need at least twice the pattern length for comparison
        if pop_delta_count < max_pattern_length * 2:
            return False
        
        # Check for complete stasis (no changes)
        if num_born == 0 and num_died == 0:
            return True
        
        # Check for repeating pattern
        if max_pattern_length >= 2:
            recent = pop_deltas[-pattern_length * 2:]
            
            # Compare first half with second half of the pattern
            pattern_matches = True
            for pattern_length in range(min_pattern_length, max_pattern_length):
                for i in range(pattern_length):
                    if recent[i] != recent[i + pattern_length]:
                        pattern_matches = False
                        break
                if not pattern_matches:
                    break
            
            if pattern_matches:
                # Additional check: ensure the pattern represents minimal change
                # Sum of absolute changes in the pattern should be small
                total_pattern_change = sum(abs(recent[i]) for i in range(pattern_length))
                avg_change_per_generation = total_pattern_change / pattern_length if pattern_length > 0 else 0
                
                # Consider it stasis if average change per generation is very small
                if avg_change_per_generation <= 1.5:  # Configurable threshold
                    in_stasis = True
        
        return in_stasis

    def cv1_out(self, cellarium):
        """Override for CV1 output logic"""
        pass

    def cv2_out(self, cellarium):
        """Override for CV2 output logic"""
        pass

    def cv3_out(self, cellarium):
        """Override for CV3 output logic"""
        pass

    def cv4_out(self, cellarium):
        """Override for CV4 output logic"""
        pass

    #CV5 is gate triggered if in stasis
    #def cv5_out(self, cellarium):
    #    """Override for CV5 output logic"""
    #    pass
    
    #CV6 is gate triggered for simulation time
    #def cv6_out(self, cellarium):
    #    """Override for CV6 output logic"""
    #    pass