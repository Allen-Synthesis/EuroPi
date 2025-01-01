"""
This is an example of how to use the SettingsMenu class.

It is not intended to be a useful script, just a convenient programming
reference to show how the menu system _can_ be used.
"""

from configuration import *
from europi import *
from europi_script import EuroPiScript
from experimental.settings_menu import *


class SettingsMenuExample(EuroPiScript):
    def __init__(self):
        super().__init__()

        on_off_labels = {
            True: "On",
            False: "Off"
        }

        # Create the main menu
        # the menu items can be generated ad-hoc like this, or passed
        # as an array generated elsewhere
        self.menu = SettingsMenu(
            menu_items = [
                SettingMenuItem(
                    config_point = FloatConfigPoint(
                        name="cv1_volts",  # every config point must have a unique name!
                        minimum=0.0,
                        maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                        default=0.0,
                    ),
                    prefix="Analog",
                    title="CV1",

                    # This is a function that gets called when the user changes the setting
                    # callback_arg is an additional parameter we can pass to the callback
                    callback=self.set_analog_cv,
                    callback_arg=cv1,

                    # change this to increase the resolution of floats
                    # making it too large may cause issues with flickering
                    # generally 1-2 should be fine, 3 is usable for relatively
                    # small ranges (e.g. 0-1 with 3 decimal places)
                    float_resolution=1,

                    # Create child items that can be accessed with a long-press
                    children=[
                        SettingMenuItem(
                            config_point=FloatConfigPoint(
                                name="cv2_volts",
                                minimum=0.0,
                                maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                                default=0.0,
                            ),
                            prefix="Analog",
                            title="CV2",
                            callback=self.set_analog_cv,
                            callback_arg=cv2,
                            float_resolution=1,
                        ),
                        SettingMenuItem(
                            config_point=FloatConfigPoint(
                                name="cv3_volts",
                                minimum=0.0,
                                maximum=europi_config.MAX_OUTPUT_VOLTAGE,
                                default=0.0,
                            ),
                            prefix="Analog",
                            title="CV3",
                            callback=self.set_analog_cv,
                            callback_arg=cv3,
                            float_resolution=1,
                        ),
                    ]
                ),
                SettingMenuItem(
                    config_point = BooleanConfigPoint(
                        name="cv4_on",
                        default=False,
                    ),
                    prefix="Digital",
                    title="CV4",
                    callback=self.set_digital_cv,
                    callback_arg=cv4,
                    labels=on_off_labels,
                    children=[
                        SettingMenuItem(
                            config_point=BooleanConfigPoint(
                                name="cv5_on",
                                default=False,
                            ),
                            prefix="Digital",
                            title="CV5",
                            callback=self.set_digital_cv,
                            callback_arg=cv5,
                            labels=on_off_labels,
                        ),
                        SettingMenuItem(
                            config_point=BooleanConfigPoint(
                                name="cv6_on",
                                default=False,
                            ),
                            prefix="Digital",
                            title="CV6",
                            callback=self.set_digital_cv,
                            callback_arg=cv6,
                            labels=on_off_labels,
                        ),
                    ]
                ),
            ]
        )

        # Read the persistent settings file and load the settings for the menu's configuration points
        # This will trigger the callbacks as necessary
        self.menu.load_defaults(self._state_filename)

    def set_analog_cv(self, new_value, old_value, config_point, arg=None):
        """
        Callback function for the CV1-3 menu items

        These are floating-point settings that set voltages with 1 decimal point accuracy

        @param new_value  The new value the user has selected
        @param old_value  The previous value
        @param config_point  The ConfigPoint instance the user is editing
        @param arg  A user-defined argument, in this case cvN that we're setting the voltage for
        """
        arg.voltage(new_value)

    def set_digital_cv(self, new_value, old_value, config_point, arg=None):
        """
        Callback function for the CV4-6 menu items

        These are boolean settings that turn gate signals on/off

        @param new_value  The new value the user has selected
        @param old_value  The previous value
        @param config_point  The ConfigPoint instance the user is editing
        @param arg  A user-defined argument, in this case cvN that we're setting the voltage for
        """
        if new_value:
            arg.on()
        else:
            arg.off()

    def main(self):
        while True:
            # We must clear the screen before drawing the menu and
            # call .show() afterwards
            # You may draw additional graphics/text on top of the menu
            # before calling.draw() if desired
            oled.fill(0)
            self.menu.draw()
            oled.show()


if __name__ == "__main__":
    SettingsMenuExample().main()
