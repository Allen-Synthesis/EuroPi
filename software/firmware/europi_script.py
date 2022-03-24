"""Provides a base class for scripts which wish to participate in the bootloader menu."""
import os
import json
from json.decoder import JSONDecodeError


class EuroPiScript:
    """A base class for scripts which wish to participate in the bootloader menu.

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

    .. note::
       EuroPiScripts should not call ``europi.reset_state()`` as this call would remove the button handlers that
       allow the user to exit the program and return to the menu. Similarly, EuroPiScripts should not override the
       handlers that provide this functionality.
    """

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

    def save_state(self, state: str):
        """Take state in persistence format as a string and write to disk.
        
        .. note::
            Be mindful of how often `save_state_bytes()` is called because
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

        ::

            # https://docs.python.org/3/library/struct.html#format-characters
            format_string = "b?"
            state = pack(format_string, 2, True)
            super().save_state_bytes(state)
        """
        return self._save_state(state, mode='wb')

    def save_state_json(self, state: dict):
        """Take state as a dict and save as a json string.

        .. note::
            Be mindful of how often `save_state_json()` is called because
            writing to disk too often can slow down the performance of your
            script. Only call save state when state has changed and consider
            adding a time since last save check to reduce save frequency.

        ::

            # Save the current state variables as JSON.
            state = {
                "counter": self.counter,  # int
                "enabled": self.enabled,  # bool
            }
            super().save_state_json(state)
        """
        json_str = json.dumps(state)
        return self._save_state(json_str)

    def _save_state(self, state: str, mode: str ='w'):
        with open(self._state_filename, mode) as file:
            file.write(state)

    def load_state(self) -> str:
        """Check disk for saved state, if it exists, return the raw state value as a string."""
        return self._load_state()

    def load_state_bytes(self) -> bytes:
        """Check disk for saved state, if it exists, return the raw state value as bytes.
        
        ::

            # Check for a previously saved state. If it exists, return state as a
            # byte string. If no state is found, an empty string will be returned.
            state = super().load_state_bytes()

            # Unpack the state bytes using the given format string, which in our
            # example unpacks an integer and bool.
            self.count, self.enabled = unpack(format_string, state)
        """
        return self._load_state(mode="rb")

    def load_state_json(self) -> dict:
        """Load previously saved state as a dict.

        ::

            # Check for a previously saved state. If it exists, return state as a
            # dict. If no state is found, an empty dictionary will be returned.
            state = super().load_state_json()

            # Set state variables with default fallback values if not found in the
            # json save state.
            self.counter = state.get("counter", 0)
            self.enabled = state.get("enabled", True)
        """
        json_str = self._load_state()
        if json_str == "":
            return {}
        try:
            return json.loads(json_str)
        except JSONDecodeError as e:
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
