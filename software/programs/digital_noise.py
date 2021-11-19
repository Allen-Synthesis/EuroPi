from europi import *
from random import randint

machine.freq(250000000)

while True:
    if randint(0,1) == 0:
        cv1.duty(65534)
    else:
        cv1.off()
