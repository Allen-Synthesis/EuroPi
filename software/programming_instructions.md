# Setting up and programming the EuroPi

This document will take you through the steps to get your module ready to program.  
  
## Setting Up
  
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

5. Click Tools -> Manage Packages to open the package manager.
6. Type 'ssd1306' into the search box and click search.
7. Click the result named 'micropython-ssd1306'.

    ![ssd1306 library](https://i.imgur.com/7t2mWHh.jpg)

8. Click 'Install'.
9. You will see that a folder has been created inside the Pico named 'lib', which contains the new file 'ssd1306.py'.

    ![ssd1306 inside lib](https://i.imgur.com/jkmeaFM.jpg)

### Installing the europi library

1. Open the [europi.py](/software/firmware/europi.py) file from this repository.
2. Copy its entire contents by selecting all and pressing Ctrl-C.
3. Open Thonny back up and press Ctrl-N to create a new file.
4. Paste the europi.py contents into the new file, and press Ctrl-Shift-S to save as.
5. Choose Raspberry Pi Pico.

    ![Save to Pico](https://i.imgur.com/BTn7kAz.jpg)

6. Navigate inside the 'lib' folder by double clicking it.
7. Save the new file as 'europi.py', making sure to include the '.py' at the end.

    ![Save europi.py](https://i.imgur.com/vK5Xgik.jpg)

### Calibration
  
If you wish to calibrate the module yourself, you will need access to fixed voltage sources, ideally up to 10V.
  
**NOTE: For calibration, the module *must* be connected to both USB for programming *and* rack power for ±12V.**

If you don't need high accuracy, you can finish at this point and begin programming (skip to the next section).
If however you'd like your module to be able to accurately read and output specific voltages, then get ready your voltage source(s).

A benchtop power supply is ideal for this, but you could potentially use another Eurorack module if the voltage is accurate enough (it's reccommended to use a multimeter to make sure the voltage you input to the program variables is accurate).

1. Now make sure the module is connected to both your computer and to Eurorack power, and that the power is switched on.
1. Either run [calibrate.py](/software/firmware/calibrate.py) from Thonny, or save it to the module as `main.py` in the root directory.
1. Then simply run the program and follow the instructions in the terminal.
1. If at any point you do something wrong, just stop the program and run it again to start again.
1. Once the screen shows 'Calibration complete', you're all done! Now you can move on to programming

## Programming

To program the module, just create a new Python file, and then press Ctrl-Shift-S to save as to the Raspberry Pi Pico, and name it 'main.py'.  
Do not save files to the 'lib' folder, as this is just for libraries to be imported rather than programs that you will write.  
Now import the entire europi library by simply adding the line 'from europi import *'

![From europi import](https://i.imgur.com/UK3nJcV.jpg)

Now you have access to the inputs and outputs using easy methods, which you can read about more in the [README.md](/software/README.md) of the software folder.
