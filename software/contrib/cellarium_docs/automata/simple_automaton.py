import micropython
from europi import cv1  # Only import what we need
from contrib.cellarium_docs.automata_base import BaseAutomata

class SimpleAutomaton(BaseAutomata):
    def __init__(self, width, height, current_food_value, current_tick_limit):
        super().__init__(width, height, current_food_value, current_tick_limit)
        self.name = "Simple"
        self.population = 0

    def simulate_generation(self, sim_current, sim_next):
        births = 0
        deaths = 0
        
        # Calculate and verify buffer size
        expected_buffer_size = (self.width * self.height) // 8
        actual_buffer_size = len(sim_next)
        if actual_buffer_size != expected_buffer_size:
            print(f"Buffer size mismatch: expected {expected_buffer_size}, got {actual_buffer_size}")
            # Use the smaller size to prevent index errors
            buffer_size = min(expected_buffer_size, actual_buffer_size)
        else:
            buffer_size = actual_buffer_size
            
        # Clear next grid
        for i in range(buffer_size):
            sim_next[i] = 0
            
        # Keep track of which tick we're on (alternating between 0 and 1)
        self.tick = getattr(self, 'tick', 0)
        self.tick = 1 - self.tick  # Flip between 0 and 1
        
        # Process the grid one byte at a time
        for y in range(self.height):
            for byte_x in range(self.bytes_per_row):
                byte_index = y * self.bytes_per_row + byte_x
                
                # Skip if we're beyond buffer size
                if byte_index >= buffer_size:
                    continue
                    
                # Handle each bit in the current byte
                for bit in range(8):
                    # Calculate actual x position
                    x = byte_x * 8 + bit
                    
                    # Skip if beyond actual width
                    if x >= self.width:
                        continue
                    
                    bit_mask = 1 << bit
                    is_alive = bool(sim_current[byte_index] & bit_mask)
                    
                    # Create checkerboard pattern that alternates each tick
                    should_be_alive = ((x + y) % 2) == self.tick
                    
                    if should_be_alive and not is_alive:
                        sim_next[byte_index] |= bit_mask
                        births += 1
                    elif not should_be_alive and is_alive:
                        deaths += 1
        
        # Pack births and deaths into return value as required by framework
        return int((births & 0xffff) | ((deaths & 0xffff) << 16))

    @micropython.native
    def feed_rule(self, sim_current, sim_next, food_chance, num_alive) -> int:
        self.population = num_alive
        return num_alive

    @micropython.native
    def cv1_out(self, cellarium):
        # Output population as voltage
        voltage = (self.population / (self.width * self.height)) * 10
        cv1.voltage(voltage)
