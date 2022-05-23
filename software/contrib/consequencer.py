from europi import *
import machine
from time import ticks_diff, ticks_ms
from random import randint, uniform
from europi_script import EuroPiScript

'''
Consequencer
author: Nik Ansell (github.com/gamecat69)
date: 2022-02-05
labels: sequencer, triggers, drums, randomness

A gate and CV sequencer inspired by Grids from Mutable Instruments that contains pre-loaded drum patterns that can be smoothly morphed from one to another. Triggers are sent from outputs 1 - 3, randomized stepped CV patterns are sent from outputs 4 - 6.
Send a clock to the digital input to start the sequence.

Demo video: https://youtu.be/UwjajP6uiQU

digital_in: clock in
analog_in: randomness CV

knob_1: randomness
knob_2: select pre-loaded drum pattern

button_1: Short Press: toggle randomized hi-hats on / off. Long Press: Play previous CV Pattern
button_2:
- Short Press  (<300ms)  : Generate a new random cv pattern for outputs 4 - 6.
- Medium Press (>300ms)  : Cycle through analogue input modes
- Long Press   (>3000ms) : Toggle option to send clocks from output 4 on / off

output_1: trigger 1 / Bass Drum
output_2: trigger 2 / Snare Drum
output_3: trigger 3 / Hi-Hat
output_4: randomly generated CV (cycled by pushing button 2)
output_5: randomly generated CV (cycled by pushing button 2)
output_6: randomly generated CV (cycled by pushing button 2)

'''

class Consequencer(EuroPiScript):
    def __init__(self):
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)

        # Initialize sequencer pattern arrays   
        p = pattern()     
        self.BD=p.BD
        self.SN=p.SN
        self.HH=p.HH

        # Initialize variables
        self.step = 0
        self.trigger_duration_ms = 50
        self.clock_step = 0
        self.pattern = 0
        self.random_HH = False
        self.minAnalogInputVoltage = 0.9
        self.randomness = 0
        self.analogInputMode = 1 # 1: Randomness, 2: Pattern, 3: CV Pattern
        self.CvPattern = 0
        self.reset_timeout = 500

        # option to always output a clock on output 4
        # this helps to sync Consequencer with other modules
        self.output4isClock = False
        
        # Calculate the longest pattern length to be used when generating random sequences
        self.maxStepLength = len(max(self.BD, key=len))
        
        # Generate random CV for cv4-6
        self.random4 = []
        self.random5 = []
        self.random6 = []
        self.generateNewRandomCVPattern()

        # Triggered when button 2 is released.
        # Short press: Generate random CV for cv4-6
        # Long press: Change operating mode
        @b2.handler_falling
        def b2Pressed():
            
            if ticks_diff(ticks_ms(), b2.last_pressed()) >  300:
                if self.analogInputMode < 3:
                    self.analogInputMode += 1
                else:
                    self.analogInputMode = 1
            else:
                # Move to next cv pattern if one already exists, otherwise create a new one
                self.CvPattern += 1
                if self.CvPattern == len(self.random4):
                    self.generateNewRandomCVPattern()
            
        # Triggered when button 1 is released
        # Short press: Play previous CV pattern for cv4-6
        # Long press: Toggle random high-hat mode
        @b1.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b1.last_pressed()) > 2000:
                self.output4isClock = not self.output4isClock
            elif ticks_diff(ticks_ms(), b1.last_pressed()) >  300:
                self.random_HH = not self.random_HH
            else:
                # Play previous CV Pattern, unless we are at the first pattern
                if self.CvPattern != 0:
                    self.CvPattern -= 1

        # Triggered on each clock into digital input. Output triggers.
        @din.handler
        def clockTrigger():

            # function timing code. Leave in and activate as needed
            #t = time.ticks_us()
            
            self.step_length = len(self.BD[self.pattern])
            
            # A pattern was selected which is shorter than the current step. Set to zero to avoid an error
            if self.step >= self.step_length:
                self.step = 0 
            
            cv5.voltage(self.random5[self.CvPattern][self.step])
            cv6.voltage(self.random6[self.CvPattern][self.step])

            # How much randomness to add to cv1-3
            # As the randomness value gets higher, the chance of a randomly selected int being lower gets higher
            if randint(0,99) < self.randomness:
                cv1.value(randint(0, 1))
                cv2.value(randint(0, 1))
                cv3.value(randint(0, 1))
            else:
                cv1.value(int(self.BD[self.pattern][self.step]))
                cv2.value(int(self.SN[self.pattern][self.step]))                    

                # If randomize HH is ON:
                if self.random_HH:
                    cv3.value(randint(0, 1))
                else:
                    cv3.value(int(self.HH[self.pattern][self.step]))

            # Set cv4-6 voltage outputs based on previously generated random pattern
            if self.output4isClock:
                cv4.value(1)
            else:
                cv4.voltage(self.random4[self.CvPattern][self.step])

            # Incremenent the clock step
            self.clock_step +=1
            self.step += 1

            # function timing code. Leave in and activate as needed
            #delta = time.ticks_diff(time.ticks_us(), t)
            #print('Function {} Time = {:6.3f}ms'.format('clockTrigger', delta/1000))

        @din.handler_falling
        def clockTriggerEnd():
            cv1.off()
            cv2.off()
            cv3.off()
            if self.output4isClock:
                cv4.off()

    def generateNewRandomCVPattern(self):
        self.random4.append(self.generateRandomPattern(self.maxStepLength, 0, 9))
        self.random5.append(self.generateRandomPattern(self.maxStepLength, 0, 9))
        self.random6.append(self.generateRandomPattern(self.maxStepLength, 0, 9))

    def getPattern(self):
        # If mode 2 and there is CV on the analogue input use it, if not use the knob position
        val = 100 * ain.percent()
        if self.analogInputMode == 2 and val > self.minAnalogInputVoltage:
            self.pattern = int((len(self.BD) / 100) * val)
        else:
            self.pattern = k2.read_position(len(self.BD))
        
        self.step_length = len(self.BD[self.pattern])

    def getCvPattern(self):
        # If analogue input mode 3, get the CV pattern from CV input
        if self.analogInputMode != 3:
            return
        else:
            # Get the analogue input voltage as a percentage
            CvpVal = 100 * ain.percent()
            
            # Is there a voltage on the analogue input and are we configured to use it?
            if CvpVal > 0.4:
                # Convert percentage value to a representative index of the pattern array
                self.CvPattern = int((len(self.random4) / 100) * CvpVal)

    def generateRandomPattern(self, length, min, max):
        self.t=[]
        for i in range(0, length):
            self.t.append(uniform(0,9))
        return self.t


    def getRandomness(self):
        # If mode 1 and there is CV on the analogue input use it, if not use the knob position
        val = 100 * ain.percent()
        if self.analogInputMode == 1 and val > self.minAnalogInputVoltage:
            self.randomness = val
        else:
            self.randomness = k1.read_position()

    def main(self):
        while True:
            self.getPattern()
            self.getRandomness()
            self.getCvPattern()
            self.updateScreen()
            # If I have been running, then stopped for longer than reset_timeout, reset the steps and clock_step to 0
            if self.clock_step != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.reset_timeout:
                self.step = 0
                self.clock_step = 0

    def visualizePattern(self, pattern):
        self.t = pattern
        self.t = self.t.replace('1','^')
        self.t = self.t.replace('0',' ')
        return self.t

    def updateScreen(self):
        # oled.clear() - dont use this, it causes the screen to flicker!
        oled.fill(0)

        # Show selected pattern visually
        oled.text(self.visualizePattern(self.BD[self.pattern]), 0, 0, 1)
        oled.text(self.visualizePattern(self.SN[self.pattern]), 0, 10, 1)
        oled.text(self.visualizePattern(self.HH[self.pattern]), 0, 20, 1)

        # If the random toggle is on, show a rectangle
        if self.random_HH:
            oled.fill_rect(0, 29, 10, 3, 1)

        # Show self.output4isClock value
        if self.output4isClock:
            oled.rect(12, 29, 10, 3, 1)

        # Show randomness
        oled.text('R' + str(int(self.randomness)), 26, 25, 1)

        # Show CV pattern
        oled.text('C' + str(self.CvPattern), 56, 25, 1)

        # Show the analogInputMode
        oled.text('M' + str(self.analogInputMode), 85, 25, 1)

        # Show the pattern number
        oled.text(str(self.pattern), 110, 25, 1)

        oled.show()

class pattern:

    # Initialize pattern lists
    BD=[]
    SN=[]
    HH=[]

    # African Patterns
    BD.append("10110000001100001011000000110000")
    SN.append("10001000100010001010100001001010")
    HH.append("00001011000010110000101100001011")

    BD.append("10101010101010101010101010101010")
    SN.append("00001000000010000000100000001001")
    HH.append("10100010101000101010001010100000")

    BD.append("11000000101000001100000010100000")
    SN.append("00001000000010000000100000001010")
    HH.append("10111001101110011011100110111001")

    BD.append("10001000100010001000100010001010")
    SN.append("00100100101100000010010010110010")
    HH.append("10101010101010101010101010101011")

    BD.append("00101011101000111010001110100010")
    SN.append("00101011101000111010001110100010")
    HH.append("00001000000010000000100000001000")

    BD.append("10101111101000111010001110101000")
    SN.append("10101111101000111010001110101000")
    HH.append("00000000101000001010000010100010")

    BD.append("10110110000011111011011000001111")
    SN.append("10110110000011111011011000001111")
    HH.append("11111010001011111010001110101100")

    BD.append("10010100100101001001010010010100")
    SN.append("00100010001000100010001000100010")
    HH.append("01010101010101010101010101010101")

    # 0,1,1,2,3,5,8,12
    BD.append("0101011011101111")
    SN.append("1010100100010000")
    HH.append("1110100100010000")

    # Add patterns
    BD.append("1000100010001000")
    SN.append("0000000000000000")
    HH.append("0000000000000000")

    BD.append("1000100010001000")
    SN.append("0000000000000000")
    HH.append("0010010010010010")

    BD.append("1000100010001000")
    SN.append("0000100000000000")
    HH.append("0010010010010010")

    BD.append("1000100010001000")
    SN.append("0000100000001000")
    HH.append("0010010010010010")

    BD.append("1000100010001000")
    SN.append("0000100000000000")
    HH.append("0000000000000000")

    BD.append("1000100010001000")
    SN.append("0000100000001000")
    HH.append("0000000000000000")

    BD.append("1000100010001000")
    SN.append("0000100000001000")
    HH.append("0000100010001001")

    BD.append("1000100010001000")
    SN.append("0000100000001000")
    HH.append("0101010101010101")

    BD.append("1000100010001000")
    SN.append("0000000000000000")
    HH.append("1111111111111111")

    BD.append("1000100010001000")
    SN.append("0000100000001000")
    HH.append("1111111111111111")

    BD.append("1000100010001000")
    SN.append("0000100000000000")
    HH.append("0001000000000000")

    BD.append("1000100010001000")
    SN.append("0000100000000000")
    HH.append("0001001000000000")

    # Source: https://docs.google.com/spreadsheets/d/19_3BxUMy3uy1Gb0V8Wc-TcG7q16Amfn6e8QVw4-HuD0/edit#gid=0
    BD.append("1000000010000000")
    SN.append("0000100000001000")
    HH.append("1010101010101010")

    BD.append("1010001000100100")
    SN.append("0000100101011001")
    HH.append("0000000100000100")

    BD.append("1000000110000010")
    SN.append("0000100000001000")
    HH.append("1010101110001010")

    BD.append("1100000100110000")
    SN.append("0000100000001000")
    HH.append("1010101010101010")

    BD.append("1000000110100000")
    SN.append("0000100000001000")
    HH.append("0010101010101010")

    BD.append("1010000000110001")
    SN.append("0000100000001000")
    HH.append("1010101010101010")

    BD.append("1000000110100001")
    SN.append("0000100000001000")
    HH.append("0000100010101011")

    BD.append("1001001010000000")
    SN.append("0000100000001000")
    HH.append("0000100000001000")

    BD.append("1010001001100000")
    SN.append("0000100000001000")
    HH.append("1010101010001010")

    BD.append("1010000101110001")
    SN.append("0000100000001000")
    HH.append("1010101010001010")

    # End external patterns

    BD.append("1000100010001000")
    SN.append("0000101001001000")
    HH.append("0101010101010101")

    BD.append("1100000001010000")
    SN.append("0000101000001000")
    HH.append("0101010101010101")

    BD.append("1100000001010000")
    SN.append("0000101000001000")
    HH.append("1111111111111111")

    BD.append("1001001001000100")
    SN.append("0001000000010000")
    HH.append("0101110010011110")

    BD.append("1001001001000100")
    SN.append("0001000000010000")
    HH.append("1111111111111111")

    # Be warned patterns < 16 steps can sound disjointed when using CV to select the pattern!

    BD.append("10010000010010")
    SN.append("00010010000010")
    HH.append("11100110111011")

    BD.append("1001000001001")
    SN.append("0001001000001")
    HH.append("1110011011101")

    BD.append("100100000100")
    SN.append("000100100000")
    HH.append("111001101110")

    BD.append("10010000010")
    SN.append("00010010000")
    HH.append("11100110111")

    BD.append("10010000010")
    SN.append("00010010000")
    HH.append("11111010011")

    BD.append("1001000010")
    SN.append("0001000000")
    HH.append("1111101101")

    BD.append("100100010")
    SN.append("000100000")
    HH.append("111110111")

    BD.append("10010010")
    SN.append("00010000")
    HH.append("11111111")

    BD.append("1001001")
    SN.append("0001000")
    HH.append("1111111")

    BD.append("100100")
    SN.append("000100")
    HH.append("111111")

    BD.append("10000")
    SN.append("00001")
    HH.append("11110")

    BD.append("1000")
    SN.append("0000")
    HH.append("1111")

    BD.append("100")
    SN.append("000")
    HH.append("111")


if __name__ == '__main__':
    # Reset module display state.
    [cv.off() for cv in cvs]
    dm = Consequencer()
    dm.main()

