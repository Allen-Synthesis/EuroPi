from europi import *
from time import ticks_diff, ticks_ms, sleep
from random import randint, uniform
from europi_script import EuroPiScript
import machine

'''
Probapoly
author: Nik Ansell (github.com/gamecat69)

A polyrhythmic sequencer with probability

digital_in: Clock input
analog_in: TBC

button_1: TBC
button_2: TBC

knob_1: Select upper polyrhythm
knob_2: Select lower polyrhythm

output_1: Gate upper polyrhythm
output_2: Gate lower polyrhythm
output_3: Gate upper polyrhythm (50% probability)
output_4: Gate lower polyrhythm (50% probability)
output_5: Gate upper polyrhythm (25% probability)
output_6: Gate upper polyrhythm (50% probability)

'''

'''
To do:
- Add option to manually control the pattern length using k2 (toggle using B2)
'''

class Poly(EuroPiScript):
    def __init__(self):
        
        # Needed if using europi_script
        super().__init__()

        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)

        # Variables
        self.step = 1
        self.clockStep = 0
        self.resetTimeout = 2000
        self.maxPolyVal = 12
        self.upper = 1
        self.lower = 3
        self.upperBernoulliProb = 50
        self.lowerBernoulliProb = 50
        self.upperProb1 = 50
        self.upperProb2 = 25
        self.lowerProb1 = 50
        self.lowerProb2 = 25
        self.doubleTime = False
        self.manualPatternLength = False
        self.patternLength = self.lcm(self.upper, self.lower)
        self.patternLengthPrevious = self.patternLength

        @din.handler
        def clockRising():
            for cv in cvs:
                cv.off()
            self.updateScreen()
            self.handleClock()
            self.clockStep +=1
            self.step += 1

            # Reached of of pattern, or a shorter patter is now needed, reset step to 0
            if self.step >= self.patternLength + 1:
                self.step = 1

        @din.handler_falling
        def clockFalling():
            for cv in cvs:
                cv.off()
            if self.doubleTime:
                self.updateScreen()
                self.handleClock()
                self.clockStep +=1
                self.step += 1

                # Reached of of pattern, or a shorter patter is now needed, reset step to 0
                if self.step >= self.patternLength + 1:
                    self.step = 1

        @b1.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b1.last_pressed()) >  500:
                # toggle double-time feature
                self.doubleTime = not self.doubleTime
            else:
                # Decrement pattern length by 1
                self.patternLength -= 1
                # Set the pattern length to the previous value for playability
                self.patternLengthPrevious = self.patternLength

        @b2.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b2.last_pressed()) >  500:
                # Reserved for future use
                self.manualPatternLength = not self.manualPatternLength
                if self.manualPatternLength:
                    # Set the pattern length to the previous value for playability, or 32 if not set previously (un changed)
                    if self.patternLengthPrevious == self.patternLength:
                        self.patternLength
                    else:
                        self.patternLength = self.patternLengthPrevious
            else:
                # Increment pattern length by 1
                self.patternLength += 1
                # Set the pattern length to the previous value for playability
                self.patternLengthPrevious = self.patternLength

    def handleClock(self):

        #print(f"[{self.step}] Upper: {self.step % self.upper}")
        #print(f"[{self.step}] Lower: {self.step % self.upper}")
        
        # Play upper gate
        if self.step == 1 or (self.step-1) % self.upper == 0:
            #print(f"[{self.step}]      Upper")
            cv1.value(1)

        # Test 1: Outputs trigger with fixed and unrelated probabilities    
            # if randint(0,99) < self.upperProb1:
            #     cv2.value(1)

            # if randint(0,99) < self.upperProb2:
            #     cv3.value(1)

        # Test 2: Outputs trigger using a Bernoulli distribution
            if randint(0,99) < self.upperBernoulliProb:
                cv2.value(1)
            else:
                cv3.value(1)

        # Play lower gate
        if self.step == 1 or (self.step-1) % self.lower == 0:
            #print(f"[{self.step}] Lower")
            cv4.value(1)

            # Test 1: Outputs trigger with fixed and unrelated probabilities    
            # if randint(0,99) < self.lowerProb1:
            #     cv5.value(1)

            # if randint(0,99) < self.lowerProb2:
            #     cv6.value(1)

        # Test 2: Outputs trigger using a Bernoulli distribution
            if randint(0,99) < self.lowerBernoulliProb:
                cv5.value(1)
            else:
                cv5.value(1)

    # Generate pattern length by finding the lowest common multiple (LCM) and greatest common divisor (GCD)
    # https://www.programiz.com/python-programming/examples/lcm
    def lcm(self, x, y):
        return (x*y)//self.computeGcd(x,y)

    def computeGcd(self, x, y):
        while(y):
            x, y = y, x % y
        return x

    def getUpper(self):
        self.upper = k1.read_position(self.maxPolyVal) + 1

    def getLower(self):
        self.lower = k2.read_position(self.maxPolyVal) + 1

    def updateScreen(self):
        # Clear the screen
        oled.fill(0)
        oled.text(str(self.upper) + ':' + str(self.lower) + ' (' + str(self.step) + '/' + str(self.patternLength) + ')', 0, 0, 1)
        if self.doubleTime:
            oled.text('x2', 0, 24, 1)
        if self.manualPatternLength:
            oled.text('mP', 80, 24, 1)
        oled.show()

    def main(self):
        while True:
            self.getLower()
            self.getUpper()
            if not self.manualPatternLength:
                self.patternLength = self.lcm(self.upper, self.lower)
            #self.patternLength = 16
            #self.updateScreen()

            # If I have been running, then stopped for longer than reset_timeout, reset the steps and clock_step to 0
            if self.clockStep != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.resetTimeout:
                self.step = 1
                self.clockStep = 0
                #print('resetting')

if __name__ == '__main__':
    dm = Poly()
    dm.main()