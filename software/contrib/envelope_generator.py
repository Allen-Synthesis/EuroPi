from time import sleep
from europi import oled, din, cv1, cv2, cv3, k1, k2, b1, b2, ain, OLED_WIDTH, OLED_HEIGHT
from europi_script import EuroPiScript

from time import sleep_ms, ticks_ms, ticks_diff
from math import log


class EnvelopeGenerator(EuroPiScript):
    def __init__(self):
        super().__init__()
        state = self.load_state_json()
        
        self.sustain_mode = state.get("sustain_mode", 1)
        self.looping_mode = state.get("looping_mode", 0)

        self.max_output_voltage = 10
        
        #Distance of envelope voltage from max voltage/0 before 'jumping' to it - prevents large logarithmic calculations
        self.voltage_threshold = 0.1
        
        #Length of the longest possible envelope (not in any meaningful unit)
        self.max_increment_factor = 256
        self.update_increment_factor()
        
        #Time in ms between incrementing value of envelope
        self.increment_delay = 1
        
        #0 will start a new envelope at the current value, 1 will start it from zero
        self.retrig_mode = 0
        
        #Display refresh rate in ms
        self.display_refresh_rate = 30
        self.last_refreshed_display = self.display_refresh_rate

        self.envelope_display_bounds = [0, 0, int(OLED_WIDTH), int(OLED_HEIGHT / 2)]
        
        self.direction = 3  # Rising = 1, Falling = 0, Sustain = 3
        self.envelope_value = 0
        
        self.envelope_out = cv2
        self.envelope_inverted_out = cv3
        self.din_copy_out = cv1

        din.handler(self.receive_trigger_rise)
        din.handler_falling(self.receive_trigger_fall)
        b1.handler(self.change_sustain_mode)
        b2.handler(self.change_looping_mode)
        

    @classmethod
    def display_name(cls):
        return "EnvelopeGen"

    def receive_trigger_rise(self):
        if self.retrig_mode == 1:
            self.envelope_value = 0
        self.direction = 1
    
    def receive_trigger_fall(self):
        self.direction = 0
        
    def change_sustain_mode(self):
        self.sustain_mode = 1 - self.sustain_mode
        #Save state to file
        self.save_state()
        
    def change_looping_mode(self):
        self.looping_mode = 1 - self.looping_mode
        #Save state to file
        self.save_state()
        
    def copy_digital_input(self):
        self.din_copy_out.value(din.value())

    def difference(self, a, b):
        return abs(a - b)
    
    def update_increment_factor(self):
        increment_factor_rising = k1.range(self.max_increment_factor, 512) / 2
        self.increment_factor = [(increment_factor_rising + 1), (k2.range(self.max_increment_factor, 256) + 1 + (ain.percent(256) * self.max_increment_factor))]
        
    def log(self, number):
        return log(max(number, 1))

    def update_envelope_value(self):
        #Envelope rising
        if self.direction == 1:
            increment = self.difference(self.envelope_value, self.max_output_voltage) / self.increment_factor[0]
            self.envelope_value += increment
            if self.difference(self.envelope_value, self.max_output_voltage) <= self.voltage_threshold:
                self.envelope_value = self.max_output_voltage
                if self.sustain_mode == 1 and self.looping_mode == 0:
                    self.direction = 3
                else:
                    self.direction = 0
            else:
                sleep_ms(self.increment_delay)
            
        #Envelope falling
        elif self.direction == 0:
            increment = self.difference(0, self.envelope_value) / self.increment_factor[1]
            self.envelope_value -= increment
            if self.difference(0, self.envelope_value) <= self.voltage_threshold:
                self.envelope_value = 0
                if self.looping_mode == 0:
                    self.direction = 3
                else:
                    self.direction = 1
            else:
                sleep_ms(self.increment_delay)
            
        #Update CV output to envelope value
        self.update_output_voltage()
            
        
    def update_output_voltage(self):
        self.envelope_out.voltage(self.envelope_value)
        self.envelope_inverted_out.voltage(self.max_output_voltage - self.envelope_value)
        
    def update_display(self):
        if ticks_diff(ticks_ms(), self.last_refreshed_display) >= self.display_refresh_rate:
            
            #Draw slope graph axis
            oled.hline(self.envelope_display_bounds[0], self.envelope_display_bounds[3], self.envelope_display_bounds[2], 1)
            oled.vline(self.envelope_display_bounds[0], self.envelope_display_bounds[1], self.envelope_display_bounds[3], 1)
            oled.vline((self.envelope_display_bounds[2] - 1), self.envelope_display_bounds[1], self.envelope_display_bounds[3], 1)
            
            try:
                rise_width = (self.increment_factor[0] - 1) / ((self.increment_factor[0] - 1) + (self.increment_factor[1] - 1))	#If envelope has zero rise and zero fall this will throw a ZeroDivisonError
                draw_envelope = True
            except ZeroDivisionError:
                draw_envelope = False
            
            if draw_envelope == True:
                rise_width_pixels = int(rise_width * self.envelope_display_bounds[2])
                fall_width = 1 - rise_width
                fall_width_pixels = int(self.envelope_display_bounds[2] - rise_width_pixels)
                
                #Generate rise slope pixels
                rise_pixels = []
                for pixel in range(rise_width_pixels):
                    x = pixel / (rise_width_pixels + 1)
                    y = x**2
                    x_pixel = rise_width_pixels - int(x * rise_width_pixels)
                    y_pixel = int(y * (self.envelope_display_bounds[3] - self.envelope_display_bounds[1]))
                    rise_pixels.append((x_pixel, y_pixel))
                rise_pixels.append((self.envelope_display_bounds[0], self.envelope_display_bounds[3]))
                    
                #Generate fall slope pixels
                fall_pixels = []
                for pixel in range(fall_width_pixels):
                    x = pixel / (fall_width_pixels + 1)
                    y = x**2
                    x_pixel = (fall_width_pixels - int(x * fall_width_pixels)) + rise_width_pixels
                    y_pixel = self.envelope_display_bounds[3] - int(y * (self.envelope_display_bounds[3] - self.envelope_display_bounds[1]))
                    fall_pixels.append((x_pixel, y_pixel))
                fall_pixels.append((rise_width_pixels, self.envelope_display_bounds[1]))
                    
                #Draw rise and fall slopes
                for array in [rise_pixels, fall_pixels]:
                    for index, pixel in enumerate(array[:-1]):
                        oled.line(array[index + 1][0], array[index + 1][1], pixel[0], pixel[1], 1)
                
                #Draw current envelope position
                current_envelope_position = 0
                if self.direction == 1 or self.direction == 3:
                    current_envelope_position = int((self.envelope_value / self.max_output_voltage) * rise_width_pixels)
                elif self.direction == 0:
                    current_envelope_position = self.envelope_display_bounds[2] - 1 - int((self.envelope_value / self.max_output_voltage) * (self.envelope_display_bounds[2] - rise_width_pixels))
                oled.vline(current_envelope_position, self.envelope_display_bounds[1], (self.envelope_display_bounds[3] - 1), 1)
            else:
                oled.vline(self.envelope_display_bounds[0], self.envelope_display_bounds[1], self.envelope_display_bounds[3], 1)
                oled.hline(self.envelope_display_bounds[0], self.envelope_display_bounds[1], self.envelope_display_bounds[2], 1)
                oled.vline((self.envelope_display_bounds[2] - 1), self.envelope_display_bounds[1], self.envelope_display_bounds[3], 1)
            
            #Display current envelope direction
            if self.direction == 1:
                direction_text = 'rise'
            elif self.direction == 0:
                direction_text = 'fall'
            elif self.direction == 3 and self.envelope_value == self.max_output_voltage:
                direction_text = 'hold'
            else:
                direction_text = 'off'
            oled.text(direction_text, 0, 20, 1)
            
            #Display current envelope mode (AR or ASR)
            if self.sustain_mode == 0:
                sustain_mode_text = 'ar'
            else:
                sustain_mode_text = 'asr'
            oled.text(sustain_mode_text, 50 + (4 if sustain_mode_text == 'ar' else 0), 20, 1)
            
            #Display current envelope looping mode
            if self.looping_mode == 0:
                looping_mode_text = 'once'
            else:
                looping_mode_text = 'loop'
            oled.text(looping_mode_text, 94, 20, 1)
            
            oled.show()
            oled.fill(0)
            self.last_refreshed_display = ticks_ms()

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return

        state = {
            "sustain_mode": self.sustain_mode,
            "looping_mode": self.looping_mode,
        }
        self.save_state_json(state)

    def main(self):
        while True:
            self.copy_digital_input()
            self.update_display()
            self.update_increment_factor()
            self.update_envelope_value()

if __name__ == "__main__":
    EnvelopeGenerator().main()

