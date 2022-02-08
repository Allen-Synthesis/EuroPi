from europi import *
from time import sleep_ms, ticks_diff, ticks_ms
from random import randint, randrange, uniform
#from patterns import *

'''
Drum Sequencer (Inspired by Mutable Grids)
author: Nik Ansell (github.com/gamecat69)
date: 2022-02-05
labels: sequencer, triggers, drums, randomness

A drum sequencer inspired by Grids from Mutable Instruments that contains pre-loaded drum patterns that can be smoothly morphed from one to another. Triggers are sent from outputs 1 - 3, randomized stepped CV patterns are sent from outputs 4 - 6.
Send a clock to the digital input to start the sequence.

Demo video: TBC

digital_in: clock in
analog_in: randomness CV

knob_1: randomness
knob_2: select pre-loaded drum pattern

button_1: Short Press: toggle randomized hi-hats on / off. Long Press: Play previous CV Pattern
button_2: Short PressL Generate a new random cv pattern for outputs 4 - 6. Long Press: Cycle through analogue input modes

output_1: trigger 1 / Bass Drum
output_2: trigger 2 / Snare Drum
output_3: trigger 3 / Hi-Hat
output_4: randomly generated CV (cycled by pushing button 2)
output_5: randomly generated CV (cycled by pushing button 2)
output_6: randomly generated CV (cycled by pushing button 2)

'''

# Overclock the Pico for improved performance.
machine.freq(250_000_000)

class drumMachine:
    def __init__(self):

        # Initialize sequencer pattern arrays        
        self.BD=[]
        self.SN=[]
        self.HH=[]

        # Initialize variables
        self.step = 0
        self.step_length = 16
        self.trigger_duration_ms = 50
        self.clock_step = 0
        self.clock_division = 1
        self.pattern = 0
        self.random_HH = False
        self.last_clock_input = 0
        self.randomness = 0
        self.analogInputMode = 1 # 1: Randomness, 2: Pattern, 3: CV Pattern
        self.CvPattern = 0
        
        # Generate random CV for cv4-6
        self.random4 = []
        self.random5 = []
        self.random6 = []

        #self.random4.append(self.generateRandomPattern(self.step_length, 0, 9))
        #self.random5.append(self.generateRandomPattern(self.step_length, 0, 9))
        #self.random6.append(self.generateRandomPattern(self.step_length, 0, 9))

        #self.random4 = self.generateRandomPattern(self.step_length, 0, 9)
        #self.random5 = self.generateRandomPattern(self.step_length, 0, 9)
        #self.random6 = self.generateRandomPattern(self.step_length, 0, 9)

        self.generateNewRandomCVPattern()

        #cv1.voltage(10)
        print(INPUT_CALIBRATION_VALUES)
        print(OUTPUT_CALIBRATION_VALUES)

        #print(self.random4)
        #print(self.random5)
        #print(self.random6)
        
        # ------------------------
        # Pre-loaded patterns
        # ------------------------

        self.BD.append("1000100010001000")
        self.SN.append("0000000000000000")
        self.HH.append("0000000000000000")

        self.BD.append("1000100010001000")
        self.SN.append("0000000000000000")
        self.HH.append("0010010010010010")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000000000")
        self.HH.append("0010010010010010")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000001000")
        self.HH.append("0010010010010010")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000000000")
        self.HH.append("0000000000000000")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000001000")
        self.HH.append("0000000000000000")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000001000")
        self.HH.append("0000100010001001")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000001000")
        self.HH.append("0101010101010101")

        self.BD.append("1000100010001000")
        self.SN.append("0000000000000000")
        self.HH.append("1111111111111111")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000001000")
        self.HH.append("1111111111111111")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000000000")
        self.HH.append("0001000000000000")

        self.BD.append("1000100010001000")
        self.SN.append("0000100000000000")
        self.HH.append("0001001000000000")

        # Source: https://docs.google.com/spreadsheets/d/19_3BxUMy3uy1Gb0V8Wc-TcG7q16Amfn6e8QVw4-HuD0/edit#gid=0
        self.BD.append("1000000010000000")
        self.SN.append("0000100000001000")
        self.HH.append("1010101010101010")

        self.BD.append("1010001000100100")
        self.SN.append("0000100101011001")
        self.HH.append("0000000100000100")

        self.BD.append("1000000110000010")
        self.SN.append("0000100000001000")
        self.HH.append("1010101110001010")

        self.BD.append("1100000100110000")
        self.SN.append("0000100000001000")
        self.HH.append("1010101010101010")

        self.BD.append("1000000110100000")
        self.SN.append("0000100000001000")
        self.HH.append("0010101010101010")

        self.BD.append("1010000000110001")
        self.SN.append("0000100000001000")
        self.HH.append("1010101010101010")

        self.BD.append("1000000110100001")
        self.SN.append("0000100000001000")
        self.HH.append("0000100010101011")

        self.BD.append("1001001010000000")
        self.SN.append("0000100000001000")
        self.HH.append("0000100000001000")

        self.BD.append("1010001001100000")
        self.SN.append("0000100000001000")
        self.HH.append("1010101010001010")

        self.BD.append("1010000101110001")
        self.SN.append("0000100000001000")
        self.HH.append("1010101010001010")

        # End external patterns

        self.BD.append("1000100010001000")
        self.SN.append("0000101001001000")
        self.HH.append("0101010101010101")

        self.BD.append("1100000001010000")
        self.SN.append("0000101000001000")
        self.HH.append("0101010101010101")

        self.BD.append("1100000001010000")
        self.SN.append("0000101000001000")
        self.HH.append("1111111111111111")

        self.BD.append("1001001001000100")
        self.SN.append("0001000000010000")
        self.HH.append("0101110010011110")

        self.BD.append("1001001001000100")
        self.SN.append("0001000000010000")
        self.HH.append("1111111111111111")

        # Triggered when button 2 is released.
        # Short press: Generate random CV for cv4-6
        # Long press: Change operating mode
        @b2.handler_falling
        def b2Pressed():
            
            if (ticks_ms() - b2.last_rising_ms) > 300:
                #print('b2 long press')
                if self.analogInputMode < 3:
                    self.analogInputMode += 1
                else:
                    self.analogInputMode = 1
                #if self.analogInputMode == 1:
                #    self.analogInputMode = 2
                #else:
                #    self.analogInputMode = 1
            else:
                # Move to next cv pattern is already exists, otherwise create a new one
                self.CvPattern += 1
                if self.CvPattern == len(self.random4):
                    self.generateNewRandomCVPattern()
                print('CV Pattern:' + str(self.CvPattern))
                #print('r4 len: ' + str(len(self.random4)))
                #print('r5 len: ' + str(len(self.random5)))
                #print('r6 len: ' + str(len(self.random5)))
            
        # Triggered when button 1 is released
        # Short press: Play previous CV pattern for cv4-6
        # Long press: Toggle random high-hat mode
        @b1.handler_falling
        def b1Pressed():
            #print(ticks_ms() - b1.last_rising_ms)
            if (ticks_ms() - b1.last_rising_ms) > 300:
                #print('b1 long press')
                self.random_HH = not self.random_HH
            else:
                # Play previous CV Pattern, unless we are at the first pattern
                if self.CvPattern != 0:
                    self.CvPattern -= 1

        # Triggered on each clock into digital input. Output triggers.
        @din.handler
        def clockTrigger():
            #self.setClockDivision()
            #self.updateScreen()
            self.last_clock_input = ticks_ms()
            
            if self.clock_step % self.clock_division == 0:
                
                #self.getPattern()
                #self.getRandomness()

                # Set cv4-6 voltage outputs based on previously generated random pattern
                #print(self.random4[self.step])
                cv4.voltage(self.random4[self.CvPattern][self.step])
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
                
                sleep_ms(self.trigger_duration_ms)
                cv1.off()
                cv2.off()
                cv3.off()
    
            if self.clock_step < 128:
                self.clock_step +=1
            else:
                self.clock_step = 0
    
            if self.step < self.step_length - 1:
                self.step += 1
            else:
                self.step = 0

    def generateNewRandomCVPattern(self):
        #self.random4 = self.generateRandomPattern(self.step_length, 0, 9)
        #self.random5 = self.generateRandomPattern(self.step_length, 0, 9)
        #self.random6 = self.generateRandomPattern(self.step_length, 0, 9)

        self.random4.append(self.generateRandomPattern(self.step_length, 0, 9))
        self.random5.append(self.generateRandomPattern(self.step_length, 0, 9))
        self.random6.append(self.generateRandomPattern(self.step_length, 0, 9))

    def getPattern(self):

        # Get the analogue input voltage as a percentage
        pVal = 100 * ain.percent()
        
        # Is there a voltage on the analogue input and are we configured to use it?
        if pVal > 0.4 and self.analogInputMode == 2:
            # Convert percentage value to a representative index of the pattern array
            self.pattern = int((len(self.BD) / 100) * pVal)
        else:
            self.pattern = k2.read_position(len(self.BD))

    def getCvPattern(self):

        # Get the analogue input voltage as a percentage
        CvpVal = 100 * ain.percent()
        
        # Is there a voltage on the analogue input and are we configured to use it?
        #print('CvpVal: ' + str(CvpVal))
        if CvpVal > 0.4 and self.analogInputMode == 3:
            # Convert percentage value to a representative index of the pattern array
            self.CvPattern = int((len(self.random4) / 100) * CvpVal)

    def generateRandomPattern(self, length, min, max):
        self.t=[]
        for i in range(0, length):
            self.t.append(uniform(0,9))
        return self.t


    def getRandomness(self):
        # Check if there is CV on the Analogue input, if not use the k1 position
        rCvVal = 100 * ain.percent()
        if rCvVal > 0.4 and self.analogInputMode == 1:
            self.randomness = rCvVal
        else:
            self.randomness = k1.read_position()

        #print(rCvVal)
        #print(ain.read_voltage())

    def main(self):
        while True:

            #self.setClockDivision()
            self.getPattern()
            self.getRandomness()
            self.getCvPattern()
            self.updateScreen()
            self.reset_timeout = 500
            # If I have been stopped for longer than reset_timeout, reset the steps and clock_step to 0
            if ticks_diff(ticks_ms(), self.last_clock_input) > self.reset_timeout:
                self.step = 0
                self.clock_step = 0
            #sleep_ms(100)

    def setClockDivision(self):
        k1Val = k1.read_position()
        if int(k1Val) <= 1:
            self.clock_division = 1
        elif k1Val >= 90:
            self.clock_division = 32
        elif k1Val >= 80:
            self.clock_division = 16           
        elif k1Val >= 70:
            self.clock_division = 8 
        elif k1Val >= 60:
            self.clock_division = 7
        elif k1Val >= 50:
            self.clock_division = 6           
        elif k1Val >= 40:
            self.clock_division = 5 
        elif k1Val >= 30:
            self.clock_division = 4               
        elif k1Val >= 20:
            self.clock_division = 3 
        else:
            self.clock_division = 2

    def visualizePattern(self, pattern):
        self.t = pattern
        self.t = self.t.replace('1','^')
        self.t = self.t.replace('0',' ')
        return self.t

    def updateScreen(self):
        #oled.clear() - dont use this, it causes the screen to flicker!
        oled.fill(0)
        
        # Show selected pattern visually
        oled.text(self.visualizePattern(self.BD[self.pattern]),0,0,1)
        oled.text(self.visualizePattern(self.SN[self.pattern]),0,10,1)
        oled.text(self.visualizePattern(self.HH[self.pattern]),0,20,1)

        # If the random toggle is on, show a rectangle
        if self.random_HH:
            oled.fill_rect(0,29,20,3,1)

        # Show the analogInputMode
        oled.text('m' + str(self.analogInputMode), 112, 25, 1)
        #if self.analogInputMode == 2:
        #    oled.text('m2', 112, 25, 1)
        #elif self.analogInputMode == 1:
        #    oled.text('m1', 112, 25, 1)
        #else:
        #    oled.text('m3', 112, 25, 1)
        #self.analogInputMode

        # Show CV pattern
        oled.text(str(self.CvPattern), 80, 25, 1)

        oled.show()
        

# Reset module display state.
reset_state()
dm = drumMachine()
dm.main()
