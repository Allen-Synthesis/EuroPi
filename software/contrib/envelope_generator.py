from time import sleep
from europi import oled, din, cv1, cv2, cv3, k1, k2, b1, b2, ain, OLED_WIDTH, OLED_HEIGHT
from europi_script import EuroPiScript

from time import sleep_ms, ticks_ms
from math import log


class EnvelopeGenerator(EuroPiScript):
    def __init__(self):
        super().__init__()
        state = self.load_state_json()

        self.max_output_voltage = 10
        self.envelope_value = 0
        self.direction = 1
        
        self.voltage_threshold = 0.1		#Distance of envelope voltage from max voltage/0 before 'jumping' to it - prevents large logarithmic calculations
        
        self.max_increment_factor = 256		#Length of the longest envelope (not in any meaningful unit)
        self.update_increment_factor()
        self.increment_delay = 1			#Time in ms between incrementing value of envelope
        
        self.last_refreshed_display = 30
        
        self.log_multiplier = OLED_HEIGHT / log(OLED_HEIGHT)
        
        self.envelope_display_bounds = [0, 0, int(OLED_WIDTH / 1.7), int(OLED_HEIGHT / 2)]
        
        self.sustain_mode = 0	#0 is attack release (no sustain), 1 is attack sustain release
        self.looping_mode = 0
        
        self.envelope_out = cv1
        self.envelope_inverted_out = cv2
        self.din_copy_out = cv3

        din.handler(self.receive_trigger_rise)
        din.handler_falling(self.receive_trigger_fall)
        b1.handler(self.change_sustain_mode)
        b2.handler(self.change_looping_mode)
        

    @classmethod
    def display_name(cls):
        return "EnvelopeGen"

    def receive_trigger_rise(self):
        self.direction = 1
    
    def receive_trigger_fall(self):
        self.direction = 0
        
    def change_sustain_mode(self):
        self.sustain_mode = 1 - self.sustain_mode
        
    def change_looping_mode(self):
        self.looping_mode = 1 - self.looping_mode
        
    def copy_digital_input(self):
        self.din_copy_out.value(din.value())

    def difference(self, a, b):
        return abs(a - b)
    
    def update_increment_factor(self):
        self.increment_factor = [(k1.range(self.max_increment_factor) + 1), (k2.range(self.max_increment_factor) + 1 + (ain.percent(128) * self.max_increment_factor))]
        
    def log(self, number):
        return log(max(number, 1))

    def update_envelope_value(self):
        if self.direction == 1:																						#If envelope is rising
            increment = self.difference(self.envelope_value, self.max_output_voltage) / self.increment_factor[0]	#Logarithmic increase
            self.envelope_value += increment
            if self.difference(self.envelope_value, self.max_output_voltage) <= self.voltage_threshold:				#If the threshold is reached
                self.envelope_value = self.max_output_voltage
                if self.sustain_mode == 1:																			#If mode uses sustain
                    self.direction = 3																				#Waiting (holding max voltage)
                else:
                    self.direction = 0
                
            else:
                sleep_ms(self.increment_delay)																		#Otherwise continute envelope rise
            
        elif self.direction == 0:																					#If envelope is falling
            increment = self.difference(0, self.envelope_value) / self.increment_factor[1]							#Logarithmic decrease
            self.envelope_value -= increment
            if self.difference(0, self.envelope_value) <= self.voltage_threshold:									#If the threshold is reached
                self.envelope_value = 0
                if self.looping_mode == 0:
                    self.direction = 3																				#Waiting (holding zero voltage)
                else:
                    self.direction = 1
            else:
                sleep_ms(self.increment_delay)																		#Otherwise continute envelope rise
            
        self.update_output_voltage()
            
        
    def update_output_voltage(self):
        self.envelope_out.voltage(self.envelope_value)
        self.envelope_inverted_out.voltage(self.max_output_voltage - self.envelope_value)
        
    def update_display(self):
        if ticks_ms() - self.last_refreshed_display >= 30:
            
            oled.rect(self.envelope_display_bounds[0], self.envelope_display_bounds[1], self.envelope_display_bounds[2], self.envelope_display_bounds[3], 1)
            
            try:
                rise_width = (self.increment_factor[0] - 1) / ((self.increment_factor[0] - 1) + (self.increment_factor[1] - 1))
                rise_width_pixels = int(rise_width * self.envelope_display_bounds[2]) - 1
                oled.line(self.envelope_display_bounds[0], (self.envelope_display_bounds[3] - 1), rise_width_pixels, self.envelope_display_bounds[1], 1)
                oled.line(rise_width_pixels, self.envelope_display_bounds[1], (self.envelope_display_bounds[2] - 1), (self.envelope_display_bounds[3] - 1), 1)
                
                current_envelope_position = 0
                if self.direction == 1 or self.direction == 3:
                    current_envelope_position = int((self.envelope_value / self.max_output_voltage) * rise_width_pixels)
                elif self.direction == 0:
                    current_envelope_position = self.envelope_display_bounds[2] - 1 - int((self.envelope_value / self.max_output_voltage) * (self.envelope_display_bounds[2] - rise_width_pixels))
                oled.vline(current_envelope_position, self.envelope_display_bounds[1], (self.envelope_display_bounds[3] - 1), 1)
                
            except ZeroDivisionError:
                oled.vline(self.envelope_display_bounds[0], self.envelope_display_bounds[1], self.envelope_display_bounds[3], 1)
                oled.hline(self.envelope_display_bounds[0], self.envelope_display_bounds[1], self.envelope_display_bounds[2], 1)
                oled.vline(self.envelope_display_bounds[2], self.envelope_display_bounds[1], self.envelope_display_bounds[3], 1)
            
            if self.direction == 1:
                direction_text = 'rise'
            elif self.direction == 0:
                direction_text = 'fall'
            elif self.direction == 3 and self.envelope_value == self.max_output_voltage:
                direction_text = 'hold'
            else:
                direction_text = 'off'
            oled.text(direction_text, 0, 20, 1)
            
            if self.sustain_mode == 0:
                sustain_mode_text = 'ar'
            else:
                sustain_mode_text = 'asr'
            oled.text(sustain_mode_text, 80, -2, 1)
            
            if self.looping_mode == 0:
                looping_mode_text = 'once'
            else:
                looping_mode_text = 'loop'
            oled.text(looping_mode_text, 80, 9, 1)
            
            oled.show()
            oled.fill(0)
            self.last_refreshed_display = ticks_ms()

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return

        state = {
            #"counter": self.counter,
            #"enabled": self.enabled,
        }
        self.save_state_json(state)

    def main(self):
        while True:
            self.copy_digital_input()
            self.update_display()
            self.update_increment_factor()
            self.update_envelope_value()
            #sleep(1)

if __name__ == "__main__":
    EnvelopeGenerator().main()