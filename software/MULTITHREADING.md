# Multi-Threading

The Raspberry Pi Pico used in EuroPi has 2 CPU cores.  By default only one core is used.  Micropython contains a
module called `_thread` that can be used to run code on both cores.  This can be helpful if, for example, your program
features a lot of mathematical calculations (e.g. floating point operations, trigonometry (e.g. `sin` or `cos`)) that
must be run quickly, but also features a complex GUI to render to the OLED.

## WARNING

Multi-threading is considered an experimental feature, and is intended for advanced programmers only. Adding threads to
your program can introduce many hard-to-debug errors and requires some understanding of some advanced topics not
covered here, including:
- thread safety
- concurrency
- semaphores & mutexes

Unless you're certain you need the additional processing power offered by the EuroPi CPU's second core, it is
_strongly_ recommended that you write your program using a single thread.

## Using `_thread`

To use the `_thread` library you must first import it into your program:
```python
import _thread
```

Your program will always contain at least one thread, referred to as the "main thread."  To start a second thread
you must define a function to execute and start it with `_thread.start_new_thread`:
```python
from europi import *
import time
import _thread

def my_second_thread():
    """The secondary thread; toggles CV2 on and off at 0.5Hz

    To allow the Python shell to connect when the USB is connected, we must terminate this thread
    when the USB state changes. Otherwise the secondary thread will continue running, blocking the shell
    """
    usb_connected_at_start = europi.usb_connected.value()
    while eurpi.usb_connected.value() == usb_connected_at_start:
        cv2.on()
        time.sleep(1)
        cv2.off()
        time.sleep(1)

def main():
    """The main thread; creates the secondary thread and then toggles CV1 at 1Hz

    This thread will automatically die if the USB is connected for debugging, so we don't
    need to check the USB state here.
    """

    # Start the second thread
    second_thread = _thread.start_new_thread(my_second_thread, ())

    while True:
        cv1.on()
        time.sleep(0.5)
        cv1.off()
        time.sleep(0.5)
```

This is a more complex example that implements the same logic as above, but wrapped in a `EuroPiScript`:
```python
from europi import *
from europi_script import EuroPiScript
import time
import _thread

class BasicThreadingDemo1(EuroPiScript):
    def __init__(self):
        super().__init__()

    def main_thread(self):
        """The main thread; toggles CV1 on and off at 1Hz
        """
        while True:
            cv1.on()
            time.sleep(0.5)
            cv1.off()
            time.sleep(0.5)

    def secondary_thread(self):
        """The secondary thread; toggles CV2 on and off at 0.5Hz
        """
        usb_connected_at_start = europi.usb_connected.value()
        while eurpi.usb_connected.value() == usb_connected_at_start:
            cv2.on()
            time.sleep(1)
            cv2.off()
            time.sleep(1)

    def main(self):
        # Clear the display
        oled.fill(0)
        oled.show()

        second_thread = _thread.start_new_thread(self.secondary_thread, ())
        self.main_thread()

if __name__ == "__main__":
    BasicThreadingDemo1().main()
```

## Best Practices

Because each thread runs on a different core, and the EuroPi's processor only has 2 cores, it is recommended to limit
your program to 2 thread: the main thread, and a single additional thread started with `_thread.start_new_thread`.

Interrupt Service Routines (ISRs), implemented as `handler` functions for button presses and `din` rising/falling edges
have been known to cause threaded programs to hang.  It is therefore recommended to _avoid_ using `handler` functions
in your program:
```python
# To NOT do this:
@b1.handler
def on_b1_rising():
    self.do_stuff()
```

Instead, [`experimental.thread`](/software/firmware/experimental/thread.py) provides a `DigitalInputHelper` class
that can be used inside your main thread to check the state of the buttons & `din` and invoke callback functions
when a rising or falling edge is detected.

For example:
```python
from europi import *
from europi_script import EuroPiScript

import time
import _thread

from experimental.thread import DigitalInputHelper

class BasicThreadingDemo2(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.digital_input_helper = DigitalInputHelper(
            on_b1_rising = self.on_b1_press,
            on_b1_falling = self.on_b1_release,
            on_b2_rising = self.on_b2_press,
            on_b2_falling = self.on_b2_release,
            on_din_rising = self.on_din_high,
            on_din_falling = self.on_din_low
        )

    def on_b1_press(self):
        """Turn on CV4 when the button is held
        """
        cv4.on()

    def on_b1_release(self):
        """Turn off CV4 when the button is released
        """
        cv4.off()

    def on_b2_press(self):
        """Turn on CV5 when the button is held
        """
        cv5.on()

    def on_b2_release(self):
        """Turn off CV5 when the button is released
        """
        cv5.off()

    def on_din_high(self):
        """Turn on CV6 when the signal goes high
        """
        cv6.on()

    def on_din_low(self):
        """Turn off CV6 when the signal drops low
        """
        cv6.off()

    def main_thread(self):
        """The main thread; toggles CV1 on and off at 1Hz and handles the buttons + DIN
        """
        # calling time.sleep will block the input handling, so we need to check the clock instead
        last_state_change_time = time.ticks_ms()
        cv1_on = True
        cv1.on()

        while True:
            # Check the inputs
            self.digital_input_helper.update()

            now = time.ticks_ms()
            if time.ticks_diff(now, last_state_change_time) >= 500:
                last_state_change_time = now
                cv1_on = not cv1_on
                if cv1_on:
                    cv1.on()
                else:
                    cv1.off()

    def secondary_thread(self):
        """The secondary thread; toggles CV2 on and off at 0.5Hz
        """
        usb_connected_at_start = europi.usb_connected.value()
        while eurpi.usb_connected.value() == usb_connected_at_start:
            cv2.on()
            time.sleep(1)
            cv2.off()
            time.sleep(1)

    def main(self):
        # Clear the display
        oled.fill(0)
        oled.show()

        second_thread = _thread.start_new_thread(self.secondary_thread, ())
        self.main_thread()


if __name__ == "__main__":
    BasicThreadingDemo2().main()
```

One of the slowest operations in the EuroPi firmware is updated the OLED. If possible moving any GUI rendering into
a secondary thread is a good idea to optimize your program.  Note that you will likely need to use `Lock` objects
to prevent threads from trying to read/write data at the same time.

```python
from europi import *
from europi_script import EuroPiScript

import math
import _thread

class BasicThreadingDemo3(EuroPiScript):
    def __init__(self):
        super().__init__()

        # Create a lock object to prevent multiple threads from accessing our pixel array
        self.pixel_lock = _thread.allocate_lock()

        # Create an array that we'll store vertical pixel positions in to draw on screen
        self.pixel_heights = []

    def cv_thread(self):
        """The main thread; generates a sine wave on CV1
        """
        CYCLE_TICKS = 10000  # one complete sine wave every N times through the loop

        ticks = 0
        cv1_volts = 0
        while True:
            # convert the tick counter to radians for use with sin/cos
            theta = ticks / CYCLE_TICKS * (2*math.pi)

            # sin gives us [-1, 1], but we need to shift it to [0, MAX_OUTPUT_VOLTAGE]
            cv1_volts = (math.sin(theta) + 1) / 2 * MAX_OUTPUT_VOLTAGE

            # convert the voltage to an integer from 0 to OLED_HEIGHT
            # note that row 0 is the top, so we'll draw a line that goes down as the voltage goes up
            # since this is just an example, that's fine; the math to flip the visualization is left as
            # an exercise for the reader
            with self.pixel_lock:
                self.pixel_heights.append(int(cv1_volts * OLED_HEIGHT / MAX_OUTPUT_VOLTAGE))

                # Restrict the number of pixel heights to match the width of the screen
                if len(self.pixel_heights) >= OLED_WIDTH:
                    self.pixel_heights.pop(0)

            ticks = ticks + 1
            if ticks >= CYCLE_TICKS:
                ticks = 0

            cv1.voltage(cv1_volts)

    def gui_thread(self):
        """Draw the wave shapes to the screen
        """
        usb_connected_at_start = europi.usb_connected.value()
        while eurpi.usb_connected.value() == usb_connected_at_start:
            # clear the screen
            oled.fill(0)

            # Draw the pixels representing our waves
            # Make sure to grab the lock so the arrays aren't modified while we're reading them!
            with self.pixel_lock:
                for i in range(len(self.pixel_heights)):
                    oled.pixel(i, self.pixel_heights[i], 0xff)  # draw a white pixel

            # Show the updated display
            oled.show()

    def main(self):
        second_thread = _thread.start_new_thread(self.gui_thread, ())
        self.cv_thread()


if __name__ == "__main__":
    BasicThreadingDemo3().main()
```

## Cancelling Execution and Thonny

If you use Thonny to debug your EuroPi programs, note that when you cancel execution with `ctrl+C` the second core
will likely still be busy. This can cause Thonny to raise errors when trying to e.g. run another function in the
Python terminal or saving files to the module.

If this happens, simply Stop/Restart the backend via Thonny's Run menu.


## References

- [Official Python `_thread` docs](https://docs.python.org/3/library/_thread.html)
