from time import sleep
from europi import oled, b1, b2, k2, ain, cvs, usb_connected, turn_off_all_cvs
from europi_script import EuroPiScript
from os import stat, mkdir


class CalibrationValues:
    """Wrapper class for the input & output calibration values used for analogue inputs & outputs

    In low-accuracy mode, input_calibration_values is a length 2 array with the raw samples taken at 0V and 10V

    In high-accuracy mode, input_calibration_values is a length 11 array with the raw samples taken at 0-10V, in 1V
    increments.

    In either mode, output_calibration_values is a length 11 array with the raw samples taken at 0-10V, in 1V
    increments.
    """

    MODE_UNKNOWN = "unk"
    MODE_LOW_10V = "low10"
    MODE_LOW_5V = "low5"
    MODE_HIGH = "high"

    mode = "unk"

    input_calibration_values = []
    output_calibration_values = []

    def __init__(self, mode):
        """Create the calibration values, specifying the mode we're operating in

        @param mode  The calibration mode, one of MODE_LOW_10, MODE_LOW_5, or MODE_HIGH
        """
        self.mode = mode

    def save(self):
        """Save the calibration readings to /lib/calibration_values.py

        Note: this will overwrite all previous calibrations
        """
        with open(f"lib/calibration_values.py", "w") as file:
            values = ", ".join(map(str, self.input_calibration_values))
            file.write(f"INPUT_CALIBRATION_VALUES=[{values}]\n")

            values = ", ".join(map(str, self.output_calibration_values))
            file.write(f"OUTPUT_CALIBRATION_VALUES=[{values}]\n")

            file.write(f"CALIBRATION_MODE = '{self.mode}'\n")


class Calibrate(EuroPiScript):
    """
    A script to interactively calibrate the module

    General flow:
        1. Sanity check (rack power, necessary file structure exists)
        2. Input calibration. One of:
            a. low-accuracy 10V in
            b. low-accuracy 5V in
            c. high-accuracy 0-10V in
        3. Output calibration
        4. Save calibration
        5. Idle for reboot

    Output calibration only applies to CV1; all other outputs will
    use the same calibration values.
    """

    # The initial state; prompt the user to select their calibration mode using K2 + B2
    STATE_STARTUP = 0

    # Asking the user to select their calibration mode
    STATE_MODE_SELECT = 1

    # Initial states for each input calibration mode:
    # - low-accuracy w/ 10V input
    # - low-accuracy w/ 5V input
    # - high-accuracy w/ variable 0-10V input
    STATE_START_LOW_10 = 2
    STATE_START_LOW_5 = 3
    STATE_START_HIGH = 4

    # Start output calibration
    STATE_START_OUTPUT = 5

    # Flags indicating we're waiting for the user to press B1
    STATE_WAITING_B1 = -1
    STATE_B1_PRESSED = -2

    # As above, but for B2
    STATE_WAITING_B2 = -3
    STATE_B2_PRESSED = -4

    # The current state of the program
    # The state progresses pretty linearly with minimal branching, so mostly
    # this is used for debugging.
    # It _is_ necessary for button press detection
    state = 0

    @classmethod
    def display_name(cls):
        """Push this script to the end of the menu."""
        return "~Calibrate"

    def text_wait(self, text, duration):
        """
        Display text on the screen and block for the specified duration

        @param text  The text to display
        @param duration  The duration to wait in seconds
        """
        oled.centre_text(text)
        sleep(duration)

    def read_sample(self):
        """
        Read from the raw ain pin and return the average across several readings

        @return  The average across 256 distinct readings from the pin
        """
        N_READINGS = 512
        readings = []
        for reading in range(N_READINGS):
            readings.append(ain.pin.read_u16())

        # discard the lowest & highest 1/4 of the readings as outliers
        readings.sort()
        readings = readings[N_READINGS // 4 : 3 * N_READINGS // 4]
        return round(sum(readings) / N_READINGS)

    def wait_for_voltage(self, voltage):
        """
        Wait for the user to connect the desired voltage to ain & press b1

        @param voltage  The voltage to instruct the user to connect. Used for display only

        @return  The average samples read from ain (see @read_sample)
        """
        if voltage == 0:
            oled.centre_text(f"Unplug all\n\nDone: Button 1")
        else:
            oled.centre_text(f"Plug in {voltage:0.1f}V\n\nDone: Button 1")
        self.wait_for_b1()
        return self.read_sample()

    def wait_for_b1(self, wait_fn=None):
        """
        Wait for the user to press B1, returning to the original state when they have

        @param wait_fn  A function to execute while waiting (e.g. refresh the UI)
        """
        if wait_fn is None:
            wait_fn = lambda: sleep(0.01)

        prev_state = self.state
        self.state = self.STATE_WAITING_B1
        while self.state == self.STATE_WAITING_B1:
            wait_fn()
        self.state = prev_state

    def wait_for_b2(self, wait_fn=None):
        """
        Wait for the user to press B2, returning to the original state when they have

        @param wait_fn  A function to execute while waiting (e.g. refresh the UI)
        """
        if wait_fn is None:
            wait_fn = lambda: sleep(0.01)

        prev_state = self.state
        self.state = self.STATE_WAITING_B2
        while self.state == self.STATE_WAITING_B2:
            wait_fn()
        self.state = prev_state

    def check_directory(self):
        """Check if /lib exists. If it does not, create it"""
        try:
            stat("/lib")
        except OSError:
            mkdir("/lib")

    def check_rack_power(self):
        if usb_connected.value() == 1:
            oled.centre_text("Make sure rack\npower is on\nDone: Button 1")
            self.wait_for_b1()

    def input_calibration_low10(self):
        """
        Low-accuracy, 10V input calibration

        Prompt the user for 0 and 10V inputs only

        @return  The sample readings for 0 and 10V
        """
        self.state = self.STATE_START_LOW_10
        readings = [
            self.wait_for_voltage(0),
            self.wait_for_voltage(10),
        ]
        return readings

    def input_calibration_low5(self):
        """
        Low-accuracy, 5V input calibration

        Prompt the user for 0 and 5V inputs only. The 5V reading is extrapolated to 10V.

        @return  The sample readings for 0 and 10V
        """
        self.state = self.STATE_START_LOW_5
        readings = [
            self.wait_for_voltage(0),
            self.wait_for_voltage(5),
        ]

        # Extrapolate from 5V input to 10V, assuming a linear progression
        samples_per_volt = round((readings[-1] - readings[0]) / 5)
        readings[-1] = samples_per_volt * 10 + readings[0]

        return readings

    def input_calibration_high(self):
        """
        High accuracy input calibration

        User is prompted to connect 0, 1, 2, ..., 9, 10V

        @return  The sample readings for 0 to 10V (inclusive)
        """
        self.state = self.STATE_START_HIGH
        readings = []
        for i in range(11):
            readings.append(self.wait_for_voltage(i))
        return readings

    def main(self):
        # Button handlers
        @b1.handler
        def on_b1_press():
            if self.state == self.STATE_WAITING_B1:
                self.state = self.STATE_B1_PRESSED

        @b2.handler
        def on_b2_press():
            if self.state == self.STATE_WAITING_B2:
                self.state = self.STATE_B2_PRESSED

        # The available calibration modes (selected by k2)
        CALIBRATION_MODES = [
            "Low (10V in)",
            "Low (5V in)",
            "High (0-10V in)",
        ]

        self.text_wait("Calibration\nMode", 3)

        ######################################################################################################

        # Initial hardware & software checks
        self.check_directory()
        self.check_rack_power()

        ######################################################################################################

        # Calibration start
        self.state = self.STATE_MODE_SELECT
        refresh_ui = lambda: oled.centre_text(
            f"Choose mode (k2)\n{k2.choice(CALIBRATION_MODES)}\nDone: Button 2"
        )
        refresh_ui()
        self.wait_for_b2(refresh_ui)

        ######################################################################################################

        # Peform the requested input calibration
        choice = k2.choice(CALIBRATION_MODES)
        if choice == CALIBRATION_MODES[0]:
            calibration_values = CalibrationValues(CalibrationValues.MODE_LOW_10V)
            calibration_values.input_calibration_values = self.input_calibration_low10()
        elif choice == CALIBRATION_MODES[1]:
            calibration_values = CalibrationValues(CalibrationValues.MODE_LOW_5V)
            calibration_values.input_calibration_values = self.input_calibration_low5()
        else:
            calibration_values = CalibrationValues(CalibrationValues.MODE_HIGH)
            calibration_values.input_calibration_values = self.input_calibration_high()

        if calibration_values.mode == CalibrationValues.MODE_HIGH:
            readings_in = calibration_values.input_calibration_values
        else:
            # expand the raw calibration values if we were in a low-accuracy mode such that
            # we have an expected reading for every volt from 0-10
            readings_in = [calibration_values.input_calibration_values[0]]
            m = (
                calibration_values.input_calibration_values[1]
                - calibration_values.input_calibration_values[0]
            ) / 10
            c = calibration_values.input_calibration_values[0]
            for x in range(1, 10):
                readings_in.append(round((m * x) + c))
            readings_in.append(calibration_values.input_calibration_values[-1])

        ######################################################################################################

        # Output calibration
        self.state = self.STATE_START_OUTPUT
        calibration_values.output_calibration_values = []

        turn_off_all_cvs()
        for i in range(len(cvs)):
            oled.centre_text(f"Plug CV{i+1} into\nanalogue in\nDone: Button 1")
            self.wait_for_b1()

            # always 0 duty for 0V out
            calibration_values.output_calibration_values.append([0])

            # Output 1-10V on each CV output & read the result on AIN
            # Adjust the duty cycle of the CV output until the input is within an acceptable range
            duty = 0
            cvs[i].pin.duty_u16(duty)
            reading = self.read_sample()
            COARSE_STEP = 10
            FINE_STEP = 1
            for volts, expected_reading in enumerate(readings_in[1:]):
                oled.centre_text(f"Calibrating...\n CV{i+1} @ {volts+1}V")

                # Step 1: coarse calibration
                # increase the duty in large steps until we get within 0.002V of teh expected reading
                while abs(reading - expected_reading) > 0.002 and reading < expected_reading:
                    duty += COARSE_STEP
                    cvs[i].pin.duty_u16(duty)
                    reading = self.read_sample()

                # Step 2: fine calibration
                # increase or decrease the duty in much smaller increments
                count = 0
                while abs(reading - expected_reading) > 0.001 and count <= COARSE_STEP * 2:
                    count += 1
                    if reading < expected_reading:
                        duty += FINE_STEP
                    elif reading > expected_reading:
                        duty -= FINE_STEP

                    cvs[i].pin.duty_u16(duty)
                    sleep(0.05)
                    reading = self.read_sample()

                calibration_values.output_calibration_values[-1].append(duty)

            cvs[i].off()

        # Save the result
        oled.centre_text("Saving\ncalibration...")
        calibration_values.save()

        # Prompt the user to reboot to apply the new calibration
        # Spin here forever if necessary
        while True:
            self.text_wait("Calibration\ncomplete", 3)
            self.text_wait("Reboot\nto apply\nnew calibration", 3)


if __name__ == "__main__":
    Calibrate().main()
