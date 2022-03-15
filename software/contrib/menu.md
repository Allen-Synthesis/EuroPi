# Menu 
A Menu which allows the user to select and execute one of the scripts available to this EuroPi. The menu will 
include the ``EuroPiScripts`` included in the ``EUROPI_SCRIPT_CLASSES`` List. Button press handlers are added that allow
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

## Support testing

For a simple, but complete example of a testable ``EuroPiScript`` see [hello_world.py](/software/contrib/hello_world.py)
and its test [test_hello_world.py](/software/tests/contrib/test_hello_world.py).
