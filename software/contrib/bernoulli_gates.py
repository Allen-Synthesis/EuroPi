from europi import *
from time import sleep_ms, ticks_diff, ticks_ms
from random import random

'''
03/13 first version finished
03/17 fixed undefined coin and sampled probability if not receiving trigger and change mode
'''

'''### for return back to menu
def app_back():
    global done
    oled.centre_text('App Select')
    done = 1
    sleep_ms(1500)
'''

def digital_trigger():
    global toss_flg
    toss_flg = 1

def mode_switch_1():
    global mode_flg_1
    mode_flg_1 += 1
    if mode_flg_1 == 3:
        mode_flg_1 = 0

def mode_switch_2():
    global mode_flg_2
    mode_flg_2 += 1
    if mode_flg_2 == 3:
        mode_flg_2 = 0

def init():
    global bar_length, bar_width, indicator_width, toss_flg, mode_flg_1, mode_flg_2, coin_1, coin_1, coin_2, right_possibility_1_sampled, left_possibility_1_sample, right_possibility_2_sampled, left_possibility_2_sample
    
    bar_length = 50
    bar_width = 6
    indicator_width = 5
    toss_flg = 0
    mode_flg_1 = 0 # mode 0: Latch, mode 1: Toggle
    mode_flg_2 = 0
    coin_1 = 0
    coin_2 = 0
    right_possibility_1_sampled = 0
    left_possibility_1_sample = 0
    right_possibility_2_sampled = 0
    left_possibility_2_sample = 0

    # Number of sequential reads for smoothing analog read values.
    k1.set_samples(32)
    k2.set_samples(32)
    
    din.handler(digital_trigger)
    b1.handler(mode_switch_1)
    b2.handler(mode_switch_2)

def run():
    global bar_length, bar_width, indicator_width, toss_flg, mode_flg_1, mode_flg_2, coin_1, coin_2, right_possibility_1_sampled, left_possibility_1_sample, right_possibility_2_sampled, left_possibility_2_sample#, done
    
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
        
        # Get Possibility
        right_possibility_1 = k1.percent() + ain.read_voltage()/12
        left_possibility_1 = 1 - right_possibility_1
        
        right_possibility_2 = k2.percent()
        left_possibility_2 = 1 - right_possibility_2
        
        # OLED Show Possibility Bar
        oled.fill(0)
        oled.text(f"P1:{right_possibility_1:.2f}", 0, 0, 1)
        oled.rect(int(OLED_WIDTH / 2), int((OLED_HEIGHT - bar_width) / 2) - 3, int(right_possibility_1 * bar_length), bar_width, 1) # right
        oled.fill_rect(int(OLED_WIDTH / 2 - left_possibility_1 * bar_length), int((OLED_HEIGHT - bar_width) / 2) - 3, int(left_possibility_1 * bar_length), bar_width, 1) # left
        
        oled.text(f"P2:{right_possibility_2:.2f}", int(OLED_WIDTH / 2) + 8, 0, 1)
        oled.rect(int(OLED_WIDTH / 2), int((OLED_HEIGHT - bar_width) / 2) + bar_width - 1, int(right_possibility_2 * bar_length), bar_width, 1) # right
        oled.fill_rect(int(OLED_WIDTH / 2 - left_possibility_2 * bar_length), int((OLED_HEIGHT - bar_width) / 2) + bar_width - 1, int(left_possibility_2 * bar_length), bar_width, 1) # left
        
        # Triggered
        if toss_flg == 1:
            right_possibility_1_sampled = right_possibility_1
            left_possibility_1_sample = left_possibility_1
            
            right_possibility_2_sampled = right_possibility_2
            left_possibility_2_sample = left_possibility_2
            
            cv3.on()
            
            ################ coin 1 #################
            coin_1 = random()
            if mode_flg_1 == 0 or mode_flg_1 == 1:
                if coin_1 < (right_possibility_1_sampled):
                    cv1.off() 
                    cv2.on()
                    if mode_flg_1 == 0: oled.fill_rect(int(OLED_WIDTH / 2 + right_possibility_1 * bar_length) + 2, int((OLED_HEIGHT - bar_width) / 2) - 3, indicator_width, bar_width, 1)               
                else:
                    cv2.off()
                    cv1.on()
                    if mode_flg_1 == 0: oled.rect(int(OLED_WIDTH / 2 - left_possibility_1 * bar_length) - indicator_width - 2, int((OLED_HEIGHT - bar_width) / 2) - 3, indicator_width, bar_width, 1)
            else:
                if coin_1 < (right_possibility_1_sampled):
                    cv1.toggle()
                    cv2.value(cv1._duty == 0)
                    
            ################ coin 2 #################
            coin_2 = random()
            if mode_flg_2 == 0 or mode_flg_2 == 1:
                if coin_2 < (right_possibility_2_sampled):
                    cv4.off() 
                    cv5.on()
                    if mode_flg_2 == 0: oled.fill_rect(int(OLED_WIDTH / 2 + right_possibility_2 * bar_length) + 2, int((OLED_HEIGHT - bar_width) / 2)  + bar_width - 1, indicator_width, bar_width, 1)               
                else:
                    cv5.off()
                    cv4.on()
                    if mode_flg_2 == 0: oled.rect(int(OLED_WIDTH / 2 - left_possibility_2 * bar_length) - indicator_width - 2, int((OLED_HEIGHT - bar_width) / 2)  + bar_width - 1, indicator_width, bar_width, 1)
            else:
                if coin_2 < (right_possibility_2_sampled):
                    cv4.toggle()
                    cv5.value(cv4._duty == 0)
                    
            cv6.value((cv1._duty and cv4._duty) != 0)
            toss_flg = 0
        
        # Not Triggered --> Reset CV, OLED show mode
        ################ coin 1 #################
        # mode 0: Trigger, mode 1: Gate, mode 2: Toggle
        if mode_flg_1 == 0:
            oled.text('Tr', 0, OLED_HEIGHT-8, 1)
            
            sleep_ms(10)
            cv1.off()
            cv2.off()
            cv3.off()
        elif mode_flg_1 == 1:
            oled.text('G', 0, OLED_HEIGHT-8, 1)
            if coin_1 < (right_possibility_1_sampled):
                oled.fill_rect(int(OLED_WIDTH / 2 + right_possibility_1 * bar_length) + 2, int((OLED_HEIGHT - bar_width) / 2) - 3, indicator_width, bar_width, 1)                
            else:
                oled.rect(int(OLED_WIDTH / 2 - left_possibility_1 * bar_length) - indicator_width - 2, int((OLED_HEIGHT - bar_width) / 2) - 3, indicator_width, bar_width, 1)
                
            sleep_ms(10)
            cv3.off()
        elif mode_flg_1 == 2:
            oled.text('Tg', 0, OLED_HEIGHT-8, 1)
            
        ################ coin 2 #################
        if mode_flg_2 == 0:
            oled.text('Tr', 110, OLED_HEIGHT-8, 1)
            
            sleep_ms(10)
            cv4.off()
            cv5.off()
            cv6.off()
        elif mode_flg_2 == 1:
            oled.text('G', 110, OLED_HEIGHT-8, 1)
            if coin_2 < (right_possibility_2_sampled):
                oled.fill_rect(int(OLED_WIDTH / 2 + right_possibility_2 * bar_length) + 2, int((OLED_HEIGHT - bar_width) / 2)  + bar_width - 1, indicator_width, bar_width, 1)                
            else:
                oled.rect(int(OLED_WIDTH / 2 - left_possibility_2 * bar_length) - indicator_width - 2, int((OLED_HEIGHT - bar_width) / 2)  + bar_width - 1, indicator_width, bar_width, 1)
                
            sleep_ms(10)
        elif mode_flg_2 == 2:
            oled.text('Tg', 110, OLED_HEIGHT-8, 1)
            
        oled.show()
                                
if __name__ == "__main__":
    run()


