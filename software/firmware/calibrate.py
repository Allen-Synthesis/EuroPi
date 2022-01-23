from europi import AnalogueInput, MAX_UINT16
from machine import Pin, PWM, freq

# Overclock for faster calibration
freq(250_000_000)

ain = AnalogueInput(26)
cv1 = PWM(Pin(21))


def wait_for_voltage(voltage):
    if voltage != 0:
        input(f"\nPlease plug {voltage}V into the CV input and then press Enter")
    else:
        input('\nPlease unplug all cables and then press Enter')
    print('\n Calibrating...')
    readings = []
    for reading in range(256):
        readings.append(ain.pin.read_u16())
    return round(sum(readings)/256)


## Input Calibration 

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
    file.write(f"INPUT_CALIBRATION_VALUES=[{values}]")
print(f'\n{readings}\n')


## Output Calibration

output_duties = [0]
duty = 0
reading = 0
step = 25
input('\nPlease plug CV output 1 into the analogue input and then press Enter')
for voltage in range(1,11):
    while abs(reading - voltage) > 0.005 and reading < voltage:
        if duty > MAX_UINT16:
            print(f'{output_duties}')
            raise Exception(f"The module failed to output {voltage}v. Last voltage reading: {reading}v")
        cv1.duty_u16(duty)
        duty += step
        reading = round(ain.read_voltage(), 2)
    output_duties.append(duty)
    print(f'\n{voltage}V')

print(f'\n{output_duties}')

with open(f'lib/calibration.py', 'a+') as file:
    values = ", ".join(map(str, output_duties))
    file.write(f"\nOUTPUT_CALIBRATION_VALUES=[{values}]")

print('\nCalibration Complete!')
