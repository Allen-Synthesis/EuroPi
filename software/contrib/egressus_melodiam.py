from europi import *
import machine
from time import ticks_diff, ticks_ms
from random import randint, uniform
from europi_script import EuroPiScript
import gc
import math

'''
Egressus Melodium (Stepped Melody)
author: Nik Ansell (github.com/gamecat69)
date: 22-Apr-23
labels: sequencer, CV, randomness

Generates variable length looping patterns of random stepped CV.
Patterns can be linked together into sequences to create rhythmically evolving CV patterns.
Inspired by the Noise Engineering Mimetic Digitalis.

'''

'''
To do:
- Finalize UI controls and OLED
- Remove self.firstStep control
- Add knob histeris blocking?
- Add stepped triangle?
'''

class EgressusMelodium(EuroPiScript):
    def __init__(self):

        # Initialize variables
        self.step = 0
        self.firstStep = 0
        self.clockStep = 0
        self.minAnalogInputVoltage = 0.5
        self.CvPattern = 0
        self.numCvPatterns = 4  # Initial number, this can be increased
        self.resetTimeout = 10000
        self.maxRandomPatterns = 2  # This prevents a memory allocation error (happens with > 5, but 4 is nice round number!)
        self.maxCvVoltage = 9  # The maximum is 9 to maintain single digits in the voltage list
        self.maxStepLength = 32
        self.screenRefreshNeeded = True
        self.cycleModes = ['0000', '0101', '0001', '0011', '1212', '1112', '1122', '0012', '2323', '2223', '2233', '0123']
        self.cycleMode = False
        self.cycleStep = 0
        self.selectedCycleMode = 0
        self.debugMode = False
        self.dataDumpToScreen = False
        self.shreadedVis = False
        self.shreadedVisClockStep = 0
        
        self.slewArray = []
        self.lastClockTime = 0
        self.lastSlewVoltageOutput = 0
        self.slewGeneratorObject = self.slewGenerator([0])
        self.slewGeneratorObjects = [self.slewGenerator([0]), self.slewGenerator([0]), self.slewGenerator([0]), self.slewGenerator([0]), self.slewGenerator([0]), self.slewGenerator([0])]
        self.slewShapes = [self.stepUpStepDown, self.linspace, self.smooth, self.expUpexpDown, self.sharkTooth, self.sharkToothReverse, self.logUpStepDown, self.stepUpExpDown]
        self.voltageExtremes=[0, 10]
        self.slewSampleCounter = 0
        self.outputVoltageFlipFlops = [True, True, True, True, True, True] # Flipflops between self.VoltageExtremes for LFO mode

        self.msBetweenClocks = 0
        self.selectedOutput = 0
        self.maxOutputDivision = 8
        self.lastK1Reading = 0
        self.currentK1Reading = 0
        self.lastK2Reading = 0
        self.currentK2Reading = 0

        self.unClockedMode = False
        self.unClockedModeIndicator = ['', 'U']
        self.minLfoCycleMs = 50

        self.inputClockDiffs = []
        self.bpm = 0

        self.sampleCounter = 0

        # pre-create slew buffers to avoid memory allocation errors
        self.initSlewBuffers()

        self.loadState()

        self.slewResolution = min(40, int(self.msBetweenClocks / 15)) + 1

        # Dump the entire CV Pattern structure to screen
        if self.debugMode and self.dataDumpToScreen:
            for idx, output in enumerate(self.cvPatternBanks):
                print(f"Output Channel: {idx}")
                for idx, n in enumerate(output):
                    print(f"  CV Pattern Bank: {idx}")
                    for idx, voltage in enumerate(n):
                        print(f"    Step {idx}: {voltage}")

        '''Triggered on each clock into digital input'''
        @din.handler
        def clockTrigger():

            if self.debugMode:
                reset=''
                if self.clockStep % 16 == 0:
                    reset = '*******'
                print(f"[{reset}{self.clockStep}] : [0][{self.CvPattern}][{self.step}][{self.cvPatternBanks[0][self.CvPattern][self.step]}]")

            if not self.unClockedMode:
                # Incremenent the clock step
                self.clockStep +=1

                # calculate different between input clock triggers using a 20 value FiFo list (inputClockDiffs)
                newDiffBetweenClocks = ticks_ms() - self.lastClockTime
                self.inputClockDiffs.append(newDiffBetweenClocks)
                # Remove first item to keep only 20 values in the list
                if len(self.inputClockDiffs) == 20:
                    del self.inputClockDiffs[0]

                # Attempt to BPM change and sync to it
                if self.clockStep >= 4:
                    newBpm = self.calculateBpm(self.inputClockDiffs)
                    if abs(newBpm - self.bpm) > 2:
                        self.bpm = newBpm
                        if self.debugMode:
                            print(f'new BPM: {self.bpm}')
                        self.msBetweenClocks = newDiffBetweenClocks
                        self.slewResolution = min(40, int(self.msBetweenClocks / 15)) + 1
                        # Save state every n clock steps
                        if self.clockStep == 2 or self.clockStep % 16 == 0:
                            self.saveState()
            
                self.handleClockStep()

        '''Triggered when B1 is pressed and released'''
        @b1.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b1.last_pressed()) > 2000 and ticks_diff(ticks_ms(), b1.last_pressed()) < 5000:
                # long press
                self.generateNewRandomCVPattern(new=False)
                self.shreadedVis = True
                self.screenRefreshNeeded = True
                self.shreadedVisClockStep = self.clockStep
                self.saveState()
            elif ticks_diff(ticks_ms(), b1.last_pressed()) >  300:
                # medium press
                self.saveState()
            else:
                # short press
                self.selectedOutput = (self.selectedOutput + 1) % 6
                self.screenRefreshNeeded = True
                self.saveState()


        '''Triggered when B2 is pressed and released'''
        @b2.handler_falling
        def b2Pressed():
            if ticks_diff(ticks_ms(), b2.last_pressed()) > 2000 and ticks_diff(ticks_ms(), b2.last_pressed()) < 5000:
                # long press
                self.saveState()
            elif ticks_diff(ticks_ms(), b2.last_pressed()) >  300:
                # medium press
                self.unClockedMode = not self.unClockedMode
                self.clearSlewBuffers()
                self.saveState()
            else:
                # short press
                self.outputSlewModes[self.selectedOutput] = (self.outputSlewModes[self.selectedOutput] + 1) % len(self.slewShapes)
                self.screenRefreshNeeded = True
                self.saveState()

        # '''Triggered when B1 is pressed and released'''
        # @b1.handler_falling
        # def b1Pressed():
        #     if ticks_diff(ticks_ms(), b1.last_pressed()) > 2000 and ticks_diff(ticks_ms(), b1.last_pressed()) < 5000:
        #         # Generate new pattern for existing pattern
        #         self.generateNewRandomCVPattern(new=False)
        #         self.shreadedVis = True
        #         self.screenRefreshNeeded = True
        #         self.shreadedVisClockStep = self.clockStep
        #         self.saveState()
        #     elif ticks_diff(ticks_ms(), b1.last_pressed()) >  300:
        #         self.saveState()
        #     else:
        #         # Play previous CV Pattern, unless we are at the first pattern
        #         if self.CvPattern != 0:
        #             self.CvPattern -= 1
        #             # Update screen with CV Pattern
        #             self.screenRefreshNeeded = True
        #             if self.debugMode:
        #                 print('CV Pattern down')

        # '''Triggered when B1 is pressed and released'''
        # @b2.handler_falling
        # def b2Pressed():
        #     if ticks_diff(ticks_ms(), b2.last_pressed()) > 300 and ticks_diff(ticks_ms(), b2.last_pressed()) < 5000:
        #         # Toggle cycle mode
        #         self.cycleMode = not self.cycleMode
        #         # Update screen with CV Pattern
        #         self.screenRefreshNeeded = True
        #     else:
        #         if self.CvPattern < self.numCvPatterns-1: # change to next CV pattern
        #             self.CvPattern += 1
        #             # Update screen with CV Pattern
        #             self.screenRefreshNeeded = True
        #             if self.debugMode:
        #                 print('CV Pattern up')
        #         else:
        #             # Generate a new CV pattern, unless we have reached the maximum allowed
        #             if self.CvPattern < self.maxRandomPatterns-1:
        #                 if self.generateNewRandomCVPattern():
        #                     self.CvPattern += 1
        #                     self.numCvPatterns += 1
        #                     self.saveState()
        #                     # Update screen with CV Pattern
        #                     self.screenRefreshNeeded = True
        #                     if self.debugMode:
        #                         print('Generating NEW pattern')

    def initSlewBuffers(self):
        self.slewBuffers = []
        for n in range(6): # for each output 0-5
            self.slewBuffers.append([]) # add new empty list to the buffer list
            for m in range(42 * self.maxOutputDivision): # 41 is maximum resolution/samplerate
                self.slewBuffers[n].append(0.0) # add 0.0 (float) as a default value

    def clearSlewBuffers(self):
        for n in range(6): # for each output 0-5
            for m in range(42 * self.maxOutputDivision): # 41 is maximum resolution/samplerate
                self.slewBuffers[n][m] = 0.0 # add 0.0 (float) as a default value

    def bpmFromMs(self, ms):
        return int(((1/(ms/1000))*60)/4)

    def calculateBpm(self, list):
        self.averageDiff = self.average(list)
        return self.bpmFromMs(self.averageDiff)

    def average(self, list):
        myList = list.copy()
        # Remove highest value to help with smoothing
        #myList.remove(max(myList))
        return sum(myList) / len(myList)

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
            self.getK2Value()
            #self.getCycleMode()
            #self.getFirstStep()
            self.getOutputDivision()

            self.slewResolution = min(40, int(self.msBetweenClocks / 15)) + 1
            #self.slewResolution = 40
            if ticks_diff(ticks_ms(), self.lastSlewVoltageOutput) >= (self.msBetweenClocks / self.slewResolution):
                for idx in range(len(cvs)):
                    try:
                        v = next(self.slewGeneratorObjects[idx])
                        cvs[idx].voltage(v)
                        # if idx == 0:
                        #     self.sampleCounter += 1
                        #     print(f'Sample Num: {self.sampleCounter}')
                    except StopIteration:
                        v = 0
                self.slewSampleCounter += 1
                self.lastSlewVoltageOutput = ticks_ms()

                # Trigger a clock step without a din interrupt - free running mode
                if self.unClockedMode and self.slewSampleCounter % self.slewResolution == 0:
                    self.clockStep +=1
                    self.handleClockStep()

            # If I have been running, then stopped for longer than resetTimeout, reset all steps to 0
            if not self.unClockedMode and self.clockStep != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.resetTimeout:
                #self.step = 0
                self.step = self.firstStep
                #self.clockStep = 0
                self.cycleStep = 0
                if self.numCvPatterns >= int(self.cycleModes[self.selectedCycleMode][self.cycleStep]):
                    self.CvPattern = int(self.cycleModes[self.selectedCycleMode][self.cycleStep])
                # Update screen with the upcoming CV pattern
                self.screenRefreshNeeded = True

    '''Advances step and generates voltage slew voltages to next value in CV pattern'''
    def handleClockStep(self):

        # Increment / reset step unless we have reached the max step length, or selected pattern length
        if self.step < self.maxStepLength -1 and self.step < (self.firstStep + self.patternLength) -1:
            self.step += 1
        else:
            # Reset step back to 0
            if self.debugMode:
                print(f'[{self.clockStep}] [{self.step}]reset step to 0')
            #self.step = 0
            self.step = self.firstStep
            #self.screenRefreshNeeded = True

            # Move to next CV Pattern in the cycle if cycleMode is enabled
            if self.cycleMode:

                # Advance the cycle step, unless we are at the end, then reset to 0
                if self.cycleStep < int(len(self.cycleModes[self.selectedCycleMode])-1):
                    self.cycleStep += 1
                else:
                    self.cycleStep = 0
                
                self.CvPattern = int(self.cycleModes[self.selectedCycleMode][int(self.cycleStep)])

        # calculate the next step
        if self.step == (self.firstStep + self.patternLength)-1:
            nextStep = self.firstStep
        else:
            nextStep = self.step+1

        # Cycle through outputs and generate slew for each
        for idx in range(len(cvs)):

            # If the clockstep is a division of the output division
            if self.clockStep % (self.outputDivisions[idx]) == 0:

                # flip the flip flop value for LFO mode
                self.outputVoltageFlipFlops[idx] = not self.outputVoltageFlipFlops[idx]
                
                if not self.unClockedMode:
                    sampleReductionOffset = (self.outputDivisions[idx] - 1)
                else:
                    sampleReductionOffset = 0

                # If length is one, cycle between high and low voltages (traditional LFO)
                # Each output uses a its configured slew shape
                if self.patternLength == 1:
                    self.slewArray = self.slewShapes[self.outputSlewModes[idx]](
                        self.voltageExtremes[int(self.outputVoltageFlipFlops[idx])],
                        self.voltageExtremes[int(not self.outputVoltageFlipFlops[idx])],
                        #(self.slewResolution * self.outputDivisions[idx]), # Increase the sample rate for slower divisions
                        (self.slewResolution * self.outputDivisions[idx]) - (sampleReductionOffset), # Increase the sample rate for slower divisions. '- (self.outputDivisions[idx] - 1)' reduces the chance of not completing all samples before the next clock
                        self.slewBuffers[idx]
                        )
                    # if idx == 0:
                    #     print(f'Asking for a buffer with {self.slewResolution * self.outputDivisions[idx]} values')
                    # self.sampleCounter = 0
                else:
                    self.slewArray = self.slewShapes[self.outputSlewModes[idx]](
                        self.cvPatternBanks[idx][self.CvPattern][self.step],
                        self.cvPatternBanks[idx][self.CvPattern][nextStep],
                        self.slewResolution * self.outputDivisions[idx], # Increase the sample rate for slower divisions
                        self.slewBuffers[idx]
                        )
                self.slewGeneratorObjects[idx] = self.slewGenerator(self.slewArray)
        
        self.lastClockTime = ticks_ms()
        
        # Hide the shreaded visual indicator after 2 clock steps
        if self.clockStep > self.shreadedVisClockStep + 2:
            self.shreadedVis = False

    '''Get the k2 value, update params if changed'''
    def getK2Value(self):
        # previousPatternLength = self.patternLength
        # val = 100 * ain.percent()
        # if val > self.minAnalogInputVoltage:
        #     self.patternLength = min(int((self.maxStepLength / 100) * val) + k2.read_position(self.maxStepLength), self.maxStepLength-1) + 1
        # else:
        #     self.patternLength = k2.read_position(self.maxStepLength) + 1
        
        # if previousPatternLength != self.patternLength:
        #     self.screenRefreshNeeded = True
        #     self.lastK2Reading = self.currentK2Reading
        #     self.saveState()

        self.currentK2Reading = k2.read_position(100) + 1
        
        if self.currentK2Reading != self.lastK2Reading:
            # knob has moved
            if self.unClockedMode:
                # Set LFO speed
                self.msBetweenClocks = self.minLfoCycleMs + (self.currentK2Reading * 5)
            else:
                # Set pattern length
                self.patternLength = int((self.maxStepLength / 100) * (self.currentK2Reading-1)) + 1
                
            # Something changed, update screen and save state
            self.saveState()
            self.screenRefreshNeeded = True
        
        self.lastK2Reading = self.currentK2Reading


    # '''Get the firstStep from k1'''
    # def getFirstStep(self):
    #     previousFirstStep = self.firstStep
    #     self.firstStep = k1.read_position(self.maxStepLength-self.patternLength)
        
    #     if previousFirstStep != self.firstStep:
    #         self.screenRefreshNeeded = True

    '''Get the output division from k1'''
    def getOutputDivision(self):
        #previousOutputDivision = self.outputDivisions[self.selectedOutput]
        self.currentK1Reading = (k1.read_position(self.maxOutputDivision) + 1)
        
        if self.currentK1Reading != self.lastK1Reading:
            self.outputDivisions[self.selectedOutput] = (k1.read_position(self.maxOutputDivision) + 1)
            self.screenRefreshNeeded = True
            self.lastK1Reading = self.currentK1Reading
            self.saveState()

    # '''Get the cycle mode from k1'''
    # def getCycleMode(self):
    #     previousCycleMode = self.selectedCycleMode
    #     self.selectedCycleMode = k2.read_position(len(self.cycleModes))
        
    #     if previousCycleMode != self.selectedCycleMode:
    #         self.screenRefreshNeeded = True

    ''' Save working vars to a save state file'''
    def saveState(self):
        self.state = {
            "cvPatternBanks": self.cvPatternBanks,
            "cycleMode": self.cycleMode,
            "CvPattern": self.CvPattern,
            "outputSlewModes": self.outputSlewModes,
            "outputDivisions": self.outputDivisions,
            "patternLength": self.patternLength,
            "msBetweenClocks": self.msBetweenClocks,
            "unClockedMode": self.unClockedMode
        }
        self.save_state_json(self.state)

    ''' Load a previously saved state, or initialize working vars, then save'''
    def loadState(self):
        self.state = self.load_state_json()
        self.cvPatternBanks = self.state.get("cvPatternBanks", [])
        self.cycleMode = self.state.get("cycleMode", False)
        self.CvPattern = self.state.get("CvPattern", 0)
        self.outputSlewModes = self.state.get("outputSlewModes", [0, 0, 0, 0, 0, 0])
        self.outputDivisions = self.state.get("outputDivisions", [1, 2, 4, 1, 2, 4])
        self.patternLength = self.state.get("patternLength", 1)
        self.msBetweenClocks = self.state.get("msBetweenClocks", 976)
        self.unClockedMode = self.state.get("unClockedMode", True)

        if len(self.cvPatternBanks) == 0:
            self.initCvPatternBanks()
            if self.debugMode:
                print('Initializing CV Pattern banks')
        else:
            if self.debugMode:
                print(f"Loaded {len(self.cvPatternBanks[0])} CV Pattern Banks")
        
        if self.cycleMode:
            self.CvPattern = int(self.cycleModes[self.selectedCycleMode][self.cycleStep])

        self.saveState()
        # Let the rest of the script know how many pattern banks we have
        self.numCvPatterns = len(self.cvPatternBanks[0])

    def draw_wave(self):
        if self.outputSlewModes[self.selectedOutput] == 0: # stepUpStepDown
            oled.vline(3, 24, 8, 1)
            oled.hline(3, 24, 6, 1)
            oled.vline(9, 24, 8, 1)
            oled.hline(9, 31, 6, 1)
            oled.vline(15, 24, 8, 1)
        elif self.outputSlewModes[self.selectedOutput] == 1: # linspace
            oled.pixel(3, 29, 1)
            oled.pixel(4, 28, 1)
            oled.pixel(5, 27, 1)
            oled.pixel(6, 26, 1)
            oled.pixel(7, 25, 1)
            oled.pixel(8, 24, 1)
            oled.pixel(9, 23, 1)
            oled.pixel(10, 24, 1)
            oled.pixel(11, 25, 1)
            oled.pixel(12, 26, 1)
            oled.pixel(13, 27, 1)
            oled.pixel(14, 28, 1)
            oled.pixel(15, 29, 1)
        elif self.outputSlewModes[self.selectedOutput] == 2: # smooth (cosine)
            oled.pixel(3, 23, 1)
            oled.pixel(4, 23, 1)
            oled.pixel(5, 24, 1)
            oled.pixel(6, 25, 1)
            oled.pixel(6, 26, 1)
            oled.pixel(6, 27, 1)
            oled.pixel(7, 28, 1)
            oled.pixel(7, 29, 1)
            oled.pixel(7, 30, 1)
            oled.pixel(8, 31, 1)
            oled.pixel(9, 31, 1)
            oled.pixel(10, 31, 1)
            oled.pixel(11, 30, 1)
            oled.pixel(11, 29, 1)
            oled.pixel(11, 28, 1)
            oled.pixel(12, 27, 1)
            oled.pixel(12, 26, 1)
            oled.pixel(12, 25, 1)
            oled.pixel(13, 24, 1)
            oled.pixel(14, 23, 1)
            oled.pixel(15, 23, 1)
            #oled.pixel(16, 24, 1)
        elif self.outputSlewModes[self.selectedOutput] == 3: # expUpexpDown
            oled.pixel(3, 31, 1)
            oled.pixel(4, 30, 1)
            oled.pixel(5, 30, 1)
            oled.pixel(6, 29, 1)
            oled.pixel(6, 29, 1)
            oled.pixel(6, 27, 1)
            oled.pixel(7, 26, 1)
            oled.pixel(8, 25, 1)
            oled.pixel(8, 24, 1)
            oled.pixel(9, 23, 1)
            oled.pixel(10, 24, 1)
            oled.pixel(10, 25, 1)
            oled.pixel(11, 26, 1)
            oled.pixel(12, 27, 1)
            oled.pixel(12, 28, 1)
            oled.pixel(12, 29, 1)
            oled.pixel(13, 30, 1)
            oled.pixel(14, 30, 1)
            oled.pixel(15, 31, 1)
        elif self.outputSlewModes[self.selectedOutput] == 4: # sharkTooth
            oled.pixel(3, 30, 1)
            oled.pixel(3, 29, 1)
            oled.pixel(3, 28, 1)
            oled.pixel(4, 27, 1)
            oled.pixel(4, 26, 1)
            oled.pixel(5, 25, 1)
            oled.pixel(6, 25, 1)
            oled.pixel(7, 24, 1)
            oled.pixel(8, 24, 1)
            oled.pixel(9, 23, 1)
            oled.pixel(10, 24, 1)
            oled.pixel(10, 25, 1)
            oled.pixel(10, 26, 1)
            oled.pixel(11, 27, 1)
            oled.pixel(11, 28, 1)
            oled.pixel(12, 28, 1)
            oled.pixel(13, 29, 1)
            oled.pixel(14, 29, 1)
            oled.pixel(15, 30, 1)
        elif self.outputSlewModes[self.selectedOutput] == 5: # sharkToothReverse
            oled.pixel(3, 30, 1)
            oled.pixel(4, 29, 1)
            oled.pixel(5, 29, 1)
            oled.pixel(6, 28, 1)
            oled.pixel(7, 28, 1)
            oled.pixel(7, 27, 1)
            oled.pixel(8, 26, 1)
            oled.pixel(8, 25, 1)
            oled.pixel(8, 24, 1)
            oled.pixel(9, 23, 1)
            oled.pixel(10, 24, 1)
            oled.pixel(11, 24, 1)
            oled.pixel(12, 25, 1)
            oled.pixel(13, 25, 1)
            oled.pixel(14, 26, 1)
            oled.pixel(14, 27, 1)
            oled.pixel(15, 28, 1)
            oled.pixel(15, 29, 1)
            oled.pixel(15, 30, 1)
        elif self.outputSlewModes[self.selectedOutput] == 6: # logUpStepDown
            oled.pixel(5, 31, 1)
            oled.pixel(5, 30, 1)
            oled.pixel(6, 29, 1)
            oled.pixel(7, 28, 1)
            oled.pixel(7, 27, 1)
            oled.pixel(8, 26, 1)
            oled.pixel(8, 25, 1)
            oled.pixel(9, 24, 1)
            oled.pixel(10, 23, 1)
            oled.pixel(11, 23, 1)
            oled.pixel(12, 23, 1)
            oled.pixel(13, 33, 1)
            oled.pixel(13, 24, 1)
            oled.pixel(13, 25, 1)
            oled.pixel(13, 26, 1)
            oled.pixel(13, 27, 1)
            oled.pixel(13, 28, 1)
            oled.pixel(13, 29, 1)
            oled.pixel(13, 30, 1)
            oled.pixel(13, 31, 1)
        elif self.outputSlewModes[self.selectedOutput] == 7: # stepUpExpDown
            oled.pixel(5, 31, 1)
            oled.pixel(5, 30, 1)
            oled.pixel(5, 29, 1)
            oled.pixel(5, 28, 1)
            oled.pixel(5, 27, 1)
            oled.pixel(5, 26, 1)
            oled.pixel(5, 25, 1)
            oled.pixel(5, 24, 1)
            oled.pixel(5, 23, 1)
            oled.pixel(6, 23, 1)
            oled.pixel(7, 24, 1)
            oled.pixel(7, 25, 1)
            oled.pixel(8, 26, 1)
            oled.pixel(9, 27, 1)
            oled.pixel(9, 28, 1)
            oled.pixel(10, 29, 1)
            oled.pixel(11, 30, 1)
            oled.pixel(12, 31, 1)
            oled.pixel(13, 31, 1)

    '''Update the screen only if something has changed. oled.show() hogs the processor and causes latency.'''
    def updateScreen(self):

        # Only update if something has changed
        if not self.screenRefreshNeeded:
            return
        # Clear screen
        oled.fill(0)

        oled.fill_rect(0, 0, 20, 32, 0)
        oled.fill_rect(0, 0, 20, 9, 1)
        oled.text(f'{self.selectedOutput + 1}', 6, 1, 0)
        
        number = self.outputDivisions[self.selectedOutput]
        x = 2 if number >= 10 else 6
        oled.text(f'{number}', x, 12, 1)

        self.draw_wave()

        if self.unClockedMode:

            if self.msBetweenClocks != 0:
                oled.text(f"Cycle: {self.msBetweenClocks * 2}ms", 24, 1, 1)
        
        else:

            # Draw pattern length
            row1 = ''
            row2 = ''
            row3 = ''
            row4 = ''
            if self.patternLength > 24:
                # draw two rows
                row1 = '........'
                row2 = '........'
                row3 = '........'
                for i in range(24, self.patternLength):
                    row4 = row4 + '.'
            elif self.patternLength > 16:
                row1 = '........'
                row2 = '........'
                for i in range(16, self.patternLength):
                    row3 = row3 + '.'
            elif self.patternLength > 8:
                row1 = '........'
                for i in range(8, self.patternLength):
                    row2 = row2 + '.'
            else:
                # draw one row
                for i in range(self.patternLength):
                    row1 = row1 + '.'

            xStart = 40
            oled.text(row1,xStart, 0, 1)
            oled.text(row2,xStart, 6, 1)
            oled.text(row3,xStart, 12, 1)
            oled.text(row4,xStart, 18, 1)

        if self.shreadedVis:
            oled.text('x', 22, 12, 1)

        oled.show()

    '''Update the screen only if something has changed. oled.show() hogs the processor and causes latency.'''
    def updateScreenOld(self):
        if not self.screenRefreshNeeded:
            return
        # oled.clear() - dont use this, it causes the screen to flicker!
        oled.fill(0)

        # Show the pattern number
        oled.text('P',10, 0, 1)
        oled.text(str(self.CvPattern),10 , 16, 1)

        # Show the pattern length        
        oled.text('Len',30, 0, 1)
        oled.text(f"{str(self.step+1)}({self.firstStep+1})/{str(self.patternLength)}",30 , 16, 1)
        
        # Show the pattern sequence
        if self.cycleMode:
            oled.text('Seq',80, 0, 1)
            oled.text(str(self.cycleModes[self.selectedCycleMode]),80 , 16, 1)
            cycleIndicatorPosition = 80 +(self.cycleStep * 8)
            oled.text('_', cycleIndicatorPosition, 22, 1)

        if self.shreadedVis:
            oled.text('x',120 ,23)

        oled.show()
        self.screenRefreshNeeded = False

# -----------------------------
# Slew functions
# -----------------------------

    '''Produces step up, step down'''
    def stepUpStepDown(self, start, stop, num, buffer):
        c = 0
        if self.patternLength == 1: # LFO Mode, make sure we complete a full cycle
            for i in range(num/2):
                buffer[c] = start
                c += 1
            for i in range(num/2):
                buffer[c] = stop
                c += 1
        else:
            for i in range(num-1):
                buffer[c] = stop
                c += 1
        return buffer

    '''Produces linear transitions'''
    def linspace(self, start, stop, num, buffer):
        c = 0
        diff = (float(stop) - start)/(num)
        for i in range(num ):
            val = ((diff * i) + start)
            buffer[c] = val
            c += 1
        return buffer

    '''Produces log up, step down'''
    def logUpStepDown(self, start, stop, num, buffer):
        c = 0
        if self.patternLength == 1: # LFO Mode, make sure we complete a full cycle
            for i in range(num/2):
                i = max(i, 1)
                x = 1 - ((stop - float(start))/(i)) + (stop-1)
                buffer[c] = x
                c += 1
            for i in range(num/2):
                buffer[c] = stop
                c += 1
        else:
            if stop >= start:
                for i in range(num-1):
                    i = max(i, 1)
                    x = 1 - ((stop - float(start))/(i)) + (stop-1)
                    buffer[c] = x
                    c += 1
            else:
                for i in range(num-1):
                    buffer[c] = stop
                    c += 1
        return buffer

    '''Produces step up, exp down'''
    def stepUpExpDown(self, start, stop, num, buffer):
        c = 0
        if stop <= start:
            for i in range(num-1):
                i = max(i, 1)
                x = 1 - ((stop - float(start))/(i)) + (stop-1)
                buffer[c] = x
                c += 1
        else:
            for i in range(num):
                buffer[c] = stop
                c += 1
        return buffer

    '''Produces smooth curve using half a cosine wave'''
    def smooth(self, start, stop, sampleRate, buffer):
        c = 0
        freqHz = 0.5 # We want to complete half a cycle
        amplitude = abs((stop - start) / 2) # amplitude is half of the diff between start and stop (this is peak to peak)
        if start <= stop:
            # Starting position is 90 degrees (cos) at 'start' volts
            startOffset = sampleRate
            amplitudeOffset = start
        else:
            # Starting position is 0 degrees (cos) at 'stop' volts
            startOffset = 0
            amplitudeOffset = stop
        for i in range(sampleRate):
            i += startOffset
            val = amplitude + float(amplitude * math.cos(2 * math.pi * freqHz * i / float(sampleRate)))
            buffer[c] = round(val+amplitudeOffset,4)
            c += 1
        return buffer

    '''Produces a pointy exponential wave using a quarter cosine'''
    def expUpexpDown(self, start, stop, sampleRate, buffer):
        c = 0
        freqHz = 0.25 # We want to complete quarter of a cycle
        amplitude = abs((stop - start)) # amplitude is half of the diff between start and stop (this is peak to peak)
        if start <= stop:
            startOffset = sampleRate * 2
            amplitudeOffset = start
            for i in range(sampleRate):
                i += startOffset
                val = amplitude + float(amplitude * math.cos(2 * math.pi * freqHz * i / float(sampleRate)))
                buffer[c] = round(val+amplitudeOffset,4)
                c += 1
        else:
            startOffset = sampleRate
            amplitudeOffset = stop
            for i in range(sampleRate):
                i += startOffset
                val = amplitude + float(amplitude * math.cos(2 * math.pi * freqHz * i / float(sampleRate)))
                buffer[c] = round(val+amplitudeOffset,4)
                c += 1
        return buffer

    '''Produces a log(ish) up and exponential(ish) down using a quarter cosine'''
    def sharkTooth(self, start, stop, sampleRate, buffer):
        c = 0
        freqHz = 0.25 # We want to complete quarter of a cycle
        amplitude = abs((stop - start)) # amplitude is half of the diff between start and stop (this is peak to peak)
        if start <= stop:
            startOffset = sampleRate * 3
            amplitudeOffset = start - amplitude
            for i in range(sampleRate):
                i += startOffset
                val = amplitude + float(amplitude * math.cos(2 * math.pi * freqHz * i / float(sampleRate)))
                buffer[c] = round(val+amplitudeOffset,4)
                c += 1
        else:
            startOffset = sampleRate
            amplitudeOffset = stop
            for i in range(sampleRate):
                i += startOffset
                val = amplitude + float(amplitude * math.cos(2 * math.pi * freqHz * i / float(sampleRate)))
                buffer[c] = round(val+amplitudeOffset,4)
                c += 1
        return buffer

    '''Produces an exponential(ish) up and log(ish) down using a quarter cosine'''
    def sharkToothReverse(self, start, stop, sampleRate, buffer):
        c = 0
        freqHz = 0.25 # We want to complete quarter of a cycle
        amplitude = abs((stop - start)) # amplitude is half of the diff between start and stop (this is peak to peak)
        if start <= stop:
            startOffset = sampleRate * 2
            amplitudeOffset = start
            for i in range(sampleRate):
                i += startOffset
                val = amplitude + float(amplitude * math.cos(2 * math.pi * freqHz * i / float(sampleRate)))
                buffer[c] = round(val+amplitudeOffset,4)
                c += 1
        else:
            startOffset = 0
            amplitudeOffset = 1 - (amplitude - stop + 1)
            for i in range(sampleRate):
                i += startOffset
                val = amplitude + float(amplitude * math.cos(2 * math.pi * freqHz * i / float(sampleRate)))
                buffer[c] = round(val+amplitudeOffset,4)
                c += 1
        return buffer

    def slewGenerator(self, arr):
        for s in range(len(arr)):
            yield arr[s]

if __name__ == '__main__':
    # Reset module display state.
    [cv.off() for cv in cvs]
    dm = EgressusMelodium()
    dm.main()
