from europi import *
from time import ticks_diff, ticks_ms

'''
CVecorder
author: Nik Ansell (github.com/gamecat69)
date: 2022-04-04
labels: sequencer, CV

Multi-channel CV recording and playback.

Note, due to limitations in the RPi, only positive CV can be recorded and played back.

Demo video: https://youtu.be/Crj0P7pr2YA

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
# Overclock the Pico for improved performance.
machine.freq(250_000_000)

class cvecorder:
    def __init__(self):

        # Initialize variables
        self.step = 0
        self.stepLength = 64
        self.clockStep = 0
        self.ActiveCvr = 0
        self.ActiveBank = 0
        self.resetTimeout = 500
        self.debug = True
        self.CvIn = 0
        self.random_HH = False
        self.justBooted = True

        # Initialize CV recorder and control channels
        self.numCVR = 5  # Number of CV recorder channels - zero based
        self.CVR = []  # CV recorder channels
        self.CvRecording = []  # CV recorder flags
        self.numCVRBanks = 5  # Number of CV recording channel banks - zero based
        self.initCvrs()

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
                # reverse the ActiveCvr increment caused by the initial button press
                if self.ActiveCvr > 0:
                    self.ActiveCvr -= 1
                else:
                    self.ActiveCvr = self.numCVR
            # 500ms press clears the active bank
            elif ticks_diff(ticks_ms(), b2.last_pressed()) >  500:
                self.clearCvrs(self.ActiveBank)
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

        # Sample input
        self.CvIn = 20 * ain.percent()

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
            # Reset step to zero and stop recording
            self.step = 0
            if self.CvRecording[self.ActiveCvr] == 'true':
                self.CvRecording[self.ActiveCvr] = 'false'

    def clearCvrs(self, bank):
        for b in range(self.numCVRBanks+1):
            if b != bank and bank != 'all':
                continue
            print('Clearing bank: ' + str(b))
            for i in range(self.numCVR+1):
                for n in range (0, self.stepLength):
                    self.CVR[b][i][n] = 0

    def initCvrs(self):
        for b in range(self.numCVRBanks+1):
            self.CVR.append([])
            for i in range(self.numCVR+1):
                self.CVR[b].append([])
                self.CvRecording.append('false')
                for n in range (0, self.stepLength):
                    self.CVR[b][i].append(0)

    def main(self):
        while True:
            self.getCvBank()
            self.updateScreen()

            # If I have been running, then stopped for longer than reset_timeout, reset the steps and clock_step to 0
            if self.clockStep != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.resetTimeout:
                self.step = 0
                self.clockStep = 0

    def getCvBank(self):
        self.ActiveBank = k1.read_position(self.numCVRBanks+1)

    def updateScreen(self):
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

        # Active recording channel
        oled.text(str(self.ActiveBank+1) + ':' + str(self.ActiveCvr+1), 100, 25, 1)
        
        # Current step
        oled.rect(lPadding-1, 26, 64, 6, 1)
        oled.fill_rect(lPadding-1, 26, self.step, 6, 1)

        oled.show()

cvr = cvecorder()
cvr.main()  
