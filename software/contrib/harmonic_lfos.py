from europi import *
from math import cos, radians
from random import randint
from time import sleep_ms
from europi_script import EuroPiScript

MAX_VOLTAGE = 10
HARMONICS = [1, 3, 5, 7, 11, 13]
MAX_HARMONIC = 32

machine.freq(250_000_000)

def read_k2():
    return k2.read_position(MAX_HARMONIC, 1) + 1

def reset():
    global degree
    degree = 0

def change_mode():
    global MODE
    MODE += 1
    
    if MODE == 3:
        MODE = 0

def get_delay_increment_value():
    delay = (0.1 - (k1.read_position(100, 1)/1000)) + (ain.read_voltage(1)/100)
    return delay, round((((1/delay)-10)/1)+1)

def increment_selection():
    global selected_lfo, selected_lfo_start_value
    selected_lfo += 1
    if selected_lfo == 6:
        selected_lfo = 0
    selected_lfo_start_value = read_k2()

MODE = 0
degree = 0
delay, increment_value = get_delay_increment_value()
pixel_x = OLED_WIDTH-1
pixel_y = OLED_HEIGHT-1
selected_lfo = 0
selected_lfo_start_value = read_k2()

class HarmonicLFOs(EuroPiScript):

    def main(self):
        global degree, delay, increment_value, selected_lfo, selected_lfo_start_value

        din.handler(reset)
        b1.handler(change_mode)
        b2.handler(increment_selection)

        while True:
            rad = radians(degree)
            
            #Hysteresis to prevent each LFO's value from being changed as soon as it is selected
            k2_reading = read_k2()
            if k2_reading != selected_lfo_start_value:
                selected_lfo_start_value = k2_reading
                HARMONICS[selected_lfo] = k2_reading
            
            oled.vline(pixel_x,0,OLED_HEIGHT,0)
            for cv, multiplier in zip(cvs, HARMONICS):
                three_sixty = 360*multiplier
                degree_three_sixty = degree % three_sixty
                
                if MODE == 0: #Sin
                    volts = ((0-(cos(rad*(1/multiplier)))+1)) * (MAX_VOLTAGE/2)
                elif MODE == 1: #Saw
                    volts = (degree_three_sixty / (three_sixty)) * MAX_VOLTAGE
                elif MODE == 2: #Square
                    volts = MAX_VOLTAGE * (int((degree_three_sixty / (three_sixty)) * MAX_VOLTAGE) < (MAX_VOLTAGE/2))
                    
                cv.voltage(volts)
                oled.pixel(pixel_x,pixel_y-int(volts*(pixel_y/10)),1)
            
            #Draw the current LFO's information to the display
            oled.fill_rect(0,0,18,32,0)
            oled.fill_rect(0,0,18,9,1)
            oled.text(str(selected_lfo+1),0,1,0)
            
            oled.text('1',0,15,1)
            oled.hline(0,23,(8 * (((HARMONICS[selected_lfo]) // 10) + 1)),1)
            oled.text(str(HARMONICS[selected_lfo]),0,25,1)
            
            #Delay based on the speed, controlled by knob 1
            degree += increment_value
            sleep_ms(int(delay))
            oled.scroll(-1,0)
            
            #Update the display every 10 cycles
            if round(degree, -1) % 10 == 0:
                delay, increment_value = get_delay_increment_value()
                oled.show()


if __name__ == "__main__":
    HarmonicLFOs().main()
