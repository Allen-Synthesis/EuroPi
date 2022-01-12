from europi import *
from math import sin, radians

MAX_VOLTAGE = 5
HARMONICS = [1, 2, 3, 5, 7, 11]
degree = 0
delay = (0.1 - (k1.read_position(100)/1000)) + (ain.read_voltage(1)/100)
while True:
    rad = radians(degree)
    for cv, multiplier in zip(cvs, HARMONICS):
        cv.voltage(((sin(rad*(1/multiplier)))+1)*(MAX_VOLTAGE/2))
    degree += 1
    sleep(delay)
    if degree % 10 == 0:
        delay = (0.1 - (k1.read_position(100)/1000)) + (ain.read_voltage(1)/100)
