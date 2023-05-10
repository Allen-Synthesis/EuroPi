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

Generates variable length looping patterns of random stepped CV.
Patterns can be linked together into sequences to create rhythmically evolving CV patterns.
Inspired by the Noise Engineering Mimetic Digitalis.

'''

class EgressusMelodium(EuroPiScript):
    def __init__(self):

        # Initialize variables
        self.step = 0
        self.clock_step = 0
        self.minAnalogInputVoltage = 0.5
        self.randomness = 0
        self.CvPattern = 0
        self.numCvPatterns = 4  # Initial number, this can be increased
        self.reset_timeout = 10000
        self.maxRandomPatterns = 4  # This prevents a memory allocation error (happens with > 5, but 4 is nice round number!)
        self.maxCvVoltage = 9  # The maximum is 9 to maintain single digits in the voltage list
        self.patternLength = 16
        self.maxStepLength = 32
        self.screenRefreshNeeded = True
        self.cycleModes = ['0000', '0101', '0001', '0011', '1212', '1112', '1122', '0012', '2323', '2223', '2233', '0123']
        self.cycleMode = False
        self.cycleStep = 0
        self.selectedCycleMode = 0
        self.debugMode = False
        self.dataDumpToScreen = False
        
        self.experimentalSlewMode = True
        self.slewResolution = 80  # number of values in slewArray between clock step voltages
        self.slewArray = []
        self.msBetweenClocks = 0
        self.lastClockTime = 0
        self.lastSlewVoltageOutput = 0
        self.slewGeneratorObject = self.slewGenerator([0])
        self.slewShapes = ['none','log','linear']
        self.slewShape = 0

        self.loadState()

        # Dump the entire CV Pattern structure to screen
        if self.debugMode and self.dataDumpToScreen:
            for idx, output in enumerate(self.cvPatternBanks):
                print(f"Output Channel: {idx}")
                for idx, n in enumerate(output):
                    print(f"  CV Pattern Bank: {idx}")
                    for idx, voltage in enumerate(n):
                        print(f"    Step {idx}: {voltage}")

        @din.handler_falling
        def handleFalingDin():
            cvs[5].off()
        
        '''Triggered on each clock into digital input. Output stepped CV'''
        @din.handler
        def clockTrigger():
            if self.debugMode:
                reset=''
                if self.clock_step % 16 == 0:
                    reset = '*******'
                print(f"[{reset}{self.clock_step}] : [0][{self.CvPattern}][{self.step}][{self.cvPatternBanks[0][self.CvPattern][self.step]}]")
            # Cycle through outputs and output CV voltage based on currently selected CV Pattern and Step
            for idx, pattern in enumerate(self.cvPatternBanks):
                if self.experimentalSlewMode and self.slewShape > 0:
                    if idx == 0:
                        continue
                if idx != 5:
                    cvs[idx].voltage(pattern[self.CvPattern][self.step])
                else:
                    if self.step == self.patternLength - 1:
                        # send end of cycle gate
                        cvs[5].on()

            # Increment / reset step unless we have reached the max step length, or selected pattern length
            if self.step < self.maxStepLength -1 and self.step < self.patternLength -1:
                self.step += 1
            else:
                # Reset step back to 0
                if self.debugMode:
                    print(f'[{self.clock_step}] [{self.step}]reset step to 0')
                self.step = 0
                self.screenRefreshNeeded = True

                # Move to next CV Pattern in the cycle if cycleMode is enabled
                if self.cycleMode:

                    # Advance the cycle step, unless we are at the end, then reset to 0
                    #print(f"cycleStep: {self.cycleStep} vs {int(len(self.cycleModes[self.selectedCycleMode])-1)}")
                    if self.cycleStep < int(len(self.cycleModes[self.selectedCycleMode])-1):
                        self.cycleStep += 1
                    else:
                        self.cycleStep = 0
                    
                    # print(f"Setting next self.CvPattern to {self.cycleModes[self.selectedCycleMode][int(self.cycleStep)]}")
                    self.CvPattern = int(self.cycleModes[self.selectedCycleMode][int(self.cycleStep)])
                    #self.screenRefreshNeeded = True

            # Incremenent the clock step
            self.clock_step +=1
            self.screenRefreshNeeded = True

            # Generate slew voltages between steps,
            # only if we have more than >= 2 clock steps to calculate the time between clocks
            if self.clock_step >= 2:
                self.msBetweenClocks = ticks_ms() - self.lastClockTime
                # Gerate slew voltages between steps
                if self.step == self.patternLength-1:
                    nextStep = 0
                else:
                    nextStep = self.step+1
                if self.slewShapes[self.slewShape] == 'linear':
                    self.slewArray = self.linspace(
                            self.cvPatternBanks[0][self.CvPattern][self.step],
                            self.cvPatternBanks[0][self.CvPattern][nextStep],
                            self.slewResolution
                            )
                elif self.slewShapes[self.slewShape] == 'log':
                    self.slewArray = self.logspace(
                            self.cvPatternBanks[0][self.CvPattern][self.step],
                            self.cvPatternBanks[0][self.CvPattern][nextStep],
                            self.slewResolution
                            )
                else:
                    pass
                self.slewGeneratorObject = self.slewGenerator(self.slewArray)
                #print(f"self.msBetweenClocks: {self.msBetweenClocks}")
                #print(f"slewArray: {self.slewArray}")
            
            self.lastClockTime = ticks_ms()

        '''Triggered when B1 is pressed and released'''
        @b1.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b1.last_pressed()) > 2000 and ticks_diff(ticks_ms(), b1.last_pressed()) < 5000:
                # Generate new pattern for existing pattern
                self.generateNewRandomCVPattern(new=False)
                self.saveState()
            elif ticks_diff(ticks_ms(), b1.last_pressed()) >  300:
                if self.slewShape == len(self.slewShapes)-1:
                    self.slewShape = 0
                else:
                    self.slewShape += 1
                self.screenRefreshNeeded = True
                self.saveState()
                #self.experimentalSlewMode = not self.experimentalSlewMode
            else:
                # Play previous CV Pattern, unless we are at the first pattern
                if self.CvPattern != 0:
                    self.CvPattern -= 1
                    # Update screen with CV Pattern
                    self.screenRefreshNeeded = True
                    if self.debugMode:
                        print('CV Pattern down')

        '''Triggered when B1 is pressed and released'''
        @b2.handler_falling
        def b2Pressed():
            if ticks_diff(ticks_ms(), b2.last_pressed()) > 300 and ticks_diff(ticks_ms(), b2.last_pressed()) < 5000:
                # Toggle cycle mode
                self.cycleMode = not self.cycleMode
                # Update screen with CV Pattern
                self.screenRefreshNeeded = True
            else:
                if self.CvPattern < self.numCvPatterns-1: # change to next CV pattern
                    self.CvPattern += 1
                    # Update screen with CV Pattern
                    self.screenRefreshNeeded = True
                    if self.debugMode:
                        print('CV Pattern up')
                else:
                    # Generate a new CV pattern, unless we have reached the maximum allowed
                    if self.CvPattern < self.maxRandomPatterns-1:
                        if self.generateNewRandomCVPattern():
                            self.CvPattern += 1
                            self.numCvPatterns += 1
                            self.saveState()
                            # Update screen with CV Pattern
                            self.screenRefreshNeeded = True
                            if self.debugMode:
                                print('Generating NEW pattern')

    '''Initialize CV pattern banks'''
    def initCvPatternBanks(self):
        # Init CV pattern banks
        self.cvPatternBanks = [[], [], [], [], [], []]
        for n in range(self.maxRandomPatterns):
            self.generateNewRandomCVPattern(self)
        return self.cvPatternBanks 

    '''Generate new CV pattern for existing bank or create a new bank'''
    def generateNewRandomCVPattern(self, new=True):
        try:
            gc.collect()
            if new:
                for pattern in self.cvPatternBanks:
                    pattern.append(self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage))
            else:
                for pattern in self.cvPatternBanks:
                    pattern[self.CvPattern] = self.generateRandomPattern(self.maxStepLength, 0, self.maxCvVoltage)
            return True
        except Exception:
            return False

    '''Generate a random pattern between min and max of the desired length'''
    def generateRandomPattern(self, length, min, max):
        self.t=[]
        for i in range(0, length):
            self.t.append(round(uniform(min,max),3))
        return self.t


    '''Entry point - main loop'''
    def main(self):
        while True:
            self.updateScreen()
            self.getPatternLength()
            self.getCycleMode()

            # experimental slew mode....
            if self.experimentalSlewMode and self.slewShape > 0 and ticks_diff(ticks_ms(), self.lastSlewVoltageOutput) >= (self.msBetweenClocks / self.slewResolution):
                try:
                    v = next(self.slewGeneratorObject)
                    cvs[0].voltage(v)
                except StopIteration:
                    v = 0
                self.lastSlewVoltageOutput = ticks_ms()
            # If I have been running, then stopped for longer than reset_timeout, reset all steps to 0
            if self.clock_step != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.reset_timeout:
                self.step = 0
                self.clock_step = 0
                self.cycleStep = 0
                if self.numCvPatterns >= int(self.cycleModes[self.selectedCycleMode][self.cycleStep]):
                    self.CvPattern = int(self.cycleModes[self.selectedCycleMode][self.cycleStep])
                # Update screen with the upcoming CV pattern
                self.screenRefreshNeeded = True

    '''Get the CV pattern length from k2 / ain'''
    def getPatternLength(self):
        previousPatternLength = self.patternLength
        val = 100 * ain.percent()
        if val > self.minAnalogInputVoltage:
            self.patternLength = min(int((self.maxStepLength / 100) * val) + k2.read_position(self.maxStepLength), self.maxStepLength-1) + 1
        else:
            self.patternLength = k2.read_position(self.maxStepLength) + 1
        
        if previousPatternLength != self.patternLength:
            self.screenRefreshNeeded = True

    '''Get the cycle mode from k1'''
    def getCycleMode(self):
        previousCycleMode = self.selectedCycleMode
        self.selectedCycleMode = k1.read_position(len(self.cycleModes))
        
        if previousCycleMode != self.selectedCycleMode:
            self.screenRefreshNeeded = True

    ''' Save working vars to a save state file'''
    def saveState(self):
        self.state = {
            "cvPatternBanks": self.cvPatternBanks,
            "cycleMode": self.cycleMode,
            "CvPattern": self.CvPattern,
            "slewShape": self.slewShape
        }
        self.save_state_json(self.state)

    ''' Load a previously saved state, or initialize working vars, then save'''
    def loadState(self):
        self.state = self.load_state_json()
        self.cvPatternBanks = self.state.get("cvPatternBanks", [])
        self.cycleMode = self.state.get("cycleMode", False)
        self.CvPattern = self.state.get("CvPattern", 0)
        self.slewShape = self.state.get("slewShape", 0)
        if len(self.cvPatternBanks) == 0:
            self.initCvPatternBanks()
            if self.debugMode:
                print('Initializing CV Pattern banks')
        else:
            if self.debugMode:
                print(f"Loaded {len(self.cvPatternBanks[0])} CV Pattern Banks")
        
        if self.cycleMode:
            print(f"[loadState]Setting self.CvPattern to {int(self.cycleModes[self.selectedCycleMode][self.cycleStep])}")
            self.CvPattern = int(self.cycleModes[self.selectedCycleMode][self.cycleStep])

        self.saveState()
        # Let the rest of the script know how many pattern banks we have
        self.numCvPatterns = len(self.cvPatternBanks[0])

    '''Update the screen only if something has changed. oled.show() hogs the processor and causes latency.'''
    def updateScreen(self):
        if not self.screenRefreshNeeded:
            return
        # oled.clear() - dont use this, it causes the screen to flicker!
        oled.fill(0)

        # Show the pattern number
        oled.text('P',10, 0, 1)
        oled.text(str(self.CvPattern),10 , 16, 1)

        # Show the pattern length        
        oled.text('Len',30, 0, 1)
        oled.text(f"{str(self.step+1)}/{str(self.patternLength)}",30 , 16, 1)
        
        # Show the pattern sequence
        if self.cycleMode:
            oled.text('Seq',80, 0, 1)
            oled.text(str(self.cycleModes[self.selectedCycleMode]),80 , 16, 1)
            cycleIndicatorPosition = 80 +(self.cycleStep * 8)
            #print('position:', str(cycleIndicatorPosition))
            oled.text('_', cycleIndicatorPosition, 22, 1)

        if self.experimentalSlewMode:
            if self.slewShapes[self.slewShape] == 'log':
                # log
                oled.pixel(123, 9, 1)
                oled.pixel(123, 8, 1)
                oled.pixel(123, 7, 1)
                oled.pixel(124, 6, 1)
                oled.pixel(124, 5, 1)
                oled.pixel(124, 4, 1)
                oled.pixel(124, 3, 1)
                oled.pixel(125, 2, 1)
                oled.pixel(126, 1, 1)
                oled.pixel(127, 1, 1)
                oled.pixel(128, 0, 1)
                oled.pixel(128, 0, 1)
            if self.slewShapes[self.slewShape] == 'linear':
                oled.pixel(120, 9, 1)
                oled.pixel(121, 8, 1)
                oled.pixel(122, 7, 1)
                oled.pixel(123, 6, 1)
                oled.pixel(124, 5, 1)
                oled.pixel(125, 4, 1)
                oled.pixel(126, 3, 1)
                oled.pixel(127, 2, 1)
                oled.pixel(128, 1, 1)

        oled.show()
        self.screenRefreshNeeded = False

    '''Produces an evenly spaced set of num numbers between start and stop using linear transitions'''
    def linspace(self, start, stop, num):
        w = []
        diff = (float(stop) - start)/(num - 1)
        for i in range(num):
            w.append(diff * i + start)
        return w

    '''Produces an evenly spaced set of num numbers between start and stop using logarithmic transitions'''
    def logspace(self, start, stop, num):
        w = []
        for i in range(num-1):
            x = 1 - ((stop - float(start))/(i+1)) + stop
            w.append(x-1)
        w.append(stop)
        return w

    def slewGenerator(self, arr):
        for s in range(len(arr)):
            yield arr[s]

if __name__ == '__main__':
    # Reset module display state.
    [cv.off() for cv in cvs]
    dm = EgressusMelodium()
    dm.main()