from europi import *
from time import ticks_diff, ticks_ms
from random import randint, uniform
from europi_script import EuroPiScript
import machine
import json
import gc

'''
CVecorder
author: Nik Ansell (github.com/gamecat69)

digital_in: Clock input
analog_in: Incoming CV

button_1: Toggle recording stop/start
button_2: Short Press: Cycle through CV recorder channels. Long Press (0.5 seconds): Clear the current bank. Long Press (2 seconds): Clear all banks.

output_1: CV record / playback
output_2: CV record / playback
output_3: CV record / playback
output_4: CV record / playback
output_5: CV record / playback
output_6: CV record / playback

'''

'''
Ideas / to do:
- Add a morph capability using k2: left reduces CV values, right increases. Don’t adjust all values at once, so odds, then evens with each slight movement
'''

# Needed if using europi_script
class CVecorder(EuroPiScript):
    def __init__(self):
        
        # Needed if using europi_script
        super().__init__()

        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)

        # Micropython heap fragmentation notes:
        # - The pico has very limited memory and in some cases needs to be managed carefully
        # - In some cases you can get a MemoryError even if there is enough free memory, this is because micropython could not find enough contiguous memory because the heap has become fragmented
        # - Avoid heap fragmentation as much as possible by initializing and creating variables early, then updating. Rather than created new and destrying old variables.

        # Initialize variables
        self.step = 0
        self.stepLength = 64
        self.clockStep = 0
        self.ActiveCvr = 0
        self.ActiveBank = 0
        self.resetTimeout = 500
        self.debug = True
        self.CvIn = 0
        self.bankToSave = 0
        self.debugTest = False
        self.writeError = False

        self.numCVR = 5  # Number of CV recorder channels - zero based
        self.numCVRBanks = 5  # Number of CV recording channel banks - zero based

        #self.CVR = []  # CV recorder channels
        #self.CvRecording = []  # CV recorder flags

        # Load CV Recordings from a previously stored state on disk or initialize if blank
        self.loadState()

        # Test routine, pick a random bank n times and save, then load the state
        if self.debugTest:
            #print(micropython.mem_info("level"))
            for n in range(3000):
                # Clear vars
                #self.CvRecording = []
                print(f"Running test: {n}")
                self.ActiveBank = randint(0, self.numCVRBanks)
                self.ActiveCvr = randint(0, self.numCVR)
                for i in range(0, self.stepLength-1):
                    self.CVR[self.ActiveBank][self.ActiveCvr][i] = uniform(0.0, 9.99)
                    #print(f"[{self.ActiveBank}][{self.ActiveCvr}][{i}] = {self.CVR[self.ActiveBank][self.ActiveCvr][i]}")
                self.bankToSave = self.ActiveBank
                self.saveState()
                self.loadState()

        @din.handler
        def dInput():
            self.handleClock()
            self.clockStep +=1

        @din.handler_falling
        def endClock():
            self.handleClock()

        @b1.handler
        def b1Pressed():
            # Set recording boolean to true and clear the recording buffer
            self.CvRecording[self.ActiveCvr] = 'pending'
            # Clear the array
            for n in range (0, self.stepLength):
                self.CVR[self.ActiveBank][self.ActiveCvr][n] = 0

        # B2 Long press
        @b2.handler_falling
        def b2PressedLong():
            # 2000ms press clears all banks
            if ticks_diff(ticks_ms(), b2.last_pressed()) >  2000:
                self.clearCvrs('all')
                #self.bankToSave = self.ActiveBank
                #self.saveState()
                # reverse the ActiveCvr increment caused by the initial button press
                if self.ActiveCvr > 0:
                    self.ActiveCvr -= 1
                else:
                    self.ActiveCvr = self.numCVR
            # 500ms press clears the active bank
            elif ticks_diff(ticks_ms(), b2.last_pressed()) >  500:
                self.clearCvrs(self.ActiveBank)
                self.bankToSave = self.ActiveBank
                self.saveState()
                # reverse the ActiveCvr increment caused by the initial button press
                if self.ActiveCvr > 0:
                    self.ActiveCvr -= 1
                else:
                    self.ActiveCvr = self.numCVR

        # B2 short press
        @b2.handler
        def b2Pressed():
            # Change the active recorder channel
            if self.ActiveCvr < self.numCVR:
                self.ActiveCvr += 1
            else:
                self.ActiveCvr = 0

    def handleClock(self):

        # Sample input to 2 decimal places
        self.CvIn = round(20 * ain.percent(), 2)

        # Start recording if pending and on first step
        if self.step == 0 and self.CvRecording[self.ActiveCvr] == 'pending':
            self.CvRecording[self.ActiveCvr] = 'true'

        for i in range(self.numCVR+1):
            # If recording, write the sampled value to the CVR list and play the voltage
            if self.CvRecording[i] == 'true':
                self.CVR[self.ActiveBank][self.ActiveCvr][self.step] = self.CvIn
                cvs[self.ActiveCvr].voltage(self.CvIn)
            else:
                cvs[i].voltage(self.CVR[self.ActiveBank][i][self.step])

        # Reset step number at stepLength -1 as pattern arrays are zero-based
        if self.step < self.stepLength - 1:
            self.step += 1
        else:
            # Reset step to zero , stop recording and save recording to local storage
            self.step = 0
            if self.CvRecording[self.ActiveCvr] == 'true':
                self.CvRecording[self.ActiveCvr] = 'false'
                self.bankToSave = self.ActiveBank
                self.saveState()

    def clearCvrs(self, bank):
        for b in range(self.numCVRBanks+1):
            # skip bank unless 'all' is passed
            if b != bank and bank != 'all':
                continue
            if self.debugTest:
                print('Clearing bank: ' + str(b))
            # Set all CV values to zero
            for i in range(self.numCVR+1):
                for n in range (0, self.stepLength):
                    self.CVR[b][i][n] = 0
            # Save the cleared bank to local storage
            self.bankToSave = b
            self.saveState()

    # Currently not used, but keeping in this script for future use
    def initCvrs(self):
        for b in range(self.numCVRBanks+1):
            self.CVR.append([])
            for i in range(self.numCVR+1):
                self.CVR[b].append([])
                self.CvRecording.append('false')
                for n in range (0, self.stepLength):
                    self.CVR[b][i].append(0)

    def saveState(self):
        # generate output filename
        outputFile = f"saved_state_{self.__class__.__qualname__}_{self.bankToSave}.txt"

        # Convert each value to an int by multiplying by 100. This saves of storage and memory a little
        for i in range(len(self.CVR[self.bankToSave])):
            self.CVR[self.bankToSave][i] = [int(x * 100) for x in self.CVR[self.bankToSave][i]]

        if self.debugTest:
            print('Saving state for bank: ' + str(self.bankToSave))

        # Trigger garbage collection to minimize memory use
        gc.collect()

        # Show free memory if running a debug test
        if self.debugTest:
            print(self.free())

        # Write the value to a the state file
        maxRetries = 6
        attempts = 0
        while attempts < maxRetries:
            try:
                attempts += 1
                # Create json object of current CV bank
                jsonState = json.dumps(self.CVR[self.bankToSave])
                with open(outputFile, 'w') as file:
                    # Attempt write data to state on disk, then break from while loop if the return (num bytes written) > 0
                    if file.write(jsonState) > 0:
                        self.writeError = False
                        break
            except MemoryError as e:
                self.writeError = True
                if self.debugTest:
                    print(f'[{attempts}] Error: Memory allocation failed, retrying: {e}')
                    #print(micropython.mem_info("level"))
                else:
                    pass

        # Convert from int back to float
        i=0
        for channel in self.CVR[self.bankToSave]:
            self.CVR[self.bankToSave][i] = [x / 100 for x in self.CVR[self.bankToSave][i]]
            i += 1

    def loadState(self):

        # For each bank, check if a state file exists, then load it
        # If not, initialize the bank with zeros

        self.CVR = []  # CV recorder channels
        self.CvRecording = []  # CV recorder flags

        # init cvRecording list
        for i in range(self.numCVR+1):
            self.CvRecording.append('false')

        for b in range(self.numCVRBanks+1):
            # Create a new array for the bank
            self.CVR.append([])

            # Check if a state file exists
            fileName = f"saved_state_{self.__class__.__qualname__}_{b}.txt"
            try:
                # save state exists for this bank, load it
                with open(fileName, 'r') as file:
                    if self.debugTest:
                        print('Loading previous state for bank: ' + str(b))

                    # read state from file into json object
                    jsonData = file.read()

                    # populate CV recording channel with saved json data
                    self.CVR[b] = json.loads(jsonData)

                    # convert values in the list from int back to float
                    i=0
                    for channel in self.CVR[b]:
                        self.CVR[b][i] = [x / 100 if x > 0 else 0 for x in self.CVR[b][i]]
                        i += 1

            except OSError as e:
                # No state file exists, initialize the array with zeros
                if self.debugTest:
                    print('Initializing bank: ' + str(b))

                for i in range(self.numCVR+1):
                    self.CVR[b].append([])
                    for n in range (0, self.stepLength):
                        self.CVR[b][i].append(0)

    # Currently not used, but keeping in this script for future use
    def debugDumpCvr(self):
        for b in range(self.numCVRBanks+1):
            for i in range(self.numCVR+1):
                print(str(b) + ':' + str(i) + ':' + str(self.CVR[b][i]))

    def free(self, full=False):
        #gc.collect()
        F = gc.mem_free()
        A = gc.mem_alloc()
        T = F+A
        P = '{0:.2f}%'.format(F/T*100)
        if not full: return P
        else : return ('Total:{0} Free:{1} ({2})'.format(T,F,P))

    def main(self):
        while True:
            self.getCvBank()
            self.updateScreen()

            # If I have been running, then stopped for longer than reset_timeout, reset the steps and clock_step to 0
            if self.clockStep != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.resetTimeout:
                self.step = 0
                self.clockStep = 0

    def getCvBank(self):
        # Read CV Bank selection from knob 1
        self.ActiveBank = k1.read_position(self.numCVRBanks+1)

    def updateScreen(self):
        # Clear the screen
        oled.fill(0)
                
        # Visualize each CV channel
        lPadding = 4
        # oled.fill_rect(x, y, width, height)
        oled.rect(lPadding+0 , 0, int(self.CVR[self.ActiveBank][0][self.step]*4), 11, 1)
        oled.rect(lPadding+42 , 0, int(self.CVR[self.ActiveBank][1][self.step]*4), 11, 1)
        oled.rect(lPadding+84 , 0, int(self.CVR[self.ActiveBank][2][self.step]*4), 11, 1)
        oled.rect(lPadding+0 , 12, int(self.CVR[self.ActiveBank][3][self.step]*4), 11, 1)
        oled.rect(lPadding+42 , 12, int(self.CVR[self.ActiveBank][4][self.step]*4), 11, 1)
        oled.rect(lPadding+84 , 12, int(self.CVR[self.ActiveBank][5][self.step]*4), 11, 1)

        # Show 'Rec' if recording
        if self.CvRecording[self.ActiveCvr] == 'true':
            oled.text('REC', 71, 25, 1)
        elif self.CvRecording[self.ActiveCvr] == 'pending':
            oled.text('. .', 71, 25, 1)
        
        if self.writeError:
            oled.text('!w!', 71, 25, 1)

        # Active recording channel
        oled.text(str(self.ActiveBank+1) + ':' + str(self.ActiveCvr+1), 100, 25, 1)
        
        # Current step
        oled.rect(lPadding-1, 26, 64, 6, 1)
        oled.fill_rect(lPadding-1, 26, self.step, 6, 1)

        oled.show()

if __name__ == '__main__':
    dm = CVecorder()
    dm.main()