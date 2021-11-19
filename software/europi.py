from machine import Pin, PWM, ADC, I2C
from ssd1306 import SSD1306_I2C
from time import sleep


oled = SSD1306_I2C(128, 32, I2C(0, sda=Pin(0), scl=Pin(1), freq=400000))
oled.fill(0)
oled.show()

button1 = Pin(4, Pin.IN)
button2 = Pin(5, Pin.IN)

digital_input = Pin(22, Pin.IN)


class output:
    def __init__(self, pin):
        self.output = PWM(Pin(pin))
        self.output.freq(1000000)
        self.pin = pin
        self.current_duty = 0
        self.output_multiplier = get_output_calibration_data()
        
    def clamp(self, value):
        return max(min(value, 65534), 0)
        
    def duty_raw(self, cycle):
        cycle = int(cycle)
        self.output.duty_u16(self.clamp(cycle))
        self.current_duty = cycle
        
    def duty(self, cycle):
        self.duty_raw(cycle)
        
    def voltage(self, voltage):
        self.duty(voltage * self.output_multiplier)
        
    def on(self):
        self.voltage(5)
    
    def off(self):
        self.duty_raw(0)
        

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

class analogue_input:
    def __init__(self, pin):
        self.input = ADC(Pin(pin))
        self.input_multiplier, self.input_offset = get_input_calibration_data()
    
    def read_raw(self, samples=256):
        return sample_adc(self.input, samples)
    
    def read_duty(self):
        return self.read_raw()
    
    def read_voltage(self):
        return (self.read_duty() * self.input_multiplier) + self.input_offset


class knob:
    def __init__(self, pin):
        self.input = ADC(Pin(pin))
        
    def read_position(self, steps=100):
        return round(steps - ((sample_adc(self.input) / 4096) * steps))


def digital_input_handler(pin): 
    digital_input.irq(handler=None)
    #function
    digital_input.irq(handler=digital_input_handler)
digital_input.irq(trigger=Pin.IRQ_FALLING, handler=digital_input_handler)


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


ain = analogue_input(26)

cv1 = output(21)
cv2 = output(20)
cv3 = output(16)
cv4 = output(17)
cv5 = output(18)
cv6 = output(19)

cvs = [cv1, cv1, cv3, cv4, cv5, cv6]

for cv in cvs:
    cv.duty(0)
    
k1 = knob(27)
k2 = knob(28)


#General use functions
def centre_text(text):
    oled.fill(0)
    lines = text.split('\n')[0:3]
    x = len(lines)
    heights = [int((-5*x)+15),int((-5*x)+25),int((-10*x)+50)] #This is a disgusting line, just trust me it works
    for line in lines:
        oled.text(str(line), int(64 - (((len(line) * 5) + ((len(line) - 1) * 2)) / 2)), heights[lines.index(line)], 1)



if __name__ == '__main__':
    def wait_for_range(low, high):
        while ain.read_raw() < low or ain.read_raw() > high:
            sleep(0.05)
            
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
    
    centre_text('Welcome\nto the\ncalibrator')
    oled.show()
    sleep(3)
    if ain.read_raw() > 100:
        centre_text('Please unplug\nall patch\ncables')
        oled.show()
    wait_for_range(0, 100)
    centre_text('Plug 1V into\nanalogue input')
    oled.show()
    wait_and_show(low_threshold_low, low_threshold_high)
    low_reading = ain.read_raw(4096)
    centre_text('Now plug 10V\ninto analogue\ninput')
    oled.show()
    wait_and_show(high_threshold_low, high_threshold_high)
    high_reading = ain.read_raw(4096)
    
    input_multiplier = (HIGH_VOLTAGE - LOW_VOLTAGE) / (high_reading - low_reading)
    input_offset = HIGH_VOLTAGE - (input_multiplier * high_reading)
    
    centre_text('Please unplug\nall patch\ncables')
    oled.show()
    wait_for_range(0, 100)
    centre_text('Plug output 1\ninto analogue\ninput')
    oled.show()
    cv1.duty_raw(65534)
    wait_and_show(high_threshold_low, high_threshold_high)
    output_multiplier = 65534 / ((ain.read_raw(4096) * input_multiplier) + input_offset)

    with open('lib/calibration.txt', 'w') as file:
        file.write(str(input_multiplier) + '\n' + str(input_offset) + '\n' + str(output_multiplier))

    centre_text('Calibration\ncomplete!')
    oled.show()