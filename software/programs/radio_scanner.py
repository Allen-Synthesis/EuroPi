from europi import *
from time import sleep
from random import randint
import _thread


def button_1_handler(pin): 
    button1.irq(handler=None)
    
    global button_1_bounce
    
    if button_1_bounce > 0.1:
        rotate_cvs()
        button_1_bounce = 0
    
    button1.irq(handler=button_1_handler)
button1.irq(trigger=Pin.IRQ_FALLING, handler=button_1_handler)

def digital_input_handler(pin): 
    digital_input.irq(handler=None)
    
    rotate_cvs()
    
    digital_input.irq(handler=digital_input_handler)
digital_input.irq(trigger=Pin.IRQ_FALLING, handler=digital_input_handler)


def button_2_handler(pin): 
    button2.irq(handler=None)
    
    global button_2_bounce
    
    if button_2_bounce > 0.1:
        global knob_mapping
        knob_mapping += 1
        if knob_mapping == 3:
            knob_mapping = 0
            
        global display_time
        display_time = 0
            
        button_2_bounce = 0
    
    button2.irq(handler=button_2_handler)
button2.irq(trigger=Pin.IRQ_FALLING, handler=button_2_handler)


button_1_bounce = 9999
button_2_bounce = 9999

def rotate_cvs():
    global cv_mapping
    new_cv_mapping = []
    for cv in cv_mapping[1:]: #Append all but the first (in order)
        new_cv_mapping.append(cv)
    new_cv_mapping.append(cv_mapping[0]) #Append the first
    
    cv_mapping = new_cv_mapping

def value_to_cv(value):
    return value * 16

def x_to_oled(x):
    return round(x * 0.0312)
def y_to_oled(y):
    return 31 - round(y * 0.0076)

cv_mapping = [cv1, cv2, cv3, cv4, cv5, cv6]
knob_mapping = 0 #0 = not used, 1 = knob 1, 2 = knob 2
knob_mapping_text = ['Off', 'Knob 1', 'Knob 2']

def do_step(x, y):
    oledx = x_to_oled(x)
    oledy = y_to_oled(y)
    
    cvx = value_to_cv(x)
    cvy = value_to_cv(y)
    
    oled.fill(0)
    oled.vline(oledx, 0, 32, 1)
    oled.hline(0, oledy, 128, 1)
    
    cv_mapping[0].duty(cvx) #0-65534
    cv_mapping[1].duty(cvy) #0-65534
    cv_mapping[2].duty(abs(cvy - cvx))
    cv_mapping[3].duty(32767 - cvx)
    cv_mapping[4].duty(32767 - cvy)
    cv_mapping[5].duty(32767 - abs(cvy - cvx))
    
    sleep(0.01)
    
    global button_1_bounce
    global button_2_bounce
    global display_time
    button_1_bounce += 0.01
    button_2_bounce += 0.01
    display_time += 0.01


def display_mapping(new_map):
    oled.fill_rect(0, 0, 64, 12, 1)
    oled.text(knob_mapping_text[new_map], 0, 2, 0)
    
    
    
display_time = 9999
while True:

    if knob_mapping != 1:
        x = k1.read_position(4096)
    else:
        x = ain.read_raw() + k1.read_position(4096)
        
    if knob_mapping != 2:
        y = k2.read_position(4096)
    else:
        y = ain.read_raw() + k2.read_position(4096)
    
    do_step(x, y)
    
    if display_time < 1:
        display_mapping(knob_mapping)
    oled.show()
