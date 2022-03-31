
try:
    # Local development
    from software.firmware.europi import ain, b1, b2, clamp, cvs, din, k1, k2, oled
    from software.firmware.europi import MAX_OUTPUT_VOLTAGE, OLED_HEIGHT, OLED_WIDTH
    from software.firmware.europi_script import EuroPiScript
except ImportError:
    # Device import path
    from europi import *
    from europi_script import EuroPiScript

from time import sleep_ms, ticks_diff, ticks_ms

HEADER_DURATION = 2000  # 2 seconds in ms


class RadioScanner(EuroPiScript):
    def __init__(self):
        super().__init__()

        # Load state if previous state exists.
        state = self.load_state_json()
        # Set state variables with default fallback values if not found in the
        # json save state.
        self.knob_mapping = state.get("knob_mapping", 0)
        self.cv_mapping = state.get("cv_mapping", [0, 1, 2, 3, 4, 5])

        self.knob_mapping_text = ['Off', 'Knob 1', 'Knob 2']

        def remap_knob():
            self.knob_mapping += 1
            if self.knob_mapping == 3:
                self.knob_mapping = 0
            self.save_state()

        def rotate_cvs():
            self.cv_mapping = self.cv_mapping[1:] + [self.cv_mapping[0]]
            self.save_state()

        b1.handler(rotate_cvs)
        din.handler(rotate_cvs)
        b2.handler(remap_knob)

    def save_state(self):
        """Save the current state variables as JSON."""
        state = {
            "knob_mapping": self.knob_mapping,
            "cv_mapping": self.cv_mapping,
        }
        self.save_state_json(state)

    def value_to_cv(self, value):
        return value * MAX_OUTPUT_VOLTAGE

    def x_to_oled(self, x):
        return round(x * (OLED_WIDTH - 1))

    def y_to_oled(self, y):
        return (OLED_HEIGHT - 1) - round(y * (OLED_HEIGHT - 1))

    def do_step(self, x, y):
        oledx = self.x_to_oled(x)
        oledy = self.y_to_oled(y)

        cvx = self.value_to_cv(x)
        cvy = self.value_to_cv(y)

        oled.fill(0)
        oled.vline(oledx, 0, OLED_HEIGHT, 1)
        oled.hline(0, oledy, OLED_WIDTH, 1)

        cvs[self.cv_mapping[0]].voltage(cvx)  # 0 to 10 (volts)
        cvs[self.cv_mapping[1]].voltage(cvy)
        cvs[self.cv_mapping[2]].voltage(abs(cvy - cvx))
        cvs[self.cv_mapping[3]].voltage(MAX_OUTPUT_VOLTAGE - cvx)
        cvs[self.cv_mapping[4]].voltage(MAX_OUTPUT_VOLTAGE - cvy)
        cvs[self.cv_mapping[5]].voltage(MAX_OUTPUT_VOLTAGE - abs(cvy - cvx))

        sleep_ms(10)

    def display_mapping(self, new_map):
        oled.fill_rect(0, 0, 64, 12, 1)
        oled.text(self.knob_mapping_text[new_map], 0, 2, 0)

    def main(self):

        while True:
            if self.knob_mapping != 1:
                x = k1.percent()
            else:
                x = clamp(ain.percent() + k1.percent(), 0, 1)

            if self.knob_mapping != 2:
                y = k2.percent()
            else:
                y = clamp(ain.percent() + k2.percent(), 0, 1)

            self.do_step(x, y)

            if ticks_diff(ticks_ms(), b2.last_pressed()) < HEADER_DURATION:
                self.display_mapping(self.knob_mapping)

            oled.show()

if __name__ == "__main__":
    RadioScanner().main()
