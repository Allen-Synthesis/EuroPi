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

### Installing the EuroPi library

1. Open the [europi.py](/software/firmware/europi.py) file from this repository.
2. Copy its entire contents by selecting all and pressing Ctrl-C.
3. Open Thonny back up and press Ctrl-N to create a new file.
4. Paste the europi.py contents into the new file, and press Ctrl-Shift-S to save as.
5. Choose Raspberry Pi Pico.

    ![Save to Pico](https://i.imgur.com/BTn7kAz.jpg)

6. Navigate inside the 'lib' folder by double clicking it.
7. Save the new file as 'europi.py', making sure to include the '.py' at the end.

    ![Save europi.py](https://i.imgur.com/vK5Xgik.jpg)


## Next Steps

Now that you have installed the europi.py and ssd1306 libraries, you are ready to take the next step with the module.  

[Option 1](https://github.com/roryjamesallen/EuroPi/blob/main/software/programming_instructions.md#write-your-own-program-from-scratch): Start writing your own program from scratch  
[Option 2](https://github.com/roryjamesallen/EuroPi/blob/main/software/programming_instructions.md#copy-someone-elses-program-to-run-on-your-module): Use someone else's program from the [contrib folder](/contrib/)  
[Option 3](https://github.com/roryjamesallen/EuroPi/blob/main/software/programming_instructions.md#calibrate-the-module): Calibrate the module for higher accuracy  


### Write your own program from scratch

To program the module, just create a new Python file, and then press Ctrl-Shift-S to save as to the Raspberry Pi Pico, and name it 'main.py'.  
Do not save files to the 'lib' folder, as this is just for libraries to be imported rather than programs that you will write.  
Now import the entire europi library by simply adding the line 'from europi import *'

  ![From europi import](https://i.imgur.com/UK3nJcV.jpg)

Now you have access to the inputs and outputs using easy methods, which you can read about more in the [README.md](/software/README.md) of the software folder.


### Copy someone else's program to run on your module

1. Open the [contrib folder](/contrib/) and decide which program you would like to run. Each program will have an identically named '.md' file describing how to use it.
2. Once you have chosen a program, click the '.py' file with the same name as the explanatory '.md' file to open it in GitHub.
3. Click the pencil icon to 'Edit this file' in the top right  
  
  ![image](https://user-images.githubusercontent.com/79809962/151053257-44d4be25-e959-4781-9ff8-49348ff5e2b4.png)  
4. Highlight the entire contents of the file  
  
  ![image](https://user-images.githubusercontent.com/79809962/151053508-24c9d5f7-fbf7-43c4-95ac-867b48ef924d.png)  
5. Press Ctrl-C to copy the contents of the file
6. Open Thonny, make sure your module is connected, and then press Ctrl-N to create a new blank file
7. Press Ctrl-V in the file to paste the contents of the file you copied
8. Press Ctrl-S to save the file, then choose 'Raspberry Pi Pico'  
  
  ![image](https://user-images.githubusercontent.com/79809962/151053911-7145ddb6-12e9-4606-909c-e1f888e3b4b9.png)  
9. Name the file 'main.py', being careful to include the '.py' so the module knows it is a Python file. If you do not name it 'main.py', the module will not know to automatically run your program whenever it is connected to power.  
  
  ![image](https://user-images.githubusercontent.com/79809962/151054018-0f495bb5-067e-4cd6-9640-c38e44a216de.png)  
  
  
### Calibrate the module

To use the module for accurately reading and outputting voltages, you need to complete a calibration process. This will allow your specific module to account for any differences in components, such as resistor tolerances.  
If you do not wish to calibrate the module and don't mind your voltages being slightly inaccurate, simply skip to the programming step and your module will use default values.

1. To begin, you need to copy the [calibrate.py](/software/firmware/calibrate.py) file from the firmware folder to your Pico using the [process outlined above](https://github.com/roryjamesallen/EuroPi/blob/main/software/programming_instructions.md#copy-someone-elses-program-to-run-on-your-module).
2. Name it 'main.py', just as if it were a program you were running as normal. Make sure there are no other programs also called 'main.py' at the same time, or Python won't know which one to run.
3. Make sure your module is connected to rack power for the calibration process. It doesn't matter if it connected to USB as well, however if it is it will give an extra warning to turn on rack power which you need to skip using button 1.
4. Turn on the rack power supply, and the screen will display 'Calibration Mode'. If it doesn't, try [troubleshooting](../troubleshooting.md).  
5. There are 2 options for calibration:
  - Low Accuracy: Only a single 10V supply is required
  - High Accuracy: A variable supply is required to produce voltages from 0-10V  
  Press button 1 to choose Low Accuracy mode, or button 2 to choose High Accuracy mode.
6. Connect your voltage source to the analogue input, and input each voltage displayed on the screen. To take a reading (once your voltage is connected), press button 1.
7. Once all the required voltages have been input, you now need to disconnect the analogue input from your voltage source, and instead connect it to CV output 1.
8. Once you have connected the analogue input to CV output 1, press button 1
9. Wait for each voltage up to 10V to complete. The module will tell you once it has completed.
10. The calibration process is now complete! You now need to rename or delete the 'calibrate.py' program, however DO NOT delete the new file created called 'calibration_values.py'. This file is where the calibration values are stored, and if you delete it you will have to complete the calibration again.



