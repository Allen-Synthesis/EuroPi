from europi import *
from time import *

# Overclock the Pico for improved performance.
machine.freq(250_000_000)
oled.contrast(0)

g23 = Pin(23, Pin.OUT)
g23.value(1)

class sampleAin:
    def __init__(self):
        self.maxSamples = 256
        self.samples = []
        self.times = []
        self.inputVoltage = 0
        self.Message = 'Capture: Button1'

        @b1.handler_falling
        def b1Pressed():
            self.samples = []
            self.times = []
            self.Message = 'Capturing...'
            while len(self.samples) < self.maxSamples:
                self.inputVoltage = ain.read_voltage()
                t = ticks_ms()
                self.samples.append(self.inputVoltage)
                self.times.append(t)
                self.updateScreen()
                sleep(0.01)

            self.Message = 'Range:' + str(abs(min(self.samples) - max(self.samples)))

            # Print out values
            print('\n\nsamples:')
            for s in self.samples:
                print(str(s) + ',', end="")
            print('\n\ntimes:')
            for t in self.times:
                print(str(t) + ',', end="") 
            
            print('\n\nRange:' + str(min(self.samples) - max(self.samples)))

    
    def main(self):
        while True:
            self.inputVoltage = ain.read_voltage()
            self.updateScreen()
        
    def updateScreen(self):
        #oled.clear() - dont use this, it causes the screen to flicker!
        oled.fill(0)
        oled.text('Input: ' + str(self.inputVoltage),0,0,1)
        oled.text(self.Message,0,10,1)
        oled.show()

me = sampleAin()
me.main()