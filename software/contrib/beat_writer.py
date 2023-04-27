from time import sleep_ms, ticks_ms, ticks_diff
from europi import *
from europi_script import EuroPiScript
from random import randint
from machine import freq

freq(250_000_000)

class BeatWriter(EuroPiScript):
    def __init__(self):
        super().__init__()
        
        self.length = 16
        
        state = self.load_state_json()
        self.rhythm_1 = state.get("rhythm_1", self.create_blank_rhythm(self.length))
        self.rhythm_2 = state.get("rhythm_2", self.create_blank_rhythm(self.length))
        
        self.previous_step_ticks = ticks_ms
        self.previous_step_length = 0
    
        self.step = 0
                
        self.din_out = cv1
        self.rhythm_1_output = cv2
        self.rhythm_2_output = cv5
        self.start_output = cv4
        
        din.handler(self.increment_step)
        
        b1.handler(self.place_beat)
        b2.handler(self.place_beat)

        b1.handler_falling(self.check_if_reset_rhythm_1)
        b2.handler_falling(self.check_if_reset_rhythm_2)

    @classmethod
    def display_name(cls):
        return "Beat Writer"

    def create_blank_rhythm(self, length):
        rhythm = []
        for beat in range(length):
            rhythm.append(0)
        return rhythm
    
    def update_randomisation(self):
        self.randomisation_1 = k1.read_position()
        self.randomisation_2 = k2.read_position()
    
    def update_outputs(self):
        self.update_randomisation()
        output_1_value = randint(0, 1) if randint(2, 98) < self.randomisation_1 else self.rhythm_1[self.step]
        output_2_value = randint(0, 1) if randint(2, 98) < self.randomisation_2 else self.rhythm_2[self.step]
        
        self.rhythm_1_output.value(output_1_value)
        self.rhythm_2_output.value(output_2_value)
    
    def increment_step(self):
        current_ticks = ticks_ms()
        self.previous_step_length = ticks_diff(current_ticks, self.previous_step_ticks)
        self.previous_step_ticks = current_ticks
        
        self.start_output.value(0)
        self.step += 1
        if self.step == self.length:
            self.step = 0
            self.start_output.value(1)
            
        self.update_outputs()
        self.update_display()
        
    def check_if_reset_rhythm_1(self):
        current_ticks = ticks_ms()
        b1_difference = ticks_diff(current_ticks, b1.last_pressed())
        if b1_difference > 300:
            self.reset_rhythm(self.rhythm_1)
        self.save_state()
            
    def check_if_reset_rhythm_2(self):
        current_ticks = ticks_ms()
        b2_difference = ticks_diff(current_ticks, b2.last_pressed())
        if b2_difference > 300:
            self.reset_rhythm(self.rhythm_2)
        self.save_state()
            
    def reset_rhythm(self, rhythm):
        for index, beat in enumerate(rhythm):
            rhythm[index] = 0
        
    def update_display(self):
        oled.fill(0)
        oled.text(f"{self.randomisation_1}%", 0, 0, 1)
        oled.text(f"{self.randomisation_2}%", 64, 0, 1)
        oled.text(f"{self.convert_rhythm_to_string(self.rhythm_1)}", 0, 12, 1)
        oled.text(f"{self.convert_rhythm_to_string(self.rhythm_2)}", 0, 24, 1)
        oled.show()
    
    def convert_rhythm_to_string(self, rhythm):
        output_string = ''
        for beat_step, beat in enumerate(rhythm):
            if beat_step == self.step:
                output_string += '-'
            elif beat == 0:
                output_string += '_'
            else:
                output_string += '^'
        return output_string
    
    def place_beat(self):
        if b1.value() == 1:
            rhythm = self.rhythm_1
            self.rhythm_1_output.value(1)
        elif b2.value() == 1:
            rhythm = self.rhythm_2
            self.rhythm_2_output.value(1)
        else:
            return
        
        half_beat_length = int(self.previous_step_length / 2)
        current_time_difference_from_previous_beat = ticks_diff(ticks_ms(), self.previous_step_ticks)
        if current_time_difference_from_previous_beat > half_beat_length:	#If the length of time since the last beat is more than 1/2 one beat's length
            rhythm[(self.step + 1) % self.length] = 1 - rhythm[(self.step + 1) % self.length]	#Invert the current step
        else:
            rhythm[(self.step - 1) % self.length] = 1 - rhythm[(self.step + 1) % self.length]	#Invert the current step
        
        self.save_state()
        
    def splash_screen(self):
        oled.centre_text('BEAT WRITER\n\nplug in clock')
        oled.hline(0, 14, OLED_WIDTH, 1)
        oled.show()
    
    def save_state(self):
        """Save the current state variables as JSON."""
        state = {
            "rhythm_1": self.rhythm_1,
            "rhythm_2": self.rhythm_2,
        }
        self.save_state_json(state)

    def main(self):
        self.splash_screen()
        while din.value() == 0:
            sleep_ms(100)
        while True:
            self.din_out.value(din.value())

if __name__ == "__main__":
    BeatWriter().main()