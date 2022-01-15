from europi import *

CALIBRATION_TEMPLATE = """
INPUT_MULTIPLIER = {0}
INPUT_OFFSET = {1}
OUTPUT_MULTIPLIER = {2}}
"""


#General use functions
def clamp(value, low, high): #Returns a value that is no lower than 'low' and no higher than 'high'
    return max(min(value, high), low)
        
def get_output_calibration_data(): #Retrieves the calibration data for the output
    with open('lib/calibration.txt', 'r') as data: #Open the text file in read mode
        data = data.readlines() #Create a list containing the lines read from the file
        OUTPUT_MULTIPLIER = float(data[2].replace('\n','')) #The third line is the output multiplier, convert to float as it is a string in the text file
    return OUTPUT_MULTIPLIER

def get_input_calibration_data(): #Retrieves the calibration data for the input
    with open('lib/calibration.txt', 'a+') as file: #Open the text file in 'all+' mode which means it will create a file if one isn't present
        data = file.readlines() #Create a list containing the lines read from the file
        if len(data) == 0: #If the file is empty
            default_values = ['0.003646677', '-0.05753613', '6347.393']
            file.write(default_values[0]+'\n'+default_values[1]+'\n'+default_values[2]) #Populate the file with default values
            data = default_values #Re-read the file now it contains the default values
        
        INPUT_MULTIPLIER = float(data[0].replace('\n','')) #The first line is the input multiplier
        INPUT_OFFSET = float(data[1].replace('\n','')) #The second line is the input offset
        return INPUT_MULTIPLIER, INPUT_OFFSET

def sample_adc(adc, samples=256): #Over-samples the ADC and returns the average. Default 256 samples
    values = [] #Empty list to begin with
    for sample in range(samples): #Sample continuously for as many samples as specified
        values.append(adc.read_u16() / 16) #Add the value to values list. /16 as u16 reads as a 16 bit number but the ADC is only 12 bit
    return round(sum(values) / len(values)) #Return the average (mean) of the values list



#Calibration program. Run this program to calibrate the module
if __name__ == '__main__':
    def wait_for_range(low, high):
        while ain.read_duty() < low or ain.read_duty() > high:
            sleep_ms(5)

    def wait_and_show(low, high):
        wait_for_range(low, high)
        oled.centre_text('Calibrating...')
        oled.show()
        sleep_ms(2000)
            
    LOW_VOLTAGE = 1 #Change these values if you have easier access to alternative accurate voltage sources
    HIGH_VOLTAGE = 10 #Make sure you still use as wide a range as you can and keep it within the 0-10V range
    
    low_threshold_low = (270*LOW_VOLTAGE)-150
    low_threshold_high = (270*LOW_VOLTAGE)+150
    high_threshold_low = (270*HIGH_VOLTAGE)-150
    high_threshold_high = (270*HIGH_VOLTAGE)+150
    
    samples = 2048
    
    oled.centre_text('Welcome\nto the\ncalibrator')
    sleep(3)
    if ain.read_duty() > 100:
        oled.centre_text('Please unplug\nall patch\ncables')
    wait_for_range(0, 100)
    oled.centre_text('Plug 1V into\nanalogue input')
    wait_and_show(low_threshold_low, low_threshold_high)
    low_reading = ain.read_duty(samples)
    oled.centre_text('Now plug 10V\ninto analogue\ninput')
    wait_and_show(high_threshold_low, high_threshold_high)
    high_reading = ain.read_duty(samples)
    
    input_multiplier = (HIGH_VOLTAGE - LOW_VOLTAGE) / (high_reading - low_reading)
    input_offset = HIGH_VOLTAGE - (input_multiplier * high_reading)
    
    oled.centre_text('Please unplug\nall patch\ncables')
    wait_for_range(0, 100)
    oled.centre_text('Plug output 1\ninto analogue\ninput')
    cv1.duty(65534)
    wait_and_show(high_threshold_low, high_threshold_high)
    output_multiplier = 65534 / ((ain.read_duty(samples) * input_multiplier) + input_offset)

    with open('lib/calibration.txt', 'w') as file:
        file.write(str(input_multiplier) + '\n' + str(input_offset) + '\n' + str(output_multiplier))

    oled.centre_text('Calibration\ncomplete!')
