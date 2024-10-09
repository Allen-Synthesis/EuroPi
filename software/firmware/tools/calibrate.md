# Calibration

Input & output calibration too for EuroPi.

## Required Equipment

Calibration requires the following physical setup:
1. EuroPi _must_ be connected to rack power
2. For low-accuracy calibration you need either another EuroRack module or an external voltage source capable of
   generating precise voltages of either 5V or 10V
3. For high-accuracy calibration you need another EuroRack module or adjustable external voltage source capable of
   generating precise voltages of 1.0, 2.0, 3.0, ..., 9.0, 10.0V.

## Usage

Calibration is interactive with instructions displayed on-screen. These instructions are summarized below:
1. Make sure the module is powered from your Eurorack power supply.
2. Select input calibration mode by turning `K2`. Press `B2` when ready
    a. low-accuracy with 10V input
    b. low-accuracy with 5V input
    c. high-accuracy with variable 0-10V input
3. Disconnect all patch cables from the module. Press `B1`
4. Connect your voltage source to `AIN`. Press `B1` when instructed.
    a. low-accuracy with 10V input: connect 10V to `AIN`
    b. low-accuracy with 5V input: connect 5V to `AIN`
    c. high-accuracy: read the on-screen instructions and connect the specified voltages when required.
5. Connect `CV1` directly to `AIN`. Press `B1`. Wait for the module to perform the output calibration.
6. Repeat step 5 for `CV2`, `CV3`, etc... until all CV outputs are calibrated
7. Reboot the module when prompted. The new calibration will be applied automatically.

Calibration data is saved to `/lib/calibration_values.py`. DO NOT delete this file; if you delete it you will have to
complete the calibration again.

After calibrating and rebooting the module it is recommended to run the `Diagnostic` program to verify that the
inputs and outputs have been properly calibrated.
