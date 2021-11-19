from machine import Pin, PWM, ADC, I2C
from ssd1306 import SSD1306_I2C
from time import sleep


#Rory Allen 19/11/2021 CC BY-SA 4.0
#Import this library into your own programs using 'from europi import *'
#You can then use the inputs, outputs, knobs, and buttons as objects, and make use of the general purpose functions


oled = SSD1306_I2C(128, 32, I2C(0, sda=Pin(0), scl=Pin(1), freq=400000))
oled.fill(0)
oled.show()



        
#General use functions
def centre_text(text):
    oled.fill(0)
    lines = text.split('\n')[0:3]
    center_line_height = int((-5 * len(lines)) + 25)
    heights = [center_line_height - 10, center_line_height, 2 * center_line_height]
    for line in lines:
        oled.text(str(line), int(64 - (((len(line) * 5) + ((len(line) - 1) * 2)) / 2)), heights[lines.index(line)], 1)

def clamp(value, low, high):
    return max(min(value, high), low)
        
def get_output_calibration_data():
    with open('lib/calibration.txt', 'r') as data:
        data = data.readlines()
        OUTPUT_MULTIPLIER = float(data[2].replace('\n',''))
    return OUTPUT_MULTIPLIER

def get_input_calibration_data():
    with open('lib/calibration.txt', 'r') as data:
        data = data.readlines()
        INPUT_MULTIPLIER = float(data[0].replace('\n',''))
        INPUT_OFFSET = float(data[1].replace('\n',''))
        return INPUT_MULTIPLIER, INPUT_OFFSET

def sample_adc(adc, samples=256):
    values = []
    for sample in range(samples):
        values.append(adc.read_u16() / 16)
    return round(sum(values) / len(values))




class output:
    def __init__(self, pin):
        self.output = PWM(Pin(pin))
        self.output.freq(1000000)
        self.pin = pin
        self.current_duty = 0
        self.output_multiplier = get_output_calibration_data()
        
    def duty(self, cycle):
        cycle = int(cycle)
        self.output.duty_u16(clamp(cycle, 0, 65534))
        self.current_duty = cycle
        
    def voltage(self, voltage):
        self.duty(voltage * self.output_multiplier)
        
    def on(self):
        self.voltage(5)
    
    def off(self):
        self.duty(0)

class analogue_input:
    def __init__(self, pin):
        self.input = ADC(Pin(pin))
        self.input_multiplier, self.input_offset = get_input_calibration_data()

    def read_duty(self, samples=256):
        return clamp(sample_adc(self.input, samples), 0, 65535)
    
    def read_voltage(self):
        return clamp((self.read_duty() * self.input_multiplier) + self.input_offset, 0, 12)

class knob:
    def __init__(self, pin):
        self.input = ADC(Pin(pin))
        
    def read_position(self, steps=100, samples=256):
        return round(steps - ((sample_adc(self.input, samples) / 4096) * steps))




button1 = Pin(4, Pin.IN)
button2 = Pin(5, Pin.IN)
k1 = knob(27)
k2 = knob(28)
din = Pin(22, Pin.IN)
ain = analogue_input(26)
cv1 = output(21)
cv2 = output(20)
cv3 = output(16)
cv4 = output(17)
cv5 = output(18)
cv6 = output(19)
cvs = [cv1, cv1, cv3, cv4, cv5, cv6]
for cv in cvs: #When imported, all outputs are turned off. This is because otherwise the op-amps may be left 'floating' and output unpredictable voltages
    cv.duty(0)




def din_handler(pin): 
    din.irq(handler=None)
    #function
    din.irq(handler=din_handler)
din.irq(trigger=Pin.IRQ_FALLING, handler=din_handler)

def button_1_handler(pin): 
    button1.irq(handler=None)
    #function
    button1.irq(handler=button_1_handler)
button1.irq(trigger=Pin.IRQ_FALLING, handler=button_1_handler)

def button_2_handler(pin): 
    button2.irq(handler=None)
    #function
    button2.irq(handler=button_2_handler)
button2.irq(trigger=Pin.IRQ_FALLING, handler=button_2_handler)
    



#Calibration program. Run this program to calibrate the module
if __name__ == '__main__':
    def wait_for_range(low, high):
        while ain.read_duty() < low or ain.read_duty() > high:
            sleep(0.05)
            
    def centre_and_show(text):
        centre_text(text)
        oled.show()
            
    def wait_and_show(low, high):
        wait_for_range(low, high)
        centre_text('Calibrating...')
        oled.show()
        sleep(2)
            
    LOW_VOLTAGE = 1 #Change these values if you have easier access to alternative accurate voltage sources
    HIGH_VOLTAGE = 10 #Make sure you still use as wide a range as you can and keep it within the 0-10V range
    
    low_threshold_low = (270*LOW_VOLTAGE)-150
    low_threshold_high = (270*LOW_VOLTAGE)+150
    high_threshold_low = (270*HIGH_VOLTAGE)-150
    high_threshold_high = (270*HIGH_VOLTAGE)+150
    
    samples = 8192
    
    centre_and_show('Welcome\nto the\ncalibrator')
    sleep(3)
    if ain.read_duty() > 100:
        centre_and_show('Please unplug\nall patch\ncables')
    wait_for_range(0, 100)
    centre_and_show('Plug 1V into\nanalogue input')
    wait_and_show(low_threshold_low, low_threshold_high)
    low_reading = ain.read_duty(samples)
    centre_and_show('Now plug 10V\ninto analogue\ninput')
    wait_and_show(high_threshold_low, high_threshold_high)
    high_reading = ain.read_duty(samples)
    
    input_multiplier = (HIGH_VOLTAGE - LOW_VOLTAGE) / (high_reading - low_reading)
    input_offset = HIGH_VOLTAGE - (input_multiplier * high_reading)
    
    centre_and_show('Please unplug\nall patch\ncables')
    wait_for_range(0, 100)
    centre_and_show('Plug output 1\ninto analogue\ninput')
    cv1.duty(65534)
    wait_and_show(high_threshold_low, high_threshold_high)
    output_multiplier = 65534 / ((ain.read_duty(samples) * input_multiplier) + input_offset)

    with open('lib/calibration.txt', 'w') as file:
        file.write(str(input_multiplier) + '\n' + str(input_offset) + '\n' + str(output_multiplier))

    centre_and_show('Calibration\ncomplete!')