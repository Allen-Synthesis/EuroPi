from time import sleep
from europi import oled, b1, b2, ain, cv1, usb_connected
from europi_script import EuroPiScript
from os import stat, mkdir


class Calibrate(EuroPiScript):
    @classmethod
    def display_name(cls):
        """Push this script to the end of the menu."""
        return "~Calibrate"

    def sample(self):
        """
        Read the raw ADC samples from ain over several attempts and return their average

        @return  The average of the ADC samples, rounded to the nearest integer
        """
        N_READINGS = 256
        readings = []
        for i in range(N_READINGS):
            readings.append(ain.pin.read_u16())
        return round(sum(readings) / N_READINGS)

    def wait_for_voltage(self, voltage):
        """
        Wait for the user to connect the desired voltage into ain.

        Pressing B1 confirms they've done it, pressing B2 will skip and return None

        @param voltage  The requested voltage
        @return  The measured sample, or None if the user skipped this measurement
        """
        self.wait_for_b1(0)
        if voltage != 0:
            oled.centre_text(f"""Plug in {voltage:0.1f}V
Done      Skip
 B1        B2""")
            pressed = self.wait_for_button(1)
            if pressed == b2:
                oled.centre_text("Skipping...")
                sleep(1.5)
                return None
        else:
            oled.centre_text(f"Unplug all\n\nDone: Button 1")
            self.wait_for_b1(1)
        oled.centre_text("Calibrating...")
        sleep(1.5)
        return self.sample()

    def text_wait(self, text, wait):
        oled.centre_text(text)
        sleep(wait)

    def wait_for_button(self):
        """
        Wait for either button to be pressed


        @return b1 or b2, indicating what button was maniupulated
        """
        b1_pressed = b1.value() != 0
        b2_pressed = b2.value() != 0
        while not b1_pressed and not b2_pressed:
            sleep(0.05)
            b1_pressed = b1.value() != 0
            b2_pressed = b2.value() != 0
        if b1_pressed:
            return b1
        else:
            return b2

    def wait_for_b1(self, value):
        """
        Wait for b1 to be pressed or released

        @param value  Either 0 or 1, indicating if we're waiting for a release or a press
        """
        while b1.value() != value:
            sleep(0.05)

    def main(self):
        # Test if /lib exists. If not: Create it

        try:
            stat("/lib")
        except OSError:
            mkdir("/lib")

        # Calibration start

        if usb_connected.value() == 1:
            oled.centre_text("Make sure rack\npower is on\nDone: Button 1")
            self.wait_for_b1(1)
            self.wait_for_b1(0)

        self.text_wait("Calibration\nMode", 3)

        oled.centre_text("Choose Process\n\n1:LOW    2:HIGH")
        while True:
            if b1.value() == 1:
                chosen_process = 1
                break
            elif b2.value() == 1:
                chosen_process = 2
                break

        # Input calibration

        readings = []
        if chosen_process == 1:
            # Not every rack can generate both 5 and 10V, but most should have at least one
            # Ask for both voltages, but we can skip one or the other
            readings.append(self.wait_for_voltage(0))
            readings.append(self.wait_for_voltage(5))
            readings.append(self.wait_for_voltage(10))
        else:
            for voltage in range(11):
                readings.append(self.wait_for_voltage(voltage))

        # remove Nones from skipped values in the readings
        #
        done = False
        while not done:
            try:
                readings.remove(None)
            except ValueError:
                done = True

        with open(f"lib/calibration_values.py", "w") as file:
            values = ", ".join(map(str, readings))
            file.write(f"INPUT_CALIBRATION_VALUES=[{values}]")

        # Output Calibration

        oled.centre_text(f"Plug CV1 into\nanalogue in\nDone: Button 1")
        self.wait_for_b1(1)
        oled.centre_text("Calibrating...")

        if chosen_process == 1:
            new_readings = [readings[0]]
            m = (readings[1] - readings[0]) / 10
            c = readings[0]
            for x in range(1, 10):
                new_readings.append(round((m * x) + c))
            new_readings.append(readings[1])
            readings = new_readings

        output_duties = [0]
        duty = 0
        cv1.duty_u16(duty)
        reading = self.sample()
        for index, expected_reading in enumerate(readings[1:]):
            while abs(reading - expected_reading) > 0.002 and reading < expected_reading:
                cv1.duty_u16(duty)
                duty += 10
                reading = self.sample()
            output_duties.append(duty)
            oled.centre_text(f"Calibrating...\n{index+1}V")

        with open(f"lib/calibration_values.py", "a+") as file:
            values = ", ".join(map(str, output_duties))
            file.write(f"\nOUTPUT_CALIBRATION_VALUES=[{values}]")

        oled.centre_text("Calibration\nComplete!")


if __name__ == "__main__":
    Calibrate().main()
