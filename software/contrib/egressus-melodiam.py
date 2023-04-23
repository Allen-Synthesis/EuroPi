from europi import *
import machine
from time import ticks_diff, ticks_ms
from random import randint, uniform
from europi_script import EuroPiScript
import gc

'''
Egressus Melodium (Stepped Melody)
author: Nik Ansell (github.com/gamecat69)
date: 22-Apr-23
labels: sequencer, CV, randomness

A CV sequencer based on outputs 4,5&6 from the Consequencer.

Demo video: TBC

digital_in: clock in
analog_in: Adjusts pattern length

knob_1: TBC
knob_2: Set Pattern Length

button_1: Short Press: Select CV Pattern (-). Long Press: TBC
button_2: Short Press: Select CV Pattern (+). Long Press: TBC

output_1: randomly generated CV
output_2: randomly generated CV
output_3: randomly generated CV
output_4: randomly generated CV
output_5: randomly generated CV
output_6: randomly generated CV

'''

class EgressusMelodium(EuroPiScript):
    def __init__(self):

        # Initialize variables
        self.step = 0
        self.clock_step = 0
        self.pattern = 0
        self.minAnalogInputVoltage = 0.5
        self.randomness = 0
        self.CvPattern = 0
        self.reset_timeout = 1000
        self.maxRandomPatterns = 32  # This prevents a memory allocation error
        self.maxCvVoltage = 9  # The maximum is 9 to maintain single digits in the voltage list
        self.patternLength = 16
        self.maxStepLength = 32
        self.screenRefreshNeeded = True

        # Generate random CV patterns
        self.random1 = []
        self.random2 = []
        self.random3 = []
        self.random4 = []
        self.random5 = []
        self.random6 = []
        self.generateNewRandomCVPattern()

        # Triggered on each clock into digital input. Output triggers.
        @din.handler
        def clockTrigger():
            cv1.voltage(self.random1[self.CvPattern][self.step])
            cv2.voltage(self.random2[self.CvPattern][self.step])
            cv3.voltage(self.random3[self.CvPattern][self.step])
            cv4.voltage(self.random4[self.CvPattern][self.step])
            cv5.voltage(self.random5[self.CvPattern][self.step])
            cv6.voltage(self.random6[self.CvPattern][self.step])

            # Incremenent the clock step
            self.clock_step +=1
            # increment / reset step
            if self.step < self.maxStepLength -1 and self.step < self.patternLength -1:
                self.step += 1
            else:
                self.step = 0

        @b1.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b1.last_pressed()) > 2000 and ticks_diff(ticks_ms(), b1.last_pressed()) < 5000:
                pass
            elif ticks_diff(ticks_ms(), b1.last_pressed()) >  300:
                pass
            else:
                # Play previous CV Pattern, unless we are at the first pattern
                if self.CvPattern != 0:
                    self.CvPattern -= 1
                    self.screenRefreshNeeded = True

        @b2.handler_falling
        def b2Pressed():
            if ticks_diff(ticks_ms(), b2.last_pressed()) > 300 and ticks_diff(ticks_ms(), b2.last_pressed()) < 5000:
                pass
            else:
                if self.CvPattern < len(self.random4)-1: # change to next CV pattern
                    self.CvPattern += 1
                    self.screenRefreshNeeded = True
                else:
                    if len(self.random4) < self.maxRandomPatterns: # We need to try and generate a new CV value
                        if self.generateNewRandomCVPattern():
                            self.CvPattern += 1
                            self.screenRefreshNeeded = True

    def generateNewRandomCVPattern(self):
        try:
            gc.collect()
            self.random1.append(self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage))
            self.random2.append(self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage))
            self.random3.append(self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage))
            self.random4.append(self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage))
            self.random5.append(self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage))
            self.random6.append(self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage))
            return True
        except Exception:
            return False

    def generateRandomPattern(self, length, min, max):
        self.t=[]
        for i in range(0, length):
            self.t.append(uniform(min,max))
        return self.t


    def main(self):
        while True:
            self.updateScreen()
            self.getPatternLength()
            # If I have been running, then stopped for longer than reset_timeout, reset the steps and clock_step to 0
            if self.clock_step != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.reset_timeout:
                self.step = 0
                self.clock_step = 0

    def getPatternLength(self):
        previousPatternLength = self.patternLength
        val = 100 * ain.percent()
        if val > self.minAnalogInputVoltage:
            self.patternLength = min(int((len(self.BD) / 100) * val) + k2.read_position(self.maxStepLength), self.maxStepLength-1) + 1
        else:
            self.patternLength = k2.read_position(self.maxStepLength) + 1
        
        if previousPatternLength != self.patternLength:
            self.screenRefreshNeeded = True

    def updateScreen(self):
        if not self.screenRefreshNeeded:
            return
        # oled.clear() - dont use this, it causes the screen to flicker!
        oled.fill(0)

        # # Show selected pattern visually
        # lpos = 8-(self.step*8)
        # oled.text(self.visualizePattern(self.BD[self.pattern], self.BdProb[self.pattern]), lpos, 0, 1)
        # oled.text(self.visualizePattern(self.SN[self.pattern], self.SnProb[self.pattern]), lpos, 10, 1)
        # oled.text(self.visualizePattern(self.HH[self.pattern], self.HhProb[self.pattern]), lpos, 20, 1)

        # # If the random toggle is on, show a rectangle
        # if self.random_HH:
        #     oled.fill_rect(0, 29, 10, 3, 1)

        # # Show self.output4isClock indicator
        # if self.output4isClock:
        #     oled.rect(12, 29, 10, 3, 1)

        # # Show randomness
        # oled.text('R' + str(int(self.randomness)), 26, 25, 1)

        # # Show CV pattern
        # oled.text('C' + str(self.CvPattern), 56, 25, 1)

        # # Show the analogInputMode
        # oled.text('M' + str(self.analogInputMode), 85, 25, 1)

        # Show the pattern number
        oled.text(str(self.CvPattern),10 , 16, 1)
        oled.text(str(self.patternLength),50 , 16, 1)

        oled.show()
        self.screenRefreshNeeded = False

if __name__ == '__main__':
    # Reset module display state.
    [cv.off() for cv in cvs]
    dm = EgressusMelodium()
    dm.main()