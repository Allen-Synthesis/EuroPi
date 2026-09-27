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

"""Implements water droplet physics simulation using cellular automata rules.

Features realistic water flow and interaction mechanics:
- Fluid dynamics with gravity and surface tension
- Procedurally generated terrain obstacles
- Multi-point water source spawning
- Animated flow visualization
- Configurable boundary conditions

Outputs:
- CV1: Water volume level
- CV2: Flow velocity
- CV3: Terrain interaction
- CV4: Overflow detection gate

Fully custom cellular automaton authored by:
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

# Simulation constants
# Rock generation parameters
MIN_ROCK_COUNT = 1
MAX_ROCK_COUNT = 20
MIN_ROCK_RADIUS = 5
MAX_ROCK_RADIUS = 16
MIN_ROCK_HEIGHT = 3
MAX_ROCK_HEIGHT = 6

# Water parameters
MAX_DROPLET_AMOUNT = 10000
MAX_DROPLET_RESPAWN_PER_FRAME = 5

# Spawn area constants (as fractions of screen dimensions 0.0-1.0)
WATER_SPAWN_MIN_X = 0.0    # Left edge
WATER_SPAWN_MAX_X = 1.0    # Right edge  
WATER_SPAWN_MIN_Y = 0.0    # Top edge
WATER_SPAWN_MAX_Y = 0.3    # Top 30% of screen

BLOB_SPAWN_MIN_X = 0.0     # Left edge
BLOB_SPAWN_MAX_X = 1.0     # Right edge
BLOB_SPAWN_MIN_Y = 0.4     # 40% from top edge  
BLOB_SPAWN_MAX_Y = 1.0     # Bottom edge

# Visualization patterns
TERRAIN_PATTERNS = {
    'solid':  0xFFFF,     # Full solid
    'dense':  0xFBDF,     # Dense dithered
    'medium': 0xA5A5,     # 50% checkerboard
    'light':  0x2408,     # Light dithered
    'sparse': 0x1004      # Very sparse
}

# Animated water flow patterns (4x4)
WATER_ANIMATION_PATTERNS = [
    0xFFFF,  # Frame 0: Solid (stationary)
    0xF7EF,  # Frame 1: Dense flow 1
    0xEFBF,  # Frame 2: Dense flow 2  
    0xBFDF,  # Frame 3: Dense flow 3
]

class Droplets(BaseAutomata):
    """
    Water droplet simulation using cellular automaton rules.
    
    Features:
    - Realistic water flow and pooling behavior
    - Procedurally generated terrain obstacles
    - Water source spawning system
    - Optional flow animation patterns
    - Configurable edge behavior
    
    Controls:
    - disable_water_animation: Toggle water pattern animation
    - bottom_edge_is_terrain: Make bottom edge solid or permeable
    """
    def __init__(self, width, height, current_food_value, current_tick_limit):
        super().__init__(width, height, current_food_value, current_tick_limit)
        self.name = "Droplets"
        self.use_stasis = False  # Water simulation doesn't reach stasis
        
        # Separate buffers for water and terrain
        grid_size = (width * height) // 8
        self.water_current = bytearray(grid_size)
        self.water_next = bytearray(grid_size)
        self.terrain_grid = bytearray(grid_size)  # Solid terrain for collision detection
        self.terrain_display = bytearray(grid_size)  # Dithered terrain for display, water is actually only animated when we display to the sim_current buffer
        
        # Row-based bias directions (one direction per row)
        # 0 = left bias (check left first), 1 = right bias (check right first)
        self.row_bias_directions = bytearray(height)
        
        # Animation frame counter for water flow effects
        self.animation_frame = 0
        
        # Animation control option
        self.disable_water_animation = True  # Set to True to render raw droplets
        
        # Edge behavior control
        self.bottom_edge_is_terrain = False  # Set to True to make bottom edge act like terrain
        
        # CV output tracking variables (for viper compatibility, use standard operators)
        self.droplets_moved_down = 0      # CV1: Number of droplets that moved down due to gravity
        self.droplets_hit_bottom = 0      # CV2: Number of droplets that hit bottom edge  
        self.droplets_respawned = 0       # CV3: Number of new droplets added this tick
        self.total_bias_samples = 0       # CV4: Total bias samples for average calculation
        self.right_bias_count = 0         # CV4: Count of right-biased droplets
        
        # Running droplet count for performance (updated during simulation)
        self.current_droplet_count = 0    # Total droplets currently in simulation
        
        # Calculate how many droplets we can add this frame
        self.droplets_to_add = (self.current_food_value / 100 ) * MAX_DROPLET_RESPAWN_PER_FRAME
        
        # Row bias flip tracking
        self.row_droplet_counts = bytearray(height)      # Count of droplets per row
        self.row_blocked_counts = bytearray(height)      # Count of blocked droplets per row
        
        # Generate initial terrain
        self._generate_terrain()
        
        # Initialize row bias directions with random values
        self._initialize_random_row_bias()
        
    @micropython.native
    def _initialize_random_row_bias(self):
        """Initialize row bias directions with random values"""
        for row in range(self.height):
            # Generate random bias for each row: 0 = left bias, 1 = right bias
            self.row_bias_directions[row] = randint(0, 1)
    
    @micropython.viper
    def _check_and_flip_blocked_rows(self):
        """Check if all droplets in a row are blocked in bias direction and flip bias if so"""
        h = int(self.height)
        
        # Get pointers for fast array access
        row_droplet_counts_ptr = ptr8(self.row_droplet_counts)
        row_blocked_counts_ptr = ptr8(self.row_blocked_counts)
        row_bias_directions_ptr = ptr8(self.row_bias_directions)
        
        row = int(0)
        while row < h:
            droplet_count = int(row_droplet_counts_ptr[row])
            blocked_count = int(row_blocked_counts_ptr[row])
            
            # If there are droplets in this row and ALL of them are blocked in bias direction
            if droplet_count > 0 and blocked_count == droplet_count:
                # Flip the bias direction for this row
                current_bias = int(row_bias_directions_ptr[row])
                row_bias_directions_ptr[row] = int(1 - current_bias)
            
            row = int(row + 1)
        
    @micropython.native
    def _generate_terrain(self):
        """Generate randomized terrain blobs of different sizes and irregular shapes"""
        w, h, bpr = self.width, self.height, self.bytes_per_row
        
        # Clear terrain grids first
        for i in range(len(self.terrain_grid)):
            self.terrain_grid[i] = 0
            self.terrain_display[i] = 0
            
        # Generate random terrain blobs
        num_blobs = randint(MIN_ROCK_COUNT, MAX_ROCK_COUNT)
        
        for blob_idx in range(num_blobs):
            # Random blob center using spawn area constants
            min_x = int(w * BLOB_SPAWN_MIN_X)
            max_x = int(w * BLOB_SPAWN_MAX_X)
            min_y = int(h * BLOB_SPAWN_MIN_Y)
            max_y = int(h * BLOB_SPAWN_MAX_Y)
            
            center_x = randint(min_x, max_x)
            center_y = randint(min_y, max_y)
            
            # Random blob size
            blob_radius = randint(MIN_ROCK_RADIUS, MAX_ROCK_RADIUS)
            blob_height = randint(MIN_ROCK_HEIGHT, MAX_ROCK_HEIGHT)
            
            # Create irregular blob shape
            for dy in range(-blob_height, blob_height + 1):
                for dx in range(-blob_radius, blob_radius + 1):
                    x = center_x + dx
                    y = center_y + dy
                    
                    # Check bounds
                    if 0 <= x < w and 0 <= y < h:
                        # Create irregular shape using distance and random noise
                        distance_sq = dx * dx + dy * dy
                        max_distance_sq = blob_radius * blob_radius
                        
                        # Add randomness to make irregular blobs
                        noise = randint(-4, 4)
                        adjusted_distance_sq = distance_sq + noise * noise
                        
                        # Create gradient effect - denser in center, sparser at edges
                        if adjusted_distance_sq <= max_distance_sq:
                            # Calculate density based on distance from center
                            distance_ratio = adjusted_distance_sq / max_distance_sq
                            
                            # Higher chance for pixels closer to center
                            placement_chance = 1.0 - distance_ratio
                            
                            # Add some randomness to edges
                            random_factor = randint(0, 100) / 100.0
                            
                            if random_factor < placement_chance:
                                byte_idx, bit_pos = x >> 3, x & 7
                                grid_idx = y * bpr + byte_idx
                                bit_mask = 1 << bit_pos
                                
                                # Always set solid terrain for collision detection
                                self.terrain_grid[grid_idx] |= bit_mask
                                
                                # Set dithered terrain for display - inline pattern check
                                # Using 'dense' pattern: 0xFBDF
                                pattern_x = x & 3
                                pattern_y = y & 3
                                pattern_bit = pattern_y * 4 + pattern_x
                                if (0xFBDF >> pattern_bit) & 1:
                                    self.terrain_display[grid_idx] |= bit_mask
    
    @micropython.viper
    def simulate_generation(self, sim_current, sim_next) -> int:
        """Fast byte-parallel water simulation with terrain collision and row-based bias"""
        w = int(self.width)
        h = int(self.height)
        bpr = int(self.bytes_per_row)
        grid_len = int(len(self.water_current))
        
        # Get pointers for current and next states
        water_curr_ptr = ptr8(self.water_current)
        water_next_ptr = ptr8(self.water_next)
        terrain_ptr = ptr8(self.terrain_grid)
        row_bias_ptr = ptr8(self.row_bias_directions)
        
        # Cache frequently accessed instance variables as local variables for performance
        total_moved = int(0)
        droplets_moved_down = int(0)
        droplets_hit_bottom = int(0)
        droplets_respawned = int(0)
        total_bias_samples = int(0)
        right_bias_count = int(0)
        bottom_edge_is_terrain = bool(self.bottom_edge_is_terrain)
        current_droplet_count = int(0)  # Count droplets during simulation
        
        # Pre-allocate local arrays for row tracking (faster than instance variables)
        row_droplet_counts = ptr8(self.row_droplet_counts)
        row_blocked_counts = ptr8(self.row_blocked_counts)
        
        # Reset row tracking arrays efficiently
        for row in range(h):
            row_droplet_counts[row] = 0
            row_blocked_counts[row] = 0
        
        # Initialize next state by clearing it efficiently
        i = int(0)
        while i < grid_len:
            water_next_ptr[i] = 0
            i = i + 1
            
        # Process water flow from bottom to top (gravity)
        row = int(h - 1)
        while row >= 0:
            row_offset = int(row * bpr)
            row_bias = int(row_bias_ptr[row])  # Get bias direction for this row
            
            # Cache row-specific variables
            row_droplet_count = int(0)
            row_blocked_count = int(0)
            
            # Determine iteration order based on row bias
            # If bias is left (0), iterate left to right (so left cells are processed first)
            # If bias is right (1), iterate right to left (so right cells are processed first)
            iterate_left_to_right = int(row_bias == 0)
            
            if iterate_left_to_right:
                # Process bytes from left to right
                byte_idx = int(0)
                while byte_idx < bpr:
                    current_addr = int(row_offset + byte_idx)
                    water_byte = int(water_curr_ptr[current_addr])
                    
                    if water_byte != 0:
                        # Process bits from left to right (0 to 7)
                        bit_pos = int(0)
                        while bit_pos < 8:
                            bit_mask = int(1 << bit_pos)
                            
                            if water_byte & bit_mask:
                                x = int((byte_idx << 3) + bit_pos)
                                if x < w:
                                    moved = int(0)
                                    blocked_in_bias_direction = int(0)
                                    
                                    # Count this droplet for the row (use local cache)
                                    row_droplet_count = row_droplet_count + 1
                                    
                                    # Count this droplet for total running count
                                    current_droplet_count = current_droplet_count + 1
                                    
                                    # Track bias for CV4 (use local cache)
                                    total_bias_samples = total_bias_samples + 1
                                    if row_bias == 1:  # Right bias
                                        right_bias_count = right_bias_count + 1
                                    
                                    # Try to move down first
                                    can_move_down = int(0)
                                    if row < h - 1:
                                        down_row = int(row + 1)
                                        down_addr = int(down_row * bpr + byte_idx)
                                        down_terrain = int(terrain_ptr[down_addr])
                                        down_water_next = int(water_next_ptr[down_addr])
                                        
                                        # Check if we can move down (no terrain AND no water in next state)
                                        if not (down_terrain & bit_mask) and not (down_water_next & bit_mask):
                                            can_move_down = int(1)
                                    elif row == h - 1 and not bottom_edge_is_terrain:
                                        # At bottom row with deletion mode - can move down (will be deleted later)
                                        can_move_down = int(1)
                                    
                                    if can_move_down:
                                        if row < h - 1:
                                            down_row = int(row + 1)
                                            down_addr = int(down_row * bpr + byte_idx)
                                            # Double-check that position is still free before moving
                                            current_water_at_target = int(water_next_ptr[down_addr])
                                            if not (current_water_at_target & bit_mask):
                                                water_next_ptr[down_addr] = int(water_next_ptr[down_addr] | bit_mask)
                                                moved = int(1)
                                                total_moved = total_moved + 1
                                                droplets_moved_down = droplets_moved_down + 1
                                            else:
                                                # Position was taken by another droplet, stay in place
                                                can_move_down = int(0)
                                        else:
                                            # If row == h - 1, droplet will be deleted later by _handle_bottom_edge_deletion
                                            moved = int(1)
                                            total_moved = total_moved + 1
                                            droplets_moved_down = droplets_moved_down + 1
                                    
                                    # If couldn't move down, try sideways based on row bias
                                    if moved == 0:
                                        # Determine direction based on row bias
                                        if row_bias == 1:  # Right bias
                                            side_dir = int(1)   # Right
                                        else:  # Left bias
                                            side_dir = int(-1)  # Left
                                        
                                        # Try to move in bias direction only
                                        new_x = int(x + side_dir)
                                        if 0 <= new_x and new_x < w:
                                            new_byte_idx = int(new_x >> 3)
                                            new_bit_pos = int(new_x & 7)
                                            new_bit_mask = int(1 << new_bit_pos)
                                            new_addr = int(row_offset + new_byte_idx)
                                            
                                            side_terrain = int(terrain_ptr[new_addr])
                                            side_water_next = int(water_next_ptr[new_addr])
                                            
                                            # Check if target position is free AND not already reserved
                                            if not (side_terrain & new_bit_mask) and not (side_water_next & new_bit_mask):
                                                # Double-check that position is still free (atomic-like operation)
                                                current_water_at_target = int(water_next_ptr[new_addr])
                                                if not (current_water_at_target & new_bit_mask):
                                                    water_next_ptr[new_addr] = int(water_next_ptr[new_addr] | new_bit_mask)
                                                    moved = int(1)
                                                    total_moved = total_moved + 1
                                                else:
                                                    # Blocked in bias direction
                                                    blocked_in_bias_direction = int(1)
                                            else:
                                                # Blocked in bias direction
                                                blocked_in_bias_direction = int(1)
                                        else:
                                            # Can't move in bias direction (edge of screen)
                                            blocked_in_bias_direction = int(1)
                                    
                                    # If couldn't move at all, stay in place
                                    if moved == 0:
                                        water_next_ptr[current_addr] = int(water_next_ptr[current_addr] | bit_mask)
                                    
                                    # Track if this droplet was blocked in bias direction (use local cache)
                                    if blocked_in_bias_direction == 1:
                                        row_blocked_count = row_blocked_count + 1
                            
                            bit_pos = int(bit_pos + 1)
                    
                    byte_idx = int(byte_idx + 1)
            else:
                # Process bytes from right to left
                byte_idx = int(bpr - 1)
                while byte_idx >= 0:
                    current_addr = int(row_offset + byte_idx)
                    water_byte = int(water_curr_ptr[current_addr])
                    
                    if water_byte != 0:
                        # Process bits from right to left (7 to 0)
                        bit_pos = int(7)
                        while bit_pos >= 0:
                            bit_mask = int(1 << bit_pos)
                            
                            if water_byte & bit_mask:
                                x = int((byte_idx << 3) + bit_pos)
                                if x < w:
                                    moved = int(0)
                                    blocked_in_bias_direction = int(0)
                                    
                                    # Count this droplet for the row (use local cache)
                                    row_droplet_count = row_droplet_count + 1
                                    
                                    # Count this droplet for total running count
                                    current_droplet_count = current_droplet_count + 1
                                    
                                    # Track bias for CV4 (use local cache)
                                    total_bias_samples = total_bias_samples + 1
                                    if row_bias == 1:  # Right bias
                                        right_bias_count = right_bias_count + 1
                                    
                                    # Try to move down first
                                    can_move_down = int(0)
                                    if row < h - 1:
                                        down_row = int(row + 1)
                                        down_addr = int(down_row * bpr + byte_idx)
                                        down_terrain = int(terrain_ptr[down_addr])
                                        down_water_next = int(water_next_ptr[down_addr])
                                        
                                        # Check if we can move down (no terrain AND no water in next state)
                                        if not (down_terrain & bit_mask) and not (down_water_next & bit_mask):
                                            can_move_down = int(1)
                                    elif row == h - 1 and not bottom_edge_is_terrain:
                                        # At bottom row with deletion mode - can move down (will be deleted later)
                                        can_move_down = int(1)
                                    
                                    if can_move_down:
                                        if row < h - 1:
                                            down_row = int(row + 1)
                                            down_addr = int(down_row * bpr + byte_idx)
                                            # Double-check that position is still free before moving
                                            current_water_at_target = int(water_next_ptr[down_addr])
                                            if not (current_water_at_target & bit_mask):
                                                water_next_ptr[down_addr] = int(water_next_ptr[down_addr] | bit_mask)
                                                moved = int(1)
                                                total_moved = total_moved + 1
                                                droplets_moved_down = droplets_moved_down + 1
                                            else:
                                                # Position was taken by another droplet, stay in place
                                                can_move_down = int(0)
                                        else:
                                            # If row == h - 1, droplet will be deleted later by _handle_bottom_edge_deletion
                                            moved = int(1)
                                            total_moved = total_moved + 1
                                            droplets_moved_down = droplets_moved_down + 1
                                    
                                    # If couldn't move down, try sideways based on row bias
                                    if moved == 0:
                                        # Determine direction based on row bias
                                        if row_bias == 1:  # Right bias
                                            side_dir = int(1)   # Right
                                        else:  # Left bias
                                            side_dir = int(-1)  # Left
                                        
                                        # Try to move in bias direction only
                                        new_x = int(x + side_dir)
                                        if 0 <= new_x and new_x < w:
                                            new_byte_idx = int(new_x >> 3)
                                            new_bit_pos = int(new_x & 7)
                                            new_bit_mask = int(1 << new_bit_pos)
                                            new_addr = int(row_offset + new_byte_idx)
                                            
                                            side_terrain = int(terrain_ptr[new_addr])
                                            side_water_next = int(water_next_ptr[new_addr])
                                            
                                            # Check if target position is free AND not already reserved
                                            if not (side_terrain & new_bit_mask) and not (side_water_next & new_bit_mask):
                                                # Double-check that position is still free (atomic-like operation)
                                                current_water_at_target = int(water_next_ptr[new_addr])
                                                if not (current_water_at_target & new_bit_mask):
                                                    water_next_ptr[new_addr] = int(water_next_ptr[new_addr] | new_bit_mask)
                                                    moved = int(1)
                                                    total_moved = total_moved + 1
                                                else:
                                                    # Blocked in bias direction
                                                    blocked_in_bias_direction = int(1)
                                            else:
                                                # Blocked in bias direction
                                                blocked_in_bias_direction = int(1)
                                        else:
                                            # Can't move in bias direction (edge of screen)
                                            blocked_in_bias_direction = int(1)
                                    
                                    # If couldn't move at all, stay in place
                                    if moved == 0:
                                        water_next_ptr[current_addr] = int(water_next_ptr[current_addr] | bit_mask)
                                    
                                    # Track if this droplet was blocked in bias direction (use local cache)
                                    if blocked_in_bias_direction == 1:
                                        row_blocked_count = row_blocked_count + 1
                            
                            bit_pos = int(bit_pos - 1)
                    
                    byte_idx = int(byte_idx - 1)
            
            # Write cached row data back to arrays at end of row processing
            row_droplet_counts[row] = row_droplet_count
            row_blocked_counts[row] = row_blocked_count
            
            row = int(row - 1)
        
        # Swap arrays efficiently
        for i in range(grid_len):
            # Swap water grids
            temp_water = water_curr_ptr[i]
            water_curr_ptr[i] = water_next_ptr[i]
            water_next_ptr[i] = temp_water
        
        # Write cached values back to instance variables
        self.droplets_moved_down = droplets_moved_down
        self.droplets_hit_bottom = droplets_hit_bottom
        self.droplets_respawned = droplets_respawned
        self.total_bias_samples = total_bias_samples
        self.right_bias_count = right_bias_count
        self.current_droplet_count = current_droplet_count
        
        # Increment animation frame
        current_animation_frame = int(self.animation_frame)
        self.animation_frame = int(current_animation_frame) + 1
        
        # Handle deletion of droplets that reached the bottom edge
        self._handle_bottom_edge_deletion()
        
        # Add new droplets each frame if needed
        self._add_new_droplets()
        
        # Check for blocked rows and flip bias if needed
        self._check_and_flip_blocked_rows()
        
        # Apply final display composition
        self._apply_final_display(sim_current, sim_next)
            
        return int(total_moved)

    @micropython.viper
    def _handle_bottom_edge_deletion(self):
        """Delete droplets that have reached the bottom edge (if enabled)"""
        # If bottom edge acts as terrain, don't delete droplets
        if bool(self.bottom_edge_is_terrain):
            return
            
        w = int(self.width)
        h = int(self.height)
        bpr = int(self.bytes_per_row)
        bottom_row = int(h - 1)
        bottom_row_offset = int(bottom_row * bpr)
        
        # Get pointer for fast access
        water_current_ptr = ptr8(self.water_current)
        
        droplets_hit_bottom = int(self.droplets_hit_bottom)
        current_droplet_count = int(self.current_droplet_count)

        # Scan bottom row for water droplets and delete them
        byte_idx = int(0)
        while byte_idx < bpr:
            grid_idx = int(bottom_row_offset + byte_idx)
            water_byte = int(water_current_ptr[grid_idx])
            
            if water_byte != 0:
                # Check each bit in the byte
                bit_pos = int(0)
                while bit_pos < 8:
                    bit_mask = int(1 << bit_pos)
                    if water_byte & bit_mask:
                        x = int((byte_idx << 3) + bit_pos)
                        if x < w:
                            # Remove droplet from bottom
                            water_current_ptr[grid_idx] &= ~bit_mask
                            
                            # Update running count
                            current_droplet_count = current_droplet_count - 1
                            
                            # Track droplets that hit bottom edge (CV2)
                            droplets_hit_bottom = droplets_hit_bottom + 1
                    bit_pos = bit_pos + 1
            byte_idx = byte_idx + 1
        
        # Write back cached values
        self.droplets_hit_bottom = droplets_hit_bottom
        self.current_droplet_count = current_droplet_count

    @micropython.native
    def _add_new_droplets(self):
        """Add new droplets each frame based on constants and current count"""
        if self.current_food_value <= 0:
            return
            
        # Use cached droplet count instead of expensive bit counting
        current_droplet_count = self.current_droplet_count
        max_droplets = MAX_DROPLET_AMOUNT
        
        # If we already have more droplets than the max, don't add any
        if current_droplet_count >= max_droplets:
            return
            
        # Calculate how many droplets we can add this frame
        # Make sure we don't exceed the max droplet count
        available_space = max_droplets - current_droplet_count
        self.droplets_to_add = (self.current_food_value / 100 ) * MAX_DROPLET_RESPAWN_PER_FRAME
        droplets_to_add = min(self.droplets_to_add, available_space)
        
        # Cache frequently used values
        w = self.width
        h = self.height
        bpr = self.bytes_per_row
        droplets_added = 0
        
        # Pre-calculate spawn area bounds
        min_x = int(w * WATER_SPAWN_MIN_X)
        max_x = int(w * WATER_SPAWN_MAX_X - 1)
        min_y = int(h * WATER_SPAWN_MIN_Y)
        max_y = int(h * WATER_SPAWN_MAX_Y)
        
        for droplet in range(droplets_to_add):
            # Try to find a free position in spawn area
            attempts = 0
            while attempts < 10:  # Limit attempts to avoid infinite loop
                x = randint(min_x, max_x)
                y = randint(min_y, max_y)
                
                byte_idx = x >> 3
                bit_pos = x & 7
                bit_mask = 1 << bit_pos
                grid_idx = y * bpr + byte_idx
                
                # Only add if no terrain and no water already there
                if not (self.terrain_grid[grid_idx] & bit_mask) and not (self.water_current[grid_idx] & bit_mask):
                    self.water_current[grid_idx] |= bit_mask
                    droplets_added += 1
                    # Update running count
                    self.current_droplet_count += 1
                    break
                attempts += 1
        
        # Track successful spawns (CV3)
        self.droplets_respawned = droplets_added

    @micropython.viper
    def _apply_final_display(self, sim_current, sim_next):
        """Combine terrain and water display buffers for final output"""
        w = int(self.width)
        h = int(self.height)
        bpr = int(self.bytes_per_row)
        
        # Get pointers for fast array access
        sim_current_ptr = ptr8(sim_current)
        sim_next_ptr = ptr8(sim_next)
        terrain_display_ptr = ptr8(self.terrain_display)
        water_current_ptr = ptr8(self.water_current)
        
        grid_len = int(len(sim_current))
        disable_water_animation = bool(self.disable_water_animation)
        animation_frame = int(self.animation_frame)
        
        # Clear display buffers first
        i = int(0)
        while i < grid_len:
            sim_current_ptr[i] = 0
            sim_next_ptr[i] = 0
            i = i + 1
        
        # Apply dithered terrain for display
        i = int(0)
        while i < grid_len:
            sim_current_ptr[i] |= terrain_display_ptr[i]
            i = i + 1
        
        # Apply water display directly to sim_current (animated or raw)
        if disable_water_animation:
            # Raw droplet display - copy water_current directly to sim_current
            i = int(0)
            while i < grid_len:
                sim_current_ptr[i] |= water_current_ptr[i]
                i = i + 1
        else:
            # Animated water display
            frame = int(animation_frame & 3)  # 0-3 cycle
            
            # Pre-calculate pattern for efficiency
            if frame == 0:
                pattern = int(0xFFFF)  # WATER_ANIMATION_PATTERNS[0]
            elif frame == 1:
                pattern = int(0xF7EF)  # WATER_ANIMATION_PATTERNS[1]
            elif frame == 2:
                pattern = int(0xEFBF)  # WATER_ANIMATION_PATTERNS[2]
            else:
                pattern = int(0xBFDF)  # WATER_ANIMATION_PATTERNS[3]
            
            y = int(0)
            while y < h:
                row_offset = int(y * bpr)
                byte_idx = int(0)
                while byte_idx < bpr:
                    grid_idx = int(row_offset + byte_idx)
                    water_byte = int(water_current_ptr[grid_idx])
                    
                    if water_byte != 0:
                        # Process each bit in the byte
                        bit_pos = int(0)
                        while bit_pos < 8:
                            bit_mask = int(1 << bit_pos)
                            if water_byte & bit_mask:
                                x = int((byte_idx << 3) + bit_pos)
                                if x < w:
                                    # Apply animated water pattern - inline pattern check
                                    pattern_x = int(x & 3)
                                    pattern_y = int(y & 3)
                                    pattern_bit = int(pattern_y * 4 + pattern_x)
                                    if (pattern >> pattern_bit) & 1:
                                        sim_current_ptr[grid_idx] |= bit_mask
                            bit_pos = bit_pos + 1
                    byte_idx = byte_idx + 1
                y = y + 1
        
        # Copy to next buffer
        i = int(0)
        while i < grid_len:
            sim_next_ptr[i] = sim_current_ptr[i]
            i = i + 1

    @micropython.native
    def feed_rule(self, sim_current, sim_next, food_chance, num_alive):
        """Store current food value for droplet spawning control"""
        self._add_new_droplets()
        # Return cached droplet count
        return self.current_droplet_count

    @micropython.native
    def reset(self):
        """Reset water and generate new terrain every time"""
        super().reset()
        
        # Clear water grids
        for i in range(len(self.water_current)):
            self.water_current[i] = 0
            self.water_next[i] = 0
            self.terrain_grid[i] = 0
            self.terrain_display[i] = 0
        
        # Reset row bias directions
        self.row_bias_directions = bytearray(self.height)
            
        # Reset running droplet count
        self.current_droplet_count = 0
            
        # Always generate new terrain on reset for variety
        self._generate_terrain()
        
        # Initialize row bias directions with random values
        self._initialize_random_row_bias()

    @micropython.native
    def cv1_out(self, cellarium):
        """Output number of droplets that moved down due to gravity (0-10V scale)"""
        # Scale based on reasonable max expected (e.g., 50 droplets moving down per tick)
        voltage = 0
        if MAX_DROPLET_AMOUNT > 0:
            voltage = 10 * min(self.droplets_moved_down / MAX_DROPLET_AMOUNT, 1.0)
        cv1.voltage(voltage)

    @micropython.native  
    def cv2_out(self, cellarium):
        """Output number of droplets that hit bottom edge (0-10V scale) - only when deletion enabled"""
        # Scale based on max possible (e.g., 200 droplets hitting bottom per tick)
        voltage = 0
        if MAX_DROPLET_AMOUNT > 0:
            voltage = 10 * min(self.droplets_hit_bottom / MAX_DROPLET_AMOUNT, 1.0)
        cv2.voltage(voltage)

    @micropython.native
    def cv3_out(self, cellarium):
        """Output number of new droplets added this tick (0-10V scale)"""
        # Scale based on reasonable max expected (e.g., 10 new droplets per tick)
        voltage = 0
        if self.droplets_to_add > 0:
            voltage = 10 * min(self.droplets_respawned / self.droplets_to_add, 1.0)
        cv3.voltage(voltage)

    @micropython.native
    def cv4_out(self, cellarium):
        """Output average left/right bias (0V=all left, 5V=balanced, 10V=all right)"""
        if self.total_bias_samples > 0:
            # Calculate right bias ratio (0.0 = all left, 1.0 = all right)
            right_bias_ratio = self.right_bias_count / self.total_bias_samples
            # Scale to 0-10V where 5V is the midpoint (0.5 ratio)
            voltage = 10 * right_bias_ratio
            cv4.voltage(voltage)
        else:
            # No bias samples this tick, output midpoint (balanced)
            cv4.voltage(5.0)