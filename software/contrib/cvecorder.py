from europi import *
from time import ticks_diff, ticks_ms, sleep
from random import randint

'''
CVecorder
author: Nik Ansell (github.com/gamecat69)
date: 2022-03-20
labels: sequencer, CV

Multi-channel CV recording and playback.

Note, due to limitations in the RPi, only positive CV can be recorded and played back.

Demo video: TBC

digital_in: Clock input
analog_in: Incoming CV

button_1: Toggle recording stop/start
button_2: Cycle through CV recroder channels

output_1: CV playback
output_2: CV playback
output_3: CV playback
output_4: /1 clock
output_5: /2 clock
output_6: /4 clock

'''

'''
To Do:
- Double sample rate by recording a sample on handler_falling? How would this affect the joystick melodt solution, make it optional?
- Allow the number of steps to be adjusted with a knob?
- Store previously recorded CV tracks and cycle through them with a knob?
'''

# Overclock the Pico for improved performance.
machine.freq(250_000_000)

class cvecorder:
    def __init__(self):

        # Initialize variables
        self.step = 0
        self.stepLength = 32
        self.clockStep = 0
        self.ActiveCvr = 0
        self.resetTimeout = 500
        self.debug = True
        self.CvIn = 0

        # Initialize CV recorder and control channels
        self.numCVR = 2  # Number of CV recorder channels
        self.CVR=[]  # CV recorder channels
        self.CvRecording = []  # CV recorder flags
        self.Visualization = []  # Visualization

        for i in range(self.numCVR+1):
            self.CVR.append([])
            self.CvRecording.append(False)
            for n in range (0, self.stepLength):
                self.CVR[i].append(0)

        @din.handler
        def dInput():

            # Send out clocks
            cv4.on()
            cv5.on() if self.clockStep % 2 == 0 else 0
            cv6.on() if self.clockStep % 4 == 0 else 0

            # Sample input
            self.CvIn = 20 * ain.percent()

            for i in range(self.numCVR+1):

                # If recording, write the sampled value to the CVR list and play the voltage
                if self.CvRecording[i] == True:
                    self.CVR[self.ActiveCvr][self.step] = self.CvIn
                    cvs[self.ActiveCvr].voltage(self.CvIn)
                else:
                    cvs[i].voltage(self.CVR[i][self.step])

            # Reset clock step at 128 to avoid a HUGE integer if running for a long time
            # over a really long period of time this would look like a memory leak
            #if self.clockStep < 128:
            #    self.clockStep +=1
            #else:
            #    self.clockStep = 0
            self.clockStep +=1

            # Reset step number at stepLength -1 as pattern arrays are zero-based
            if self.step < self.stepLength - 1:
                self.step += 1
            else:
                # Reset step to zero and stop recording
                self.step = 0
                self.CvRecording[self.ActiveCvr] = False

        @din.handler_falling
        def endClock():
            cv4.off()
            cv5.off()
            cv6.off()

        @b1.handler
        def b1Pressed():
            # Set recording boolean to true and clear the recording buffer
            self.step = 0
            self.CvRecording[self.ActiveCvr] = True
            # Clear the array
            for n in range (0, self.stepLength):
                self.CVR[self.ActiveCvr][n] = 0

        @b2.handler
        def b2Pressed():
            # Change the active recorder channel
            if self.ActiveCvr < self.numCVR:
                self.ActiveCvr += 1
            else:
                self.ActiveCvr = 0

    def main(self):
        while True:       
            self.updateScreen()

            # If I have been running, then stopped for longer than reset_timeout, reset the steps and clock_step to 0
            if self.clockStep != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.resetTimeout:
                self.step = 0
                self.clockStep = 0

    def updateScreen(self):
        oled.fill(0)
                
        #self.lineLength = int(42 / self.stepLength)
        #self.lineHeight = int(22 / 5)

        # Visualize each CV channel
        for i in range(0, self.stepLength):
            # oled.fill_rect(x, y, width, height)
            oled.fill_rect(0 , int(22-self.CVR[0][self.step]*2), 40, int(self.CVR[0][self.step]*2), 1)
            oled.fill_rect(42, int(22-self.CVR[1][self.step]*2), 40, int(self.CVR[1][self.step]*2), 1)
            oled.fill_rect(84, int(22-self.CVR[2][self.step]*2), 40, int(self.CVR[2][self.step]*2), 1)

        # Show the active CV Recording channel
        if self.CvRecording[self.ActiveCvr]:
            oled.text('Rec', 50, 25, 1)
        oled.text(str(self.ActiveCvr+1), 120, 25, 1)
        oled.text(str(self.step), 0, 25, 1)

        oled.show()

cvr = cvecorder()
cvr.main()  
