from machine import Pin, PWM, ADC, I2C
from time import sleep
from random import randint
from ssd1306 import SSD1306_I2C

oled = SSD1306_I2C(128, 32, I2C(0, sda=Pin(0), scl=Pin(1), freq=400000))
oled.fill(0)
oled.show()


digital_input = Pin(22, Pin.IN)

button1 = Pin(4, Pin.IN)
button2 = Pin(5, Pin.IN)

knob1 = ADC(Pin(27))
knob2 = ADC(Pin(28))


with open('callibration_values.csv', 'r') as file:
    values = file.readlines()
    ANALOGUE_INPUT_FACTOR = float(values[0])
    OUTPUT_FACTOR = float(values[1])

def read_analogue_input(): #Reads the analogue input and converts the reading to a voltage (float)
    return analogue_input.read_u16() * ANALOGUE_INPUT_FACTOR
    
def output_voltage(amount): #Converts a voltage value into a duty cycle value to give to an output
    return round(amount * OUTPUT_FACTOR)

def quantise(voltage): #This operates on voltages, not duty cycle amounts, so use it *before* an output_voltage call
    semitone = 1 / 12
    return round(voltage / semitone) * semitone


class analogue_input:
    def __init__(self, pin):
        self.input = ADC(Pin(pin))
    
    def read(self):
        return self.input.read_u16() * ANALOGUE_INPUT_FACTOR
    
    def raw_read(self):
        return self.input.read_u16()


class output:
    def __init__(self, pin):
        self.output = PWM(Pin(pin))
        self.output.freq(2000)
        self.current_duty = 0
        
    def duty(self, value): #Sets the output CV based on a duty cycle
        clamped_value = max(min(value, 65534), 0)
        self.output.duty_u16(clamped_value)
        self.current_duty = clamped_value
        
    def voltage(self, voltage): #Sets the output CV based on a voltage
        clamped_value = max(min(round(voltage * OUTPUT_FACTOR), 65534), 0)
        self.duty(clamped_value)
        
    def on(self):
        self.output.duty_u16(65534)
        
    def off(self):
        self.output.duty_u16(65534)
        
    def toggle(self):
        if self.current_duty == 65534:
            self.duty(0)
        else:
            self.duty(65534)


output1 = output(21)
output2 = output(20)
output3 = output(16)
output4 = output(17)
output5 = output(18)
output6 = output(19)

analogue_input = analogue_input(26)


if __name__ == '__main__':
    oled.text('test',0,0)
    oled.show()
    
    voltage_input = input('Please plug a known voltage source into the analogue input and enter the voltage used, then press enter: ')
    reading = analogue_input.raw_read()
    print('read: ' + str(reading))

    analogue_input_factor = float(voltage_input) / reading #Multiply a reading by the analogue_input_factor to get the corresponding voltage

    useless = input('Now please plug output 1 into the analogue input and press enter')
    print('Callibrating...')

    output1.duty(65334)
    
    output_voltage = analogue_input.raw_read() * analogue_input_factor #Multiply a voltage by the output_factor to get the duty cycle required to produce it
    print('output voltage: ' + str(output_voltage))
    output_factor = 65334 / output_voltage

    with open('callibration_values.csv', 'w') as file:
        file.write(str(analogue_input_factor) + '\n' + str(output_factor) + '\n')

    print('Callibration complete! Enjoy your EuroPi :)')
