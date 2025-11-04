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

"""Main application script for Cellarium cellular automaton environment.

cell (plural cells), Noun
    1. The basic unit of a living organism
    2. The minimal unit of a cellular automaton that can change state 

-arium (plural -ariums or -aria), Suffix
    1. A place associated with a specified thing.
    2. A device associated with a specified function.

Cellarium, Noun
    1. A place for observing cellular automata simulations, such as Life.

Provides a multi-threaded environment for running, displaying, and controlling 
cellular automata simulations on EuroPi hardware. 
Features:
- Multi-threaded: A thread for simulation and an asynchronous thread for display
- Real-time parameter control via knobs and buttons
- Settings display overlay, showing current mode and parameters
- Automaton hot-swapping
    - Stasis detection and response, configurable per automaton
    - Automata-defined CV input/output integration
        - CV5 reserved for stasis indication
        - CV6 reserved for simulation duration gate (clock)

Lables:
- Externally Clockable
- Clock Source
- Clock Divider
- LFO
- Envelope Generator
- Random
- CV Generation
- CV Modulation
- And possibly more to observe within the Cellarium...

Controls:
- B1: Cycle through B2 modes
- B2: Adjust current active mode settings.
- K1: Food value (value used by automata for population growth)
- K2: Tick rate limiter (simulation speed)
- DIN: Control reset, feed, or clocking based on mode
- AIN: Modulate food or tick rate
- CV1-4 Out: Automaton-specific outputs
- CV5 Out: Stasis indication (on when in stasis)
- CV6 Out: Simulation duration gate (simulation tick as clock source)

@author Grybbit (https://github.com/Bearwynn)
@year 2025
"""

# EuroPi core imports
from europi import *
from europi_script import EuroPiScript

# Standard library imports
from random import randint
from framebuf import MONO_HMSB
import gc
import math
import micropython
import _thread
from utime import ticks_ms, ticks_diff, sleep_ms
from ucollections import OrderedDict

# Local imports
from contrib.cellarium_docs.automata_registry import get_automata_by_index, get_automata_names

# Display constants
W = OLED_WIDTH
H = OLED_HEIGHT
BUF_LEN = (W * H) // 8
MIN_TICK_LIMIT = 0 #milliseconds
MAX_TICK_LIMIT = 500 #milliseconds
SETTING_DISPLAY_TIME = 4000
MAX_POP_DELTA = 24
MIN_FOOD_VALUE = 0
MAX_FOOD_VALUE = 100

class Cellarium(EuroPiScript):
    MODES_B2 = OrderedDict(((n, i) for i, n in enumerate(('RESET','FEED','CLOCK','AUTOMATA','D IN','A IN','CV SYNC','STASIS'))))
    MODES_DIN = OrderedDict(((n, i) for i, n in enumerate(('OFF','RESET','FEED','CLOCK'))))
    MODES_AIN = OrderedDict(((n, i) for i, n in enumerate(('OFF','FEED','TICK'))))
    MODES_CVRATIO = OrderedDict(((n, v) for n, v in (('1/1',1),('1/2',2),('1/4',4),('1/8',8),('1/16',16))))
    MODES_STASIS = OrderedDict(((n, i) for i, n in enumerate(('FEED','RESET','OFF'))))

    def __init__(self):
        self.width = W
        self.height = H
        # Buffers
        self.sim_current = bytearray(BUF_LEN)
        self.sim_next = bytearray(BUF_LEN)
        self.sim_frame = FrameBuffer(self.sim_current, W, H, MONO_HMSB)
        self.sim_next_frame = FrameBuffer(self.sim_next, W, H, MONO_HMSB)
        self._buf_lock = _thread.allocate_lock()
        self._display_ready = True
        self._display_request = False
        # State
        self.num_alive = 0
        self.num_born = 0
        self.num_died = 0
        self.pop_deltas = []
        self.reset_req = False
        self.feed_req = False
        self.food_value = MAX_FOOD_VALUE // 2
        self.b2_idx = 0
        self.din_idx = 0
        self.ain_idx = 0  
        self.cv_idx = 0
        self.stasis_idx = 0
        self._show_settings_req = False
        self.settings_display_start = 0
        self._settings_lock = _thread.allocate_lock()
        # Timing
        self.cv_update_req = True
        self.tick_req = False
        self.tick_limit = MIN_TICK_LIMIT
        now = ticks_ms()
        self._last_tick = now
        self._last_display = now
        self._display_thread_started = False
        # automata support
        self.automata_names = get_automata_names()
        self.automata_idx = 0
        self.current_automata = get_automata_by_index(self.automata_idx)(W, H, self.food_value, self.tick_limit)
        # INIT
        turn_off_all_cvs()
        oled.fill(0)
        oled.show()
        
        @b1.handler
        def on_b1():
            self.b2_idx = (self.b2_idx + 1) % len(self.MODES_B2)
            with self._settings_lock:
                self._show_settings_req = True
                self.settings_display_start = ticks_ms()
            
        @b2.handler
        def on_b2():
            show_settings = False
            b2_mode = list(self.MODES_B2.keys())[self.b2_idx]
            if b2_mode == 'D IN':
                self.din_idx = (self.din_idx + 1) % len(self.MODES_DIN)
                mode = list(self.MODES_DIN.keys())[self.din_idx]
                show_settings = True
            elif b2_mode == 'A IN':
                self.ain_idx = (self.ain_idx + 1) % len(self.MODES_AIN)
                mode = list(self.MODES_AIN.keys())[self.ain_idx]
                show_settings = True
            elif b2_mode == 'CV SYNC':
                self.cv_idx = (self.cv_idx + 1) % len(self.MODES_CVRATIO)
                mode = list(self.MODES_CVRATIO.keys())[self.cv_idx]
                show_settings = True
            elif b2_mode == 'STASIS':
                self.stasis_idx = (self.stasis_idx + 1) % len(self.MODES_STASIS)
                mode = list(self.MODES_STASIS.keys())[self.stasis_idx]
                show_settings = True
            elif b2_mode == 'AUTOMATA':
                self.automata_idx = (self.automata_idx + 1) % len(self.automata_names)
                with self._buf_lock:
                    gc.collect()
                    #create new automata
                    new_automata = get_automata_by_index(self.automata_idx)(W, H, self.food_value, self.tick_limit)
                    self.current_automata = new_automata
                # Reset all simulation data when switching automata
                self.reset()
                mode = self.automata_names[self.automata_idx]
                show_settings = True
            elif b2_mode == 'RESET':
                self.reset_req = True
            elif b2_mode == 'FEED':
                self.feed_req = True
            elif b2_mode == 'CLOCK':
                self.tick_req = True
                
            if show_settings:
                with self._settings_lock:
                    self._show_settings_req = True
                    self.settings_display_start = ticks_ms()

        @din.handler
        def on_din():
            din_mode = list(self.MODES_DIN.keys())[self.din_idx]
            if din_mode == 'RESET':
                self.reset()
            elif din_mode == 'FEED':
                self.feed_grid()
            elif din_mode == 'CLOCK':
                self.tick_req = True

    @micropython.native
    def main(self):
        """Main entry point for the Cellarium application.
        
        Initializes the environment:
        - Turns off all CV outputs
        - Updates initial input states
        - Resets simulation state
        - Starts the asynchronous display thread
        - Launches simulation thread
        """
        turn_off_all_cvs()
        self.update_inputs()
        self.reset()
        #Start ASYNC display thread
        if not self._display_thread_started:
            self._display_thread_started = True
            _thread.start_new_thread(self._display_thread, ())
        #Start simulation thread
        self._simulation_thread()
    
    @micropython.native
    def update_inputs(self):
        """Process and update input states from knobs and analog input.
        
        Handles:
        - K1/K2 knob values with easing functions
        - Analog input modulation
        - Food value and tick limit calculations
        - Input mode-specific adjustments
        """
        # Inline easeInCubic calculation
        k1_percent = k1.percent()
        easedIn_k1_value = k1_percent * k1_percent * k1_percent
        #easedIn_k1_value = k1_percent
        
        # Inline easeOutCubic calculation
        k2_percent = k2.percent()
        k2_ease = k2_percent - 1
        easedOut_k2_value = (k2_ease * k2_ease * k2_ease + 1)

        food_value = int(MAX_FOOD_VALUE * easedIn_k1_value)
        tick_limit = int(MAX_TICK_LIMIT * (1.0 - easedOut_k2_value) )# 1.0 - easedOut_k2_value inverts the percentage so right turn is faster sim

        #adjust by analogue in
        cv_knob_adjustment_value = (ain.percent() - 0.5) # offset to -0.5 to +0.5, so that values below 50% decrease and above 50% increase
        if self.ain_idx == self.MODES_AIN['FEED']:
                food_value = food_value + (MAX_FOOD_VALUE * cv_knob_adjustment_value)
        elif self.ain_idx == self.MODES_AIN['TICK']:
                tick_limit = tick_limit - (MAX_TICK_LIMIT * cv_knob_adjustment_value)
        
        self.food_value = max(MIN_FOOD_VALUE, min(MAX_FOOD_VALUE, food_value))
        self.tick_limit = max(MIN_TICK_LIMIT, min(MAX_TICK_LIMIT, tick_limit))

    # ----- Simulation Thread Functions ------
    @micropython.native
    def _simulation_thread(self):
        """Main simulation thread that handles automata state updates and output generation.
        
        Manages:
        - Input processing and updates
        - Simulation timing and clock modes
        - CV update scheduling
        - Stasis detection and response
        - Buffer swapping and display updates
        - CV output generation
        """
        update_cv_counter = 0
        while True:
            now = ticks_ms()
            self.update_inputs()
            automata = self.current_automata
            automata.update_input_data(self.food_value, self.tick_limit)
            
            should_tick = False
            if self.din_idx == self.MODES_DIN['CLOCK'] or self.b2_idx == self.MODES_B2['CLOCK']:
                should_tick = True if self.tick_req else False
            else:
                should_tick = ticks_diff(now, self._last_tick) >= self.tick_limit
                
            cv_update_division = list(self.MODES_CVRATIO.values())[self.cv_idx]
            if update_cv_counter >= cv_update_division or cv_update_division == 1:
                self.cv_update_req = True
                update_cv_counter = 0
                
            if should_tick:
                self._last_tick = now
                self.tick_req = False
                update_cv_counter +=1
                
                if self.stasis_check():
                    if self.cv_update_req:
                        cv5.on()
                    if self.stasis_idx == self.MODES_STASIS['FEED']:
                        self.feed_req = True
                    elif self.stasis_idx == self.MODES_STASIS['RESET']:
                        self.reset_req = True
                else:
                    if self.cv_update_req:
                        cv5.off()
                               
                if self.reset_req:
                    self.reset()
                    self.reset_req = False
                    self.feed_req = False
                if self.feed_req:
                    self.feed_grid()
                    self.feed_req = False
                
                if self.cv_update_req:
                    cv6.on()
                with self._buf_lock:
                    # Get simulation metrics
                packed = int(automata.simulate_generation(self.sim_current, self.sim_next))
                if self.cv_update_req:
                    cv6.off()
                
                # Retrieve metrics from simulation - split for MicroPython
                self.num_born = packed & 0xffff
                self.num_died = (packed >> 16) & 0xffff
                born_died_diff = self.num_born - self.num_died
                self.num_alive = self.num_alive + born_died_diff

                # Atomic swap under lock
                with self._buf_lock:
                    # Swap simulation buffers
                    temp_sim = self.sim_current
                    self.sim_current = self.sim_next
                    self.sim_next = temp_sim
                    
                    # Swap frame buffers
                    temp_frame = self.sim_frame
                    self.sim_frame = self.sim_next_frame
                    self.sim_next_frame = temp_frame
                    
                    self._display_request = True
                
                if self.cv_update_req:
                    # Use automata-specific CV outputs
                    automata.cv1_out(self)
                    automata.cv2_out(self)
                    automata.cv3_out(self)
                    automata.cv4_out(self)
                    
                    self.cv_update_req = False
        
    @micropython.native
    def feed_grid(self):
        """Feed the simulation grid with new cells.
        
        Uses automaton's feed rule to:
        - Add new live cells based on food value
        - Update population counts
        - Handle grid feeding mechanics
        """
        fc = self.food_value
        if fc <= 0:
            self.feed_req = False
            return
        with self._buf_lock:
            self.num_alive = self.current_automata.feed_rule(self.sim_current, self.sim_next, fc, self.num_alive)
        self.feed_req = False
    
    @micropython.native
    def reset(self):
        """Reset the simulation state.
        
        - Clears simulation buffers
        - Resets population counters
        - Cleans up automata state
        - Refeeds the grid if needed
        """
        with self._buf_lock:
            #clear simulation buffers
            sim_current = self.sim_current
            sim_next = self.sim_next
            for i in range(BUF_LEN):
                sim_current[i] = 0
                sim_next[i] = 0
            self.num_alive = 0
            self.pop_deltas.clear()
                # Reset current automata safely
            if hasattr(self, 'current_automata') and self.current_automata is not None:
                try:
                    self.current_automata.reset()
                except Exception as e:
                    #if automata reset fails, just continue. The buffers are cleared
                    pass
        self.feed_grid()

    # ----- Analysis ------
    @micropython.native
    def stasis_check(self):
        """Check if simulation has reached a stable state.
        
        - Tracks population changes over time
        - Maintains history of birth/death deltas
        - Delegates to automaton's stasis rule
        - Used for stasis detection and response
        
        Returns:
            bool: True if simulation is in stasis, False otherwise
        """
        # Calculate and store population delta
        population_delta = self.num_born - self.num_died
        self.pop_deltas.append(population_delta)
        pop_delta_count = len(self.pop_deltas)
        if pop_delta_count > MAX_POP_DELTA:
            self.pop_deltas.pop(0)
        # Delegate to current automaton's stasis rule with num_alive
        with self._buf_lock: 
            return self.current_automata.stasis_rule(MAX_POP_DELTA, self.pop_deltas, self.num_born, self.num_died, self.num_alive)
        return False
 
    # ----- Display Pipeline -----
    @micropython.native
    def draw_settings(self):
        """Draw the current settings on the OLED display.
        
        Displays:
        - DIN mode status
        - Analog input mode
        - B2 button mode and associated settings
        - Current automaton name
        - CV sync ratio or stasis settings when active
        
        Uses text overlays at top and bottom of screen.
        """
        # Get current mode names
        din_mode = list(self.MODES_DIN.keys())[self.din_idx]
        ain_mode = list(self.MODES_AIN.keys())[self.ain_idx]
        b2_mode = list(self.MODES_B2.keys())[self.b2_idx]
        oled.fill_rect(0,0,len(din_mode)*8+16,8,0)
        oled.text(f"D:{din_mode}",0,0,1)
        ain_text = f"A:{ain_mode}"
        aw = len(ain_text)*8
        oled.fill_rect(W-aw,0,aw,8,0)
        oled.text(ain_text, W-aw,0,1)
        if b2_mode == 'CV SYNC':
            cv_ratio = list(self.MODES_CVRATIO.keys())[self.cv_idx]
            b2_text = "B2:CV:"+cv_ratio
        elif b2_mode == 'STASIS':
            stasis = list(self.MODES_STASIS.keys())[self.stasis_idx]
            b2_text = "STASIS:"+stasis
        elif b2_mode == 'AUTOMATA':
            automata_name = self.current_automata.name
            b2_text = automata_name
        else:
            b2_text = "B2:"+b2_mode
        bw = len(b2_text)*8
        oled.fill_rect(W-bw, H-8, bw,8,0)
        oled.text(b2_text, W-bw, H-8,1)

    @micropython.native
    def _display_thread(self):
        """Asynchronous display update thread.
        
        Handles:
        - Display buffer swapping
        - Settings overlay drawing
        - OLED screen updates
        - Display request processing
        - Settings timeout management
        
        Runs continuously in background thread.
        """
        while True:
            if self._display_ready:
                show = False
                if self._display_request:
                    with self._buf_lock:
                        oled.blit(self.sim_frame, 0, 0)
                        self._display_request = False
                        show = True
                if self._show_settings_req:
                    with self._buf_lock:
                        self.draw_settings()
                        show = True
                    if ticks_diff(ticks_ms(), self.settings_display_start) >= SETTING_DISPLAY_TIME:
                        self._show_settings_req = False
                if show:
                    oled.show()
            sleep_ms(0)

if __name__ == "__main__":
    Cellarium().main()