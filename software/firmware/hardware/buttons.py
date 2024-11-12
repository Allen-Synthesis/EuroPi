from hardware.io import DigitalReader


class Button(DigitalReader):
    """A class for handling push button behavior.

    Button instances have a method ``last_pressed()``
    (similar to ``DigitalInput.last_triggered()``) which can be used by your
    script to help perform some action or behavior relative to when the button
    was last pressed (or input trigger received). For example, if you want to
    call a function to display a message that a button was pressed, you could
    add the following code to your main script loop::

        # Inside the main loop...
        if b1.last_pressed() > 0 and ticks_diff(ticks_ms(), b1.last_pressed()) < 2000:
            # Call this during the 2000 ms duration after button press.
            display_button_pressed()

    Note, if a button has not yet been pressed, the ``last_pressed()`` default
    return value is 0, so you may want to add the check `if b1.last_pressed() > 0`
    before you check the elapsed duration to ensure the button has been
    pressed. This is also useful when checking if the digital input has been
    triggered with the ``DigitalInput.last_triggered()`` method.

    """

    def __init__(self, pin, debounce_delay=200):
        super().__init__(pin, debounce_delay)

    def last_pressed(self):
        """Return the ticks_ms of the last button press

        If the button has not yet been pressed, the default return value is 0.
        """
        return self.last_rising_ms
