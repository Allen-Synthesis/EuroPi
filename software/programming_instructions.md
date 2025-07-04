# Setting up and programming the EuroPi

This document will take you through the steps to get your module ready to program.

> **Note**
> If you already have any version of the firmware or any other code loaded onto your EuroPi and want to ensure a clean installation, or you just want to make sure you have all the most recent scripts available, first follow these instructions:

1. Download [flash_nuke.uf2](https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython#flash-resetting-uf2-3083182) from Adafruit.

2. Holding down the white button labeled 'BOOTSEL' on the Raspberry Pi Pico, connect the module to your computer via the USB cable.
> **Note**
> If you are already running the menu system on the EuroPi (with a version greater or equal to X.X.X) and would rather not take the module out of your rack, you can instead run the script `_Bootloader Mode` while the module is connected to your computer over USB, and the module will enter bootloader mode

![_DSC2400](https://user-images.githubusercontent.com/79809962/148647201-52b0d279-fc1e-4615-9e65-e51543605e15.jpg)

3. Open your file manager and drag and drop the downloaded `flash_nuke.uf2` onto the new drive named 'RPI-RP2'. This will wipe your Pico clean, ready for a new installation of the firmware.

4. The Pico will automatically eject once the process is completed.

5. Continue to [Setting Up](#setting-up) as normal.

 ## Optional Quick start

> **Warning**
> This version of firmware will not let you override `main.py` nor can you modify existing scripts. Do not use this version of the firmware if you plan to write custom scripts for the EuroPi.

The quickest way to get your EuroPi flashed with the latest firmware is to head over to the [releases](https://github.com/Allen-Synthesis/EuroPi/releases) page and download the latest `europi-vX.Y.Z.uf2` file. Then follow the 'BOOTSEL' instructions above to flash the EuroPi firmware to your pico.

## Pico Setup

This section assumes you are using the Raspberry Pi Pico (or a compatible clone) featuring the RP2040 processor.  If you
are using a different model of Pico, e.g. the Pico W, or Pico 2, see [below](#alternative-picos).

### Downloading Thonny
To start with, you'll need to download the [Thonny IDE](https://thonny.org/). This is what you will use to program and debug the module.

![Thonny](https://i.imgur.com/UX4uQDO.jpg)

### Installing the firmware
1. Download the [most recent firmware](https://micropython.org/download/rp2-pico/) from the MicroPython website.
2. Holding down the white button labeled 'BOOTSEL' on the Raspberry Pi Pico, connect the module to your computer via the USB cable.

    ![_DSC2400](https://user-images.githubusercontent.com/79809962/148647201-52b0d279-fc1e-4615-9e65-e51543605e15.jpg)

3. Open your file manager and drag and drop the downloaded .uf2 onto the new drive named 'RPI-RP2'.
4. The Pico will automatically eject once the process is completed.

### Installing the OLED library
1. Disconnect the Pico from the USB cable.
2. Reconnect, this time without holding down the button on the back.

    ![_DSC2401](https://user-images.githubusercontent.com/79809962/148647207-b43a2e44-0ca2-48d0-b13c-b5d091b44ae1.jpg)

3. Open up Thonny if not already open, and go to the bottom right where you can select the interpreter.
4. Click to select interpreter and choose 'MicroPython (Raspberry Pi Pico)'.

    ![Interpreter Select](https://i.imgur.com/XeRem1w.jpg)

5. **Important**: Wait until the Shell window at the bottom shows the MicroPython version and the purple ```>>>``` symbol.

    ![image](https://user-images.githubusercontent.com/79809962/196224993-70a7a662-90ca-45df-90f6-a2c1f1f70a9e.png)

6. Click Tools -> Manage Packages to open the package manager.
7. Type 'micropython-ssd1306' into the search box and click 'Search on PyPi'
8. Click the result named 'micropython-ssd1306'.

    ![ssd1306 library](https://i.imgur.com/7t2mWHh.jpg)

9. Click 'Install'.
10. You will see that a folder has been created inside the Pico named 'lib', which contains the new file 'ssd1306.py'.

    ![ssd1306 inside lib](https://i.imgur.com/jkmeaFM.jpg)

### Installing the EuroPi library

Use the exact same process as for the ssd1306 library to install the europi library:
1. Type 'micropython-europi' into the search box and click 'Search on PyPi'
2. Click the result named 'micropython-europi'.

    ![image](https://user-images.githubusercontent.com/79809962/156630180-7f727567-89b1-4b8a-a3e0-63f2da3ea30c.png)

3. Click 'Install'.
4. You will now see several new files, including 'europi.py' alongside the 'ssd1306.py' inside the 'lib' folder.

### (Optional) Installing the EuroPi Contrib library

The EuroPi Contrib library will make user-contributed software available on your EuroPi when using the [Menu](/software/contrib/menu.md) software. To install it, follow the same steps as the previous libraries on Thonny:

1. Type 'micropython-europi-contrib' into the search box and click 'Search on PyPi'
1. Click the result named 'micropython-europi-contrib'.

    ![Screenshot from 2023-07-14 03-02-02](https://github.com/Allen-Synthesis/EuroPi/assets/5189714/6690e1e3-56e1-49d6-8701-6f5912d10ba1)

1. Click 'Install'.
1. You will now see a `contrib` folder inside the `lib` folder which contains several software options with the extension `.py`.

## Alternative Picos

The Raspberry Pi Pico family has several different versions, all of which are mechanically and electronically interchangeable. This means
you can swap the Raspberry Pi Pico for the newer Pico 2 to take advantage of the RP2350 CPU's higher clock speed, or a Pico W/Pico 2 W
to add wi-fi connectivity to your EuroPi.

Each Pico model has its own MicroPython firmware:
- [Raspberry Pi Pico](https://micropython.org/download/RPI_PICO/) (the default for EuroPi)
- [Raspberry Pi Pico W](https://micropython.org/download/RPI_PICO_W/)
- [Raspberry Pi Pico 2](https://micropython.org/download/RPI_PICO2/)
- [Raspberry Pi Pico 2 W](https://micropython.org/download/RPI_PICO2_W/)
It is recommended to download the latest stable release for your Pico model.

Once the firmware is installed, continue installing the rest of the software:
1. [Installing the OLED library](#installing-the-oled-library)
2. [Installing the EuroPi library](#installing-the-oled-library)
3. [Installing the EuroPi Contrib library](#optional-installing-the-europi-contrib-library)

Once the software is installed, you will need to [configure the software](/software/CONFIGURATION.md#system) to finish setting up
the Pico.


## Next Steps

Now that you have installed the europi.py and ssd1306 libraries, you are ready to take the next step with the module.

* [Option 1](#install-the-contrib-scripts-and-setup-the-menu): Install all of the contrib scripts and use the bootloader menu
* [Option 2](#write-your-own-program-from-scratch): Start writing your own program from scratch
* [Option 3](#copy-someone-elses-program-to-run-on-your-module): Use someone else's program from the [contrib folder](/software/contrib/)
* [Option 4](#calibrate-the-module): Calibrate the module for higher accuracy


### Install the contrib scripts and setup the menu

The easiest way to start using EuroPi is to [install the `europi_contrib` library](#optional-installing-the-europi-contrib-library).
This will automatically create `lib/main.py` containing the following:

```python
import gc
from contrib.menu import *

gc.collect()
BootloaderMenu(EUROPI_SCRIPTS).main()
```

Copy this file from the `lib` directory into the root folder of the Pico using Thonny's file browser.
This file, when copied to the root folder, will automatically run a menu when EuroPi boots, allowing you to select a program from
the list to run.  After choosing a program, EuroPi will automatically restart that program next time it powers-on.  To return to
the menu, reset EuroPi by holding `B1` and `B2` for a few seconds.

If this is a brand new EuroPi, or you have just reinstalled the software, we recommend running
the [`~Calibrate`](#calibrate-the-module) program first. Calibrating is optional, but if you
plan on using EuroPi to produce [quantized](/software/contrib/quantizer.md) outputs it will
improve the accuracy.


#### Navigating the menu

To navigate the menu use the right knob. Turning clockwise will scroll down and turning anticlockwise will scroll up.

To run the selected program, press the either button once.  The last-run program will automatically start the next time you power-on your EuroPi.

To return to the main menu at any time, press and hold both buttons for 0.5s.


### Write your own program from scratch

To program the module, just create a new Python file, and then press Ctrl-Shift-S to save as to the Raspberry Pi Pico, and name it 'main.py'.
If you have [installed `europi_contrib`](#optional-installing-the-europi-contrib-library)
your module will already have the default `main.py` installed on it. If this is the case, you
may freely modify its contents. Note that if you reinstall or upgrade `europi_contrib` you will
lose any modifications you've made to `main.py`, so make sure to keep a backup.

Alternatively, you can create your program inside the `lib/contrib` directory, and add it to
`lib/contrib/menu.py` to launch it from the main menu.

#### Accessing EuroPi Hardware

For your program to make use of EuroPi's inputs and outputs add the line
`from europi import *` to the top of your program:

  ![From europi import](https://i.imgur.com/UK3nJcV.jpg)

The `europi` module contains all of the objects and methods necessary for reading the six inputs
- `ain`, the analogue input jack;
- `din`, the digital input jack;
- `b1` and `b2`,  the two buttons; and
- `k1` and `k2`, the two knobs
and the six outputs: `cv1`-`cv6`.

Now you have access to the inputs and outputs using easy methods, which you can read about more in the [README.md](/software/README.md) of the software folder.


### Copy someone else's program to run on your module

1. Use the exact same process as for the ssd1306 and europi libraries to install the europi-contrib library:
   1. In Thonny, click Tools -> Manage Packages to open the package manager.
   2. Type 'europi' into the search box and click 'Search on PyPi'
   3. Click the result named 'micropython-europi-contrib'.
   4. Click 'Install'.
2. You will now see the new directory 'contrib' inside the 'lib' folder, containing the contrib scripts.
3. You can now choose any script from inside this contrib folder to run on your module. When you've chosen, double click the file on the Pico to open it.
4. Press 'Ctrl-Shift-S' to Save As, and choose 'Raspberry Pi Pico'

  ![image](https://user-images.githubusercontent.com/79809962/151053911-7145ddb6-12e9-4606-909c-e1f888e3b4b9.png)
5. Name the file ``main.py``, being careful to include the '.py' so the module knows it is a Python file. If you do not name it ``main.py``, the module will not know to automatically run your program whenever it is connected to power. Save the file to the root directory of the Pico (not inside any folders)

  ![image](https://user-images.githubusercontent.com/79809962/151054018-0f495bb5-067e-4cd6-9640-c38e44a216de.png)
6. Now you can disconnect the module from your computer, connect it to rack power, and the your chosen script will run automatically.


### Calibrate the module

To use the module for accurately reading and outputting voltages, you need to complete a calibration process. This will allow your specific module to account for any differences in components, such as resistor tolerances.
If you do not wish to calibrate the module and don't mind your voltages being slightly inaccurate, simply skip to the programming step and your module will use default values.

> **Note**
> If you have just installed the menu, simply run the calibration script and skip to step 2.

1. To begin, you need to choose the `calibrate.py` file and save it as `main.py` in the root directory, as we did in [Option 2](#copy-someone-elses-program-to-run-on-your-module) above. You can obtain the `calibrate.py` file from either the `lib/tools` directory on your Pico, or from [the firmware directory in the repository](/software/firmware/tools/calibrate.py).
2. Make sure your module is connected to rack power for the calibration process. It doesn't matter if it connected to USB as well, however if it is it will give an extra warning to turn on rack power which you need to skip using button 1.
3. Turn on the rack power supply, and the screen will display 'Calibration Mode'. If it doesn't, try [troubleshooting](../troubleshooting.md).
4. See [calibration](/software/firmware/tools/calibrate.md) for details on the calibration process.


# Programming Limitations

As with all hardware, the EuroPi has certain limitations. Some are more obvious and are required knowledge for any user, and some are more in depth and are only relevant if you will be programming the module yourself.

### Obvious Limitations
- Analogue input is only 0-10V
- Digital input can only detect signals above 0.7V (meaning it may trigger accidentally if you have a noisy 'low' state)
- Outputs, analogue input, and knobs, have a maximum resolution of 12 bits (4096 steps)
- Debouncing of the buttons means that very fast double presses may not be detected

### In Depth Limitations
- Clock pulses shorter than approximately 0.01s (10ms) will not be reliably detected (this depends on clock speed too)
- Reading any analogue source, either the analogue input or knobs, will result in a slight delay of the script (this can be reduced by using fewer samples, at the cost of accuracy)

## API Documentation

Auto-generated API documentation for Europi's core firmware and the user-created `experimental` libraries
can be found [here](https://allen-synthesis.github.io/EuroPi/).
