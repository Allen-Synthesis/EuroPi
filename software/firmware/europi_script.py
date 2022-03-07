import os

class EuroPiScript:
    """Base class for scripts which wish to participate in the bootloader menu.
     
    To make your script compatible with the menu, you must define your script
    as a class that inherits this base class. For example::
        from europi_script import EuroPiScript
        
        MyScript(EuroPiScript):
            # init and other methods
            # Override main with your script main method.
            def main(self):
                # Your script's main loop.
    
    """

    def __init__(self) -> None:
        self._state_filename = f"saved_state_{self.display_name()}.txt"

    def main(self):
        """Override this method with your script's main loop method."""
        raise NotImplementedError

    @classmethod
    def display_name(cls):
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
