# Screensaver

This script has no inputs and no outputs. It simply displays the EuroPi logo on the screen at a random location every
2 seconds.

The main intention of this script is to provide the `Screensaver` class, which can be used by other scripts to help
prevent burn-in.

## Usage

To instantiate a `Screensaver` simply call its constructor.  To draw the logo in random positions, call the
`.draw()` method inside your application's main loop.  Alternatively, call `.draw_blank()` to clear the screen.

e.g.
```
class MyEuroPiScript(EuroPiScript):
    # ...

    def main(self):
        scr = Screensaver()

        while True:
            idle_time = # ... calculate the amount of time the module's been active and idle

            if idle_time > BLANK_SCREEN_THRESHOLD:
                scr.draw_blank()
            elif idle_time > SCREENSAVER_THRESHOLD:
                scr.draw()
            else:
                # ... show whatever the script normally shows on-screen
```
