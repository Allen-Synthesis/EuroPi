from europi import *
from time import sleep_ms
from random import random
from europi_script import EuroPiScript
import machine

'''
03/13 first version finished
03/17 fixed undefined coin and sampled probability if not receiving trigger and change mode
03/20 change the code structure to cooperate with the new menu function
'''

# Constant values for display
BAR_LEN = 50
BAR_WID = 6
INDI_WID = 5

# Trigger Time (some module may not be able to catch up the trigger if it is too short)
TRG_T = 20

# Number of sequential reads for smoothing analog read values.
k1.set_samples(32)
k2.set_samples(32)

# Overclock the Pico for improved performance.
machine.freq(250_000_000)

class BernoulliGates(EuroPiScript):
    def __init__(self):
        self.toss_flg = 0
        self.mode_flg_1 = 0 # First gate: (mode 0: Trigger, mode 1: Gate, mode 2: Toggle)
        self.mode_flg_2 = 0 # Second gate
        self.coin_1 = 0
        self.coin_2 = 0
        self.right_possibility_1_sampled = 0
        self.left_possibility_1_sampled = 0
        self.right_possibility_2_sampled = 0
        self.left_possibility_2_sampled = 0

        @din.handler
        def digital_trigger():
            self.toss_flg = 1

        @b1.handler
        def mode_switch_1():
            self.mode_flg_1 += 1
            if self.mode_flg_1 == 3:
                self.mode_flg_1 = 0

        @b2.handler
        def mode_switch_2():
            self.mode_flg_2 += 1
            if self.mode_flg_2 == 3:
                self.mode_flg_2 = 0

    def main(self):
        while True:
            # Get Possibility
            right_possibility_1 = k1.percent() + ain.read_voltage()/12
            left_possibility_1 = 1 - right_possibility_1
            
            right_possibility_2 = k2.percent()
            left_possibility_2 = 1 - right_possibility_2

            # OLED Show Possibility Bar
            oled.fill(0)
            # First Gate
            oled.text(f"P1:{right_possibility_1:.2f}", 0, 0, 1)
            oled.rect(int(OLED_WIDTH / 2), 
                        int((OLED_HEIGHT - BAR_WID) / 2) - 3, 
                        int(right_possibility_1 * BAR_LEN), 
                        BAR_WID, 1) # right
            oled.fill_rect(int(OLED_WIDTH / 2 - left_possibility_1 * BAR_LEN), 
                        int((OLED_HEIGHT - BAR_WID) / 2) - 3, 
                        int(left_possibility_1 * BAR_LEN), 
                        BAR_WID, 1) # left
            # Second Gate
            oled.text(f"P2:{right_possibility_2:.2f}", int(OLED_WIDTH / 2) + 8, 0, 1)
            oled.rect(int(OLED_WIDTH / 2), 
                    int((OLED_HEIGHT - BAR_WID) / 2) + BAR_WID - 1, 
                    int(right_possibility_2 * BAR_LEN), 
                    BAR_WID, 1) # right
            oled.fill_rect(int(OLED_WIDTH / 2 - left_possibility_2 * BAR_LEN), 
                        int((OLED_HEIGHT - BAR_WID) / 2) + BAR_WID - 1, 
                        int(left_possibility_2 * BAR_LEN), 
                        BAR_WID, 1) # left
            
            # Triggered
            if self.toss_flg == 1:
                self.right_possibility_1_sampled = right_possibility_1
                self.left_possibility_1_sampled = left_possibility_1
                self.right_possibility_2_sampled = right_possibility_2
                self.left_possibility_2_sampled = left_possibility_2
                cv3.on()

                ################ coin 1 #################
                self.coin_1 = random()
                if self.mode_flg_1 == 0 or self.mode_flg_1 == 1:
                    if self.coin_1 < (self.right_possibility_1_sampled):
                        cv1.off() 
                        cv2.on()
                        if self.mode_flg_1 == 0: 
                            oled.fill_rect(int(OLED_WIDTH / 2 + right_possibility_1 * BAR_LEN) + 2, 
                                        int((OLED_HEIGHT - BAR_WID) / 2) - 3, 
                                        INDI_WID, 
                                        BAR_WID, 1)               
                    else:
                        cv2.off()
                        cv1.on()
                        if self.mode_flg_1 == 0: 
                            oled.rect(int(OLED_WIDTH / 2 - left_possibility_1 * BAR_LEN) - INDI_WID - 2, 
                                        int((OLED_HEIGHT - BAR_WID) / 2) - 3, 
                                        INDI_WID, 
                                        BAR_WID, 1)
                else:
                    if self.coin_1 < (self.right_possibility_1_sampled):
                        cv1.toggle()
                        cv2.value(cv1._duty == 0)
                        
                ################ coin 2 #################
                self.coin_2 = random()
                if self.mode_flg_2 == 0 or self.mode_flg_2 == 1:
                    if self.coin_2 < (self.right_possibility_2_sampled):
                        cv4.off() 
                        cv5.on()
                        if self.mode_flg_2 == 0: 
                            oled.fill_rect(int(OLED_WIDTH / 2 + right_possibility_2 * BAR_LEN) + 2, 
                                        int((OLED_HEIGHT - BAR_WID) / 2)  + BAR_WID - 1, 
                                        INDI_WID, 
                                        BAR_WID, 1)               
                    else:
                        cv5.off()
                        cv4.on()
                        if self.mode_flg_2 == 0: 
                            oled.rect(int(OLED_WIDTH / 2 - left_possibility_2 * BAR_LEN) - INDI_WID - 2, 
                                    int((OLED_HEIGHT - BAR_WID) / 2)  + BAR_WID - 1, 
                                    INDI_WID, 
                                    BAR_WID, 1)
                else:
                    if self.coin_2 < (self.right_possibility_2_sampled):
                        cv4.toggle()
                        cv5.value(cv4._duty == 0)

                ################ CV6 ################    
                cv6.value((cv1._duty and cv4._duty) != 0)
                self.toss_flg = 0

            # Not Triggered --> Reset CV, OLED show mode
            ################ coin 1 #################
            # mode 0: Trigger, mode 1: Gate, mode 2: Toggle
            if self.mode_flg_1 == 0:
                oled.text('Tr', 0, OLED_HEIGHT-8, 1)
                
                sleep_ms(TRG_T)
                cv1.off()
                cv2.off()
                cv3.off()
            elif self.mode_flg_1 == 1:
                oled.text('G', 0, OLED_HEIGHT-8, 1)
                if self.coin_1 < (self.right_possibility_1_sampled):
                    oled.fill_rect(int(OLED_WIDTH / 2 + right_possibility_1 * BAR_LEN) + 2, 
                                int((OLED_HEIGHT - BAR_WID) / 2) - 3, 
                                INDI_WID, 
                                BAR_WID, 1)                
                else:
                    oled.rect(int(OLED_WIDTH / 2 - left_possibility_1 * BAR_LEN) - INDI_WID - 2, 
                            int((OLED_HEIGHT - BAR_WID) / 2) - 3, 
                            INDI_WID, 
                            BAR_WID, 1)   
                sleep_ms(TRG_T)
                cv3.off()
            elif self.mode_flg_1 == 2:
                oled.text('Tg', 0, OLED_HEIGHT-8, 1)
                sleep_ms(TRG_T)
                cv3.off()
                
            ################ coin 2 #################
            if self.mode_flg_2 == 0:
                oled.text('Tr', 110, OLED_HEIGHT-8, 1)
                
                sleep_ms(TRG_T)
                cv4.off()
                cv5.off()
                cv6.off()
            elif self.mode_flg_2 == 1:
                oled.text('G', 110, OLED_HEIGHT-8, 1)
                if self.coin_2 < (self.right_possibility_2_sampled):
                    oled.fill_rect(int(OLED_WIDTH / 2 + right_possibility_2 * BAR_LEN) + 2, 
                                int((OLED_HEIGHT - BAR_WID) / 2)  + BAR_WID - 1, 
                                INDI_WID, 
                                BAR_WID, 1)                
                else:
                    oled.rect(int(OLED_WIDTH / 2 - left_possibility_2 * BAR_LEN) - INDI_WID - 2, 
                            int((OLED_HEIGHT - BAR_WID) / 2)  + BAR_WID - 1, 
                            INDI_WID, 
                            BAR_WID, 1)
                sleep_ms(TRG_T)
            elif self.mode_flg_2 == 2:
                oled.text('Tg', 110, OLED_HEIGHT-8, 1)
                
            oled.show()
    
if __name__ == "__main__":
    bernoulli_gates = BernoulliGates()
    bernoulli_gates.main()
