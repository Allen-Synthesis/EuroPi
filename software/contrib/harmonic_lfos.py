from europi import *
from math import cos, radians
from random import randint
from time import sleep
from europi_script import EuroPiScript

MAX_VOLTAGE = 10
HARMONICS = [1, 3, 5, 7, 11, 13]

def reset():
    global degree
    degree = 0

def change_mode():
    global MODE
    MODE += 1
    
    if MODE == 3:
        MODE = 0

def get_delay_increment_value_random_chance():
    random_chance = k2.read_position(100,1)
    delay = (0.1 - (k1.read_position(100)/1000)) + (ain.read_voltage(1)/100)
    return delay, round((((1/delay)-10)/1)+1), random_chance

def change_harmonic():
    global HARMONICS
    HARMONICS[randint(0,5)] = randint(1,13)

MODE = 0
degree = 0
delay, increment_value, random_chance = get_delay_increment_value_random_chance()
pixel_x = OLED_WIDTH-1
pixel_y = OLED_HEIGHT-1

class HarmonicLFOs(EuroPiScript):

    def main(self):
        global degree, delay, increment_value, random_chance

        din.handler(reset)
        b1.handler(reset)
        b2.handler(change_mode)

        while True:
            rad = radians(degree)
            
            if randint(0,100) < random_chance:
                change_harmonic()
            
            oled.vline(pixel_x,0,OLED_HEIGHT,0)
            for cv, multiplier in zip(cvs, HARMONICS):
                if MODE == 0: #Sin
                    volts = ((0-(cos(rad*(1/multiplier)))+1))*(MAX_VOLTAGE/2)
                elif MODE == 1: #Saw
                    volts = ((degree%(360*multiplier))/(360*multiplier))*MAX_VOLTAGE
                elif MODE == 2: #Square
                    volts = MAX_VOLTAGE * (int(((degree%(360*multiplier))/(360*multiplier))*MAX_VOLTAGE) < (MAX_VOLTAGE/2))
                    
                cv.voltage(volts)
                if cv != cv1:
                    oled.pixel(pixel_x,pixel_y-int(volts*(pixel_y/10)),1)
            
            degree += increment_value
            sleep(delay)
            oled.scroll(-1,0)
            
            if round(degree, -1) % 10 == 0:
                delay, increment_value, random_chance = get_delay_increment_value_random_chance()
                oled.show()


if __name__ == "__main__":
    HarmonicLFOs().main()