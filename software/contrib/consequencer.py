from europi import *
import machine
from time import ticks_diff, ticks_ms
from random import randint, uniform
from europi_script import EuroPiScript
import gc

'''
Consequencer
author: Nik Ansell (github.com/gamecat69)
date: 2022-02-05
labels: sequencer, triggers, drums, randomness

A gate and CV sequencer inspired by Grids from Mutable Instruments that contains pre-loaded drum patterns that can be smoothly morphed from one to another. Triggers are sent from outputs 1 - 3, randomized stepped CV patterns are sent from outputs 4 - 6.
Send a clock to the digital input to start the sequence.

Demo video: https://youtu.be/UwjajP6uiQU

digital_in: clock in
analog_in: Mode 1: Adjusts randomness, Mode 2: Selects gate pattern, Mode 3: Selects stepped CV pattern

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

'''
Version History
March-23    decreased maxRandomPatterns to 32 to avoid crashes on some systems
            pattern is now sum of ain and k2
            randomness is now sum of ain and k1
            added garbage collection to avoid memory allocation errors when creating new random sequences
            scroll pattern on display
            minor pattern updates and reshuffled the order
'''

class Consequencer(EuroPiScript):
    def __init__(self):
        # Initialize sequencer pattern arrays   
        p = pattern()     
        self.BD=p.BD
        self.SN=p.SN
        self.HH=p.HH

        # Initialize sequencer pattern probabiltiies
        self.BdProb = p.BdProb
        self.SnProb = p.SnProb
        self.HhProb = p.HhProb

        # Load and populate probability patterns
        # If the probability string len is < pattern len, automatically fill out with the last digit:
        # - 9   becomes 999999999
        # - 95  becomes 955555555
        # - 952 becomes 952222222 
        for pi in range(len(self.BD)):
            if len(self.BdProb[pi]) < len(self.BD[pi]):
                self.BdProb[pi] = self.BdProb[pi] + (self.BdProb[pi][-1] * (len(self.BD[pi]) - len(self.BdProb[pi])))
        for pi in range(len(self.SN)):
            if len(self.SnProb[pi]) < len(self.SN[pi]):
                self.SnProb[pi] = self.SnProb[pi] + (self.SnProb[pi][-1] * (len(self.SN[pi]) - len(self.SnProb[pi])))
        for pi in range(len(self.HH)):
            if len(self.HhProb[pi]) < len(self.HH[pi]):
                self.HhProb[pi] = self.HhProb[pi] + (self.HhProb[pi][-1] * (len(self.HH[pi]) - len(self.HhProb[pi])))

        # Initialize variables
        self.step = 0
        self.trigger_duration_ms = 50
        self.clock_step = 0
        self.pattern = 0
        self.minAnalogInputVoltage = 0.5
        self.randomness = 0
        self.CvPattern = 0
        self.reset_timeout = 1000
        self.maxRandomPatterns = 32  # This prevents a memory allocation error
        self.maxCvVoltage = 9  # The maximum is 9 to maintain single digits in the voltage list
        self.gateVoltage = 10
        self.gateVoltages = [0, self.gateVoltage]

        # Moved these params into the save/load state pair
        #self.analogInputMode = 1 # 1: Randomness, 2: Pattern, 3: CV Pattern
        #self.random_HH = False
        #self.output4isClock = False
        self.loadState()
        
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
            if ticks_diff(ticks_ms(), b2.last_pressed()) > 300 and ticks_diff(ticks_ms(), b2.last_pressed()) < 5000:
                if self.analogInputMode < 3:
                    self.analogInputMode += 1
                else:
                    self.analogInputMode = 1
                self.saveState()
            else:
                if self.analogInputMode == 3: # Allow changed by CV only in mode 3
                    return

                if self.CvPattern < len(self.random4)-1: # change to next CV pattern
                    self.CvPattern += 1
                else:
                    if len(self.random4) < self.maxRandomPatterns: # We need to try and generate a new CV value
                        if self.generateNewRandomCVPattern():
                            self.CvPattern += 1
            
        # Triggered when button 1 is released
        # Short press: Play previous CV pattern for cv4-6
        # Long press: Toggle random high-hat mode
        @b1.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b1.last_pressed()) > 2000 and ticks_diff(ticks_ms(), b1.last_pressed()) < 5000:
                self.output4isClock = not self.output4isClock
                self.saveState()
            elif ticks_diff(ticks_ms(), b1.last_pressed()) >  300:
                self.random_HH = not self.random_HH
                self.saveState()
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
            # The output will only trigger if the randint() is <= than the probability of the step in BdProb, SnProb and HhProb respectively
            # Random number 0-99
            randomNumber0_99 = randint(0,99)
            # Random number 0-9
            randomNumber0_9 = randomNumber0_99 // 10
            if randomNumber0_99 < self.randomness:
                if randomNumber0_9 <= int(self.BdProb[self.pattern][self.step]):
                    cv1.voltage(self.gateVoltages[randint(0, 1)])
                if randomNumber0_9 <= int(self.SnProb[self.pattern][self.step]):
                    cv2.voltage(self.gateVoltages[randint(0, 1)])
                if randomNumber0_9 <= int(self.HhProb[self.pattern][self.step]):
                    cv3.voltage(self.gateVoltages[randint(0, 1)])
            else:
                if randomNumber0_9 <= int(self.BdProb[self.pattern][self.step]):
                    cv1.voltage(self.gateVoltages[int(self.BD[self.pattern][self.step])])
                if randomNumber0_9 <= int(self.SnProb[self.pattern][self.step]):
                    cv2.voltage(self.gateVoltages[int(self.SN[self.pattern][self.step])])

                # If randomize HH is ON:
                if self.random_HH:
                    cv3.value(randint(0, 1))
                else:
                    if randomNumber0_9 <= int(self.HhProb[self.pattern][self.step]):
                        cv3.voltage(self.gateVoltages[int(self.HH[self.pattern][self.step])])

            # Set cv4-6 voltage outputs based on previously generated random pattern
            if self.output4isClock:
                cv4.voltage(self.gateVoltage)
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

    ''' Save working vars to a save state file'''
    def saveState(self):
        self.state = {
            "analogInputMode": self.analogInputMode,
            "random_HH": self.random_HH,
            "output4isClock": self.output4isClock
        }
        self.save_state_json(self.state)


    ''' Load a previously saved state, or initialize working vars, then save'''
    def loadState(self):
        self.state = self.load_state_json()
        self.analogInputMode = self.state.get("analogInputMode", 1)
        self.random_HH = self.state.get("random_HH", False)
        self.output4isClock = self.state.get("output4isClock", False)
        self.saveState()

    def generateNewRandomCVPattern(self):
        try:
            gc.collect()
            self.random4.append(self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage))
            self.random5.append(self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage))
            self.random6.append(self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage))
            return True
        except Exception:
            return False

    def getPattern(self):
        # If mode 2 and there is CV on the analogue input use it, if not use the knob position
        val = 100 * ain.percent()
        if self.analogInputMode == 2 and val > self.minAnalogInputVoltage:
            self.pattern = int((len(self.BD) / 100) * val)
            self.pattern = min(int((len(self.BD) / 100) * val) + k2.read_position(len(self.BD)), len(self.BD)-1)
        else:
            self.pattern = k2.read_position(len(self.BD))
        
        self.step_length = len(self.BD[self.pattern])

    def getCvPattern(self):
        # If analogue input mode 3, get the CV pattern from CV input
        val = 100 * ain.percent()
        if self.analogInputMode == 3 and val > self.minAnalogInputVoltage:
            # Convert percentage value to a representative index of the pattern array
            self.CvPattern = int((len(self.random4) / 100) * val)

    def generateRandomPattern(self, length, min, max):
        self.t=[]
        for i in range(0, length):
            self.t.append(uniform(0,9))
        return self.t


    def getRandomness(self):
        # If mode 1 and there is CV on the analogue input use it, if not use the knob position
        val = 100 * ain.percent()
        if self.analogInputMode == 1 and val > self.minAnalogInputVoltage:
            self.randomness = min(val + k1.read_position(), 99)
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

    def visualizePattern(self, pattern, prob):
        output=''
        for s in range (len(pattern)):
            if pattern[s] == "1":
                char = '^' if prob[s] == '9' else '-'
                output = output + char
            else:
                output = output + ' '
        return output

    def updateScreen(self):
        # oled.clear() - dont use this, it causes the screen to flicker!
        oled.fill(0)

        # Show selected pattern visually
        lpos = 8-(self.step*8)
        oled.text(self.visualizePattern(self.BD[self.pattern], self.BdProb[self.pattern]), lpos, 0, 1)
        oled.text(self.visualizePattern(self.SN[self.pattern], self.SnProb[self.pattern]), lpos, 10, 1)
        oled.text(self.visualizePattern(self.HH[self.pattern], self.HhProb[self.pattern]), lpos, 20, 1)

        # If the random toggle is on, show a rectangle
        if self.random_HH:
            oled.fill_rect(0, 29, 10, 3, 1)

        # Show self.output4isClock indicator
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

    # Initialize pattern probabilities

    BdProb = []
    SnProb = []
    HhProb = []

    # 11 interesting patterns
    BD.append("1000100010001000")
    SN.append("0000000000000000")
    HH.append("0000000000000000")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000100010001000")
    SN.append("0000000000000000")
    HH.append("0010010010010010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000100010001000")
    SN.append("0000100000000000")
    HH.append("0010010010010010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000100010001000")
    SN.append("0000100000001000")
    HH.append("0010010010010010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000100010001000")
    SN.append("0000100000000000")
    HH.append("0000000000000000")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000100010001000")
    SN.append("0000100000001000")
    HH.append("0000000000000000")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000100010001000")
    SN.append("0000100000001000")
    HH.append("0000100010001001")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000100010001000")
    SN.append("0000100000001000")
    HH.append("1010101010101010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000100010001000")
    SN.append("0000000000000000")
    HH.append("1111111111111111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000100010001000")
    SN.append("0000100000001000")
    HH.append("1111111111111111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000100010001000")
    SN.append("0000100000000000")
    HH.append("0001001000000000")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    # 10 commonly found patterns
    # Source: https://docs.google.com/spreadsheets/d/19_3BxUMy3uy1Gb0V8Wc-TcG7q16Amfn6e8QVw4-HuD0/edit#gid=0
    BD.append("1000000010000000")
    SN.append("0000100000001000")
    HH.append("1010101010101010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1010001000100100")
    SN.append("0000100101011001")
    HH.append("0000000100000100")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000000110000010")
    SN.append("0000100000001000")
    HH.append("1010101110001010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1100000100110000")
    SN.append("0000100000001000")
    HH.append("1010101010101010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000000110100000")
    SN.append("0000100000001000")
    HH.append("0010101010101010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1010000000110001")
    SN.append("0000100000001000")
    HH.append("1010101010101010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000000110100001")
    SN.append("0000100000001000")
    HH.append("0000100010101011")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1001001010000000")
    SN.append("0000100000001000")
    HH.append("0000100000001000")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1010001001100000")
    SN.append("0000100000001000")
    HH.append("1010101010001010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1010000101110001")
    SN.append("0000100000001000")
    HH.append("1010101010001010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    # 5 interesting patterns?
    BD.append("1000100010001000")
    SN.append("0000101001001000")
    HH.append("1010101010101010")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1100000001010000")
    SN.append("0000101000001000")
    HH.append("0101010101010101")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1100000001010000")
    SN.append("0000101000001000")
    HH.append("1111111111111111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1001001001000100")
    SN.append("0001000000010000")
    HH.append("0101110010011110")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1001001001000100")
    SN.append("0001000000010000")
    HH.append("1111111111111111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    # 5 Mixed probability patterns
    BD.append("10111111111100001011000000110000")
    SN.append("10001000100010001010000001001000")
    HH.append("10101010101010101010101010101010")
    BdProb.append("99992111129999999999999999969999")
    SnProb.append("95")
    HhProb.append("92939495969792939495969792939492")

    BD.append("10111111111100001011000000110000")
    SN.append("10001000100010001010000001001000")
    HH.append("11111111111111111111111111111111")
    BdProb.append("99992222229999999999999999999999")
    SnProb.append("95")
    HhProb.append("44449999555599996666999922229999")

    BD.append("1000100010001000")
    SN.append("0000101001001000")
    HH.append("0101010101010101")
    BdProb.append("999995")
    SnProb.append("5")
    HhProb.append("99995")

    BD.append("1000110010001100")
    SN.append("0000101001001000")
    HH.append("1111111111111111")
    BdProb.append("9999939999999299")
    SnProb.append("9")
    HhProb.append("9293949592939495")

    BD.append("1000100010001000")
    SN.append("0000101000001000")
    HH.append("1111111111111111")
    BdProb.append("9")
    SnProb.append("9999995999999999")
    HhProb.append("9293949592939495")

    # 5 African Patterns
    BD.append("10110000001100001011000000110000")
    SN.append("10001000100010001010100001001010")
    HH.append("00001011000010110000101100001011")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("10101010101010101010101010101010")
    SN.append("00001000000010000000100000001001")
    HH.append("10100010101000101010001010100000")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("11000000101000001100000010100000")
    SN.append("00001000000010000000100000001010")
    HH.append("10111001101110011011100110111001")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("10001000100010001000100010001010")
    SN.append("00100100101100000010010010110010")
    HH.append("10101010101010101010101010101011")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("10010100100101001001010010010100")
    SN.append("00100010001000100010001000100010")
    HH.append("01010101010101010101010101010101")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    # 13 patterns with < 16 steps - can sound disjointed when using CV to select the pattern!

    BD.append("10010000010010")
    SN.append("00010010000010")
    HH.append("11100110111011")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1001000001001")
    SN.append("0001001000001")
    HH.append("1110011011101")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("100100000100")
    SN.append("000100100000")
    HH.append("111001101110")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("10010000010")
    SN.append("00010010000")
    HH.append("11100110111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("10010000010")
    SN.append("00010010000")
    HH.append("11111010011")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1001000010")
    SN.append("0001000000")
    HH.append("1111101101")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("100100010")
    SN.append("000100000")
    HH.append("111110111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("10010010")
    SN.append("00010000")
    HH.append("11111111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1001001")
    SN.append("0001000")
    HH.append("1111111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("100100")
    SN.append("000100")
    HH.append("111111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("10000")
    SN.append("00001")
    HH.append("11110")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

    BD.append("1000")
    SN.append("0000")
    HH.append("1111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9595")

    BD.append("100")
    SN.append("000")
    HH.append("111")
    BdProb.append("9")
    SnProb.append("9")
    HhProb.append("9")

if __name__ == '__main__':
    # Reset module display state.
    [cv.off() for cv in cvs]
    dm = Consequencer()
    dm.main()


