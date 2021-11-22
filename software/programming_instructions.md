# Setting up and programming the EuroPi

This document will take you through the steps to get your module ready to program.  
  
## Setting Up
  
### Downloading Thonny
To start with, you'll need to download the [Thonny IDE](https://thonny.org/). This is what you will use to program and debug the module.  

![Thonny](https://i.imgur.com/UX4uQDO.jpg)

### Installing the firmware
1. Download the [firmware.uf2](https://github.com/Allen-Synthesis/EuroPi/raw/main/software/firmware/firmware.uf2) file from this repository.
2. Holding down the white button on the Raspberry Pi Pico, connect the module to your computer via the USB cable.
3. Open your file manager and drag and drop the downloaded firmware.uf2 onto the new drive named 'RPI-RP2'.
4. The Pico will automatically eject once the process is completed

### Installing the OLED library
1. Disconnect the Pico from the USB cable.
2. Reconnect, this time without holding down the button on the back.
3. Open up Thonny if not already open, and go to the bottom right where you can select the interpreter.
4. Click to select interpreter and choose 'MicroPython (Raspberry Pi Pico)'

![Interpreter Select](https://i.imgur.com/XeRem1w.jpg)

5. Click Tools -> Manage Packages to open the package manager.
6. Type 'ssd1306' into the search box and click search.
7. Click the result named 'micropython-ssd1306'

![ssd1306 library](https://i.imgur.com/7t2mWHh.jpg)

8. Click 'Install'
9. You will see that a folder has been created inside the Pico named 'lib', which contains the new file 'ssd1306.py'

![ssd1306 inside lib](https://i.imgur.com/jkmeaFM.jpg)

### Installing the europi library

1. Open the [europi.py](https://github.com/Allen-Synthesis/EuroPi/blob/main/software/firmware/europi.py) file from this repository.
2. Copy its entire contents by selecting all and pressing Ctrl-C.
3. Open Thonny back up and press Ctrl-N to create a new file.
4. Paste the europi.py contents into the new file, and press Ctrl-Shift-S to save as.
5. Choose Raspberry Pi Pico.

![Save to Pico](https://i.imgur.com/BTn7kAz.jpg)

6. Navigate inside the 'lib' folder by double clicking it.
7. Save the new file as 'europi.py', making sure to include the '.py' at the end.

![Save europi.py](https://i.imgur.com/vK5Xgik.jpg)

### Calibration

The europi.py program is made to be imported as a library, but you are also able to run it directly to calibrate the module.  
  
If you wish to calibrate the module yourself, you will need access to two fixed voltage sources, ideally 1V and 10V.  
  
As soon as you run the program, a 'calibration.txt' file will be generated, which will allow you to use the module, but they are only default values and will not allow high accuracy input or output.  
  
If you don't need high accuracy, you can finish at this point and begin programming (skip to the next section).
If however you'd like your module to be able to accurately read and output specific voltages, then get ready your voltage source(s).  
A benchtop power supply is ideal for this, but you could potentially use another Eurorack module if the voltage is accurate enough.  

1. If the voltages you plan to use are any different to 1V and 10V, open the europi.py file and change the values of LOW_VOLTAGE and HIGH_VOLTAGE to whichever you are using. As long as they are between 0-10V and are far enough apart from each other, the process will work.

![Changing voltage variables](https://i.imgur.com/3evVnIn.png)

1. Now make sure the module is connected to both your computer and to Eurorack power, and that the power is switched on.
2. Then simply run the europi.py program and follow the instructions on the OLED display.
3. If at any point you do something wrong, just stop the program and run it again to start again.
4. Once the screen shows 'Calibration complete', you're all done! Now you can move on to programming

  
## Programming

To program the module, just create a new Python file, and then press Ctrl-Shift-S to save as to the Raspberry Pi Pico, and name it 'main.py'.  
Do not save files to the 'lib' folder, as this is just for libraries to be imported rather than programs that you will write.  
Now import the entire europi library by simply adding the line 'from europi import *'

![From europi import](https://i.imgur.com/UK3nJcV.jpg)

Now you have access to the inputs and outputs using easy methods, which you can read about more in the [README.md](https://github.com/Allen-Synthesis/EuroPi/blob/main/software/README.md) of the software folder.
