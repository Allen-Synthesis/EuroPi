from europi import *
from time import sleep_ms, ticks_ms, ticks_add, ticks_diff
from europi_script import EuroPiScript
import machine

# Internal clock tempo range.
EUCLIDEAN_MAX_BPM = 280
EUCLIDEAN_MIN_BPM = 20

# Trigger Time (some module may not be able to catch up the trigger if it is too short)
EUCLIDEAN_TRG_T = 20

class SingleEuclideanGate():
    def __init__(self, box_position, output, box_size, indicator_offset_x, indicator_offset_y, bar_length_on, bar_length_off, cv_text_offset, cv_text):
        self.notes_para = [1, 0, 0, 0] # length, fill, offset, cv
        self.notes_para_final = [1, 0, 0] # length, fill, offset
        self.notes_list = []
        self.step = 0
        
        self.box_position = box_position
        self.output = output
        self.box_size = box_size
        self.indicator_offset_x = indicator_offset_x
        self.indicator_offset_y = indicator_offset_y
        self.bar_length_on = bar_length_on
        self.bar_length_off = bar_length_off
        self.cv_text_offset = cv_text_offset
        self.cv_text = cv_text

    def para_add_cv(self, cv_value):
        if self.notes_para[3] == 1:
            self.notes_para_final[0] = self.notes_para[0] + cv_value
            self.notes_para_final[1] = self.notes_para[1]
            self.notes_para_final[2] = self.notes_para[2]
        elif self.notes_para[3] == 2:
            self.notes_para_final[0] = self.notes_para[0]
            self.notes_para_final[1] = self.notes_para[1] + cv_value
            self.notes_para_final[2] = self.notes_para[2]
        elif self.notes_para[3] == 3:
            self.notes_para_final[0] = self.notes_para[0]
            self.notes_para_final[1] = self.notes_para[1]
            self.notes_para_final[2] = self.notes_para[2] + cv_value
        else:
            self.notes_para_final[0] = self.notes_para[0]
            self.notes_para_final[1] = self.notes_para[1]
            self.notes_para_final[2] = self.notes_para[2]

    def bound_notes_para(self):
        # Bound L
        if self.notes_para[0] > 19: self.notes_para[0] = 19
        if self.notes_para[0] < 1: self.notes_para[0] = 1
        # Bound F
        if self.notes_para[1] > self.notes_para[0]: 
            self.notes_para[1] = self.notes_para[0]
        if self.notes_para[0] > 1:
            if self.notes_para[1] < 1: self.notes_para[1] = 1
        else:
            if self.notes_para[1] < 0: self.notes_para[1] = 0
        # Bound O
        if self.notes_para[2] > self.notes_para[0]: self.notes_para[2] = self.notes_para[0]
        if self.notes_para[2] < 0: self.notes_para[2] = 0
        # Bound CV
        if self.notes_para[3] > 3: self.notes_para[3] = 3
        if self.notes_para[3] < 0: self.notes_para[3] = 0

    def bound_notes_para_final(self):
        # Bound L
        if self.notes_para_final[0] > 19: self.notes_para_final[0] = 19
        if self.notes_para_final[0] < 1: self.notes_para_final[0] = 1
        # Bound F
        if self.notes_para_final[1] > self.notes_para_final[0]: 
            self.notes_para_final[1] = self.notes_para_final[0]
        if self.notes_para_final[0] > 1:
            if self.notes_para_final[1] < 1: self.notes_para_final[1] = 1
        else:
            if self.notes_para_final[1] < 0: self.notes_para_final[1] = 0
        # Bound O
        if self.notes_para_final[2] > self.notes_para_final[0]: self.notes_para_final[2] = self.notes_para_final[0]
        if self.notes_para_final[2] < 0: self.notes_para_final[2] = 0

    def draw_para_indicator(self, para_idx):
        for cur_para_idx in range(para_idx + 1):
            oled.fill_rect(self.box_position[0] + self.indicator_offset_x[cur_para_idx], 
                           self.box_position[1] + self.indicator_offset_y[cur_para_idx], 
                           2, 2, 1)
        if para_idx == 3:
            oled.text(self.cv_text[self.notes_para[3]], 
                      self.box_position[0] + self.cv_text_offset[0], 
                      self.box_position[1] + self.cv_text_offset[1], 
                      1)

    def draw_notes(self):
        for i in range(len(self.notes_list)):
            # High
            if self.notes_list[i] == 1:
                if len(self.notes_list) < 10:
                    if i != self.step:
                        oled.fill_rect(self.box_position[0] + 2 + i * 4, self.box_position[1] + 5, 3, self.box_size[1] - 5, 1)
                    else:
                        oled.fill_rect(self.box_position[0] + 2 + i * 4, self.box_position[1] + 8, 3, self.box_size[1] - 8, 1)
                        oled.fill_rect(self.box_position[0] + 2 + i * 4, self.box_position[1] + 5, 3, 2, 1)
                elif len(self.notes_list) < 14:
                    if i != self.step:
                        oled.fill_rect(self.box_position[0] + 2 + i * 3, self.box_position[1] + 5, 2, self.box_size[1] - 5, 1)
                    else:
                        oled.fill_rect(self.box_position[0] + 2 + i * 3, self.box_position[1] + 8, 2, self.box_size[1] - 8, 1)
                        oled.fill_rect(self.box_position[0] + 2 + i * 3, self.box_position[1] + 5, 2, 2, 1)
                elif len(self.notes_list) < 20:
                    if i != self.step:
                        oled.fill_rect(self.box_position[0] + 2 + i * 2, self.box_position[1] + 5, 1, self.box_size[1] - 5, 1)
                    else:
                        oled.fill_rect(self.box_position[0] + 2 + i * 2, self.box_position[1] + 8, 1, self.box_size[1] - 8, 1)
                        oled.fill_rect(self.box_position[0] + 2 + i * 2, self.box_position[1] + 5, 1, 2, 1)
            # Low
            else:
                if len(self.notes_list) < 10:
                    if i != self.step:
                        oled.fill_rect(self.box_position[0] + 2 + i * 4, self.box_position[1] + 12, 3, self.box_size[1] - 12, 1)
                    else:
                        oled.fill_rect(self.box_position[0] + 2 + i * 4, self.box_position[1] + 15, 3, self.box_size[1] - 15, 1)
                        oled.fill_rect(self.box_position[0] + 2 + i * 4, self.box_position[1] + 12, 3, 2, 1)
                elif len(self.notes_list) < 14:
                    if i != self.step:
                        oled.fill_rect(self.box_position[0] + 2 + i * 3, self.box_position[1] + 12, 2, self.box_size[1] - 12, 1)
                    else:
                        oled.fill_rect(self.box_position[0] + 2 + i * 3, self.box_position[1] + 15, 2, self.box_size[1] - 15, 1)
                        oled.fill_rect(self.box_position[0] + 2 + i * 3, self.box_position[1] + 12, 2, 2, 1)
                elif len(self.notes_list) < 20:
                    if i != self.step:
                        oled.fill_rect(self.box_position[0] + 2 + i * 2, self.box_position[1] + 12, 1, self.box_size[1] - 12, 1)
                    else:
                        oled.fill_rect(self.box_position[0] + 2 + i * 2, self.box_position[1] + 15, 1, self.box_size[1] - 15, 1)
                        oled.fill_rect(self.box_position[0] + 2 + i * 2, self.box_position[1] + 12, 1, 2, 1)

    def draw_box(self):
        oled.rect(self.box_position[0], self.box_position[1], self.box_size[0], self.box_size[1], 1)

    def step_reset(self):
        if self.step >= self.notes_para_final[0]:
            self.step = 0

    def step_increase(self):
        self.step += 1
        if self.step == self.notes_para_final[0]:
            self.step = 0

    def change_output(self):
        if self.notes_list[self.step] == 1:
            self.output.on()
        else:
            self.output.off()

    def print_para(self):
        print(self.step)
        print(self.notes_list)
        print(self.notes_para)
        print(self.notes_para_final, '\n')

class EuclideanRhythm(EuroPiScript):
    def __init__(self):
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)
        
        all_box_position = [[0, 0],
                            [int(OLED_WIDTH/3), 0],
                            [int(OLED_WIDTH/3*2), 0],
                            [0, int(OLED_HEIGHT/2)],
                            [int(OLED_WIDTH/3), int(OLED_HEIGHT/2)],
                            [int(OLED_WIDTH/3*2), int(OLED_HEIGHT/2)]]
        output = cvs
        box_size = [int(OLED_WIDTH/3), int(OLED_HEIGHT/2)]
        indicator_offset_x  = [29, 32, 35, 38]
        indicator_offset_y = [1, 1, 1, 1]
        bar_length_on = 8
        bar_length_off = 2
        cv_text_offset = [16, 6]
        cv_text = ['-', 'L', 'F', 'O']

        self.euclidean_gates = [SingleEuclideanGate(all_box_position[i], 
                                                    output[i], 
                                                    box_size, 
                                                    indicator_offset_x, 
                                                    indicator_offset_y, 
                                                    bar_length_on, 
                                                    bar_length_off, 
                                                    cv_text_offset, 
                                                    cv_text) 
                                for i in range(6)]

        self.cv_value = 0
        self.gate_idx = 0 # change editing gates
        self.para_idx = 0 # change editing parameters
        self.blink_flg = 0 # blink selection with tempo
        self.external_clock = False
        self.tempo = 60 # current tempo
        self.deadline = 0  # internal clock parameter
        self.prev_clock = 0 # external clock parameter

        # Visualization related
        self.tempo_text_pos = [8, 12]
        self.tempo_box_pos = [5, 7]
        self.tempo_box_size = [33, 20]

        @b1.handler_falling
        def para_sub():
            if self.gate_idx <= 5:
                self.euclidean_gates[self.gate_idx].notes_para[self.para_idx] -= 1
                self.euclidean_gates[self.gate_idx].bound_notes_para()
            else:
                self.external_clock = False
        
        @b2.handler_falling
        def para_add():
            if self.gate_idx <= 5:
                self.euclidean_gates[self.gate_idx].notes_para[self.para_idx] += 1
                self.euclidean_gates[self.gate_idx].bound_notes_para()
            else:
                self.external_clock = True

    def bjorklund(self, steps, pulses):
        steps = int(steps)
        pulses = int(pulses)   
        
        pattern = []    
        counts = []
        remainders = []
        
        divisor = steps - pulses
        remainders.append(pulses)
        level = 0
        while True:
            counts.append(divisor // remainders[level])
            remainders.append(divisor % remainders[level])
            divisor = remainders[level]
            level = level + 1
            if remainders[level] <= 1:
                break
        counts.append(divisor)
        
        def build(level):
            if level == -1:
                pattern.append(0)
            elif level == -2:
                pattern.append(1)         
            else:
                for i in range(0, counts[level]):
                    build(level - 1)
                if remainders[level] != 0:
                    build(level - 2)
        
        build(level)
        i = pattern.index(1)
        pattern = pattern[i:] + pattern[0:i]
        return pattern

    def draw_tempo_setting(self):
        if self.gate_idx == 6:
            oled.text(str(self.tempo), self.tempo_text_pos[0], self.tempo_text_pos[1], 1)
            oled.text('Ext', int(OLED_WIDTH/2) + self.tempo_text_pos[0], self.tempo_text_pos[1], 1)
            
            if self.external_clock == False and self.blink_flg == 0:
                oled.rect(self.tempo_box_pos[0], 
                          self.tempo_box_pos[1], 
                          self.tempo_box_size[0], 
                          self.tempo_box_size[1], 1)
            if self.external_clock == True and self.blink_flg == 0:
                oled.rect(int(OLED_WIDTH/2) + self.tempo_box_pos[0], 
                          self.tempo_box_pos[1], 
                          self.tempo_box_size[0], 
                          self.tempo_box_size[1], 1)

    def get_next_deadline(self):
        # The duration of a quarter note in ms for the current tempo.
        wait_ms = int(60 / self.tempo / 4 * 1000)
        return ticks_add(ticks_ms(), wait_ms)

    def wait(self):
        # Internal clock
        if self.external_clock == False:
            while True:
                if ticks_diff(self.deadline, ticks_ms()) <= 0:
                    self.deadline = self.get_next_deadline()
                    return
        # External clock
        else:
            # Loop until digital in goes high (clock pulse received).
            while self.external_clock == True:
                if din.value() != self.prev_clock:
                    self.prev_clock = 1 if self.prev_clock == 0 else 0
                    if self.prev_clock == 0:
                        return

    def main(self):
        while True:
            self.cv_value = int(ain.read_voltage())
            self.gate_idx = k2.choice([i for i in range(7)])
            if self.gate_idx <= 5: # gate selection mode
                self.para_idx = k1.choice([i for i in range(4)]) # length, fill, offset, cv
            else: # clock editing mode
                self.tempo = round(k1.read_position(EUCLIDEAN_MAX_BPM - EUCLIDEAN_MIN_BPM) + EUCLIDEAN_MIN_BPM)

            self.blink_flg += 1
            # blink every four notes
            if self.external_clock == False:
                if self.blink_flg > 3:
                    self.blink_flg = 0
            # blink every note
            else:
                if self.blink_flg > 1:
                    self.blink_flg = 0
            
            # Set CV controled parameters
            for i in range(6):
                self.euclidean_gates[i].para_add_cv(self.cv_value)
                self.euclidean_gates[i].bound_notes_para_final()
            
            # Generate Euclidean Notes
            for i in range(6):
                if self.euclidean_gates[i].notes_para_final[1] == 0:
                    self.euclidean_gates[i].notes_list = [0, ]
                else:
                    self.euclidean_gates[i].notes_list = self.bjorklund(self.euclidean_gates[i].notes_para_final[0], 
                                                                        self.euclidean_gates[i].notes_para_final[1])
                # Add Offset
                self.euclidean_gates[i].notes_list = self.euclidean_gates[i].notes_list[self.euclidean_gates[i].notes_para_final[2]:] +\
                                                     self.euclidean_gates[i].notes_list[:self.euclidean_gates[i].notes_para_final[2]]

            # Draw and Change Outputs
            oled.fill(0)
            for i in range(6):
                # reset steps
                self.euclidean_gates[i].step_reset()

                # Change Outputs
                self.euclidean_gates[i].change_output()
                
                # Visualization
                if self.gate_idx <= 5:
                    # Box, and editing indicator
                    if self.gate_idx == i:
                        self.euclidean_gates[i].draw_para_indicator(self.para_idx)
                        # Draw Blinking Box
                        if self.blink_flg == 0:
                            self.euclidean_gates[i].draw_box()
                    else:
                        # Draw other Boxes
                        self.euclidean_gates[i].draw_box()
                    
                    if self.para_idx == 3 and self.gate_idx == i:
                        pass
                    else:
                        # Draw Notes
                        self.euclidean_gates[i].draw_notes()
                
                # Increase Step
                self.euclidean_gates[i].step_increase()
            
            # Turn off outputs
            sleep_ms(EUCLIDEAN_TRG_T)
            [o.off() for o in cvs]

            # Draw tempo setting
            self.draw_tempo_setting()
                    
            
            oled.show()
            self.wait()
                  
if __name__ == "__main__":
    euclidean_rhythm = EuclideanRhythm()
    euclidean_rhythm.main()