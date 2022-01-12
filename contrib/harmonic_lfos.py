from europi import *
from math import sin, radians


MAX_VOLTAGE = 5
HARMONICS = [1, 3, 5, 7, 11, 13]


def reset():
    global degree
    degree = 0
din.handler(reset)
b1.handler(reset)

def get_delay_increment_value():
    delay = (0.1 - (k1.read_position(100)/1000)) + (ain.read_voltage(1)/100)
    return delay, round((((1/delay)-10)/1)+1)

degree = 0
delay, increment_value = get_delay_increment_value()
while True:
    rad = radians(degree)
    for cv, multiplier in zip(cvs, HARMONICS):
        cv.voltage(((sin(rad*(1/multiplier)))+1)*(MAX_VOLTAGE/2))
    
    degree += increment_value
    sleep(delay)
    
    if round(degree, -1) % 10 == 0:
        delay, increment_value = get_delay_increment_value()

