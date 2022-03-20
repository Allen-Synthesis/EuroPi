from europi import *
from time import sleep_ms, ticks_ms, ticks_add, ticks_diff
import machine

# Internal clock tempo range.
MAX_BPM = 280
MIN_BPM = 20

def bjorklund(steps, pulses):
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

'''### for return back to menu
def app_back():
    global done
    print('long')
    oled.centre_text('App Select')
    done = 1
    sleep_ms(1500)
'''###

def reset_step():
    global steps_idx
    steps_idx = [0 for i in range(6)]

def para_add():
    global notes_para, selection_idx, editing_idx, clock_flg
    
    if selection_idx <= 5:
        if editing_idx == 0:
            notes_para[selection_idx][0] += 1 # length
        elif editing_idx == 1:
            notes_para[selection_idx][1] += 1 # fill
        elif editing_idx == 2:
            notes_para[selection_idx][2] += 1 # offset
        elif editing_idx == 3:
            notes_para[selection_idx][3] += 1 # CV
        
        # Bound
        if notes_para[selection_idx][0] > 19: notes_para[selection_idx][0] = 19
        if notes_para[selection_idx][0] < 1: notes_para[selection_idx][0] = 1
        if notes_para[selection_idx][1] > notes_para[selection_idx][0]: notes_para[selection_idx][1] = notes_para[selection_idx][0]
        if notes_para[selection_idx][1] < 1: notes_para[selection_idx][1] = 1
        if notes_para[selection_idx][2] > notes_para[selection_idx][0]: notes_para[selection_idx][2] = notes_para[selection_idx][0]
        if notes_para[selection_idx][2] < 0: notes_para[selection_idx][2] = 0
        if notes_para[selection_idx][3] > 3: notes_para[selection_idx][3] = 3
        if notes_para[selection_idx][3] < 0: notes_para[selection_idx][3] = 0
        print(selection_idx, notes_para[selection_idx])
    else:
        clock_flg = 1

def para_sub():
    global notes_para, selection_idx, editing_idx, clock_flg
    
    if selection_idx <= 5:
        if editing_idx == 0:
            notes_para[selection_idx][0] -= 1 # length
        elif editing_idx == 1:
            notes_para[selection_idx][1] -= 1 # fill
        elif editing_idx == 2:
            notes_para[selection_idx][2] -= 1 # offset
        elif editing_idx == 3:
            notes_para[selection_idx][3] -= 1 # CV
            
        # Bound
        if notes_para[selection_idx][0] > 19: notes_para[selection_idx][0] = 19
        if notes_para[selection_idx][0] < 1: notes_para[selection_idx][0] = 1
        if notes_para[selection_idx][1] > notes_para[selection_idx][0]: notes_para[selection_idx][1] = notes_para[selection_idx][0]
        if notes_para[selection_idx][1] < 1: notes_para[selection_idx][1] = 1
        if notes_para[selection_idx][2] > notes_para[selection_idx][0]: notes_para[selection_idx][2] = notes_para[selection_idx][0]
        if notes_para[selection_idx][2] < 0: notes_para[selection_idx][2] = 0
        if notes_para[selection_idx][3] > 3: notes_para[selection_idx][3] = 3
        if notes_para[selection_idx][3] < 0: notes_para[selection_idx][3] = 0
        print(selection_idx, notes_para[selection_idx])
    else:
        clock_flg = 0

def para_cv():
    global notes_para, notes_para_final, cv_value
    
    for i in range(6):
        if notes_para[i][3] == 1:
            notes_para_final[i][0] = notes_para[i][0] + cv_value
            notes_para_final[i][1] = notes_para[i][1]
            notes_para_final[i][2] = notes_para[i][2]
        elif notes_para[i][3] == 2:
            notes_para_final[i][0] = notes_para[i][0]
            notes_para_final[i][1] = notes_para[i][1] + cv_value
            notes_para_final[i][2] = notes_para[i][2]
        elif notes_para[i][3] == 3:
            notes_para_final[i][0] = notes_para[i][0]
            notes_para_final[i][1] = notes_para[i][1]
            notes_para_final[i][2] = notes_para[i][2] + cv_value
        else:
            notes_para_final[i][0] = notes_para[i][0]
            notes_para_final[i][1] = notes_para[i][1]
            notes_para_final[i][2] = notes_para[i][2]
            
        # Bound
        if notes_para_final[i][0] > 19: notes_para_final[i][0] = 19
        if notes_para_final[i][0] < 1: notes_para_final[i][0] = 1
        if notes_para_final[i][1] > notes_para_final[i][0]: notes_para_final[i][1] = notes_para_final[i][0]
        if notes_para_final[i][1] < 1: notes_para_final[i][1] = 1
        if notes_para_final[i][2] > notes_para_final[i][0]: notes_para_final[i][2] = notes_para_final[i][0]
        if notes_para_final[i][2] < 0: notes_para_final[i][2] = 0

class notes_plot():
    global box_position, box_size, selection_idx, blink_flg
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

# Small dot indicators shown current editing parameter
def draw_editing_idx(selection_idx, editing_idx, cv_idx):
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

def get_next_deadline():
    global clock_flg, tempo

    # The duration of a quarter note in ms for the current tempo.
    wait_ms = int(60 / tempo / 4 * 1000)
    return ticks_add(ticks_ms(), wait_ms)

def wait():
    global clock_flg, deadline, prev_clock
    if clock_flg == 0:
        while True:
            if ticks_diff(deadline, ticks_ms()) <= 0:
                deadline = get_next_deadline()
                return
    else:  # External clock
        # Loop until digital in goes high (clock pulse received).
        while clock_flg == 1:
            if din.value() != prev_clock:
                prev_clock = 1 if prev_clock == 0 else 0
                if prev_clock == 0:
                    return

def init():
    global box_position, box_size, notes_para, notes_para_final, selection_idx, editing_idx, blink_flg, steps_idx, clock_flg, tempo, deadline, prev_clock, cv_value
    
    # Overclock the Pico for improved performance.
    machine.freq(250_000_000)
    
    # Button IRQ
    b1.handler_falling(para_sub)
    b1.handler_long(reset_step)
    b2.handler_falling(para_add)
    
    # Number of sequential reads for smoothing analog read values.
    k1.set_samples(32)
    k2.set_samples(32)
    
    # BBox positions
    box_position = [[0, 0],
                    [int(OLED_WIDTH/3), 0],
                    [int(OLED_WIDTH/3*2), 0],
                    [0, int(OLED_HEIGHT/2)],
                    [int(OLED_WIDTH/3), int(OLED_HEIGHT/2)],
                    [int(OLED_WIDTH/3*2), int(OLED_HEIGHT/2)]]
    box_size = [int(OLED_WIDTH/3), int(OLED_HEIGHT/2)]

    # length, fill, offset, cv
    notes_para = [[1, 1, 0, 0], [1, 1, 0, 0], [1, 1, 0, 0],
                  [1, 1, 0, 0], [1, 1, 0, 0], [1, 1, 0, 0]]
    
    # length, fill, offset
    notes_para_final = [[1, 1, 0], [1, 1, 0], [1, 1, 0],
                  [1, 1, 0], [1, 1, 0], [1, 1, 0]]
    
    # Visualization parameters
    bar_length_on = 8
    bar_length_off = 2
    
    editing_idx = 0 # change editing parameters
    blink_flg = 0 # blink selection with tempo
    clock_flg = 0 # 0: internal clock, 1: external clock (from digital in)
    steps_idx = [0 for i in range(6)] # step of each sequencer
    tempo = 60 # current tempo
    deadline = 0  # internal clock parameter
    prev_clock = 0 # external clock parameter
    cv_value = 0

def run():
    global box_position, box_size, notes_para, notes_para_final, selection_idx, editing_idx, blink_flg, steps_idx, clock_flg, tempo, cv_value#, done
    
    '''### for return back to menu
    b2.handler_long(app_back)
    done = 0
    '''###
    
    init()
    while True:
        '''### for return back to menu
        if done == 1:
            print('Return')
            return 0
        '''###
        
        cv_value = int(ain.read_voltage())
        selection_idx = k2.choice([i for i in range(7)])
        if selection_idx <= 5:
            editing_idx = k1.choice([i for i in range(4)]) # length, fill, offset, cv
        else:
            tempo = round(k1.read_position(MAX_BPM - MIN_BPM) + MIN_BPM)
        
        blink_flg += 1
        if blink_flg > 3:
            blink_flg = 0
        
        # Set CV controled parameters
        para_cv()
        #print(steps_idx[0])
        #print(notes_para[0])
        #print(notes_para_final[0], '\n')
        
        # Generate Euclidean Notes
        notes_list = [bjorklund(notes_para_final[i][0], notes_para_final[i][1]) for i in range(6)]
        
        # Add Offset
        for i in range(6):
            notes_list[i] = notes_list[i][notes_para_final[i][2]:] + notes_list[i][:notes_para_final[i][2]]

        # Instantiate notes_plot
        notes_plot_list = [notes_plot(i, notes_list[i]) for i in range(6)]
        
        # Draw and Change Outputs
        oled.fill(0)
        print
        for i in range(6):
            if steps_idx[i] >= notes_para_final[i][0]:
                steps_idx[i] = 0
            # Change Outputs
            if notes_list[i][steps_idx[i]] == 1:
                cvs[i].on()
            else:
                cvs[i].off()
            sleep_ms(10)
            [o.off() for o in cvs]
            
            if selection_idx <= 5:
                # Box, and editing indicator
                if selection_idx == i:
                    draw_editing_idx(i, editing_idx, notes_para[i][3])
                    # Draw Blink Box
                    if blink_flg == 0:
                        oled.rect(box_position[i][0], box_position[i][1], box_size[0], box_size[1], 1)
                else:
                    # Draw other Boxes
                    oled.rect(box_position[i][0], box_position[i][1], box_size[0], box_size[1], 1)
                
                if editing_idx == 3 and selection_idx == i:
                    pass
                else:
                    # Draw Notes
                    notes_plot_list[i].draw_notes(steps_idx[i])
            
            # Increase Step
            steps_idx[i] += 1
            if steps_idx[i] == notes_para_final[i][0]:
                steps_idx[i] = 0
        
        # Draw tempo setting
        if selection_idx == 6:
            oled.text(str(tempo), 8, 12, 1)
            oled.text('Ext', int(OLED_WIDTH/2) + 8, 12, 1)
            
            if clock_flg == 0 and blink_flg == 0:
                oled.rect(5, 7, 33, 20, 1)
            if clock_flg == 1 and blink_flg == 0:
                oled.rect(int(OLED_WIDTH/2) + 5, 7, 33, 20, 1)
                
        
        oled.show()
        wait()
         
if __name__ == "__main__":
    run()


