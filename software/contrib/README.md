# Contributions

If you have written a program that you would like to share to the community, please feel free to submit a Pull Request.  
To do this, you'll need to fork this repository to your own page, upload your program to the contrib folder, and then submit a request to merge your fork back into this repository.
  
### Submission Format
Please include:
- Your name (or username) and the date you uploaded the program (dd/mm/yy) as a comment at the top of the file
- Either a description as a comment at the top of the code itself if the program is very simple/obvious, or as a file with the exact same name as the program but with the '.md' suffix. It's much preferred to always have an 'md' file rather than a comment, as it's a much nicer way to view the program's function and a place for you to explain how the inputs and outputs are used.
- The labels that apply to the program. You can come up with any labels, but some suggested ones are listed in the labels section of this page

### Labels
Suggested labels:
LFO, Quantiser, Random, CV Generation, CV Modulation, Sampling, Controller

Just write any labels that apply to your program, including any not listed here but that you think are relevant, in the 'md' file for your program.
Think of this as the second most obvious way to see what your program does, after the title.

### File Naming
Please use all lowercase and separate words with underscores for your program names.
e.g. the files associated with a program for a Sample and Hold function would look as follows:  
  
**sample_and_hold.py  
sample_and_hold.md**

### Menu Inclusion

In order to be included in the menu a program needs to meet a few additional requirements. See 
[menu.md](/software/contrib/menu.md) for details. Programs are not required to participate in the menu in order to be 
accepted, but it is nice.

### Save/Load Script State

You can add a bit of code to enable your script to save state upon change, and load previous state at startup.

```python

class BeatCounter(EuroPiScript):

    def __init__(self):
        # The EuroPiScript base class has the method `load_state_json()` to
        # check for a previously saved state. If no state is found, an empty
        # dictionary will be returned.
        state = super().load_state_json()

        # Set state variables with default fallback values if not found in the
        # json save state.
        self.counter = state.get("counter", 0)
        self.enabled = state.get("enabled", True)

        @din.handler
        def increment_beat():
            if self.enabled:
                self.counter += 1
                self.save_state()
        
        @b1.handler
        def toggle_enablement():
            self.enabled = not self.enabled
            self.save_state()

    def save_state(self):
        """Save the current state variables as JSON."""
        state = {
            "counter": self.counter,
            "enabled": self.enabled,
        }
        super().save_state_json(state)
```

See https://github.com/Allen-Synthesis/EuroPi/issues/102 for details.

### If you are unsure
Take a look at other submitted programs to see how to format yours if you are unsure, and feel free to send me any questions at either [contact@allensynthesis.co.uk](mailto:contact@allensynthesis.co.uk)
