from machine import Pin, ADC, PWM
from time import sleep


ain = ADC(Pin(26, Pin.IN, Pin.PULL_DOWN))
cv1 = PWM(Pin(21))


def wait_for_voltage(voltage):
    if voltage != 0:
        input(f"\nPlease plug {voltage}V into the CV input and then press Enter")
    else:
        input('\nPlease unplug all cables and then press Enter')
    print('\n Calibrating...')
    sleep(2)
    return round(ain.read_u16())


chosen_process = ''
print("""
There are two options for running the calibration process, 1 and 2

1. Low accuracy (Only requires 10V)
2. High accuracy (Requires adjustable voltage source)

Please type your chosen calibration process to choose it""")
while chosen_process not in ['1','2']:
    chosen_process = input('\n> ')
    if chosen_process not in ['1','2']:
        print("\n\033[1;31;48mPlease choose a value from the list, either 1 or 2\033[0m")

chosen_process = int(chosen_process)

readings = []
if chosen_process == 1:
    readings.append(wait_for_voltage(0))
    readings.append(wait_for_voltage(10))
else:
    for voltage in range(11):
        readings.append(wait_for_voltage(voltage))
        
with open(f'lib/calibration.py', 'w') as file:
    values = ", ".join(map(str, readings))
    file.write(f"CALIBRATION_VALUES=[{values}]")
