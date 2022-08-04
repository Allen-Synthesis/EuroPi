from europi import *
import machine
from time import ticks_diff, ticks_ms
from europi_script import EuroPiScript
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from random import randint

'''
Master Clock
author: Nik Ansell (github.com/gamecat69)
date: 2022-08-02
labels: clock, divider

A master clock and clock divider. Each output sends a +5V trigger/gate at different divisions of the master clock, or randomly if condigured with a division of zero.
Pulse width (gate/trigger duration) is configurable up to a maximum of 50% of the pulse width of output 1.

All configuration (BPM, Pulse Width, output clock divisions) is automatically saved, then loaded when the module is restarted.

For wonky/more interesting clock patterns try these:
- Reset to step 1 using a gate into the digital input, or by using an odd value for the maximum division
- Vary BPM by sending CV into the analog input
- Set the division to zero for an output, this will cause the output to randomly go from high (+5V) to low (0V)

Demo video: TBC

digital_in: (optional) Reset step count on rising edge
analog_in: (optional) Adjust BPM

knob_1: Screen 2: Adjust BPM. Screen 3: Select output to edit 
knob_2: Screen 2: Adjust Pulse width. Screen 3: Adjust division of selected output 

button_1: Start / Stop
button_2: Short Press (<500ms): Cycle through screens. Long Press (>500ms): Enter config mode

Defaults:
output_1: clock / 1
output_2: clock / 2
output_3: clock / 4
output_4: clock / 8
output_5: clock / 16
output_6: clock / 32

Known Issues:
- If playback is restarted while screen 2 is in config mode, playback will be slightly irratic

'''

class MasterClockInner(EuroPiScript):
    def __init__(self):
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)
        self.step = 1
        self.completedCycles = 0
        self.running = True
        self.CLOCKS_PER_QUARTER_NOTE = 4
        self.MIN_BPM = 20  # Successfully calibrated to >= 20 and <= 240 BPM
        self.MAX_BPM = 240
        self.MIN_PULSE_WIDTH = 8
        self.resetTimeout = 2000
        self.previousStepTime = 0
        self.minAnalogInputVoltage = 0.9
        self.screen = 2
        self.configMode = False
        self.screenIndicator = ['.  ', ' . ', '  .' ]

        self.MAX_DIVISION = 128
        self.clockDivisions = []
        for n in range(self.MAX_DIVISION+1):
            self.clockDivisions.append(n)
        
        # When enabled, set msDriftCompensation to 30
        # When disabled, set msDriftCompensation to 28
        self.DEBUG = False

        # In testing a 28ms drift was found at all tempos
        # Adding this offset brings the BPM and pulse width back into a reasonable tolerance
        self.msDriftCompensation = 28

        # Vars to drive UI on screen3
        self.markerPositions = [ [0, 0], [69, 0], [0, 12], [40, 12], [80, 12], [0, 24], [40, 24], [80, 24]]
        self.activeOption = 1
        self.previousSelectedDivision = ''

        # Get working vars
        self.loadState()
        self.calcSleepTime()
        self.getPulseWidth()

        # Get asyncio event loop object
        self.el = asyncio.get_event_loop()
        #self.el.run_forever()

        # Starts/Stops the master clock
        @b1.handler_falling
        def StartStop():
            self.running = not self.running

        # Cycle screen and toggle config mode
        @b2.handler_falling
        def cycleScreen():
            if ticks_diff(ticks_ms(), b2.last_pressed()) > 500 and ticks_diff(ticks_ms(), b2.last_pressed()) < 4000:
                self.configMode = not self.configMode
                self.running = False
                if not self.configMode:
                    # config mode has just been turned off, save state
                    self.saveState()
            else:
                # Turn off config mode to avoid current knob positions messing up other settings on the next screen
                if self.configMode:
                    self.configMode = False

                if self.screen == 1:
                    self.screen = 2
                elif self.screen == 2:
                    self.screen = 1
                else:
                    self.screen = 1

        
        # Reset step count upon receiving a din voltage
        @din.handler
        def resetDin():
            self.step = 1

    '''Show running status'''
    def screen1(self):
        oled.fill(0)
        #oled.text(self.screenIndicator[self.screen-1], 100, 23, 1)
        oled.text(str(self.completedCycles) + ':' + str(self.step), 0, 0, 1)
        if not self.running:
            oled.text('B1:Start', 0, 23, 1)
        else:
            oled.text('B1:Stop', 0, 23, 1)
        oled.show()

    '''Configure BPM and Pulse Width'''
    def screen2_old(self):
        oled.fill(0)
        oled.text(self.screenIndicator[self.screen-1], 100, 23, 1)
        if self.configMode:
            oled.text('*', 120, 0, 1)
            self.getBPM()
            self.calcSleepTime()
            self.getPulseWidth()
            self.saveState()
        
        oled.text('BPM: ' + str(self.bpm), 0, 1, 1)
        oled.text('PW: ' + str(self.pulseWidthPercent) + '%/' + str(self.pulseWidthMs) + 'ms', 0, 12, 1)
        oled.show()

    '''new screen testing'''
    def screen2(self):
        # k1 adjusts selected option
        self.activeOption = k1.choice([1, 2, 3, 4, 5, 6, 7, 8])
        oled.fill(0)
        if self.configMode:
            configMarker = '|'
            if self.activeOption == 1:
                # BPM
                self.bpm = self.MIN_BPM + k2.read_position(steps=(self.MAX_BPM - self.MIN_BPM + 1), samples=512)
            elif self.activeOption == 2:
                # Pulse Width
                self.calcSleepTime()
                self.MAX_PULSE_WIDTH = self.timeToSleepMs // 2  # Maximum of 50% pulse width
                # Get desired PW percent
                self.pulseWidthPercent = k2.read_position(steps=50, samples=512) + 1
                # Calc Pulse Width duration (x 2 needed because the max is 50%)
                self.pulseWidthMs = int((self.MAX_PULSE_WIDTH * 2) * (self.pulseWidthPercent / 100)) 
                # Don't allow a pulse width less than the minimum
                if self.pulseWidthMs < self.MIN_PULSE_WIDTH:
                    self.pulseWidthMs = self.MIN_PULSE_WIDTH
                    self.pulseWidthPercent = 'm'
            elif self.activeOption > 2:
                # k2 adjusts clock division
                selectedDivision = k2.choice(self.clockDivisions)

                # Only adjust values if k2 has moved. This avoids a potentially annoying UX
                if self.previousSelectedDivision != selectedDivision:
                    if self.activeOption == 4:
                        self.divisionOutput2 = selectedDivision
                    elif self.activeOption == 5:
                        self.divisionOutput3 = selectedDivision
                    elif self.activeOption == 6:
                        self.divisionOutput4 = selectedDivision
                    elif self.activeOption == 7:
                        self.divisionOutput5 = selectedDivision
                    elif self.activeOption == 8:
                        self.divisionOutput6 = selectedDivision
                
                self.previousSelectedDivision = selectedDivision

            #oled.text('|', 62, 0, 1)
            #self.getBPM()
            #self.calcSleepTime()
            #self.getPulseWidth()
            #self.saveState()
        else:
            configMarker = '.'

        oled.text(str(self.bpm) + ' bpm', 6, 0, 1)
        oled.text(str(self.pulseWidthPercent) + ':' + str(str(self.pulseWidthMs)), 75, 0, 1)
        oled.text('/1', 6, 12, 1)
        oled.text('/' + str(self.divisionOutput2), 45, 12, 1)
        oled.text('/' + str(self.divisionOutput3), 85, 12, 1)
        oled.text('/' + str(self.divisionOutput4), 6, 24, 1)
        oled.text('/' + str(self.divisionOutput5), 45, 24, 1)
        oled.text('/' + str(self.divisionOutput6), 85, 24, 1)
        oled.text(configMarker, self.markerPositions[self.activeOption-1][0], self.markerPositions[self.activeOption-1][1], 1)
        oled.show() 

    '''Configure clock divisions'''
    def screen3_old(self):
        lPadding1 = 5
        lPadding2 = 58
        # k1 adjusts selected option
        self.activeOption = k1.choice([2, 3, 4, 5, 6])
        oled.fill(0)
        oled.text(self.screenIndicator[self.screen-1], 100, 23, 1)
        if self.configMode:
            oled.text('*', 120, 0, 1)

            # k2 adjusts clock division
            selectedDivision = k2.choice(self.clockDivisions)

            # Only adjust values if k2 has moved. This avoids a potentially annoying UX
            if self.previousSelectedDivision != selectedDivision:
                if self.activeOption == 2:
                    self.divisionOutput2 = selectedDivision
                elif self.activeOption == 3:
                    self.divisionOutput3 = selectedDivision
                elif self.activeOption == 4:
                    self.divisionOutput4 = selectedDivision
                elif self.activeOption == 5:
                    self.divisionOutput5 = selectedDivision
                elif self.activeOption == 6:
                    self.divisionOutput6 = selectedDivision
                self.saveState()
            
            self.previousSelectedDivision = selectedDivision

        oled.text('1:/1', lPadding1, 1, 1)
        oled.text('2:/' + str(self.divisionOutput2), lPadding1, 11, 1)
        oled.text('3:/' + str(self.divisionOutput3), lPadding1, 21, 1)
        oled.text('4:/' + str(self.divisionOutput4), lPadding2, 1, 1)
        oled.text('5:/' + str(self.divisionOutput5), lPadding2, 11, 1)
        oled.text('6:/' + str(self.divisionOutput6), lPadding2, 21, 1)
        oled.text('|', self.markerPositions[self.activeOption-1][0], self.markerPositions[self.activeOption-1][1], 1)
        oled.show()

    ''' Holds given output (cv) high for pulseWidthMs duration '''
    async def outputPulse(self, cv):
        cv.voltage(5)
        await asyncio.sleep_ms(self.pulseWidthMs)
        cv.off()

    ''' Given a desired BPM, calculate the time to sleep between clock pulses '''
    def calcSleepTime(self):
        self.timeToSleepMs = int((60000 / self.bpm / self.CLOCKS_PER_QUARTER_NOTE))
    
    def checkForAinBPM(self):
        val = 100 * ain.percent()
        # If there is an analogue input voltage use that for BPM
        if val > self.minAnalogInputVoltage:
            self.bpm = int((((self.MAX_BPM) / 100) * val) + self.MIN_BPM)
            self.calcSleepTime()
            self.getPulseWidth()      

    def getBPM(self):
        self.bpm = self.MIN_BPM + k1.read_position(steps=(self.MAX_BPM - self.MIN_BPM + 1), samples=512)

    def getPulseWidth(self):
        self.MAX_PULSE_WIDTH = self.timeToSleepMs // 2  # Maximum of 50% pulse width
        if self.configMode:
            # Get desired PW percent
            self.pulseWidthPercent = k2.read_position(steps=50, samples=512) + 1
            # Calc Pulse Width duration (x 2 needed because the max is 50%)
            self.pulseWidthMs = int((self.MAX_PULSE_WIDTH * 2) * (self.pulseWidthPercent / 100)) 
            # Don't allow a pulse width less than the minimum
            if self.pulseWidthMs < self.MIN_PULSE_WIDTH:
                self.pulseWidthMs = self.MIN_PULSE_WIDTH
                self.pulseWidthPercent = 'm'
        else:
            self.pulseWidthMs = int((self.MAX_PULSE_WIDTH * 2) * (self.pulseWidthPercent / 100))

    ''' Triggered by main. Sends output pulses at required division '''
    def clockTrigger(self):

        if self.DEBUG:
            print('BPM: ' + str(self.bpm) + ' cycle: ' + str(self.timeToSleepMs) + ' PW:' + str(self.pulseWidthMs))

        self.el.create_task(self.outputPulse(cv1))

        if self.divisionOutput2 != 0:
            if self.step % self.divisionOutput2 == 0:
                self.el.create_task(self.outputPulse(cv2))
        else:
            # 0 = random
            cv2.value(randint(0, 1))

        if self.divisionOutput3 != 0:
            if self.step % self.divisionOutput3 == 0:
                self.el.create_task(self.outputPulse(cv3))
        else:
            # 0 = random
            cv3.value(randint(0, 1))

        if self.divisionOutput4 != 0:
            if self.step % self.divisionOutput4 == 0:
                self.el.create_task(self.outputPulse(cv4))
        else:
            # 0 = random
            cv4.value(randint(0, 1))

        if self.divisionOutput5 != 0:
            if self.step % self.divisionOutput5 == 0:
                self.el.create_task(self.outputPulse(cv5))
        else:
            # 0 = random
            cv5.value(randint(0, 1))

        if self.divisionOutput6 != 0:
            if self.step % self.divisionOutput6 == 0:
                self.el.create_task(self.outputPulse(cv6))
        else:
            # 0 = random
            cv6.value(randint(0, 1))

        # advance/reset clock step, resetting at the maximum configured division
        maxConfiguredDivision = max(self.divisionOutput2, self.divisionOutput3, self.divisionOutput4, self.divisionOutput5, self.divisionOutput6)
        if self.step < maxConfiguredDivision:
            self.step += 1
        else:
            self.completedCycles += 1
            self.step = 1
        
        # Get time of last step to use in the auto reset function
        self.previousStepTime = ticks_ms()

    ''' Save working vars to a save state file'''
    def saveState(self):
        state = {
            "bpm": self.bpm,
            "pulseWidthPercent": self.pulseWidthPercent,
            "divisionOutput2": self.divisionOutput2,
            "divisionOutput3": self.divisionOutput3,
            "divisionOutput4": self.divisionOutput4,
            "divisionOutput5": self.divisionOutput5,
            "divisionOutput6": self.divisionOutput6
        }
        self.save_state_json(state)
        if self.DEBUG:
            print('State saved')

    ''' Load a previously saved state, or initialize working vars, then save'''
    def loadState(self):

        state = self.load_state_json()

        self.bpm = state.get("bpm", 100)
        self.pulseWidthPercent = state.get("self.pulseWidthPercent", 50)

        self.divisionOutput2 = state.get("divisionOutput2", 2)
        self.divisionOutput3 = state.get("divisionOutput3", 4)
        self.divisionOutput4 = state.get("divisionOutput4", 8)
        self.divisionOutput5 = state.get("divisionOutput5", 16)
        self.divisionOutput6 = state.get("divisionOutput6", 32)

        self.saveState()

    async def main(self):
        while True:

            # Display selected screen
            if self.screen == 1:
                self.screen1()
            else:
                self.screen2()
            #else:
                #self.screen3()

            # Auto reset function after resetTimeout
            if self.step != 0 and ticks_diff(ticks_ms(), self.previousStepTime) > self.resetTimeout:
                 self.step = 1
                 self.completedCycles = 0

            if not self.configMode:
                self.checkForAinBPM()

            if self.running:
                self.clockTrigger()
                self.calcSleepTime()
                await asyncio.sleep_ms(int(self.timeToSleepMs - self.msDriftCompensation))


class MasterClock(EuroPiScript):
    def __init__(self):
        pass
    def main(self):
        mc = MasterClockInner()
        el = asyncio.get_event_loop()
        el.create_task(mc.main())
        el.run_forever()

if __name__ == '__main__':
    m = MasterClock()
    m.main()



