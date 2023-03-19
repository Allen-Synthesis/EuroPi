# Menu 
A Menu which allows the user to select and execute one of the scripts available to this EuroPi. The menu will 
include the ``EuroPiScripts`` included in the ``EUROPI_SCRIPTS`` List. Button press handlers are added that allow
the user to exit the script and return to the menu by holding both buttons down for a short period of time. If the 
module is restarted while a script is running it will boot right back into that same script.

In the menu: 

* **Button 1:** choose the selected item
* **Button 2:** choose the selected item
* **Knob 1:** unused
* **Knob 2:** change the current selection

In a program that was launched from the menu:

* Hold both buttons for at least 0.5s and release to return to the menu.

## Script requirements

An example 'hello world' script is shown here and the requirement details are discussed below.

``hello_world.py``
```Python
from europi import oled
from europi_script import EuroPiScript  # 1

class HelloWorld(EuroPiScript):  # 2
    def main():  # 3
        oled.centre_text("Hello world")


if __name__ == "__main__":  #4
    HelloWorld().main()
```

1. **Import ``EuroPiScript``:** Import the ``EuroPiScript`` base class so that we can implement it below.
2. **Define a class that extends ``EuroPiScript``:** This defines your script as one that adheres to the menu's requirements.
3. **A ``main()`` method:** The main code of the script should be encapsulated in an 'main()' method. The menu will initialize your class and then call this function to launch your script.
4. **a ``__name__`` guard around the ``main()`` call site:** This allows your code to work correctly when it itself is the ``main.py``. To read more about name guarding, see the [Python Documentation](https://docs.python.org/3/library/__main__.html), or alternatively just copy and paste the example above, using your own script's name in place of 'HelloWorld'.

## Menu Inclusion

Once you have a script that conforms to the above requirements, you can add it to the list of scripts that are included
in the menu. This list is in [menu.py](/software/contrib/menu.py) in the contrib folder. You will need to add two lines,
one to import your class and one to add the class to the list. Use the existing scripts as examples.

Note that the scripts are sorted before being displayed, so order in this file doesn't matter.

## Save/Load Script State

You can add a bit of code to enable your script to save state upon change, and load previous state at startup.

When adding save state functionality to your script, there are a few important considerations to keep in mind:

1. Frequency of saves - scripts should only save state to disk when state changes, and should not save too frequently because OS write operations are expensive in terms of time. Saving too frequently will affect the performance of a script.
1. Save state file size - The Pico only has about 1MB of free space available so save state storage format is important to keep as minimal as possible.
1. No externally influenced input - The instance variables your script saves should not be externally influenced, meaning you should not save the current knob position, current analog input value or current digital input value.

Here is an extension of the script above with some added trivial features that incorporate saving and loading script state.

```python
from europi import oled
from europi_script import EuroPiScript

class HelloWorld(EuroPiScript):
    def __init__(self):
        super().__init__()  # 1

        state = self.load_state_json()  # 2

        self.counter = state.get("counter", 0)  # 3
        self.enabled = state.get("enabled", True)

        @din.handler
        def increment_counter():
            if self.enabled:
                self.counter += 1
                self.save_state()  # 4
        
        @b1.handler
        def toggle_enablement():
            self.enabled = not self.enabled
            self.save_state()  # 4

    def save_state(self):  # 5
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:  # 6
            return

        state = {
            "counter": self.counter,
            "enabled": self.enabled,
        }
        self.save_state_json(state)
    
    def main(self):
        oled.centre_text("Hello world")
```

1. **Initialize base classes** When implementing the `EuroPiScript` base class, its initialization method must be called to initialize its intance variables.

1. **Call the inherited `EuroPiScript` method `load_state_json()`.** The `EuroPiScript` base class has the method `load_state_json()` to check for a previously saved state in JSON format. When initializing your script, call `load_X_state()` where `X` is the persistence format of choice. If no state is found, an empty value will be returned.

1. **Apply saved state variables to this instance.** Set state variables with default fallback values if not found in the json save state.

1. **Save state upon state change.** When a state variable changes, call the save state function.

1. **Implement `save_state()` method.** Provide an implementation to serialize the state variables into a string, JSON, or bytes an call the appropriate save state method.


1. **Throttle the frequency of saves.** Saving state too often could negatively impact the performance of your script, so it is advised to add some checks in your code to ensure it doesn't save too frequently.

## Support testing

For a simple, but complete example of a testable ``EuroPiScript`` see [hello_world.py](/software/contrib/hello_world.py)
and its test [test_hello_world.py](/software/tests/contrib/test_hello_world.py).
