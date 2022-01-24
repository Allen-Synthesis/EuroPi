from machine import Pin, ADC, PWM, freq
from time import sleep
from europi import oled, b1, b2

machine.freq(250000000)


ain = ADC(Pin(26, Pin.IN, Pin.PULL_DOWN))
cv1 = PWM(Pin(21))
usb = Pin(24, Pin.IN)


def wait_for_voltage(voltage):
    wait_for_b1(0)
    if voltage != 0:
        oled.centre_text(f'Plug {voltage}V into\nanalogue in\nthen press B1')
        wait_for_b1(1)
    else:
        oled.centre_text(f'Please unplug\nall cables\nthen press B1')
        wait_for_b1(1)
    oled.centre_text('Calibrating...')
    sleep(1.5)
    readings = []
    for reading in range(256):
        readings.append(ain.read_u16())
    return round(sum(readings)/256)

def text_wait(text, wait):
    oled.centre_text(text)
    sleep(wait)
    
def fill_show(colour):
    oled.fill(colour)
    oled.show()
    
def flash(flashes, period):
    for flash in range(flashes):
        fill_show(1)
        sleep(period/2)
        fill_show(0)
        sleep(period/2)
    
def wait_for_b1(value):
    while b1.value() != value:
        sleep(0.05)


flash(8, 0.2)


if usb.value() == 1:
    text_wait('Please connect\nrack power only\nnot USB', 4)
    oled.centre_text('Please connect\nrack power only\nnot USB')

text_wait('Welcome to the\ncalibration\nprocess', 3)
text_wait('There are 2\noptions for\ncalibrating', 3)
text_wait('1: You need\n a variable\nvoltage source', 3)
text_wait('2: You only\nneed a\n10V supply', 3)
text_wait('Use buttons to\nchoose\n1           2', 0)
while True:
    if b1.value() == 1:
        chosen_process = 1
        break
    elif b2.value() == 1:
        chosen_process = 2
        break


readings = []
if chosen_process == 1:
    readings.append(wait_for_voltage(0))
    readings.append(wait_for_voltage(10))
else:
    for voltage in range(11):
        readings.append(wait_for_voltage(voltage))
        
with open(f'lib/calibration.py', 'w') as file:
    values = ", ".join(map(str, readings))
    file.write(f"INPUT_CALIBRATION_VALUES=[{values}]")
    

from europi import AnalogueInput
ain = AnalogueInput(26)
cv1 = PWM(Pin(21))

oled.centre_text(f'Plug CV1 into\nanalogue in\nthen press B1')
wait_for_b1(1)
oled.centre_text('Calibrating...')

output_duties = [0]
duty = 0
reading = 0
for voltage in range(1,11):
    while abs(reading - voltage) > 0.005 and reading < voltage:
        cv1.duty_u16(duty)
        duty += 25
        if duty > MAX_UINT16:
            text_wait('Calibration\ncould not\ncomplete', 2)
            text_wait('Double check\nresistor values\and soldering', 2)
            break
        reading = round(ain.read_voltage(),2)
    output_duties.append(duty)
    oled.centre_text(f'Calibrating...\n{voltage}V')

with open(f'lib/calibration.py', 'a+') as file:
    values = ", ".join(map(str, output_duties))
    file.write(f"\nOUTPUT_CALIBRATION_VALUES=[{values}]")
    
    
oled.centre_text('Calibration\nComplete!')


