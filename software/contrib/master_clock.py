from europi import *
import machine
from time import ticks_diff, ticks_ms
from europi_script import EuroPiScript
import uasyncio as asyncio

'''
Master Clock
author: Nik Ansell (github.com/gamecat69)
date: 2022-08-01
labels: clock

A master clock and clock divider. Each output sends a +5V trigger/gate at different divisions of the master clock.
The pulse width (gate/trigger duration) is configurable using knob 1.
The maximum gate/trigger duration is 50% of the pulse width of output 1.

For wonky/more interesting clock patterns there are two additional functions:
- Reset to step 1 using a gate into the digital input
- Variable BPM using CV into the analog input

Demo video: TBC

digital_in: Reset step count on rising edge
analog_in: Adjust BPM

knob_1: BPM
knob_2: Pulse width

button_1: Start / Stop
button_2: Reset step count when released

output_1: clock / 1
output_2: clock / 2
output_3: clock / 4
output_4: clock / 8
output_5: clock / 16
output_6: clock / 32

'''

class MasterClock(EuroPiScript):
    def __init__(self):
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)
        self.step = 1
        self.bpm = 100
        self.pulseWidthMs = 10
        self.running = True
        self.MAX_DIVISION = 32
        self.CLOCKS_PER_QUARTER_NOTE = 4
        self.MIN_BPM = 20  # Successfully calibrated to >= 20 and <= 240 BPM
        self.MAX_BPM = 240
        self.MIN_PULSE_WIDTH = 8
        self.resetTimeout = 2000
        self.previousStepTime = 0
        self.minAnalogInputVoltage = 0.9

        # When enabled, set msDriftCompensation to 30
        # When disabled, set msDriftCompensation to 28
        self.DEBUG = False

        # In testing a 28ms drift was found at all tempos
        # Adding this offset brings the BPM and Pulse width back into a reasonable tolerance
        self.msDriftCompensation = 28

        # Clock Divisions. Hold these are vars in case these are ever exposed via the UI
        # Output 1 is always master clock / 1
        self.divisionOutput2 = 2
        self.divisionOutput3 = 4
        self.divisionOutput4 = 8
        self.divisionOutput5 = 16
        self.divisionOutput6 = 32

        self.getSleepTime()
        self.MAX_PULSE_WIDTH = self.timeToSleepMs // 2

        # Get asyncio event loop object
        self.el = asyncio.get_event_loop()
        self.el.run_forever()

        # Starts/Stops the master clock
        @b1.handler_falling
        def StartStop():
            self.running = not self.running

        # Reset step count with button press
        @b2.handler_falling
        def resetButton():
            self.step = 1
        
        # Reset step count upon receiving a din voltage
        @din.handler
        def resetDin():
            self.step = 1

    # Holds given output (cv) high for pulseWidthMs duration
    async def outputPulse(self, cv):
        cv.voltage(5)
        await asyncio.sleep_ms(self.pulseWidthMs)
        cv.off()

    # Given a desired BPM, calculate the time to sleep between clock pulses
    def getSleepTime(self):
        self.timeToSleepMs = int((60000 / self.bpm / self.CLOCKS_PER_QUARTER_NOTE))
    
    def getBPM(self):
        val = 100 * ain.percent()
        # If there is an analogue input voltage use that for BPM. If not use the knob setting
        if val > self.minAnalogInputVoltage:
            self.bpm = int((((self.MAX_BPM) / 100) * val) + self.MIN_BPM)
        else:
            self.bpm = self.MIN_BPM + k1.read_position(steps=(self.MAX_BPM - self.MIN_BPM + 1), samples=512)

    def getPulseWidth(self):
        # Get desired PW percent
        self.pulseWidthPercent = k2.read_position(steps=50, samples=512) + 1
        # Calc Pulse Width duration (x 2 needed because the max is 50%)
        self.pulseWidthMs = int((self.MAX_PULSE_WIDTH * 2) * (self.pulseWidthPercent / 100)) 
        # Don't allow a pulse width less than the minimum
        if self.pulseWidthMs < self.MIN_PULSE_WIDTH:
            self.pulseWidthMs = self.MIN_PULSE_WIDTH
            self.pulseWidthPercent = 'min'

    # Triggered by main. Sends output pulses at required division
    def clockTrigger(self):

        if self.DEBUG:
            print('BPM: ' + str(self.bpm) + ' cycle: ' + str(self.timeToSleepMs) + ' PW:' + str(self.pulseWidthMs))

        el.create_task(self.outputPulse(cv1))

        if self.step % self.divisionOutput2 == 0:
            el.create_task(self.outputPulse(cv2))

        if self.step % self.divisionOutput3 == 0:
            el.create_task(self.outputPulse(cv3))

        if self.step % self.divisionOutput4 == 0:
            el.create_task(self.outputPulse(cv4))

        if self.step % self.divisionOutput5 == 0:
            el.create_task(self.outputPulse(cv5))

        if self.step % self.divisionOutput6 == 0:
            el.create_task(self.outputPulse(cv6))

        # advance/reset clock step
        if self.step < self.MAX_DIVISION:
            self.step += 1
        else:
            self.step = 1
        
        # Get time of last step to use in the auto reset function
        self.previousStepTime = ticks_ms()

    async def main(self):
        while True:
            self.getBPM()
            self.getSleepTime()
            self.MAX_PULSE_WIDTH = self.timeToSleepMs // 2  # Maximum of 50% pulse width
            self.getPulseWidth()
            self.updateScreen()

            # Auto reset function after resetTimeout
            if self.step != 0 and ticks_diff(ticks_ms(), self.previousStepTime) > self.resetTimeout:
                 self.step = 1

            if self.running:
                self.clockTrigger()
                await asyncio.sleep_ms(int(self.timeToSleepMs - self.msDriftCompensation))

    def updateScreen(self):
        # oled.clear() - dont use this, it causes the screen to flicker!
        oled.fill(0)
        oled.text('BPM: ' + str(self.bpm), 0, 1, 1)
        oled.text('PW: ' + str(self.pulseWidthPercent) + '% (' + str(self.pulseWidthMs) + 'ms)', 0, 12, 1)
        oled.text(str(self.step), 112, 0, 1)
        if not self.running:
            oled.text('B1:Start', 0, 23, 1)
        else:
            oled.text('B1:Stop', 0, 23, 1)
        oled.show()

if __name__ == '__main__':
    [cv.off() for cv in cvs]
    mc = MasterClock()
    el = asyncio.get_event_loop()
    el.create_task(mc.main())
    el.run_forever()

