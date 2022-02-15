# menu

author: Matthew Jaskula

date: 2022/02/15

labels: utility

A Menu which allows the user to select and execute one of the scripts available to this EuroPi. The menu will includes
the contents of the contrib directory as well as the calibrate script. In addition, handlers are added that allow the
user to exit the running script by rebooting the board back to this menu. Both the selection of a menu item and the
exiting of a running program is achieved with the a 'hold one button and tap the other' action. This will work with 
either button first.

In the menu: 

* button 1: scroll up
* button 2: scroll down
* tap button 1 while holding down button 2: launch selected program
* tap button 2 while holding down button 1: launch selected program

In a program that was launched from the menu:

* tap button 1 while holding down button 2: exit the running program, returning to the menu
* tap button 2 while holding down button 1: exit the running program, returning to the menu

## Setup

In order to use the menu you must copy it to ``main.py`` like any other script. In addition you must have all of the
scripts you'd like to use copied to your pico in the places where the menu expects them. An example of the expected
directory structure is below.

```
/
├── main.py
├── lib
│   ├── contrib
│   │   ├── coin_toss.py
│   │   ├── diagnostic.py
│   │   ├── harmonic_lfos.py
│   │   ├── hello_world.py
│   │   ├── menu.py
│   │   ├── polyrhythmic_sequencer.py
│   │   ├── radio_scanner.py
│   │   └── scope.py
│   ├── calibrate.py
│   ├── europi.py
│   └── ssd1306.py
```

You can use either Thony or rshell to copy the files to the pico. If you'd like to use rshell, the [deploy_firmware
script](scripts/deploy_firmware.rshell) may be useful. It can be called using ``rshell -f scripts/deploy_firmware.rshell``

## Menu Inclusion

In order to be included in the menu a program needs to meet a few additional requirements, described below. Programs are
not required to participate in the menu, but if they do not, they should be added to the ``EXCLUDED_SCRIPTS`` list near 
the top of [``menu.py``](/software/contrib/menu.py).

An example 'hello world' script is shown here and the details discussed below.

``hello_world.py``
```Python
import uasyncio as asyncio  # 1
from europi import oled


async def main():  # 2
    while True:
        oled.centre_text("Hello world")
        await asyncio.sleep(1)  # 3


asyncio.run(main())  # 4

```

1. **Import ``asyncio``:** MicroPython includes an asyncio library that is similar to the library included in CPython 
under the name ``uasyncio``. These libraries are similar enough that it is standard practice to import ``uasyncio`` 
under the alias ``asyncio``.

2. **An asynchronous main method:** The main code of the script should be encapsulated in an asynchronous method so that
you can await on any sleep calls, described below. The method itself does not need to be called 'main'.

3. **``sleep()`` inside any loops:** In order for the user to be able to request that your program exit, your program should 
periodically relinquish control to other threads. This is most easily done by adding calls to `asyncio.sleep()` to any
loops that will run for a significant amount of time. The program's main loop is the most obvious place for this; but,
depending on your code, there may be other loops that also execute for a significant amount of time which should also
sleep.

4. **Execute your main method asynchronously:** Use ``asyncio.run()`` to call your main method asynchronously. This
allows the menu program to properly call your script and wait for its completion.

## Support testing

To support unit testing in CPython, a couple of changes need to be made to the example ``hello_world.py``. In order to have something to test, we'll add the display of a simple counter to our script, a method to increment it, and add a test
that the increment method works properly.

``hello_world.py``
```python
try:  # 1
    import uasyncio as asyncio
except ImportError:
    import asyncio
from europi import oled


def increment(counter):
    return counter + 1


async def main():
    counter = 0
    while True:
        oled.centre_text(f"Hello world\n{counter}")

        counter = increment(counter)

        await asyncio.sleep(1)


if __name__ in ["__main__", "contrib.hello_world"]:  # 2
    asyncio.run(main())

```

``test_hello_world.py``
```python
from hello_world import increment


def test_increment():
    assert increment(1) == 2
```

1. **Import ``uasyncio`` but fall back to ``asyncio``:** Since ``uasyncio`` doesn't exist in CPython, it will raise an 
error if we try to import it. We can catch that error and instead import CPython's ``asyncio``. This will result in code
that may be portable between the two environments. In most cases this is good enough to execute our tests.

2. **A ``__name__`` guard around the ``main()`` call site:** The guard allows the script to be imported without being 
executed in the cases where that is not desired, such as tests. This form of guard is a bit different than what you may
be used to in a standard python script. These two cases allow the script to be executed both with and without the menu.
