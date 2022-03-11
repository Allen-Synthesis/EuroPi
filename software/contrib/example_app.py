from europi import *
from time import sleep_ms

def app_back():
    """This is the go-back-to-menu handler"""
    global done
    print('long')
    oled.centre_text('App Select')
    done = 1
    sleep_ms(1500)

def utility(para_1):
    print('Call utility', para_1)

def run():
    global done
    """
    1. go-back-to-menu handler must be defined locally in the run app
    2. try not define global variables
    """
    b2.handler_long(app_back)
    done = 0
    para_1 = 1
    
    while True:
        if done == 1:
            print('Return')
            return 0
        
        # This is 
        oled.fill(0)
        oled.centre_text('APP 1')
        utility(para_1)
        sleep_ms(1000)
