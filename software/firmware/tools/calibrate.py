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
from time import sleep
from europi import oled, b1, b2, k2, ain, cvs, usb_connected, turn_off_all_cvs
from europi_script import EuroPiScript
from os import stat, mkdir
from experimental.math_extras import mean


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

        @return  The average across several distinct readings from the pin
        """
        N_READINGS = 512
        readings = []
        for i in range(N_READINGS):
            readings.append(ain.pin.read_u16())

        # discard the lowest & highest 1/4 of the readings as outliers
        readings.sort()
        readings = readings[N_READINGS // 4 : 3 * N_READINGS // 4]
        return round(mean(readings))

    def wait_for_voltage(self, voltage):
        """
        Wait for the user to connect the desired voltage to ain & press b1

        @param voltage  The voltage to instruct the user to connect. Used for display only

        @return  The average samples read from ain (see @read_sample)
        """
        if voltage == 0:
            oled.centre_text("Unplug all\n\nDone: Button 1")
        else:
            oled.centre_text(f"Plug in {voltage:0.1f}V\n\nDone: Button 1")
        self.wait_for_b1()
        oled.centre_text(f"Calibrating...\nAIN @ {voltage:0.1f}V")
        sleep(1)
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

    def calibrate_output(self, cv_n, calibration_values, input_readings):
        """
        Send volts from CVx to AIN, adjusting the duty cycle so the output is correct.

        @param cv_n  A value 0 <= cv_n < len(cvs) indicating which CV output we're calibrating
        @param calibration_values  The array of calibration values we append our results to
        @param input_readings  The duty cycles of AIN corresponding to 0, 1, 2, ..., 9, 10 volts
        """
        oled.centre_text(f"Plug CV{cv_n+1} into\nanalogue in\nDone: Button 1")
        self.wait_for_b1()

        # Initial calibration in steps of 50, rapidly to get close to the goal
        COARSE_STEP = 50

        # Intermediate calibration in steps of 5
        INTERMEDIATE_STEP = 5

        # Final fine calibration in steps of 1
        FINE_STEP = 1

        # always 0 duty for 0V out
        calibration_values.output_calibration_values.append([0])

        # Output 1-10V on each CV output & read the result on AIN
        # Adjust the duty cycle of the CV output until the input is within an acceptable range
        duty = 0
        cvs[cv_n].pin.duty_u16(duty)
        for volts, expected_reading in enumerate(input_readings[1:]):
            oled.centre_text(f"Calibrating...\n CV{cv_n+1} @ {volts+1}V\n1/3")
            sleep(1)
            duty = self.coarse_output_calibration(cvs[cv_n], expected_reading, duty, COARSE_STEP)
            oled.centre_text(f"Calibrating...\n CV{cv_n+1} @ {volts+1}V\n2/3")
            duty = self.fine_output_calibration(
                cvs[cv_n], expected_reading, duty, INTERMEDIATE_STEP, COARSE_STEP
            )
            oled.centre_text(f"Calibrating...\n CV{cv_n+1} @ {volts+1}V\n3/3")
            duty = self.fine_output_calibration(
                cvs[cv_n], expected_reading, duty, FINE_STEP, INTERMEDIATE_STEP
            )

            calibration_values.output_calibration_values[-1].append(duty)

        cvs[cv_n].off()

    def coarse_output_calibration(self, cv, goal_duty, start_duty, step_size):
        """
        Perform a fast, coarse calibration to bring the CV output's duty cycle somewhere close

        This will exit if either the calibration is within +/- the step_size OR if the measured duty
        cycle is higher than the goal (i.e. we've over-shot the goal)

        @param cv  The CV output pin we're adjusting
        @param goal_duty  The AIN duty cycle we're expecting to read
        @param start_duty  The CVx duty cycle we're applying to the output initially
        @param step_size  The amount by which we adjust the duty cycle up to reach the goal

        @return The adjusted output duty cycle
        """
        read_duty = self.read_sample()
        duty = start_duty
        while abs(read_duty - goal_duty) > step_size and read_duty < goal_duty:
            duty += step_size
            cv.pin.duty_u16(duty)
            read_duty = self.read_sample()

        return duty

    def fine_output_calibration(self, cv, goal_duty, start_duty, step_size, prev_step_size):
        """
        Perform a slower, fine calibration to bring the CV output's duty cycle towards the goal

        This exits if the measured duty cycle is within +/- 2*step_size OR if we make
        2*prev_step_size adjustments

        @param cv  The CV output pin we're adjusting
        @param goal_duty  The AIN duty cycle we're expecting to read
        @param start_duty  The CVx duty cycle we're applying to the output initially
        @param step_size  The amount by which we adjust the duty cycle up/down to reach the goal
        @param prev_step_size  The previous iteration's step size, used to limit how many adjustments we make

        @return The adjusted output duty cycle
        """
        MAX_COUNT = 2 * prev_step_size
        count = 0
        read_duty = self.read_sample()
        duty = start_duty
        while abs(read_duty - goal_duty) >= 2 * step_size and count < MAX_COUNT:
            count += 1
            if read_duty < goal_duty:
                duty += step_size
            elif read_duty > goal_duty:
                duty -= step_size
            cv.pin.duty_u16(duty)
            sleep(0.1)
            read_duty = self.read_sample()

        return duty

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

        # make a local copy of the analogue-in readings, extrapolated if necessary,
        # that we can use to perform the output calibration
        if calibration_values.mode == CalibrationValues.MODE_HIGH:
            readings_in = list(calibration_values.input_calibration_values)
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
            self.calibrate_output(i, calibration_values, readings_in)

        ######################################################################################################

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
