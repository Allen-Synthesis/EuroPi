from europi import *
from time import sleep_ms, ticks_diff, ticks_ms
from random import randint

'''
To do:

- Accept a clock input then trigger a function with every clock input to decide whether or not trigger outputs
- Add a ratchet function
- Add a clock divider function
- Use a button to toggle between triggers and gates?
- Create different patterns
- Create the ability to rotate/morph between different patterns using a knob/knob choice?
'''


BD=[1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0]
SN=[0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0]
HH=[1,1,1,0,1,0,1,0,0,1,1,1,1,0,1,1]

max_step = len(BD)

step = 0
trigger_duration_ms = 50
HH_ratchet = 0
ratchet_delay = 0

def ratchet(cv, num, delay):
    # CV: output
    # num: number of even ratchets
    for b in range (0, num):
        cv.value(1)
        sleep_ms(int(delay / num))
        cv.off()
    
while True:
    
    BPM = k1.read_position()+30
    # Calculate the delay for each beat in 1/16 time
    # 60000 / BPM = 1/4 note
    delay = int(60000/BPM/4)
    
    #if HH_ratchet > 1:
    #    ratchet_delay = int(delay / HH_ratchet)

    oled.clear()
    oled.text("Step: " + str(step),0,0,1)
    oled.text("BPM: " + str(BPM),0,10,1)
    oled.text("Drum: " + str(BD[step]) + " | " + str(SN[step]) + " | " + str(HH[step]),0,20,1)
    oled.show()
    
    cv1.value(BD[step])
    cv2.value(SN[step])
    
    # It would be nice to add a ratchet feature. But need to calculate the sleep times correctly
    #ratchet(cv3, randint(1,2), delay)
    cv3.value(HH[step])
    #sleep_ms(ratchet_delay)
    #cv3.off()
    #cv3.value(HH[step])
    #cv3.off()
    sleep_ms(trigger_duration_ms)
    cv1.off()
    cv2.off()
    cv3.off()
 
 
    delay = int(delay - trigger_duration_ms)
    print(delay)
 
    if step < 15:
        step += 1
    else:
        step = 0

    sleep_ms(delay)