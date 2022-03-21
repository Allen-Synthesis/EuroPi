from europi import *
from time import sleep_ms, ticks_ms, ticks_add, ticks_diff
from europi_script import EuroPiScript
import machine

# Internal clock tempo range.
MAX_BPM = 280
MIN_BPM = 20

# Constant values for display.
box_position = [[0, 0],
                    [int(OLED_WIDTH/3), 0],
                    [int(OLED_WIDTH/3*2), 0],
                    [0, int(OLED_HEIGHT/2)],
                    [int(OLED_WIDTH/3), int(OLED_HEIGHT/2)],
                    [int(OLED_WIDTH/3*2), int(OLED_HEIGHT/2)]]
box_size = [int(OLED_WIDTH/3), int(OLED_HEIGHT/2)]
bar_length_on = 8
bar_length_off = 2

# Overclock the Pico for improved performance.
machine.freq(250_000_000)

class NotesPlot():
    def __init__(self, position, notes_list):
        self.position = position
        self.notes_list = notes_list
        
    def draw_notes(self, step):
        for i in range(len(self.notes_list)):
            # blink
            if i != step:
                # High
                if self.notes_list[i] == 1:
                    if len(self.notes_list) < 10:
                        oled.fill_rect(box_position[self.position][0]+2+i*4, box_position[self.position][1]+5, 3, box_size[1]-5, 1)
                    elif len(self.notes_list) < 14:
                        oled.fill_rect(box_position[self.position][0]+2+i*3, box_position[self.position][1]+5, 2, box_size[1]-5, 1)
                    elif len(self.notes_list) < 20:
                        oled.fill_rect(box_position[self.position][0]+2+i*2, box_position[self.position][1]+5, 1, box_size[1]-5, 1)
                # Low
                else:
                    if len(self.notes_list) < 10:
                        oled.fill_rect(box_position[self.position][0]+2+i*4, box_position[self.position][1]+12, 3, box_size[1]-12, 1)
                    elif len(self.notes_list) < 14:
                        oled.fill_rect(box_position[self.position][0]+2+i*3, box_position[self.position][1]+12, 2, box_size[1]-12, 1)
                    elif len(self.notes_list) < 20:
                        oled.fill_rect(box_position[self.position][0]+2+i*2, box_position[self.position][1]+12, 1, box_size[1]-12, 1)
            else:
                # High
                if self.notes_list[i] == 1:
                    if len(self.notes_list) < 10:
                        oled.fill_rect(box_position[self.position][0]+2+i*4, box_position[self.position][1]+8, 3, box_size[1]-8, 1)
                        oled.fill_rect(box_position[self.position][0]+2+i*4, box_position[self.position][1]+5, 3, 2, 1)
                    elif len(self.notes_list) < 14:
                        oled.fill_rect(box_position[self.position][0]+2+i*3, box_position[self.position][1]+8, 2, box_size[1]-8, 1)
                        oled.fill_rect(box_position[self.position][0]+2+i*3, box_position[self.position][1]+5, 2, 2, 1)
                    elif len(self.notes_list) < 20:
                        oled.fill_rect(box_position[self.position][0]+2+i*2, box_position[self.position][1]+8, 1, box_size[1]-8, 1)
                        oled.fill_rect(box_position[self.position][0]+2+i*2, box_position[self.position][1]+5, 1, 2, 1)
                # Low
                else:
                    if len(self.notes_list) < 10:
                        oled.fill_rect(box_position[self.position][0]+2+i*4, box_position[self.position][1]+15, 3, box_size[1]-15, 1)
                        oled.fill_rect(box_position[self.position][0]+2+i*4, box_position[self.position][1]+12, 3, 2, 1)
                    elif len(self.notes_list) < 14:
                        oled.fill_rect(box_position[self.position][0]+2+i*3, box_position[self.position][1]+15, 2, box_size[1]-15, 1)
                        oled.fill_rect(box_position[self.position][0]+2+i*3, box_position[self.position][1]+12, 2, 2, 1)
                    elif len(self.notes_list) < 20:
                        oled.fill_rect(box_position[self.position][0]+2+i*2, box_position[self.position][1]+15, 1, box_size[1]-15, 1)
                        oled.fill_rect(box_position[self.position][0]+2+i*2, box_position[self.position][1]+12, 1, 2, 1)

class EuclideanRhythm(EuroPiScript):
    def __init__(self):
        # length, fill, offset, cv
        self.notes_para = [[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0],
                           [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]]
        
        # length, fill, offset
        self.notes_para_final = [[1, 0, 0], [1, 0, 0], [1, 0, 0],
                                 [1, 0, 0], [1, 0, 0], [1, 0, 0]]

        
        self.selection_idx = 0 # change editing gates
        self.editing_idx = 0 # change editing parameters
        self.blink_flg = 0 # blink selection with tempo
        self.clock_flg = 0 # 0: internal clock, 1: external clock (from digital in)
        self.steps_idx = [0 for i in range(6)] # step of each sequencer
        self.tempo = 60 # current tempo
        self.deadline = 0  # internal clock parameter
        self.prev_clock = 0 # external clock parameter
        self.cv_value = 0

        @b1.handler_falling
        def para_sub():
            if self.selection_idx <= 5:
                if self.editing_idx == 0:
                    self.notes_para[self.selection_idx][0] -= 1 # length
                elif self.editing_idx == 1:
                    self.notes_para[self.selection_idx][1] -= 1 # fill
                elif self.editing_idx == 2:
                    self.notes_para[self.selection_idx][2] -= 1 # offset
                elif self.editing_idx == 3:
                    self.notes_para[self.selection_idx][3] -= 1 # CV
                    
                # Bound
                if self.notes_para[self.selection_idx][0] > 19: self.notes_para[self.selection_idx][0] = 19
                if self.notes_para[self.selection_idx][0] < 1: self.notes_para[self.selection_idx][0] = 1
                if self.notes_para[self.selection_idx][1] > self.notes_para[self.selection_idx][0]: self.notes_para[self.selection_idx][1] = self.notes_para[self.selection_idx][0]
                if self.notes_para[self.selection_idx][0] > 1:
                    if self.notes_para[self.selection_idx][1] < 1: self.notes_para[self.selection_idx][1] = 1
                else:
                    if self.notes_para[self.selection_idx][1] < 0: self.notes_para[self.selection_idx][1] = 0
                if self.notes_para[self.selection_idx][2] > self.notes_para[self.selection_idx][0]: self.notes_para[self.selection_idx][2] = self.notes_para[self.selection_idx][0]
                if self.notes_para[self.selection_idx][2] < 0: self.notes_para[self.selection_idx][2] = 0
                if self.notes_para[self.selection_idx][3] > 3: self.notes_para[self.selection_idx][3] = 3
                if self.notes_para[self.selection_idx][3] < 0: self.notes_para[self.selection_idx][3] = 0
                #print(self.selection_idx, self.notes_para[self.selection_idx])
            else:
                self.clock_flg = 0
        
        @b2.handler_falling
        def para_add():
            if self.selection_idx <= 5:
                if self.editing_idx == 0:
                    self.notes_para[self.selection_idx][0] += 1 # length
                elif self.editing_idx == 1:
                    self.notes_para[self.selection_idx][1] += 1 # fill
                elif self.editing_idx == 2:
                    self.notes_para[self.selection_idx][2] += 1 # offset
                elif self.editing_idx == 3:
                    self.notes_para[self.selection_idx][3] += 1 # CV
                
                # Bound
                if self.notes_para[self.selection_idx][0] > 19: self.notes_para[self.selection_idx][0] = 19
                if self.notes_para[self.selection_idx][0] < 1: self.notes_para[self.selection_idx][0] = 1
                if self.notes_para[self.selection_idx][1] > self.notes_para[self.selection_idx][0]: self.notes_para[self.selection_idx][1] = self.notes_para[self.selection_idx][0]
                if self.notes_para[self.selection_idx][0] > 1:
                    if self.notes_para[self.selection_idx][1] < 1: self.notes_para[self.selection_idx][1] = 1
                else:
                    if self.notes_para[self.selection_idx][1] < 0: self.notes_para[self.selection_idx][1] = 0
                if self.notes_para[self.selection_idx][2] > self.notes_para[self.selection_idx][0]: self.notes_para[self.selection_idx][2] = self.notes_para[self.selection_idx][0]
                if self.notes_para[self.selection_idx][2] < 0: self.notes_para[self.selection_idx][2] = 0
                if self.notes_para[self.selection_idx][3] > 3: self.notes_para[self.selection_idx][3] = 3
                if self.notes_para[self.selection_idx][3] < 0: self.notes_para[self.selection_idx][3] = 0
                #print(self.selection_idx, self.notes_para[self.selection_idx])
            else:
                self.clock_flg = 1

    def bjorklund(self, steps, pulses):
        steps = int(steps)
        pulses = int(pulses)
        
        if pulses > steps:
            raise ValueError    
        
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

    # Small dot indicators shown current editing parameter
    def draw_editing_idx(self, selection_idx, editing_idx, cv_idx):
        if editing_idx == 0:
            oled.fill_rect(box_position[selection_idx][0]+29, box_position[selection_idx][1]+1, 2, 2, 1)
        if editing_idx == 1:
            oled.fill_rect(box_position[selection_idx][0]+29, box_position[selection_idx][1]+1, 2, 2, 1)
            oled.fill_rect(box_position[selection_idx][0]+32, box_position[selection_idx][1]+1, 2, 2, 1)
        if editing_idx == 2:
            oled.fill_rect(box_position[selection_idx][0]+29, box_position[selection_idx][1]+1, 2, 2, 1)
            oled.fill_rect(box_position[selection_idx][0]+32, box_position[selection_idx][1]+1, 2, 2, 1)
            oled.fill_rect(box_position[selection_idx][0]+35, box_position[selection_idx][1]+1, 2, 2, 1)
        if editing_idx == 3:
            oled.fill_rect(box_position[selection_idx][0]+29, box_position[selection_idx][1]+1, 2, 2, 1)
            oled.fill_rect(box_position[selection_idx][0]+32, box_position[selection_idx][1]+1, 2, 2, 1)
            oled.fill_rect(box_position[selection_idx][0]+35, box_position[selection_idx][1]+1, 2, 2, 1)
            oled.fill_rect(box_position[selection_idx][0]+38, box_position[selection_idx][1]+1, 2, 2, 1)
            if cv_idx == 0:
                oled.text('-', box_position[selection_idx][0]+16, box_position[selection_idx][1]+6, 1)
            elif cv_idx == 1:
                oled.text('L', box_position[selection_idx][0]+16, box_position[selection_idx][1]+6, 1)
            elif cv_idx == 2:
                oled.text('F', box_position[selection_idx][0]+16, box_position[selection_idx][1]+6, 1)
            elif cv_idx == 3:
                oled.text('O', box_position[selection_idx][0]+16, box_position[selection_idx][1]+6, 1)

    def get_next_deadline(self):
        # The duration of a quarter note in ms for the current tempo.
        wait_ms = int(60 / self.tempo / 4 * 1000)
        return ticks_add(ticks_ms(), wait_ms)

    def wait(self):
        if self.clock_flg == 0:
            while True:
                if ticks_diff(self.deadline, ticks_ms()) <= 0:
                    self.deadline = self.get_next_deadline()
                    return
        else:  # External clock
            # Loop until digital in goes high (clock pulse received).
            while self.clock_flg == 1:
                if din.value() != self.prev_clock:
                    self.prev_clock = 1 if self.prev_clock == 0 else 0
                    if self.prev_clock == 0:
                        return

    def para_cv(self):
        for i in range(6):
            if self.notes_para[i][3] == 1:
                self.notes_para_final[i][0] = self.notes_para[i][0] + self.cv_value
                self.notes_para_final[i][1] = self.notes_para[i][1]
                self.notes_para_final[i][2] = self.notes_para[i][2]
            elif self.notes_para[i][3] == 2:
                self.notes_para_final[i][0] = self.notes_para[i][0]
                self.notes_para_final[i][1] = self.notes_para[i][1] + self.cv_value
                self.notes_para_final[i][2] = self.notes_para[i][2]
            elif self.notes_para[i][3] == 3:
                self.notes_para_final[i][0] = self.notes_para[i][0]
                self.notes_para_final[i][1] = self.notes_para[i][1]
                self.notes_para_final[i][2] = self.notes_para[i][2] + self.cv_value
            else:
                self.notes_para_final[i][0] = self.notes_para[i][0]
                self.notes_para_final[i][1] = self.notes_para[i][1]
                self.notes_para_final[i][2] = self.notes_para[i][2]
                
            # Bound (LFO)
            if self.notes_para_final[i][0] > 19: self.notes_para_final[i][0] = 19
            if self.notes_para_final[i][0] < 1: self.notes_para_final[i][0] = 1
            if self.notes_para_final[i][1] > self.notes_para_final[i][0]: self.notes_para_final[i][1] = self.notes_para_final[i][0]
            if self.notes_para_final[i][0] > 1:
                if self.notes_para_final[i][1] < 1: self.notes_para_final[i][1] = 1
            else:
                if self.notes_para_final[i][1] < 0: self.notes_para_final[i][1] = 0
            if self.notes_para_final[i][2] > self.notes_para_final[i][0]: self.notes_para_final[i][2] = self.notes_para_final[i][0]
            if self.notes_para_final[i][2] < 0: self.notes_para_final[i][2] = 0

    def main(self):
        while True:
            self.cv_value = int(ain.read_voltage())
            
            self.selection_idx = k2.choice([i for i in range(7)])
            if self.selection_idx <= 5: # gate selection mode
                self.editing_idx = k1.choice([i for i in range(4)]) # length, fill, offset, cv
            else: # clock editing mode
                self.tempo = round(k1.read_position(MAX_BPM - MIN_BPM) + MIN_BPM)
            
            self.blink_flg += 1
            if self.clock_flg == 0:
                # blink every four note
                if self.blink_flg > 3:
                    self.blink_flg = 0
            else:
                if self.blink_flg > 1:
                    self.blink_flg = 0
            
            # Set CV controled parameters
            self.para_cv()
            
            # Generate Euclidean Notes
            notes_list = []
            for i in range(6):
                if self.notes_para_final[i][1] == 0:
                    notes_list.append([0, ])
                else:
                    notes_list.append(self.bjorklund(self.notes_para_final[i][0], self.notes_para_final[i][1]))
                # Add Offset
                notes_list[i] = notes_list[i][self.notes_para_final[i][2]:] + notes_list[i][:self.notes_para_final[i][2]]
 
            # Instantiate NotesPlot
            notes_plot_list = [NotesPlot(i, notes_list[i]) for i in range(6)]
            
            # Draw and Change Outputs
            oled.fill(0)
            for i in range(6):
                # reset steps
                if self.steps_idx[i] >= self.notes_para_final[i][0]:
                    self.steps_idx[i] = 0

                # Change Outputs
                if notes_list[i][self.steps_idx[i]] == 1:
                    cvs[i].on()
                else:
                    cvs[i].off()
                sleep_ms(10)
                [o.off() for o in cvs]
                
                if self.selection_idx <= 5:
                    # Box, and editing indicator
                    if self.selection_idx == i:
                        self.draw_editing_idx(i, self.editing_idx, self.notes_para[i][3])
                        # Draw Blink Box
                        if self.blink_flg == 0:
                            oled.rect(box_position[i][0], box_position[i][1], box_size[0], box_size[1], 1)
                    else:
                        # Draw other Boxes
                        oled.rect(box_position[i][0], box_position[i][1], box_size[0], box_size[1], 1)
                    
                    if self.editing_idx == 3 and self.selection_idx == i:
                        pass
                    else:
                        # Draw Notes
                        notes_plot_list[i].draw_notes(self.steps_idx[i])
                
                # Increase Step
                self.steps_idx[i] += 1
                if self.steps_idx[i] == self.notes_para_final[i][0]:
                    self.steps_idx[i] = 0
            
            # Draw tempo setting
            if self.selection_idx == 6:
                oled.text(str(self.tempo), 8, 12, 1)
                oled.text('Ext', int(OLED_WIDTH/2) + 8, 12, 1)
                
                if self.clock_flg == 0 and self.blink_flg == 0:
                    oled.rect(5, 7, 33, 20, 1)
                if self.clock_flg == 1 and self.blink_flg == 0:
                    oled.rect(int(OLED_WIDTH/2) + 5, 7, 33, 20, 1)
                    
            
            oled.show()
            self.wait()
    
                    
if __name__ == "__main__":
    # Number of sequential reads for smoothing analog read values.
    k1.set_samples(32)
    k2.set_samples(32)

    euclidean_rhythm = EuclideanRhythm()
    euclidean_rhythm.main()