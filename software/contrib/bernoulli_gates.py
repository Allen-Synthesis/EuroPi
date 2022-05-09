from europi import *
from time import sleep_ms
from random import random
from europi_script import EuroPiScript
import machine

# Constant values for display
BERNOULLI_BAR_LEN = 50
BERNOULLI_BAR_WID = 6
BERNOULLI_INDI_WID = 5

# Trigger Time (some module may not be able to catch up the trigger if it is too short)
BERNOULLI_TRG_T = 20

class SingleBernoulliGate():
    def __init__(self, control_knob =  k1, control_port = ain, out_port = (cv1, cv2, cv3), visualization_para = ('P1', (0, 0), 0, -3), port3_func = 'clock', port3_source_cv = None):
        '''
        1. control_knob and control_port tunes the probability threshold
        if control_port == None, probability threshold is only determined by control_knob
        2. out_port assigns left, right, and function port accordingly
        out_port shoud have at least 2 ports (port3_func == 'none')
        3. visualization_para = (text, text_pos, tex1_pos, bar_pos_offset)
        4. port3_func and port3_source_cv determine the function of port3,
        where port3_func can be 'none', 'clock', 'and', 'or', 'xor',
        and port3_source_cv can be None or any other output port
        the output of function_port = logic(current left, source), or clock(trigger)
        '''
        self.mode_flg = 0 # mode 0: Trigger, mode 1: Gate, mode 2: Toggle
        self.coin = 0 # probability
        self.right_possibility = 0 # change every iteration
        self.left_possibility = 0
        self.right_possibility_sampled = 0 # only change when triggered
        self.left_possibility_sampled = 0

        self.port3_func = port3_func
        self.port3_source_cv = port3_source_cv

        self.control_knob = control_knob
        self.control_port = control_port

        self.left_port = out_port[0]
        self.right_port = out_port[1]
        if port3_func != 'none':
            self.function_port = out_port[2]

        self.text = visualization_para[0]
        self.text_pos = visualization_para[1]
        self.text1_pos = visualization_para[2]
        self.bar_pos_offset = visualization_para[3]

    def get_prob(self):
        if self.control_port:
            self.right_possibility = self.control_knob.percent() + self.control_port.read_voltage()/12
            self.left_possibility = 1 - self.right_possibility
        else:
            self.right_possibility = self.control_knob.percent()
            self.left_possibility = 1 - self.right_possibility

    def probability_text_visualization(self):
        oled.text(self.text + f':{self.right_possibility:.2f}', self.text_pos[0], self.text_pos[1], 1)

    def bar_visualization(self):
        # right
        oled.rect(int(OLED_WIDTH / 2), 
                  int((OLED_HEIGHT - BERNOULLI_BAR_WID) / 2) + self.bar_pos_offset, 
                  int(self.right_possibility * BERNOULLI_BAR_LEN), 
                  BERNOULLI_BAR_WID, 1)
        # left
        oled.fill_rect(int(OLED_WIDTH / 2 - self.left_possibility * BERNOULLI_BAR_LEN), 
                       int((OLED_HEIGHT - BERNOULLI_BAR_WID) / 2) + self.bar_pos_offset, 
                       int(self.left_possibility * BERNOULLI_BAR_LEN), 
                       BERNOULLI_BAR_WID, 1)
                       
    def probability_sample(self):
        self.right_possibility_sampled = self.right_possibility
        self.left_possibility_sampled = self.left_possibility
    
    def triggered_maneuver(self):
        self.coin = random()
        if self.mode_flg == 0 or self.mode_flg == 1:
            if self.coin < (self.right_possibility_sampled):
                self.left_port.off()
                self.right_port.on()
                if self.mode_flg == 0:
                    # Draw right indicator
                    oled.fill_rect(int(OLED_WIDTH / 2 + self.right_possibility * BERNOULLI_BAR_LEN) + 2, 
                                   int((OLED_HEIGHT - BERNOULLI_BAR_WID) / 2) + self.bar_pos_offset, 
                                   BERNOULLI_INDI_WID, 
                                   BERNOULLI_BAR_WID, 1)
            else:
                self.left_port.on()
                self.right_port.off()
                if self.mode_flg == 0:
                    # Draw left indicator
                    oled.rect(int(OLED_WIDTH / 2 - self.left_possibility * BERNOULLI_BAR_LEN) - BERNOULLI_INDI_WID - 2, 
                              int((OLED_HEIGHT - BERNOULLI_BAR_WID) / 2) + self.bar_pos_offset, 
                              BERNOULLI_INDI_WID, 
                              BERNOULLI_BAR_WID, 1)
        else:
            if self.coin < (self.right_possibility_sampled):
                self.left_port.toggle()
                self.right_port.value(self.left_port._duty == 0)

    def function_port_maneuver(self):
        if self.port3_func == 'none':
            pass
        elif self.port3_func == 'clock':
            self.function_port.on()
        else:
            if self.port3_func == 'and':
                self.function_port.value((self.port3_source_cv._duty and self.left_port._duty) != 0)
            elif self.port3_func == 'or':
                self.function_port.value((self.port3_source_cv._duty or self.left_port._duty) != 0)
            elif self.port3_func == 'xor':
                self.function_port.value((self.port3_source_cv._duty ^ self.left_port._duty) != 0)
            else:
                self.function_port.off()

    def regular_visualization(self):
        if self.mode_flg == 0:
            oled.text('Tr', self.text1_pos, OLED_HEIGHT-8, 1)
        elif self.mode_flg == 1:
            oled.text('G', self.text1_pos, OLED_HEIGHT-8, 1)
            # Draw indicator
            if self.coin < (self.right_possibility_sampled):
                oled.fill_rect(int(OLED_WIDTH / 2 + self.right_possibility * BERNOULLI_BAR_LEN) + 2, 
                               int((OLED_HEIGHT - BERNOULLI_BAR_WID) / 2) + self.bar_pos_offset, 
                               BERNOULLI_INDI_WID, 
                               BERNOULLI_BAR_WID, 1)                
            else:
                oled.rect(int(OLED_WIDTH / 2 - self.left_possibility * BERNOULLI_BAR_LEN) - BERNOULLI_INDI_WID - 2, 
                          int((OLED_HEIGHT - BERNOULLI_BAR_WID) / 2) + self.bar_pos_offset, 
                          BERNOULLI_INDI_WID, 
                          BERNOULLI_BAR_WID, 1)
        elif self.mode_flg == 2:
            oled.text('Tg', self.text1_pos, OLED_HEIGHT-8, 1)

    def regular_maneuver(self):
        if self.mode_flg == 0:
            self.left_port.off()
            self.right_port.off()
            if self.port3_func != 'none':
                self.function_port.off()
        elif self.mode_flg == 1:
            if self.port3_func == 'clock':
                self.function_port.off()
            else:
                pass
        elif self.mode_flg == 2:
            if self.port3_func == 'none':
                pass
            else:
                self.function_port.off()

class BernoulliGates(EuroPiScript):
    def __init__(self):
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)

        self.toss_flg = 0
        self.first_gate = SingleBernoulliGate(control_knob =  k1,
                                              control_port = ain,
                                              out_port = (cv1, cv2, cv3),
                                              visualization_para = ('P1', (0, 0), 0, -3),
                                              port3_func = 'clock', port3_source_cv = None)
        self.second_gate = SingleBernoulliGate(control_knob =  k2, 
                                               control_port = None, 
                                               out_port = (cv4, cv5, cv6), 
                                               visualization_para = ('P2', (int(OLED_WIDTH / 2) + 8, 0), 110, BERNOULLI_BAR_WID - 1), 
                                               port3_func = 'and', port3_source_cv = cv1)

        @din.handler
        def digital_trigger():
            self.toss_flg = 1

        @b1.handler
        def mode_switch_1():
            self.first_gate.mode_flg += 1
            if self.first_gate.mode_flg == 3:
                self.first_gate.mode_flg = 0

        @b2.handler
        def mode_switch_2():
            self.second_gate.mode_flg += 1
            if self.second_gate.mode_flg == 3:
                self.second_gate.mode_flg = 0

    def main(self):
        while True:
            # Get Possibility
            self.first_gate.get_prob()
            self.second_gate.get_prob()

            # OLED Show Possibility Bar
            oled.fill(0)
            self.first_gate.probability_text_visualization()
            self.second_gate.probability_text_visualization()
            self.first_gate.bar_visualization()
            self.second_gate.bar_visualization()
            
            # Triggered maneuver
            if self.toss_flg == 1:
                self.first_gate.probability_sample()
                self.second_gate.probability_sample()
                
                self.first_gate.triggered_maneuver()
                self.second_gate.triggered_maneuver()
                
                self.first_gate.function_port_maneuver()
                self.second_gate.function_port_maneuver()
                
                self.toss_flg = 0
                
            # Regular maneuver
            self.first_gate.regular_visualization()
            self.second_gate.regular_visualization()
            sleep_ms(BERNOULLI_TRG_T)
            self.first_gate.regular_maneuver()
            self.second_gate.regular_maneuver()
            oled.show()
    
if __name__ == "__main__":    
    bernoulli_gates = BernoulliGates()
    bernoulli_gates.main()