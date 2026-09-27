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

"""Implements multi-agent Langton's Ant cellular automaton.

Each ant follows simple rules that create complex emergent patterns:
1. At white square: Turn right, flip color, move forward
2. At black square: Turn left, flip color, move forward

Features:
- Multiple ants operating simultaneously
- Dynamic ant population control
- Spatial tracking and analysis
- Emergent pattern detection

Outputs:
- CV1: Ant population ratio
- CV2: Average ant X position
- CV3: Average ant Y position
- CV4: Population activity gate

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
from contrib.cellarium_docs.automata_base import BaseAutomata

class LangtonsAnt(BaseAutomata):
    """
    Langton's Ant cellular automaton implementation.
    
    A virtual ant moves on a grid following simple rules:
    1. At a white square, turn 90° right, flip the color, move forward
    2. At a black square, turn 90° left, flip the color, move forward
    
    This implementation supports multiple ants simultaneously.
    Despite simple rules, creates complex emergent behavior and
    eventually builds a recurring "highway" pattern.
    """
    def __init__(self, width, height, current_food_chance, current_tick_limit):
        super().__init__(width, height, current_food_chance, current_tick_limit)
        self.name = "Langton's Ant"
        self.use_stasis = False
        
        # Start with one ant in the center
        self.ants = []
        self.max_ants = 10
        self.total_steps = 0
        
    def reset(self):
        super().reset()
        self.ants.clear()
        self.total_steps = 0
        self.feed_rule()
    
    @micropython.viper
    def simulate_generation(self, sim_current, sim_next) -> int:
        """Multi-Ant Langton's Ant: process all ants simultaneously"""
        buf_len = int(len(sim_current))
        
        # Initialize dimensions for MicroPython compatibility
        bpr = int(self.bytes_per_row)
        w = int(self.width)
        h = int(self.height)
        
        # Get pointers to buffers
        curr_ptr = ptr8(sim_current)
        next_ptr = ptr8(sim_next)
        
        # Copy current state to next
        for i in range(buf_len):
            next_ptr[i] = curr_ptr[i]
        
        ants_list = self.ants
        num_ants = int(len(ants_list))
        
        # Process each ant
        for ant_idx in range(num_ants):
            ant = ants_list[ant_idx]
            ant_x = int(ant[0])
            ant_y = int(ant[1])
            ant_dir = int(ant[2])
            
            # Ensure ant is within bounds
            if ant_x >= 0 and ant_x < w and ant_y >= 0 and ant_y < h:
                # Get current cell state
                byte_idx = int(ant_y * bpr + (ant_x >> 3))
                bit_pos = int(ant_x & 7)
                
                if byte_idx >= 0 and byte_idx < buf_len:
                    current_cell = int((curr_ptr[byte_idx] >> bit_pos) & 1)
                    
                    # Langton's Ant rules:
                    # At white square (0): turn right, flip to black, move forward
                    # At black square (1): turn left, flip to white, move forward
                    if current_cell == 0:  # White square
                        ant_dir = (ant_dir + 1) % 4  # Turn right
                        next_ptr[byte_idx] |= (1 << bit_pos)  # Flip to black
                    else:  # Black square
                        ant_dir = (ant_dir + 3) % 4  # Turn left
                        next_ptr[byte_idx] &= ~(1 << bit_pos)  # Flip to white
                    
                    # Move forward in current direction
                    if ant_dir == 0:    # North
                        ant_y = ant_y - 1
                        if ant_y < 0: ant_y = h - 1
                    elif ant_dir == 1:  # East
                        ant_x = ant_x + 1
                        if ant_x >= w: ant_x = 0
                    elif ant_dir == 2:  # South
                        ant_y = ant_y + 1
                        if ant_y >= h: ant_y = 0
                    elif ant_dir == 3:  # West
                        ant_x = ant_x - 1
                        if ant_x < 0: ant_x = w - 1
                    
                    # Update ant position
                    ant[0] = ant_x
                    ant[1] = ant_y 
                    ant[2] = ant_dir
        
        self.total_steps = int(self.total_steps) + 1
        return int(self.total_steps)
    
    @micropython.native
    def feed_rule(self, sim_current, sim_next, food_chance, num_alive):
        """Spawn additional ants based on food_chance"""
        from random import randint
        if food_chance <= 0 or len(self.ants) >= self.max_ants:
            return num_alive
        
        self.ants.clear()
        
        # Spawn new ants based on food_chance
        # Higher food_chance = more likely to spawn ants
        ant_spawn_amount = min(food_chance, self.max_ants)
        
        for ant_idx in range(ant_spawn_amount):
            # Spawn ant at random location with random direction
            new_x = randint(0, self.width - 1)
            new_y = randint(0, self.height - 1)
            new_dir = randint(0, 3)
            self.ants.append([new_x, new_y, new_dir])
        
        return ant_spawn_amount

    @micropython.native  
    def cv1_out(self, c): 
        """CV1 output: Ant population ratio.
        
        Higher voltage = more ants currently active.
        0V = no ants, 10V = maximum number of ants (self.max_ants).
        Scales linearly with ant count.
        """
        from europi import cv1
        cv1.voltage(10 * min(len(self.ants) / self.max_ants, 1.0))

    @micropython.native
    def cv2_out(self, c): 
        """CV2 output: Average ant X position.
        
        Higher voltage = ants concentrated on right side.
        Lower voltage = ants concentrated on left side.
        0V = leftmost edge, 10V = rightmost edge.
        """
        from europi import cv2
        if self.ants:
            avg_x = sum(ant[0] for ant in self.ants) / len(self.ants)
            cv2.voltage(10 * (avg_x / self.width))
        else:
            cv2.voltage(0)

    @micropython.native
    def cv3_out(self, c): 
        """CV3 output: Average ant Y position.
        
        Higher voltage = ants concentrated at bottom.
        Lower voltage = ants concentrated at top.
        0V = top edge, 10V = bottom edge.
        """
        from europi import cv3
        if self.ants:
            avg_y = sum(ant[1] for ant in self.ants) / len(self.ants)
            cv3.voltage(10 * (avg_y / self.height))
        else:
            cv3.voltage(0)

    @micropython.native
    def cv4_out(self, c): 
        """CV4 output: Simulation progress.
        
        Higher voltage = more steps completed.
        Ramps up to 10V over 1000 steps, then stays at 10V.
        Useful for tracking long-term behavior development.
        """
        from europi import cv4
        cv4.voltage(10 * min(self.total_steps / 1000, 1.0))