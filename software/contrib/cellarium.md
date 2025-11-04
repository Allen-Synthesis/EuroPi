# Cellarium: A Cellular Automata Framework for EuroPi

> *Etymology:*
> 
> *cell (plural cells), Noun*  
> &nbsp;&nbsp;&nbsp;&nbsp;*1. The basic unit of a living organism*  
> &nbsp;&nbsp;&nbsp;&nbsp;*2. The minimal unit of a cellular automaton that can change state*
>
> *-arium (plural -ariums or -aria), Suffix*  
> &nbsp;&nbsp;&nbsp;&nbsp;*1. A place associated with a specified thing*  
> &nbsp;&nbsp;&nbsp;&nbsp;*2. A device associated with a specified function*
>
> *Cellarium, Noun*  
> &nbsp;&nbsp;&nbsp;&nbsp;*1. A place for observing cellular automata simulations, such as Life*

Cellarium is a flexible and performant cellular automata framework designed for the EuroPi modular synthesis platform. It enables the creation and execution of various cellular automata patterns that can be used for generative CV and gate modulation.

## Features

- High-performance MicroPython optimized simulation engine
- Multiple included automata implementations
  - Conway's Game of Life
  - Brian's Brain
  - Rule 30 & Rule 90 (Elementary Cellular Automata)
  - Langton's Ant
  - Water Droplets Simulation
  - Seeds
- Dynamic pattern visualization on the OLED display
- CV input/output mapping for each automaton
- Configurable simulation parameters
- Extensible architecture for adding new automata

## Controls and Settings

The Cellarium interface provides comprehensive control over simulation parameters and modes:

### Core Controls

- **K1 (Knob 1)**: Controls food value (0-100) for population growth
- **K2 (Knob 2)**: Controls tick rate limit (0-500ms) for simulation speed
- **B1**: Cycles through different B2 modes
- **B2**: Activates or adjusts the current mode's settings

### B2 Modes

1. **RESET**: Clears and reinitializes the simulation
2. **FEED**: Triggers manual feeding of the simulation
3. **CLOCK**: Enables manual clock control
4. **AUTOMATA**: Cycles through available cellular automata
5. **D IN**: Configure digital input behavior
   - OFF: Digital input disabled
   - RESET: Triggers simulation reset
   - FEED: Triggers feeding
   - CLOCK: External clock input
6. **A IN**: Configure analog input behavior
   - OFF: Analog input disabled
   - FEED: Modulates food value
   - TICK: Modulates tick rate
7. **CV SYNC**: Set CV output division ratio
   - Available ratios: 1/1, 1/2, 1/4, 1/8, 1/16
   - Based on simulation tick count, so 1/2 would be every second simulation tick
8. **STASIS**: Configure stasis response
   - FEED: Auto-feed when stasis detected
   - RESET: Auto-reset when stasis detected
   - OFF: No action on stasis

### CV Outputs

- **CV1-4**: Automaton-specific outputs
- **CV5**: Stasis indication (on when in stasis)
- **CV6**: Simulation duration gate (clock)

## Patch Examples

Here are some creative ways to use different automata in your patches:

### Complex Life Modulation
Using Conway's Game of Life:
1. Set STASIS mode to OFF
2. Turn K1 (food value) to about 75%
3. Set D IN mode to FEED or RESET
4. Use CV2 for envelope shape (birth rate)
5. Use CV3 for amplitude (population density)
6. CV4 gates a VCA (population growth)
- Creates organic modulation based on colony entropy (CV1)
- K1 adjusts pattern complexity
- K2 controls evolution speed
- CV1 great for filter cutoff modulation

### Water Flow Dynamics
Using Water Droplets simulation:
1. Set CV SYNC to 1/1 for accurate timing
2. CV1 tracks downward movement (gravity)
3. CV2 outputs impacts (bottom edge hits)
4. CV3 shows new droplet creation
5. CV4 indicates flow direction bias
- Natural water-like rhythm patterns
- CV2 perfect for percussion triggers
- Use CV4 for stereo panning
- K1 controls droplet density

### Rule 30 Pattern Generator
Using Elementary CA Rule 30:
1. Keep STASIS on with RESET response
2. Use moderate tick rate (K2)
3. CV2 outputs current line activity
4. CV3 provides bottom row entropy
- Bottom row analysis for melody generation
- Global density on CV1 for long patterns
- Activity gate on CV4 for rhythm
- Great for generative sequences

### Brian's Brain Waves
Using Brian's Brain:
1. CV1 outputs wave complexity
2. CV2 tracks activation levels
3. CV3 provides state entropy
4. CV4 indicates pattern stability
- Perfect for complex filter modulation
- Use CV2 for VCA control
- CV3 works well with reverb mix
- Stability gate for sequence reset

### Ant Path Modulation
Using Langton's Ant:
1. CV1 outputs ant population voltage
2. CV2/CV3 give X/Y coordinates
3. CV4 ramps up over time
4. Use fast tick rate for smooth motion
- Great for stereo field control
- CV4 useful for long evolving patches
- Population changes affect intensity
- Reset for new walking patterns

### Chaotic Seeds Bursts
Using Seeds automata:
1. CV1 shows population density
2. CV2 indicates birth rate intensity
3. CV3 outputs total state change level
4. CV4 gates on high birth activity
- Perfect for burst generators
- CV2 great for envelope triggering
- CV3 excellent for effect intensity
- High activity gate for rhythmic patterns

Tips for all automata:
- Use CV SYNC ratios to control update timing
- STASIS modes can auto-reset patterns
- D IN modes add external control
- Experiment with different food values (K1)
- Adjust simulation speed with K2
- CV6 provides timing reference

These patches demonstrate different ways to use cellular automata as modulation sources. Experiment with combining different modes and CV routings to create your own unique patches.

## Adding New Automata

To create a new cellular automaton, follow these steps:

1. **Create a New File**
   - Place it in the `cellarium_docs/automata/` directory
   - Name should describe the automaton type (e.g., `my_automaton.py`)

2. **Import Required Modules**
   ```python
   from contrib.cellarium_docs.automata_base import BaseAutomata
   ```

3. **Create Your Automaton Class**
   ```python
   class MyAutomaton(BaseAutomata):
       def __init__(self, width, height, current_food_value, current_tick_limit):
           super().__init__(width, height, current_food_value, current_tick_limit)
           self.name = "My Automaton"
           # Initialize your specific variables here
   ```

4. **Implement Required Methods**
   ```python
   def simulate_generation(self, sim_current, sim_next) -> int:
       """Core simulation logic. Returns number of cells changed."""
       # Your simulation code here
       return cells_changed

   def feed_rule(self, sim_current, sim_next, food_chance, num_alive) -> int:
       """Handle food/energy input. Returns current population."""
       # Your feeding rules here
       return population_count
   ```

5. **Optional Methods**
   ```python
   def reset(self):
       """Reset the automaton state"""
       super().reset()
       # Your reset code here

   def cv1_out(self, cellarium):
       """CV1 output mapping"""
       # Your CV1 logic here

   def cv2_out(self, cellarium):
       """CV2 output mapping"""
       # Your CV2 logic here

   def cv3_out(self, cellarium):
       """CV3 output mapping"""
       # Your CV3 logic here

   def cv4_out(self, cellarium):
       """CV4 output mapping"""
       # Your CV4 logic here
   ```

### Hardware Limitations and Performance Considerations

The Raspberry Pi Pico, while powerful for its size, has some important limitations to consider:

- **Limited RAM**: Only 264KB of RAM available
  - Heap fragmentation can cause memory issues
  - Large object creation/deletion can lead to memory exhaustion
  - String operations and list comprehensions are memory-intensive

- **CPU Constraints**:
  - 133 MHz dual-core ARM Cortex-M0+
  - No hardware floating-point unit (FPU)
  - Float operations are software-emulated and slow
  - Limited instruction cache (16KB shared)

- **MicroPython Overhead**:
  - Dynamic typing adds runtime overhead
  - Garbage collection can cause timing jitter
  - Dictionary lookups are relatively expensive
  - Function calls have higher overhead than C

> **Note on Newer Pico Models**: While newer Raspberry Pi Pico models (like the Pico 2) feature hardware improvements such as increased RAM and hardware floating-point acceleration, it's recommended to develop with original Pico limitations in mind. This ensures backwards compatibility and wider module compatibility. Any optimizations made for the original Pico will still benefit newer models, and critical performance paths will remain efficient across all versions.

### General Performance Tips

The following is just a brief overview, it is advised to read the documentation here:
- https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html

1. **Function Call Optimization**
   - Minimize function calls in tight loops
   - Use inline calculations instead of helper functions
   - Cache method lookups in local variables
   - Avoid recursive functions when possible
   - Consider moving small functions inline with @micropython.viper

2. **Memory Management**
   - Pre-allocate fixed-size buffers
   - Reuse existing objects
   - Minimize string operations
   - Use bytearrays instead of lists
   - Avoid creating temporary objects in loops

3. **Computation Optimization**
   - Cache frequently used values
   - Use integer math when possible
   - Avoid floating-point operations
   - Unroll small loops
   - Use bit operations instead of arithmetic when possible

4. **Data Structures**
   - Use bytearrays for bit fields
   - Prefer simple types (int, bool)
   - Avoid dictionaries in hot paths
   - Minimize object attributes
   - Never use tuples - they're slow on the Pico

5. **Code Organization**
   - Keep critical paths short
   - Move constants outside loops
   - Use local variables over attributes
   - Batch similar operations
   - Put frequently accessed values in local scope

6. **Pico-Specific Optimizations**
   - Avoid tuple assignments (x, y = 1, 2)
   - Don't use list/dict comprehensions
   - Minimize garbage collection triggers
   - Use viper mode for array access
   - Cache attribute lookups (self.x) in local vars

7. **Loop Optimization**
   - Use while loops instead of for when possible
   - Pre-calculate loop bounds
   - Avoid range() in tight loops with viper
   - Move invariant calculations out of loops
   - Consider manual loop unrolling for small ranges

8. **Memory Layout**
   - Align data structures to word boundaries
   - Use contiguous memory blocks
   - Minimize fragmentation with pre-allocation
   - Reuse buffers instead of creating new ones
   - Clear large objects explicitly when done

### Performance Optimization with MicroPython

MicroPython provides three levels of code execution optimization:

1. **Regular Python (@micropython.native)**
   ```python
   @micropython.native
   def simple_function():
       # Faster than regular Python
       # Still has type checking
       # Good for simple methods
   ```
   - Pros:
     - Maintains Python semantics
     - Keeps type checking for safety
     - Moderate speed improvement
   - Cons:
     - Still has function call overhead
     - Limited optimization potential
     - Not suitable for tight loops
   - Documentation:
     - https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#the-native-code-emitter

2. **Viper Mode (@micropython.viper)**
   ```python
   @micropython.viper
   def fast_function():
       # Much faster execution
       # Must use type hints: int(), ptr8(), etc.
       # No Python objects allowed
   ```
   - Pros:
     - Near-C execution speed
     - Direct memory access
     - Efficient numeric operations
   - Cons:
     - Limited to simple types
     - No Python objects
     - Stricter syntax requirements
     - Harder to debug
   - Documentation:
     - https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#the-viper-code-emitter

### Bit-Parallel Processing and Bitwise Operations

Bit-parallel and byte-parallel processing are optimization techniques that leverage the binary nature of cellular automata states:

**Bit-Parallel Processing**:
- Processes multiple cells simultaneously within a single byte
- Each bit in a byte represents one cell's state (alive/dead)
- Bitwise operations affect all 8 bits (cells) at once
- Perfect for simple binary state automata like Life or Seeds
- Example: Checking 8 neighbors using shift operations

**Byte-Parallel Processing**:
- Processes entire bytes as discrete units
- Each byte can represent multiple states or properties
- More flexible for complex state tracking
- Used in automata with >2 states like Brian's Brain
- Example: Using separate bytes for different cell states

**Hybrid Approaches**:
- Combine bit and byte parallel techniques
- Use bit operations for state checks
- Use byte operations for state tracking
- Balance between flexibility and performance
- Example: Life with separate birth/death counting

Cellular automata can be optimized using bit-parallel operations in bytearrays:

> Note: Some of this is covered in software/firmware/experimental/bitarray.py, but when performance is 
> critical it can be better to inline the get and set bit operations, especially with viper decorators and
> parallel operations at the cost of increasing code duplication.

1. **Bytearray Basics**
   ```python
   # Each byte stores 8 cells
   # Integer division (//) divides and rounds down to nearest integer
   # We divide by 8 since each byte holds 8 bits/cells
   grid = bytearray((width * height) // 8)
   ```

2. **Bitwise Operations**
   ```python
   # Common operations:
   x | y    # OR: Set bits
   x & y    # AND: Test bits
   x ^ y    # XOR: Toggle bits
   ~x       # NOT: Invert bits
   x << n   # Left shift
   x >> n   # Right shift
   ```

3. **Bit Manipulation**
   ```python
   # Set a bit
   byte_idx = x >> 3     # Divide (/) by 8
   bit_pos = x & 7       # Modulo (%) 8
   bit_mask = 1 << bit_pos
   grid[byte_idx] |= bit_mask

   # Test a bit
   is_set = grid[byte_idx] & bit_mask

   # Clear a bit
   grid[byte_idx] &= ~bit_mask
   ```

### Example CV Mapping Ideas

- Map living cell count to voltage
- Convert pattern density to CV
- Output pulses on specific pattern formations
- Generate gates from state transitions
- Create rhythmic patterns from cell births/deaths

## Example Implementation

Here's a minimal example of a new automaton:

```python
from contrib.cellarium_docs.automata_base import BaseAutomata

class SimpleAutomaton(BaseAutomata):
    def __init__(self, width, height, current_food_value, current_tick_limit):
        super().__init__(width, height, current_food_value, current_tick_limit)
        self.name = "Simple"
        self.population = 0

    @micropython.viper
    def simulate_generation(self, sim_current, sim_next) -> int:
        w = int(self.width)
        h = int(self.height)
        changes = int(0)
        
        # Simple alternating pattern
        for y in range(h):
            for x in range(w):
                byte_idx = int(x >> 3)
                bit_pos = int(x & 7)
                bit_mask = int(1 << bit_pos)
                grid_idx = int(y * self.bytes_per_row + byte_idx)
                
                # Flip state each generation
                if sim_current[grid_idx] & bit_mask:
                    changes += 1
                else:
                    sim_next[grid_idx] |= bit_mask
                    changes += 1
                    
        return changes

    @micropython.native
    def feed_rule(self, sim_current, sim_next, food_chance, num_alive) -> int:
        self.population = num_alive
        return num_alive

    @micropython.native
    def cv1_out(self, cellarium):
        # Output population as voltage
        voltage = (self.population / (self.width * self.height)) * 10
        cv1.voltage(voltage)
```

This example creates a simple automaton that alternates cell states and outputs the population ratio as CV1 voltage.

## Additional Resources

- See existing automata implementations in `cellarium_docs/automata/` for more examples
- Read `automata_base.py` for detailed documentation of the base class
- Check the EuroPi documentation for CV/Gate handling details
