from machine import Pin, PWM, ADC, I2C
from ssd1306 import SSD1306_I2C


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
        self.gain_error, self.voltage_multiplier = get_output_calibration_data()
        
    def clamp(self, value):
        return max(min(value, 65534), 0)
        
    def duty_raw(self, cycle):
        cycle = int(cycle)
        self.output.duty_u16(self.clamp(cycle))
        self.current_duty = cycle
        
    def duty(self, cycle):
        self.duty_raw(cycle * self.gain_error)
        
    def voltage(self, voltage):
        self.duty(voltage * self.voltage_multiplier)
        
    def on(self):
        self.voltage(5)
    
    def off(self):
        self.duty_raw(0)
        

def get_output_calibration_data():
    with open('lib/calibration.txt', 'r') as data:
        data = data.readlines()
        OUTPUT_GAIN_ERROR = float(data[3].replace('\n',''))
        OUTPUT_VOLTAGE_MULTIPLIER = float(data[4].replace('\n',''))
    return OUTPUT_GAIN_ERROR, OUTPUT_VOLTAGE_MULTIPLIER


def get_input_calibration_data():
    with open('lib/calibration.txt', 'r') as data:
        data = data.readlines()
        INPUT_GAIN_ERROR = float(data[0].replace('\n',''))
        INPUT_OFFSET_ERROR = float(data[1].replace('\n',''))
        INPUT_VOLTAGE_MULTIPLIER = float(data[2].replace('\n',''))
        return INPUT_GAIN_ERROR, INPUT_OFFSET_ERROR, INPUT_VOLTAGE_MULTIPLIER


def sample_adc(adc, samples=256):
    values = []
    for sample in range(samples):
        values.append(adc.read_u16() / 16)
    return round(sum(values) / len(values))

class analogue_input:
    def __init__(self, pin):
        self.input = ADC(Pin(pin))
        self.gain_error, self.offset_error, self.voltage_multiplier = get_input_calibration_data()
    
    def read_raw(self, samples=256):
        return sample_adc(self.input, samples)
    
    def read_duty(self):
        return ((self.read_raw() + self.offset_error) * self.gain_error)
    
    def read_voltage(self):
        return self.read_duty() / self.voltage_multiplier


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


if __name__ == '__main__':
    None
        
    

