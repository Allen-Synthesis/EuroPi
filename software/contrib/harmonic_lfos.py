from europi import *
from math import cos, radians
from time import sleep_ms
from machine import freq
from random import randint
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
        self.modes = state.get("modes", [0, 0, 0, 0, 0, 0])
        self.MODE_COUNT = 5
        
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
        self.modes[self.selected_lfo] = (self.modes[self.selected_lfo] + 1) % self.MODE_COUNT
        self.save_state()

    def get_delay_increment_value(self):
        """Calculate the wait time between degrees"""
        delay = (0.1 - (k1.read_position(100, 1)/1000)) + (ain.read_voltage(1)/100)
        return delay, round((((1/delay)-10)/1)+1)

    def increment_selection(self):
        """Move the selection to the next LFO"""
        self.selected_lfo = (self.selected_lfo + 1) % 6
        self.selected_lfo_start_value = self.get_clock_division()

    def save_state(self):
        """Save the current set of divisions to file"""
        if self.last_saved() < 5000:
            return
        
        state = {
            "divisions": self.divisions,
            "modes": self.modes
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
        
    def draw_wave(self):
        shape = self.modes[self.selected_lfo]
        if shape == 0: #Sine
            oled.pixel(3,31,1)
            oled.pixel(3,30,1)
            oled.pixel(3,29,1)
            oled.pixel(4,28,1)
            oled.pixel(4,27,1)
            oled.pixel(4,26,1)
            oled.pixel(4,25,1)
            oled.pixel(5,24,1)
            oled.pixel(6,23,1)
            oled.pixel(7,23,1)
            oled.pixel(8,24,1)
            oled.pixel(9,25,1)
            oled.pixel(9,26,1)
            oled.pixel(9,27,1)
            oled.pixel(10,28,1)
            oled.pixel(10,29,1)
            oled.pixel(11,30,1)
            oled.pixel(12,31,1)
            oled.pixel(13,31,1)
            oled.pixel(14,30,1)
            oled.pixel(15,29,1)
            oled.pixel(15,28,1)
            oled.pixel(15,27,1)
            oled.pixel(15,26,1)
            oled.pixel(16,25,1)
            oled.pixel(16,24,1)
            oled.pixel(16,23,1)
        elif shape == 1: #Saw
            oled.line(3,31,9,24,1)
            oled.vline(9,24,8,1)
            oled.line(9,31,15,24,1)
            oled.vline(15,24,8,1)
        elif shape == 2: #Square
            oled.vline(3,24,8,1)
            oled.hline(3,24,6,1)
            oled.vline(9,24,8,1)
            oled.hline(9,31,6,1)
            oled.vline(15,24,8,1)
        elif shape == 3: #Off
            oled.line(3,24,15,31,1)
            oled.line(15,24,3,31,1)
        elif shape == 4: #Random(ish)
            oled.pixel(3,29,1)
            oled.pixel(4,28,1)
            oled.pixel(4,27,1)
            oled.pixel(5,26,1)
            oled.pixel(6,26,1)
            oled.pixel(7,27,1)
            oled.pixel(8,28,1)
            oled.pixel(9,28,1)
            oled.pixel(10,27,1)
            oled.pixel(10,26,1)
            oled.pixel(10,25,1)
            oled.pixel(11,24,1)
            oled.pixel(12,25,1)
            oled.pixel(13,26,1)
            oled.pixel(13,27,1)
            oled.pixel(14,28,1)
            oled.pixel(14,29,1)
            oled.pixel(15,30,1)
            oled.pixel(16,30,1)
        
    def display_selected_lfo(self):
        """Draw the current LFO's number and division to the OLED display"""
        oled.fill_rect(0,0,20,32,0)
        oled.fill_rect(0,0,20,9,1)
        oled.text(str(self.selected_lfo+1),6,1,0)
        
        number = self.divisions[self.selected_lfo]
        x = 2 if number >= 10 else 6
        oled.text(str(number),x,12,1)
        
        self.draw_wave()
        
    def round_nearest(self, x, a):
        return round(x / a) * a
        
    def calculate_voltage(self, cv, multiplier):
        """Determine the voltage based on current degree, wave shape, and MAX_VOLTAGE"""
        three_sixty = 360*multiplier
        degree_three_sixty = self.degree % three_sixty
        lfo_mode = self.modes[cvs.index(cv)]
        if lfo_mode == 0: #Sin
            voltage = ((0-(cos(self.rad*(1/multiplier)))+1)) * (MAX_VOLTAGE/2)
        elif lfo_mode == 1: #Saw
            voltage = (degree_three_sixty / (three_sixty)) * MAX_VOLTAGE
        elif lfo_mode == 2: #Square
            voltage = MAX_VOLTAGE * (int((degree_three_sixty / (three_sixty)) * MAX_VOLTAGE) < (MAX_VOLTAGE/2))
        elif lfo_mode == 3: #Off
            voltage = 0
        elif lfo_mode == 4: #Random(ish). This is NOT actually random, it is the sum of 3 out of sync sine waves, but it produces a flucutating voltage that is near impossible to predict over time, and which can be clocked to be in time
            voltage = ((((0-(cos(self.rad*(1/multiplier)))+1)) * (MAX_VOLTAGE/2)) / 3) + ((((0-(cos(self.rad*(1/(multiplier*2.3))))+1)) * (MAX_VOLTAGE/2)) / 3) + ((((0-(cos(self.rad*(1/(multiplier*5.6))))+1)) * (MAX_VOLTAGE/2)) / 3)
        return voltage
        
    def display_graphic_lines(self):
        """Draw the lines displaying each LFO's voltage to the OLED display"""
        self.rad = radians(self.degree)
        oled.vline(self.pixel_x,0,OLED_HEIGHT,0)
        for cv, multiplier in zip(cvs, self.divisions):
            volts = self.calculate_voltage(cv, multiplier)
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
