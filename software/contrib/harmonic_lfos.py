from europi import *
from math import cos, radians
from random import randint
from time import sleep_ms
from machine import freq
from europi_script import EuroPiScript

MAX_VOLTAGE = 10
MAX_HARMONIC = 32

freq(250_000_000)

class HarmonicLFOs(EuroPiScript):

    def __init__(self):
        super().__init__()
        state = self.load_state_json()
        
        self.HARMONICS = state.get("HARMONICS", [1, 3, 5, 7, 11, 13])
        self.MODE = state.get("MODE", 0)
        
        self.degree = 0
        self.delay, self.increment_value = self.get_delay_increment_value()
        self.pixel_x = OLED_WIDTH-1
        self.pixel_y = OLED_HEIGHT-1
        self.selected_lfo = 0
        self.selected_lfo_start_value = self.read_k2()
        
        din.handler(self.reset)
        b1.handler(self.change_mode)
        b2.handler(self.increment_selection)

    def read_k2(self):
        return k2.read_position(MAX_HARMONIC) + 1

    def reset(self):
        self.degree = 0

    def change_mode(self):
        self.MODE += 1
        
        if self.MODE == 3:
            self.MODE = 0
            
        self.save_state()

    def get_delay_increment_value(self):
        delay = (0.1 - (k1.read_position(100, 1)/1000)) + (ain.read_voltage(1)/100)
        return delay, round((((1/delay)-10)/1)+1)

    def increment_selection(self):
        self.selected_lfo += 1
        if self.selected_lfo == 6:
            self.selected_lfo = 0
        self.selected_lfo_start_value = self.read_k2()

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return
        
        state = {
            "HARMONICS": self.HARMONICS,
            "MODE": self.MODE
        }
        self.save_state_json(state)

    def main(self):
        global degree, delay, increment_value, selected_lfo, selected_lfo_start_value

        while True:
            rad = radians(self.degree)
            
            #Hysteresis to prevent each LFO's value from being changed as soon as it is selected
            self.k2_reading = self.read_k2()
            if self.k2_reading != self.selected_lfo_start_value:
                self.selected_lfo_start_value = self.k2_reading
                self.HARMONICS[self.selected_lfo] = self.k2_reading
                self.save_state()
            
            oled.vline(self.pixel_x,0,OLED_HEIGHT,0)
            for cv, multiplier in zip(cvs, self.HARMONICS):
                three_sixty = 360*multiplier
                degree_three_sixty = self.degree % three_sixty
                
                if self.MODE == 0: #Sin
                    volts = ((0-(cos(rad*(1/multiplier)))+1)) * (MAX_VOLTAGE/2)
                elif self.MODE == 1: #Saw
                    volts = (degree_three_sixty / (three_sixty)) * MAX_VOLTAGE
                elif self.MODE == 2: #Square
                    volts = MAX_VOLTAGE * (int((degree_three_sixty / (three_sixty)) * MAX_VOLTAGE) < (MAX_VOLTAGE/2))
                    
                cv.voltage(volts)
                oled.pixel(self.pixel_x,self.pixel_y-int(volts*(self.pixel_y/10)),1)
            
            #Draw the current LFO's information to the display
            oled.fill_rect(0,0,20,32,0)
            oled.fill_rect(0,0,20,9,1)
            oled.text(str(self.selected_lfo+1),6,1,0)
            
            number = self.HARMONICS[self.selected_lfo]
            x = int(number >= 10) * 4
            oled.text(str(number),(6 - x),20,1)
            
            #Delay based on the speed, controlled by knob 1
            self.degree += self.increment_value
            sleep_ms(int(self.delay))
            oled.scroll(-1,0)
            
            #Update the display every 10 cycles
            if round(self.degree, -1) % 10 == 0:
                self.delay, self.increment_value = self.get_delay_increment_value()
                oled.show()


if __name__ == "__main__":
    HarmonicLFOs().main()
