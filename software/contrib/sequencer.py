from time import sleep, ticks_ms, ticks_diff
from europi import *
from europi_script import EuroPiScript
from framebuf import FrameBuffer, MONO_HLSB

from contrib.polyrhythmic_sequencer import NOTES, VOLT_PER_OCT

NOTES[0] = "OFF"
KNOB_SAMPLES = 512

class Sequence:
    def __init__(self, sequence, steps, clock_output, pitch_output):
        self.steps = steps
        if sequence == None:
            self.clear_sequence()
        else:
            self.sequence = sequence
        self.position = 0
        self.clock_output = clock_output
        self.pitch_output = pitch_output
        
    def update_position(self, new_position):
        self.position = new_position % self.steps
        self.pad_sequence()
        self.update_pitch_voltage()
        
    def clear_sequence(self):
        self.sequence = []
        for step in range(self.steps):
            self.sequence.append("OFF")
            
    def pad_sequence(self):
        while len(self.sequence) < self.steps:
            self.sequence.append("OFF")
            
    def set_step(self, step, note):
        self.sequence[step] = note
        
    def set_length(self, length):
        self.steps = length
        self.update_position(self.position)
        
    def update_pitch_voltage(self):
        self.pitch_output.voltage(NOTES.index(self.sequence[self.position]) * VOLT_PER_OCT)
        if self.pitch_output.voltage() != 0:
            self.clock_output.on()
            
    def clock_off(self):
        self.clock_output.off()
        
class Sequencer(EuroPiScript):
    def __init__(self):
        super().__init__()
        
        state = self.load_state_json()
        old_sequence_1_length = state.get("sequence_1_length", 8)
        old_sequence_1 = state.get("sequence_1", None)
        old_sequence_2_length = state.get("sequence_2_length", 8)
        old_sequence_2 = state.get("sequence_2", None)
        
        self.sequence_1 = Sequence(old_sequence_1, old_sequence_1_length, cv1, cv2)
        self.sequence_2 = Sequence(old_sequence_2, old_sequence_2_length, cv4, cv5)
        self.sequences = [self.sequence_1, self.sequence_2]
        self.sequence = self.sequences[0]
        
        self.step_images = [
            FrameBuffer(bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\xe0'), 3, 9, MONO_HLSB),
            FrameBuffer(bytearray(b'\x00\x00\x00\x00\x00\x00\x00\xe0\xe0'), 3, 9, MONO_HLSB),
            FrameBuffer(bytearray(b'\x00\x00\x00\x00\x00\x00\xe0\xe0\xe0'), 3, 9, MONO_HLSB),
            FrameBuffer(bytearray(b'\x00\x00\x00\x00\x00\xe0\xe0\xe0\xe0'), 3, 9, MONO_HLSB),
            FrameBuffer(bytearray(b'\x00\x00\x00\x00\xe0\xe0\xe0\xe0\xe0'), 3, 9, MONO_HLSB),
            FrameBuffer(bytearray(b'\x00\x00\x00\xe0\xe0\xe0\xe0\xe0\xe0'), 3, 9, MONO_HLSB),
            FrameBuffer(bytearray(b'\x00\x00\xe0\xe0\xe0\xe0\xe0\xe0\xe0'), 3, 9, MONO_HLSB),
            FrameBuffer(bytearray(b'\x00\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0'), 3, 9, MONO_HLSB),
            FrameBuffer(bytearray(b'\x00\xe0\xe0\xe0\xe0\xe0\xe0\xe0\xe0'), 3, 9, MONO_HLSB)
            ]

        self.image_blank = FrameBuffer(bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00'), 3, 9, MONO_HLSB)
        self.step_image_selected = FrameBuffer(bytearray(b'\xa0@\xa0@\xa0@\xa0@\xa0'), 3, 9, MONO_HLSB)
        self.position_image = FrameBuffer(bytearray(b'\xe0'), 3, 2, MONO_HLSB)
        
        self.displaying_sequences = False
        self.selected_step = 0
        self.editing_step = False
        self.editing_sequence = False
        self.update_sequence_ui = False
        
        self.long_press_amount = 400
        
        self.position = 0
        
        b2.handler_falling(self.b2_handler_falling)
        din.handler(self.increment_position)
        din.handler_falling(self.clock_off)
        b1.handler(self.increment_position)

    @classmethod
    def display_name(cls):
        return "Sequencer"
    
    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
    
        state = {
            "sequence_1_length": self.sequence_1.steps,
            "sequence_1": self.sequence_1.sequence,
            "sequence_2_length": self.sequence_2.steps,
            "sequence_2": self.sequence_2.sequence,
        }
        self.save_state_json(state)
    
    def increment_position(self):
        self.position += 1
        
        for sequence in self.sequences:
            sequence.update_position(self.position)
        
    def clock_off(self):
        for sequence in self.sequences:
            sequence.clock_off()
    
    def b2_handler_falling(self):
        if abs(ticks_diff(ticks_ms(), b2.last_pressed())) > self.long_press_amount:	# Long press
            self.displaying_sequences = True
            self.long_pressed = True
            self.editing_sequence = False
            self.editing_step = False
            
        if self.displaying_sequences:	# If displaying sequences, then the user has just chosen the sequence to edit
            self.sequence = self.sequences[k2.read_position(len(self.sequences)), KNOB_SAMPLES]
            if not self.long_pressed:
                self.displaying_sequences = False
            else:
                self.long_pressed = False
        elif self.editing_step:	# If editing step, then the user has just chosen the new note value for the step
            self.sequence.set_step(self.selected_step, NOTES[self.currently_selected_step])
            self.editing_step = False
        elif self.editing_sequence:	# If editing sequence, then the user has just chosen the step to change the note value for
            self.sequence.set_length(self.currently_selected_step)
            self.editing_sequence = False
            self.update_sequence_ui = True	# A new sequence length requires a full OLED update to cover up the old sequence images
        else:
            if self.currently_selected_step != 0:
                self.editing_step = True
                self.selected_step = self.currently_selected_step - 1
            else:
                self.editing_sequence = True

        self.save_state()
        
    def calculate_ui_elements(self):
        if self.displaying_sequences:
            self.currently_selected_step = k2.read_position(len(self.sequences))
            left_text = f'EDIT SEQUENCE'
            right_text = f'{self.currently_selected_step + 1}'
        elif self.editing_step:
            self.currently_selected_step = k2.read_position(len(NOTES), KNOB_SAMPLES)
            left_text = f'STEP {self.selected_step + 1}'
            right_text = NOTES[self.currently_selected_step]
        elif self.editing_sequence:
            self.currently_selected_step = k2.read_position(32, KNOB_SAMPLES) + 1
            left_text = f'LENGTH: {self.currently_selected_step}'
            right_text = ""
        else:
            self.currently_selected_step = k2.read_position(self.sequence.steps + 1, KNOB_SAMPLES)
            if self.currently_selected_step != 0:
                left_text = f'STEP {self.currently_selected_step}'
                right_text = self.sequence.sequence[self.currently_selected_step - 1]
            else:
                left_text = 'EDIT LENGTH'
                right_text = ''
                
        return left_text, right_text
        
    def display_ui(self):
        left_text, right_text = self.calculate_ui_elements()
        
        # If the sequence length has changed then cover up the old sequence images, otherwise only cover up the text at the bottom
        oled.fill_rect(0, 0 if self.update_sequence_ui else 23, OLED_WIDTH, OLED_HEIGHT, 0)
        self.update_sequence_ui = False
        
        for index, sequence in enumerate(self.sequences):
            # Draw the indicator of the current position
            #position_indicator_offset = index * 12
            #oled.fill_rect(0, position_indicator_offset, OLED_WIDTH, position_indicator_offset + 2, 0)
            #oled.blit(self.position_image, (sequence.position * 4), (index * 12))
            
            # If not in any edit mode, display the sequence images
            if self.editing_sequence and sequence == self.sequence:
                for step in range(32):
                    x = step * 4
                    y = (index * 10)
                    
                    if step < self.currently_selected_step:
                        image = self.step_image_selected
                    else:
                        image = self.image_blank
                    oled.blit(image, x, y)
            else:
                for step in range(sequence.steps):
                    x = step * 4
                    y = (index * 10)
                    
                    if (self.editing_step == False and step == self.currently_selected_step - 1) and (sequence == self.sequence):
                        image = self.step_image_selected
                    else:
                        if (self.editing_step and step == self.selected_step) and (sequence == self.sequence):
                            step_image_index = int(k2.read_position(len(NOTES), KNOB_SAMPLES) / 6.7)
                        else:
                            step_image_index = int(NOTES.index(sequence.sequence[step]) / 6.7)
                        image = self.step_images[step_image_index]
                    oled.blit(image, x, y)
            
        # Draw the left and right text
        oled.text(left_text, 0, 23, 1)
        oled.fill_rect(OLED_WIDTH - 24, OLED_HEIGHT - 10, 24, 10, 1 if self.editing_step else 0)
        oled.text(right_text, OLED_WIDTH - (len(right_text) * 8), 23, 0 if self.editing_step else 1)
        
        oled.show()

    def main(self):
        while True:
            self.display_ui()

if __name__ == "__main__":
    Sequencer().main()

