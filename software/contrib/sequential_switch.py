"""Sequential switch for the EuroPi

    @author Chris Iverach-Brereton <ve4cib@gmail.com>
    @date   2023-02-13
"""

from europi import *
from europi_script import EuroPiScript
import time
import random

## Move in order 1>2>3>4>5>6>1>2>...
MODE_SEQUENTIAL=0

## Move in order 1>6>5>4>3>2>1>6>...
MODE_REVERSE=1

## Move in order 1>2>3>4>5>6>5>4>...
MODE_PINGPONG=2

## Pick a random output, which can be the same as the one we're currently using
MODE_RANDOM=3

## How many milliseconds of idleness do we need before we trigger the screensaver?
#
#  =20 minutes
SCREENSAVER_TIMEOUT_MS = 1000 * 60 * 20

class ScreensaverScreen:
    """Blank the screen when idle
    Eventually it might be neat to have an animation, but that's
    not necessary for now
    """
    
    def __init__(self, parent):
        self.parent = parent
        
    def on_button1(self):
        self.parent.active_screen = self.parent.switch_screen
        self.parent.on_trigger()
    
    def draw(self):
        oled.fill(0)
        oled.show()

class SwitchScreen:
    """Default display: shows what output is currently active
    """
    
    def __init__(self, parent):
        self.parent = parent
        
    def on_button1(self):
        # the button can be used to advance the output
        self.parent.on_trigger()
        
    def draw(self):
        oled.fill(0)
        
        # Show all 6 outputs as a string on 2 lines to mirror the panel
        switches = ""
        for i in range(2):
            for j in range(3):
                out_no = i*3 + j
                if out_no < self.parent.num_outputs:
                    # output is enabled; is it hot?
                    if self.parent.current_output == out_no:
                        switches = switches + " [*] "
                    else:
                        switches = switches + " [ ] "
                else:
                    # output is disabled; mark it with .
                    switches = switches + "  .  "
                    
            switches = switches + "\n"
        
        oled.centre_text(switches)
        
        oled.show()

class MenuScreen:
    """Advanced menu options screen
    """
    def __init__(self, parent):
        self.parent = parent
        
        self.menu_items = [
            NumOutsChooser(parent),
            ModeChooser(parent)
        ]
        
    def draw(self):
        self.menu_items[self.parent.menu_item].draw()
        
    def on_button1(self):
        self.menu_items[self.parent.menu_item].on_button1()

class NumOutsChooser:
    """Used by MenuScreen to choose the number of outputs
    """
    
    def __init__(self, parent):
        self.parent = parent
        
    def read_num_outs(self):
        return k2.range(5) + 2 # result should be 2-6
        
    def on_button1(self):
        num_outs = self.read_num_outs()
        self.parent.num_outputs = num_outs
        self.parent.current_output = self.parent.current_output % num_outs
        self.parent.save()
        
    def draw(self):
        num_outs = self.read_num_outs()
        oled.fill(0)
        oled.text(f"-- # Outputs --", 0, 0)
        oled.text(f"{self.parent.num_outputs} <- {num_outs}", 0, 10)
        oled.show()
    
class ModeChooser:
    """Used by MenuScreen to choose the operating mode
    """
    def __init__(self, parent):
        self.parent = parent
        
        self.mode_names = [
            "Seq.",
            "Rev.",
            "P-P",
            "Rand."
        ]
        
    def read_mode(self):
        return k2.range(len(self.mode_names))
        
    def on_button1(self):
        new_mode = self.read_mode()
        self.parent.mode = new_mode
        self.parent.save()
        
    def draw(self):
        new_mode = self.read_mode()
        oled.fill(0)
        oled.text(f"-- Mode --", 0, 0)
        oled.text(f"{self.mode_names[self.parent.mode]} <- {self.mode_names[new_mode]}", 0, 10)
        oled.show()

class SequentialSwitch(EuroPiScript):
    """The main workhorse of the whole module

    Copies the analog input to one of the 6 outputs, cycling which output
    whenever a trigger is received
    """
    
    def __init__(self):
        super().__init__()
        
        # keep track of the last time the user interacted with the module
        # if we're idle for too long, start the screensaver
        self.last_interaction_time = time.ticks_ms()
        
        # How do we advance the output?
        self.mode = MODE_SEQUENTIAL
        
        # Use all 6 outputs by default
        self.num_outputs = 6
        
        # The index of the current outputs
        self.current_output = 0
        
        # For MODE_PINGPONG, this indicates the direction of travel
        # it will always be +1 or -1
        self.direction = 1
        
        # GUI/user interaction
        self.switch_screen = SwitchScreen(self)
        self.menu_screen = MenuScreen(self)
        self.screensaver = ScreensaverScreen(self)
        self.active_screen = self.switch_screen
        
        self.menu_item = 0              # the active item from the advanced menu
        
        self.load()
       
    def load(self):
        """Load the persistent settings from storage and apply them
        """
        state = self.load_state_json()
        
        self.mode = state.get("mode", self.mode)
        self.num_outputs = state.get("num_outputs", self.num_outputs)
    
    def save(self):
        """Save the current settings to persistent storage
        """
        state = {
            "mode": self.mode,
            "num_outputs": self.num_outputs
        }
        self.save_state_json(state)
        
    @classmethod
    def display_name(cls):
        return "Seq. Switch"
    
    def on_trigger(self):
        """Handler for the rising edge of the input clock

        Also used for manually advancing the output on a button press
        """
        # to save on clock cycles, don't use modular arithmetic
        # instead just to integer math and handle roll-over manually
        next_out = self.current_output
        if self.mode == MODE_SEQUENTIAL:
            next_out = next_out + 1
        elif self.mode == MODE_REVERSE:
            next_out = next_out - 1
        elif self.mode == MODE_PINGPONG:
            next_out = next_out + self.direction
        else:
            next_out = random.randint(0, self.num_outputs-1)
            
        if next_out < 0:
            if self.mode == MODE_REVERSE:
                next_out = self.num_outputs-1
            else:
                next_out = -next_out
                self.direction = -self.direction
        elif next_out >= self.num_outputs:
            if self.mode == MODE_SEQUENTIAL:
                next_out = 0
            else:
                next_out = self.num_outputs-2
                self.direction = -self.direction
                
        self.current_output = next_out
    
    def main(self):
        """The main loop

        Connects event handlers for clock-in and button presses
        and runs the main loop
        """
        
        @din.handler
        def on_rising_clock():
            self.on_trigger()
            
        @b1.handler
        def on_b1_press():
            self.last_interaction_time = time.ticks_ms()
            self.active_screen.on_button1()
            
        @b2.handler
        def on_b2_press():
            self.last_interaction_time = time.ticks_ms()
        
            if self.active_screen == self.switch_screen:
                self.active_screen = self.menu_screen
            else:
                self.active_screen = self.switch_screen
            
        while True:
            # keep the menu items sync'd with the left knob
            self.menu_item = k1.range(len(self.menu_screen.menu_items))
            
            # check if we've been idle for too long; if so, blank the screen
            # to prevent burn-in
            now = time.ticks_ms()
            if time.ticks_diff(now, self.last_interaction_time) > SCREENSAVER_TIMEOUT_MS:
                self.active_screen = self.screensaver
            
            # read the input and send it to the current output
            # all other outputs should be zero
            input_volts = ain.read_voltage()
            for i in range(len(cvs)):
                if i == self.current_output:
                    cvs[i].voltage(input_volts)
                else:
                    cvs[i].voltage(0)
            
            self.active_screen.draw()
    
if __name__ == "__main__":
    SequentialSwitch().main()
