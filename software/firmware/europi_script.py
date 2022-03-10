import os

class EuroPiScript:
    """A Base class for scripts which wish to participate in the bootloader menu.
     
    To make your script compatible with the menu, you must:
      
      * define your script as a class that inherits from this base class.
      * override ``main()`` to define your script's main loop

    For example::
    
       from europi_script import EuroPiScript
    
       class HelloWorld(EuroPiScript):
           # init and other methods
           # Override main with your script main method.
           def main(self):
               # Your script's main loop.
    
    """

    def __init__(self) -> None:
        self._state_filename = f"saved_state_{self.display_name()}.txt"

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
        print(f"saved file: {self._state_filename}")

    def _load_state(self) -> str:
        print(f"loading file: {self._state_filename}")
        try:
            with open(self._state_filename, 'r') as file:
                return file.read()
        except OSError as e:
            print(e)
            return ""
    
    def _reset_state(self):
        print(f"deleting file: {self._state_filename}")
        try: 
            os.remove(self._state_filename)
        except OSError:
            pass
