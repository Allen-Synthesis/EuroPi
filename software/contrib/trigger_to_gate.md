# Trigger to Gate

- author: Andy Bulka (tcab) (github.com/abulka)
- date: 2023-05-13
- labels: trigger, gate, clock

Trigger to Gate: Generates a gate on cv1 in response to a trigger on din.
Control the outgoing pulse width with k1. Control the delay between the trigger
and the gate starting with k2. Handy for converting short triggers (e.g. 1ms)
into longer gates (e.g. 10ms) as some eurorack modules don't like short
triggers.

    din = trigger input
    cv1 = gate output
    b1 = toggle gate output on/off
    k1 = length of gate (1-1500ms)
    k2 = delay of gate (0-1500ms)

Clock: Generates an independent (unrelated to din or gate output),
internally driven clock output on cv2. Handy for when you need a simple clock.

    cv2 = clock output
    b1 = toggle clock output on/off
    k1 = length of clock pulse (1-1500ms)
    k2 = period of clock (1-1500ms) - how fast the clock pulses

## Usage

You can have both the gate and clock outputs running at the same time. There are
two configuration screens, gate and clock. The screen mode is toggled by pressing b2.

    b2 = toggle between gate/clock screen

This is what the screens look like:

```
                       Trigger to Gate Screen                                           
         ┌─────────────────────────────────────────────┐                                
         │ Incoming din pulse length    din period   . │ ◀────── . symbol means that    
         │                                             │         that gate output is on 
(knob 1) │ Length of Gate                              │                                
         │                                             │         (b1 toggles)           
(knob 2) │ Gate Delay                                  │                                
         └─────────────────────────────────────────────┘                                
                                                                                        
                           Clock Screen                                                 
         ┌─────────────────────────────────────────────┐                                
         │ Clock bpm                                 . │ ◀────── . symbol means that    
         │                                             │         that clock output is on
(knob 1) │ Clock pulse length                          │                                
         │                                             │         (b1 toggles)           
(knob 2) │ Clock period (speed)                        │                                
         └─────────────────────────────────────────────┘                                                             
```

## Note on changing knob values:

### Pass-through knob values

Because the knobs are used in two different modes, we run into the problem of the physical
knob position not matching the value when you switch between modes. To solve this, the knobs
use "pass-through" logic, which you may be familiar with when loading presets into a hardware
synthesiser.

The term "pass-through" refers to the technique of enabling a parameter's value
only when the knob physical position passes through the existing value, which
prevents sudden jumps in values when you switch screen modes.

If turning a knob doesn't change the value, it's because the knob is not yet
"passed-through" the current value. Simply turn the knob until it does change. For example,
if the existing value is 0 and your physical knob position is at "5 o'clock" then you need to
turn the physical knob counter-clockwise until it passes through 0 and then clockwise again
to your required value.

### Hysteresis Mitigation

The knobs also use hysteresis mitigation which prevents the values flickering,
even though you are not turning the knob. There is a 1 second timeout when you
can dial in the exact value you want, then the knob value will "lock". To unlock
the knob value, turn the knob past the threshold again.

## Installation

If your version of the EuroPi `software/contrib` does not have this
script already bundled then you will need to manually install it by copying it
onto the EuroPi.

> There is limited file management on the EuroPi via the Thonny IDE. Thonny can
delete files and copy files into the root of your EuroPi's filesystem, but to
move files into position you will have to use Python.  Here are some handy
snippets to help you move files around.

### Steps

1. Copy `trigger_to_gate.py` to `/lib/contrib/trigger_to_gate.py` on your EuroPi.

```python
import os
os.listdir('/')
os.rename('/trigger_to_gate.py', '/lib/contrib/trigger_to_gate.py')
```

2. Edit `main.py` to include the Trigger to Gate script in the menu:

If you have Firmware `0.7.1` or earlier

```python
EUROPI_SCRIPTS = [
    ....
    TriggerToGate,  # <-- add this line
]
```

If you have firmware `0.8.1` or later

```python
EUROPI_SCRIPTS = [
    ....
    "contrib.trigger_to_gate.TriggerToGate",  # <-- add this line
]
```

### Handy Python Snippets

```python
import os
os.listdir('/')
os.rename('/lib/contrib/menu.py', '/menu.py')
os.rename('/menu.py', '/main.py')
os.rename('/main.py', '/menu.py') # to undo
```

Rename `menu.py` to `main.py` to run it on boot.

# Documentation of Classes used by Trigger to Gate

Documentation needed to be moved from the classes in the code to here, due to memory constraints on the EuroPi.

```python
class KnobWithHysteresis:
    """
    This is a class to cure the hysteresis problem with the rotary encoder.

    You can set any value within the `delay` time period and it will be
    accepted but once the lock window time expires you have to move the knob by at
    least `tolerance` to change the value, at which point the lock window is
    extended by `delay` time.

    Usage:

        k1 = KnobWithHysteresis(k1)  # backwards compatible, no hyteresis mitigation
        k1 = KnobWithHysteresis(k1, tolerance=2)  # set tolerance to 2, hysteresis mitigation
    """
```

```python
class KnobWithPassThrough:
    """
    Disable changing value till knob is moved and "passes-through" the current cached value.
    Useful for when you have a knob that is used in two different modes and you don't want
    the value to jump when you switch modes (think recalling presets on a hardware synth).

    Usage
    -----
    Simplest usage is to wrap a knob with this class, passing the initial value e.g.

        k1 = KnobWithPassThrough(k1, initial=50)
        k1.choice(list(range(0, 400)))  # use as normal

    If you want to switch modes, you need to create two instances of this class,
    wrapping the same knob e.g.

        k1_mode1 = KnobWithPassThrough(k1, initial=50)
        k2_mode2 = KnobWithPassThrough(k1, initial=100)

    When you switch modes e.g. as a result of a button press, you need to call `reactivate()` on the
    mode you are switching to, in order to tell it to use its cached value until physical knob 
    pass-through has ocurred e.g.

        @b2.handler_falling
        def button2_click():
            mode = 2 if mode == 1 else 1
            if mode == 1:
                k1_mode.reactivate()
            elif mode == 2:
                k2_mode.reactivate()
    """
```

```python
class Scheduler:
    """
    A simple scheduler for running tasks at a given time in the future.

    Usage:
    ------
    s = Scheduler()

    s.schedule_task(some_function, ms=1000)  # run some_function in 1 second
    s.schedule_task(some_other_function, ms=2000)  # run some_other_function in 2 seconds
    
    while s.enabled:
        s.run_once()
        utime.sleep_ms(10) # the lower this is, the more accurate the schedule will be

    def some_function():
        print("some_function called")
        s.schedule_task(some_function, ms=1000)  # reschedule some_function to run in 1 second

    You can stop your loop using s.stop() which sets s.enabled to False,
    or just interrupt it with Ctrl-C. Its really up to you how you implement the loop.

    Callbacks can be any callable object, e.g. a function, a method, a lambda, etc.
    No support for passing arguments to callbacks yet.

    Implementation Note: MicroPython does not support methods having reference
    equality (regular functions are ok) so we have to compare callbacks using the
    callback's function name string rather than by the callback function object
    itself.
    """
```


