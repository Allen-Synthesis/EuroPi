"""Provides a base class for scripts which wish to participate in the bootloader menu."""
import os
import json
from utime import ticks_diff, ticks_ms


class EuroPiScript:
    """A base class for scripts which wish to participate in the bootloader menu and add save state functionality.

    **Menu Inclusion**

    To make your script compatible with the menu, you must:

      1. import ``EuroPiScript``
      2. define your script as a class that inherits from this base class.
      3. override ``main()`` to define your script's main loop
      4. Surround the call to ``main()`` with a guard to prevent execution upon import

    An minimal example::

       from europi import oled
       from europi_script import EuroPiScript  # 1

       class HelloWorld(EuroPiScript):  # 2
           def main():  # 3
               oled.centre_text("Hello world")


       if __name__ == "__main__":  # 4
           HelloWorld().main()

    To include your script in the menu it must be added to the ``EUROPI_SCRIPT_CLASSES`` list in ``contrib/menu.py``.

    **Save/Load Script State**

    Optionally, you can add a bit of code to enable your script to save state, and load previous state at startup. By default, when exiting the script to menu selection, ``save_state()`` will be called. Additionally, you can add calls to ``save_state()`` whenever state changes.

    When adding ``save_state()`` calls to your script, there are a few important considerations to keep in mind:

        * Frequency of saves - scripts should only save state to disk when state changes, and should not save too frequently because os write operations are expensive in terms of time. Saving too frequently will affect the performance of a script.
        * Save state file size - The pico only has about 1MB of free space available so save state storage format is important to keep as minimal as possible.
        * No externally influenced input - The instance variables your script saves should not be externally influenced, meaning you should not save the current knob position, current analog input value or current digital input value.

    To add the ability to save and load state, you must:
        
        1. **Initialize base classes** When implementing the ``EuroPiScript`` base class, its initialization method must be called to initialize its intance variables.
        
        2. **Call the inherited EuroPiScript method load_state_X().** The ``EuroPiScript`` base class has ``load_state_X()`` methods to check for a previously saved state of a specific format. When initializing your script, call ``load_state_X()`` where ``X`` is the persistance format of choice. If no state is found, an empty value will be returned.

        3. **Apply saved state variables to this instance.** Set state variables with default fallback values if not found in the json save state.

        4. **Save state upon state change.** When a state variable changes, call the save state function.

        5. **Implement save_state() method.** Provide an implementation to serialize the state variables into a string, JSON, or bytes an call the appropriate save state method.

        6. **Throttle the frequency of saves.** Saving state too often could negatively impact the performance of your script, so it is advised to add some checks in your code to ensure it doesn't save too frequently.


    Here is an extension of the script above with some added trivial features that incorporate saving and loading script state::

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


    .. note::
       EuroPiScripts should not call ``europi.reset_state()`` as this call would remove the button handlers that
       allow the user to exit the program and return to the menu. Similarly, EuroPiScripts should not override the
       handlers that provide this functionality.
    """

    def __init__(self):
        self._last_saved = 0

    def main(self):
        """Override this method with your script's main loop method."""
        raise NotImplementedError

    @classmethod
    def display_name(cls) -> str:
        """Returns the string used to identify this script in the Menu. Defaults to the class name. Override it if you
        would like to use a different name::

           @classmethod
           def display_name(cls):
               return "Hello World"

        Note that the screen is only 16 characters wide. Anything longer will be cut off.
        """
        return cls.__qualname__

    # Save State Methods

    @property
    def _state_filename(self):
        return f"saved_state_{self.__class__.__qualname__}.txt"
    
    def save_state(self):
        """Encode state and call the appropriate persistence save method.
        
        Override this class with the script specific encoding of state into
        the persistence format that best matches its use case. Then call the
        appropriate save method, such as `save_state_json(state)`. See the
        class documentation for a full example.
        """
        pass

    def save_state_str(self, state: str):
        """Take state in persistence format as a string and write to disk.
        
        .. note::
            Be mindful of how often `save_state_str()` is called because
            writing to disk too often can slow down the performance of your
            script. Only call save state when state has changed and consider
            adding a time since last save check to reduce save frequency.
        """
        return self._save_state(state)

    def save_state_bytes(self, state: bytes):
        """Take state in persistence format as bytes and write to disk.

        .. note::
            Be mindful of how often `save_state_bytes()` is called because
            writing to disk too often can slow down the performance of your
            script. Only call save state when state has changed and consider
            adding a time since last save check to reduce save frequency.
        """
        return self._save_state(state, mode='wb')

    def save_state_json(self, state: dict):
        """Take state as a dict and save as a json string.

        .. note::
            Be mindful of how often `save_state_json()` is called because
            writing to disk too often can slow down the performance of your
            script. Only call save state when state has changed and consider
            adding a time since last save check to reduce save frequency.
        """
        json_str = json.dumps(state)
        return self._save_state(json_str)

    def _save_state(self, state: str, mode: str ='w'):
        with open(self._state_filename, mode) as file:
            file.write(state)
        self._last_saved = ticks_ms()

    def load_state_str(self) -> str:
        """Check disk for saved state, if it exists, return the raw state value as a string.
        
        Check for a previously saved state. If it exists, return state as a
        string. If no state is found, an empty string will be returned.
        """
        return self._load_state()

    def load_state_bytes(self) -> bytes:
        """Check disk for saved state, if it exists, return the raw state value as bytes.
        
        Check for a previously saved state. If it exists, return state as a
        byte string. If no state is found, an empty string will be returned.
        """
        return self._load_state(mode="rb")

    def load_state_json(self) -> dict:
        """Load previously saved state as a dict.

        Check for a previously saved state. If it exists, return state as a
        dict. If no state is found, an empty dictionary will be returned.
        """
        json_str = self._load_state()
        if json_str == "":
            return {}
        try:
            return json.loads(json_str)
        except ValueError as e:
            print(f"Unable to decode {json_str}: {e}")
            return {}

    def _load_state(self, mode: str ='r') -> any:
        try:
            with open(self._state_filename, mode) as file:
                return file.read()
        except OSError as e:
            return ""

    def remove_state(self):
        """Remove the state file for this script."""
        try:
            os.remove(self._state_filename)
        except OSError:
            pass
    
    def last_saved(self):
        """Return the ticks in milliseconds since last save."""
        try:
            return ticks_diff(ticks_ms(), self._last_saved)
        except AttributeError:
            raise Exception("EuroPiScript classes must call `super().__init__()`.")
