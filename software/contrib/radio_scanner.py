from europi import *
from time import sleep_ms, ticks_diff, ticks_ms
from europi_script import EuroPiScript

HEADER_DURATION = 2000  # 2 seconds in ms


def remap_knob():
    global knob_mapping
    knob_mapping += 1
    if knob_mapping == 3:
        knob_mapping = 0

def rotate_cvs():
    global cv_mapping
    new_cv_mapping = []
    for cv in cv_mapping[1:]: #Append all but the first (in order)
        new_cv_mapping.append(cv)
    new_cv_mapping.append(cv_mapping[0]) #Append the first

    cv_mapping = new_cv_mapping

def value_to_cv(value):
    return value * MAX_OUTPUT_VOLTAGE

def x_to_oled(x):
    return round(x * (OLED_WIDTH - 1))

def y_to_oled(y):
    return (OLED_HEIGHT - 1) - round(y * (OLED_HEIGHT - 1))

def do_step(x, y):
    oledx = x_to_oled(x)
    oledy = y_to_oled(y)

    cvx = value_to_cv(x)
    cvy = value_to_cv(y)

    oled.fill(0)
    oled.vline(oledx, 0, OLED_HEIGHT, 1)
    oled.hline(0, oledy, OLED_WIDTH, 1)

    cv_mapping[0].voltage(cvx)  # 0 to 10 (volts)
    cv_mapping[1].voltage(cvy)
    cv_mapping[2].voltage(abs(cvy - cvx))
    cv_mapping[3].voltage(MAX_OUTPUT_VOLTAGE - cvx)
    cv_mapping[4].voltage(MAX_OUTPUT_VOLTAGE - cvy)
    cv_mapping[5].voltage(MAX_OUTPUT_VOLTAGE - abs(cvy - cvx))

    sleep_ms(10)

def display_mapping(new_map):
    oled.fill_rect(0, 0, 64, 12, 1)
    oled.text(knob_mapping_text[new_map], 0, 2, 0)


cv_mapping = [cv1, cv2, cv3, cv4, cv5, cv6]
knob_mapping = 0 #0 = not used, 1 = knob 1, 2 = knob 2
knob_mapping_text = ['Off', 'Knob 1', 'Knob 2']


class RadioScanner(EuroPiScript):
    def main(self):
        
        b1.handler(rotate_cvs)
        din.handler(rotate_cvs)
        b2.handler(remap_knob)

        while True:

            if knob_mapping != 1:
                x = k1.percent()
            else:
                x = clamp(ain.percent() + k1.percent(), 0, 1)

            if knob_mapping != 2:
                y = k2.percent()
            else:
                y = clamp(ain.percent() + k2.percent(), 0, 1)

            do_step(x, y)

            if ticks_diff(ticks_ms(), b2.last_pressed()) < HEADER_DURATION:
                display_mapping(knob_mapping)
            oled.show()

if __name__ == "__main__":
    RadioScanner().main()