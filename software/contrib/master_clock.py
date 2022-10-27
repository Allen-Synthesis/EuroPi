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
- If playback is restarted while screen 2 is in config mode, playback will be slightly irratic, especially when moving knobs
- BPM occasionally drifts by 1ms - possibly because asyncio is is truely async

'''

class MasterClockInner(EuroPiScript):
    def __init__(self):
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)
        self.step = 1
        self.completedCycles = 0
        self.running = True
        self.resetTimeout = 2000
        self.previousStepTime = 0
        self.screen = 2
        self.configMode = False
        self.k2Unlocked = False
        self.previousSelectedDivision = 0
        self.previousActiveOption = ''

        self.MIN_BPM = 20  # Successfully calibrated to >= 20 and <= 240 BPM
        self.MAX_BPM = 240
        self.MIN_PULSE_WIDTH = 8
        self.MIN_AIN_VOLTAGE = 1.1
        self.MAX_DIVISION = 128
        self.MAX_PW_PERCENTAGE = 80
        self.CLOCKS_PER_QUARTER_NOTE = 4

        # Create list of available clock divisions
        self.clockDivisions = []
        for n in range(self.MAX_DIVISION+1):
            self.clockDivisions.append(n)
        
        # When enabled, set msDriftCompensation to 30
        # When disabled, set msDriftCompensation to 28
        self.DEBUG = False

        # In testing a 17ms drift was found at all tempos and a 25ms drift when editing BPM/PW
        # Adding this offset brings the BPM and pulse width back into a reasonable tolerance
        # self.msDriftCompensationConfigMode is an additional offset if configMode causes additional slowdown
        self.msDriftCompensation = 17
        self.msDriftCompensationConfigMode = 0

        # Vars to drive UI
        self.markerPositions = [ [0, 0], [69, 0], [0, 12], [40, 12], [80, 12], [0, 24], [40, 24], [80, 24]]
        self.activeOption = 1

        # Get working vars
        self.loadState()
        self.calcSleepTime()
        self.getPulseWidth()

        # Get asyncio event loop object
        #self.el = asyncio.get_event_loop()

        self.tasks = []
        for n in range(6):
            self.tasks.append(0)

        # Starts/Stops the master clock
        @b1.handler_falling
        def StartStop():
            self.running = not self.running

        # Cycle screen and toggle config mode
        @b2.handler_falling
        def cycleScreen():
            if ticks_diff(ticks_ms(), b2.last_pressed()) > 500 and ticks_diff(ticks_ms(), b2.last_pressed()) < 4000:
                self.configMode = not self.configMode
                # [temp] keep the clock running when in config mode to see if the previous slowdown bug occurs in testing
                #self.running = False
                if not self.configMode:
                    # config mode has just been turned off, save state and lock k2
                    self.saveState()
                    self.k2Unlocked = False
            else:
                self.k2Unlocked = False
                
                # Turn off config mode to avoid current knob positions messing up other settings on the next screen
                if self.configMode:
                    self.configMode = False
                    self.saveState()

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
        oled.text(str(self.completedCycles) + ':' + str(self.step), 0, 0, 1)
        if not self.running:
            oled.text('B1:Start', 0, 23, 1)
        else:
            oled.text('B1:Stop', 0, 23, 1)
        oled.show()

    '''config screen'''
    def screen2(self):
        # k1 adjusts selected option
        self.activeOption = k1.choice([1, 2, 3, 4, 5, 6, 7, 8])

        oled.fill(0)
        if self.configMode and self.activeOption != 3:
            configMarker = '|'
            
            # if active config option changes, lock k2 and save state
            if self.previousActiveOption != self.activeOption:
                self.k2Unlocked = False
                self.saveState()

            if self.activeOption == 1:
                # read current knob value
                newBpm = self.MIN_BPM + k2.read_position(steps=(self.MAX_BPM - self.MIN_BPM + 2))
                # unlock the knob if it has reached near the same value - avoids messy UX
                if abs(newBpm - self.state.get('bpm')) <= 10:
                    self.k2Unlocked = True
                # update config value if k2 is unlocked
                if self.k2Unlocked:
                    self.bpm = newBpm
                    # calculate the new pulse width in milliseconds based on the new bpm
                    self.calcSleepTime()
                    self.getPulseWidth()
                    
            elif self.activeOption == 2:
                # read current knob value
                newPw = k2.read_position(steps=self.MAX_PW_PERCENTAGE) + 1
                # unlock the knob if it has reached near the same value - avoids messy UX
                if abs(newPw - self.state.get('pulseWidthPercent')) <= 2:
                    self.k2Unlocked = True
                # update config value if k2 is unlocked
                if self.k2Unlocked:
                    self.pulseWidthPercent = newPw
                    self.calcSleepTime()
                    self.getPulseWidth()

            elif self.activeOption > 2:
                # k2 adjusts clock division
                selectedDivision = k2.choice(self.clockDivisions)
                # Only adjust values if k2 has moved. This avoids a potentially annoying UX
                # self.activeOption != 3 / output 1 is disabled from configuration
                if self.previousSelectedDivision != selectedDivision and self.activeOption != 3:
                    self.outputDivisions[self.activeOption - 3] = selectedDivision
                
                self.previousSelectedDivision = selectedDivision
            
            self.previousActiveOption = self.activeOption
                    
        else:
            configMarker = '.'
        
        oled.text(str(self.bpm) + ' bpm', 6, 0, 1)
        oled.text(str(self.pulseWidthPercent) + ':' + str(str(self.pulseWidthMs)), 75, 0, 1)
        oled.text('/' + str(self.outputDivisions[0]), 6, 12, 1)
        oled.text('/' + str(self.outputDivisions[1]), 45, 12, 1)
        oled.text('/' + str(self.outputDivisions[2]), 85, 12, 1)
        oled.text('/' + str(self.outputDivisions[3]), 6, 24, 1)
        oled.text('/' + str(self.outputDivisions[4]), 45, 24, 1)
        oled.text('/' + str(self.outputDivisions[5]), 85, 24, 1)
        oled.text(configMarker, self.markerPositions[self.activeOption-1][0], self.markerPositions[self.activeOption-1][1], 1)
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
        # If there is an analogue input voltage use that for BPM. clamp ensures it is higher than MIN and lower than MAX
        if val > self.MIN_AIN_VOLTAGE:
            self.bpm = clamp(int((((self.MAX_BPM) / 100) * val) + self.MIN_BPM), self.MIN_BPM, self.MAX_BPM)
            self.calcSleepTime()
            self.getPulseWidth()
        else:
            # No analog input, revert to last saved state
            self.bpm = self.state.get("bpm", 100)
            self.calcSleepTime()
            self.getPulseWidth()

    def getPulseWidth(self):
        # Set max of self.MAX_PW_PERCENTAGE percent of total cycle time
        self.MAX_PULSE_WIDTH = int(self.timeToSleepMs * self.MAX_PW_PERCENTAGE // 100)
        # Calc pulse width in milliseconds given the desired percentage. clamp ensures it is higher than MIN and lower than MAX
        self.pulseWidthMs = clamp((self.timeToSleepMs * (self.pulseWidthPercent)//100), self.MIN_PULSE_WIDTH, self.MAX_PULSE_WIDTH)

    def computeGcd(self, x, y):
        while(y):
            x, y = y, x % y
        return x

    def lcm(self, li):
        lcm = 1
        for item in li:
            lcm = lcm*item//max(self.computeGcd(lcm, item), 1)
        return lcm

    ''' Triggered by main. Sends output pulses at required division '''
    def clockTrigger(self):

        if self.DEBUG:
            print('BPM: ' + str(self.bpm) + ' cycle: ' + str(self.timeToSleepMs) + ' PW:' + str(self.pulseWidthMs))

        for idx, output in enumerate(self.outputDivisions):
            if output != 0:
                if self.step % output == 0:
                    #self.tasks[idx] = self.el.create_task(self.outputPulse(cvs[idx]))
                    if self.tasks[idx] != 0 and not self.tasks[idx].done():
                        print(f'Task: {idx} is not done')
                    self.tasks[idx] = asyncio.create_task(self.outputPulse(cvs[idx]))
            else:
                cvs[idx].off()

        # advance/reset clock step, resetting at the lowest common multiple
        if self.step < self.lcm(self.outputDivisions):
            self.step += 1
        else:
            self.completedCycles += 1
            self.step = 1
        
        # Get time of last step to use in the auto reset function
        self.previousStepTime = ticks_ms()

        # Debug print tasks
        #for i in self.tasks:
        #    if i != 0:
        #        #attrs = dir(i)
        #        #print(', '.join("%s" % item for item in attrs))
        #        print(f'[{i}] done: {str(i.done())}. state: {str(i.state)}. data: {str(i.data)}. coro: {str(i.coro)}')
        #    else:
        #        print(0)

    ''' Save working vars to a save state file'''
    def saveState(self):
        self.state = {
            "bpm": self.bpm,
            "pulseWidthPercent": self.pulseWidthPercent,
            "outputDivisions": self.outputDivisions
        }
        self.save_state_json(self.state)
        if self.DEBUG:
            print('State saved')

    ''' Load a previously saved state, or initialize working vars, then save'''
    def loadState(self):

        self.state = self.load_state_json()

        self.bpm = self.state.get("bpm", 100)
        self.pulseWidthPercent = self.state.get("pulseWidthPercent", 50)
        self.outputDivisions = self.state.get("outputDivisions", [1,2,4,8,16,32])

        self.saveState()

    async def main(self):
        while True:

            # Display selected screen
            if self.screen == 1:
                self.screen1()
            else:
                self.screen2()

            # Auto reset function after resetTimeout
            if self.step != 0 and ticks_diff(ticks_ms(), self.previousStepTime) > self.resetTimeout:
                 self.step = 1
                 self.completedCycles = 0

            if not self.configMode:
                self.checkForAinBPM()

            if self.running:
                self.clockTrigger()
                self.calcSleepTime()
                if self.configMode:
                    await asyncio.sleep_ms(int(self.timeToSleepMs - self.msDriftCompensation - self.msDriftCompensationConfigMode))
                else:
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



