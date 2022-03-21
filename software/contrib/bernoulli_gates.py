from europi import *
from time import sleep_ms
from random import random
from europi_script import EuroPiScript
import machine

# Constant values for display
BAR_LEN = 50
BAR_WID = 6
INDI_WID = 5

# Trigger Time (some module may not be able to catch up the trigger if it is too short)
TRG_T = 20

# Overclock the Pico for improved performance.
machine.freq(250_000_000)

class SingleBernoulliGate():
    def __init__(self, id):
        self.mode_flg = 0 # mode 0: Trigger, mode 1: Gate, mode 2: Toggle
        self.coin = 0 # probability
        self.right_possibility = 0 # change every iteration
        self.left_possibility = 0
        self.right_possibility_sampled = 0 # only change when triggered
        self.left_possibility_sampled = 0
        self.id = id
        if self.id == 0:
            self.knob_control = k1
            self.text = 'P1'
            self.text_pos = (0, 0)
            self.text1_pos = 0
            self.bar_pos_offset = -3
            self.left_port = cv1
            self.right_port = cv2
            self.function_port = cv3
        else:
            self.knob_control = k2
            self.text = 'P2'
            self.text_pos = (int(OLED_WIDTH / 2) + 8, 0)
            self.text1_pos = 110
            self.bar_pos_offset = BAR_WID - 1
            self.left_port = cv4
            self.right_port = cv5
            self.function_port = cv6
        
    def get_prob(self):
        if self.id == 0:
            self.right_possibility = self.knob_control.percent() + ain.read_voltage()/12
            self.left_possibility = 1 - self.right_possibility
        else:
            self.right_possibility = self.knob_control.percent()
            self.left_possibility = 1 - self.right_possibility
            
    def bar_visualization(self):
        oled.text(self.text + f':{self.right_possibility:.2f}', self.text_pos[0], self.text_pos[1], 1)
        oled.rect(int(OLED_WIDTH / 2), 
                  int((OLED_HEIGHT - BAR_WID) / 2) + self.bar_pos_offset, 
                  int(self.right_possibility * BAR_LEN), 
                  BAR_WID, 1) # right
        oled.fill_rect(int(OLED_WIDTH / 2 - self.left_possibility * BAR_LEN), 
                       int((OLED_HEIGHT - BAR_WID) / 2) + self.bar_pos_offset, 
                       int(self.left_possibility * BAR_LEN), 
                       BAR_WID, 1) # left
                       
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
                    oled.fill_rect(int(OLED_WIDTH / 2 + self.right_possibility * BAR_LEN) + 2, 
                                   int((OLED_HEIGHT - BAR_WID) / 2) + self.bar_pos_offset, 
                                   INDI_WID, 
                                   BAR_WID, 1)
            else:
                self.left_port.on()
                self.right_port.off()
                if self.mode_flg == 0:
                    # Draw left indicator
                    oled.rect(int(OLED_WIDTH / 2 - self.left_possibility * BAR_LEN) - INDI_WID - 2, 
                              int((OLED_HEIGHT - BAR_WID) / 2) + self.bar_pos_offset, 
                              INDI_WID, 
                              BAR_WID, 1)
        else:
            if self.coin < (self.right_possibility_sampled):
                self.left_port.toggle()
                self.right_port.value(self.left_port._duty == 0)
                 
        if self.id == 1: self.function_port.value((cv1._duty and cv4._duty) != 0)

    def regular_maneuver(self):
        if self.mode_flg == 0:
            oled.text('Tr', self.text1_pos, OLED_HEIGHT-8, 1)
            sleep_ms(TRG_T)
            self.left_port.off()
            self.right_port.off()
            self.function_port.off()
        elif self.mode_flg == 1:
            oled.text('G', self.text1_pos, OLED_HEIGHT-8, 1)
            # Draw indicator
            if self.coin < (self.right_possibility_sampled):
                oled.fill_rect(int(OLED_WIDTH / 2 + self.right_possibility * BAR_LEN) + 2, 
                               int((OLED_HEIGHT - BAR_WID) / 2) + self.bar_pos_offset, 
                               INDI_WID, 
                               BAR_WID, 1)                
            else:
                oled.rect(int(OLED_WIDTH / 2 - self.left_possibility * BAR_LEN) - INDI_WID - 2, 
                          int((OLED_HEIGHT - BAR_WID) / 2) + self.bar_pos_offset, 
                          INDI_WID, 
                          BAR_WID, 1)   
            sleep_ms(TRG_T)
            if self.id == 0: self.function_port.off()
        elif self.mode_flg == 2:
            oled.text('Tg', self.text1_pos, OLED_HEIGHT-8, 1)
            sleep_ms(TRG_T)
            self.function_port.off()

class BernoulliGates(EuroPiScript):
    def __init__(self):
        self.toss_flg = 0
        self.first_gate = SingleBernoulliGate(0)
        self.second_gate = SingleBernoulliGate(1)

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
            self.first_gate.bar_visualization()
            self.second_gate.bar_visualization()
            
            # Triggered maneuver
            if self.toss_flg == 1:
                self.first_gate.probability_sample()
                self.second_gate.probability_sample()
                cv3.on()
                
                self.first_gate.triggered_maneuver()
                self.second_gate.triggered_maneuver()
                
                self.toss_flg = 0
                
            # Regular maneuver
            self.first_gate.regular_maneuver()
            self.second_gate.regular_maneuver()
                
            oled.show()
    
if __name__ == "__main__":
    # Number of sequential reads for smoothing analog read values.
    k1.set_samples(32)
    k2.set_samples(32)
    
    bernoulli_gates = BernoulliGates()
    bernoulli_gates.main()