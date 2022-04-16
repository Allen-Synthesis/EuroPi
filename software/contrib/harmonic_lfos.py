from europi import *
from math import cos, radians
from random import randint
from time import sleep_ms
from machine import freq
from europi_script import EuroPiScript

MAX_VOLTAGE = MAX_OUTPUT_VOLTAGE #Default is inherited but this can be overriden by replacing "MAX_OUTPUT_VOLTAGE" with an integer
MAX_HARMONIC = 32 #Too high a value may be hard to select using the knob, but the actual hardware limit is only reached at 4096

class HarmonicLFOs(EuroPiScript):
    def __init__(self):
        super().__init__()
        
        #Retreive saved state information from file
        state = self.load_state_json()
        
        #Overclock the Pico for improved performance
        freq(250_000_000)
        
        #Use the saved values for the LFO divisions and mode if found in the save state file, using defaults if not
        self.divisions = state.get("divisions", [1, 3, 5, 7, 11, 13])
        self.mode = state.get("mode", 0)
        
        #Initialise all the other variables
        self.degree = 0
        self.delay, self.increment_value = self.get_delay_increment_value()
        self.pixel_x = OLED_WIDTH-1
        self.pixel_y = OLED_HEIGHT-1
        self.selected_lfo = 0
        self.selected_lfo_start_value = self.get_clock_division()
        
        #Set the digital input and button handlers
        din.handler(self.reset)
        b1.handler(self.change_mode)
        b2.handler(self.increment_selection)

    def get_clock_division(self):
        """Determine the new clock division based on the position of knob 2"""
        return k2.read_position(MAX_HARMONIC) + 1

    def reset(self):
        """Reset all LFOs to zero volts, maintaining their divisions"""
        self.degree = 0

    def change_mode(self):
        """Change the mode that controls wave shape"""
        self.mode += 1
        
        if self.mode == 3:
            self.mode = 0
            
        self.save_state()

    def get_delay_increment_value(self):
        """Calculate the wait time between degrees"""
        delay = (0.1 - (k1.read_position(100, 1)/1000)) + (ain.read_voltage(1)/100)
        return delay, round((((1/delay)-10)/1)+1)

    def increment_selection(self):
        """Move the selection to the next LFO"""
        self.selected_lfo += 1
        if self.selected_lfo == 6:
            self.selected_lfo = 0
        self.selected_lfo_start_value = self.get_clock_division()

    def save_state(self):
        """Save the current set of divisions to file"""
        if self.last_saved() < 5000:
            return
        
        state = {
            "divisions": self.divisions,
            "mode": self.mode
        }
        self.save_state_json(state)
        
    def update_display(self):
        """Update the OLED display every 10 cycles (degrees)"""
        oled.scroll(-1,0)
        if round(self.degree, -1) % 10 == 0:
            oled.show()
            
    def increment(self):
        """Increment the current degree and determine new values of delay and increment_value"""
        self.degree += self.increment_value
        self.delay, self.increment_value = self.get_delay_increment_value()
        sleep_ms(int(self.delay))
        
    def display_selected_lfo(self):
        """Draw the current LFO's number and division to the OLED display"""
        oled.fill_rect(0,0,20,32,0)
        oled.fill_rect(0,0,20,9,1)
        oled.text(str(self.selected_lfo+1),6,1,0)
        
        number = self.divisions[self.selected_lfo]
        x = 2 if number >= 10 else 6
        oled.text(str(number),x,20,1)
        
    def calculate_voltage(self, multiplier):
        """Determine the voltage based on current degree, wave shape, and MAX_VOLTAGE"""
        three_sixty = 360*multiplier
        degree_three_sixty = self.degree % three_sixty
        if self.mode == 0: #Sin
            voltage = ((0-(cos(self.rad*(1/multiplier)))+1)) * (MAX_VOLTAGE/2)
        elif self.mode == 1: #Saw
            voltage = (degree_three_sixty / (three_sixty)) * MAX_VOLTAGE
        elif self.mode == 2: #Square
            voltage = MAX_VOLTAGE * (int((degree_three_sixty / (three_sixty)) * MAX_VOLTAGE) < (MAX_VOLTAGE/2))
        return voltage
        
    def display_graphic_lines(self):
        """Draw the lines displaying each LFO's voltage to the OLED display"""
        self.rad = radians(self.degree)
        oled.vline(self.pixel_x,0,OLED_HEIGHT,0)
        for cv, multiplier in zip(cvs, self.divisions):
            volts = self.calculate_voltage(multiplier)
            cv.voltage(volts)
            oled.pixel(self.pixel_x,self.pixel_y-int(volts*(self.pixel_y/10)),1)

    def check_change_clock_division(self):
        """Change current LFO's division with knob movement detection"""
        self.clock_division = self.get_clock_division()
        if self.clock_division != self.selected_lfo_start_value:
            self.selected_lfo_start_value, self.divisions[self.selected_lfo] = self.clock_division, self.clock_division
            self.save_state()
        

    def main(self):
        while True:
            self.check_change_clock_division()
            
            self.display_graphic_lines()
            
            self.display_selected_lfo()
            
            self.update_display()
            
            self.increment()


if __name__ == "__main__":
    HarmonicLFOs().main()
