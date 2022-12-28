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

button_1: Short Press (<500ms): Start / Stop. Long Press (>500ms): Select clock source (Internal/External)
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
- BPM occasionally drifts by 1ms - possibly due to asyncio, pico performance limitations, or some other as-yet unknown error

'''

class MasterClockInner(EuroPiScript):
    def __init__(self):
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)
        self.step = 1
        self.clockInputNum = 1
        self.completedCycles = 0
        self.running = True
        self.resetTimeout = 2000
        self.previousStepTime = 0
        self.screen = 2
        self.configMode = False
        self.k2Unlocked = False
        self.previousSelectedDivision = 0
        self.previousActiveOption = ''
        self.previousClockTime = 0
        self.inputClockDiffs = []
        self.clockSelectionScreenActive = False

        self.MIN_BPM = 20  # Successfully calibrated to >= 20 and <= 240 BPM
        self.MAX_BPM = 240
        self.MIN_PULSE_WIDTH = 8
        self.MIN_AIN_VOLTAGE = 1.1
        self.MAX_DIVISION = 128
        self.MAX_PW_PERCENTAGE = 80
        self.CLOCKS_PER_QUARTER_NOTE = 4

        # Create list of available clock divisions, with 'r' (random) at the end
        self.clockDivisions = []
        for n in range(1,self.MAX_DIVISION+1):
            self.clockDivisions.append(n)
        self.clockDivisions.append('r')
        
        # When enabled, set msDriftCompensation to 30
        # When disabled, set msDriftCompensation to 28
        self.DEBUG = False

        # Default value is using an internal clock source
        self.externalClockInput = False

        # Set to 1 for a 4 ppqn (clock every 16th beat)
        # Set to 6 for MIDI DinSync 24 (To divide to 4 ppqn)
        # Set to 12 for MIDI DinSync 48  (To divide to 4 ppqn)
        # Note: Currently does not work well using a Din Sync input - Perhaps the pico cannot keep up?
        self.inputClockDivision = 1

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

        self.tasks = []
        for n in range(6):
            self.tasks.append(0)            

        # Starts/Stops the master clock
        @b1.handler_falling
        def StartStop():
            if ticks_diff(ticks_ms(), b1.last_pressed()) > 500 and ticks_diff(ticks_ms(), b1.last_pressed()) < 4000:
                self.getClockOption()
            else:
                self.running = not self.running


        # Cycle screen and toggle config mode
        @b2.handler_falling
        def cycleScreen():
            if ticks_diff(ticks_ms(), b2.last_pressed()) > 500 and ticks_diff(ticks_ms(), b2.last_pressed()) < 4000:
                self.configMode = not self.configMode
                # This will stop the clock from running in config mode - keep here as it might be needed in the future
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

        # Trigger clock if using an external clock, or reset if not
        @din.handler
        def dinTrigger():
            if self.externalClockInput:
                # Divide input clocks by self.inputClockDivision and trigger the clock
                if self.clockInputNum % self.inputClockDivision == 0:
                    self.clockTrigger()
                    if self.clockInputNum > 1: # Ignore the first entry as it has no reference
                        self.mSBetweenClockCycles = time.ticks_diff(ticks_ms(), self.previousClockTime)
                        # Cap the BPM calcs at at 240 BPM to avoid steam coming out of the pico's ears
                        if self.mSBetweenClockCycles < 250:
                            self.inputClockDiffs.append(self.mSBetweenClockCycles)
                        else:
                            self.inputClockDiffs.append(250)
                        # Only keep 20 values in the buffer
                        if len(self.inputClockDiffs) == 20:
                            del self.inputClockDiffs[0]

                        if self.clockInputNum > 3: # Only calculate is there are > 3 entries
                            self.bpm = self.calculateBpm(self.inputClockDiffs)
                    self.previousClockTime = ticks_ms()
                    
                self.clockInputNum += 1
            else:
                self.step = 1

    ''' Ask to use internal or external clock'''
    def getClockOption(self):
        self.clockSelectionScreenActive = True
        oled.fill(0)
        oled.text("Clock Source:", 0, 0, 1)
        oled.text("B1: Internal", 0, 9, 1)
        oled.text("B2: External", 0, 17, 1)
        oled.show()
        while True:
            if b1.value() == 1:
                self.externalClockInput = False
                self.running = False # Need to do this to keep it running because the b1 handler will reverse the value
                self.clockSelectionScreenActive = False
                break
            elif b2.value() == 1:
                self.externalClockInput = True
                self.clockSelectionScreenActive = False
                break
            time.sleep(0.05)
        
        self.saveState()

    def bpmFromMs(self, ms):
        return int(((1/(ms/1000))*60)/4)

    def calculateBpm(self, list):
        self.averageDiff = self.average(list)
        return self.bpmFromMs(self.averageDiff)

    def average(self, list):
        return sum(list) / len(list)

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
        # k1 adjusts selected option. Remove option 1 (bpm) if using an external clock
        if self.externalClockInput:
            self.activeOption = k1.choice([2, 3, 4, 5, 6, 7, 8])
        else:
            self.activeOption = k1.choice([1, 2, 3, 4, 5, 6, 7, 8])

        oled.fill(0)
        if self.configMode and self.activeOption != 3:
            configMarker = '|'
            
            # if active config option changes, lock k2 and save state
            if self.previousActiveOption != self.activeOption:
                self.k2Unlocked = False
                self.saveState()

            # Prevent the BPM from being configured if using an external clock input
            if self.activeOption == 1 and not self.externalClockInput:
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
        self.mSBetweenClockCycles = int((60000 / self.bpm / self.CLOCKS_PER_QUARTER_NOTE))
    
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
        self.MAX_PULSE_WIDTH = int(self.mSBetweenClockCycles * self.MAX_PW_PERCENTAGE // 100)
        # Calc pulse width in milliseconds given the desired percentage. clamp ensures it is higher than MIN and lower than MAX
        self.pulseWidthMs = clamp((self.mSBetweenClockCycles * (self.pulseWidthPercent)//100), self.MIN_PULSE_WIDTH, self.MAX_PULSE_WIDTH)

    def computeGcd(self, x, y):
        while(y):
            x, y = y, x % y
        return x

    def lcm(self, li):
        lcm = 1
        for item in li:
            if item != 0 and item != 'r':
                lcm = lcm*item//max(self.computeGcd(lcm, item), 1)
        return lcm

    ''' Sends output pulses at required division '''
    def clockTrigger(self):

        if self.DEBUG:
            print('BPM: ' + str(self.bpm) + ' cycle: ' + str(self.mSBetweenClockCycles) + ' PW:' + str(self.pulseWidthMs))

        for idx, output in enumerate(self.outputDivisions):
            if output != 'r':
                if self.step % output == 0:
                    if self.tasks[idx] != 0 and not self.tasks[idx].done() and self.DEBUG:
                        print(f'Task: {idx} is not done')
                    if self.DEBUG:
                        print(f'calling outputPulse({idx}) on division {output}')
                    self.tasks[idx] = asyncio.create_task(self.outputPulse(cvs[idx]))
            else:
                # Fire pulses randomly
                if randint(0, 1):
                    self.tasks[idx] = asyncio.create_task(self.outputPulse(cvs[idx]))

        # advance/reset clock step, resetting at the lowest common multiple
        if self.step < self.lcm(self.outputDivisions):
            self.step += 1
        else:
            self.completedCycles += 1
            self.step = 1
        
        # Get time of last step to use in the auto reset function
        self.previousStepTime = ticks_ms()

        # Debug task output to check for overrunning tasks i.e. memory leaks
        if self.DEBUG:
            for i in self.tasks:
                if i != 0:
                    print(f'[{i}] done: {str(i.done())}. state: {str(i.state)}. data: {str(i.data)}. coro: {str(i.coro)}')
                else:
                    print(0)

    ''' Save working vars to a save state file'''
    def saveState(self):
        self.state = {
            "bpm": self.bpm,
            "pulseWidthPercent": self.pulseWidthPercent,
            "externalClockInput": self.externalClockInput,
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
        self.externalClockInput = self.state.get("externalClockInput", False)
        self.outputDivisions = self.state.get("outputDivisions", [1,2,4,8,16,32])

        self.saveState()

    async def main(self):
        while True:
            if not self.clockSelectionScreenActive:
                # Display selected screen
                if self.screen == 1:
                    self.screen1()
                else:
                    self.screen2()

            # Auto reset function after resetTimeout
            if self.step != 0 and ticks_diff(ticks_ms(), self.previousStepTime) > self.resetTimeout:
                 self.step = 1
                 self.completedCycles = 0

            if not self.configMode and not self.externalClockInput:
                self.checkForAinBPM()

            if self.running and not self.externalClockInput:
                self.clockTrigger()
                self.calcSleepTime()
                if self.configMode:
                    await asyncio.sleep_ms(int(self.mSBetweenClockCycles - self.msDriftCompensation - self.msDriftCompensationConfigMode))
                else:
                    await asyncio.sleep_ms(int(self.mSBetweenClockCycles - self.msDriftCompensation))
            else:
                # need to add this otherwise the async tasks never start
                await asyncio.sleep_ms(0)

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



