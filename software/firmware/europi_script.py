"""Provides a base class for scripts which wish to participate in the bootloader menu."""
import os

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

    def __init__(self) -> None:
        self._state_filename = f"saved_state_{self.__class__.__qualname__}.txt"

    def main(self) -> None:
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

    #
    # private functions for now, with the intention that they are eventually added to the public API
    #

    def _save_state(self, state: str):
        with open(self._state_filename, 'w') as file:
            file.write(state)

    def _load_state(self) -> str:
        try:
            with open(self._state_filename, 'r') as file:
                return file.read()
        except OSError as e:
            return ""
    
    def _reset_state(self):  # TODO this name clashes with europi.reset_state()
        try: 
            os.remove(self._state_filename)
        except OSError:
            pass
