# Copyright 2024 Allen Synthesis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from europi import *
from time import ticks_diff, ticks_ms
#from random import uniform
from europi_script import EuroPiScript
#from europi_config import EuroPiConfig

"""
Gate Phaser
author: Nik Ansell (github.com/gamecat69)
date: May 2024
labels: sequencer, gates
"""

# Constants
KNOB_CHANGE_TOLERANCE = 0.001
MIN_CYCLE_TIME_MS = 100
MIN_PHASE_SHIFT_MS = 5
MIN_MS_BETWEEN_SAVES = 2000
GATE_LENGTH_MS = 20

class GatePhaser(EuroPiScript):
    def __init__(self):

        # Initialize variables

        # How many multiples of the gate delay time will each gate be delayed?
        self.gateDelayMultiples = [ [0,1,2,3,4,5],[2,3,4,5,6,7],[0,1,2,3,6,9],[1,2,3,2,4,6],[5,4,3,2,1,0] ]
        # UI only, changes the behaviour of the gate delay control
        self.gateDelayControlOptions = [5, 10, 20]
        # Lists containing params for each output
        self.gateDelays = []
        self.gateOnTimes = []
        self.gateOffTimes = []
        self.gateStates = []

        self.lastK1Reading = 0
        self.lastK2Reading = 0
        self.lastSaveState = ticks_ms()
        self.pendingSaveState = False
        self.screenRefreshNeeded = True

        self.smoothK1 = 0
        self.smoothK2 = 0
        self.loadState()

        # Populate working lists
        self.calcGateDelays(newList=True)
        self.calcGateTimes(newList=True)

        # Create intervalStr for the UI
        self.buildIntervalStr()

        # -----------------------------
        # Interupt Handling functions
        # -----------------------------

        @din.handler
        def resetGates():
            """Resets gate timers"""
            self.calcGateDelays()
            self.calcGateTimes()

        @b1.handler_falling
        def b1Pressed():
            """Triggered when B1 is pressed and released. Select gate delay multiples"""
            self.selectedGateDelayMultiple = (self.selectedGateDelayMultiple + 1) % len(self.gateDelayMultiples)
            self.calcGateDelays()
            self.calcGateTimes()
            self.buildIntervalStr()
            self.screenRefreshNeeded = True
            self.pendingSaveState = True


        @b2.handler_falling
        def b2Pressed():
            """Triggered when B2 is pressed and released. Select gate control multiplier"""
            self.selectedGateControlMultiplier = (self.selectedGateControlMultiplier + 1) % len(self.gateDelayControlOptions)
            self.calcGateDelays()
            self.calcGateTimes()
            self.screenRefreshNeeded = True
            self.pendingSaveState = True


    def buildIntervalStr(self):
        """Create a string for the UI showing the gate delay multiples"""
        self.intervalsStr = ''
        for i in self.gateDelayMultiples[self.selectedGateDelayMultiple]:
            self.intervalsStr = self.intervalsStr + str(i) + ':'


    def lowPassFilter(self, alpha, prevVal, newVal):
        """Smooth out some analogue noise. Higher Alpha = more smoothing"""
        # Alpha value should be between 0 and 1.0
        return alpha * prevVal + (1 - alpha) * newVal

    def calcGateDelays(self, newList=False):
        """Populate a list containing the gate delay in ms for each output"""
        for n in range(6):
            val = self.gateDelayMultiples[self.selectedGateDelayMultiple][n] * self.slaveGateIntervalMs
            if newList:
                self.gateDelays.append(val)
            else:
                self.gateDelays[n] = (val)


    def calcGateTimes(self, newList=False):
        """Calculate the next gate on and off times based on the current time"""
        self.currentTimeStampMs = ticks_ms()
        for n in range(6):
            gateOnTime = self.currentTimeStampMs + self.gateDelays[n]
            gateOffTime = gateOnTime + GATE_LENGTH_MS
            if newList:
                self.gateOnTimes.append(gateOnTime)
                self.gateOffTimes.append(gateOffTime)
                self.gateStates.append(False)
            else:
                self.gateOnTimes[n] = gateOnTime
                self.gateOffTimes[n] = gateOffTime
                self.gateStates[n] = False


    def getKnobValues(self):
        """Get k1 and k2 values and adjust working parameters if knobs have moved"""
        changed = False

        # Get knob values and smooth using a simple low pass filter
        self.smoothK1 = int(self.lowPassFilter(0.15, self.lastK1Reading, k1.read_position(100) + 2))
        self.smoothK2 = int(self.lowPassFilter(0.15, self.lastK2Reading, k2.read_position(100) + 2))

        if abs(self.smoothK1 - self.lastK1Reading) > KNOB_CHANGE_TOLERANCE:
            self.masterGateIntervalMs = max(MIN_CYCLE_TIME_MS, self.smoothK1 * 25)
            changed = True

        if abs(self.smoothK2 - self.lastK2Reading) > KNOB_CHANGE_TOLERANCE:
            self.slaveGateIntervalMs = max(MIN_PHASE_SHIFT_MS, self.smoothK2 * self.gateDelayControlOptions[self.selectedGateControlMultiplier])
            changed = True

        if changed:
            self.calcGateDelays()
            self.calcGateTimes()
            self.screenRefreshNeeded = True
            self.pendingSaveState = True

        self.lastK1Reading = self.smoothK1
        self.lastK2Reading = self.smoothK2

    def main(self):
        """Entry point - main loop. See inline comments for more info"""
        while True:
            self.getKnobValues()
            if self.screenRefreshNeeded:
                self.updateScreen()

            # Cycle through outputs turning gates on and off as needed
            # When a gate is triggered it's next on and off time is calculated
            self.currentTimeStampMs = ticks_ms()
            for n in range(len(cvs)):
                if self.currentTimeStampMs >= self.gateOffTimes[n] and self.gateStates[n]:
                    cvs[n].off()
                    self.gateStates[n] = False
                elif self.currentTimeStampMs >= self.gateOnTimes[n] and not self.gateStates[n]:
                    cvs[n].on()
                    self.gateStates[n] = True
                    # When will the gate need to turn off?
                    self.gateOffTimes[n] = self.currentTimeStampMs + GATE_LENGTH_MS
                    # When will the next gate need to fire?
                    self.gateOnTimes[n] = self.currentTimeStampMs + self.gateDelays[n] + self.masterGateIntervalMs

            # Save state
            if self.pendingSaveState and ticks_diff(ticks_ms(), self.lastSaveState) >= MIN_MS_BETWEEN_SAVES:
                self.saveState()
                self.pendingSaveState = False

    def updateScreen(self):
        """Update the screen only if something has changed. oled.show() hogs the processor and causes latency."""

        # Clear screen
        oled.fill(0)

        oled.text("Cycle", 5, 0, 1)
        oled.text(str(self.masterGateIntervalMs), 5, 10, 1)
        oled.text("Delay", 80, 0, 1)
        oled.text(str(self.slaveGateIntervalMs), 80, 10, 1)
        oled.text(self.intervalsStr[:-1], 0, 22, 1)
        oled.text('x' + str(self.gateDelayControlOptions[self.selectedGateControlMultiplier]), 104, 22, 1)

        oled.show()
        self.screenRefreshNeeded = False

    def saveState(self):
        """Save working vars to a save state file"""
        self.state = {
            "masterGateIntervalMs": self.masterGateIntervalMs,
            "slaveGateIntervalMs": self.slaveGateIntervalMs,
            "selectedGateDelayMultiple": self.selectedGateDelayMultiple,
            "selectedGateControlMultiplier": self.selectedGateControlMultiplier,
        }
        self.save_state_json(self.state)
        self.lastSaveState = ticks_ms()

    def loadState(self):
        """Load a previously saved state, or initialize working vars, then save"""
        self.state = self.load_state_json()
        self.masterGateIntervalMs = self.state.get("masterGateIntervalMs", 1000)
        self.slaveGateIntervalMs = self.state.get("slaveGateIntervalMs", 100)
        self.selectedGateDelayMultiple = self.state.get("selectedGateDelayMultiple", 0)
        self.selectedGateControlMultiplier = self.state.get("selectedGateControlMultiplier", 0)

if __name__ == "__main__":
    GatePhaser().main()
