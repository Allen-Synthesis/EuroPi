## Sequential switch for the EuroPi
#
#  \author Chris Iverach-Brereton <ve4cib@gmail.com>
#  \date   2023-02-13

from europi import *
from europi_script import EuroPiScript
import time
import random

## Whe in triggered mode we only quantize when we receive an external clock signal
MODE_SEQUENTIAL=0

## In continuous mode the digital input is ignored and we quantize the input
#  at the highest rate possible
MODE_RANDOM=1

## How many milliseconds of idleness do we need before we trigger the screensaver?
#
#  =20 minutes
SCREENSAVER_TIMEOUT_MS = 1000 * 60 * 20

## Convert a number in one range to another
#
#  \param x        The value to convert
#  \param old_min  The old minimum value for x
#  \param old_max  The old maximum value for x
#  \param new_min  The new minimum value for x
#  \param new_max  The new maximum value for x
#  \param clip     If true, output is always between max and min. Otherwise it's extrapolated
#
#  \return x, linearly shifted to lie on the new scale
def linear_rescale(x, old_min, old_max, new_min, new_max, clip=True):
    if x < old_min and clip:
        return new_min
    elif x > old_max and clip:
        return new_max
    else:
        return (x-old_min) / (old_max-old_min) * (new_max - new_min) + new_min

## Wrapper for linear_rescale specifically for scaling knob values
#
#  \param knob  Either europi.k1 or europi.k2; the knob whose value we'll read and rescale
#  \param new_min  The new minimum value for x
#  \param new_max  The new maximum value for x
#
#  \return The knob's current position, linearly rescaled to lie between new_min and new_max
def knob_rescale(knob, new_min, new_max):
    return linear_rescale(knob.read_position(), 0, 100, new_min, new_max, True)
    

## Blank the screen when idle
#
#  Eventually it might be neat to have an animation, but that's
#  not necessary for now
class ScreensaverScreen:
    def __init__(self, parent):
        self.parent = parent
        
    def on_button1(self):
        self.parent.active_screen = self.parent.switch_screen
        self.parent.on_trigger()
    
    def draw(self):
        oled.fill(0)
        oled.show()

## Default display: shows what output is currently active
class SwitchScreen:
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

## Advanced menu options screen
class MenuScreen:
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

## Used by MenuScreen to choose the number of outputs
class NumOutsChooser:
    def __init__(self, parent):
        self.parent = parent
        
    def read_knob(self):
        num_outs = round(knob_rescale(k2, 2, 6)) # 2-6 outputs; 1 output would be useless!
        return num_outs
        
    def on_button1(self):
        num_outs = self.read_knob()
        self.parent.num_outputs = num_outs
        self.parent.current_output = self.parent.current_output % num_outs
        self.parent.save()
        
    def draw(self):
        num_outs = self.read_knob()
        oled.fill(0)
        oled.text(f"-- # Outputs --", 0, 0)
        oled.text(f"{self.parent.num_outputs} <- {num_outs}", 0, 10)
        oled.show()
    
## Used by MenuScreen to choose the operating mode
class ModeChooser:
    def __init__(self, parent):
        self.parent = parent
        
        self.mode_names = [
            "Seq.",
            "Rand."
        ]
        
    def read_knob(self):
        new_mode = round(knob_rescale(k2, 0, len(self.mode_names)-1))
        return new_mode
        
    def on_button1(self):
        new_mode = self.read_knob()
        self.parent.mode = new_mode
        self.parent.save()
        
    def draw(self):
        new_mode = self.read_knob()
        oled.fill(0)
        oled.text(f"-- Mode --", 0, 0)
        oled.text(f"{self.mode_names[self.parent.mode]} <- {self.mode_names[new_mode]}", 0, 10)
        oled.show()

## The main workhorse of the whole module
#
#  Copies the analog input to one of the 6 outputs, cycling which output
#  whenever a trigger is received
class SequentialSwitch(EuroPiScript):
    def __init__(self):
        super().__init__()
        
        # keep track of the last time the user interacted with the module
        # if we're idle for too long, start the screensaver
        self.last_interaction_time = time.ticks_ms()
        
        # Continious quantizing, or only on an external trigger?
        self.mode = MODE_SEQUENTIAL
        
        # Use all 6 outputs by default
        self.num_outputs = 6
        
        # The index of the current outputs
        self.current_output = 0
        
        # The outputs as an array for convenience
        self.outputs = [cv1, cv2, cv3, cv4, cv5, cv6]
        
        # GUI/user interaction
        self.switch_screen = SwitchScreen(self)
        self.menu_screen = MenuScreen(self)
        self.screensaver = ScreensaverScreen(self)
        self.active_screen = self.switch_screen
        
        self.highlight_note = 0         # the note on the keyboard view we can toggle now
        self.menu_item = 0              # the active item from the advanced menu
        
        self.load()
        
    ## Load the persistent settings from storage and apply them
    def load(self):
        state = self.load_state_json()
        
        self.mode = state.get("mode", self.mode)
        self.num_outputs = state.get("num_outputs", self.num_outputs)
    
    ## Save the current settings to persistent storage
    def save(self):
        state = {
            "mode": self.mode,
            "num_outputs": self.num_outputs
        }
        self.save_state_json(state)
        
    @classmethod
    def display_name(cls):
        return "Seq. Switch"
    
    ## Handler for the rising edge of the input clock
    def on_trigger(self):
        if self.mode == MODE_SEQUENTIAL:
            self.current_output = (self.current_output + 1) % self.num_outputs
        else:
            self.current_output = random.randint(0, self.num_outputs-1)
            
    ## Handler for pressing button 1
    #
    #  Button 1 is used for the main interaction and is passed to
    #  the current display for user interaction
    def on_button1(self):
        self.last_interaction_time = time.ticks_ms()
        self.active_screen.on_button1()
        
    ## Handler for pressing button 2
    #
    #  Button 2 is used to cycle between screens
    def on_button2(self):
        self.last_interaction_time = time.ticks_ms()
        
        if self.active_screen == self.switch_screen:
            self.active_screen = self.menu_screen
        else:
            self.active_screen = self.switch_screen
    
    ## The main loop
    #
    #  Connects event handlers for clock-in and button presses
    #  and runs the main loop
    def main(self):
        @din.handler
        def on_rising_clock():
            self.on_trigger()
            
        @b1.handler
        def on_b1_press():
            self.on_button1()
            
        @b2.handler
        def on_b2_press():
            self.on_button2()
        
        while True:
            input_volts = ain.read_voltage()
            
            self.menu_item = round(knob_rescale(k1, 0, len(self.menu_screen.menu_items)-1))
            
            for i in range(len(self.outputs)):
                if i == self.current_output:
                    self.outputs[i].voltage(input_volts)
                else:
                    self.outputs[i].voltage(0)
            
            self.active_screen.draw()
    
if __name__ == "__main__":
    SequentialSwitch().main()
